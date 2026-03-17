# research-agents

> 박사 논문 작성을 위한 연구 자동화 에이전트 모음

---

## 구조

```
research-agents/
├── run.py              # 통합 실행 진입점
├── config.py           # 공통 설정 (.env 로드)
├── requirements.txt
├── .env.example
├── agents/
│   ├── pdf_summarizer/ # PDF → Obsidian MD 요약 에이전트
│   ├── lit_search/     # Vault 기반 문헌 탐색 에이전트
│   ├── draft_reviewer/ # 논문 초안 검토 에이전트 (미구현)
│   └── citation_checker/ # 인용 형식 확인 에이전트 (미구현)
└── tools/
    └── theory_tagger.py  # 이론 태그 자동 추가 도구
```

---

## 실행 방법

```bash
# PDF 요약 에이전트
python run.py pdf --batch           # 전체 일괄 처리
python run.py pdf --pick            # 대화형 선택
python run.py pdf --single "경로"  # 단일 파일 처리
python run.py pdf --watch           # 폴더 감시 모드

# 문헌 탐색 에이전트
python run.py search                # 대화형 키워드 검색
python run.py search "burnout"      # 키워드 직접 전달

# 이론 태그 추가 도구
python run.py tag                   # 요약 MD에 이론 태그 자동 추가
```

---

## 환경 설정

`.env.example`을 복사하여 `.env` 파일 생성 후 편집:

```bash
cp .env.example .env
```

```
ANTHROPIC_API_KEY=your_api_key_here
REFERENCE_ROOT=C:/path/to/02. reference
MARKDOWN_DIR=C:/path/to/output
CLAUDE_MODEL=claude-haiku-4-5-20251001
```

---

## 에이전트별 상세 문서

| 에이전트 | 상태 | README |
|---|---|---|
| pdf_summarizer | 구현 완료 | [agents/pdf_summarizer/README.md](agents/pdf_summarizer/README.md) |
| lit_search | 구현 완료 | [agents/lit_search/README.md](agents/lit_search/README.md) |
| draft_reviewer | 미구현 | [agents/draft_reviewer/README.md](agents/draft_reviewer/README.md) |
| citation_checker | 미구현 | [agents/citation_checker/README.md](agents/citation_checker/README.md) |
| theory_tagger | 구현 완료 | [tools/README.md](tools/README.md) |

---

## 요구 사항

- Python 3.12+
- Anthropic API Key ([발급받기](https://console.anthropic.com))
- 주요 라이브러리: `anthropic`, `pymupdf`, `watchdog`, `python-dotenv`

```bash
pip install -r requirements.txt
```
