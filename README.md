# logfire-skill

A Claude Code skill for querying [Pydantic Logfire](https://logfire.pydantic.dev/) logs and traces.

## Installation

### 1. Add the Logfire MCP Server

```bash
claude mcp add logfire -e LOGFIRE_READ_TOKEN=your_token -- uvx logfire-mcp@latest
```

Get your read token from [Logfire Settings](https://logfire.pydantic.dev/-/redirect/latest-project/settings/read-tokens).

### 2. Install the Skill

Copy the skill to your Claude Code skills directory:

```bash
# Personal (all projects)
cp -r skills/logfire ~/.claude/skills/

# Or project-specific
cp -r skills/logfire .claude/skills/
```

### 3. Restart Claude Code

```bash
claude
```

## Usage

```
/logfire errors          # Recent exceptions
/logfire slow            # Slow requests (>1s)
/logfire recent          # Recent activity
/logfire search <term>   # Search messages
/logfire trace <id>      # Look up trace
/logfire endpoints       # Endpoint stats
/logfire file <path>     # Exceptions in file
/logfire query <sql>     # Custom SQL
```

## Examples

```
/logfire errors
/logfire slow
/logfire trace 019c22c6b9fd5b710ca67ed52055d835
/logfire search "upload failed"
/logfire file app/api/routes.py
```

## MCP Tools

The skill uses the [logfire-mcp](https://github.com/pydantic/logfire-mcp) server which provides:

- `arbitrary_query` - Run SQL against the records table
- `find_exceptions_in_file` - Recent exceptions in a file
- `schema_reference` - Database schema docs
- `logfire_link` - Generate UI links for traces

## License

MIT
