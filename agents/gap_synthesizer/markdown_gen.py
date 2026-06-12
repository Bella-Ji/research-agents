"""
markdown_gen.py — 갭 지형 지도 결과를 Obsidian MD 파일로 생성
"""

from datetime import datetime
from pathlib import Path

from config import SYNTHESIS_DIR, SYNTHESIS_MARKDOWN_TEMPLATE


def _format_list(value) -> str:
    if isinstance(value, list):
        return "\n".join(f"- {v}" for v in value if v)
    return str(value) if value else ""


def _format_clusters(clusters: list) -> str:
    if not clusters:
        return "- [갭 군집 없음]\n"
    parts = []
    for i, c in enumerate(clusters, 1):
        model_types = ", ".join(c.get("model_types_needed", []))
        theories = ", ".join(c.get("theories_involved", []))
        papers = ", ".join(c.get("papers", []))
        rep_gaps = c.get("representative_gaps", [])

        parts.append(f"### 군집 {i} — {c.get('cluster_name', '')} | {c.get('cluster_name_en', '')}")
        parts.append(f"- **갭 유형**: {c.get('gap_type', '')}")
        parts.append(f"- **필요 모형**: {model_types}")
        parts.append(f"- **관련 이론**: {theories}")
        parts.append(f"- **논문 수**: {c.get('n_papers', len(c.get('papers', [])))}")
        parts.append(f"- **설명**: {c.get('description_ko', '')}")
        parts.append(f"- **해당 논문**: {papers}")
        if rep_gaps:
            parts.append("- **대표 갭 원문**:")
            for g in rep_gaps:
                parts.append(f"  > \"{g}\"")
        parts.append("")
    return "\n".join(parts)


def _format_underexplored(paths: list) -> str:
    if not paths:
        return "- [미검증 경로 없음]\n"
    parts = []
    for p in paths:
        mentioned = ", ".join(p.get("mentioned_in", []))
        parts.append(f"- **KO**: {p.get('path_ko', '')}")
        parts.append(f"  - **EN**: {p.get('path_en', '')}")
        parts.append(f"  - **언급 논문**: {mentioned}")
    return "\n".join(parts)


def _format_methodological_gaps(gaps: list) -> str:
    if not gaps:
        return "- [방법론적 갭 없음]\n"
    parts = []
    for g in gaps:
        mentioned = ", ".join(g.get("mentioned_in", []))
        parts.append(f"- **KO**: {g.get('gap_ko', '')}")
        parts.append(f"  - **EN**: {g.get('gap_en', '')}")
        parts.append(f"  - **언급 논문**: {mentioned}")
    return "\n".join(parts)


def _format_dominant_theories(theories: list) -> str:
    if not theories:
        return "- [이론 정보 없음]\n"
    sorted_theories = sorted(theories, key=lambda t: t.get("frequency", 0), reverse=True)
    parts = []
    for t in sorted_theories:
        papers = ", ".join(t.get("papers", []))
        parts.append(f"- **{t.get('theory', '')}** ({t.get('frequency', 0)}편): {papers}")
    return "\n".join(parts)


def generate_markdown(synthesis: dict, paper_names: list[str]) -> Path | None:
    SYNTHESIS_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    filename = f"gap_landscape_{now.strftime('%Y%m%d_%H%M%S')}.md"
    md_path = SYNTHESIS_DIR / filename

    content = SYNTHESIS_MARKDOWN_TEMPLATE.format(
        created              = now.strftime("%Y-%m-%d %H:%M"),
        n_papers             = len(paper_names),
        papers_list          = _format_list(paper_names),
        gap_clusters         = _format_clusters(synthesis.get("gap_clusters", [])),
        underexplored_paths  = _format_underexplored(synthesis.get("underexplored_paths", [])),
        methodological_gaps  = _format_methodological_gaps(synthesis.get("methodological_gaps", [])),
        dominant_theories    = _format_dominant_theories(synthesis.get("dominant_theories", [])),
        summary              = synthesis.get("summary_ko", ""),
    )

    md_path.write_text(content, encoding="utf-8")
    print(f"\n  → 저장: {md_path}")
    return md_path
