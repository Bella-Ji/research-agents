# citation_checker — 인용 형식 확인 에이전트

> **상태: 미구현** — 졸업논문 작성 시점에 개발 예정

---

## 계획된 기능

논문 초안의 인용을 Mendeley 라이브러리와 대조하여 오류를 자동 검출한다.

1. 초안 `.md` 파일에서 인용 패턴 추출 (`Author, Year` / `(Author et al., Year)`)
2. `02. reference/library.bib` (Mendeley BibTeX 자동 동기화 파일)와 대조
3. 오류 항목 및 수정 제안 출력

---

## 검출 항목 (예정)

| 검사 항목 | 설명 |
|---|---|
| 저자명 불일치 | 초안의 저자명이 BibTeX 실제 저자와 다른 경우 |
| 연도 오류 | 연도가 BibTeX와 다른 경우 |
| et al. 적용 오류 | 저자 수 기준 APA 7판 et al. 규칙 위반 |
| 라이브러리 미등록 | 인용된 논문이 Mendeley에 없는 경우 |
| 형식 오류 | 괄호, 쉼표, 앰퍼샌드(&) 위치 등 APA 7판 형식 위반 |

---

## Mendeley 연동 방식

**BibTeX 자동 동기화** 사용 (SQLite DB 직접 접근 방식은 불안정하여 미채택)

- Mendeley Desktop → Tools → Options → BibTeX → Enable BibTeX syncing
- 동기화 경로: `02. reference/library.bib`
- 라이브러리 변경 시 자동 갱신 → citation_checker가 항상 최신 데이터 참조

---

## 실행 (예정)

```bash
python run.py cite --file "draft/section.md"
python run.py cite --all                      # draft/ 전체 검사
```

---

## 파일 구성

```
citation_checker/
└── __init__.py    # 미구현
```
