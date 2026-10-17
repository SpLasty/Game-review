"""Structure-preserving announcement parsing and inspectable change candidates."""

import html
import re
from urllib.parse import parse_qs, urlparse

from bs4 import BeautifulSoup, NavigableString, Tag

from steam_insights.data.text import clean_text
from steam_insights.pipeline.storage import stable_id

HEADING = re.compile(
    r"^(?:[\W_]*)(fixes|bug fixes|crash fixes|known issues|balance|balancing|performance|improvements|changes|new features|planned changes|future changes|workarounds|patch notes)(?:[\W_]*)$",
    re.I,
)
ACTION = re.compile(
    r"\b(fix(?:ed|es|ing)?|add(?:ed|s)?|remov(?:e|ed|es)|chang(?:e|ed|es)|increas(?:e|ed)|decreas(?:e|ed)|adjust(?:ed|ments?)?|improv(?:e|ed|ements?)|resolv(?:e|ed)|address(?:ed)?|nerf(?:ed)?|buff(?:ed)?|prepar(?:e|ed|ing)|workaround|known issue|investigat\w*|plan(?:ned|s)?|reduc(?:e|ed)|updat(?:e|ed))\b",
    re.I,
)


def _bbcode_html(source: str) -> str:
    text = html.escape(source, quote=False)
    text = re.sub(r"\[img(?:=[^]]*)?\].*?\[/img\]", "", text, flags=re.I | re.S)
    text = re.sub(
        r"\[(?:previewyoutube|previewyoutubeid)=[^]]*\].*?\[/(?:previewyoutube|previewyoutubeid)\]",
        "",
        text,
        flags=re.I | re.S,
    )
    text = re.sub(r"\[url(?:=[^]]*)?\]", "", text, flags=re.I)
    text = re.sub(r"\[/url\]", "", text, flags=re.I)
    for bb, tag in {
        "h1": "h1",
        "h2": "h2",
        "h3": "h3",
        "p": "p",
        "list": "ul",
        "olist": "ol",
        "table": "table",
        "tr": "tr",
        "td": "td",
        "th": "th",
        "b": "b",
        "i": "i",
        "u": "u",
        "strike": "s",
        "code": "pre",
        "quote": "blockquote",
    }.items():
        text = re.sub(rf"\[{bb}(?:=[^]]*)?\]", f"<{tag}>", text, flags=re.I)
        text = re.sub(rf"\[/{bb}\]", f"</{tag}>", text, flags=re.I)
    text = re.sub(r"\[\*\]", "</li><li>", text)
    text = re.sub(r"\[br\]", "<br>", text, flags=re.I)
    return text


def parse_document(source: str, *, flattened: bool = False) -> tuple[str, list[dict], str, bool]:
    is_bbcode = bool(re.search(r"\[(?:h[123]|list|olist|table|p|b|url)(?:=[^]]*)?\]", source, re.I))
    is_html = bool(re.search(r"<(?:p|div|h[1-6]|ul|li|table|br|b|strong|a)(?:\s|>)", source, re.I))
    kind = (
        "flattened_csv"
        if flattened
        else "bbcode"
        if is_bbcode
        else "html"
        if is_html
        else "plain_source"
    )
    structured = not flattened and (is_bbcode or is_html)
    blocks = []
    headings = {}

    def add(text, role="paragraph", level=0, depth=0, origin="none"):
        text = clean_text(text)
        if not text:
            return
        if role == "heading":
            for key in list(headings):
                if key >= level:
                    del headings[key]
            headings[level] = text
        blocks.append(
            {
                "text": text,
                "block_type": role,
                "heading_path": [headings[key] for key in sorted(headings)],
                "list_depth": depth,
                "heading_origin": origin,
            }
        )

    if structured:
        soup = BeautifulSoup(_bbcode_html(source) if is_bbcode else source, "html.parser")
        buffer = []

        def flush(role="paragraph", depth=0):
            if buffer:
                add("".join(buffer), role, depth=depth)
                buffer.clear()

        def walk(node, depth=0):
            if isinstance(node, NavigableString):
                buffer.append(str(node))
                return
            if not isinstance(node, Tag):
                return
            name = node.name.lower()
            if name in {"script", "style", "img", "iframe", "video"}:
                return
            if re.fullmatch(r"h[1-6]", name):
                flush()
                add(node.get_text(" ", strip=True), "heading", int(name[1]), origin="source_markup")
                return
            if name == "tr":
                flush()
                cells = node.find_all(["td", "th"], recursive=False)
                add(" | ".join(cell.get_text(" ", strip=True) for cell in cells), "table_row")
                return
            if name == "li":
                flush()
                for child in node.children:
                    if isinstance(child, Tag) and child.name in {"ul", "ol", "li"}:
                        flush("list_item", depth)
                        walk(child, depth + (child.name in {"ul", "ol"}))
                    else:
                        walk(child, depth)
                flush("list_item", depth)
                return
            if name == "br":
                buffer.append("\n")
                return
            boundary = name in {"p", "div", "blockquote", "ul", "ol", "table", "pre"}
            if boundary:
                flush()
            for child in node.children:
                walk(child, depth)
            if boundary:
                flush()

        walk(soup)
        flush()
    else:
        pending, bullet = [], False

        def flush_plain():
            nonlocal bullet
            if pending:
                add(" ".join(pending), "list_item" if bullet else "paragraph")
                pending.clear()
            bullet = False

        for line in source.splitlines():
            line = line.strip()
            if not line:
                flush_plain()
            elif HEADING.fullmatch(line):
                flush_plain()
                add(line, "heading", 2, origin="inferred_plain_line")
            elif re.fullmatch(r"[-*•]", line):
                flush_plain()
                bullet = True
            elif re.match(r"^(?:[-*•]|\d+[.)])\s+", line):
                flush_plain()
                bullet = True
                pending.append(re.sub(r"^(?:[-*•]|\d+[.)])\s+", "", line))
            else:
                pending.append(line)
        flush_plain()
    cursor = 0
    for index, block in enumerate(blocks):
        block["ordinal"] = index
        block["char_start"] = cursor
        cursor += len(block["text"])
        block["char_end"] = cursor
        cursor += 1
    return "\n".join(b["text"] for b in blocks), blocks, kind, structured


def branch_hint(text: str) -> str | None:
    branches = [
        name
        for name in ("unstable", "stable", "beta", "experimental", "public", "preview")
        if re.search(rf"\b{name}\b", text, re.I)
    ]
    if len(branches) > 1:
        if set(branches) <= {"unstable", "beta"}:
            return "unstable"
        return "mixed"
    return branches[0] if branches else None


def platform_hints(text: str) -> list[str]:
    return [
        name
        for name, pattern in {
            "windows": r"\bwindows\b",
            "linux": r"\blinux\b",
            "macos": r"\b(?:macos|mac os|mac)\b",
            "steam_deck": r"\bsteam deck\b",
            "playstation": r"\b(?:playstation|ps[45])\b",
            "xbox": r"\bxbox\b",
        }.items()
        if re.search(pattern, text, re.I)
    ]


def document_links(document: dict) -> list[dict]:
    source = document["source_text_original"]
    links = [
        (match.group(1), re.sub(r"\[[^]]*\]", "", match.group(2)))
        for match in re.finditer(r"\[url=([^]]+)\](.*?)\[/url\]", source, re.I | re.S)
    ]
    if document["document_format"] == "html":
        links += [
            (str(a["href"]), a.get_text(" ", strip=True))
            for a in BeautifulSoup(source, "html.parser").find_all("a", href=True)
        ]
    links += [(url, url) for url in re.findall(r"\[url\](https?://[^\[]+)\[/url\]", source, re.I)]
    result = {}
    for original, label in links:
        target = html.unescape(original)
        parsed = urlparse(target)
        if (
            parsed.hostname
            and parsed.hostname.endswith("steamcommunity.com")
            and "linkfilter" in parsed.path
        ):
            target = parse_qs(parsed.query).get("url", [target])[0]
            parsed = urlparse(target)
        if parsed.scheme not in {"http", "https"}:
            continue
        host = (parsed.hostname or "").lower()
        steam = any(
            host == suffix or host.endswith("." + suffix)
            for suffix in ("steamcommunity.com", "steampowered.com")
        )
        key = stable_id(document["announcement_revision_id"], original, label)
        result[key] = {
            "link_id": key,
            "announcement_revision_id": document["announcement_revision_id"],
            "post_id": document["post_id"],
            "appid": document["appid"],
            "label": clean_text(label),
            "original_url": original,
            "target_url": target,
            "target_host": host,
            "reference_kind": "steam_reference"
            if steam
            else "external_source_needs_domain_confirmation",
        }
    return [result[key] for key in sorted(result)]


def status_hint(text: str, context: str = "") -> str:
    combined = context + "\n" + text
    if re.search(
        r"\bknown issues?\b|\bstill (?:broken|not fixed|crash\w*)|\bnot (?:yet )?fixed\b|\bunresolved\b",
        combined,
        re.I,
    ):
        return "known_issue"
    if re.search(
        r"\b(?:planned|upcoming|future|will (?:be )?(?:fix(?:ed)?|address(?:ed)?|resolv(?:e|ed))|intend to|plan to)\b",
        combined,
        re.I,
    ):
        return "planned"
    if re.search(r"\bworkaround\b", combined, re.I):
        return "workaround"
    if re.search(r"\b(?:partial|partially|some instances|not all)\b", combined, re.I):
        return "partial_fix"
    if re.search(r"\b(?:investigating|aware of|acknowledged)\b", combined, re.I):
        return "acknowledged"
    if re.search(r"\b(?:fixed|resolved|addressed)\b", text, re.I):
        return "released_fix_claim"
    return "change_or_unknown"


def extract_changes(document: dict, blocks: list[dict]) -> list[dict]:
    changes = []
    if document["post_type"] in {"promotion", "event"}:
        return changes
    for block in blocks:
        if block["block_type"] == "heading":
            continue
        context = " > ".join(block["heading_path"])
        if not ACTION.search(block["text"]) and not ACTION.search(context):
            continue
        text = block["text"]
        topics = [
            name
            for name, pattern in {
                "performance": r"\b(?:fps|stutter|performance|lag)\b",
                "stability": r"\b(?:crash\w*|freez\w*|disconnect\w*)\b",
                "balance": r"\b(?:nerf\w*|buff\w*|balance|damage|cooldown)\b",
                "monetization": r"\b(?:price|microtransaction\w*|currency|pay.to.win)\b",
                "bugs": r"\b(?:bugs?|glitch\w*|fixed)\b",
            }.items()
            if re.search(pattern, text, re.I)
        ]
        values = re.search(
            r"\bfrom\s+(-?\d+(?:\.\d+)?\s*%?)\s+to\s+(-?\d+(?:\.\d+)?\s*%?)|(-?\d+(?:\.\d+)?\s*%?)\s*(?:->|→)\s*(-?\d+(?:\.\d+)?\s*%?)",
            text,
            re.I,
        )
        old, new = (
            (values.group(1) or values.group(3), values.group(2) or values.group(4))
            if values
            else (None, None)
        )
        hint = status_hint(text, context)
        scope = document["title"] + " " + context
        branch = branch_hint(context) or document["branch"]
        changes.append(
            {
                "change_id": stable_id(
                    "change_v1", document["announcement_revision_id"], block["block_id"]
                ),
                "announcement_revision_id": document["announcement_revision_id"],
                "block_id": block["block_id"],
                "post_id": document["post_id"],
                "appid": document["appid"],
                "game": document["game"],
                "title": document["title"],
                "heading_path": block["heading_path"],
                "text": text,
                "char_start": block["char_start"],
                "char_end": block["char_end"],
                "context_text": document["title"] + "\n" + context + "\n" + text,
                "status_hint": hint,
                "topic_hints": topics,
                "entity_hint": block["heading_path"][-1] if block["heading_path"] else None,
                "version_hint": document["version_hint"],
                "branch": branch,
                "platforms": platform_hints(scope),
                "old_value": old,
                "new_value": new,
                "needs_review": not document["structure_available"]
                or block["block_type"] == "paragraph"
                or hint == "change_or_unknown"
                or len(text) > 1000,
                "extraction_method": "structural_fragment_candidate_v1",
                "source_url": document["source_url"],
                "split": None,
            }
        )
    return changes
