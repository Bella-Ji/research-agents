# citation_checker — APA 7판 인용 형식 검사 에이전트

Obsidian 논문 초안 MD 파일과 Mendeley `library.bib`를 대조하여 APA 7판 인용 오류를 자동 검출한다.

---

## 동작 방식

```
초안 .md 파일 + 10. reference.md
        ↓
인텍스트 인용 추출 (괄호형 / 서술형)
        ↓
APA 7판 형식 규칙 검사
        ↓
library.bib 대조 (저자 수, 등록 여부)
        ↓
참고문헌 목록 형식 검사 + 교차 검사
        ↓
터미널 리포트 출력 (또는 MD 파일 저장)
```

---

## 검사 항목

### 인텍스트 인용 (본문)

| 검사 항목 | 예시 오류 | 수정 |
|---|---|---|
| `et al.` 마침표 누락 | `(Hobfoll et al, 2018)` | `(Hobfoll et al., 2018)` |
| `Et al.` 대문자 | `(Smith Et al., 2020)` | `(Smith et al., 2020)` |
| 괄호형 `and` 사용 | `(Smith and Jones, 2020)` | `(Smith & Jones, 2020)` |
| 서술형 `&` 사용 | `Smith & Jones (2020)` | `Smith and Jones (2020)` |
| library.bib 미등록 | `(Unknown, 2023)` | Mendeley 등록 필요 |
| et al. 과용 (1–2저자) | `(Lee & Park et al., 2021)` | `(Lee & Park, 2021)` |
| et al. 누락 (3저자 이상) | `(Smith, 2020)` (실제 4저자) | `(Smith et al., 2020)` |

### 참고문헌 목록 (10. reference.md)

| 검사 항목 | 예시 |
|---|---|
| DOI 말줄임 | `https://doi.org/10.1146/annurev-orgpsych-` |
| 구버전 DOI 형식 | `http://dx.doi.org/...` |
| DOI 자리에 URL 혼용 | `https://doi.org/https://www.statmodel.com/...` |
| 저자 형식 오류 | `Firstname Lastname` → `Lastname, F.` |
| 연도 형식 오류 | `(2020)` 뒤에 마침표 없음 |
| 알파벳 순서 위반 | S 다음에 A가 오는 경우 |
| 본문 인용 → 목록 누락 | 초안에 인용됐으나 목록에 없음 ❌ |
| 목록만 있고 본문 미인용 | 목록에 있으나 어디에도 인용 안 됨 ⚠️ |

---

## 실행

```bash
# research-agents 루트에서 실행

# 단일 파일 인텍스트 검사
python run.py cite --file "draft/1. introduction.md"

# 폴더 내 전체 MD 인텍스트 검사
python run.py cite --dir "01. 논문 작성/WM paper/draft"

# 참고문헌 목록만 검사
python run.py cite --ref "draft/10. reference.md"

# 전체 교차 검사 (초안 + 참고문헌 목록)
python run.py cite --dir "draft/" --ref "draft/10. reference.md"

# 결과를 MD 파일로 저장
python run.py cite --dir "draft/" --ref "draft/10. reference.md" --save
```

Claude Code에서 자연어로도 실행 가능:
> "인용 검사해줘", "참고문헌 목록 검사해줘", "초안 전체 교차 검사해줘"

---

## Mendeley 연동 방식

**BibTeX 자동 동기화** 사용 — Mendeley Desktop이 `library.bib`를 자동 갱신한다.

- Mendeley Desktop → Tools → Options → BibTeX → Enable BibTeX syncing
- 동기화 경로: `02. reference/library.bib`
- 라이브러리 변경 시 자동 갱신 → citation_checker가 항상 최신 데이터 참조

---

## 출력 예시

```
══════════════════════════════════════════════════════════════
  📋 APA 7판 인용 검사 리포트
  BibTeX: library.bib  |  2026-04-28
══════════════════════════════════════════════════════════════
  총 인용 24개  |  오류 2개  |  경고 1개

  📄 1. introduction.md
     인용 24개 (괄호형 20 / 서술형 4)  |  ❌ 2  ⚠️  1

  ❌  [줄   5]  [괄호형]  'et al' 뒤에 마침표(.) 누락
       원문:  Hobfoll et al, 2018
       수정:  Hobfoll et al., 2018

  ⚠️   [줄  18]  [괄호형]  저자 3명인데 'et al.' 없음
       원문:  Smith, 2020
       수정:  Smith et al., 2020

══════════════════════════════════════════════════════════════
  📚 참고문헌 목록 검사 리포트 (APA 7판)
  파일: 10. reference.md  |  항목: 62개
══════════════════════════════════════════════════════════════
  형식 오류 1건  |  경고 0건  |  순서 위반 0건
  누락(본문→목록 불일치) 0건  |  미인용(목록→본문 불일치) 2건

  ❌  [줄 292]  DOI가 잘린 것 같습니다
       원문:  Hobfoll, S. E., ... https://doi.org/10.1146/annurev-orgpsych-…
       수정:  DOI 전체 주소를 확인·보완하세요
```

---

## 파일 구성

```
citation_checker/
├── bib_loader.py       # library.bib 파싱 및 (저자, 연도) 인덱스 생성
├── parser.py           # MD 파일에서 인텍스트 인용 추출 (괄호형 + 서술형)
├── checker.py          # APA 7판 인텍스트 인용 규칙 검사
├── ref_list_checker.py # 참고문헌 목록 형식 검사 + 교차 검사
├── reporter.py         # 결과 터미널 출력 및 MD 파일 저장
└── main.py             # CLI 진입점
```

### 주요 함수

| 파일 | 함수 | 역할 |
|---|---|---|
| `bib_loader.py` | `load_bib(path)` | BibTeX 파싱 → BibEntry 목록 |
| `bib_loader.py` | `build_index(entries)` | (저자, 연도) → BibEntry 인덱스 |
| `parser.py` | `extract_citations(md_path)` | MD에서 Citation 목록 추출 |
| `checker.py` | `check_citation(cit, bib_index)` | 단일 인용 검사 → CiteError 목록 |
| `ref_list_checker.py` | `parse_ref_list(md_path)` | 참고문헌 목록 파싱 → RefEntry 목록 |
| `ref_list_checker.py` | `check_ref_entry(entry, bib_index)` | 단일 항목 형식 검사 |
| `ref_list_checker.py` | `check_alphabetical(entries)` | 알파벳 순서 위반 탐지 |
| `ref_list_checker.py` | `cross_check(citations, entries)` | 본문 ↔ 목록 완결성 검사 |

---

## 설정

`config.py` 또는 `.env`에서 경로 변경 가능:

```env
BIB_PATH=C:/path/to/library.bib        # 기본: REFERENCE_ROOT/library.bib
DRAFT_ROOT=C:/path/to/draft/folder     # 기본: 01. 논문 작성/
```
