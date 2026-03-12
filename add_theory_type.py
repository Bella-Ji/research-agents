"""
add_theory_type.py
요약 MD 파일에서 태그를 확인하고, 이론 관련 태그가 있으면 type: theory 속성 추가
"""

import os
import re
from pathlib import Path

# ── 설정 ──────────────────────────────────────────────────────────
REFERENCE_DIR = r"C:\Users\user\Documents\00.seohyun\Doctor\0. 졸업논문 준비\02. reference"

# 이론 관련 태그 키워드
THEORY_TAGS = [
    "cor-theory",
    "jd-r-model",
    "jd-r",
    "cor",
    "theory",
    "model",
    "theoretical-review",
    "conservation-of-resources",
    "demands-resources",
]

# ── 함수 ──────────────────────────────────────────────────────────

def has_theory_tag(content: str) -> bool:
    """태그 목록에 이론 관련 태그가 있는지 확인"""
    # tags: ["tag1", "tag2"] 형식 추출
    tag_match = re.search(r'"tags":\s*\[([^\]]*)\]', content)
    if tag_match:
        tags_str = tag_match.group(1).lower()
        for theory_tag in THEORY_TAGS:
            if theory_tag in tags_str:
                return True

    # YAML frontmatter tags: 형식도 확인
    yaml_match = re.search(r'^tags:\s*\[([^\]]*)\]', content, re.MULTILINE)
    if yaml_match:
        tags_str = yaml_match.group(1).lower()
        for theory_tag in THEORY_TAGS:
            if theory_tag in tags_str:
                return True

    return False


def already_has_type(content: str) -> bool:
    """이미 type: theory가 있는지 확인"""
    return "type: theory" in content or "type:theory" in content


def add_type_theory(filepath: Path) -> bool:
    """파일에 type: theory 속성 추가. 성공 시 True 반환"""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  [오류] 읽기 실패: {filepath.name} — {e}")
        return False

    if already_has_type(content):
        return False

    if not has_theory_tag(content):
        return False

    # YAML frontmatter가 있으면 그 안에 추가
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            new_content = content[:end] + "type: theory\n" + content[end:]
            filepath.write_text(new_content, encoding="utf-8")
            return True

    # frontmatter 없으면 맨 위에 추가
    new_content = "---\ntype: theory\n---\n\n" + content
    filepath.write_text(new_content, encoding="utf-8")
    return True


def main():
    ref_path = Path(REFERENCE_DIR)
    if not ref_path.exists():
        print(f"[오류] 경로를 찾을 수 없어요: {REFERENCE_DIR}")
        return

    md_files = list(ref_path.rglob("*_요약.md"))
    print(f"총 {len(md_files)}개 요약 MD 파일 검색 중...\n")

    updated = []
    skipped = 0

    for filepath in md_files:
        result = add_type_theory(filepath)
        if result:
            updated.append(filepath.name)
            print(f"  ✅ type: theory 추가 — {filepath.name}")
        else:
            skipped += 1

    print(f"\n완료!")
    print(f"  - type: theory 추가: {len(updated)}개")
    print(f"  - 스킵 (이론 태그 없음 또는 이미 있음): {skipped}개")


if __name__ == "__main__":
    main()
