#!/usr/bin/env python3
"""
Generate Logfire UI link for a trace.

Usage:
    python link.py 019c22c6b9fd5b710ca67ed52055d835
"""
import argparse
import asyncio
import os

import _env  # noqa: F401 - loads env vars
from logfire.experimental.query_client import AsyncLogfireQueryClient


async def get_link(trace_id: str) -> str:
    """Generate a Logfire UI link for a trace."""
    token = os.getenv('LOGFIRE_READ_TOKEN')
    if not token:
        raise ValueError('LOGFIRE_READ_TOKEN environment variable required')

    async with AsyncLogfireQueryClient(token) as client:
        response = await client.client.get('/v1/read-token-info')
        info = response.json()
        org = info['organization_name']
        project = info['project_name']

        base_url = str(client.client.base_url).rstrip('/')
        return f"{base_url}/{org}/{project}?q=trace_id='{trace_id}'"


async def main():
    parser = argparse.ArgumentParser(description='Generate Logfire UI link')
    parser.add_argument('trace_id', help='Trace ID to link to')
    args = parser.parse_args()

    link = await get_link(args.trace_id)
    print(f'Logfire UI link:\n{link}')


if __name__ == '__main__':
    asyncio.run(main())
