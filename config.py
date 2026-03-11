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

# ── API 설정 ──────────────────────────────────────────────────────────
ANTHROPIC_API_KEY   = _require_env("ANTHROPIC_API_KEY", "Anthropic API 키")
CLAUDE_MODEL        = os.getenv("CLAUDE_MODEL", "claude-opus-4-5")
CLAUDE_TIMEOUT      = int(os.getenv("CLAUDE_TIMEOUT", "120"))
CLAUDE_REQUEST_DELAY = float(os.getenv("CLAUDE_REQUEST_DELAY", "2.0"))

# ── 처리 대상 폴더 목록 ───────────────────────────────────────────────
TARGET_FOLDERS = [
    "burnout",
    "coping",
    "COR",
    "depletion",
    "DSEM",
    "emotional exhaustion",
    "esm",
    "intervention",
    "JD-R",
    "job crafting",
    "leadership",
    "methodology",
    "mistreatment",
    "mistreatment by patient",
    "nurse stressor",
    "nurse work environment",
    "occupational health psychology",
    "positive psychology",
    "psychosocial health",
    "psychosocial safety climate",
    "recovery, resources",
    "recovery, work meaningfulness-항",
    "sampling",
    "shift work-diary study, review",
    "sleep",
    "social stressor_well-being",
    "sonnentag",
    "statistics",
    "stress management",
    "well-being",
    "work meaning",
]

# ── Obsidian MD 템플릿 ────────────────────────────────────────────────
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

## 📝 내 메모
> [이 논문에 대한 개인적인 생각, 비평, 질문 등 — 직접 작성]

-

---
**원본 PDF**: `{pdf_filename}` ({source_folder})
"""
