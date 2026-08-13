"""Entry point: start the Agent Harness server.

Usage: python main.py [--reload] [--host H] [--port P]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Defensively make the project root importable before importing `harness`.
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def main() -> None:
    """Parse args, print the banner, and run uvicorn."""
    parser = argparse.ArgumentParser(description="Agent Harness 本地智能体服务")
    parser.add_argument("--host", default=None, help="监听地址(默认取配置 HOST)")
    parser.add_argument("--port", type=int, default=None, help="监听端口(默认取配置 PORT)")
    parser.add_argument("--reload", action="store_true", help="代码变更时自动重载(开发用)")
    args = parser.parse_args()

    from harness.config import get_settings
    from harness.providers import describe

    import uvicorn

    settings = get_settings()
    host = args.host if args.host is not None else settings.HOST
    port = args.port if args.port is not None else settings.PORT
    info = describe()

    print("=" * 48)
    print("Agent Harness 已启动")
    print(f"  地址:   http://{host}:{port}")
    print(f"  供应商: {info['provider']}")
    print(f"  模型:   {info['model'] or '(未设置,请在 .env 配置 LLM_MODEL)'}")
    print("  按 Ctrl-C 退出")
    print("=" * 48)

    uvicorn.run("harness.server:app", host=host, port=port, reload=args.reload)


if __name__ == "__main__":
    main()
