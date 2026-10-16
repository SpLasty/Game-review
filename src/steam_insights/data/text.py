"""One shared text convention for profiling, validation and preparation."""

import re
import unicodedata

NORMALIZATION_VERSION = "nfc_whitespace_v1"


def clean_text(text: str) -> str:
    text = unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(re.sub(r"[^\S\n]+", " ", line).strip() for line in text.split("\n"))
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def word_count(text: str) -> int:
    # Python Unicode regex semantics match the existing collector. Arrow's \w differs.
    return len(re.findall(r"\b\w+\b", text, re.UNICODE))
