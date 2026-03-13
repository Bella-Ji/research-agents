# lit_search — Obsidian Vault 기반 문헌 탐색 에이전트

Obsidian vault에 저장된 `_요약.md` 파일을 전체 스캔하여, 키워드 기반으로 관련 논문을 찾고 Claude API로 합성 출력하는 에이전트.

---

## 동작 방식

```
02. reference/ 전체 스캔
        ↓
*_요약.md 파일 파싱 (frontmatter + 한줄 요약)
        ↓
키워드 기반 관련도 스코어링
        ↓
상위 논문 → Claude API 합성
        ↓
논문 작업에 바로 쓸 수 있는 형태로 출력
```

### 스코어링 가중치

| 매칭 위치 | 점수 |
|---|---|
| tags (frontmatter) | +3 |
| title | +2 |
| source_folder (폴더명) | +2 |
| summary_kr (한줄 요약) | +1 |

---

## 출력 형식

1. **핵심 관련 논문** (상위 5편) — 왜 관련 있는지 한 문장 설명
2. **논문 활용 방법** — 어떻게 인용/활용할 수 있는지 구체적 제안
3. **APA 7판 인용 형식** — 각 논문의 인용 형식
4. **추가 탐색 제안** — vault에서 더 찾아볼 키워드·폴더 제안

---

## 실행

```bash
# run.py를 통해 실행 (research-agents/ 루트에서)
python run.py search                  # 대화형 모드
python run.py search "burnout"        # 키워드 직접 전달

# 또는 Claude Code에서 트리거 (CLAUDE.md 참고)
# "문헌 탐색해줘: [키워드]" 입력 시 자동 실행
```

---

## 지원 키워드

| 카테고리 | 키워드 |
|---|---|
| 이론 | `cor`, `jd-r`, `burnout`, `loss spiral` |
| 변수 | `emotional exhaustion`, `work meaning`, `mistreatment`, `recovery` |
| 조절/매개 | `moderation`, `first stage`, `second stage`, `mediation` |
| 방법론 | `dsem`, `multilevel`, `diary` |

키워드는 동의어를 자동 확장한다 (예: `cor` → `cor-theory`, `resource-loss`, `loss-spiral`, ...).

---

## vault 파일 요구사항

`_요약.md` 파일의 frontmatter에 아래 속성이 있어야 스코어링에 활용된다:

```yaml
---
title: "논문 제목"
author: "저자명"
year: 2023
journal: "저널명"
tags: [cor-theory, burnout, loss-spiral]
source_folder: "COR"
---

## 📌 한줄 요약
한 문장 핵심 요약 (한국어)
```

PDF 요약 에이전트(`pdf_summarizer`)가 생성한 파일은 이 형식을 자동으로 따른다.

---

## 파일 구성

```
lit_search/
├── agent.py      # 메인 로직 (스캔 → 검색 → 합성)
└── README.md
```

### agent.py 주요 함수

| 함수 | 역할 |
|---|---|
| `parse_md_file(filepath)` | `_요약.md` frontmatter + 본문 파싱 |
| `scan_vault(vault_root)` | vault 전체 스캔, 파싱 결과 리스트 반환 |
| `keyword_search(papers, query)` | 스코어링 기반 관련 논문 필터링 (상위 15편) |
| `synthesize_results(query, papers)` | Claude API로 합성 출력 생성 |
| `main()` | 대화형 검색 루프 |
