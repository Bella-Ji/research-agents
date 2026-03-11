# 📄 paper-md-summarizer

> PDF 학술 논문을 자동으로 분석하여 Obsidian 친화적인 Markdown 요약 노트로 변환하는 도구

[![Python](https://img.shields.io/badge/Python-3.12+-blue)](https://python.org)
[![Claude API](https://img.shields.io/badge/Claude-API-orange)](https://anthropic.com)
[![Obsidian](https://img.shields.io/badge/Obsidian-compatible-purple)](https://obsidian.md)

---

## ✨ 주요 기능

- **PDF 자동 분석**: Claude API가 논문을 읽고 핵심 내용을 추출
- **Obsidian 친화적 MD 생성**: YAML frontmatter + 구조화된 섹션으로 구성
- **PDF 파일 옆에 저장**: `논문명_요약.md` 형태로 원본 PDF와 같은 폴더에 생성
- **한/영 병행 요약**: 핵심 주장을 영어 + 한국어로 동시 제공
- **중복 처리 방지**: 이미 요약된 논문은 자동 스킵
- **Fallback 시스템**: API 실패 시에도 메타데이터 기반 최소 노트 생성
- **Rate limit 자동 처리**: 429 오류 발생 시 30초 대기 후 재시도

---

## 📁 생성되는 MD 파일 구조

```markdown
---
title: "논문 제목"
year: 2023
author: "저자명"
journal: "저널명"
doi: "10.xxxx/xxxxx"
tags: literature, paper, cor-theory, burnout
---

# 논문 제목

## 서지정보 (Citation)
## 한줄 요약
## 초록 (Abstract)
## 핵심 주장 (영어)
## 핵심 주장 (한국어)
## 연구 방법 (Method)
## 내 연구와의 연결점   ← 연구 맥락 기반 자동 생성
## 인용 가능한 문장
## 내 메모              ← 직접 작성 공간
```

---

## 🚀 시작하기

### 1. 설치

```bash
git clone https://github.com/Bella-Ji/paper-md-summarizer.git
cd paper-md-summarizer
pip install -r requirements.txt
```

### 2. 환경 설정

`.env.example`을 복사하여 `.env` 파일 생성:

```bash
cp .env.example .env
```

`.env` 파일 편집:

```
ANTHROPIC_API_KEY=your_api_key_here
REFERENCE_ROOT=C:/path/to/your/reference/folder
MARKDOWN_DIR=C:/path/to/output/folder
CLAUDE_MODEL=claude-opus-4-5
```

### 3. 실행

```bash
# 특정 논문 선택하여 처리
python main.py --pick

# 전체 폴더 일괄 처리
python main.py --batch

# 단일 PDF 처리
python main.py --single "path/to/paper.pdf"

# 폴더 감시 (새 PDF 추가 시 자동 처리)
python main.py --watch
```

---

## 📂 파일 구조

```
paper-md-summarizer/
├── main.py          # 메인 실행 파일
├── config.py        # 경로 및 API 설정
├── extractor.py     # PDF 텍스트/메타데이터 추출 (PyMuPDF)
├── summarizer.py    # Claude API 요약 생성
├── markdown_gen.py  # MD 파일 생성
├── .env.example     # 환경변수 예시
└── requirements.txt
```

---

## 🎯 활용 사례

이 도구는 **박사 논문 작성** 과정에서 수백 편의 학술 논문을 관리하기 위해 제작되었습니다.

- Obsidian vault에서 PDF와 요약 노트를 나란히 관리
- Claude Code와 연동하여 요약 노트를 근거로 논문 작성 지원
- 연구 분야별 폴더 구조를 그대로 유지하면서 요약 자동화

---

## 🔧 요구 사항

- Python 3.10+
- Anthropic API Key ([발급받기](https://console.anthropic.com))
- 주요 라이브러리: `anthropic`, `pymupdf`, `watchdog`, `python-dotenv`

---

## 📝 라이선스

MIT License

---

## 🙏 참고 프로젝트

- [JunyeongLee12/paper_auto_organization](https://github.com/JunyeongLee12/paper_auto_organization)
- [pymupdf/pymupdf4llm](https://github.com/pymupdf/pymupdf4llm)
