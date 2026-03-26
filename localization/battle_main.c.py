"""Merge trainer class names into src/battle_main.c from a raw GitHub header.

Source format example:
    [TRAINER_CLASS_INTERVIEWER] = _("JOURNALISTES"),

Local format example:
    [TRAINER_CLASS_INTERVIEWER] = { _("INTERVIEWER"), 12 },

Only the quoted string in local entries is replaced; everything else is preserved.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.error
import urllib.request


DEFAULT_RAW_URL = "https://raw.githubusercontent.com/simsor/pokeemerald-fr/399793ce78d21e9b16c5e032bef0bf8da426b296/src/data/text/trainer_class_names.h"


REMOTE_ENTRY_RE = re.compile(
    r"^\s*\[(?P<key>TRAINER_CLASS_[A-Z0-9_]+)\]\s*=\s*_\(\"(?P<text>(?:[^\"\\]|\\.)*)\"\),\s*$",
    re.MULTILINE,
)


LOCAL_ENTRY_RE = re.compile(
    r"^(?P<prefix>\s*\[(?P<key>TRAINER_CLASS_[A-Z0-9_]+)\]\s*=\s*\{\s*_\(\")(?P<text>(?:[^\"\\]|\\.)*)(?P<suffix>\"\)\s*,.*\},\s*)$",
    re.MULTILINE,
)


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "trainer-class-merge-script/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to fetch URL: {url}\nReason: {exc}") from exc
    return data.decode("utf-8", errors="replace").replace("\r\n", "\n")


def parse_remote_entries(text: str) -> tuple[list[re.Match[str]], dict[str, str]]:
    matches = list(REMOTE_ENTRY_RE.finditer(text))
    mapping: dict[str, str] = {}
    for match in matches:
        mapping[match.group("key")] = match.group("text")
    return matches, mapping


def merge_local_with_remote(local_text: str, remote_map: dict[str, str]) -> tuple[str, dict[str, object]]:
    local_matches = list(LOCAL_ENTRY_RE.finditer(local_text))
    local_keys = {match.group("key") for match in local_matches}

    parts: list[str] = []
    last_end = 0
    replaced = 0
    unchanged = 0
    missing_in_remote: list[str] = []

    for match in local_matches:
        start, end = match.span(0)
        key = match.group("key")
        current_text = match.group("text")
        prefix = match.group("prefix")
        suffix = match.group("suffix")

        parts.append(local_text[last_end:start])

        if key in remote_map:
            remote_text = remote_map[key]
            replacement_line = f"{prefix}{remote_text}{suffix}"
            parts.append(replacement_line)
            if remote_text != current_text:
                replaced += 1
            else:
                unchanged += 1
        else:
            parts.append(match.group(0))
            missing_in_remote.append(key)

        last_end = end

    parts.append(local_text[last_end:])
    merged = "".join(parts)

    remote_only = sorted(key for key in remote_map if key not in local_keys)

    stats: dict[str, object] = {
        "local_entries": len(local_matches),
        "remote_entries": len(remote_map),
        "replaced": replaced,
        "unchanged": unchanged,
        "missing_in_remote": sorted(missing_in_remote),
        "remote_only": remote_only,
    }
    return merged, stats


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replace trainer class display names in src/battle_main.c from a raw trainer_class_names.h URL."
    )
    parser.add_argument("--url", default=DEFAULT_RAW_URL, help="Raw URL to source trainer_class_names.h")
    parser.add_argument(
        "--local",
        default=os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src", "battle_main.c")),
        help="Path to local battle_main.c",
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

    _, remote_map = parse_remote_entries(remote_text)
    merged_text, stats = merge_local_with_remote(local_text, remote_map)

    print("=== Merge summary ===")
    print(f"Local entries:       {stats['local_entries']}")
    print(f"Remote entries:      {stats['remote_entries']}")
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

