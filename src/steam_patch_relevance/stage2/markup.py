"""Steam BBCode/HTML block extraction with offsets into the exact source string."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from typing import Iterator

TOKEN = re.compile(r"\[[^\]]{1,300}\]|<[^>]{1,1000}>")
ENTITY = re.compile(r"&(?:#x[0-9a-fA-F]+|#\d+|[A-Za-z][A-Za-z0-9]+);?")
HEADING_TAG = re.compile(r"^(?:h[1-6]|title)$", re.I)
BLOCK_TAGS = {"p", "div", "br", "li", "ul", "ol", "blockquote"}


@dataclass
class TextBlock:
    text: str
    source_start: int
    source_end: int
    kind: str
    depth: int
    bold_only: bool = False
    forced_heading: bool = False
    char_sources: list[tuple[int, int]] = field(default_factory=list)
    bold_mask: list[bool] = field(default_factory=list)


def _token_parts(token: str) -> tuple[str, bool, str | None]:
    """Return tag name, closing flag, and optional value for BBCode or HTML."""
    if token.startswith("["):
        inner = token[1:-1].strip()
        closing = inner.startswith("/")
        if closing:
            inner = inner[1:].strip()
        name = inner.split("=", 1)[0].split(None, 1)[0] if inner else ""
        return name.lower(), closing, None
    inner = token[1:-1].strip()
    closing = inner.startswith("/")
    if closing:
        inner = inner[1:].strip()
    name = inner.split(None, 1)[0].rstrip("/") if inner else ""
    return name.lower(), closing, None


def _decode_with_offsets(text: str, start: int) -> tuple[str, list[tuple[int, int]]]:
    output: list[str] = []
    offsets: list[tuple[int, int]] = []
    cursor = 0
    for match in ENTITY.finditer(text):
        for index in range(cursor, match.start()):
            output.append(text[index])
            offsets.append((start + index, start + index + 1))
        decoded = html.unescape(match.group())
        if decoded == match.group():
            for index in range(match.start(), match.end()):
                output.append(text[index])
                offsets.append((start + index, start + index + 1))
        else:
            for char in decoded:
                output.append(char)
                offsets.append((start + match.start(), start + match.end()))
        cursor = match.end()
    for index in range(cursor, len(text)):
        output.append(text[index])
        offsets.append((start + index, start + index + 1))
    return "".join(output), offsets


def iter_blocks(source: str) -> Iterator[TextBlock]:
    """Yield visible blocks; every block has a verifiable raw-source span."""
    buffer: list[str] = []
    positions: list[tuple[int, int]] = []
    bold_chars: list[bool] = []
    block_kind = "paragraph"
    depth = 0
    bold_depth = 0
    forced_heading = False

    def flush() -> TextBlock | None:
        nonlocal buffer, positions, bold_chars, block_kind, forced_heading
        text = "".join(buffer).strip()
        if not text:
            buffer = []
            positions = []
            bold_chars = []
            if block_kind == "item":
                block_kind = "paragraph"
            forced_heading = False
            return None
        left = 0
        right = len(buffer)
        while left < right and buffer[left].isspace():
            left += 1
        while right > left and buffer[right - 1].isspace():
            right -= 1
        visible_positions = positions[left:right]
        raw_start = min((span[0] for span in visible_positions), default=0)
        raw_end = max((span[1] for span in visible_positions), default=raw_start)
        bold_visible = bold_chars[left:right]
        block = TextBlock(
            text=text,
            source_start=raw_start,
            source_end=raw_end,
            kind=block_kind,
            depth=depth,
            bold_only=bool(bold_visible) and all(bold_visible),
            forced_heading=forced_heading,
            char_sources=visible_positions,
            bold_mask=bold_visible,
        )
        buffer = []
        positions = []
        bold_chars = []
        if block_kind == "item":
            block_kind = "paragraph"
        elif block_kind == "heading":
            block_kind = "paragraph"
        forced_heading = False
        return block

    def append_text(text: str, raw_start: int) -> None:
        decoded, spans = _decode_with_offsets(text, raw_start)
        for char, span in zip(decoded, spans, strict=True):
            if char in "\r\n":
                block = flush()
                if block:
                    yield_blocks.append(block)
                continue
            buffer.append(char)
            positions.append(span)
            bold_chars.append(bold_depth > 0)

    yield_blocks: list[TextBlock] = []
    cursor = 0
    for match in TOKEN.finditer(source):
        append_text(source[cursor : match.start()], cursor)
        token = match.group()
        name, closing, _ = _token_parts(token)
        if name in {"*", "li"} and not closing:
            block = flush()
            if block:
                yield_blocks.append(block)
            block_kind = "item"
        elif name == "list" or name in {"ul", "ol"}:
            if not closing:
                block = flush()
                if block:
                    yield_blocks.append(block)
                depth += 1
            else:
                block = flush()
                if block:
                    yield_blocks.append(block)
                depth = max(0, depth - 1)
        elif name in {"p", "div", "br", "li", "blockquote"}:
            if closing or name == "br":
                block = flush()
                if block:
                    yield_blocks.append(block)
            elif name in {"p", "div", "blockquote"}:
                block = flush()
                if block:
                    yield_blocks.append(block)
        elif HEADING_TAG.match(name):
            if closing:
                block = flush()
                if block:
                    yield_blocks.append(block)
            else:
                block = flush()
                if block:
                    yield_blocks.append(block)
                forced_heading = True
                block_kind = "heading"
        elif name == "b" or name == "strong":
            bold_depth = max(0, bold_depth - 1) if closing else bold_depth + 1
        cursor = match.end()
        # Flushes are yielded after handling a token to keep parser state local.
        while yield_blocks:
            yield yield_blocks.pop(0)
    append_text(source[cursor:], cursor)
    final = flush()
    if final:
        yield final


def split_bold_prefix(block: TextBlock) -> list[TextBlock]:
    """Split a leading bold heading from adjacent item/entity text when possible."""
    if block.bold_only or not block.text or not block.char_sources:
        return [block]
    bold_len = 0
    for is_bold in _bold_mask_for_block(block):
        if not is_bold:
            break
        bold_len += 1
    if bold_len == 0 or bold_len >= len(block.text):
        return [block]
    # Markup offsets are exact at the block level; derived text parts retain broad spans.
    left_text = block.text[:bold_len].strip()
    right_text = block.text[bold_len:].strip()
    if not left_text or not right_text:
        return [block]
    boundary = block.char_sources[bold_len - 1][1]
    split_at = len(left_text)
    left_sources = block.char_sources[:split_at]
    right_start = split_at
    while right_start < len(block.text) and block.text[right_start].isspace():
        right_start += 1
    right_sources = block.char_sources[right_start:]
    return [
        TextBlock(
            left_text,
            min((span[0] for span in left_sources), default=block.source_start),
            max((span[1] for span in left_sources), default=boundary),
            "heading",
            block.depth,
            True,
            char_sources=left_sources,
            bold_mask=block.bold_mask[:split_at],
        ),
        TextBlock(
            right_text,
            min((span[0] for span in right_sources), default=boundary),
            max((span[1] for span in right_sources), default=block.source_end),
            block.kind,
            block.depth,
            char_sources=right_sources,
            bold_mask=block.bold_mask[right_start:],
        ),
    ]


def _bold_mask_for_block(block: TextBlock) -> list[bool]:
    return block.bold_mask or [False] * len(block.text)
