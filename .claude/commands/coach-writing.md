---
description: 논문 글쓰기 방식(논리 구조)을 분석하고 초안 코칭 보고서를 생성한다
argument-hint: "--analyze 'PDF경로' | --multi [섹션키] | --revise 섹션키"
---

논문의 논리 전개 방식(how)을 분석하여 내 초안 글쓰기를 코칭한다.
내용(what)이 아닌 논리 구조에 집중한다.

## 인자

`$ARGUMENTS`

모드 3가지 중 하나:
- `--analyze "PDF경로"` — PDF 1편의 논리 패턴을 내 초안과 1:1 비교
  - `--sections 섹션키...` (선택): 비교할 섹션. 생략 시 전체
- `--multi [섹션키]` — good_papers/ 폴더 전체 논문의 공통 패턴 종합 코칭
  - 섹션키 생략 시 초안 전체 섹션 처리
- `--revise 섹션키` — revise_input.md의 문단 진단 + 수정안
  - multi_coaching_{섹션키}.md가 있으면 기준으로 활용

인자가 없으면 사용자에게 모드와 인자를 확인한다.

## 실행

**coach-writing 서브에이전트를 호출한다** (`subagent_type: coach-writing`).
프롬프트에 인자 전체를 그대로 전달한다.

## 완료 보고

에이전트가 생성한 보고서 파일 경로를 출력한다.
