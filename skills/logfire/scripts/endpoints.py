#!/usr/bin/env python3
"""
Show endpoint statistics from Logfire.

Usage:
    python endpoints.py
    python endpoints.py --hours 24 --errors
"""
import argparse
import asyncio
import os
from datetime import UTC, datetime, timedelta

import _env  # noqa: F401 - loads env vars
from logfire.experimental.query_client import AsyncLogfireQueryClient


async def get_endpoints(hours: int = 24, limit: int = 20, errors_only: bool = False) -> list[dict]:
    """Get endpoint statistics."""
    token = os.getenv('LOGFIRE_READ_TOKEN')
    if not token:
        raise ValueError('LOGFIRE_READ_TOKEN environment variable required')

    min_timestamp = datetime.now(UTC) - timedelta(hours=hours)

    sql = f"""
        SELECT span_name,
               COUNT(*) as count,
               SUM(CASE WHEN is_exception THEN 1 ELSE 0 END) as errors,
               AVG(duration * 1000) as avg_ms,
               MAX(duration * 1000) as max_ms
        FROM records
        WHERE span_name IS NOT NULL
    """
    if errors_only:
        sql += ' AND is_exception = true'
    sql += f"""
        GROUP BY span_name
        ORDER BY count DESC
        LIMIT {limit}
    """

    async with AsyncLogfireQueryClient(token) as client:
        result = await client.query_json_rows(sql, min_timestamp=min_timestamp)
        return result['rows']


def format_row(row: dict) -> str:
    """Format an endpoint row."""
    span = row.get('span_name', 'unknown')
    count = row.get('count', 0)
    errors = row.get('errors', 0)
    avg_ms = row.get('avg_ms', 0)
    max_ms = row.get('max_ms', 0)

    error_pct = (errors / count * 100) if count > 0 else 0
    err_str = f'{errors} ({error_pct:.1f}%)' if errors > 0 else '0'

    return f'  {span}\n    {count} reqs | {err_str} errors | avg {avg_ms:.0f}ms | max {max_ms:.0f}ms'


async def main():
    parser = argparse.ArgumentParser(description='Show Logfire endpoint stats')
    parser.add_argument('--hours', type=int, default=24, help='Hours to look back (default: 24)')
    parser.add_argument('--limit', type=int, default=20, help='Max endpoints (default: 20)')
    parser.add_argument('--errors', action='store_true', help='Only show endpoints with errors')
    args = parser.parse_args()

    rows = await get_endpoints(args.hours, args.limit, args.errors)
    print(f'Endpoint stats (last {args.hours}h, {len(rows)} endpoints):\n')

    for row in rows:
        print(format_row(row))
        print()


if __name__ == '__main__':
    asyncio.run(main())
