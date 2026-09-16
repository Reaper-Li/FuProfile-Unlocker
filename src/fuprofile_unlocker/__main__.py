from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .app import main as gui_main
from .core import generate_and_install


def main() -> None:
    parser = argparse.ArgumentParser(description="FuProfile Unlocker")
    parser.add_argument("raw", nargs="?", type=Path, help="用于无界面测试的 RAW 文件")
    parser.add_argument("--install-root", type=Path, help="覆盖安装目录，仅用于测试")
    args = parser.parse_args()
    if args.raw:
        result = generate_and_install(args.raw, destination=args.install_root, status=print)
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        gui_main()


if __name__ == "__main__":
    main()
