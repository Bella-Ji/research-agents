---
description: 선배 논문 패턴 기반으로 학위논문 초기 골격을 생성한다
---

structure-architect 에이전트를 사용해 다음을 수행하라:
1. dissertation/STRUCTURE.md가 존재하면 읽고, 없으면 템플릿에서 생성한다.
2. 연구 개수는 묻지 않는다. research-profile.md와 STRUCTURE.md frontmatter(`studies`)를 따른다
   (현재 박사논문: WM 연구 단일 연구, 5장 체제).
3. 에이전트에 정의된 [구조 패턴]에 따라 서론 8단계, 이론적 배경, 연구방법, 연구결과, 논의를
   핵심 논점(claim) 수준까지 채운 전체 아웃라인을 STRUCTURE.md에 작성한다.
4. 결과를 Obsidian 호환 마크다운으로 요약 출력한다.

$ARGUMENTS
