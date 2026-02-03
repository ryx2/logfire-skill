#!/usr/bin/env python3
"""
Query Logfire logs with arbitrary SQL.

Usage:
    python query.py "SELECT * FROM records LIMIT 10"
    python query.py --trace 019c22c6b9fd5b710ca67ed52055d835
    python query.py --trace 019c22c6b9fd5b710ca67ed52055d835 --span 30d8a278efd3f5ed
"""
import argparse
import asyncio
import json
import os
from datetime import UTC, datetime, timedelta

import _env  # noqa: F401 - loads env vars
from logfire.experimental.query_client import AsyncLogfireQueryClient


async def run_query(sql: str, age_minutes: int = 1440) -> list[dict]:
    """Execute SQL query against Logfire."""
    token = os.getenv('LOGFIRE_READ_TOKEN')
    if not token:
        raise ValueError('LOGFIRE_READ_TOKEN environment variable required')

    min_timestamp = datetime.now(UTC) - timedelta(minutes=age_minutes)
    async with AsyncLogfireQueryClient(token) as client:
        result = await client.query_json_rows(sql, min_timestamp=min_timestamp)
        return result['rows']


async def trace_lookup(trace_id: str, span_id: str | None = None) -> list[dict]:
    """Look up a specific trace, optionally filtered by span."""
    sql = f"""
        SELECT start_timestamp, span_name, message, duration, is_exception, attributes
        FROM records
        WHERE trace_id = '{trace_id}'
    """
    if span_id:
        sql += f" AND span_id = '{span_id}'"
    sql += ' ORDER BY start_timestamp'
    return await run_query(sql)


def format_row(row: dict) -> str:
    """Format a single row for display."""
    ts = row.get('start_timestamp', '')
    if ts:
        ts = ts[:23]  # Trim microseconds
    span = row.get('span_name', row.get('message', 'unknown'))
    attrs = row.get('attributes', {})

    lines = [f'  [{ts}] {span}']
    if attrs:
        lines.append(f'    {json.dumps(attrs, indent=8, default=str)}')
    return '\n'.join(lines)


async def main():
    parser = argparse.ArgumentParser(description='Query Logfire logs')
    parser.add_argument('sql', nargs='?', help='SQL query to run')
    parser.add_argument('--trace', help='Look up a specific trace ID')
    parser.add_argument('--span', help='Filter by span ID (requires --trace)')
    parser.add_argument('--age', type=int, default=1440, help='Minutes to look back (default: 1440 = 24h)')
    parser.add_argument('--json', action='store_true', help='Output raw JSON')
    args = parser.parse_args()

    if args.trace:
        print(f'Trace: {args.trace}', end='')
        if args.span:
            print(f'  Span: {args.span}')
        else:
            print()
        rows = await trace_lookup(args.trace, args.span)
    elif args.sql:
        rows = await run_query(args.sql, args.age)
    else:
        parser.error('Either SQL query or --trace is required')
        return

    print(f'Found {len(rows)} span(s)\n')

    if args.json:
        print(json.dumps(rows, indent=2, default=str))
    else:
        for row in rows:
            print(format_row(row))


if __name__ == '__main__':
    asyncio.run(main())
