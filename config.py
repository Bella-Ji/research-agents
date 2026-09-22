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
PAPER_FOLDER_MAP = {
    "dissertation": "00. 졸업 논문",
    "WM paper": "01. 투고 논문 작성(WM)",
}

CURRENT_PAPER = os.getenv("CURRENT_PAPER", "WM paper")
_paper_folder = PAPER_FOLDER_MAP.get(CURRENT_PAPER, CURRENT_PAPER)

CURRENT_STUDY = os.getenv("CURRENT_STUDY", "")
_study_subfolder = Path(CURRENT_STUDY) if CURRENT_STUDY else Path(".")

SYNTHESIS_DIR = Path(os.getenv(
    "SYNTHESIS_DIR",
    str(REFERENCE_ROOT.parent / "01. 논문 작성" / _paper_folder / "gap_synthesis" / _study_subfolder),
))
DRAFT_DIR    = Path(os.getenv("DRAFT_DIR", ""))

# ── API 설정 ──────────────────────────────────────────────────────────
ANTHROPIC_API_KEY   = _require_env("ANTHROPIC_API_KEY", "Anthropic API 키")
CLAUDE_MODEL        = os.getenv("CLAUDE_MODEL", "claude-opus-4-5")
CLAUDE_TIMEOUT      = int(os.getenv("CLAUDE_TIMEOUT", "120"))
CLAUDE_REQUEST_DELAY = float(os.getenv("CLAUDE_REQUEST_DELAY", "2.0"))

# ── pdf_summarizer 연구 맥락 (선택) ──────────────────────────────────
# 특정 논문 주제에 맞춰 요약을 커스터마이즈하려면 .env에 값을 채우세요.
# 전부 비워두면 범용 요약 모드(주제 무관)로 동작합니다.
RESEARCH_TOPIC      = os.getenv("RESEARCH_TOPIC", "")       # 예: 직장 내 부당대우 → 정서적 소진 → 일의 의미감 매개 경로
RESEARCH_THEORY     = os.getenv("RESEARCH_THEORY", "")      # 예: COR theory, JD-R model
RESEARCH_MODERATOR  = os.getenv("RESEARCH_MODERATOR", "")   # 예: 직무 소진 (job burnout, person-level)
RESEARCH_POPULATION = os.getenv("RESEARCH_POPULATION", "")  # 예: 한국 간호사/의료 종사자
RESEARCH_METHOD     = os.getenv("RESEARCH_METHOD", "")      # 예: DSEM (다층 구조방정식모형), 일기 연구
RESEARCH_VARIABLES  = os.getenv("RESEARCH_VARIABLES", "")   # 예: t_MPFs/MBSs/MBCs, t_EE, t_JC, ND_WM, ND_REC, ND_SBR

# ── 처리 대상 폴더 목록 ───────────────────────────────────────────────
# pdf_summarizer 전용: REFERENCE_ROOT 바로 아래 모든 하위 폴더를 자동으로 스캔한다.
# (MD 출력 폴더와 숨김 폴더는 제외. 새 폴더를 추가해도 코드 수정 없이 자동으로 포함됨)
PDF_TARGET_FOLDERS = sorted(
    p.name for p in REFERENCE_ROOT.iterdir()
    if p.is_dir() and not p.name.startswith(".") and p.name != MARKDOWN_DIR.name
) if REFERENCE_ROOT.exists() else []

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
