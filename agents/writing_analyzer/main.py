"""
main.py — 글쓰기 분석 에이전트 실행 파일

사용법:
  python run.py writing --analyze "경로/논문.pdf"
  python run.py writing --analyze "경로/논문.pdf" --sections introduction method discussion
  python run.py writing --analyze-multi --sections theoretical_implications
"""

import argparse
import sys
import textwrap
from pathlib import Path

from config import DRAFT_DIR, CURRENT_PAPER, WRITING_ANALYSIS_DIR
from agents.pdf_summarizer.extractor import extract_one
from agents.writing_analyzer.draft_reader import (
    read_draft_sections,
    list_available_sections,
    SECTION_MAP,
    SECTION_DISPLAY,
)
from agents.writing_analyzer.analyzer import analyze_paper, analyze_multi_papers, revise_paragraph
from agents.writing_analyzer.report_gen import generate_report, generate_multi_report, generate_revision_report


def _validate_config() -> bool:
    if not DRAFT_DIR or not DRAFT_DIR.exists():
        print(f"❌ DRAFT_DIR 경로가 없거나 설정되지 않았습니다: '{DRAFT_DIR}'")
        print("   .env 파일에 DRAFT_DIR=경로 를 추가해주세요.")
        return False
    if not CURRENT_PAPER:
        print("❌ CURRENT_PAPER가 설정되지 않았습니다.")
        print("   .env 파일에 CURRENT_PAPER=논문이름 을 추가해주세요.")
        return False
    return True


def run_analyze(pdf_path_str: str, section_keys: list[str] | None = None):
    """PDF 논문 글쓰기 분석 실행."""

    if not _validate_config():
        return

    pdf_path = Path(pdf_path_str)
    if not pdf_path.exists():
        print(f"❌ 파일 없음: {pdf_path_str}")
        return

    print("=" * 60)
    print("✍️  글쓰기 분석 모드")
    print(f"분석 논문: {pdf_path.name}")
    print(f"비교 초안: {CURRENT_PAPER}")
    print(f"결과 저장: {WRITING_ANALYSIS_DIR / CURRENT_PAPER}")
    print("=" * 60)

    # 1. PDF 텍스트 추출
    print("\n📄 PDF 텍스트 추출 중...")
    try:
        paper = extract_one(pdf_path)
    except Exception as e:
        print(f"❌ PDF 추출 실패: {e}")
        return

    if not paper.get("full_text"):
        print("❌ 텍스트를 추출할 수 없습니다 (스캔 PDF이거나 손상된 파일).")
        return

    # 2. Draft 섹션 읽기
    print("📂 초안 섹션 읽는 중...")
    available = list_available_sections(DRAFT_DIR)
    if not available:
        print(f"❌ Draft 폴더에서 읽을 수 있는 섹션이 없습니다: {DRAFT_DIR}")
        return

    # 섹션 키 검증
    if section_keys:
        invalid = [k for k in section_keys if k not in SECTION_MAP]
        if invalid:
            print(f"❌ 알 수 없는 섹션: {', '.join(invalid)}")
            print(f"   사용 가능: {', '.join(SECTION_MAP.keys())}")
            return
        # 요청 섹션 중 실제로 draft에 있는 것만
        target_keys = [k for k in section_keys if k in available]
        missing = [k for k in section_keys if k not in available]
        if missing:
            print(f"  ⚠️  draft에 없는 섹션 건너뜀: {', '.join(missing)}")
    else:
        target_keys = available

    draft_sections = read_draft_sections(DRAFT_DIR, target_keys)
    print(f"  → 분석할 섹션: {', '.join(SECTION_DISPLAY.get(k, k) for k in draft_sections)}")

    # 3. Claude 분석
    print("\n🤖 Claude 글쓰기 분석 중...")
    section_analyses = analyze_paper(paper["full_text"], draft_sections)

    if not section_analyses:
        print("❌ 분석에 실패했습니다.")
        return

    # 4. MD 보고서 생성
    print("\n📝 보고서 생성 중...")
    result = generate_report(paper, section_analyses, WRITING_ANALYSIS_DIR, CURRENT_PAPER)

    if result:
        print(f"\n✅ 완료! → {result}")
    else:
        print("\n❌ 보고서 생성 실패")


def run_revise(section_key: str):
    """revise_input.md의 문단을 읽어 수정 제안 생성."""

    if not _validate_config():
        return

    if section_key not in SECTION_MAP:
        print(f"❌ 알 수 없는 섹션: {section_key}")
        print(f"   사용 가능: {', '.join(SECTION_MAP.keys())}")
        return

    input_path = WRITING_ANALYSIS_DIR / CURRENT_PAPER / "revise_input.md"
    if not input_path.exists():
        print(f"❌ 입력 파일 없음: {input_path}")
        print("   revise_input.md 파일에 수정할 문단을 붙여넣고 다시 실행하세요.")
        return

    paragraph = input_path.read_text(encoding="utf-8").strip()
    if not paragraph or paragraph.startswith("<!--"):
        print("❌ revise_input.md가 비어 있습니다. 수정할 문단을 붙여넣어 주세요.")
        return

    # 기존 코칭 보고서 로드 (있으면 참고)
    coaching_path = WRITING_ANALYSIS_DIR / CURRENT_PAPER / f"multi_coaching_{section_key}.md"
    coaching_context = None
    if coaching_path.exists():
        coaching_context = coaching_path.read_text(encoding="utf-8")
        print(f"  📎 코칭 기준 로드: multi_coaching_{section_key}.md")
    else:
        print(f"  ℹ️  코칭 보고서 없음 — 섹션 맥락만으로 분석")

    section_display = SECTION_DISPLAY.get(section_key, section_key)
    print("=" * 60)
    print("✏️  문단 수정 제안 모드")
    print(f"섹션: {section_display}")
    print(f"비교 초안: {CURRENT_PAPER}")
    print("=" * 60)

    print("\n🤖 Claude 분석 중...")
    revision = revise_paragraph(paragraph, section_key, coaching_context)

    if not revision:
        print("❌ 수정 제안 생성 실패")
        return

    print("\n📝 결과 저장 중...")
    result = generate_revision_report(
        revision, section_key, paragraph, WRITING_ANALYSIS_DIR, CURRENT_PAPER
    )

    if result:
        print(f"\n✅ 완료! → {result}")
    else:
        print("\n❌ 보고서 저장 실패")


def run_analyze_multi(section_keys: list[str] | None = None):
    """good_papers/ 폴더의 논문들을 종합 분석하여 코칭 보고서 생성."""

    if not _validate_config():
        return

    good_papers_dir = WRITING_ANALYSIS_DIR / CURRENT_PAPER / "good_papers"
    if not good_papers_dir.exists():
        print(f"❌ good_papers 폴더 없음: {good_papers_dir}")
        return

    pdfs = sorted(good_papers_dir.glob("*.pdf"))
    if not pdfs:
        print(f"❌ good_papers 폴더에 PDF가 없습니다: {good_papers_dir}")
        return

    # 섹션 결정
    available = list_available_sections(DRAFT_DIR)
    if section_keys:
        invalid = [k for k in section_keys if k not in SECTION_MAP]
        if invalid:
            print(f"❌ 알 수 없는 섹션: {', '.join(invalid)}")
            print(f"   사용 가능: {', '.join(SECTION_MAP.keys())}")
            return
        target_keys = [k for k in section_keys if k in available]
        missing = [k for k in section_keys if k not in available]
        if missing:
            print(f"  ⚠️  draft에 없는 섹션 건너뜀: {', '.join(missing)}")
    else:
        target_keys = available

    if not target_keys:
        print("❌ 분석할 섹션이 없습니다.")
        return

    print("=" * 60)
    print("📚 멀티 논문 종합 코칭 모드")
    print(f"논문 수: {len(pdfs)}편")
    print(f"분석 섹션: {', '.join(SECTION_DISPLAY.get(k, k) for k in target_keys)}")
    print(f"비교 초안: {CURRENT_PAPER}")
    print(f"결과 저장: {WRITING_ANALYSIS_DIR / CURRENT_PAPER}")
    print("=" * 60)

    # PDF 텍스트 일괄 추출
    print("\n📄 PDF 텍스트 추출 중...")
    paper_texts: dict[str, str] = {}
    for pdf in pdfs:
        try:
            paper = extract_one(pdf)
            if paper.get("full_text"):
                paper_texts[pdf.name] = paper["full_text"]
                print(f"  ✅ {pdf.name[:50]}")
            else:
                print(f"  ⚠️  텍스트 없음 — 건너뜀: {pdf.name}")
        except Exception as e:
            print(f"  ❌ 추출 실패: {pdf.name} ({e})")

    if not paper_texts:
        print("❌ 텍스트 추출에 성공한 논문이 없습니다.")
        return

    # 섹션별 종합 코칭
    for section_key in target_keys:
        draft_sections = read_draft_sections(DRAFT_DIR, [section_key])
        if not draft_sections:
            print(f"\n⚠️  {SECTION_DISPLAY.get(section_key)} — draft 내용 없음, 건너뜀")
            continue

        my_draft = draft_sections[section_key]
        print(f"\n🤖 [{SECTION_DISPLAY.get(section_key, section_key)}] 종합 코칭 시작...")

        coaching = analyze_multi_papers(paper_texts, section_key, my_draft)

        if coaching:
            print("\n📝 코칭 보고서 생성 중...")
            result = generate_multi_report(
                coaching, section_key, WRITING_ANALYSIS_DIR, CURRENT_PAPER
            )
            if result:
                print(f"✅ 완료! → {result}")
        else:
            print(f"❌ {SECTION_DISPLAY.get(section_key)} 코칭 실패")


def main():
    parser = argparse.ArgumentParser(
        description="논문 글쓰기 방식 분석기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            예시:
              python run.py writing --analyze "C:/경로/논문.pdf"
              python run.py writing --analyze "C:/경로/논문.pdf" --sections introduction method discussion
              python run.py writing --analyze-multi --sections theoretical_implications

            사용 가능한 섹션 키:
              abstract, introduction, theoretical_background, method, results,
              discussion, theoretical_implications, practical_implications,
              limitations, conclusions
        """)
    )
    parser.add_argument(
        "--analyze", type=str, metavar="경로",
        help="논문 1편 분석: PDF 경로 지정",
    )
    parser.add_argument(
        "--analyze-multi", action="store_true",
        help="good_papers/ 폴더의 논문들 종합 코칭",
    )
    parser.add_argument(
        "--revise", type=str, metavar="섹션",
        help="revise_input.md의 문단 수정 제안 (섹션 키 필수, 예: theoretical_implications)",
    )
    parser.add_argument(
        "--sections", nargs="+", metavar="섹션",
        help="분석할 섹션 키 (미지정시 draft에 있는 전체 섹션)",
    )

    args = parser.parse_args()

    if args.analyze:
        run_analyze(args.analyze, args.sections)
    elif args.analyze_multi:
        run_analyze_multi(args.sections)
    elif args.revise:
        run_revise(args.revise)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
