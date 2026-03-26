"""Merge move names and descriptions into src/data/moves_info.h.

Name source format:
    [MOVE_SWALLOW] = _("AVALE"),

Description source format:
    static const u8 sSwallowDescription[] = _("Avale les reserves...");

Local format:
    [MOVE_SWALLOW] =
    {
        .name = COMPOUND_STRING("Swallow"),
        .description = COMPOUND_STRING(
            "Absorbs stockpiled power\\n"
            "and restores HP."),
        ...
    },

Only .name and .description values are replaced.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.error
import urllib.request


DEFAULT_RAW_URL_NAMES = "https://raw.githubusercontent.com/simsor/pokeemerald-fr/399793ce78d21e9b16c5e032bef0bf8da426b296/src/data/text/move_names.h"
DEFAULT_RAW_URL_DESC = "https://raw.githubusercontent.com/simsor/pokeemerald-fr/399793ce78d21e9b16c5e032bef0bf8da426b296/src/data/text/move_descriptions.h"


REMOTE_NAME_RE = re.compile(
    r"\[(?P<key>MOVE_[A-Z0-9_]+)\]\s*=\s*_\(\"(?P<text>(?:[^\"\\]|\\.)*)\"\)\s*,",
    re.MULTILINE | re.DOTALL,
)

# Remote: static const u8 sXxxDescription[] = _("text");  OR  _()
REMOTE_DESC_RE = re.compile(
    r"^static\s+const\s+u8\s+(?P<var>[a-zA-Z_]\w*)\[\]\s*=\s*_\((?:\"(?P<text>(?:[^\"\\]|\\.)*)\")\)\s*;",
    re.MULTILINE,
)


LOCAL_BLOCK_RE = re.compile(
    r"^(?P<indent>\s*)\[(?P<key>MOVE_[A-Z0-9_]+)\]\s*=\s*\n"
    r"(?P=indent)\{\n"
    r"(?P<body>.*?)"
    r"(?P=indent)\},\s*$",
    re.MULTILINE | re.DOTALL,
)


NAME_LINE_RE = re.compile(
    r"^(?P<prefix>\s*\.name\s*=\s*COMPOUND_STRING\(\")"
    r"(?P<text>(?:[^\"\\]|\\.)*)"
    r"(?P<suffix>\"\)\,\s*)$",
    re.MULTILINE,
)

# Local: .description = COMPOUND_STRING("..." [...]) or a plain variable reference
DESC_FIELD_RE = re.compile(
    r"(?P<prefix>[ \t]*\.description\s*=\s*)"
    r"(?P<value>COMPOUND_STRING\(\s*(?:\"(?:[^\"\\]|\\.)*\"\s*)+\)|[A-Za-z_]\w*)"
    r"(?P<suffix>,[ \t]*\n?)",
    re.DOTALL,
)


def camel_to_upper_snake(s: str) -> str:
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    return s.upper()


def desc_var_to_move_key(var_name: str) -> str | None:
    """Convert e.g. 'sPoundDescription' -> 'MOVE_POUND'."""
    if not var_name.startswith("s") or not var_name.endswith("Description"):
        return None
    middle = var_name[1 : -len("Description")]
    if not middle:
        return None
    return f"MOVE_{camel_to_upper_snake(middle)}"


def fetch_text(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "move-name-merge-script/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read()
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to fetch URL: {url}\\nReason: {exc}") from exc
    return data.decode("utf-8", errors="replace").replace("\r\n", "\n")


def parse_remote_names(text: str) -> dict[str, str]:
    return {m.group("key"): m.group("text") for m in REMOTE_NAME_RE.finditer(text)}


def parse_remote_descs(text: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for m in REMOTE_DESC_RE.finditer(text):
        key = desc_var_to_move_key(m.group("var"))
        if key is None:
            continue
        mapping[key] = m.group("text") or ""
    return mapping


def merge_local_with_remote(
    local_text: str,
    remote_names: dict[str, str],
    remote_descs: dict[str, str],
) -> tuple[str, dict[str, object]]:
    local_matches = list(LOCAL_BLOCK_RE.finditer(local_text))
    local_keys = {match.group("key") for match in local_matches}

    parts: list[str] = []
    last_end = 0
    names_replaced = 0
    names_unchanged = 0
    descs_replaced = 0
    descs_unchanged = 0
    missing_name: list[str] = []
    missing_desc: list[str] = []
    missing_name_line: list[str] = []
    missing_desc_field: list[str] = []

    for match in local_matches:
        start, end = match.span(0)
        key = match.group("key")
        body = match.group("body")
        indent = match.group("indent")

        parts.append(local_text[last_end:start])
        new_body = body

        # -- replace .name --
        if key in remote_names:
            nm = NAME_LINE_RE.search(new_body)
            if nm is None:
                missing_name_line.append(key)
            else:
                rname = remote_names[key]
                new_name_line = f"{nm.group('prefix')}{rname}{nm.group('suffix')}"
                new_body = new_body[: nm.start()] + new_name_line + new_body[nm.end() :]
                if rname != nm.group("text"):
                    names_replaced += 1
                else:
                    names_unchanged += 1
        else:
            missing_name.append(key)

        # -- replace .description --
        if key in remote_descs:
            dm = DESC_FIELD_RE.search(new_body)
            if dm is None:
                missing_desc_field.append(key)
            else:
                rdesc = remote_descs[key]
                new_desc = f"{dm.group('prefix')}COMPOUND_STRING(\"{rdesc}\"){dm.group('suffix')}"
                new_body_after = new_body[: dm.start()] + new_desc + new_body[dm.end() :]
                if new_body_after != new_body:
                    descs_replaced += 1
                else:
                    descs_unchanged += 1
                new_body = new_body_after
        else:
            missing_desc.append(key)

        if new_body == body:
            parts.append(match.group(0))
        else:
            parts.append(
                f"{indent}[{key}] =\n"
                f"{indent}{{\n"
                f"{new_body}"
                f"{indent}}},"
            )
        last_end = end

    parts.append(local_text[last_end:])
    merged = "".join(parts)

    remote_only_names = sorted(k for k in remote_names if k not in local_keys)
    remote_only_descs = sorted(k for k in remote_descs if k not in local_keys)

    stats: dict[str, object] = {
        "local_blocks": len(local_matches),
        "remote_names": len(remote_names),
        "remote_descs": len(remote_descs),
        "names_replaced": names_replaced,
        "names_unchanged": names_unchanged,
        "descs_replaced": descs_replaced,
        "descs_unchanged": descs_unchanged,
        "missing_name": sorted(missing_name),
        "missing_desc": sorted(missing_desc),
        "missing_name_line": sorted(missing_name_line),
        "missing_desc_field": sorted(missing_desc_field),
        "remote_only_names": remote_only_names,
        "remote_only_descs": remote_only_descs,
    }
    return merged, stats


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replace move .name and .description in src/data/moves_info.h from raw GitHub headers."
    )
    parser.add_argument("--url-names", default=DEFAULT_RAW_URL_NAMES, help="Raw URL to move_names.h")
    parser.add_argument("--url-desc", default=DEFAULT_RAW_URL_DESC, help="Raw URL to move_descriptions.h")
    parser.add_argument(
        "--local",
        default=os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src", "data", "moves_info.h")),
        help="Path to local moves_info.h",
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
        names_text = fetch_text(args.url_names)
        desc_text = fetch_text(args.url_desc)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    with open(local_path, "r", encoding="utf-8") as fh:
        local_text = fh.read().replace("\r\n", "\n")

    remote_names = parse_remote_names(names_text)
    remote_descs = parse_remote_descs(desc_text)
    merged_text, stats = merge_local_with_remote(local_text, remote_names, remote_descs)

    print("=== Merge summary ===")
    print(f"Local blocks:           {stats['local_blocks']}")
    print(f"Remote names:           {stats['remote_names']}")
    print(f"Remote descriptions:    {stats['remote_descs']}")
    print(f"Names replaced:         {stats['names_replaced']}")
    print(f"Names unchanged:        {stats['names_unchanged']}")
    print(f"Descs replaced:         {stats['descs_replaced']}")
    print(f"Descs unchanged:        {stats['descs_unchanged']}")
    print(f"Missing name in remote: {len(stats['missing_name'])}")
    print(f"Missing desc in remote: {len(stats['missing_desc'])}")

    missing_name_line = stats["missing_name_line"]
    missing_desc_field = stats["missing_desc_field"]
    remote_only_names = stats["remote_only_names"]
    remote_only_descs = stats["remote_only_descs"]

    if missing_name_line:
        print(f"Missing .name line ({len(missing_name_line)}):")
        for k in missing_name_line:
            print(f"  {k}")

    if missing_desc_field:
        print(f"Missing .description field ({len(missing_desc_field)}):")
        for k in missing_desc_field:
            print(f"  {k}")

    if remote_only_names:
        print(f"Remote-only names ({len(remote_only_names)}):")
        for k in remote_only_names:
            print(f"  {k}")

    if remote_only_descs:
        print(f"Remote-only desc keys ({len(remote_only_descs)}):")
        for k in remote_only_descs:
            print(f"  {k}")

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
