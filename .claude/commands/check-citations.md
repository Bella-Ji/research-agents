---
description: APA 7판 인용 형식 검사 (인텍스트 + 참고문헌 목록)
argument-hint: "[파일|폴더 경로] [--ref reference.md 경로] [--save]"
---

APA 7판 인용 형식을 검사하고 심각도별로 정리된 수정안을 제시한다.

## 인자

`$ARGUMENTS`

- 첫 번째 인자: 검사할 MD 파일 또는 폴더 경로 (절대경로 또는 프로젝트 루트 기준 상대경로)
- `--ref [경로]`: 참고문헌 목록 MD (교차 검사 활성화)
- `--save`: 결과를 MD 파일로 저장

인자가 없으면 사용자에게 대상 경로를 확인한다.

## 실행

**citation-checker 서브에이전트를 호출한다** (`subagent_type: citation-checker`).
프롬프트에 인자 전체를 그대로 전달한다.

## 완료 보고

에이전트가 반환한 결과를 그대로 출력한다.
