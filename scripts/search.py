#!/usr/bin/env python3
"""
Search Logfire logs by message content.

Usage:
    python search.py "error"
    python search.py "upload" --span --verbose
"""
import argparse
import asyncio
import json
import os
from datetime import UTC, datetime, timedelta

import _env  # noqa: F401 - loads env vars
from logfire.experimental.query_client import AsyncLogfireQueryClient


async def search_logs(query: str, hours: int = 24, limit: int = 20, search_span: bool = False) -> list[dict]:
    """Search logs by message or span name."""
    token = os.getenv('LOGFIRE_READ_TOKEN')
    if not token:
        raise ValueError('LOGFIRE_READ_TOKEN environment variable required')

    min_timestamp = datetime.now(UTC) - timedelta(hours=hours)

    if search_span:
        where = f"span_name ILIKE '%{query}%'"
    else:
        where = f"message ILIKE '%{query}%'"

    sql = f"""
        SELECT start_timestamp, span_name, message, trace_id, is_exception
        FROM records
        WHERE {where}
        ORDER BY start_timestamp DESC
        LIMIT {limit}
    """

    async with AsyncLogfireQueryClient(token) as client:
        result = await client.query_json_rows(sql, min_timestamp=min_timestamp)
        return result['rows']


def format_row(row: dict, verbose: bool = False) -> str:
    """Format a row for display."""
    ts = row.get('start_timestamp', '')[:19]
    span = row.get('span_name', '')
    msg = row.get('message', '')[:80] if not verbose else row.get('message', '')
    trace = row.get('trace_id', '')[:16]
    is_err = '❌' if row.get('is_exception') else '  '

    lines = [f'{is_err} [{ts}] {span}']
    if msg and msg != span:
        lines.append(f'    {msg}')
    lines.append(f'    trace: {trace}')
    return '\n'.join(lines)


async def main():
    parser = argparse.ArgumentParser(description='Search Logfire logs')
    parser.add_argument('query', help='Search term')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back (default: 24)')
    parser.add_argument('--limit', type=int, default=20, help='Max results (default: 20)')
    parser.add_argument('--span', action='store_true', help='Search span_name instead of message')
    parser.add_argument('--verbose', action='store_true', help='Show full messages')
    args = parser.parse_args()

    rows = await search_logs(args.query, args.hours, args.limit, args.span)
    field = 'span_name' if args.span else 'message'
    print(f'Found {len(rows)} match(es) for "{args.query}" in {field}\n')

    for row in rows:
        print(format_row(row, args.verbose))
        print()


if __name__ == '__main__':
    asyncio.run(main())
