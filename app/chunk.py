import re
import hashlib
from typing import List, Dict, Tuple

# Heuristics for "heading" lines.
# Works well for governance docs: AGENDA, ACTION ITEMS, 1. RESOLUTIONS, etc.
HEADING_PATTERNS = [
    re.compile(r'^\s*[A-Z][A-Z0-9\s&/,\-]{6,}\s*$'),                 # ALL CAPS long line
    re.compile(r'^\s*(\d+(\.\d+)*)\s*[\)\.]?\s+[A-Za-z].{2,}$'),     # 1. / 1.1 / 2) Heading
    re.compile(r'^\s*[A-Z]\)\s+[A-Za-z].{2,}$'),                     # A) Heading
    re.compile(r'^\s*[A-Za-z][A-Za-z\s&/\-]{3,}:\s*$'),              # Heading:
]

SENTENCE_SPLIT = re.compile(r'(?<=[\.\?\!])\s+(?=[A-Z0-9"\(\[])')

def _is_heading(line: str) -> bool:
    line = (line or "").strip()
    if not line:
        return False
    # ignore very short lines
    if len(line) < 6:
        return False
    return any(p.match(line) for p in HEADING_PATTERNS)

def _normalize_whitespace(text: str) -> str:
    # Keep newlines (important for headings), but normalize excessive spaces
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def _split_into_sections(page_text: str) -> List[Tuple[str, str]]:
    """
    Returns list of (section_title, section_body).
    If no headings, returns one section: ("(no heading)", full text).
    """
    lines = (page_text or "").splitlines()
    lines = [l.rstrip() for l in lines]

    sections: List[Tuple[str, List[str]]] = []
    current_title = None
    current_body: List[str] = []

    def flush():
        nonlocal current_title, current_body
        if current_title is None and not current_body:
            return
        title = current_title or "(no heading)"
        body = "\n".join(current_body).strip()
        if body:
            sections.append((title, body))
        current_title = None
        current_body = []

    for line in lines:
        if _is_heading(line):
            flush()
            current_title = line.strip()
        else:
            # keep bullets and content
            if line.strip():
                current_body.append(line)
            else:
                # preserve paragraph breaks
                if current_body and current_body[-1] != "":
                    current_body.append("")
    flush()

    if not sections:
        return [("(no heading)", (page_text or "").strip())]

    return [(t, _normalize_whitespace(b)) for (t, b) in sections]

def _split_by_sentences(text: str) -> List[str]:
    text = _normalize_whitespace(text)
    if not text:
        return []
    # If text has many bullets, keep line-based chunks
    if text.count("\n") >= 6 and ("•" in text or "-" in text):
        parts = [p.strip() for p in text.splitlines() if p.strip()]
        return parts
    return [s.strip() for s in SENTENCE_SPLIT.split(text) if s.strip()]

def _make_chunk_id(doc_id: str, page_no: int, ordinal: int) -> str:
    return hashlib.sha1(f"{doc_id}:{page_no}:{ordinal}".encode()).hexdigest()[:16]

def chunk_pages(
    doc_id: str,
    pages: List[Dict],
    max_chars: int = 1200,
    min_chars: int = 250,
    overlap_sentences: int = 1,
) -> List[Dict]:
    """
    Section-aware chunking:
    - split each page by headings
    - pack sections until max_chars
    - if a section is too big, split by sentences
    Keeps page_start/page_end as that page (tight citations).
    """
    out: List[Dict] = []
    ordinal = 0

    for p in pages:
        page_no = int(p.get("page", 1))
        page_text = (p.get("text") or "").strip()
        if not page_text:
            continue

        sections = _split_into_sections(page_text)

        # Pack sections into chunks up to max_chars (within this page)
        buf = ""
        buf_titles = []

        def flush_buf():
            nonlocal buf, buf_titles, ordinal
            text = _normalize_whitespace(buf)
            if text:
                ordinal += 1
                out.append({
                    "chunk_id": _make_chunk_id(doc_id, page_no, ordinal),
                    "ordinal": ordinal,
                    "page_start": page_no,
                    "page_end": page_no,
                    "title": " | ".join(buf_titles[:3]) if buf_titles else None,
                    "text": text,
                })
            buf = ""
            buf_titles = []

        for title, body in sections:
            body = _normalize_whitespace(body)
            if not body:
                continue

            candidate = (buf + "\n\n" + body).strip() if buf else body
            if len(candidate) <= max_chars:
                buf = candidate
                if title and title != "(no heading)":
                    buf_titles.append(title)
                continue

            # If current buffer has something, flush it first.
            if buf:
                flush_buf()

            # If this single section is still too big, split by sentences/bullets.
            if len(body) > max_chars:
                units = _split_by_sentences(body)
                if not units:
                    # fallback raw split
                    units = [body]

                pack = []
                pack_len = 0
                for u in units:
                    u = u.strip()
                    if not u:
                        continue
                    u_len = len(u) + 1
                    if pack_len + u_len > max_chars and pack:
                        # flush packed
                        text = " ".join(pack).strip()
                        ordinal += 1
                        out.append({
                            "chunk_id": _make_chunk_id(doc_id, page_no, ordinal),
                            "ordinal": ordinal,
                            "page_start": page_no,
                            "page_end": page_no,
                            "title": title if title != "(no heading)" else None,
                            "text": text,
                        })
                        # overlap last N sentences for continuity
                        pack = pack[-overlap_sentences:] if overlap_sentences > 0 else []
                        pack_len = sum(len(x) + 1 for x in pack)

                    pack.append(u)
                    pack_len += u_len

                if pack:
                    text = " ".join(pack).strip()
                    ordinal += 1
                    out.append({
                        "chunk_id": _make_chunk_id(doc_id, page_no, ordinal),
                        "ordinal": ordinal,
                        "page_start": page_no,
                        "page_end": page_no,
                        "title": title if title != "(no heading)" else None,
                        "text": text,
                    })
            else:
                # section fits alone but not with previous
                buf = body
                buf_titles = [title] if title != "(no heading)" else []

        # flush leftovers
        if buf:
            # if tiny, try to merge with previous chunk on same page
            if len(buf) < min_chars and out and out[-1]["page_start"] == page_no:
                out[-1]["text"] = _normalize_whitespace(out[-1]["text"] + "\n\n" + buf)
            else:
                flush_buf()

    # remove empty titles
    for c in out:
        if not c.get("title"):
            c.pop("title", None)

    return out
