"""Merge Pokedex category names into gen_1..gen_9 species info files.

Remote source format (pokedex_entries.h):
	[NATIONAL_DEX_BULBASAUR] =
	{
		.categoryName = _("GRAINE"),
		...
	},

Local target format (gen_*_families.h):
	[SPECIES_BULBASAUR] =
	{
		...
		.natDexNum = NATIONAL_DEX_BULBASAUR,
		.categoryName = _("Seed"),
		...
	},

The script updates only `.categoryName` based on `.natDexNum`.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.error
import urllib.request


DEFAULT_URL_FR = "https://raw.githubusercontent.com/simsor/pokeemerald-fr/399793ce78d21e9b16c5e032bef0bf8da426b296/src/data/pokemon/pokedex_entries.h"
DEFAULT_URL_OLD_EN = "https://raw.githubusercontent.com/simsor/pokeemerald-fr/a83fc52a7e393e44079abd0f616d75ad7fa230e8/src/data/pokemon/pokedex_entries.h"


REMOTE_ENTRY_RE = re.compile(
	r"\[(?P<key>NATIONAL_DEX_[A-Z0-9_]+)\]\s*=\s*\n"
	r"\s*\{\n"
	r"(?P<body>.*?)"
	r"\s*\},",
	re.DOTALL,
)

REMOTE_CATEGORY_RE = re.compile(
	r"^\s*\.categoryName\s*=\s*_\(\"(?P<text>(?:[^\"\\]|\\.)*)\"\)\s*,\s*$",
	re.MULTILINE,
)

LOCAL_BLOCK_RE = re.compile(
	r"^(?P<indent>\s*)\[(?P<species>SPECIES_[A-Z0-9_]+)\]\s*=\s*\n"
	r"(?P=indent)\{\n"
	r"(?P<body>.*?)"
	r"(?P=indent)\},\s*$",
	re.MULTILINE | re.DOTALL,
)

LOCAL_NATDEX_RE = re.compile(
	r"^\s*\.natDexNum\s*=\s*(?P<natdex>NATIONAL_DEX_[A-Z0-9_]+)\s*,\s*$",
	re.MULTILINE,
)

LOCAL_CATEGORY_RE = re.compile(
	r"^(?P<prefix>\s*\.categoryName\s*=\s*_\(\")"
	r"(?P<text>(?:[^\"\\]|\\.)*)"
	r"(?P<suffix>\"\)\s*,\s*)$",
	re.MULTILINE,
)


def fetch_text(url: str) -> str:
	req = urllib.request.Request(url, headers={"User-Agent": "pokedex-category-merge/1.0"})
	try:
		with urllib.request.urlopen(req, timeout=30) as response:
			data = response.read()
	except urllib.error.URLError as exc:
		raise RuntimeError(f"Failed to fetch URL: {url}\\nReason: {exc}") from exc
	return data.decode("utf-8", errors="replace").replace("\r\n", "\n")


def parse_remote_categories(text: str) -> list[tuple[str, str]]:
	out: list[tuple[str, str]] = []
	for entry in REMOTE_ENTRY_RE.finditer(text):
		key = entry.group("key")
		body = entry.group("body")
		cm = REMOTE_CATEGORY_RE.search(body)
		if cm is None:
			continue
		out.append((key, cm.group("text")))
	return out


def build_category_map(fr_text: str, old_en_text: str) -> tuple[dict[str, str], dict[str, str]]:
	"""Return (direct_fr_map, old_en_key_to_fr_category_map)."""
	fr_list = parse_remote_categories(fr_text)
	en_list = parse_remote_categories(old_en_text)

	fr_map = {k: v for k, v in fr_list}
	en_to_fr: dict[str, str] = {}
	for (en_key, _en_cat), (_fr_key, fr_cat) in zip(en_list, fr_list):
		en_to_fr[en_key] = fr_cat
	return fr_map, en_to_fr


def merge_local_text(
	local_text: str,
	fr_map: dict[str, str],
	en_to_fr: dict[str, str],
) -> tuple[str, dict[str, object]]:
	matches = list(LOCAL_BLOCK_RE.finditer(local_text))
	parts: list[str] = []
	last_end = 0

	replaced = 0
	unchanged = 0
	missing_natdex = 0
	missing_category_line = 0
	missing_remote = 0
	matched_via_legacy = 0
	missing_remote_keys: list[str] = []

	for m in matches:
		start, end = m.span(0)
		indent = m.group("indent")
		species = m.group("species")
		body = m.group("body")

		parts.append(local_text[last_end:start])

		nm = LOCAL_NATDEX_RE.search(body)
		if nm is None:
			missing_natdex += 1
			parts.append(m.group(0))
			last_end = end
			continue

		natdex = nm.group("natdex")
		new_category = None
		used_legacy = False
		if natdex in fr_map:
			new_category = fr_map[natdex]
		elif natdex in en_to_fr:
			new_category = en_to_fr[natdex]
			used_legacy = True

		if new_category is None:
			missing_remote += 1
			missing_remote_keys.append(f"{species}:{natdex}")
			parts.append(m.group(0))
			last_end = end
			continue

		if used_legacy:
			matched_via_legacy += 1

		cm = LOCAL_CATEGORY_RE.search(body)
		if cm is None:
			missing_category_line += 1
			parts.append(m.group(0))
			last_end = end
			continue

		new_line = f"{cm.group('prefix')}{new_category}{cm.group('suffix')}"
		new_body = body[: cm.start()] + new_line + body[cm.end() :]

		if new_body == body:
			unchanged += 1
			parts.append(m.group(0))
		else:
			replaced += 1
			parts.append(
				f"{indent}[{species}] =\n"
				f"{indent}{{\n"
				f"{new_body}"
				f"{indent}}},"
			)

		last_end = end

	parts.append(local_text[last_end:])

	stats: dict[str, object] = {
		"local_blocks": len(matches),
		"replaced": replaced,
		"unchanged": unchanged,
		"missing_natdex": missing_natdex,
		"missing_category_line": missing_category_line,
		"missing_remote": missing_remote,
		"matched_via_legacy": matched_via_legacy,
		"missing_remote_keys": sorted(missing_remote_keys),
	}
	return "".join(parts), stats


def default_local_files(script_dir: str) -> list[str]:
	base = os.path.normpath(
		os.path.join(script_dir, "..", "src", "data", "pokemon", "species_info")
	)
	return [os.path.join(base, f"gen_{i}_families.h") for i in range(1, 10)]


def main() -> int:
	parser = argparse.ArgumentParser(
		description="Replace .categoryName in gen_1..gen_9 family files using remote pokedex_entries.h."
	)
	parser.add_argument("--url-fr", default=DEFAULT_URL_FR, help="Raw URL to French pokedex_entries.h")
	parser.add_argument("--url-old-en", default=DEFAULT_URL_OLD_EN, help="Raw URL to older English pokedex_entries.h")
	parser.add_argument(
		"--files",
		nargs="*",
		help="Optional explicit local files to process (defaults to gen_1..gen_9 family files)",
	)
	parser.add_argument("--dry-run", action="store_true", help="Preview summary without writing files")
	args = parser.parse_args()

	script_dir = os.path.dirname(__file__)
	files = args.files if args.files else default_local_files(script_dir)
	files = [os.path.abspath(path) for path in files]

	missing_files = [path for path in files if not os.path.exists(path)]
	if missing_files:
		print("ERROR: some local files do not exist:")
		for path in missing_files:
			print(f"  {path}")
		return 1

	try:
		fr_text = fetch_text(args.url_fr)
		old_en_text = fetch_text(args.url_old_en)
	except RuntimeError as exc:
		print(f"ERROR: {exc}")
		return 1

	fr_map, en_to_fr = build_category_map(fr_text, old_en_text)

	print("=== Remote summary ===")
	print(f"FR categories:          {len(fr_map)}")
	print(f"Legacy key map entries: {len(en_to_fr)}")

	total_blocks = 0
	total_replaced = 0
	total_unchanged = 0
	total_missing_natdex = 0
	total_missing_category_line = 0
	total_missing_remote = 0
	total_matched_via_legacy = 0
	all_missing_remote_keys: list[str] = []

	for path in files:
		with open(path, "r", encoding="utf-8") as fh:
			local_text = fh.read().replace("\r\n", "\n")

		merged, stats = merge_local_text(local_text, fr_map, en_to_fr)

		total_blocks += int(stats["local_blocks"])
		total_replaced += int(stats["replaced"])
		total_unchanged += int(stats["unchanged"])
		total_missing_natdex += int(stats["missing_natdex"])
		total_missing_category_line += int(stats["missing_category_line"])
		total_missing_remote += int(stats["missing_remote"])
		total_matched_via_legacy += int(stats["matched_via_legacy"])
		all_missing_remote_keys.extend(stats["missing_remote_keys"])

		if not args.dry_run and merged != local_text:
			with open(path, "w", encoding="utf-8", newline="\n") as fh:
				fh.write(merged)

	print("=== Merge summary ===")
	print(f"Files processed:         {len(files)}")
	print(f"Local blocks:            {total_blocks}")
	print(f"Category replaced:       {total_replaced}")
	print(f"Category unchanged:      {total_unchanged}")
	print(f"Matched via legacy map:  {total_matched_via_legacy}")
	print(f"Missing .natDexNum:      {total_missing_natdex}")
	print(f"Missing .categoryName:   {total_missing_category_line}")
	print(f"Missing in remote map:   {total_missing_remote}")

	if all_missing_remote_keys:
		print(f"Missing remote keys ({len(all_missing_remote_keys)}):")
		for item in sorted(all_missing_remote_keys):
			print(f"  {item}")

	if args.dry_run:
		print("Dry-run mode: no file changes written.")
	else:
		print("Done.")

	return 0


if __name__ == "__main__":
	sys.exit(main())
