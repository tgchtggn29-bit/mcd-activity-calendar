#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""麦当劳 MCP 客户端：调用 tools/call，返回 JSON。

用法：
    python3 mcp_call.py <tool_name> [json_args] [--token TOKEN]

示例：
    python3 mcp_call.py campaign-calendar '{"specifiedDate":"2026-10-12"}'
    python3 mcp_call.py available-coupons
"""
import sys, json, urllib.request, os

MCP_URL = 'https://mcp.mcd.cn'
# Token 只从环境变量读取，不硬编码，避免泄露到公开仓库
DEFAULT_TOKEN = None

def call(tool, args=None, token=None):
    token = token or os.environ.get('MCD_MCP_TOKEN')
    if not token:
        raise SystemExit('缺少 MCP Token：请设置环境变量 MCD_MCP_TOKEN，或传入 --token')
    args = args or {}
    # initialize
    init = {
        'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
        'params': {'protocolVersion': '2024-11-05', 'capabilities': {},
                   'clientInfo': {'name': 'mccalendar', 'version': '1.0'}}
    }
    def post(payload):
        req = urllib.request.Request(
            MCP_URL,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/event-stream',
            },
            method='POST')
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode('utf-8')

    post(init)
    # tools/call
    payload = {
        'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call',
        'params': {'name': tool, 'arguments': args}
    }
    raw = post(payload)
    # 可能是 SSE 格式（data: ...），兼容处理
    if raw.lstrip().startswith('data:'):
        lines = []
        for line in raw.splitlines():
            if line.startswith('data:'):
                lines.append(line[5:].strip())
        raw = '\n'.join(lines)
    return json.loads(raw)

if __name__ == '__main__':
    tool = sys.argv[1]
    args = {}
    if len(sys.argv) > 2:
        args = json.loads(sys.argv[2])
    token = None
    if '--token' in sys.argv:
        token = sys.argv[sys.argv.index('--token') + 1]
    res = call(tool, args, token)
    print(json.dumps(res, ensure_ascii=False, indent=2))
