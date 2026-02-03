# Logfire Skill for Claude Code

A Claude Code skill for querying [Pydantic Logfire](https://logfire.pydantic.dev/) logs and traces.

## Installation

```bash
# Clone to your Claude Code skills directory
git clone https://github.com/raysurfer/logfire-skill ~/.claude/skills/logfire
cd ~/.claude/skills/logfire
uv sync
```

## Setup

Set `LOGFIRE_READ_TOKEN` environment variable (get from Logfire dashboard → Settings → Read Tokens).

## Usage

| Command | Description |
|---------|-------------|
| `/logfire errors` | Find recent exceptions |
| `/logfire slow` | Find slow requests (>1s) |
| `/logfire recent` | Show activity from last 5 min |
| `/logfire search <term>` | Search log messages |
| `/logfire trace <id>` | Look up specific trace |
| `/logfire endpoints` | Show endpoint statistics |
| `/logfire link <trace_id>` | Generate Logfire UI link |
| `/logfire query <sql>` | Run arbitrary SQL |

## Options

```
errors:    --hours N, --limit N, --file PATH
slow:      --hours N, --min-ms N, --limit N, --endpoint X
recent:    --minutes N, --limit N
search:    --hours N, --limit N, --span, --verbose
trace:     --span ID
endpoints: --hours N, --limit N, --errors
query:     --age N, --json
```

## License

MIT
