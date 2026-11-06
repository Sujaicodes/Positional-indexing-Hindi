"""Unicode normalization and Hindi-English lexical tokenization."""
import re
import unicodedata


def normalize_text(text: str) -> str:
    """Normalize canonically equivalent Unicode sequences and whitespace."""
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip()


def _script(ch: str):
    """Return the supported script family for a character, or None."""
    name = unicodedata.name(ch, "")
    if "DEVANAGARI" in name and unicodedata.category(ch)[0] in {"L", "M"}:
        return "hi"
    if "LATIN" in name and unicodedata.category(ch)[0] in {"L", "M"}:
        return "en"
    return None


def tokenize_with_languages(text: str):
    """Return (token, language) pairs in order.

    Supports Devanagari and Latin-script words. Punctuation, whitespace,
    numerals, symbols and script changes delimit tokens. Positions are assigned
    later over this complete bilingual lexical-token sequence.
    """
    text = normalize_text(text)
    tokens = []
    current = []
    current_script = None
    for ch in text:
        script = _script(ch)
        if script and (current_script is None or script == current_script):
            current.append(ch)
            current_script = script
        else:
            if current:
                tokens.append(("".join(current), current_script))
                current = []
            current_script = script
            if script:
                current.append(ch)
    if current:
        tokens.append(("".join(current), current_script))
    return tokens


def tokenize(text: str):
    """Return bilingual Hindi/English lexical tokens in reading order."""
    return [term for term, _language in tokenize_with_languages(text)]


def language_of(term: str) -> str:
    """Identify a token's script language as 'hi' or 'en'."""
    for ch in term:
        script = _script(ch)
        if script:
            return script
    return "unknown"
