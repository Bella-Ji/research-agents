# Claude Code 마이그레이션 플레이북 — Phase 3~5 (v2)

> 전제: Phase 1~2 완료 (context 분리, gap 파이프라인, 검증 보강 4건 반영,
> pre-migration 커밋 3개 포함 git clean 상태).
> 사용법: 위→아래 순서대로. `[프롬프트]`는 Claude Code에 복붙, `[직접]`은 서현이 할 일.
> 시간이 지나 다시 시작해도 되도록 각 프롬프트는 자체 완결로 작성됨.

---

## Phase 3 시작 전 — 세션 재개 (나중에 돌아왔을 때)

[직접] WSL 터미널에서:
```bash
cd "/mnt/c/Users/user/Documents/00.seohyun/Doctor/0. 졸업논문 준비/research-agents"
claude
```
- 직전 세션을 잇고 싶으면 `claude --continue`. 시간이 많이 지났으면 그냥
  `claude`로 새 세션이 깔끔함 (아래 3-1 프롬프트가 맥락을 다시 잡아줌).
- 새 세션이면 `/agents`로 gap 3개 에이전트가 보이는지만 먼저 확인.

---

## Phase 3 — pdf-summarizer, lit-searcher 마이그레이션

### 3-1. [프롬프트] 시작 (새 세션에서도 그대로 사용 가능)

```
research-agent-team-PRD-v2.md를 읽고 현재 진행 상태를 파악해줘.
Phase 1~2는 완료된 상태야 (git log와 .claude/agents/, .claude/context/
확인). 오늘은 PRD Phase 3 — pdf-summarizer, lit-searcher 마이그레이션이야.

시작 전에 만들 파일 목록과 각 파일의 핵심 설계를 먼저 보여주고
내 확인을 받아. 설계 시 지켜야 할 것:

[pdf-summarizer]
1. 출력 형식·파일명 규칙(*_요약.md)·frontmatter(특히 type, tags 필드)·
   저장 경로는 기존 agents/pdf_summarizer/의 템플릿과 동일하게 유지.
2. 연구 맥락은 에이전트 MD에 다시 쓰지 말고 .claude/context/
   research-profile.md의 "이중 역할 (a) 문헌 요약 시" 관점을 참조.
3. "내 연구와의 연결점" 섹션은 variable-dictionary.md의 실제 변인과
   연결해 기술.
4. 원문 인용 규칙은 gap-explorer.md와 동일하게: 담화표지 포함 문장 전체를
   한 글자도 바꾸지 말 것 + 저장 전 추출 텍스트 대상 부분문자열 자체검증
   (N건 중 N건 일치를 보고에 포함).
5. PDF 텍스트 추출은 gap-explorer와 같은 방식(PyMuPDF) — 일관성 유지.
6. 📝 메모류 placeholder가 템플릿에 있으면 그대로 둘 것.
7. new_research_ideas 필드의 역할 경계를 지침에 명시: 해당 논문 1편에서
   파생되는 가벼운 아이디어 제안까지만 (보유 변인 코드 사용은 유지).
   갭 종합·교차지연 검증·모형 설계는 gap 파이프라인(/find-gaps) 몫이므로
   여기서 하지 말 것.

[lit-searcher]
1. 기존 키워드 스코어링 가중치(tags+3/title+2/folder+2/summary+1)를
   유지할지, Grep 기반으로 단순화할지 양쪽 장단점을 먼저 제시하고
   내 결정을 받아. vault의 *_요약.md 총 개수도 함께 알려줘.
2. 검색 대상은 vault의 *_요약.md (config.py 경로 설정 따름).
3. 합성 결과의 모든 주장에 출처 요약 파일명을 표기.

기존 Python 코드와 run.py는 수정·삭제 금지.
```

### 3-2. [직접] lit-searcher 스코어링 방식 결정
- 판단 기준: 요약 파일이 수백 편 이상 + 검색 재현성 중요 → **스코어링
  스크립트 유지**. 수십~백여 편 + 의미 기반 유연 검색이 더 중요 →
  **Grep+LLM 판단**. Claude Code가 알려준 파일 개수 보고 결정.

### 3-3. [프롬프트] pdf-summarizer 테스트

```
이미 기존 Python으로 요약된 PDF 중 1편을 골라 pdf-summarizer 서브에이전트로
재요약하고, 출력은 *_요약_subagent.md로 저장해 (기존 요약 덮어쓰기 금지).
그다음 기계적 비교표를 만들어줘 (평가·결론 없이):
1. frontmatter 필드별 대조 (type, tags 등)
2. 섹션 구조 일치 여부
3. 원문 인용 각각의 PDF 추출 텍스트 exact match 검사 (공백 정규화 포함)
   — 기존 Python 출력의 인용도 같이 검사해서 나란히
4. "내 연구와의 연결점"에 언급된 변인코드가 variable-dictionary.md에
   존재하는지
```

### 3-4. [직접] 비교표 검토
- ① 인용 exact match: 자체검증 단계 덕에 새 출력이 기존 이상이어야 정상.
  미달이면 "자체검증 단계가 실제로 실행됐는지 작업 로그 보여줘"로 추궁.
- ② 연결점 섹션 품질: 기존 요약과 직접 읽고 비교 — 연구 연관성 파악이
  더 정확한가 (내용 판단, 직접 해야 함). 통과면 ↓

### 3-5. [프롬프트] lit-searcher 테스트 — M2 문헌 확인 겸용

```
pdf-summarizer 확정. lit-searcher 테스트를 실전 질문으로 진행할게.

검색 1: "부당대우 회복" (또는 mistreatment recovery)
검색 2: "abusive supervision"

각 검색에 대해 ① 매칭된 요약 파일 목록(점수 포함) ② 합성 답변
③ 합성 답변의 각 주장별 출처 파일명 표기 여부를 보여줘.
기존 python run.py search를 같은 키워드로 돌린 결과와 매칭 목록을
나란히 비교해줘 (누락 논문 확인용).

검색 1 합성 답변에는 다음 질문을 반영해줘: "부당대우(또는 대인 스트레서)가
회복경험(recovery experiences)을 거쳐 회복상태로 이어지는 경로가 내 vault의
일기연구 문헌에서 이미 검증된 적이 있는가?" — gap_strategy의 M2 모형
(부당대우→ND_REC→ND_SBR 조절된 매개)의 선행연구 중복 확인 목적이야.
```

### 3-6. [직접] 결과 검토 (이중 목적)
- **lit-searcher 검증**: 기존 대비 매칭 누락 여부, 출처 없는 주장(환각) 여부.
- **M2 판단 재료**: 검색 1 답변으로 M2 경로의 기존 검증 여부 확인.
  - 이미 같은 경로를 검증한 일기연구가 있으면 → M2 차별성 재검토 필요
    (gap_strategy의 다른 모형 검토 또는 조절변인으로 차별화).
  - 없거나 부분적이면 → M2 졸업논문 후보로 유력. 추가로 볼 것:
    ND_SBR 2문항 신뢰도, 부당대우→REC 동시점 경로의 인과 논리 보강.
- 통과면 ↓

### 3-7. [프롬프트] Phase 3 마감

```
Phase 3 변경사항 전체를 git commit 해줘.
커밋 메시지: "Phase 3: pdf-summarizer, lit-searcher 마이그레이션"
커밋 후 변경 파일 목록 요약해서 보여줘.
```

---

## Phase 4 — draft-reviewer 신규 + citation-checker 하이브리드

### 4-1. [프롬프트] 시작

```
PRD Phase 4 진행해줘. 두 에이전트의 역할 경계:
인용 형식 검사 = citation-checker / 인용 내용·논리 검사 = draft-reviewer.

[citation-checker — 하이브리드]
1. 기존 agents/citation_checker/ Python 모듈을 scripts/citation_checker/로
   복사 (동작 확인 전까지 원본 유지, 정리는 내 확인 받고).
2. 에이전트 MD: 스크립트를 Bash로 실행 → 리포트 파싱 → 오류를 심각도순
   정리 → 파일별 일괄 수정안 제시. 스크립트가 잡은 오류 목록을 에이전트가
   임의로 추가·삭제하지 말 것 (스크립트 결과가 기준).
3. library.bib 경로는 config.py 설정을 따름.

[draft-reviewer — 신규]
1. agents/draft_reviewer/README.md의 설계 그대로 구현: type: theory 태그
   요약 자동 수집 → 이론 정합성 → 인용-주장 정렬 → 학술 어조(hedging) →
   구조(topic sentence-근거-연결) → Before/After 수정 제안.
2. 이론 정합성 판단 기준은 research-profile.md의 이론 프레임 표 참조.
3. 검토 의견은 반드시 "지적 + 근거(어느 요약/이론) + 수정안" 3요소.
4. humanizer_academic 스킬이 설치되어 있으면 어조 제안 시 참조.

두 에이전트 모두 초안 원본을 직접 수정하지 말고 검토 보고서만 생성.
만들 파일 목록과 설계를 먼저 보여주고 내 확인 받고 작성해.
```

### 4-2. [프롬프트] 테스트 — 실행 전 경로 교체 필수

```
테스트:
1. /check-citations를 [초안 파일 경로]로 실행. 스크립트 원본 리포트와
   에이전트 정리본을 둘 다 보여줘 — 추가·누락 대조 가능하게.
2. /review-draft를 같은 파일의 [섹션명] 섹션으로 실행. 검토 의견 각각에
   3요소(지적/근거/수정안)가 갖춰졌는지 표시해줘.
```
> [직접] `[초안 파일 경로]`·`[섹션명]` 교체. 추천: WM 논문 Discussion 또는
> Theoretical Implications — 내용을 제일 잘 아는 섹션이라 검토 품질 판단이 쉬움.

### 4-3. [직접] 결과 검토
- citation-checker: 스크립트 리포트 ↔ 에이전트 정리본 1:1 대응 확인.
- draft-reviewer: 지적의 타당성, 특히 이론 정합성 지적이 COR/JD-R 이해에
  기반했는지. **틀린 지적은 사례를 그대로 인용해** "이 지적은 ~라서 부적절,
  이런 오판을 막는 기준을 에이전트 지침에 추가해줘"로 피드백.
- 통과면 [프롬프트]:
```
Phase 4 변경사항 git commit ("Phase 4: draft-reviewer 신규,
citation-checker 하이브리드") 후 Phase 5 진행해줘.
```

---

## Phase 5 — writing-analyzer 마이그레이션 + 오케스트레이터 정비

### 5-1. [프롬프트] 시작

```
PRD Phase 5 진행해줘.

[writing-analyzer]
1. 기존 3개 모드를 /coach-writing 커맨드 인자로 통합:
   --analyze(1:1 비교) / --multi(good_papers 종합) / --revise(문단 수정).
2. revise 모드는 기존 multi_coaching_*.md 산출물을 기준 파일로 재사용하는
   2단계 구조 유지. 기준 파일이 없으면 --multi 먼저 실행하라고 안내.
3. good_papers 폴더 경로는 config.py 설정 따름.

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

### 5-4. [프롬프트] 사용 가이드 README 생성 (마이그레이션 최종 산출물)

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

> [직접] 받은 README를 한 번 통독하면서 실제와 다른 부분(특히 산출물
> 경로, 커맨드 인자)이 있는지 확인 — 이 문서가 앞으로의 매뉴얼이 됨.

---

## 공통 규칙

- Claude Code가 "내 확인" 단계를 건너뛰고 진행하면 → Esc 중단 후
  "방금 단계 보고부터 보여줘"
- 기존 산출물(*_요약.md, *_갭분석.md, history JSON) 덮어쓰기 발견 →
  즉시 중단, "git status로 변경 확인하고 의도하지 않은 변경 되돌려줘"
- 새 서브에이전트 인식 안 됨 → /exit 후 claude --continue 재시작
- 검증 보고는 항상 "평가·결론 없이 기계적으로" 요구 — 판단은 서현이가
