#!/usr/bin/env python3

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
import re


LABEL_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(::|:)\s*$")
MAP_SCRIPT_RE = re.compile(r"^\s*map_script\s+([^,]+?)\s*,\s*([A-Za-z_][A-Za-z0-9_]*)\s*$")
MAP_SCRIPT_2_RE = re.compile(r"^\s*map_script_2\s+([^,]+?)\s*,\s*([^,]+?)\s*,\s*([A-Za-z_][A-Za-z0-9_]*)\s*$")
STRING_RE = re.compile(r"^\s*\.string\s+(.*)$")
TEXT_DIRECTIVE_RE = re.compile(r'^\s*\.(ascii|[A-Za-z_][A-Za-z0-9_]*)\s+(".*")\s*$')
ITEM_RE = re.compile(r"^\s*\.2byte\s+(ITEM_[A-Za-z0-9_]+)\s*$")
ITEM_NONE_RE = re.compile(r"^\s*\.2byte\s+ITEM_NONE\s*$")
ALIGN_RE = re.compile(r"^\s*\.align\s+\d+\s*$")
BYTE_ZERO_RE = re.compile(r"^\s*\.byte\s+0\s*$")
HWORD_ZERO_RE = re.compile(r"^\s*\.2byte\s+0\s*$")
SWITCH_RE = re.compile(r"^\s*switch\s+(.+?)\s*$")
CASE_RE = re.compile(r"^\s*case\s+([^,]+?)\s*,\s*([A-Za-z_][A-Za-z0-9_]*)\s*$")
COMMENT_LINE_RE = re.compile(r"^\s*@\s?(.*)$")
CALL_CMD_RE = re.compile(r"^\s*call\s+([A-Za-z_][A-Za-z0-9_]*)\s*$")
PORY_CALL_RE = re.compile(r"^call\(([A-Za-z_][A-Za-z0-9_]*)\)(?:\s*//.*)?$")
PORY_GOTO_RE = re.compile(r"^goto\(([A-Za-z_][A-Za-z0-9_]*)\)(?:\s*//.*)?$")
PORY_CONDITIONAL_RE = re.compile(r"^(goto|call)_if_(eq|ne|lt|le|gt|ge|set|unset)\((.*)\)(?:\s*//\s*(.*))?$")

DEFAULT_SCOPE = {
	"script": "global",
	"text": "global",
	"movement": "local",
	"mart": "local",
	"mapscripts": "global",
}


@dataclass
class Block:
	label: str
	scope: str
	prelude: list[str]
	body: list[str]


@dataclass
class ConversionStats:
	scripts: int = 0
	texts: int = 0
	movements: int = 0
	marts: int = 0
	mapscripts: int = 0
	raw_blocks: int = 0
	folded_tables: int = 0


@dataclass
class ConversionResult:
	lines: list[str]
	raw_lines: list[str] = field(default_factory=list)


@dataclass
class ConditionalLine:
	action: str
	op: str
	args: list[str]
	comment: str | None = None


def parse_blocks(text: str) -> tuple[list[str], list[Block], list[str]]:
	lines = text.splitlines()
	leading: list[str] = []
	blocks: list[Block] = []
	prelude: list[str] = []
	current_label: str | None = None
	current_scope: str | None = None
	current_prelude: list[str] = []
	current_body: list[str] = []

	for line in lines:
		match = LABEL_RE.match(line)
		if match:
			if current_label is None:
				if not blocks:
					leading = prelude
				else:
					blocks[-1].body.extend(prelude)
				prelude = []
			else:
				blocks.append(Block(current_label, current_scope or "global", current_prelude, current_body))
			current_label = match.group(1)
			current_scope = "global" if match.group(2) == "::" else "local"
			current_prelude = prelude
			prelude = []
			current_body = []
			continue

		if current_label is None:
			prelude.append(line)
		else:
			current_body.append(line)

	trailing: list[str] = []
	if current_label is None:
		trailing = prelude
		if not blocks:
			leading = prelude
			trailing = []
	else:
		blocks.append(Block(current_label, current_scope or "global", current_prelude, current_body))
		trailing = prelude

	return leading, blocks, trailing


def is_blank(line: str) -> bool:
	return not line.strip()


def is_comment(line: str) -> bool:
	return COMMENT_LINE_RE.match(line) is not None


def comment_to_pory(line: str) -> str:
	match = COMMENT_LINE_RE.match(line)
	if match is None:
		return line
	content = match.group(1)
	return "//" if content == "" else f"// {content}"


def split_asm_comment(line: str) -> tuple[str, str | None]:
	in_quotes = False
	escaped = False
	for index, char in enumerate(line):
		if char == '"' and not escaped:
			in_quotes = not in_quotes
		if char == "@" and not in_quotes:
			return line[:index].rstrip(), line[index + 1 :].strip()
		escaped = char == "\\" and not escaped
		if char != "\\":
			escaped = False
	return line.rstrip(), None


def significant(line: str) -> bool:
	return not is_blank(line) and not is_comment(line)


def indent(lines: list[str], level: int = 1) -> list[str]:
	prefix = "\t" * level
	return [prefix + line if line else "" for line in lines]


def render_statement_header(kind: str, label: str, scope: str) -> str:
	default_scope = DEFAULT_SCOPE[kind]
	if scope == default_scope:
		return f"{kind} {label} {{"
	return f"{kind}({scope}) {label} {{"


def render_raw_block(lines: list[str]) -> list[str]:
	if not any(line.strip() for line in lines):
		return []
	output = ["raw `"]
	output.extend(lines)
	output.append("`")
	return output


def render_free_lines(lines: list[str]) -> list[str]:
	output: list[str] = []
	raw_buffer: list[str] = []
	for line in lines:
		if ALIGN_RE.match(line):
			continue
		if is_comment(line):
			if raw_buffer:
				output.extend(render_raw_block(raw_buffer))
				output.append("")
				raw_buffer = []
			output.append(comment_to_pory(line))
		elif is_blank(line):
			if raw_buffer:
				output.extend(render_raw_block(raw_buffer))
				output.append("")
				raw_buffer = []
			output.append("")
		else:
			raw_buffer.append(line)
	if raw_buffer:
		output.extend(render_raw_block(raw_buffer))
	return trim_blank_edges(output)


def trim_blank_edges(lines: list[str]) -> list[str]:
	while lines and lines[0] == "":
		lines.pop(0)
	while lines and lines[-1] == "":
		lines.pop()
	return lines


def merge_sections(sections: list[list[str]]) -> list[str]:
	output: list[str] = []
	for section in sections:
		section = trim_blank_edges(section)
		if not section:
			continue
		if output:
			output.append("")
		output.extend(section)
	return output


def parse_mapscript_root(block: Block) -> tuple[list[tuple[str, str]], list[str], list[str]] | None:
	entries: list[tuple[str, str]] = []
	comments: list[str] = []
	found_terminator = False
	tail: list[str] = []
	for index, line in enumerate(block.body):
		if not found_terminator:
			if is_blank(line):
				comments.append("")
				continue
			if is_comment(line):
				comments.append(comment_to_pory(line))
				continue
			match = MAP_SCRIPT_RE.match(line)
			if match:
				entries.append((match.group(1).strip(), match.group(2).strip()))
				continue
			if BYTE_ZERO_RE.match(line):
				found_terminator = True
				tail = block.body[index + 1 :]
				continue
			return None
		else:
			tail.append(line)
	if not found_terminator:
		return None
	return entries, comments, tail


def parse_mapscript_table(block: Block) -> tuple[list[tuple[str, str, str]], list[str], list[str]] | None:
	rows: list[tuple[str, str, str]] = []
	comments: list[str] = []
	found_terminator = False
	tail: list[str] = []
	for index, line in enumerate(block.body):
		if not found_terminator:
			if is_blank(line):
				comments.append("")
				continue
			if is_comment(line):
				comments.append(comment_to_pory(line))
				continue
			match = MAP_SCRIPT_2_RE.match(line)
			if match:
				rows.append((match.group(1).strip(), match.group(2).strip(), match.group(3).strip()))
				continue
			if HWORD_ZERO_RE.match(line):
				found_terminator = True
				tail = block.body[index + 1 :]
				continue
			return None
		else:
			tail.append(line)
	if not found_terminator:
		return None
	return rows, comments, tail


def parse_text_block(block: Block) -> tuple[list[str], list[str]] | None:
	values: list[str] = []
	tail: list[str] = []
	for index, line in enumerate(block.body):
		if is_blank(line):
			values.append("")
			continue
		if is_comment(line):
			values.append(comment_to_pory(line))
			continue
		match = STRING_RE.match(line)
		if match:
			values.append(match.group(1).strip())
			continue
		match = TEXT_DIRECTIVE_RE.match(line)
		if match:
			values.append(f"{match.group(1)}{match.group(2)}")
			continue
		tail = block.body[index:]
		break
	if not values or any(significant(line) and not (line.startswith('"') or line.startswith("ascii\"") or line.startswith("//") or not line) and not re.match(r"^[A-Za-z_][A-Za-z0-9_]*\"", line) for line in values):
		return None
	return values, tail


def parse_movement_block(block: Block) -> tuple[list[str], list[str]] | None:
	commands: list[str] = []
	found_end = False
	tail: list[str] = []
	for index, line in enumerate(block.body):
		if not found_end:
			if is_blank(line):
				commands.append("")
				continue
			if is_comment(line):
				commands.append(comment_to_pory(line))
				continue
			code, comment = split_asm_comment(line)
			stripped = code.strip()
			if not stripped:
				if comment is not None:
					commands.append(f"// {comment}" if comment else "//")
				continue
			if stripped.startswith("."):
				return None
			rendered = stripped
			if comment is not None:
				rendered = f"{rendered} // {comment}" if comment else rendered
			commands.append(rendered)
			if stripped == "step_end":
				found_end = True
				tail = block.body[index + 1 :]
		else:
			tail.append(line)
	if not found_end:
		return None
	return commands, tail


def parse_mart_block(block: Block) -> tuple[list[str], list[str]] | None:
	if block.scope != "local":
		return None
	items: list[str] = []
	found_terminator = False
	tail: list[str] = []
	for index, line in enumerate(block.body):
		if not found_terminator:
			if is_blank(line):
				continue
			if is_comment(line):
				return None
			if ITEM_NONE_RE.match(line) or line.strip() == "pokemartlistend":
				found_terminator = True
				tail = block.body[index + 1 :]
				continue
			match = ITEM_RE.match(line)
			if match:
				items.append(match.group(1))
				continue
			return None
		else:
			tail.append(line)
	if not found_terminator:
		return None
	return items, tail


def wrap_switch_operand(operand: str) -> str:
	operand = operand.strip()
	if operand.startswith("var(") or operand.startswith("check") or operand.startswith("specialvar("):
		return operand
	if operand.startswith("VAR_"):
		return f"var({operand})"
	return f"var({operand})"


def split_argument_list(text: str) -> list[str]:
	parts: list[str] = []
	current: list[str] = []
	depth = 0
	in_quotes = False
	escaped = False
	for char in text:
		if char == '"' and not escaped:
			in_quotes = not in_quotes
		elif char == '(' and not in_quotes:
			depth += 1
		elif char == ')' and not in_quotes and depth > 0:
			depth -= 1
		elif char == ',' and not in_quotes and depth == 0:
			parts.append("".join(current).strip())
			current = []
			escaped = False
			continue
		current.append(char)
		if char == "\\" and not escaped:
			escaped = True
		else:
			escaped = False
	if current:
		parts.append("".join(current).strip())
	return parts


def parse_pory_conditional(line: str) -> ConditionalLine | None:
	match = PORY_CONDITIONAL_RE.match(line.strip())
	if match is None:
		return None
	args = split_argument_list(match.group(3))
	expected_count = 2 if match.group(2) in {"set", "unset"} else 3
	if len(args) != expected_count:
		return None
	comment = match.group(4).strip() if match.group(4) else None
	return ConditionalLine(match.group(1), match.group(2), args, comment)


def parse_pory_unconditional(line: str) -> tuple[str, str] | None:
	stripped = line.strip()
	match = PORY_GOTO_RE.match(stripped)
	if match is not None:
		return "goto", match.group(1)
	match = PORY_CALL_RE.match(stripped)
	if match is not None:
		return "call", match.group(1)
	return None


def render_pory_action(action: str, target: str) -> str:
	return f"{action}({target})"


def render_condition(line: ConditionalLine) -> str:
	if line.op == "set":
		return f"flag({line.args[0]})"
	if line.op == "unset":
		return f"!flag({line.args[0]})"
	operator = {
		"eq": "==",
		"ne": "!=",
		"lt": "<",
		"le": "<=",
		"gt": ">",
		"ge": ">=",
	}[line.op]
	left = wrap_switch_operand(line.args[0])
	return f"{left} {operator} {line.args[1]}"


def can_render_call_chain_as_elif(conditionals: list[ConditionalLine]) -> bool:
	if not conditionals:
		return False
	first = conditionals[0]
	if any(line.action != "call" for line in conditionals):
		return False
	if first.op in {"set", "unset"}:
		if any(line.args[0] != first.args[0] for line in conditionals):
			return False
		ops = {line.op for line in conditionals}
		return ops <= {"set", "unset"} and len(conditionals) == len(ops)
	if first.op != "eq":
		return False
	if any(line.op != "eq" for line in conditionals):
		return False
	if any(line.args[0] != first.args[0] for line in conditionals):
		return False
	values = [line.args[1] for line in conditionals]
	return len(values) == len(set(values))


def render_if_block(keyword: str, condition: str, action_line: str, comment: str | None = None) -> list[str]:
	header = f"{keyword} ({condition}) {{"
	if comment:
		header = f"{header} // {comment}"
	return [header, f"\t{action_line}", "}"]


def optimize_conditionals(script_lines: list[str]) -> list[str]:
	optimized: list[str] = []
	index = 0
	while index < len(script_lines):
		conditional = parse_pory_conditional(script_lines[index])
		if conditional is None:
			optimized.append(script_lines[index])
			index += 1
			continue

		if conditional.action == "goto":
			chain: list[ConditionalLine] = [conditional]
			probe = index + 1
			while probe < len(script_lines):
				next_conditional = parse_pory_conditional(script_lines[probe])
				if next_conditional is None or next_conditional.action != "goto":
					break
				chain.append(next_conditional)
				probe += 1
			fallback = parse_pory_unconditional(script_lines[probe]) if probe < len(script_lines) else None
			if fallback is not None and fallback[0] != "goto":
				fallback = None

			keyword = "if"
			for line in chain:
				optimized.extend(
					render_if_block(
						keyword,
						render_condition(line),
						render_pory_action("goto", line.args[-1]),
						line.comment,
					)
				)
				keyword = "elif"
			if fallback is not None:
				optimized.extend(["else {", f"\t{render_pory_action('goto', fallback[1])}", "}"])
				probe += 1
			index = probe
			continue

		chain = [conditional]
		probe = index + 1
		while probe < len(script_lines):
			next_conditional = parse_pory_conditional(script_lines[probe])
			if next_conditional is None or next_conditional.action != "call":
				break
			chain.append(next_conditional)
			probe += 1

		if can_render_call_chain_as_elif(chain):
			keyword = "if"
			for line in chain:
				optimized.extend(
					render_if_block(
						keyword,
						render_condition(line),
						render_pory_action("call", line.args[-1]),
						line.comment,
					)
				)
				keyword = "elif"
		else:
			for line in chain:
				optimized.extend(
					render_if_block(
						"if",
						render_condition(line),
						render_pory_action("call", line.args[-1]),
						line.comment,
					)
				)
		index = probe

	return optimized


def convert_script_lines(lines: list[str]) -> tuple[list[str], list[str]] | None:
	output: list[str] = []
	tail: list[str] = []
	index = 0
	seen_terminal = False
	while index < len(lines):
		line = lines[index]
		if seen_terminal:
			tail.extend(lines[index:])
			break
		if is_blank(line):
			output.append("")
			index += 1
			continue
		if is_comment(line):
			output.append(comment_to_pory(line))
			index += 1
			continue

		code, comment = split_asm_comment(line)
		stripped = code.strip()
		if not stripped:
			output.append(f"// {comment}" if comment else "//")
			index += 1
			continue
		if stripped.startswith("."):
			return None

		switch_match = SWITCH_RE.match(stripped)
		if switch_match:
			cases: list[tuple[str, str]] = []
			comment_lines: list[str] = []
			probe = index + 1
			while probe < len(lines):
				probe_line = lines[probe]
				if is_blank(probe_line):
					comment_lines.append("")
					probe += 1
					continue
				if is_comment(probe_line):
					comment_lines.append(comment_to_pory(probe_line))
					probe += 1
					continue
				case_match = CASE_RE.match(probe_line.strip())
				if case_match:
					cases.append((case_match.group(1).strip(), case_match.group(2).strip()))
					probe += 1
					continue
				break
			if not cases:
				return None
			header = f"switch ({wrap_switch_operand(switch_match.group(1))}) {{"
			if comment is not None:
				header = f"{header} // {comment}" if comment else header
			output.append(header)
			for comment_line in comment_lines:
				output.append(f"\t{comment_line}" if comment_line else "")
			for value, target in cases:
				output.append(f"\tcase {value}: goto({target})")
			output.append("}")
			index = probe
			continue

		pieces = stripped.split(None, 1)
		if len(pieces) == 1:
			rendered = pieces[0]
			if pieces[0] in {"end", "return"}:
				seen_terminal = True
		else:
			rendered = f"{pieces[0]}({pieces[1].strip()})"
		if comment is not None:
			rendered = f"{rendered} // {comment}" if comment else rendered
		output.append(rendered)
		index += 1

	return trim_blank_edges(output), tail


class IncToPoryConverter:
	def __init__(
		self,
		source_path: Path,
		include_header: bool = True,
		minimize_calls: bool = True,
		global_call_usage: dict[str, int] | None = None,
	):
		self.source_path = source_path
		self.include_header = include_header
		self.minimize_calls = minimize_calls
		self.global_call_usage = global_call_usage or {}
		self.stats = ConversionStats()
		self.blocks_by_label: dict[str, Block] = {}
		self.consumed_labels: set[str] = set()
		self.inlined_call_targets: set[str] = set()

	def convert(self, text: str) -> tuple[str, ConversionStats]:
		leading, blocks, trailing = parse_blocks(text)
		self.blocks_by_label = {block.label: block for block in blocks}

		sections: list[list[str]] = []
		if self.include_header:
			sections.append([f"// Generated from {self.source_path.as_posix()} by dev_scripts/inc_to_pory.py"])

		free_leading = render_free_lines(leading)
		if free_leading:
			sections.append(free_leading)

		for block in blocks:
			if block.label in self.consumed_labels:
				continue
			converted = self.convert_block(block)
			sections.append(converted)

		free_trailing = render_free_lines(trailing)
		if free_trailing:
			sections.append(free_trailing)

		return "\n".join(merge_sections(sections)) + "\n", self.stats

	def convert_block(self, block: Block) -> list[str]:
		mapscript_root = parse_mapscript_root(block)
		if mapscript_root is not None:
			rendered = self.render_mapscripts(block, mapscript_root)
			if rendered is not None:
				self.stats.mapscripts += 1
				return rendered

		text_block = parse_text_block(block)
		if text_block is not None:
			self.stats.texts += 1
			return self.render_text(block, *text_block)

		movement_block = parse_movement_block(block)
		if movement_block is not None:
			self.stats.movements += 1
			return self.render_movement(block, *movement_block)

		mart_block = parse_mart_block(block)
		if mart_block is not None:
			self.stats.marts += 1
			return self.render_mart(block, *mart_block)

		script_block = convert_script_lines(block.body)
		if script_block is not None and self.prelude_is_comment_only(block.prelude):
			self.stats.scripts += 1
			return self.render_script(block, *script_block)

		self.stats.raw_blocks += 1
		return self.render_block_as_raw(block)

	def prelude_is_comment_only(self, prelude: list[str], allow_align: bool = False) -> bool:
		for line in prelude:
			if is_blank(line) or is_comment(line):
				continue
			if allow_align and ALIGN_RE.match(line):
				continue
			return False
		return True

	def render_block_comments(self, prelude: list[str], allow_align: bool = False) -> list[str] | None:
		if not self.prelude_is_comment_only(prelude, allow_align=allow_align):
			return None
		output: list[str] = []
		for line in prelude:
			if is_blank(line):
				output.append("")
			elif is_comment(line):
				output.append(comment_to_pory(line))
		return output

	def render_mapscripts(
		self,
		block: Block,
		parsed: tuple[list[tuple[str, str]], list[str], list[str]],
	) -> list[str] | None:
		prelude = self.render_block_comments(block.prelude)
		if prelude is None:
			return None
		entries, comments, tail = parsed
		body: list[str] = []
		comment_index = 0
		for comment_line in comments:
			if comment_line:
				body.append(comment_line)
			else:
				body.append("")
			comment_index += 1
		for map_type, target in entries:
			helper = self.blocks_by_label.get(target)
			helper_rows = parse_mapscript_table(helper) if helper is not None else None
			helper_comments = self.render_block_comments(helper.prelude) if helper is not None else None
			if helper is not None and helper_rows is not None and helper_comments is not None:
				rows, row_comments, helper_tail = helper_rows
				if not any(significant(line) for line in helper_tail) and helper.scope == "local":
					if helper_comments:
						body.extend(helper_comments)
					body.append(f"{map_type} [")
					for row_comment in row_comments:
						if row_comment:
							body.append(f"\t{row_comment}")
						else:
							body.append("")
					for var_name, value, label in rows:
						body.append(f"\t{var_name}, {value}: {label}")
					body.append("]")
					self.consumed_labels.add(helper.label)
					self.stats.folded_tables += 1
					continue
			body.append(f"{map_type}: {target}")

		rendered: list[str] = []
		if prelude:
			rendered.extend(prelude)
		rendered.append(render_statement_header("mapscripts", block.label, block.scope))
		if body:
			rendered.extend(indent(body))
		rendered.append("}")
		tail_rendered = render_free_lines(tail)
		return merge_sections([rendered, tail_rendered])

	def render_text(self, block: Block, values: list[str], tail: list[str]) -> list[str]:
		prelude = self.render_block_comments(block.prelude, allow_align=True)
		if prelude is None:
			return self.render_block_as_raw(block)
		rendered: list[str] = []
		if prelude:
			rendered.extend(prelude)
		rendered.append(render_statement_header("text", block.label, block.scope))
		rendered.extend(indent(trim_blank_edges(values)))
		rendered.append("}")
		tail_rendered = render_free_lines(tail)
		return merge_sections([rendered, tail_rendered])

	def render_movement(self, block: Block, commands: list[str], tail: list[str]) -> list[str]:
		prelude = self.render_block_comments(block.prelude, allow_align=True)
		if prelude is None:
			return self.render_block_as_raw(block)
		rendered: list[str] = []
		if prelude:
			rendered.extend(prelude)
		rendered.append(render_statement_header("movement", block.label, block.scope))
		rendered.extend(indent(trim_blank_edges(commands)))
		rendered.append("}")
		tail_rendered = render_free_lines(tail)
		return merge_sections([rendered, tail_rendered])

	def render_mart(self, block: Block, items: list[str], tail: list[str]) -> list[str]:
		prelude = self.render_block_comments(block.prelude, allow_align=True)
		if prelude is None:
			return self.render_block_as_raw(block)
		rendered: list[str] = []
		if prelude:
			rendered.extend(prelude)
		rendered.append("mart {0} {{".format(block.label))
		rendered.extend(indent(items))
		rendered.append("}")
		tail_rendered = render_free_lines(tail)
		return merge_sections([rendered, tail_rendered])

	def render_script(self, block: Block, script_lines: list[str], tail: list[str]) -> list[str]:
		prelude = self.render_block_comments(block.prelude)
		if prelude is None:
			return self.render_block_as_raw(block)
		if self.minimize_calls:
			script_lines = self.inline_single_use_calls(script_lines, block.label, set())
			script_lines = optimize_conditionals(script_lines)
		rendered: list[str] = []
		if prelude:
			rendered.extend(prelude)
		rendered.append(render_statement_header("script", block.label, block.scope))
		rendered.extend(indent(script_lines))
		rendered.append("}")
		tail_rendered = render_free_lines(tail)
		return merge_sections([rendered, tail_rendered])

	def inline_single_use_calls(self, script_lines: list[str], owner_label: str, stack: set[str]) -> list[str]:
		output: list[str] = []
		for line in script_lines:
			match = PORY_CALL_RE.match(line.strip())
			if match is None:
				output.append(line)
				continue

			target_label = match.group(1)
			if self.global_call_usage.get(target_label, 0) != 1:
				output.append(line)
				continue
			if target_label == owner_label or target_label in stack:
				output.append(line)
				continue

			target_block = self.blocks_by_label.get(target_label)
			if target_block is None:
				output.append(line)
				continue
			if not self.prelude_is_comment_only(target_block.prelude):
				output.append(line)
				continue

			target_script = convert_script_lines(target_block.body)
			if target_script is None:
				output.append(line)
				continue
			target_lines, target_tail = target_script
			if any(significant(tail_line) for tail_line in target_tail):
				output.append(line)
				continue
			if not target_lines:
				output.append(line)
				continue
			if target_lines[-1].strip() != "return":
				output.append(line)
				continue

			inlined_lines = target_lines[:-1]
			if not inlined_lines:
				continue

			inline_prefix_comments = self.render_block_comments(target_block.prelude) or []
			inlined_lines = [*inline_prefix_comments, *inlined_lines]
			inlined_lines = self.inline_single_use_calls(inlined_lines, target_label, {target_label, *stack})
			self.inlined_call_targets.add(target_label)
			output.extend(inlined_lines)
		return output

	def render_block_as_raw(self, block: Block) -> list[str]:
		raw_lines = [*block.prelude, f"{block.label}{'::' if block.scope == 'global' else ':'}", *block.body]
		return render_raw_block(raw_lines)


def translate_path(
	input_path: Path,
	output_path: Path | None,
	include_header: bool,
	minimize_calls: bool,
	global_call_usage: dict[str, int],
) -> ConversionStats:
	converter = IncToPoryConverter(
		input_path,
		include_header=include_header,
		minimize_calls=minimize_calls,
		global_call_usage=global_call_usage,
	)
	converted_text, stats = converter.convert(input_path.read_text(encoding="utf-8"))
	if output_path is None:
		sys.stdout.write(converted_text)
	else:
		output_path.parent.mkdir(parents=True, exist_ok=True)
		output_path.write_text(converted_text, encoding="utf-8")
	return stats


def collect_inputs(input_path: Path) -> list[Path]:
	if input_path.is_dir():
		return sorted(path for path in input_path.rglob("*.inc") if path.is_file())
	return [input_path]


def count_call_usage(root_path: Path) -> dict[str, int]:
	usage: dict[str, int] = {}
	if root_path.is_file():
		inc_paths = [root_path] if root_path.suffix == ".inc" else []
	else:
		inc_paths = sorted(path for path in root_path.rglob("*.inc") if path.is_file())
	for inc_path in inc_paths:
		for line in inc_path.read_text(encoding="utf-8").splitlines():
			code, _ = split_asm_comment(line)
			match = CALL_CMD_RE.match(code)
			if match is None:
				continue
			label = match.group(1)
			usage[label] = usage.get(label, 0) + 1
	return usage


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Translate pokeemerald-style .inc script files into mostly-structured Poryscript."
	)
	parser.add_argument("input", type=Path, help="Input .inc file or directory containing .inc files")
	parser.add_argument(
		"-o",
		"--output",
		type=Path,
		help="Output .pory path for a single input file, or output directory for directory input",
	)
	parser.add_argument(
		"--no-header",
		action="store_true",
		help="Omit the generated-from header comment",
	)
	parser.add_argument(
		"--optimize",
		action=argparse.BooleanOptionalAction,
		default=True,
		help=(
			"Optimize generated Poryscript by inlining single-use call targets and "
			"rewriting conditional goto/call chains as if/elif/else where safe. "
			"Enabled by default; pass --no-optimize to disable"
		),
	)

	parser.add_argument(
		"--minimize-calls",
		action=argparse.BooleanOptionalAction,
		default=None,
		help=(
			"Deprecated alias for --optimize / --no-optimize"
		),
	)
	parser.add_argument(
		"--call-usage-root",
		type=Path,
		default=Path("."),
		help=(
			"Root directory used to count call usage across .inc files "
			"(default: current working directory)"
		),
	)
	return parser.parse_args()


def main() -> int:
	args = parse_args()
	input_path = args.input
	if not input_path.exists():
		print(f"error: input path does not exist: {input_path}", file=sys.stderr)
		return 1
	if not args.call_usage_root.exists():
		print(f"error: call usage root does not exist: {args.call_usage_root}", file=sys.stderr)
		return 1

	inputs = collect_inputs(input_path)
	if not inputs:
		print(f"error: no .inc files found under {input_path}", file=sys.stderr)
		return 1
	if args.minimize_calls is not None:
		args.optimize = args.minimize_calls

	global_call_usage = count_call_usage(args.call_usage_root) if args.optimize else {}

	if input_path.is_dir() and args.output is None:
		print("error: directory input requires --output to be an output directory", file=sys.stderr)
		return 1
	if len(inputs) > 1 and args.output is not None and args.output.suffix:
		print("error: multiple inputs require --output to be a directory", file=sys.stderr)
		return 1
	if len(inputs) == 1 and input_path.is_file() and args.output is None:
		translate_path(
			inputs[0],
			None,
			include_header=not args.no_header,
			minimize_calls=args.optimize,
			global_call_usage=global_call_usage,
		)
		return 0

	output_root = args.output
	if output_root is None:
		print("error: unable to determine output path", file=sys.stderr)
		return 1

	aggregate = ConversionStats()
	for source_path in inputs:
		if input_path.is_dir():
			relative = source_path.relative_to(input_path)
			destination = output_root / relative.with_suffix(".pory")
		else:
			destination = output_root
		stats = translate_path(
			source_path,
			destination,
			include_header=not args.no_header,
			minimize_calls=args.optimize,
			global_call_usage=global_call_usage,
		)
		aggregate.scripts += stats.scripts
		aggregate.texts += stats.texts
		aggregate.movements += stats.movements
		aggregate.marts += stats.marts
		aggregate.mapscripts += stats.mapscripts
		aggregate.raw_blocks += stats.raw_blocks
		aggregate.folded_tables += stats.folded_tables

	print(
		(
			"converted {count} file(s): scripts={scripts}, texts={texts}, movements={movements}, "
			"marts={marts}, mapscripts={mapscripts}, folded_tables={folded_tables}, raw_blocks={raw_blocks}"
		).format(
			count=len(inputs),
			scripts=aggregate.scripts,
			texts=aggregate.texts,
			movements=aggregate.movements,
			marts=aggregate.marts,
			mapscripts=aggregate.mapscripts,
			folded_tables=aggregate.folded_tables,
			raw_blocks=aggregate.raw_blocks,
		),
		file=sys.stderr,
	)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
