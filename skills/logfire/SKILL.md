---
name: logfire
description: Query Logfire logs and traces for debugging. Use when user mentions logs, traces, errors, exceptions, slow requests, or asks to debug backend issues.
argument-hint: "[errors|slow|recent|search <term>|trace <id>|query <sql>]"
---

# Logfire Log Query Skill

Query Pydantic Logfire for logs, traces, errors, and performance data using the Logfire MCP server.

## Available MCP Tools

Use these MCP tools for Logfire queries:

- `mcp__logfire__arbitrary_query` - Run SQL queries against the records table
- `mcp__logfire__find_exceptions_in_file` - Find recent exceptions in a specific file
- `mcp__logfire__schema_reference` - Get the database schema for query help
- `mcp__logfire__logfire_link` - Generate UI links for trace IDs

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
- `service_name` - Service that generated the span

## Common Query Patterns

### Recent Errors
```sql
SELECT start_timestamp, span_name, message, trace_id
FROM records
WHERE is_exception
ORDER BY start_timestamp DESC
LIMIT 20
```

### Slow Requests (>1 second)
```sql
SELECT start_timestamp, span_name, duration * 1000 AS duration_ms, trace_id
FROM records
WHERE duration > 1
ORDER BY duration DESC
LIMIT 20
```

### Recent Activity
```sql
SELECT start_timestamp, span_name, message, is_exception
FROM records
ORDER BY start_timestamp DESC
LIMIT 30
```

### Search by Message
```sql
SELECT start_timestamp, span_name, message, trace_id
FROM records
WHERE message ILIKE '%search_term%'
ORDER BY start_timestamp DESC
LIMIT 20
```

### Trace Lookup
```sql
SELECT start_timestamp, span_name, message, attributes
FROM records
WHERE trace_id = 'your_trace_id'
ORDER BY start_timestamp
```

### Endpoint Stats
```sql
SELECT span_name, COUNT(*) as count,
       SUM(CASE WHEN is_exception THEN 1 ELSE 0 END) as errors,
       AVG(duration * 1000) as avg_ms
FROM records
WHERE span_name IS NOT NULL
GROUP BY span_name
ORDER BY count DESC
LIMIT 20
```

## Argument Handling

Parse user arguments as follows:

| Command | Action |
|---------|--------|
| `/logfire errors` | Query recent exceptions |
| `/logfire slow` | Query slow requests (>1s) |
| `/logfire recent` | Show recent activity |
| `/logfire search <term>` | Search messages for term |
| `/logfire trace <id>` | Look up specific trace |
| `/logfire query <sql>` | Run custom SQL query |
| `/logfire endpoints` | Show endpoint statistics |
| `/logfire file <path>` | Find exceptions in file |

## Response Format

When presenting results:
1. Show a summary count first
2. Format timestamps as readable dates
3. Truncate long messages to ~100 chars
4. Include trace_id for drill-down
5. Offer to generate Logfire UI links for traces

## Example Usage

User: `/logfire errors`
→ Use `arbitrary_query` with the recent errors SQL

User: `/logfire trace 019c22c6b9fd5b710ca67ed52055d835`
→ Use `arbitrary_query` filtering by trace_id, then offer `logfire_link`

User: `/logfire file app/api/routes.py`
→ Use `find_exceptions_in_file` with the filepath
