#!/usr/bin/env python3
"""
Find slow requests in Logfire.

Usage:
    python slow.py
    python slow.py --min-ms 1000 --endpoint upload
"""
import argparse
import asyncio
import os
from datetime import UTC, datetime, timedelta

import _env  # noqa: F401 - loads env vars
from logfire.experimental.query_client import AsyncLogfireQueryClient


async def find_slow(hours: int = 24, min_ms: int = 1000, limit: int = 20, endpoint: str | None = None) -> list[dict]:
    """Find slow requests."""
    token = os.getenv('LOGFIRE_READ_TOKEN')
    if not token:
        raise ValueError('LOGFIRE_READ_TOKEN environment variable required')

    min_timestamp = datetime.now(UTC) - timedelta(hours=hours)
    min_seconds = min_ms / 1000

    sql = f"""
        SELECT start_timestamp, span_name, duration * 1000 AS duration_ms, trace_id
        FROM records
        WHERE duration > {min_seconds}
    """
    if endpoint:
        sql += f" AND span_name ILIKE '%{endpoint}%'"
    sql += f' ORDER BY duration DESC LIMIT {limit}'

    async with AsyncLogfireQueryClient(token) as client:
        result = await client.query_json_rows(sql, min_timestamp=min_timestamp)
        return result['rows']


def format_slow(row: dict) -> str:
    """Format a slow request row."""
    ts = row.get('start_timestamp', '')[:19]
    span = row.get('span_name', 'unknown')
    duration = row.get('duration_ms', 0)
    trace = row.get('trace_id', '')[:16]

    return f'  [{ts}] {span}\n    {duration:.0f}ms | trace: {trace}'


async def main():
    parser = argparse.ArgumentParser(description='Find slow Logfire requests')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back (default: 24)')
    parser.add_argument('--min-ms', type=int, default=1000, help='Minimum duration in ms (default: 1000)')
    parser.add_argument('--limit', type=int, default=20, help='Max results (default: 20)')
    parser.add_argument('--endpoint', help='Filter by endpoint name')
    args = parser.parse_args()

    rows = await find_slow(args.hours, args.min_ms, args.limit, args.endpoint)
    print(f'Found {len(rows)} request(s) slower than {args.min_ms}ms\n')

    for row in rows:
        print(format_slow(row))
        print()


if __name__ == '__main__':
    asyncio.run(main())
