---
name: logfire
description: Query Logfire logs and traces for debugging. Use when user mentions logs, traces, errors, exceptions, slow requests, or asks to debug backend issues.
argument-hint: "[errors|slow|recent|search <term>|trace <id>|query <sql>]"
---

# Logfire Log Query Skill

Query Pydantic Logfire for logs, traces, errors, and performance data.

## Setup

Requires `LOGFIRE_READ_TOKEN` environment variable (from .env or exported).

## Bundled Scripts

Run scripts from the skill's scripts directory using `uv run`:

| Command | Script |
|---------|--------|
| `/logfire errors` | `uv run python {SKILL_DIR}/scripts/errors.py` |
| `/logfire slow` | `uv run python {SKILL_DIR}/scripts/slow.py` |
| `/logfire recent` | `uv run python {SKILL_DIR}/scripts/recent.py` |
| `/logfire search <term>` | `uv run python {SKILL_DIR}/scripts/search.py "<term>"` |
| `/logfire trace <id>` | `uv run python {SKILL_DIR}/scripts/query.py --trace <id>` |
| `/logfire trace <id> --span <span>` | `uv run python {SKILL_DIR}/scripts/query.py --trace <id> --span <span>` |
| `/logfire query <sql>` | `uv run python {SKILL_DIR}/scripts/query.py "<sql>"` |
| `/logfire endpoints` | `uv run python {SKILL_DIR}/scripts/endpoints.py` |
| `/logfire link <trace_id>` | `uv run python {SKILL_DIR}/scripts/link.py <trace_id>` |

Replace `{SKILL_DIR}` with the actual skill directory path shown in the "Base directory" header.

## Script Options

### errors.py
```
--hours N      Hours to look back (default: 24)
--limit N      Max results (default: 20)
--file PATH    Filter by filepath in stacktrace
```

### slow.py
```
--hours N      Hours to look back (default: 24)
--min-ms N     Minimum duration in ms (default: 1000)
--limit N      Max results (default: 20)
--endpoint X   Filter by endpoint name
```

### recent.py
```
--minutes N    Minutes to look back (default: 5)
--limit N      Max results (default: 30)
```

### search.py
```
--hours N      Hours to look back (default: 24)
--limit N      Max results (default: 20)
--span         Search span_name instead of message
--verbose      Show full messages
```

### query.py
```
--trace ID     Look up specific trace
--span ID      Filter by span ID (requires --trace)
--age N        Minutes to look back (default: 1440)
--json         Output raw JSON
```

### endpoints.py
```
--hours N      Hours to look back (default: 24)
--limit N      Max endpoints (default: 20)
--errors       Only show endpoints with errors
```

## Records Table Schema

Key columns in the `records` table:
- `start_timestamp` - When the span started
- `span_name` - Name of the span (e.g., endpoint name)
- `message` - Log message
- `duration` - Span duration in seconds (multiply by 1000 for ms)
- `is_exception` - Boolean, true if this span has an exception
- `trace_id` - Trace identifier (use for grouping related spans)
- `span_id` - Individual span identifier
- `attributes` - JSON object with span attributes

## Example Usage

User: `/logfire errors`
→ Run: `uv run python {SKILL_DIR}/scripts/errors.py`

User: `/logfire trace 019c22c6b9fd5b710ca67ed52055d835`
→ Run: `uv run python {SKILL_DIR}/scripts/query.py --trace 019c22c6b9fd5b710ca67ed52055d835`

User: `/logfire search "upload" --span`
→ Run: `uv run python {SKILL_DIR}/scripts/search.py "upload" --span`

User: `/logfire slow --min-ms 2000`
→ Run: `uv run python {SKILL_DIR}/scripts/slow.py --min-ms 2000`
