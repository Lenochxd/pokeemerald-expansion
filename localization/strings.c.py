"""Merge matching string declarations in src/strings.c from a raw GitHub strings.c.

The script only replaces existing local declarations by symbol name and never adds
new declarations. It prints a summary plus missing/unmatched symbols.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.error
import urllib.request


DEFAULT_RAW_URL = "https://raw.githubusercontent.com/simsor/pokeemerald-fr/french/src/strings.c"


DECLARATION_RE = re.compile(
    r"(?P<full>^const\s+u8\s+(?P<name>[A-Za-z_]\w*)\[\]\s*=\s*.*?;\n?)",
    re.MULTILINE | re.DOTALL,
)


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "strings-merge-script/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to fetch URL: {url}\nReason: {exc}") from exc
    return data.decode("utf-8", errors="replace").replace("\r\n", "\n").replace('«', '“').replace('»', '“')


def parse_declarations(text: str) -> tuple[list[re.Match[str]], dict[str, str]]:
    matches = list(DECLARATION_RE.finditer(text))
    mapping: dict[str, str] = {}
    for match in matches:
        mapping[match.group("name")] = match.group("full")
    return matches, mapping


def merge_local_with_remote(local_text: str, remote_map: dict[str, str]) -> tuple[str, dict[str, object]]:
    local_matches, local_map = parse_declarations(local_text)

    parts: list[str] = []
    last_end = 0
    replaced = 0
    unchanged = 0
    missing_in_remote: list[str] = []

    for match in local_matches:
        start, end = match.span("full")
        name = match.group("name")
        current_block = match.group("full")

        parts.append(local_text[last_end:start])
        if name in remote_map:
            replacement = remote_map[name]
            parts.append(replacement)
            if replacement != current_block:
                replaced += 1
            else:
                unchanged += 1
        else:
            parts.append(current_block)
            missing_in_remote.append(name)

        last_end = end

    parts.append(local_text[last_end:])
    merged = "".join(parts)

    remote_only = sorted(name for name in remote_map if name not in local_map)

    stats: dict[str, object] = {
        "local_declarations": len(local_matches),
        "remote_declarations": len(remote_map),
        "replaced": replaced,
        "unchanged": unchanged,
        "missing_in_remote": sorted(missing_in_remote),
        "remote_only": remote_only,
    }
    return merged, stats


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replace matching const u8 string declarations in src/strings.c from a raw URL source."
    )
    parser.add_argument("--url", default=DEFAULT_RAW_URL, help="Raw URL to source strings.c")
    parser.add_argument(
        "--local",
        default=os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src", "strings.c")),
        help="Path to local strings.c",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview summary without writing file",
    )
    args = parser.parse_args()

    local_path = os.path.abspath(args.local)
    if not os.path.exists(local_path):
        print(f"ERROR: local file not found: {local_path}")
        return 1

    try:
        remote_text = fetch_text(args.url)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    with open(local_path, "r", encoding="utf-8") as fh:
        local_text = fh.read().replace("\r\n", "\n")

    _, remote_map = parse_declarations(remote_text)
    merged_text, stats = merge_local_with_remote(local_text, remote_map)

    print("=== Merge summary ===")
    print(f"Local declarations:  {stats['local_declarations']}")
    print(f"Remote declarations: {stats['remote_declarations']}")
    print(f"Replaced:            {stats['replaced']}")
    print(f"Unchanged matches:   {stats['unchanged']}")

    missing_in_remote = stats["missing_in_remote"]
    remote_only = stats["remote_only"]

    print(f"Missing in remote:   {len(missing_in_remote)}")
    if missing_in_remote:
        print("- Symbols present locally but missing remotely:")
        for name in missing_in_remote:
            print(f"  {name}")

    print(f"Remote-only symbols: {len(remote_only)}")
    if remote_only:
        print("- Symbols present remotely but not in local file:")
        for name in remote_only:
            print(f"  {name}")

    if args.dry_run:
        print("Dry-run mode: no file changes written.")
        return 0

    if merged_text == local_text:
        print("No changes needed.")
        return 0

    with open(local_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(merged_text)

    print(f"Updated file: {local_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

