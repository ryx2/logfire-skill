#!/usr/bin/env python3
"""
Find recent exceptions in Logfire.

Usage:
    python errors.py
    python errors.py --hours 24 --limit 50
    python errors.py --file app/api/routes.py
"""
import argparse
import asyncio
import os
from datetime import UTC, datetime, timedelta

import _env  # noqa: F401 - loads env vars
from logfire.experimental.query_client import AsyncLogfireQueryClient


async def find_errors(hours: int = 24, limit: int = 20, filepath: str | None = None) -> list[dict]:
    """Find recent exceptions."""
    token = os.getenv('LOGFIRE_READ_TOKEN')
    if not token:
        raise ValueError('LOGFIRE_READ_TOKEN environment variable required')

    min_timestamp = datetime.now(UTC) - timedelta(hours=hours)

    sql = """
        SELECT start_timestamp, span_name, message, trace_id,
               exception_type, exception_message
        FROM records
        WHERE is_exception = true
    """
    if filepath:
        sql += f" AND exception_stacktrace LIKE '%{filepath}%'"
    sql += f' ORDER BY start_timestamp DESC LIMIT {limit}'

    async with AsyncLogfireQueryClient(token) as client:
        result = await client.query_json_rows(sql, min_timestamp=min_timestamp)
        return result['rows']


def format_error(row: dict) -> str:
    """Format an error row for display."""
    ts = row.get('start_timestamp', '')[:19]
    span = row.get('span_name', 'unknown')
    exc_type = row.get('exception_type', '')
    exc_msg = row.get('exception_message', '')[:100]
    trace = row.get('trace_id', '')[:16]

    return f'  [{ts}] {span}\n    {exc_type}: {exc_msg}\n    trace: {trace}'


async def main():
    parser = argparse.ArgumentParser(description='Find recent Logfire exceptions')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back (default: 24)')
    parser.add_argument('--limit', type=int, default=20, help='Max results (default: 20)')
    parser.add_argument('--file', help='Filter by filepath in stacktrace')
    args = parser.parse_args()

    rows = await find_errors(args.hours, args.limit, args.file)
    print(f'Found {len(rows)} exception(s) in last {args.hours}h\n')

    for row in rows:
        print(format_error(row))
        print()


if __name__ == '__main__':
    asyncio.run(main())
