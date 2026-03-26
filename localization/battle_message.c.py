"""Merge battle message table strings into src/battle_message.c.

Remote source files:
1) French battle_message.c (current text source)
2) Older English battle_message.c (fallback alignment source)

Remote format uses symbol declarations plus a STRINGID->symbol table:
	static const u8 sText_PkmnGrewToLv[] = _("...");
	...
	[STRINGID_PKMNGREWTOLV - BATTLESTRINGS_TABLE_START] = sText_PkmnGrewToLv,

Local target format uses direct table entries:
	[STRINGID_PKMNGREWTOLV] = COMPOUND_STRING("..."),

Only entries currently using COMPOUND_STRING(...) are replaced.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.error
import urllib.request


DEFAULT_URL_FR = "https://raw.githubusercontent.com/simsor/pokeemerald-fr/399793ce78d21e9b16c5e032bef0bf8da426b296/src/battle_message.c"
DEFAULT_URL_OLD_EN = "https://raw.githubusercontent.com/simsor/pokeemerald-fr/5d4b76c0badffc2bf1d7b9db750971a95799277a/src/battle_message.c"


REMOTE_DECL_RE = re.compile(
	r"^(?:static\s+)?const\s+u8\s+(?P<name>[A-Za-z_]\w*)\[\]\s*=\s*_\((?P<body>.*?)\);\s*$",
	re.MULTILINE | re.DOTALL,
)

REMOTE_TABLE_RE = re.compile(
	r"^\s*\[(?P<key>STRINGID_[A-Z0-9_]+)\s*-\s*BATTLESTRINGS_TABLE_START\]\s*=\s*(?P<name>[A-Za-z_]\w*)\s*,",
	re.MULTILINE,
)

LOCAL_ENTRY_RE = re.compile(
	r"(?P<full>^(?P<indent>\s*)\[(?P<key>STRINGID_[A-Z0-9_]+)\]\s*=\s*"
	r"COMPOUND_STRING\((?P<body>.*?)\)\s*,(?P<comment>[ \t]*//[^\n]*)?\s*$)",
	re.MULTILINE | re.DOTALL,
)


def fetch_text(url: str) -> str:
	req = urllib.request.Request(url, headers={"User-Agent": "battle-message-merge/1.0"})
	try:
		with urllib.request.urlopen(req, timeout=30) as response:
			data = response.read()
	except urllib.error.URLError as exc:
		raise RuntimeError(f"Failed to fetch URL: {url}\\nReason: {exc}") from exc
	return data.decode("utf-8", errors="replace").replace("\r\n", "\n")


def parse_remote_decls(text: str) -> dict[str, str]:
	return {m.group("name"): m.group("body") for m in REMOTE_DECL_RE.finditer(text)}


def parse_remote_table(text: str) -> list[tuple[str, str]]:
	return [(m.group("key"), m.group("name")) for m in REMOTE_TABLE_RE.finditer(text)]


def build_remote_key_text_map(remote_text: str) -> tuple[dict[str, str], list[tuple[str, str]]]:
	decls = parse_remote_decls(remote_text)
	table = parse_remote_table(remote_text)
	key_to_text: dict[str, str] = {}
	for key, symbol in table:
		if symbol in decls:
			key_to_text[key] = decls[symbol]
	return key_to_text, table


def normalize_remote_body(body: str, inner_indent: str) -> tuple[str, bool]:
	"""Return normalized body and whether it's multiline."""
	lines = body.splitlines()
	if len(lines) <= 1:
		return body.strip(), False

	non_empty = [line for line in lines if line.strip()]
	min_indent = 0
	if non_empty:
		min_indent = min(len(line) - len(line.lstrip(" \t")) for line in non_empty)

	normalized = "\n".join(f"{inner_indent}{line[min_indent:]}" if line else "" for line in lines)
	return normalized, True


def _extract_macros(text: str) -> set[str]:
	"""Extract all macro references {MACRO_NAME} from text."""
	return set(re.findall(r'\{([A-Z_0-9]+)\}', text))


def _has_incompatible_macros(text: str, local_text: str) -> bool:
	"""Check if text contains macros not present in local_text."""
	fr_macros = _extract_macros(text)
	local_macros = _extract_macros(local_text)
	return bool(fr_macros - local_macros)


def _is_malformed(text: str) -> bool:
	"""Check if text appears malformed (contains declarations or other C syntax)."""
	# Check for stray C declarations in the text (indicates regex over-matched)
	if re.search(r'^\s*(?:static\s+)?const\s+', text, re.MULTILINE):
		return True
	# Check for unclosed string or suspicious patterns
	if '");' in text and not text.strip().endswith('"'):
		return True
	return False


def merge_local(
	local_text: str,
	fr_map: dict[str, str],
	fr_table: list[tuple[str, str]],
	old_en_table: list[tuple[str, str]],
) -> tuple[str, dict[str, object]]:
	# Fallback alignment by index between old EN and FR tables.
	aligned_old_to_fr: dict[str, str] = {}
	for (old_key, _), (fr_key, _) in zip(old_en_table, fr_table):
		if fr_key in fr_map:
			aligned_old_to_fr[old_key] = fr_map[fr_key]

	parts: list[str] = []
	last_end = 0

	replaced = 0
	unchanged = 0
	missing_remote: list[str] = []
	skipped_incompatible: list[str] = []

	for m in LOCAL_ENTRY_RE.finditer(local_text):
		start, end = m.span("full")
		indent = m.group("indent")
		key = m.group("key")
		old_body = m.group("body")
		comment = m.group("comment") or ""

		parts.append(local_text[last_end:start])

		new_body = None
		if key in fr_map:
			new_body = fr_map[key]
		elif key in aligned_old_to_fr:
			new_body = aligned_old_to_fr[key]

		if new_body is None:
			missing_remote.append(key)
			parts.append(m.group("full"))
			last_end = end
			continue

		# Check for malformed or incompatible remote text before replacing
		if _is_malformed(new_body):
			skipped_incompatible.append(key)
			parts.append(m.group("full"))
			last_end = end
			continue

		if _has_incompatible_macros(new_body, local_text):
			skipped_incompatible.append(key)
			parts.append(m.group("full"))
			last_end = end
			continue

		normalized, multiline = normalize_remote_body(new_body, indent + "    ")
		if multiline:
			replacement = (
				f"{indent}[{key}] = COMPOUND_STRING(\n"
				f"{normalized}"
				f"),{comment}"
			)
		else:
			replacement = f"{indent}[{key}] = COMPOUND_STRING({normalized}),{comment}"

		if replacement == m.group("full"):
			unchanged += 1
		else:
			replaced += 1
		parts.append(replacement)
		last_end = end

	parts.append(local_text[last_end:])

	stats: dict[str, object] = {
		"fr_mapped_keys": len(fr_map),
		"local_compound_entries": len(list(LOCAL_ENTRY_RE.finditer(local_text))),
		"replaced": replaced,
		"unchanged": unchanged,
		"missing_remote": sorted(set(missing_remote)),
		"skipped_incompatible_macros": len(skipped_incompatible),
	}
	return "".join(parts), stats


def main() -> int:
	parser = argparse.ArgumentParser(
		description="Replace local battle STRINGID COMPOUND_STRING entries from remote French battle_message.c."
	)
	parser.add_argument("--url-fr", default=DEFAULT_URL_FR, help="Raw URL to French battle_message.c")
	parser.add_argument("--url-old-en", default=DEFAULT_URL_OLD_EN, help="Raw URL to older English battle_message.c")
	parser.add_argument(
		"--local",
		default=os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "src", "battle_message.c")),
		help="Path to local battle_message.c",
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

	fr_map, fr_table = build_remote_key_text_map(fr_text)
	_old_map, old_en_table = build_remote_key_text_map(old_en_text)

	with open(local_path, "r", encoding="utf-8") as fh:
		local_text = fh.read().replace("\r\n", "\n")

	merged, stats = merge_local(local_text, fr_map, fr_table, old_en_table)

	print("=== Merge summary ===")
	print(f"Remote FR keys mapped:    {stats['fr_mapped_keys']}")
	print(f"Local COMPOUND entries:  {stats['local_compound_entries']}")
	print(f"Replaced:                {stats['replaced']}")
	print(f"Unchanged:               {stats['unchanged']}")
	print(f"Skipped (incompatible):  {stats['skipped_incompatible_macros']}")
	print(f"Missing in remote map:   {len(stats['missing_remote'])}")

	if stats["missing_remote"]:
		print(f"Missing keys ({len(stats['missing_remote'])}):")
		for key in stats["missing_remote"]:
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
