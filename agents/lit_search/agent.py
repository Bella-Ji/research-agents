"""
Obsidian Vault 기반 문헌 탐색 에이전트
사용법: python lit_search_agent.py
"""

import os
import re
import anthropic
from pathlib import Path
from dotenv import load_dotenv

# .env에서 API 키 로드 (research-agents 루트 기준)
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# ─────────────────────────────────────────
# 설정
# ─────────────────────────────────────────
VAULT_ROOT = Path(r"C:/Users/user/Documents/00.seohyun/Doctor/0. 졸업논문 준비/02. reference")
API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=API_KEY)


# ─────────────────────────────────────────
# 1단계: MD 파일 파싱
# ─────────────────────────────────────────
def parse_md_file(filepath: Path) -> dict:
    """요약 MD 파일에서 frontmatter + 본문 파싱"""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception:
        return {}

    result = {
        "filepath": str(filepath),
        "filename": filepath.name,
        "title": "",
        "author": "",
        "year": "",
        "journal": "",
        "tags": [],
        "type": "",
        "source_folder": "",
        "summary_kr": "",  # 한줄 요약
        "abstract": "",
    }

    # frontmatter 파싱 (--- 블록 또는 속성 형식)
    # Obsidian properties 형식: `title: ...`
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("title:"):
            result["title"] = line.replace("title:", "").strip()
        elif line.startswith("author:"):
            result["author"] = line.replace("author:", "").strip()
        elif line.startswith("year:"):
            result["year"] = line.replace("year:", "").strip()
        elif line.startswith("journal:"):
            result["journal"] = line.replace("journal:", "").strip()
        elif line.startswith("tags:"):
            tags_raw = line.replace("tags:", "").strip()
            # "tag1 × tag2 ×" 또는 "tag1, tag2" 형식 처리
            tags = re.split(r"[×,\s]+", tags_raw)
            result["tags"] = [t.strip().lower() for t in tags if t.strip()]
        elif line.startswith("type:"):
            result["type"] = line.replace("type:", "").strip()
        elif line.startswith("source_folder:"):
            result["source_folder"] = line.replace("source_folder:", "").strip()

    # 한줄 요약 추출 (📌 한줄 요약 또는 ## 한줄 요약 섹션)
    summary_match = re.search(
        r"(?:📌\s*한줄 요약|##\s*한줄 요약)\s*\n(.+?)(?:\n\n|\n#)", text, re.DOTALL
    )
    if summary_match:
        result["summary_kr"] = summary_match.group(1).strip()

    # 초록 추출
    abstract_match = re.search(
        r"(?:초록|Abstract|## Abstract)\s*\n(.+?)(?:\n\n|\n#)", text, re.DOTALL
    )
    if abstract_match:
        result["abstract"] = abstract_match.group(1).strip()[:500]  # 500자 제한

    return result


# ─────────────────────────────────────────
# 2단계: Vault 전체 스캔
# ─────────────────────────────────────────
def scan_vault(vault_root: Path) -> list[dict]:
    """vault의 모든 _요약.md 파일 로드"""
    papers = []
    md_files = list(vault_root.rglob("*_요약.md"))
    print(f"📚 총 {len(md_files)}개 요약 MD 발견")

    for f in md_files:
        parsed = parse_md_file(f)
        if parsed.get("title") or parsed.get("filename"):
            papers.append(parsed)

    return papers


# ─────────────────────────────────────────
# 3단계: 키워드 기반 검색
# ─────────────────────────────────────────
KEYWORD_MAP = {
    # 이론 관련
    "cor": ["cor-theory", "cor", "conservation", "resource-loss", "loss-spiral", "stress-spiral"],
    "jd-r": ["jd-r", "jd_r", "job demands", "job-demands", "id-r-model"],
    "burnout": ["burnout", "burn-out", "소진"],
    "loss spiral": ["loss-spiral", "stress-spiral", "resource-loss", "cor-theory"],

    # 변수 관련
    "emotional exhaustion": ["emotional-exhaustion", "exhaustion", "정서적 소진"],
    "work meaning": ["work-meaning", "meaningfulness", "meaning", "wami", "의미감"],
    "mistreatment": ["mistreatment", "workplace-mistreatment", "부당대우", "abusive"],
    "recovery": ["recovery", "detachment", "sonnentag", "회복"],

    # 조절효과
    "moderation": ["moderation", "moderating", "interaction", "조절"],
    "first stage": ["first-stage", "stage1", "moderation"],
    "second stage": ["second-stage", "stage2", "moderation"],
    "mediation": ["mediation", "mediating", "indirect", "매개"],

    # 방법론
    "dsem": ["dsem", "dynamic", "time-series"],
    "multilevel": ["multilevel", "mlm", "hierarchical", "diary", "esm"],
    "diary": ["diary", "esm", "daily", "일기"],
}


def keyword_search(papers: list[dict], query: str, top_n: int = 15) -> list[dict]:
    """쿼리 기반 관련 논문 필터링"""
    query_lower = query.lower()
    scored = []

    # 쿼리에서 검색 키워드 확장
    search_terms = set(query_lower.split())
    for key, synonyms in KEYWORD_MAP.items():
        if key in query_lower:
            search_terms.update(synonyms)

    for paper in papers:
        score = 0
        tags = paper.get("tags", [])
        title = paper.get("title", "").lower()
        summary = paper.get("summary_kr", "").lower()
        folder = paper.get("source_folder", "").lower()

        for term in search_terms:
            # 태그 매칭 (가중치 높음)
            if any(term in tag for tag in tags):
                score += 3
            # 제목 매칭
            if term in title:
                score += 2
            # 폴더명 매칭
            if term in folder:
                score += 2
            # 요약 매칭
            if term in summary:
                score += 1

        if score > 0:
            scored.append((score, paper))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[:top_n]]


# ─────────────────────────────────────────
# 4단계: Claude API로 합성
# ─────────────────────────────────────────
def synthesize_results(query: str, papers: list[dict]) -> str:
    """찾은 논문들을 Claude가 합성하여 논문 작업에 바로 쓸 수 있게 정리"""

    if not papers:
        return "❌ 관련 논문을 찾지 못했어요. 다른 키워드로 검색해보세요."

    # 논문 정보 텍스트 구성
    papers_text = ""
    for i, p in enumerate(papers, 1):
        papers_text += f"""
[{i}] {p.get('title', '제목 없음')}
- 저자/연도: {p.get('author', '')} ({p.get('year', '')})
- 저널: {p.get('journal', '')}
- 태그: {', '.join(p.get('tags', []))}
- 한줄 요약: {p.get('summary_kr', '')}
- 폴더: {p.get('source_folder', '')}
"""

    prompt = f"""당신은 직업건강심리학 전문 연구자입니다.
다음은 사용자의 검색 질문과 관련된 논문 목록입니다.

검색 질문: "{query}"

관련 논문 목록:
{papers_text}

다음 형식으로 답변해주세요:

1. **핵심 관련 논문** (상위 5편): 왜 이 논문이 관련 있는지 한 문장으로 설명
2. **논문에 활용 방법**: 이 논문들을 어떻게 인용/활용할 수 있는지 구체적 제안
3. **APA 7판 인용 형식**: 각 논문의 인용 형식 제시
4. **추가 탐색 제안**: vault에서 더 찾아볼 키워드나 폴더 제안

답변은 한국어로, 논문 수정에 바로 쓸 수 있도록 실용적으로 작성해주세요."""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


# ─────────────────────────────────────────
# 메인 실행
# ─────────────────────────────────────────
def main():
    print("=" * 60)
    print("📖 Obsidian Vault 문헌 탐색 에이전트")
    print("=" * 60)
    print(f"Vault 경로: {VAULT_ROOT}")
    print()

    # Vault 스캔
    print("🔍 Vault 스캔 중...")
    papers = scan_vault(VAULT_ROOT)
    print(f"✅ {len(papers)}개 논문 로드 완료\n")

    # 대화형 검색 루프
    while True:
        print("-" * 60)
        query = input("🔎 검색 질문 (종료: q): ").strip()

        if query.lower() in ("q", "quit", "exit", "종료"):
            print("👋 종료합니다.")
            break

        if not query:
            continue

        print(f"\n⚙️  '{query}' 검색 중...")
        matched = keyword_search(papers, query)
        print(f"📄 {len(matched)}개 관련 논문 발견 → Claude 합성 중...\n")

        result = synthesize_results(query, matched)
        print(result)
        print()


if __name__ == "__main__":
    main()
