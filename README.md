# Freshdesk MCP Server
[![smithery badge](https://smithery.ai/badge/@effytech/freshdesk_mcp)](https://smithery.ai/server/@effytech/freshdesk_mcp)

[![Trust Score](https://archestra.ai/mcp-catalog/api/badge/quality/effytech/freshdesk_mcp)](https://archestra.ai/mcp-catalog/effytech__freshdesk_mcp)

An MCP server implementation that integrates with Freshdesk, enabling AI models to interact with Freshdesk modules and perform various support operations.

## Features

- **Freshdesk Integration**: Seamless interaction with Freshdesk API endpoints
- **AI Model Support**: Enables AI models to perform support operations through Freshdesk
- **Automated Ticket Management**: Handle ticket creation, updates, and responses

## Components

### Tools

The server offers several tools for Freshdesk operations:

- `create_ticket`: Create new support tickets
  - **Inputs**:
    - `subject` (string, required): Ticket subject
    - `description` (string, required): Ticket description
    - `source` (number, required): Ticket source code
    - `priority` (number, required): Ticket priority level
    - `status` (number, required): Ticket status code
    - `email` (string, optional): Email of the requester
    - `requester_id` (number, optional): ID of the requester
    - `custom_fields` (object, optional): Custom fields to set on the ticket
    - `additional_fields` (object, optional): Additional top-level fields

- `update_ticket`: Update existing tickets
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket to update
    - `ticket_fields` (object, required): Fields to update

- `delete_ticket`: Delete a ticket
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket to delete

- `search_tickets`: Search for tickets based on criteria
  - **Inputs**:
    - `query` (string, required): Search query string

- `get_ticket_fields`: Get all ticket fields
  - **Inputs**:
    - None

- `get_tickets`: Get all tickets
  - **Inputs**:
    - `page` (number, optional): Page number to fetch
    - `per_page` (number, optional): Number of tickets per page

- `get_ticket`: Get a single ticket
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket to get

- `get_ticket_conversation`: Get conversation for a ticket
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket

- `create_ticket_reply`: Reply to a ticket
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket
    - `body` (string, required): Content of the reply

- `create_ticket_note`: Add a note to a ticket
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket
    - `body` (string, required): Content of the note

- `update_ticket_conversation`: Update a conversation
  - **Inputs**:
    - `conversation_id` (number, required): ID of the conversation
    - `body` (string, required): Updated content

- `view_ticket_summary`: Get the summary of a ticket
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket

- `update_ticket_summary`: Update the summary of a ticket
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket
    - `body` (string, required): New summary content

- `delete_ticket_summary`: Delete the summary of a ticket
  - **Inputs**:
    - `ticket_id` (number, required): ID of the ticket

- `get_agents`: Get all agents
  - **Inputs**:
    - `page` (number, optional): Page number
    - `per_page` (number, optional): Number of agents per page

- `view_agent`: Get a single agent
  - **Inputs**:
    - `agent_id` (number, required): ID of the agent

- `create_agent`: Create a new agent
  - **Inputs**:
    - `agent_fields` (object, required): Agent details

- `update_agent`: Update an agent
  - **Inputs**:
    - `agent_id` (number, required): ID of the agent
    - `agent_fields` (object, required): Fields to update

- `search_agents`: Search for agents
  - **Inputs**:
    - `query` (string, required): Search query

- `list_contacts`: Get all contacts
  - **Inputs**:
    - `page` (number, optional): Page number
    - `per_page` (number, optional): Contacts per page

- `get_contact`: Get a single contact
  - **Inputs**:
    - `contact_id` (number, required): ID of the contact

- `search_contacts`: Search for contacts
  - **Inputs**:
    - `query` (string, required): Search query

- `update_contact`: Update a contact
  - **Inputs**:
    - `contact_id` (number, required): ID of the contact
    - `contact_fields` (object, required): Fields to update

- `list_companies`: Get all companies
  - **Inputs**:
    - `page` (number, optional): Page number
    - `per_page` (number, optional): Companies per page

- `view_company`: Get a single company
  - **Inputs**:
    - `company_id` (number, required): ID of the company

- `search_companies`: Search for companies
  - **Inputs**:
    - `query` (string, required): Search query

- `find_company_by_name`: Find a company by name
  - **Inputs**:
    - `name` (string, required): Company name

- `list_company_fields`: Get all company fields
  - **Inputs**:
    - None

## Getting Started

### Installing via Smithery

To install freshdesk_mcp for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@effytech/freshdesk_mcp):

```bash
npx -y @smithery/cli install @effytech/freshdesk_mcp --client claude
```

### Prerequisites

- A Freshdesk account (sign up at [freshdesk.com](https://freshdesk.com))
- Freshdesk API key
- `uvx` installed (`pip install uv` or `brew install uv`)

### Configuration

1. Generate your Freshdesk API key from the Freshdesk admin panel
2. Set `FRESHDESK_DOMAIN` on the server (for example `yourcompany.freshdesk.com`)
3. For remote HTTP clients, each user passes their own Freshdesk API key as `Authorization: Bearer <api-key>`

Copy `.env.example` to `.env` and adjust runtime settings as needed.

| Variable | Required | Description |
| --- | --- | --- |
| `FRESHDESK_DOMAIN` | yes | Freshdesk tenant hostname |
| `MCP_TRANSPORT` | no | `stdio` (default), `sse`, or `streamable-http` |
| `MCP_HOST` | no | Bind address for HTTP transports (default `127.0.0.1`) |
| `MCP_PORT` | no | Port for HTTP transports (default `8000`) |
| `ENABLED_MCP_TOOLS` | no | Comma-separated allowlist |
| `DISABLED_MCP_TOOLS` | no | Comma-separated denylist |

### Local usage (stdio)

For Claude Desktop, Cursor, or other stdio MCP clients on the same machine:

```json
"mcpServers": {
  "freshdesk-mcp": {
    "command": "uvx",
    "args": [
      "freshdesk-mcp"
    ],
    "env": {
      "FRESHDESK_API_KEY": "<YOUR_FRESHDESK_API_KEY>",
      "FRESHDESK_DOMAIN": "<YOUR_FRESHDESK_DOMAIN>"
    }
  }
}
```

See `mcp-local.example.json` for a project-local `uv run` variant.

Replace `YOUR_FRESHDESK_API_KEY` and `YOUR_FRESHDESK_DOMAIN` with your actual values.

### Remote usage (HTTP)

The server supports two remote MCP transports:

| Transport | Endpoint | Clients |
| --- | --- | --- |
| SSE (legacy) | `GET /sse` + `POST /messages/` | Cursor, Claude Desktop (remote URL) |
| Streamable HTTP | `POST /mcp` | OpenAI Codex |

With `MCP_TRANSPORT=sse`, both `/sse` and `/mcp` are served on the same port. Use `MCP_TRANSPORT=streamable-http` to expose only `/mcp`.

Run behind a reverse proxy (Nginx, Caddy, etc.) with TLS. Example client config is in `mcp.example.json`:

```json
"mcpServers": {
  "freshdesk-mcp-remote-sse": {
    "url": "https://mcp.example.com/sse",
    "headers": {
      "Authorization": "Bearer <your-freshdesk-api-key>"
    }
  },
  "freshdesk-mcp-remote-codex": {
    "url": "https://mcp.example.com/mcp",
    "headers": {
      "Authorization": "Bearer <your-freshdesk-api-key>"
    }
  }
}
```

**Codex** does not support SSE. Point it at `/mcp` in `~/.codex/config.toml` (see `codex.example.toml`):

```toml
[mcp_servers.freshdesk]
url = "https://mcp.example.com/mcp"
bearer_token_env_var = "FRESHDESK_API_KEY"
```

Codex CLI 0.134.0+ is required for remote MCP. Verify with `codex --version` and `/mcp` inside the TUI.

## Example Operations

Once configured, you can ask Claude to perform operations like:

- "Create a new ticket with subject 'Payment Issue for customer A101' and description as 'Reaching out for a payment issue in the last month for customer A101', where customer email is a101@acme.com and set priority to high"
- "Update the status of ticket #12345 to 'Resolved'"
- "List all high-priority tickets assigned to the agent John Doe"
- "List previous tickets of customer A101 in last 30 days"


## Testing

Local stdio:

```bash
uvx freshdesk-mcp
```

Remote HTTP (serves `/sse` and `/mcp`):

```bash
MCP_TRANSPORT=sse MCP_HOST=0.0.0.0 MCP_PORT=8000 uv run freshdesk-mcp
```

Unit tests:

```bash
uv run python -m unittest tests.test_tool_config -v
```

## Troubleshooting

- Verify your Freshdesk API key and domain are correct
- Ensure proper network connectivity to Freshdesk servers
- Check API rate limits and quotas
- Verify the `uvx` command is available in your PATH
- **Codex `POST /sse` → 405**: Codex requires Streamable HTTP at `/mcp`, not SSE at `/sse`
- **`BrokenResourceError` in server logs**: usually a client speaking SSE badly; switch the client to `/mcp`
- **Remote 401**: send `Authorization: Bearer <freshdesk-api-key>` on every HTTP request
- **SSE through Nginx**: disable buffering and use long proxy timeouts on `/sse` and `/mcp`

## License

This MCP server is licensed under the MIT License. See the LICENSE file in the project repository for full details.
