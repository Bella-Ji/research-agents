---
description: 저널 피어리뷰 수준으로 논문 전체를 평가한다. 2-Pass — Pass 1(컨텍스트 수립) → 사용자 승인 → Pass 2(5축 상세 리뷰)
argument-hint: "[논문 파일 경로] [모드: dissertation|journal-article (선택)] [Pass 번호 (선택, 기본 1)]"
---

논문 전체를 피어리뷰어 관점으로 평가하고 5축(기여도·방법-결과 정합성·과대해석·대안 설명·한계 충분성) 보고서를 생성한다.
원본 논문 파일은 수정하지 않는다.

## 인자

`$ARGUMENTS`

- 첫 번째 인자: 논문 MD 파일 절대경로 (dissertation의 경우 특정 연구만 리뷰하려면 "연구2" 등 범위 함께 전달)
- 두 번째 인자 (선택): 모드 — `dissertation` 또는 `journal-article`
- 세 번째 인자 (선택): Pass 번호 — `1`(기본) 또는 `2`

인자가 없으면 사용자에게 논문 파일 경로를 확인한다.

## 사전 확인

1. **모드**: 인자에 없고, 논문 폴더의 STRUCTURE.md frontmatter에도 `mode`가 없으면 사용자에게 먼저 확인한다. 폴더명으로 추측하지 않는다.
2. **vault 준비 상태**: 축 1(기여도) 판단에는 기존 vault 산출물(`*_요약.md`, `*_갭분석.md`, `gap_landscape_*.md`)이 필요하다. 논문 주제 관련 산출물이 부족해 보이면 `/find-gaps`·`/search-lit`을 먼저 돌리도록 사용자에게 안내한다 (peer-reviewer는 기존 파일만 참조하고 실시간 재검색을 하지 않음).

## 실행

### Pass 1 — 컨텍스트 수립 (Pass 번호 미지정 또는 1)

1. **peer-reviewer 서브에이전트를 호출한다** (`subagent_type: peer-reviewer`).
   프롬프트에 논문 파일 경로, 모드, 범위(있으면), `Pass 1`을 명시해 전달한다.
2. 에이전트가 생성한 `peer-review-context.md`의 **전체 내용을 사용자에게 그대로 보여준다.**
3. **여기서 반드시 멈춘다.** 사용자의 명시적 승인 없이 Pass 2를 자동 실행하지 않는다.
   승인 시 사용자에게 `/peer-review "[경로]" [모드] 2` 재실행 또는 "승인, Pass 2 진행" 응답을 안내한다.

### Pass 2 — 5축 상세 리뷰 (Pass 번호 2, 또는 사용자가 Pass 1 결과를 승인한 직후)

1. 논문 폴더에 `peer-review-context.md`가 있는지 확인한다. 없으면 Pass 1부터 시작하도록 안내하고 중단한다.
2. **peer-reviewer 서브에이전트를 호출한다** (`subagent_type: peer-reviewer`).
   프롬프트에 논문 파일 경로, 모드, `Pass 2`, `peer-review-context.md` 절대경로를 전달한다.

## 완료 보고

- Pass 1: peer-review-context.md 경로 + 전체 내용 + 승인 대기 안내
- Pass 2: 피어리뷰 보고서(`*_peerreview_YYYYMMDD.md`) 경로 + 축별 지적 수·심각도 요약 표
