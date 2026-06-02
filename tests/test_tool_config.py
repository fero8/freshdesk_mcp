import asyncio
import base64
import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path

from freshdesk_mcp.tool_config import (
    is_mcp_tool_enabled,
    make_configured_tool_decorator,
    parse_mcp_tool_list,
)


class FakeMCP:
    def __init__(self):
        self.registered_tools = []

    def tool(self):
        def decorator(func):
            self.registered_tools.append(func.__name__)
            return func

        return decorator


async def get_ticket():
    return {"id": 1}


async def update_ticket():
    return {"id": 1}


class TestToolConfig(unittest.TestCase):
    def test_parse_mcp_tool_list_returns_none_for_unset_or_blank_values(self):
        self.assertIsNone(parse_mcp_tool_list(None))
        self.assertIsNone(parse_mcp_tool_list(""))
        self.assertIsNone(parse_mcp_tool_list("   "))
        self.assertIsNone(parse_mcp_tool_list(" , , "))

    def test_parse_mcp_tool_list_strips_comma_separated_tool_names(self):
        self.assertEqual(
            parse_mcp_tool_list("get_ticket, update_ticket,,search_tickets "),
            {"get_ticket", "update_ticket", "search_tickets"},
        )

    def test_default_configuration_exposes_all_tools(self):
        self.assertTrue(is_mcp_tool_enabled("get_ticket", None, None))
        self.assertTrue(is_mcp_tool_enabled("update_ticket", None, None))

    def test_allowlist_exposes_only_enabled_tools(self):
        enabled_tools = {"get_ticket"}

        self.assertTrue(is_mcp_tool_enabled("get_ticket", enabled_tools, None))
        self.assertFalse(is_mcp_tool_enabled("update_ticket", enabled_tools, None))

    def test_denylist_hides_disabled_tools(self):
        disabled_tools = {"update_ticket"}

        self.assertTrue(is_mcp_tool_enabled("get_ticket", None, disabled_tools))
        self.assertFalse(is_mcp_tool_enabled("update_ticket", None, disabled_tools))

    def test_denylist_takes_precedence_over_allowlist(self):
        enabled_tools = {"get_ticket", "update_ticket"}
        disabled_tools = {"update_ticket"}

        self.assertTrue(is_mcp_tool_enabled("get_ticket", enabled_tools, disabled_tools))
        self.assertFalse(is_mcp_tool_enabled("update_ticket", enabled_tools, disabled_tools))

    def test_configured_tool_decorator_registers_only_exposed_tools(self):
        fake_mcp = FakeMCP()
        tool = make_configured_tool_decorator(
            fake_mcp,
            enabled_tools={"get_ticket", "update_ticket"},
            disabled_tools={"update_ticket"},
        )

        decorated_get_ticket = tool()(get_ticket)
        decorated_update_ticket = tool()(update_ticket)

        self.assertIs(decorated_get_ticket, get_ticket)
        self.assertIs(decorated_update_ticket, update_ticket)
        self.assertEqual(fake_mcp.registered_tools, ["get_ticket"])


class TestServerToolRegistration(unittest.TestCase):
    MCP_RUNTIME_ENV_VARS = ("MCP_TRANSPORT", "MCP_HOST", "MCP_PORT")

    class FakeRunnableMCP:
        def __init__(self):
            self.transport = None

        def run(self, transport):
            self.transport = transport

    def registered_tool_names(self, enabled_tools=None, disabled_tools=None):
        original_enabled_tools = os.environ.get("ENABLED_MCP_TOOLS")
        original_disabled_tools = os.environ.get("DISABLED_MCP_TOOLS")

        try:
            self.set_env_var("ENABLED_MCP_TOOLS", enabled_tools)
            self.set_env_var("DISABLED_MCP_TOOLS", disabled_tools)
            sys.modules.pop("freshdesk_mcp.server", None)
            server = importlib.import_module("freshdesk_mcp.server")
            tools = asyncio.run(server.mcp.list_tools())
            return {tool.name for tool in tools}
        finally:
            self.set_env_var("ENABLED_MCP_TOOLS", original_enabled_tools)
            self.set_env_var("DISABLED_MCP_TOOLS", original_disabled_tools)
            sys.modules.pop("freshdesk_mcp.server", None)

    @staticmethod
    def set_env_var(name, value):
        if value is None:
            os.environ.pop(name, None)
            return

        os.environ[name] = value

    def test_server_exposes_all_tools_when_config_is_unset(self):
        tools = self.registered_tool_names()

        self.assertIn("get_ticket", tools)
        self.assertIn("update_ticket", tools)

    def test_server_exposes_only_enabled_tools(self):
        tools = self.registered_tool_names(enabled_tools="get_ticket")

        self.assertIn("get_ticket", tools)
        self.assertNotIn("update_ticket", tools)

    def test_server_hides_disabled_tools(self):
        tools = self.registered_tool_names(disabled_tools="update_ticket")

        self.assertIn("get_ticket", tools)
        self.assertNotIn("update_ticket", tools)

    def test_server_disabled_tools_override_enabled_tools(self):
        tools = self.registered_tool_names(
            enabled_tools="get_ticket,update_ticket",
            disabled_tools="update_ticket",
        )

        self.assertIn("get_ticket", tools)
        self.assertNotIn("update_ticket", tools)

    def test_server_uses_default_stdio_runtime_settings(self):
        server = self.import_server_with_runtime_env()

        self.assertEqual(server.MCP_TRANSPORT, "stdio")
        self.assertEqual(server.MCP_HOST, "127.0.0.1")
        self.assertEqual(server.MCP_PORT, 8000)
        self.assertEqual(server.mcp.settings.host, "127.0.0.1")
        self.assertEqual(server.mcp.settings.port, 8000)

    def test_server_uses_env_runtime_settings(self):
        server = self.import_server_with_runtime_env(
            MCP_TRANSPORT="sse",
            MCP_HOST="127.0.0.1",
            MCP_PORT="8001",
        )

        self.assertEqual(server.MCP_TRANSPORT, "sse")
        self.assertEqual(server.MCP_HOST, "127.0.0.1")
        self.assertEqual(server.MCP_PORT, 8001)
        self.assertEqual(server.mcp.settings.host, "127.0.0.1")
        self.assertEqual(server.mcp.settings.port, 8001)

    def test_main_runs_configured_transport(self):
        server = self.import_server_with_runtime_env(MCP_TRANSPORT="sse")
        runner_called = False

        async def fake_authenticated_sse_runner():
            nonlocal runner_called
            runner_called = True

        original_runner = server.run_authenticated_sse_async

        try:
            server.run_authenticated_sse_async = fake_authenticated_sse_runner
            server.main()
        finally:
            server.run_authenticated_sse_async = original_runner

        self.assertTrue(runner_called)

    def test_server_loads_env_file_values_from_working_directory(self):
        original_cwd = os.getcwd()
        env_names = ("FRESHDESK_DOMAIN", "MCP_TRANSPORT", "MCP_PORT")
        original_values = {name: os.environ.get(name) for name in env_names}

        try:
            with tempfile.TemporaryDirectory() as directory:
                Path(directory, ".env").write_text(
                    "FRESHDESK_DOMAIN=example.freshdesk.com\n"
                    "MCP_TRANSPORT=sse\n"
                    "MCP_PORT=8002\n",
                    encoding="utf-8",
                )
                for name in env_names:
                    self.set_env_var(name, None)
                os.chdir(directory)

                sys.modules.pop("freshdesk_mcp.server", None)
                server = importlib.import_module("freshdesk_mcp.server")

                self.assertEqual(server.FRESHDESK_DOMAIN, "example.freshdesk.com")
                self.assertEqual(server.MCP_TRANSPORT, "sse")
                self.assertEqual(server.MCP_PORT, 8002)
        finally:
            os.chdir(original_cwd)
            for name, value in original_values.items():
                self.set_env_var(name, value)
            sys.modules.pop("freshdesk_mcp.server", None)

    def import_server_with_runtime_env(self, **env_vars):
        original_cwd = os.getcwd()
        original_values = {
            name: os.environ.get(name)
            for name in (*self.MCP_RUNTIME_ENV_VARS, *env_vars.keys())
        }

        try:
            with tempfile.TemporaryDirectory() as directory:
                os.chdir(directory)
                for name in self.MCP_RUNTIME_ENV_VARS:
                    self.set_env_var(name, env_vars.get(name))

                sys.modules.pop("freshdesk_mcp.server", None)
                return importlib.import_module("freshdesk_mcp.server")
        finally:
            os.chdir(original_cwd)
            for name, value in original_values.items():
                self.set_env_var(name, value)
            sys.modules.pop("freshdesk_mcp.server", None)


class TestBearerAuthentication(unittest.TestCase):
    def setUp(self):
        self.original_freshdesk_api_key = os.environ.get("FRESHDESK_API_KEY")
        os.environ.pop("FRESHDESK_API_KEY", None)
        sys.modules.pop("freshdesk_mcp.server", None)
        self.server = importlib.import_module("freshdesk_mcp.server")

    def tearDown(self):
        if self.original_freshdesk_api_key is None:
            os.environ.pop("FRESHDESK_API_KEY", None)
        else:
            os.environ["FRESHDESK_API_KEY"] = self.original_freshdesk_api_key
        sys.modules.pop("freshdesk_mcp.server", None)

    def test_extract_bearer_token_accepts_only_bearer_authorization(self):
        self.assertEqual(
            self.server.extract_bearer_token("Bearer freshdesk-user-key"),
            "freshdesk-user-key",
        )
        self.assertEqual(
            self.server.extract_bearer_token("bearer freshdesk-user-key"),
            "freshdesk-user-key",
        )
        self.assertIsNone(self.server.extract_bearer_token(None))
        self.assertIsNone(self.server.extract_bearer_token(""))
        self.assertIsNone(self.server.extract_bearer_token("Basic abc123"))
        self.assertIsNone(self.server.extract_bearer_token("Bearer "))

    def test_freshdesk_authorization_header_uses_session_bearer_token(self):
        token = self.server.set_freshdesk_api_key("freshdesk-user-key")

        try:
            encoded = base64.b64encode(b"freshdesk-user-key:X").decode()
            self.assertEqual(
                self.server.build_freshdesk_authorization_header(),
                f"Basic {encoded}",
            )
        finally:
            self.server.reset_freshdesk_api_key(token)

    def test_protected_tool_returns_401_when_bearer_is_missing(self):
        async def sample_tool():
            return {"ok": True}

        protected_tool = self.server.require_freshdesk_auth(sample_tool)

        self.assertEqual(
            asyncio.run(protected_tool()),
            {
                "error": "Missing Bearer token",
                "status_code": 401,
            },
        )

    def test_sse_endpoint_returns_401_when_bearer_is_missing(self):
        async def request_sse_without_bearer():
            import httpx

            transport = httpx.ASGITransport(app=self.server.create_sse_app())
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://testserver",
            ) as client:
                return await client.get("/sse")

        response = asyncio.run(request_sse_without_bearer())

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers["www-authenticate"], "Bearer")


if __name__ == "__main__":
    unittest.main()
