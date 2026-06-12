"""
main.py — 갭 지형 지도 → 내 데이터로 채울 수 있는 연구 모형 제안

사용법:
  python main.py --latest    # 가장 최근 갭 지형 지도 사용
  python main.py --pick      # 갭 지형 지도 선택
  python main.py --all       # 전체 갭 지형 지도 종합
"""

import argparse
import textwrap

from agents.gap_strategist.reader import find_landscapes, load_landscapes
from agents.gap_strategist.strategist import strategize
from agents.gap_strategist.markdown_gen import generate_markdown


def run_latest():
    items = find_landscapes()
    if not items:
        print("❌ 갭 지형 지도가 없습니다. 먼저 gap_synthesizer를 실행하세요.")
        return
    selected = items[:1]
    print(f"  최신 지형 지도: {selected[0]['name']}")
    _run_strategy(selected)


def run_pick():
    items = find_landscapes()
    if not items:
        print("❌ 갭 지형 지도가 없습니다. 먼저 gap_synthesizer를 실행하세요.")
        return

    print("=" * 60)
    print("🗺️  갭 전략 분석 — 지형 지도 선택")
    print("=" * 60)
    for i, item in enumerate(items, 1):
        print(f"  {i:3d}. {item['name']}")

    print("\n번호 입력 (예: 1 / 1,3 / all)")
    choice = input("선택: ").strip().lower()

    if choice == "all":
        selected = items
    else:
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(",")]
            selected = [items[i] for i in indices]
        except (ValueError, IndexError):
            print("❌ 잘못된 입력")
            return

    _run_strategy(selected)


def run_all():
    items = find_landscapes()
    if not items:
        print("❌ 갭 지형 지도가 없습니다.")
        return
    print(f"📚 전체 {len(items)}개 갭 지형 지도 종합 분석")
    _run_strategy(items)


def _run_strategy(items: list):
    print(f"\n{len(items)}개 지형 지도 로드 중...")
    landscapes = load_landscapes(items)

    result = strategize(landscapes)
    if not result:
        print("❌ 전략 분석 실패")
        return

    landscape_names = [lp["name"] for lp in landscapes]
    generate_markdown(result, landscape_names)
    print("✅ 완료!")


def main():
    parser = argparse.ArgumentParser(
        description="갭 지형 지도 → 연구 모형 전략 제안",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            예시:
              python main.py --latest
              python main.py --pick
              python main.py --all
        """)
    )
    parser.add_argument("--latest", action="store_true", help="가장 최근 지형 지도 사용")
    parser.add_argument("--pick",   action="store_true", help="지형 지도 선택")
    parser.add_argument("--all",    action="store_true", help="전체 지형 지도 종합")

    args = parser.parse_args()

    if   args.latest: run_latest()
    elif args.pick:   run_pick()
    elif args.all:    run_all()
    else:             parser.print_help()


if __name__ == "__main__":
    main()
