"""
draft_reader.py — Obsidian draft 폴더에서 섹션별 MD 읽기
"""

from pathlib import Path

# draft 폴더 파일명 → 섹션 키 매핑
SECTION_MAP: dict[str, str] = {
    "abstract":                  "0. Abstract.md",
    "introduction":              "1. introduction.md",
    "theoretical_background":    "2. Theoretical background.md",
    "method":                    "3. Method.md",
    "results":                   "4. Results.md",
    "discussion":                "5. Discussion.md",
    "theoretical_implications":  "6. Theoretical implications.md",
    "practical_implications":    "7. Practical implications.md",
    "limitations":               "8. Limitations and future research directions.md",
    "conclusions":               "9. Conclusions.md",
}

SECTION_DISPLAY: dict[str, str] = {
    "abstract":                 "Abstract",
    "introduction":             "Introduction",
    "theoretical_background":   "Theoretical Background",
    "method":                   "Method",
    "results":                  "Results",
    "discussion":               "Discussion",
    "theoretical_implications": "Theoretical Implications",
    "practical_implications":   "Practical Implications",
    "limitations":              "Limitations & Future Research",
    "conclusions":              "Conclusions",
}


def read_draft_sections(
    draft_dir: Path,
    section_keys: list[str] | None = None,
) -> dict[str, str]:
    """Draft 폴더에서 섹션별 내용을 읽어 반환.

    Args:
        draft_dir: draft MD 파일들이 있는 폴더
        section_keys: 읽을 섹션 키 목록. None이면 존재하는 전체 섹션.

    Returns:
        {section_key: content} — 파일이 없거나 비어 있으면 제외
    """
    keys = section_keys if section_keys is not None else list(SECTION_MAP.keys())
    result: dict[str, str] = {}

    for key in keys:
        filename = SECTION_MAP.get(key)
        if not filename:
            print(f"  [경고] 알 수 없는 섹션 키: {key}")
            continue
        path = draft_dir / filename
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8").strip()
        if content:
            result[key] = content

    return result


def list_available_sections(draft_dir: Path) -> list[str]:
    """Draft 폴더에서 읽을 수 있는 섹션 키 목록 반환."""
    available = []
    for key, filename in SECTION_MAP.items():
        path = draft_dir / filename
        if path.exists() and path.read_text(encoding="utf-8").strip():
            available.append(key)
    return available
