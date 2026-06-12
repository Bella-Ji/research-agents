"""
config.py — 경로 및 API 설정
.env 파일에서 자동으로 읽어옵니다.
"""

import os
import sys
from pathlib import Path

# ── .env 파일 로드 ────────────────────────────────────────────────────
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    with open(_env_path, encoding="utf-8") as _f:
        for _line in _f:
            _line = _line.strip()
            if not _line or _line.startswith("#") or "=" not in _line:
                continue
            _key, _val = _line.split("=", 1)
            _key = _key.strip()
            _val = _val.strip().strip('"').strip("'")
            if _key and _val:
                os.environ.setdefault(_key, _val)
else:
    print("[안내] .env 파일이 없습니다. .env.example을 복사해서 .env를 만들어주세요.")


def _require_env(key: str, desc: str) -> str:
    val = os.getenv(key, "").strip()
    if not val:
        print(f"[오류] 환경변수 '{key}' 미설정 — {desc}")
        print(f"       .env 파일에 {key}=값 을 추가하세요.")
        sys.exit(1)
    return val


def _require_path(key: str, desc: str) -> Path:
    return Path(_require_env(key, desc))


# ── 경로 설정 ─────────────────────────────────────────────────────────
REFERENCE_ROOT = _require_path("REFERENCE_ROOT", "02. reference 폴더 루트 경로")
MARKDOWN_DIR   = _require_path("MARKDOWN_DIR",   "MD 파일 저장 폴더 (Obsidian 내 별도 폴더)")
JSON_PATH      = REFERENCE_ROOT / ".conversion_history.json"
GAP_JSON_PATH  = REFERENCE_ROOT / ".gap_exploration_history.json"

# ── citation_checker 전용 경로 ────────────────────────────────────────
BIB_PATH   = Path(os.getenv("BIB_PATH",   str(REFERENCE_ROOT / "library.bib")))
DRAFT_ROOT = Path(os.getenv("DRAFT_ROOT", str(REFERENCE_ROOT.parent / "01. 논문 작성")))

# ── writing_analyzer 전용 설정 ────────────────────────────────────────
WRITING_ANALYSIS_DIR = Path(os.getenv(
    "WRITING_ANALYSIS_DIR",
    str(REFERENCE_ROOT.parent / "01. 논문 작성" / "writing_analysis"),
))
SYNTHESIS_DIR = Path(os.getenv(
    "SYNTHESIS_DIR",
    str(REFERENCE_ROOT.parent / "01. 논문 작성" / "00. 졸업 논문" / "gap_synthesis"),
))
DRAFT_DIR    = Path(os.getenv("DRAFT_DIR", ""))
CURRENT_PAPER = os.getenv("CURRENT_PAPER", "WM paper")

# ── API 설정 ──────────────────────────────────────────────────────────
ANTHROPIC_API_KEY   = _require_env("ANTHROPIC_API_KEY", "Anthropic API 키")
CLAUDE_MODEL        = os.getenv("CLAUDE_MODEL", "claude-opus-4-5")
CLAUDE_TIMEOUT      = int(os.getenv("CLAUDE_TIMEOUT", "120"))
CLAUDE_REQUEST_DELAY = float(os.getenv("CLAUDE_REQUEST_DELAY", "2.0"))

# ── 처리 대상 폴더 목록 ───────────────────────────────────────────────
# pdf_summarizer 전용 (WM 논문용)
PDF_TARGET_FOLDERS = ["WM"]

# gap_explorer / gap_synthesizer 전용 (졸업논문 갭 탐색용)
GAP_TARGET_FOLDERS = ["phd"]

# 하위 호환용 (기존 에이전트 참조)
TARGET_FOLDERS = PDF_TARGET_FOLDERS

# ── Obsidian MD 템플릿 (pdf_summarizer) ──────────────────────────────
MARKDOWN_TEMPLATE = """\
---
title: "{title}"
year: {year}
author: "{author}"
journal: "{journal}"
doi: "{doi}"
tags: [{tags}]
created: {created}
source_folder: "{source_folder}"
source_pdf: "{pdf_filename}"
---

# {title}

## 서지정보 (Citation)
- **저자**: {author}
- **연도**: {year}
- **저널/출처**: {journal}
- **DOI**: {doi}
- **태그**: {hashtags}

## 📌 한줄 요약
{one_line}

## 초록 (Abstract)
{abstract}

## 🔑 핵심 주장 (English)
{key_claims_en}

## 🔑 핵심 주장 (한국어)
{key_claims_ko}

## 📐 연구 방법 (Method)
{method}

## 🔗 내 연구와의 연결점
{connection}

## 📎 인용 가능한 문장
{excerpts}

## 💡 새로운 연구 아이디어
{new_research_ideas}

## 📝 내 메모
> [이 논문에 대한 개인적인 생각, 비평, 질문 등 — 직접 작성]

-

---
**원본 PDF**: `{pdf_filename}` ({source_folder})
"""

# ── Obsidian MD 템플릿 (gap_synthesizer) ─────────────────────────────
SYNTHESIS_MARKDOWN_TEMPLATE = """\
---
type: gap-landscape
created: {created}
n_papers: {n_papers}
tags: [gap-landscape, gap-synthesizer, dissertation]
---

# 갭 지형 지도 — {created}

## 📚 분석 논문 ({n_papers}편)
{papers_list}

## 🗺️ 요약
{summary}

## 🔍 갭 군집
{gap_clusters}
## 🔗 미검증 경로
{underexplored_paths}

## 🔬 방법론적 갭
{methodological_gaps}

## 📚 이론 빈도
{dominant_theories}

## 📝 내 메모
> [직접 작성]
"""

# ── Obsidian MD 템플릿 (gap_explorer) ────────────────────────────────
GAP_MARKDOWN_TEMPLATE = """\
---
title: "{title}"
year: {year}
author: "{author}"
journal: "{journal}"
doi: "{doi}"
tags: [{tags}]
created: {created}
source_folder: "{source_folder}"
source_pdf: "{pdf_filename}"
---

# {title}

## 서지정보
- **저자**: {author}
- **연도**: {year}
- **저널**: {journal}
- **DOI**: {doi}
- **태그**: {hashtags}

## 🔓 열린 갭 (핵심 — Discussion/Limitation)
{core_gaps}
## 📖 선행연구 갭 (논리구조 참고용 — Introduction)
{intro_gaps}
## 📚 이론 프레임
{theories}

## 📝 내 메모
> [직접 작성]

---
**원본 PDF**: `{pdf_filename}` ({source_folder})
"""

# ── Obsidian MD 템플릿 (gap_strategist) ──────────────────────────────
STRATEGY_MARKDOWN_TEMPLATE = """\
---
type: gap-strategy
created: {created}
n_landscapes: {n_landscapes}
tags: [gap-strategy, research-model, dissertation]
---

# 연구 모형 전략 — {created}

## 📚 분석 지형 지도 ({n_landscapes}개)
{landscapes_list}

## ⭐ 최우선 추천
{recommendation}

## 🗺️ 갭 커버리지 (내 데이터로 채울 수 있는가)
{gap_coverage}
## 🧩 제안 모형
{viable_models}
## 🚫 제외 경로
{excluded_paths}

## 📝 내 메모
> [직접 작성]
"""
