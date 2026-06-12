"""
markdown_gen.py — 갭 전략 분석 결과를 Obsidian MD 파일로 생성
"""

from datetime import datetime
from pathlib import Path

from config import STRATEGY_MARKDOWN_TEMPLATE, SYNTHESIS_DIR


def _format_coverage(items: list) -> str:
    if not items:
        return "- [갭 커버리지 없음]\n"
    parts = []
    for c in items:
        icon = {"Full": "✅", "Partial": "⚠️", "None": "❌"}.get(c.get("coverage", ""), "•")
        matched = ", ".join(c.get("matched_variables", []))
        missing = ", ".join(c.get("missing_variables", [])) or "없음"
        parts.append(f"#### {icon} {c.get('cluster_name', '')} — {c.get('coverage', '')}")
        parts.append(f"- **대응 변인**: {matched}")
        parts.append(f"- **부재 변인**: {missing}")
        parts.append(f"- **판단**: {c.get('coverage_reason', '')}")
        parts.append("")
    return "\n".join(parts)


def _format_models(models: list) -> str:
    if not models:
        return "[제안 가능한 모형 없음]\n"
    parts = []
    for m in models:
        priority = m.get("priority", "")
        p_icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(priority, "•")
        cl_ok = "✅" if m.get("crosslag_feasible") else "❌"
        parts.append(f"### {m.get('model_id', '')} — {m.get('model_name', '')} {p_icon} {priority}")
        parts.append(f"- **채우는 갭**: {m.get('fills_gap', '')}")
        parts.append(f"- **경로**: `{m.get('path', '')}`")
        parts.append(f"- **시간 구조**: {m.get('temporal_structure', '')}")
        parts.append(f"- **분석 방법**: {m.get('analysis_method', '')} / {m.get('model_type', '')}")
        variables = ", ".join(m.get("variables_used", []))
        parts.append(f"- **사용 변인**: {variables}")
        parts.append(f"- **이론적 근거**: {m.get('theoretical_basis', '')}")
        parts.append(f"- **차별점**: {m.get('novelty', '')}")
        parts.append(f"- **교차지연 가능**: {cl_ok} — {m.get('crosslag_reason', '')}")
        parts.append(f"- **우선순위 이유**: {m.get('priority_reason', '')}")
        parts.append("")
    return "\n".join(parts)


def _format_excluded(paths: list) -> str:
    if not paths:
        return "- [제외 경로 없음]\n"
    parts = []
    for p in paths:
        parts.append(f"- **경로**: `{p.get('path', '')}`")
        parts.append(f"  - **이유**: {p.get('reason', '')}")
    return "\n".join(parts)


def generate_markdown(strategy: dict, landscape_names: list[str]) -> Path | None:
    SYNTHESIS_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    filename = f"gap_strategy_{now.strftime('%Y%m%d_%H%M%S')}.md"
    md_path = SYNTHESIS_DIR / filename

    content = STRATEGY_MARKDOWN_TEMPLATE.format(
        created         = now.strftime("%Y-%m-%d %H:%M"),
        n_landscapes    = len(landscape_names),
        landscapes_list = "\n".join(f"- {n}" for n in landscape_names),
        gap_coverage    = _format_coverage(strategy.get("gap_coverage", [])),
        viable_models   = _format_models(strategy.get("viable_models", [])),
        excluded_paths  = _format_excluded(strategy.get("excluded_paths", [])),
        recommendation  = strategy.get("top_recommendation", ""),
    )

    md_path.write_text(content, encoding="utf-8")
    print(f"\n  → 저장: {md_path}")
    return md_path
