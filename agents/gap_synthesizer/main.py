"""
main.py — 갭 분석 결과 종합 → 연구 모형 제안

사용법:
  python main.py --pick              # 갭분석 파일 선택
  python main.py --folder "폴더명"   # 특정 폴더의 갭분석 전체
  python main.py --all               # 전체 갭분석 종합
"""

import argparse
import textwrap

from agents.gap_synthesizer.reader import find_gap_analyses, load_selected
from agents.gap_synthesizer.synthesizer import synthesize
from agents.gap_synthesizer.markdown_gen import generate_markdown

MAX_PAPERS_WARNING = 15


def _warn_if_large(n: int):
    if n > MAX_PAPERS_WARNING:
        print(f"\n⚠️  선택된 논문 수가 {n}편입니다. 토큰 비용이 높을 수 있어요.")
        confirm = input("계속할까요? (y/n): ").strip().lower()
        if confirm != "y":
            print("취소됨")
            return False
    return True


def run_pick():
    all_items = find_gap_analyses()

    if not all_items:
        print("❌ 갭분석 완료된 논문이 없습니다. 먼저 gap_explorer를 실행하세요.")
        return

    print("=" * 60)
    print("🔍 갭 종합 분석 — 논문 선택")
    print("=" * 60)

    # 폴더별로 그룹화
    from collections import defaultdict
    by_folder = defaultdict(list)
    for item in all_items:
        by_folder[item["folder"]].append(item)

    folders = list(by_folder.keys())
    print("\n[폴더 선택]")
    for i, folder in enumerate(folders, 1):
        print(f"  {i:2d}. {folder}  ({len(by_folder[folder])}편)")

    print("\n폴더 번호 입력 (예: 1 / 1,3 / all)")
    folder_choice = input("선택: ").strip().lower()

    if folder_choice == "all":
        selected_folders = folders
    else:
        try:
            indices = [int(x.strip()) - 1 for x in folder_choice.split(",")]
            selected_folders = [folders[i] for i in indices]
        except (ValueError, IndexError):
            print("❌ 잘못된 입력")
            return

    # 선택된 폴더의 논문 목록 표시
    candidates = []
    for folder in selected_folders:
        candidates.extend(by_folder[folder])

    print(f"\n[선택된 논문 — {len(candidates)}편]")
    for i, item in enumerate(candidates, 1):
        print(f"  {i:3d}. [{item['folder']}] {item['name']}")

    print("\n번호 입력 (예: 1 / 1,3,5 / all)")
    choice = input("선택: ").strip().lower()

    if choice == "all":
        selected = candidates
    else:
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(",")]
            selected = [candidates[i] for i in indices]
        except (ValueError, IndexError):
            print("❌ 잘못된 입력")
            return

    if not selected:
        print("❌ 선택된 논문 없음")
        return

    if not _warn_if_large(len(selected)):
        return

    _run_synthesis(selected)


def run_folder(folder_name: str):
    all_items = find_gap_analyses()
    selected = [item for item in all_items if item["folder"] == folder_name]

    if not selected:
        print(f"❌ '{folder_name}' 폴더에 갭분석 완료된 논문이 없습니다.")
        return

    print(f"📁 {folder_name}: {len(selected)}편 종합 분석")

    if not _warn_if_large(len(selected)):
        return

    _run_synthesis(selected)


def run_all():
    all_items = find_gap_analyses()

    if not all_items:
        print("❌ 갭분석 완료된 논문이 없습니다.")
        return

    print(f"📚 전체 {len(all_items)}편 종합 분석")

    if not _warn_if_large(len(all_items)):
        return

    _run_synthesis(all_items)


def _run_synthesis(items: list):
    print(f"\n{len(items)}편 로드 중...")
    papers = load_selected(items)

    result = synthesize(papers)
    if not result:
        print("❌ 종합 분석 실패")
        return

    paper_names = [p["name"] for p in papers]
    generate_markdown(result, paper_names)
    print("✅ 완료!")


def main():
    parser = argparse.ArgumentParser(
        description="갭 분석 결과 종합 → 연구 모형 제안",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            예시:
              python main.py --pick
              python main.py --folder "COR"
              python main.py --all
        """)
    )
    parser.add_argument("--pick",   action="store_true", help="갭분석 파일 선택")
    parser.add_argument("--folder", type=str, metavar="폴더명", help="특정 폴더 전체")
    parser.add_argument("--all",    action="store_true", help="전체 갭분석 종합")

    args = parser.parse_args()

    if   args.pick:   run_pick()
    elif args.folder: run_folder(args.folder)
    elif args.all:    run_all()
    else:             parser.print_help()


if __name__ == "__main__":
    main()
