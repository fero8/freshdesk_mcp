from collections.abc import Callable
from typing import TypeVar


ToolFunc = TypeVar("ToolFunc", bound=Callable)


def parse_mcp_tool_list(raw_value: str | None) -> set[str] | None:
    if raw_value is None or not raw_value.strip():
        return None

    tools = {tool.strip() for tool in raw_value.split(",") if tool.strip()}
    return tools or None


def is_mcp_tool_enabled(
    tool_name: str,
    enabled_tools: set[str] | None,
    disabled_tools: set[str] | None,
) -> bool:
    if enabled_tools is not None and tool_name not in enabled_tools:
        return False

    if disabled_tools is not None and tool_name in disabled_tools:
        return False

    return True


def make_configured_tool_decorator(
    mcp,
    enabled_tools: set[str] | None,
    disabled_tools: set[str] | None,
):
    def tool():
        mcp_tool = mcp.tool()

        def decorator(func: ToolFunc) -> ToolFunc:
            if not is_mcp_tool_enabled(func.__name__, enabled_tools, disabled_tools):
                return func

            return mcp_tool(func)

        return decorator

    return tool
