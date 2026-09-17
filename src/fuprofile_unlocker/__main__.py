from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .app import main as gui_main
from .core import generate_and_install
from .i18n import detect_language, translate


def main() -> None:
    language = detect_language()
    parser = argparse.ArgumentParser(description="FuProfile Unlocker")
    parser.add_argument(
        "raw", nargs="?", type=Path,
        help=translate("用于无界面测试的 RAW 文件", language),
    )
    parser.add_argument(
        "--install-root", type=Path,
        help=translate("覆盖安装目录，仅用于测试", language),
    )
    args = parser.parse_args()
    if args.raw:
        try:
            result = generate_and_install(
                args.raw,
                destination=args.install_root,
                status=lambda message: print(translate(message, language)),
            )
        except Exception as error:
            parser.error(translate(str(error), language))
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    else:
        gui_main()


if __name__ == "__main__":
    main()
