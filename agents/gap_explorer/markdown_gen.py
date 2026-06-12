"""
markdown_gen.py — 갭 분석 결과를 Obsidian MD 파일로 생성
"""

import re
from datetime import date
from pathlib import Path

from config import GAP_MARKDOWN_TEMPLATE


def _sanitize_filename(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*\n\r\t]', "-", name)
    name = re.sub(r"-{2,}", "-", name)
    return name.strip(" -").replace(" ", "-")


def _build_filename(pdf_filename: str) -> str:
    stem = Path(pdf_filename).stem
    return f"{stem}_갭분석.md"


def _format_tags_yaml(tags: list) -> str:
    base  = ["gap-explorer", "research-gap"]
    extra = [t.lower().replace(" ", "-") for t in tags if t]
    all_tags = base + [t for t in extra if t not in base]
    return ", ".join(all_tags)


def _format_hashtags(tags: list) -> str:
    if not tags:
        return ""
    return " ".join(f"#{t.lower().replace(' ', '-')}" for t in tags if t)


def _format_intro_gaps(gaps: list) -> str:
    if not gaps:
        return "[서론 갭 없음 또는 추출 실패]\n"
    parts = []
    for i, g in enumerate(gaps, 1):
        parts.append(f"### 선행연구 갭 {i}")
        parts.append(f"- **갭 (KO)**: {g.get('gap_ko', '')}")
        parts.append(f"- **갭 (EN)**: {g.get('gap_en', '')}")
        parts.append(f"- **이 논문의 기여 (KO)**: {g.get('paper_contribution_ko', '')}")
        parts.append(f"- **이 논문의 기여 (EN)**: {g.get('paper_contribution_en', '')}")
        source = g.get('source', '')
        if source:
            parts.append(f"- **원문**: > \"{source}\"")
        parts.append("")
    return "\n".join(parts)


def _format_core_gaps(gaps: list) -> str:
    if not gaps:
        return "[핵심 갭 추출 실패 — Discussion/Limitation 섹션 직접 확인 필요]\n"
    parts = []
    for i, g in enumerate(gaps, 1):
        gap_type   = g.get('gap_type', '')
        model_type = g.get('model_type_needed', '')
        header = f"핵심 갭 {i}"
        if gap_type:
            header += f" — {gap_type}"
        if model_type:
            header += f" [{model_type}]"
        parts.append(f"### {header}")
        parts.append(f"- **KO**: {g.get('gap_ko', '')}")
        parts.append(f"- **EN**: {g.get('gap_en', '')}")
        source = g.get('source', '')
        if source:
            parts.append(f"- **원문**: > \"{source}\"")
        parts.append("")
    return "\n".join(parts)


def _format_list(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value if v) or "없음"
    return str(value) if value else "없음"


def generate_markdown(result: dict, paper: dict, force: bool = False) -> Path | None:
    pdf_folder   = Path(paper.get("file_path", "")).parent
    pdf_filename = paper.get("file_name", "untitled.pdf")

    md_name = _build_filename(pdf_filename)
    md_path = pdf_folder / md_name

    if md_path.exists() and not force:
        print(f"  [스킵] 이미 존재: {md_name}")
        return None

    tags = result.get("tags", [])

    content = GAP_MARKDOWN_TEMPLATE.format(
        title         = result.get("title", "").replace('"', '\\"'),
        year          = result.get("year", "미상"),
        author        = result.get("author", ""),
        journal       = result.get("journal", ""),
        doi           = result.get("doi", ""),
        tags          = _format_tags_yaml(tags),
        hashtags      = _format_hashtags(tags),
        created       = date.today().isoformat(),
        source_folder = paper.get("source_folder", ""),
        pdf_filename  = pdf_filename,
        intro_gaps    = _format_intro_gaps(result.get("intro_gaps", [])),
        core_gaps     = _format_core_gaps(result.get("core_gaps", [])),
        theories      = _format_list(result.get("theories", [])),
    )

    md_path.write_text(content, encoding="utf-8")
    print(f"  → 생성: {md_name}")
    return md_path
