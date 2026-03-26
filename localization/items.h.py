"""Merge item names and descriptions into src/data/items.h.

Remote sources:
1) items.h for item key -> French item name and description pointer variable.
2) item_descriptions.h for description pointer variable -> French description text.

Remote item format:
	[ITEM_ULTRA_BALL] =
	{
		.name = _("HYPER BALL"),
		...
		.description = sUltraBallDesc,
	},

Local format:
	[ITEM_ULTRA_BALL] =
	{
		.name = ITEM_NAME("Ultra Ball"),
		...
		.description = COMPOUND_STRING(
			"A better Ball with\n"
			"a higher catch rate\n"
			"than a Great Ball."),
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


DEFAULT_URL_ITEMS = "https://raw.githubusercontent.com/simsor/pokeemerald-fr/399793ce78d21e9b16c5e032bef0bf8da426b296/src/data/items.h"
DEFAULT_URL_ITEM_DESCS = "https://raw.githubusercontent.com/simsor/pokeemerald-fr/399793ce78d21e9b16c5e032bef0bf8da426b296/src/data/text/item_descriptions.h"


REMOTE_ITEM_BLOCK_RE = re.compile(
	r"\[(?P<key>ITEM_[A-Z0-9_]+)\]\s*=\s*\n"
	r"\s*\{\n"
	r"(?P<body>.*?)"
	r"\s*\},",
	re.DOTALL,
)

REMOTE_NAME_LINE_RE = re.compile(
	r"^\s*\.name\s*=\s*_\(\"(?P<text>(?:[^\"\\]|\\.)*)\"\)\s*,\s*$",
	re.MULTILINE,
)

REMOTE_DESC_PTR_RE = re.compile(
	r"^\s*\.description\s*=\s*(?P<var>[A-Za-z_]\w*)\s*,\s*$",
	re.MULTILINE,
)

REMOTE_DESC_DECL_RE = re.compile(
	r"^static\s+const\s+u8\s+(?P<var>[A-Za-z_]\w*)\[\]\s*=\s*_\(\n"
	r"(?P<body>.*?)"
	r"\);\s*$",
	re.MULTILINE | re.DOTALL,
)


LOCAL_BLOCK_RE = re.compile(
	r"^(?P<indent>\s*)\[(?P<key>ITEM_[A-Z0-9_]+)\]\s*=\s*\n"
	r"(?P=indent)\{\n"
	r"(?P<body>.*?)"
	r"(?P=indent)\},\s*$",
	re.MULTILINE | re.DOTALL,
)

LOCAL_NAME_LINE_RE = re.compile(
	r"^(?P<prefix>\s*\.name\s*=\s*(?:ITEM_NAME|_)\(\")"
	r"(?P<text>(?:[^\"\\]|\\.)*)"
	r"(?P<suffix>\"\)\s*,\s*)$",
	re.MULTILINE,
)

def fetch_text(url: str) -> str:
	req = urllib.request.Request(url, headers={"User-Agent": "item-merge-script/1.0"})
	try:
		with urllib.request.urlopen(req, timeout=30) as response:
			data = response.read()
	except urllib.error.URLError as exc:
		raise RuntimeError(f"Failed to fetch URL: {url}\\nReason: {exc}") from exc
	return data.decode("utf-8", errors="replace").replace("\r\n", "\n")


def parse_remote_item_map(items_text: str) -> dict[str, tuple[str, str]]:
	"""Return ITEM key -> (french_name, desc_var)."""
	mapping: dict[str, tuple[str, str]] = {}
	for m in REMOTE_ITEM_BLOCK_RE.finditer(items_text):
		key = m.group("key")
		body = m.group("body")
		nm = REMOTE_NAME_LINE_RE.search(body)
		dm = REMOTE_DESC_PTR_RE.search(body)
		if nm is None or dm is None:
			continue
		mapping[key] = (nm.group("text"), dm.group("var"))
	return mapping


def parse_remote_desc_bodies(desc_text: str) -> dict[str, str]:
	"""Return description var -> raw multiline string body inside _(...)."""
	return {m.group("var"): m.group("body") for m in REMOTE_DESC_DECL_RE.finditer(desc_text)}


def _normalize_desc_body(desc_body: str, inner_indent: str) -> list[str]:
	lines = desc_body.splitlines()
	non_empty = [line for line in lines if line.strip()]
	min_indent = 0
	if non_empty:
		min_indent = min(len(line) - len(line.lstrip(" \t")) for line in non_empty)
	return [f"{inner_indent}{line[min_indent:]}" if line else "" for line in lines]


def replace_description_fields(body: str, desc_body: str) -> tuple[str, int]:
	lines = body.split("\n")
	out: list[str] = []
	i = 0
	replaced = 0

	while i < len(lines):
		line = lines[i]
		m = re.match(r"^(?P<indent>[ \t]*)\.description\s*=\s*(?P<rest>.*)$", line)
		if m is None:
			out.append(line)
			i += 1
			continue

		indent = m.group("indent")
		rest = m.group("rest")
		end = i

		if "COMPOUND_STRING(" in rest:
			j = i
			pp_depth = 0
			saw_pp = False
			while j < len(lines):
				if j > i:
					stripped = lines[j].lstrip()
					if stripped.startswith("#if"):
						pp_depth += 1
						saw_pp = True
					elif stripped.startswith("#endif"):
						if pp_depth > 0:
							pp_depth -= 1
						if saw_pp and pp_depth == 0:
							end = j
							break

				if pp_depth == 0 and ")," in lines[j]:
					end = j
					break
				j += 1
		else:
			if "," in rest:
				end = i
			else:
				j = i + 1
				while j < len(lines):
					if "," in lines[j]:
						end = j
						break
					j += 1

		out.append(f"{indent}.description = COMPOUND_STRING(")
		out.extend(_normalize_desc_body(desc_body, f"{indent}    "))
		out.append(f"{indent}),")
		replaced += 1
		i = end + 1

	merged = "\n".join(out)
	if body.endswith("\n"):
		merged += "\n"
	return merged, replaced


def merge_local(
	local_text: str,
	remote_items: dict[str, tuple[str, str]],
	remote_desc_bodies: dict[str, str],
) -> tuple[str, dict[str, object]]:
	local_matches = list(LOCAL_BLOCK_RE.finditer(local_text))
	local_keys = {m.group("key") for m in local_matches}

	parts: list[str] = []
	last_end = 0

	names_replaced = 0
	names_unchanged = 0
	descs_replaced = 0
	descs_unchanged = 0

	missing_remote_item: list[str] = []
	missing_local_name_line: list[str] = []
	missing_local_desc_field: list[str] = []
	missing_remote_desc_var: list[str] = []

	for m in local_matches:
		start, end = m.span(0)
		indent = m.group("indent")
		key = m.group("key")
		body = m.group("body")

		parts.append(local_text[last_end:start])
		new_body = body

		if key not in remote_items:
			missing_remote_item.append(key)
			parts.append(m.group(0))
			last_end = end
			continue

		remote_name, remote_desc_var = remote_items[key]

		# Replace .name
		local_name = LOCAL_NAME_LINE_RE.search(new_body)
		if local_name is None:
			missing_local_name_line.append(key)
		else:
			new_name_line = (
				f"{local_name.group('prefix')}{remote_name}{local_name.group('suffix')}"
			)
			name_updated_body = new_body[: local_name.start()] + new_name_line + new_body[local_name.end() :]
			if name_updated_body != new_body:
				names_replaced += 1
			else:
				names_unchanged += 1
			new_body = name_updated_body

		# Replace .description using remote desc declaration text
		if remote_desc_var not in remote_desc_bodies:
			missing_remote_desc_var.append(f"{key}:{remote_desc_var}")
		else:
			desc_body = remote_desc_bodies[remote_desc_var]
			desc_updated_body, desc_count = replace_description_fields(new_body, desc_body)
			if desc_count == 0:
				missing_local_desc_field.append(key)
			else:
				if desc_updated_body != new_body:
					descs_replaced += 1
				else:
					descs_unchanged += 1
				new_body = desc_updated_body

		if new_body == body:
			parts.append(m.group(0))
		else:
			parts.append(
				f"{indent}[{key}] =\n"
				f"{indent}{{\n"
				f"{new_body}"
				f"{indent}}},"
			)

		last_end = end

	parts.append(local_text[last_end:])

	stats: dict[str, object] = {
		"local_blocks": len(local_matches),
		"remote_item_keys": len(remote_items),
		"remote_desc_vars": len(remote_desc_bodies),
		"names_replaced": names_replaced,
		"names_unchanged": names_unchanged,
		"descs_replaced": descs_replaced,
		"descs_unchanged": descs_unchanged,
		"missing_remote_item": sorted(missing_remote_item),
		"missing_local_name_line": sorted(missing_local_name_line),
		"missing_local_desc_field": sorted(missing_local_desc_field),
		"missing_remote_desc_var": sorted(missing_remote_desc_var),
		"remote_only_items": sorted(k for k in remote_items if k not in local_keys),
	}

	return "".join(parts), stats


def main() -> int:
	parser = argparse.ArgumentParser(
		description="Replace .name and .description in src/data/items.h from remote pokeemerald-fr sources."
	)
	parser.add_argument("--url-items", default=DEFAULT_URL_ITEMS, help="Raw URL to items.h")
	parser.add_argument(
		"--url-item-descs",
		default=DEFAULT_URL_ITEM_DESCS,
		help="Raw URL to item_descriptions.h",
	)
	parser.add_argument(
		"--local",
		default=os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src", "data", "items.h")),
		help="Path to local items.h",
	)
	parser.add_argument("--dry-run", action="store_true", help="Preview summary without writing file")
	args = parser.parse_args()

	local_path = os.path.abspath(args.local)
	if not os.path.exists(local_path):
		print(f"ERROR: local file not found: {local_path}")
		return 1

	try:
		items_text = fetch_text(args.url_items)
		item_descs_text = fetch_text(args.url_item_descs)
	except RuntimeError as exc:
		print(f"ERROR: {exc}")
		return 1

	with open(local_path, "r", encoding="utf-8") as fh:
		local_text = fh.read().replace("\r\n", "\n")

	remote_items = parse_remote_item_map(items_text)
	remote_desc_bodies = parse_remote_desc_bodies(item_descs_text)
	merged, stats = merge_local(local_text, remote_items, remote_desc_bodies)

	print("=== Merge summary ===")
	print(f"Local blocks:            {stats['local_blocks']}")
	print(f"Remote item keys:        {stats['remote_item_keys']}")
	print(f"Remote desc vars:        {stats['remote_desc_vars']}")
	print(f"Names replaced:          {stats['names_replaced']}")
	print(f"Names unchanged:         {stats['names_unchanged']}")
	print(f"Descriptions replaced:   {stats['descs_replaced']}")
	print(f"Descriptions unchanged:  {stats['descs_unchanged']}")
	print(f"Missing remote item key: {len(stats['missing_remote_item'])}")
	print(f"Missing local .name:     {len(stats['missing_local_name_line'])}")
	print(f"Missing local .desc:     {len(stats['missing_local_desc_field'])}")
	print(f"Missing remote desc var: {len(stats['missing_remote_desc_var'])}")

	if stats["missing_local_name_line"]:
		print(f"Missing local .name line ({len(stats['missing_local_name_line'])}):")
		for key in stats["missing_local_name_line"]:
			print(f"  {key}")

	if stats["missing_local_desc_field"]:
		print(f"Missing local .description field ({len(stats['missing_local_desc_field'])}):")
		for key in stats["missing_local_desc_field"]:
			print(f"  {key}")

	if stats["missing_remote_desc_var"]:
		print(f"Missing remote desc var ({len(stats['missing_remote_desc_var'])}):")
		for entry in stats["missing_remote_desc_var"]:
			print(f"  {entry}")

	if stats["remote_only_items"]:
		print(f"Remote-only item keys ({len(stats['remote_only_items'])}):")
		for key in stats["remote_only_items"]:
			print(f"  {key}")

	if args.dry_run:
		print("Dry-run mode: no file changes written.")
		return 0

	if merged == local_text:
		print("No changes needed.")
		return 0

	with open(local_path, "w", encoding="utf-8", newline="\n") as fh:
		fh.write(merged)

	print(f"Updated file: {local_path}")
	return 0


if __name__ == "__main__":
	sys.exit(main())
