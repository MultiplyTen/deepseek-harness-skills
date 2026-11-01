"""Generate one local text-counter overlay without changing existing config."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ignore-whitespace", action="store_true")
    options = parser.parse_args()
    plugin_path = options.plugin.resolve()
    if not plugin_path.is_file():
        parser.error(f"Plugin does not exist: {plugin_path}")
    output_path = options.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    quoted_path = json.dumps(plugin_path.as_posix(), ensure_ascii=False)
    setting = str(options.ignore_whitespace).lower()
    overlay = (
        "- insert:\n"
        "    - id: text-counter-config\n"
        f"      name: {quoted_path}\n"
        "      config:\n"
        f"        ignoreWhitespace: {setting}\n"
    )
    try:
        with output_path.open("x", encoding="utf-8", newline="\n") as output:
            output.write(overlay)
    except FileExistsError:
        parser.error(f"Output already exists; choose a new overlay file: {output_path}")
    print(output_path)


if __name__ == "__main__":
    main()
