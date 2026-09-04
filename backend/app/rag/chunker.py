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
            # A long segment has already been boundary-split; retain it safely.
            chunks.append(current)
            current = segment
    if current:
        chunks.append(current)

    # Do not leave a tiny trailing fragment when it can be retained by its predecessor.
    if len(chunks) > 1 and len(chunks[-1]) < max(80, chunk_size // 10):
        previous = chunks[-2]
        merged = f"{previous}\n\n{chunks[-1]}"
        if len(merged) <= chunk_size:
            chunks[-2] = merged
            chunks.pop()
    return chunks

