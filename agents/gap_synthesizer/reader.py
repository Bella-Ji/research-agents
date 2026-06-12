"""
reader.py — _갭분석.md 파일 탐색 및 로드
"""

from pathlib import Path

from config import REFERENCE_ROOT, GAP_TARGET_FOLDERS as TARGET_FOLDERS

MAX_CHARS_PER_PAPER = 2500


def find_gap_analyses() -> list[dict]:
    """TARGET_FOLDERS 전체에서 _갭분석.md 파일 목록 반환."""
    results = []
    for folder_name in TARGET_FOLDERS:
        folder = REFERENCE_ROOT / folder_name
        if not folder.exists():
            continue
        for md_path in sorted(folder.rglob("*_갭분석.md")):
            results.append({
                "path": md_path,
                "name": md_path.stem.replace("_갭분석", ""),
                "folder": folder_name,
            })
    return results


def load_selected(items: list[dict]) -> list[dict]:
    """선택된 갭분석 파일들을 읽어서 내용 반환. 파일당 MAX_CHARS_PER_PAPER 글자로 제한."""
    loaded = []
    for item in items:
        path: Path = item["path"]
        try:
            content = path.read_text(encoding="utf-8")
            truncated = content[:MAX_CHARS_PER_PAPER]
            if len(content) > MAX_CHARS_PER_PAPER:
                truncated += "\n...(이하 생략)"
            loaded.append({
                "name": item["name"],
                "folder": item["folder"],
                "content": truncated,
            })
        except Exception as e:
            print(f"  [오류] 파일 읽기 실패 {path.name}: {e}")
    return loaded
