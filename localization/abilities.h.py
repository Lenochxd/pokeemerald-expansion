"""Merge ability names and descriptions into src/data/abilities.h.

Remote source (single file):
	static const u8 sSturdyDescription[] = _("...");
	...
	[ABILITY_STURDY] = _("FERMETE"),
	...
	[ABILITY_STURDY] = sSturdyDescription,

Local target format:
	[ABILITY_STURDY] =
	{
		.name = _("Sturdy"),
		.description = COMPOUND_STRING("Negates 1-hit KO attacks."),
		...
	},

Only .name and .description are replaced.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.error
import urllib.request


DEFAULT_RAW_URL = "https://raw.githubusercontent.com/simsor/pokeemerald-fr/399793ce78d21e9b16c5e032bef0bf8da426b296/src/data/text/abilities.h"


# Remote: static const u8 sSturdyDescription[] = _("...");
REMOTE_DESC_DECL_RE = re.compile(
	r"^static\s+const\s+u8\s+(?P<var>[A-Za-z_]\w*)\[\]\s*=\s*_\(\"(?P<text>(?:[^\"\\]|\\.)*)\"\)\s*;",
	re.MULTILINE,
)

# Remote: [ABILITY_STURDY] = _("FERMETE"),
REMOTE_NAME_RE = re.compile(
	r"\[(?P<key>ABILITY_[A-Z0-9_]+)\]\s*=\s*_\(\"(?P<text>(?:[^\"\\]|\\.)*)\"\)\s*,",
	re.MULTILINE,
)

# Remote: [ABILITY_STURDY] = sSturdyDescription,
REMOTE_DESC_PTR_RE = re.compile(
	r"\[(?P<key>ABILITY_[A-Z0-9_]+)\]\s*=\s*(?P<var>[A-Za-z_]\w*)\s*,",
	re.MULTILINE,
)


LOCAL_BLOCK_RE = re.compile(
	r"^(?P<indent>\s*)\[(?P<key>ABILITY_[A-Z0-9_]+)\]\s*=\s*\n"
	r"(?P=indent)\{\n"
	r"(?P<body>.*?)"
	r"(?P=indent)\},\s*$",
	re.MULTILINE | re.DOTALL,
)

LOCAL_NAME_LINE_RE = re.compile(
	r"^(?P<prefix>\s*\.name\s*=\s*_\(\")"
	r"(?P<text>(?:[^\"\\]|\\.)*)"
	r"(?P<suffix>\"\)\,\s*)$",
	re.MULTILINE,
)

LOCAL_DESC_FIELD_RE = re.compile(
	r"(?P<prefix>[ \t]*\.description\s*=\s*)"
	r"(?P<value>COMPOUND_STRING\(\s*(?:\"(?:[^\"\\]|\\.)*\"\s*)+\)|[A-Za-z_]\w*)"
	r"(?P<suffix>,[ \t]*\n?)",
	re.DOTALL,
)


def fetch_text(url: str) -> str:
	req = urllib.request.Request(url, headers={"User-Agent": "ability-merge-script/1.0"})
	try:
		with urllib.request.urlopen(req, timeout=30) as response:
			data = response.read()
	except urllib.error.URLError as exc:
		raise RuntimeError(f"Failed to fetch URL: {url}\\nReason: {exc}") from exc
	return data.decode("utf-8", errors="replace").replace("\r\n", "\n")


def parse_remote_names(remote_text: str) -> dict[str, str]:
	return {m.group("key"): m.group("text") for m in REMOTE_NAME_RE.finditer(remote_text)}


def parse_remote_descs(remote_text: str) -> dict[str, str]:
	desc_var_to_text = {
		m.group("var"): m.group("text") for m in REMOTE_DESC_DECL_RE.finditer(remote_text)
	}

	mapping: dict[str, str] = {}
	for m in REMOTE_DESC_PTR_RE.finditer(remote_text):
		key = m.group("key")
		var = m.group("var")
		if var in desc_var_to_text:
			mapping[key] = desc_var_to_text[var]
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

		if key in remote_names:
			nm = LOCAL_NAME_LINE_RE.search(new_body)
			if nm is None:
				missing_name_line.append(key)
			else:
				rname = remote_names[key]
				new_name_line = f"{nm.group('prefix')}{rname}{nm.group('suffix')}"
				new_body_after = new_body[: nm.start()] + new_name_line + new_body[nm.end() :]
				if new_body_after != new_body:
					names_replaced += 1
				else:
					names_unchanged += 1
				new_body = new_body_after
		else:
			missing_name.append(key)

		if key in remote_descs:
			dm = LOCAL_DESC_FIELD_RE.search(new_body)
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
		"remote_only_names": sorted(k for k in remote_names if k not in local_keys),
		"remote_only_descs": sorted(k for k in remote_descs if k not in local_keys),
	}
	return merged, stats


def main() -> int:
	parser = argparse.ArgumentParser(
		description="Replace ability .name and .description in src/data/abilities.h from raw GitHub abilities.h"
	)
	parser.add_argument("--url", default=DEFAULT_RAW_URL, help="Raw URL to abilities.h")
	parser.add_argument(
		"--local",
		default=os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src", "data", "abilities.h")),
		help="Path to local abilities.h",
	)
	parser.add_argument("--dry-run", action="store_true", help="Preview summary without writing file")
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

	remote_names = parse_remote_names(remote_text)
	remote_descs = parse_remote_descs(remote_text)
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
		for key in missing_name_line:
			print(f"  {key}")

	if missing_desc_field:
		print(f"Missing .description field ({len(missing_desc_field)}):")
		for key in missing_desc_field:
			print(f"  {key}")

	if remote_only_names:
		print(f"Remote-only names ({len(remote_only_names)}):")
		for key in remote_only_names:
			print(f"  {key}")

	if remote_only_descs:
		print(f"Remote-only desc keys ({len(remote_only_descs)}):")
		for key in remote_only_descs:
			print(f"  {key}")

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
