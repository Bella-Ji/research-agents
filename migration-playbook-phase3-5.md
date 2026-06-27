# Claude Code 마이그레이션 플레이북 — Phase 3~5 (v3)

> **현재 상태 (2026-06-27 기준):**
> - Phase 1~2 완료 (context 분리, gap 파이프라인)
> - Phase 3 완료 (pdf-summarizer, lit-searcher — 커밋 완료)
> - Phase 4 완료 (draft-reviewer, citation-checker — 커밋 c0870b0)
> - **⏸ Phase 4 실전 테스트 미완** ← 지금 여기서 시작
>
> 사용법: 위→아래 순서대로. `[프롬프트]`는 Claude Code에 복붙, `[직접]`은 서현이 할 일.
> 각 프롬프트는 자체 완결로 작성됨 — 세션 끊겨도 바로 사용 가능.

---

## 재진입 — 매번 시작 시

[직접] WSL 터미널에서:
```bash
cd "/mnt/c/Users/user/Documents/00.seohyun/Doctor/0. 졸업논문 준비/research-agents"
claude --continue
```
> 시간이 많이 지났으면 `claude`로 새 세션. 아래 첫 프롬프트가 맥락을 다시 잡아줌.
> `/agents`로 에이전트 목록 확인 — citation-checker, draft-reviewer 보이면 정상.

---

## ✅ Phase 3 — 완료 (참고용)

**결정 사항 (실제 구현):**
- pdf-summarizer: PyMuPDF, 인용 자체검증(grep bash 실행 + N/N 일치 보고), context 파일 참조(research-profile.md SSOT), *_요약.md 저장
- lit-searcher: **Option B (grep 기반 + LLM 질적 판단)** 선택. 가중치 스코어링 방식 기각.
  - 종료조건 추가: 3회 변형 시도 후 결과 없으면 강제 종료 (31회 루프 방지용)
- fablize: local scope 설치, always-on, hooks를 `settings.local.json`에 명시적으로 등록 (세션 간 유지됨)

---

## ✅ Phase 4 — 개발 완료, 실전 테스트 미완

**결정 사항 (실제 구현):**
- citation-checker: `python3 run.py cite` 실행 (원본 `agents/citation_checker/` 모듈 호출). scripts/ 복사본은 Phase 5에서 경로 전환 예정. 에이전트는 스크립트 결과만 정리하고 임의 추가/삭제 금지.
- draft-reviewer: theory 태그 요약 자동 수집, 이론 프레임은 research-profile.md 참조 (topic-neutral — WM 논문 전용 아님). 3요소 형식 강제 (지적 + 근거 + Before/After). vault 검색은 `head -5` 제한 (루프 방지).

### 4-T. [프롬프트] Phase 4 실전 테스트 (WM 논문 최종 리뷰 겸)

```
Phase 4 실전 테스트를 WM 논문 최종 리뷰와 겸해서 진행할게.
에이전트·커맨드 파일은 이전 세션에서 모두 생성 및 커밋됨(c0870b0).

테스트 1 — citation-checker:
/check-citations [WM 논문 파일 경로]
스크립트(run.py cite) 원본 리포트와 에이전트 정리본을 나란히 보여줘.
추가·누락된 항목이 있으면 표시.

테스트 2 — draft-reviewer:
/review-draft [WM 논문 파일 경로] [섹션명]
검토 의견마다 3요소(지적/근거/수정안) 갖췄는지 ✓/✗ 표시해줘.
```
> [직접] `[WM 논문 파일 경로]`와 `[섹션명]` 교체. 추천 섹션: Discussion 또는 Theoretical Implications.

### 4-T2. [직접] 결과 검토
- **citation-checker**: 스크립트 리포트 ↔ 에이전트 정리본 1:1 대응 확인. 누락 또는 임의 추가 없는지.
- **draft-reviewer**: 이론 지적이 COR/JD-R 이해에 기반했는지, 틀린 지적은 없는지.
  - 틀린 지적 발견 시: "이 지적은 ~라서 부적절, 이런 오판을 막는 기준을 draft-reviewer 지침에 추가해줘"로 피드백.
- 통과하면 [프롬프트]:
```
Phase 4 테스트 통과. 테스트 중 수정한 지침 있으면 같이 커밋해줘:
"Phase 4 검증 완료 + 지침 보강"
그다음 Phase 5 진행해줘.
```

---

## Phase 5 — writing-analyzer + 오케스트레이터 정비

### 5-1. [프롬프트] 시작

```
PRD Phase 5 진행해줘.

[writing-analyzer]
1. 기존 3개 모드를 /coach-writing 커맨드 인자로 통합:
   --analyze(1:1 비교) / --multi(good_papers 종합) / --revise(문단 수정).
2. revise 모드는 기존 multi_coaching_*.md 산출물을 기준 파일로 재사용하는
   2단계 구조 유지. 기준 파일이 없으면 --multi 먼저 실행하라고 안내.
3. good_papers 폴더 경로는 config.py 설정 따름.

⚠️ CLAUDE.md에 fablize always-on 블록(<!-- FABLIZE:BEGIN -->~<!-- FABLIZE:END -->)이
있다. 재작성 시 이 블록은 그대로 보존하고 건드리지 말 것.

[CLAUDE.md 오케스트레이터 재작성]
1. 기존 CLAUDE.md를 CLAUDE.md.bak으로 백업 후 재작성:
   - 6개 slash command와 에이전트들의 역할 한 줄 요약 + 라우팅 기준
   - context/ 3개 파일 = 단일 진실 공급원(SSOT),
     "context와 코드가 다르면 context가 정답" 명시
   - 자연어 트리거: "이 논문 요약해줘"→/summarize-pdf,
     "갭 찾아줘"→/find-gaps, "관련 논문 찾아줘"→/search-lit,
     "인용 검사"→/check-citations, "초안 검토"→/review-draft,
     "글쓰기 코칭"→/coach-writing
2. 기존 CLAUDE.md 내용 중 새 구조와 충돌하는 부분은 목록으로 보고하고
   처리 방향은 내 확인 받아.
3. citation-checker의 scripts/ 경로 전환: 에이전트 지침에서
   `python3 run.py cite` → `python3 scripts/citation_checker/main.py`로
   교체 (Phase 4에서 미룬 것). 교체 전 scripts/ 버전 동작 확인할 것.

만들 파일 목록과 설계를 먼저 보여주고 내 확인 받고 작성해.
```

### 5-2. [프롬프트] 통합 테스트

```
통합 테스트. slash command 없이 자연어로만 아래를 순서대로 처리해봐.
각 요청마다 어느 에이전트로 라우팅했는지 먼저 밝히고 실행해:
1. "[테스트 PDF 경로] 이 논문 요약해줘"
2. "방금 요약한 논문이 내 연구랑 어떻게 연결되는지, vault에서 관련 논문도
   같이 찾아서 정리해줘" (→ lit-searcher 연계 확인)
3. "[초안 경로] 인용 형식 검사해줘"
라우팅이 틀리면 멈추고 보고해.
```

### 5-3. [직접] 마감 결정

- 라우팅 3건 정확 → 마이그레이션 완료. [프롬프트]:
```
Phase 5 git commit ("Phase 5: writing-analyzer, 오케스트레이터 정비 —
마이그레이션 완료") 해줘.
```
- 마지막 결정 2가지 (급하지 않음, 1~2주 새 시스템 써본 뒤):
  ① run.py 정리: "run.py와 agents/ 하위 Python 중 scripts/로 이동한 것
    제외하고 archive/로 이동해줘 (삭제 금지)"
  ② 외부 플러그인: "claude-scientific-writer에서 citation-management,
    scientific-writing, peer-review 스킬만 .claude/skills/로 복사"

### 5-4. [프롬프트] 사용 가이드 README 생성

```
마이그레이션이 완료됐으니 루트 README.md를 사용 가이드로 재작성해줘.
기존 README.md는 README_python.md로 이름 변경해 보존 (구 시스템 참고용).
새 README는 "이 시스템을 처음 보는 미래의 나"가 읽는다고 가정하고,
실제로 구현된 최종 상태 기준으로 정확하게 작성해 (PRD의 계획이 아니라
.claude/ 안의 실제 파일들을 읽고 쓸 것). 포함할 내용:

1. 시스템 한눈에 보기
   - 3층 구조 설명: 커맨드(/...)가 에이전트를 호출하고, 에이전트가
     context·스킬을 참조한다
   - 전체 에이전트 목록과 한 줄 역할, 사용 모델(haiku 지정 여부 포함)

2. 빠른 시작
   - 폴더 진입 + claude 실행 (경로 포함)
   - 이어하기: claude --continue
   - /agents로 에이전트 확인

3. 사용법 3가지 (각각 실제 예시 2개 이상)
   a. 슬래시 커맨드: 6개 커맨드 전체의 문법·인자·기본값·산출물
      위치를 표로 (예: /find-gaps [폴더, 생략 시 phd/] → 갭분석.md +
      gap_landscape_*.md + gap_strategy_*.md)
   b. 자연어: CLAUDE.md 라우팅 트리거 문구 예시
   c. 에이전트 직접 지명: 파이프라인 중 한 단계만 재실행하는 예시

4. 대표 워크플로우 시나리오 3개 (처음부터 끝까지)
   - 새 논문 1편 받았을 때: 요약 → vault 연관 논문 확인
   - 연구 주제 탐색: 폴더 단위 /find-gaps → strategy 파일 읽는 법
   - 초안 검토: /check-citations → /review-draft → /coach-writing --revise

5. context 파일 관리 규칙
   - 3개 파일의 역할과 SSOT 원칙
   - 변인사전이 바뀌면 어디를 고쳐야 하는지 (옵시디언 원본 → context
     동기화 절차)

6. 산출물 위치 지도: 어떤 작업이 어떤 폴더에 뭘 만드는지 한 표로

7. 문제 해결
   - 에이전트 인식 안 됨 → 재시작
   - 인용 자체검증 실패 보고가 뜰 때 의미
   - 기존 Python 시스템(run.py)으로 같은 작업 돌리는 법 (병행 기간용)

작성 후 git commit ("docs: 사용 가이드 README") + push까지.
```

---

## 공통 규칙

- Claude Code가 "내 확인" 단계를 건너뛰고 진행하면 → Esc 중단 후
  "방금 단계 보고부터 보여줘"
- 기존 산출물(*_요약.md, *_갭분석.md, history JSON) 덮어쓰기 발견 →
  즉시 중단, "git status로 변경 확인하고 의도하지 않은 변경 되돌려줘"
- 새 서브에이전트 인식 안 됨 → /exit 후 claude --continue 재시작
- 검증 보고는 항상 "평가·결론 없이 기계적으로" 요구 — 판단은 서현이가
