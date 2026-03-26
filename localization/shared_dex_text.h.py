"""Merge shared dex text entries from pokeemerald-fr into local shared_dex_text.h.

This script uses two remote sources:
1) Newer French file for translated text.
2) Older English file for legacy variable alignment when names changed.

Remote declaration format:
	const u8 gDummyPokedexText[] = _(
		"..."
		"...");

Local declaration format:
	const u8 gFallbackPokedexText[] = _(
		"..."
		"...");

Only declaration bodies inside _(... ) are replaced.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.error
import urllib.request


DEFAULT_URL_FR = "https://raw.githubusercontent.com/simsor/pokeemerald-fr/399793ce78d21e9b16c5e032bef0bf8da426b296/src/data/pokemon/pokedex_text.h"
DEFAULT_URL_OLD_EN = "https://raw.githubusercontent.com/simsor/pokeemerald-fr/2615ece23bd9463f3e43fca40eac1adcabeb2813/src/data/pokemon/pokedex_text.h"


DECL_RE = re.compile(
	r"(?P<full>^(?P<prefix>const\s+u8\s+(?P<name>[A-Za-z_]\w*)\[\]\s*=\s*_\(\n)"
	r"(?P<body>.*?)"
	r"(?P<suffix>\);\n?))",
	re.MULTILINE | re.DOTALL,
)


def fetch_text(url: str) -> str:
	req = urllib.request.Request(url, headers={"User-Agent": "shared-dex-merge-script/1.0"})
	try:
		with urllib.request.urlopen(req, timeout=30) as response:
			data = response.read()
	except urllib.error.URLError as exc:
		raise RuntimeError(f"Failed to fetch URL: {url}\\nReason: {exc}") from exc
	return data.decode("utf-8", errors="replace").replace("\r\n", "\n")


def parse_decls(text: str) -> list[tuple[str, str]]:
	return [(m.group("name"), m.group("body")) for m in DECL_RE.finditer(text)]


def build_legacy_map(fr_text: str, old_en_text: str) -> dict[str, str]:
	"""Map old English variable names to current French text by declaration order."""
	fr_decls = parse_decls(fr_text)
	old_decls = parse_decls(old_en_text)

	mapping: dict[str, str] = {}
	for (old_name, _old_body), (_fr_name, fr_body) in zip(old_decls, fr_decls):
		mapping[old_name] = fr_body
	return mapping


def local_aliases(name: str) -> list[str]:
	aliases = [name]
	if name.startswith("gFallback"):
		aliases.append("gDummy" + name[len("gFallback") :])
	return aliases


def merge_local(local_text: str, fr_text: str, old_en_text: str) -> tuple[str, dict[str, object]]:
	local_matches = list(DECL_RE.finditer(local_text))
	fr_map = {name: body for name, body in parse_decls(fr_text)}
	legacy_map = build_legacy_map(fr_text, old_en_text)

	parts: list[str] = []
	last_end = 0
	replaced = 0
	unchanged = 0
	missing: list[str] = []
	matched_via_legacy = 0

	for match in local_matches:
		start, end = match.span("full")
		name = match.group("name")
		old_body = match.group("body")

		parts.append(local_text[last_end:start])

		new_body = None
		used_legacy = False
		for candidate in local_aliases(name):
			if candidate in fr_map:
				new_body = fr_map[candidate]
				break
			if candidate in legacy_map:
				new_body = legacy_map[candidate]
				used_legacy = True
				break

		if new_body is None:
			parts.append(match.group("full"))
			missing.append(name)
		else:
			if used_legacy:
				matched_via_legacy += 1
			if new_body == old_body:
				unchanged += 1
				parts.append(match.group("full"))
			else:
				replaced += 1
				parts.append(f"{match.group('prefix')}{new_body}{match.group('suffix')}")

		last_end = end

	parts.append(local_text[last_end:])
	merged = "".join(parts)

	stats: dict[str, object] = {
		"local_entries": len(local_matches),
		"remote_fr_entries": len(fr_map),
		"legacy_entries": len(legacy_map),
		"replaced": replaced,
		"unchanged": unchanged,
		"matched_via_legacy": matched_via_legacy,
		"missing": sorted(missing),
	}
	return merged, stats


def main() -> int:
	parser = argparse.ArgumentParser(
		description="Replace local shared dex text bodies using French remote pokedex text with legacy name compatibility."
	)
	parser.add_argument("--url-fr", default=DEFAULT_URL_FR, help="Raw URL to current French pokedex_text.h")
	parser.add_argument("--url-old-en", default=DEFAULT_URL_OLD_EN, help="Raw URL to old English pokedex_text.h")
	parser.add_argument(
		"--local",
		default=os.path.normpath(
			os.path.join(
				os.path.dirname(__file__),
				"..",
				"src",
				"data",
				"pokemon",
				"species_info",
				"shared_dex_text.h",
			)
		),
		help="Path to local shared_dex_text.h",
	)
	parser.add_argument("--dry-run", action="store_true", help="Preview summary without writing file")
	args = parser.parse_args()

	local_path = os.path.abspath(args.local)
	if not os.path.exists(local_path):
		print(f"ERROR: local file not found: {local_path}")
		return 1

	try:
		fr_text = fetch_text(args.url_fr)
		old_en_text = fetch_text(args.url_old_en)
	except RuntimeError as exc:
		print(f"ERROR: {exc}")
		return 1

	with open(local_path, "r", encoding="utf-8") as fh:
		local_text = fh.read().replace("\r\n", "\n")

	merged, stats = merge_local(local_text, fr_text, old_en_text)

	print("=== Merge summary ===")
	print(f"Local entries:          {stats['local_entries']}")
	print(f"Remote FR entries:      {stats['remote_fr_entries']}")
	print(f"Legacy EN entries:      {stats['legacy_entries']}")
	print(f"Replaced:               {stats['replaced']}")
	print(f"Unchanged:              {stats['unchanged']}")
	print(f"Matched via legacy map: {stats['matched_via_legacy']}")
	print(f"Missing in remote map:  {len(stats['missing'])}")

	missing = stats["missing"]
	if missing:
		print(f"Missing entries ({len(missing)}):")
		for name in missing:
			print(f"  {name}")

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
