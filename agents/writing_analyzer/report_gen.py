"""
report_gen.py — 글쓰기 분석 결과를 Obsidian MD 파일로 생성
"""

from datetime import date
from pathlib import Path

from agents.writing_analyzer.draft_reader import SECTION_DISPLAY, SECTION_MAP


def _to_bullets(items: list | str) -> str:
    if isinstance(items, list):
        return "\n".join(f"- {item}" for item in items if item)
    return f"- {items}" if items else ""


def _section_block(section_key: str, analysis: dict) -> str:
    display = SECTION_DISPLAY.get(section_key, section_key)
    return f"""\
## {display}

### 📐 이 논문의 구조
{analysis.get("paper_structure", "")}

### 🎯 효과적인 글쓰기 전략
{_to_bullets(analysis.get("paper_rhetorical_moves", []))}

### ✍️ 문체 특징
{analysis.get("paper_style", "")}

### 🔍 내 초안과의 차이
{analysis.get("comparison", "")}

### 💪 내 초안의 강점
{analysis.get("my_strengths", "")}

### 🔧 개선 방향
{_to_bullets(analysis.get("improvements", []))}

### ✨ 지금 바로 적용할 것
{_to_bullets(analysis.get("takeaways", []))}
"""


def generate_report(
    paper_info: dict,
    section_analyses: dict[str, dict],
    output_dir: Path,
    current_paper: str,
) -> Path | None:
    """분석 결과를 MD 파일로 저장.

    Args:
        paper_info: 논문 기본 정보 (file_name, metadata 등)
        section_analyses: {section_key: analysis_dict}
        output_dir: 저장 루트 폴더 (WRITING_ANALYSIS_DIR)
        current_paper: 내가 쓰는 논문 이름 (서브폴더명)

    Returns:
        생성된 MD 파일 경로. 실패 시 None.
    """
    if not section_analyses:
        print("  [건너뜀] 분석된 섹션 없음")
        return None

    save_dir = output_dir / current_paper
    save_dir.mkdir(parents=True, exist_ok=True)

    stem = Path(paper_info.get("file_name", "unknown")).stem
    md_name = f"{stem}_writing_analysis.md"
    md_path = save_dir / md_name

    meta = paper_info.get("metadata", {})
    title  = meta.get("title", "") or stem
    author = meta.get("author", "")

    analyzed_sections = [
        SECTION_DISPLAY.get(k, k) for k in SECTION_MAP if k in section_analyses
    ]
    sections_str = ", ".join(analyzed_sections)

    header = f"""\
---
title: "Writing Analysis: {title}"
source_paper: "{paper_info.get('file_name', '')}"
author: "{author}"
my_paper: "{current_paper}"
analyzed_sections: [{sections_str}]
created: {date.today().isoformat()}
tags: [writing-analysis, literature]
---

# Writing Analysis: {title}

> **분석 목적**: 글쓰기 방식과 논리 구조 학습 (연구 내용 비교 아님)
> **분석 대상**: `{paper_info.get('file_name', '')}`
> **비교 초안**: {current_paper}

---

"""

    body_parts = []
    for key in SECTION_MAP:
        if key in section_analyses:
            body_parts.append(_section_block(key, section_analyses[key]))

    content = header + "\n---\n\n".join(body_parts)

    md_path.write_text(content, encoding="utf-8")
    print(f"  → 저장: {md_path}")
    return md_path


def generate_revision_report(
    revision: dict,
    section_key: str,
    original_paragraph: str,
    output_dir: Path,
    current_paper: str,
) -> Path | None:
    """문단 수정 제안 결과를 revise_output.md로 저장 (매 실행마다 덮어쓰기).

    Args:
        revision: revise_paragraph() 반환값
        section_key: 섹션 키
        original_paragraph: 원본 문단 텍스트
        output_dir: 저장 루트 폴더 (WRITING_ANALYSIS_DIR)
        current_paper: 내가 쓰는 논문 이름

    Returns:
        저장된 MD 파일 경로. 실패 시 None.
    """
    if not revision:
        return None

    save_dir = output_dir / current_paper
    save_dir.mkdir(parents=True, exist_ok=True)
    md_path = save_dir / "revise_output.md"

    section_display = SECTION_DISPLAY.get(section_key, section_key)

    issues_text = _to_bullets(revision.get("issues", []))
    changed_text = _to_bullets(revision.get("what_changed", []))

    content = f"""\
---
section: "{section_display}"
my_paper: "{current_paper}"
created: {date.today().isoformat()}
tags: [revision, writing-coaching]
---

# 문단 수정 제안 — {section_display}

## 📋 원본 문단
> {original_paragraph.strip().replace(chr(10), chr(10) + '> ')}

---

## 🔍 논리 진단
{revision.get("diagnosis", "")}

## ❌ 발견된 문제
{issues_text}

---

## ✏️ 수정안
{revision.get("revised_paragraph", "")}

## 🔄 변경 사항 및 이유
{changed_text}

## 💡 다른 방식의 첫 문장
{revision.get("alternative_opening", "")}

---

## 📝 내 메모
> [수정안 검토 후 생각, 채택 여부 — 직접 작성]

-
"""

    md_path.write_text(content, encoding="utf-8")
    print(f"  → 저장: {md_path}")
    return md_path


def _improvement_blocks(improvements: list) -> str:
    blocks = []
    for item in improvements:
        if isinstance(item, dict):
            blocks.append(
                f"- **{item.get('what', '')}**\n"
                f"  - 왜: {item.get('why', '')}\n"
                f"  - 방법: {item.get('how', '')}"
            )
        else:
            blocks.append(f"- {item}")
    return "\n".join(blocks)


def generate_multi_report(
    coaching: dict,
    section_key: str,
    output_dir: Path,
    current_paper: str,
) -> Path | None:
    """멀티 논문 종합 코칭 보고서를 MD 파일로 저장.

    Args:
        coaching: analyze_multi_papers() 반환값
        section_key: 분석된 섹션 키
        output_dir: 저장 루트 폴더 (WRITING_ANALYSIS_DIR)
        current_paper: 내가 쓰는 논문 이름 (서브폴더명)

    Returns:
        생성된 MD 파일 경로. 실패 시 None.
    """
    if not coaching:
        return None

    save_dir = output_dir / current_paper
    save_dir.mkdir(parents=True, exist_ok=True)

    section_display = SECTION_DISPLAY.get(section_key, section_key)
    md_name = f"multi_coaching_{section_key}.md"
    md_path = save_dir / md_name

    source_papers = coaching.get("source_papers", [])
    papers_list = "\n".join(f"- {p}" for p in source_papers)

    blueprint = coaching.get("common_logic_blueprint", [])
    blueprint_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(blueprint))

    content = f"""\
---
title: "Multi-Paper Coaching: {section_display}"
section: "{section_display}"
my_paper: "{current_paper}"
source_count: {len(source_papers)}
created: {date.today().isoformat()}
tags: [writing-coaching, multi-analysis]
---

# 논리 코칭 보고서: {section_display}

> **목적**: {len(source_papers)}편의 우수 논문에서 논리 전개 패턴을 종합하여 내 초안을 코칭
> **비교 초안**: {current_paper}

## 📚 분석한 논문 ({len(source_papers)}편)
{papers_list}

---

## 🗺️ 우수 논문들의 공통 논리 청사진

{blueprint_text}

## 🔍 공통 논리 구성 방식
{coaching.get("common_patterns", "")}

---

## 📝 내 초안 평가
{coaching.get("my_draft_evaluation", "")}

## ❌ 내 초안에서 빠진 논리적 요소
{_to_bullets(coaching.get("missing_elements", []))}

---

## 🔧 우선 개선 방향
{_improvement_blocks(coaching.get("priority_improvements", []))}

## ✨ 지금 바로 적용할 것
{_to_bullets(coaching.get("rewrite_suggestions", []))}

---

## 📝 내 메모
> [코칭 내용을 읽고 든 생각, 구체적 실행 계획 — 직접 작성]

-
"""

    md_path.write_text(content, encoding="utf-8")
    print(f"  → 저장: {md_path}")
    return md_path
