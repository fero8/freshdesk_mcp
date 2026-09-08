# Lessons

- Freshdesk `GET /api/v2/search/tickets` requires the entire `query` wrapped in double quotes (`"status:2"`). Bare `status:2` returns Validation failed / Given query is invalid. Normalize (auto-wrap) in `search_tickets` so callers and skills can omit quotes.
- For deployed MCP servers, do not assume service-wide API credentials are acceptable. Confirm whether credentials should be per-user request credentials before adding server-side `.env` secrets.
- For Forge daemons running Python console scripts through `uv`, verify both the absolute `uv` path and the daemon working directory/project sync. `uv run <script>` cannot find project scripts unless it runs from, or is pointed at, the directory containing `pyproject.toml`.
- For Forge zero-downtime deployments, daemon `directory` and `uv --project` should point at `/home/forge/<site>/current`, not the site root, and the daemon must be restarted after `current` switches to a new release.
