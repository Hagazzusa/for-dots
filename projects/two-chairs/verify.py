#!/usr/bin/env python3
"""원문·TXT·PDF의 글자 일치, 글꼴 내장, 경계·겹침·쪽 번호를 읽기 전용 검사한다.

PDF의 행갈이와 공백 폭은 원문 TXT의 줄바꿈과 다르므로, 본문 글자열은 모든
공백을 제외한 뒤 순서까지 비교한다. 공백과 줄바꿈의 원본 보존은 TXT의 바이트
일치로 별도 확인한다. 자동 검사는 모든 쪽의 렌더 이미지 육안 검토를 대신하지 않는다.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re

import pdfplumber
from pypdf import PdfReader

import sys
sys.dont_write_bytecode = True

from build_pdf import (
    BOTTOM_MARGIN, ENDING_SENTENCE, LEFT_MARGIN, PAGE_HEIGHT, PAGE_WIDTH,
    RIGHT_MARGIN, ROOT, STEM, SUBTITLE, TITLE, read_source,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def visible(text: str) -> str:
    return re.sub(r"\s+", "", text)


def check_fonts(reader: PdfReader) -> int:
    checked = set()
    for page in reader.pages:
        fonts = page["/Resources"].get("/Font", {}).get_object()
        for reference in fonts.values():
            font = reference.get_object()
            name = str(font.get("/BaseFont", ""))
            # ReportLab은 쓰지 않은 기본 Helvetica 자원을 함께 선언할 수 있다.
            if "TwoChairsNotoSerifKR" not in name:
                continue
            descriptor = font.get("/FontDescriptor")
            require(descriptor is not None, "사용 글꼴의 기술 정보가 없습니다.")
            descriptor = descriptor.get_object()
            require(any(key in descriptor for key in ("/FontFile", "/FontFile2", "/FontFile3")), "사용 글꼴이 PDF에 내장되지 않았습니다.")
            require("/ToUnicode" in font, "한글 텍스트 추출용 문자 대응표가 없습니다.")
            checked.add(name)
    require(bool(checked), "Noto Serif KR 내장 글꼴을 찾지 못했습니다.")
    return len(checked)


def verify(source_path: Path, output_root: Path, min_pages: int, max_pages: int) -> dict:
    raw, _ = read_source(source_path)
    source = raw.decode("utf-8")
    pdf_path = output_root / "pdf" / f"{STEM}.pdf"
    text_path = output_root / "text" / f"{STEM}.txt"
    require(text_path.read_bytes() == raw, "배포용 TXT 바이트가 편집 원문과 다릅니다.")
    reader = PdfReader(pdf_path)
    require(reader.metadata.author == "닷돌이", "PDF 저자 메타데이터가 다릅니다.")
    require(reader.metadata.title == TITLE, "PDF 제목 메타데이터가 다릅니다.")
    require(reader.metadata.subject == SUBTITLE, "PDF 부제 메타데이터가 다릅니다.")
    font_count = check_fonts(reader)
    fragments, page_details, row_positions = [], [], []
    with pdfplumber.open(pdf_path) as document:
        require(min_pages <= len(document.pages) <= max_pages, f"쪽 수 {len(document.pages)}: 지정 범위 {min_pages}~{max_pages}쪽 밖입니다.")
        for page_number, page in enumerate(document.pages, 1):
            require((page.width, page.height) == (PAGE_WIDTH, PAGE_HEIGHT), f"{page_number}쪽 크기가 다릅니다.")
            footer = [c for c in page.chars if c["top"] > PAGE_HEIGHT - 38]
            content = [c for c in page.chars if c not in footer]
            require("".join(c["text"] for c in footer) == str(page_number), f"{page_number}쪽 번호가 없거나 다른 글자가 푸터에 있습니다.")
            require(bool(content), f"{page_number}쪽 본문이 비었습니다.")
            for char in footer:
                require(abs((char["bottom"] - char["top"]) - 8) < 0.1, "쪽 번호의 글자 크기가 다릅니다.")
                require(PAGE_WIDTH / 2 - 14 <= char["x0"] <= char["x1"] <= PAGE_WIDTH / 2 + 14, "쪽 번호가 중앙을 벗어났습니다.")
            rows = defaultdict(list)
            for char in content:
                glyph = char["text"]
                require(glyph not in ("\ufffd", "\x00") and not glyph.startswith("(cid:"), f"{page_number}쪽에 해석할 수 없는 글자가 있습니다.")
                require("TwoChairsNotoSerifKR" in char["fontname"], f"{page_number}쪽에서 예상하지 않은 글꼴을 사용했습니다.")
                require(LEFT_MARGIN - 0.5 <= char["x0"] <= char["x1"] <= PAGE_WIDTH - RIGHT_MARGIN + 0.5, f"{page_number}쪽 글자 {glyph!r}가 좌우 경계를 벗어났습니다.")
                require(30 <= char["top"] < char["bottom"] <= PAGE_HEIGHT - BOTTOM_MARGIN + 1, f"{page_number}쪽 글자 {glyph!r}가 위아래 경계를 벗어났습니다.")
                color = char.get("non_stroking_color")
                require(color in (0, (0,), (0, 0, 0)), f"{page_number}쪽에 검정 이외의 글자가 있습니다.")
                rows[round(char["top"], 2)].append(char)
            previous_bottom = None
            for top, chars in sorted(rows.items()):
                if previous_bottom is not None:
                    require(top >= previous_bottom - 0.1, f"{page_number}쪽에서 두 행의 글자 경계가 겹칩니다.")
                chars.sort(key=lambda c: c["x0"])
                previous_x = None
                for char in chars:
                    if previous_x is not None:
                        require(char["x0"] >= previous_x - 0.1, f"{page_number}쪽에서 이웃한 글자가 겹칩니다.")
                    previous_x = char["x1"]
                previous_bottom = max(c["bottom"] for c in chars)
                row_text = "".join(c["text"] for c in chars)
                fragments.append(row_text)
                row_positions.append({"page": page_number, "top": top, "text": visible(row_text)})
            page_details.append({"쪽": page_number, "행": len(rows), "글자": len(content)})
    actual, expected = visible("".join(fragments)), visible(source)
    if actual != expected:
        mismatch = next((i for i, (a, b) in enumerate(zip(actual, expected)) if a != b), min(len(actual), len(expected)))
        raise ValueError(f"PDF와 원문의 글자열이 다릅니다. 첫 차이 위치 {mismatch}: PDF {actual[mismatch:mismatch + 20]!r}, 원문 {expected[mismatch:mismatch + 20]!r}")
    # 원문의 각 문단을 PDF 행에 대응시켜 쪽 사이에 한 행만 남지 않는지 확인한다.
    paragraph_breaks = []
    offset = 0
    rows = []
    for row in row_positions:
        rows.append((offset, offset + len(row["text"]), row))
        offset += len(row["text"])
    offset = 0
    for paragraph in source.splitlines():
        if not paragraph:
            continue
        finish = offset + len(visible(paragraph))
        occupied = [row for start, end, row in rows if start < finish and end > offset]
        page_rows = defaultdict(int)
        for row in occupied:
            page_rows[row["page"]] += 1
        if len(page_rows) > 1:
            require(all(count >= 2 for count in page_rows.values()), f"문단이 쪽 경계에 한 행만 남겼습니다: {paragraph[:35]!r}")
            paragraph_breaks.append({"문단 첫머리": paragraph[:25], "쪽별 행": dict(page_rows)})
        offset = finish
    require(fragments[-1] == ENDING_SENTENCE, "마지막 문장이 한 행에 온전히 놓이지 않았습니다.")
    return {
        "제목": TITLE,
        "쪽 수": len(page_details),
        "쪽별 검사": page_details,
        "원문 SHA256": hashlib.sha256(raw).hexdigest(),
        "PDF SHA256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
        "TXT 원문 바이트 일치": True,
        "PDF 원문 글자열 일치": True,
        "글자 경계와 행 겹침 검사": True,
        "마지막 문장 한 행 유지": True,
        "문단 한 행 고립 없음": True,
        "나누어진 문단": paragraph_breaks,
        "내장 글꼴 수": font_count,
        "한계": "PDF 글자열 비교에서는 조판으로 바뀌는 공백·줄바꿈을 제외합니다. 최종 모든 쪽의 이미지 육안 검토는 별도입니다.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "story.txt", help="편집 원문 TXT")
    parser.add_argument("--output-root", type=Path, default=ROOT / "output", help="검사할 출력 폴더")
    parser.add_argument("--min-pages", type=int, default=3, help="최소 쪽 수")
    parser.add_argument("--max-pages", type=int, default=4, help="최대 쪽 수")
    parser.add_argument("--report", type=Path, help="명시한 JSON 경로에만 결과를 저장합니다. 생략하면 읽기 전용입니다.")
    args = parser.parse_args()
    result = verify(args.source, args.output_root, args.min_pages, args.max_pages)
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report is not None:
        args.report.write_text(serialized, encoding="utf-8")
    print(serialized, end="")


if __name__ == "__main__":
    main()
