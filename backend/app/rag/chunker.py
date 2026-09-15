import re


def _split_long_paragraph(paragraph: str, chunk_size: int) -> list[str]:
    """Split oversized text at sentence or word boundaries when possible."""
    parts: list[str] = []
    remaining = paragraph.strip()
    while len(remaining) > chunk_size:
        boundary = max(
            remaining.rfind(". ", 0, chunk_size),
            remaining.rfind("? ", 0, chunk_size),
            remaining.rfind("! ", 0, chunk_size),
            remaining.rfind(" ", 0, chunk_size),
        )
        if boundary <= 0:
            boundary = chunk_size
        else:
            boundary += 1
        parts.append(remaining[:boundary].strip())
        remaining = remaining[boundary:].strip()
    if remaining:
        parts.append(remaining)
    return parts


def _overlap_tail(text: str, overlap: int) -> str:
    if overlap <= 0:
        return ""
    tail = text[-overlap:].strip()
    boundary = tail.find(" ")
    return tail[boundary + 1:] if boundary >= 0 else tail


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[str]:
    """Create deterministic, paragraph-aware overlapping chunks for local RAG."""
    if not isinstance(text, str) or not text.strip():
        return []
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")

    paragraphs = [
        re.sub(r"[ \t]+", " ", paragraph).strip()
        for paragraph in re.split(r"\n\s*\n+", text.strip())
        if paragraph.strip()
    ]
    segments = [
        piece
        for paragraph in paragraphs
        for piece in _split_long_paragraph(paragraph, chunk_size)
    ]

    chunks: list[str] = []
    current = ""
    for segment in segments:
        candidate = f"{current}\n\n{segment}" if current else segment
        if len(candidate) <= chunk_size:
            current = candidate
            continue
        if current:
            chunks.append(current)
            current = _overlap_tail(current, overlap)
        candidate = f"{current}\n\n{segment}" if current else segment
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            chunks.append(current)
            current = segment
    if current:
        chunks.append(current)

    if len(chunks) > 1 and len(chunks[-1]) < max(80, chunk_size // 10):
        previous = chunks[-2]
        merged = f"{previous}\n\n{chunks[-1]}"
        if len(merged) <= chunk_size:
            chunks[-2] = merged
            chunks.pop()
    return chunks


def _extract_section_heading(paragraph: str) -> str | None:
    lines = paragraph.strip().split("\n")
    first_line = lines[0].strip()
    if first_line.startswith("#") or first_line.startswith("[Sheet:") or first_line.startswith("[Slide"):
        return first_line.lstrip("#").strip()
    match = re.match(r"^(\d+(?:\.\d+)*\s+[^.\n]{3,60})", first_line)
    if match:
        return match.group(1).strip()
    return None


INSTRUCTIONAL_PHRASES = [
    "suggested questions for the ai workbench demo",
    "when your rag system cites this file",
    "expected demo findings",
    "use these prompts",
    "source metadata for prototype citations",
]


def is_instructional_chunk(text: str) -> bool:
    """Check if a chunk contains demo instructional text rather than operational evidence."""
    t_lower = text.lower()
    return any(phrase in t_lower for phrase in INSTRUCTIONAL_PHRASES)


def chunk_text_with_metadata(text: str, chunk_size: int = 1000, overlap: int = 150) -> list[dict[str, Any]]:
    """Chunk text into section-aware segments with extracted item IDs (INC, CAP, etc.) and content_type tagging."""
    chunks_raw = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    if not chunks_raw:
        return []

    paragraphs = re.split(r"\n\s*\n+", text.strip())
    current_section = "Overview"

    results: list[dict[str, Any]] = []
    for chunk in chunks_raw:
        for p in paragraphs:
            if p in chunk:
                heading = _extract_section_heading(p)
                if heading:
                    current_section = heading
                    break

        ids = sorted(list(set(re.findall(r"\b(?:INC|CAP|SOP|P)-\d+\b", chunk, flags=re.IGNORECASE))))
        c_type = "instructional" if is_instructional_chunk(chunk) else "evidence"
        results.append({
            "text": chunk,
            "section": current_section,
            "ids": ids,
            "content_type": c_type,
        })
    return results


