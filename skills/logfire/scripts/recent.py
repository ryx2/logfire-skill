#!/usr/bin/env python3
"""
Show recent Logfire activity.

Usage:
    python recent.py
    python recent.py --minutes 5 --limit 30
"""
import argparse
import asyncio
import os
from datetime import UTC, datetime, timedelta

import _env  # noqa: F401 - loads env vars
from logfire.experimental.query_client import AsyncLogfireQueryClient


async def get_recent(minutes: int = 5, limit: int = 30) -> list[dict]:
    """Get recent activity."""
    token = os.getenv('LOGFIRE_READ_TOKEN')
    if not token:
        raise ValueError('LOGFIRE_READ_TOKEN environment variable required')

    min_timestamp = datetime.now(UTC) - timedelta(minutes=minutes)

    sql = f"""
        SELECT start_timestamp, span_name, message, is_exception
        FROM records
        ORDER BY start_timestamp DESC
        LIMIT {limit}
    """

    async with AsyncLogfireQueryClient(token) as client:
        result = await client.query_json_rows(sql, min_timestamp=min_timestamp)
        return result['rows']


def format_row(row: dict) -> str:
    """Format a row for display."""
    ts = row.get('start_timestamp', '')[:19]
    span = row.get('span_name', row.get('message', 'unknown'))
    is_err = '❌' if row.get('is_exception') else '  '

    return f'{is_err} [{ts}] {span}'


async def main():
    parser = argparse.ArgumentParser(description='Show recent Logfire activity')
    parser.add_argument('--minutes', type=int, default=5, help='Minutes to look back (default: 5)')
    parser.add_argument('--limit', type=int, default=30, help='Max results (default: 30)')
    args = parser.parse_args()

    rows = await get_recent(args.minutes, args.limit)
    print(f'Recent activity (last {args.minutes} min, {len(rows)} spans):\n')

    for row in rows:
        print(format_row(row))


if __name__ == '__main__':
    asyncio.run(main())
