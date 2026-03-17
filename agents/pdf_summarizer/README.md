# pdf_summarizer — PDF 논문 자동 요약 에이전트

PDF 학술 논문을 Claude API로 분석하여 Obsidian 친화적인 Markdown 요약 노트로 변환한다.

---

## 동작 방식

```
PDF 파일 탐색 (02. reference/ 하위 폴더)
        ↓
PyMuPDF로 텍스트·메타데이터 추출
        ↓
Claude API로 핵심 내용 분석
        ↓
YAML frontmatter + 구조화된 섹션으로 MD 생성
        ↓
원본 PDF와 같은 폴더에 저장 (논문명_요약.md)
```

---

## 출력 MD 구조

```markdown
---
title: "논문 제목"
year: 2023
author: "저자명"
journal: "저널명"
doi: "10.xxxx/xxxxx"
tags: [literature, paper, cor-theory, burnout]
source_folder: "COR"
---

## 📌 한줄 요약       ← lit_search 스코어링에 활용
## 초록 (Abstract)
## 🔑 핵심 주장 (English)
## 🔑 핵심 주장 (한국어)
## 📐 연구 방법 (Method)
## 🔗 내 연구와의 연결점
## 📎 인용 가능한 문장
## 📝 내 메모          ← 직접 작성 공간
```

---

## 실행

```bash
# run.py를 통해 실행 (research-agents/ 루트에서)
python run.py pdf --batch           # 전체 일괄 처리
python run.py pdf --pick            # 대화형 선택
python run.py pdf --single "경로"  # 단일 파일
python run.py pdf --watch           # 폴더 감시 (새 PDF 추가 시 자동 처리)
```

---

## 주요 기능

- **중복 처리 방지**: 이미 요약된 논문은 자동 스킵 (`.conversion_history.json` 기반)
- **Fallback 시스템**: API 실패 시 메타데이터 기반 최소 노트 생성
- **Rate limit 자동 처리**: 429 오류 발생 시 30초 대기 후 재시도
- **한/영 병행 요약**: 핵심 주장을 영어 + 한국어로 동시 제공

---

## 파일 구성

```
pdf_summarizer/
├── main.py         # 실행 진입점 (--batch / --pick / --single / --watch)
├── extractor.py    # PDF 텍스트·메타데이터 추출 (PyMuPDF)
├── summarizer.py   # Claude API 요약 생성
├── markdown_gen.py # MD 파일 생성
└── __init__.py
```

### 주요 함수

| 파일 | 함수 | 역할 |
|---|---|---|
| extractor.py | `extract_pdf(path)` | PyMuPDF로 텍스트·메타데이터 추출 |
| summarizer.py | `summarize(text, metadata)` | Claude API 호출, 요약 딕셔너리 반환 |
| markdown_gen.py | `generate_md(summary, output_path)` | YAML frontmatter + 섹션 MD 파일 생성 |
| main.py | `main()` | CLI 옵션 파싱 및 흐름 제어 |

---

## 처리 대상 폴더

`config.py`의 `TARGET_FOLDERS`에 정의된 폴더만 스캔한다:

`burnout`, `COR`, `JD-R`, `emotional exhaustion`, `mistreatment`, `work meaning`, `DSEM`, `recovery` 등 (전체 목록은 `config.py` 참고)
