#!/usr/bin/env python3
"""시조의 원문·TXT·PDF, 한 행 유지, 글꼴·글자 경계·겹침을 검사한다.

기본 실행은 읽기 전용이다. --report 경로를 명시한 경우에만 JSON을 쓴다.
PDF의 공백을 포함한 여섯 행을 원문과 저자명에 정확히 대응시킨다.
이 자동 검사는 렌더 이미지의 육안 검토나 실제 인쇄 검사를 대신하지 않는다.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys

import pdfplumber
from pypdf import PdfReader

sys.dont_write_bytecode = True

from build_pdf import (
    AUTHOR, AUTHOR_SIZE, BODY_SIZE, FONT_NAME, LEFT_MARGIN, PAGE_HEIGHT,
    PAGE_WIDTH, RIGHT_MARGIN, ROOT, STEM, SUBTITLE, SUBTITLE_SIZE,
    TITLE, TITLE_SIZE, read_source,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_fonts(reader: PdfReader) -> list[str]:
    checked = set()
    for page in reader.pages:
        for reference in page["/Resources"]["/Font"].get_object().values():
            font = reference.get_object()
            name = str(font.get("/BaseFont", ""))
            # ReportLab이 선언만 하는 기본 Helvetica는 실제 사용 검사에서 제외한다.
            if FONT_NAME not in name:
                continue
            require("/FontDescriptor" in font, "사용 글꼴의 기술 정보가 없습니다.")
            descriptor = font["/FontDescriptor"].get_object()
            keys = [key for key in ("/FontFile", "/FontFile2", "/FontFile3") if key in descriptor]
            require(bool(keys), "사용 글꼴이 PDF에 내장되지 않았습니다.")
            require(all(bool(descriptor[key].get_object().get_data()) for key in keys), "내장 글꼴 데이터가 비었습니다.")
            require("/ToUnicode" in font, "한글 문자 대응표가 없습니다.")
            require(bool(font["/ToUnicode"].get_object().get_data()), "한글 문자 대응표가 비었습니다.")
            checked.add(name)
    require(bool(checked), "Noto Serif KR 내장 글꼴을 찾지 못했습니다.")
    return sorted(checked)


def verify(source_path: Path, output_root: Path) -> dict:
    raw, lines = read_source(source_path)
    pdf_path = output_root / "pdf" / f"{STEM}.pdf"
    text_path = output_root / "text" / f"{STEM}.txt"
    require(text_path.read_bytes() == raw, "배포용 TXT의 바이트가 원문과 다릅니다.")
    expected = [TITLE, SUBTITLE, *lines[3:], AUTHOR]
    expected_sizes = [TITLE_SIZE, SUBTITLE_SIZE, BODY_SIZE, BODY_SIZE, BODY_SIZE, AUTHOR_SIZE]
    reader = PdfReader(pdf_path)
    require(len(reader.pages) == 1, "PDF가 한 쪽이 아닙니다.")
    require(reader.metadata.author == AUTHOR, "저자 메타데이터가 다릅니다.")
    require(reader.metadata.title == TITLE, "제목 메타데이터가 다릅니다.")
    require(reader.metadata.subject == SUBTITLE, "부제 메타데이터가 다릅니다.")
    require((reader.pages[0].extract_text() or "").splitlines() == expected,
            "pypdf로 추출한 행과 원문의 순서 또는 공백이 다릅니다.")
    font_names = check_fonts(reader)
    with pdfplumber.open(pdf_path) as document:
        page = document.pages[0]
        require((page.width, page.height) == (PAGE_WIDTH, PAGE_HEIGHT), "쪽 크기가 다릅니다.")
        require(not (page.images or page.lines or page.rects or page.curves), "텍스트 이외의 장식이나 이미지가 있습니다.")
        rows = defaultdict(list)
        require(bool(page.chars), "PDF가 비었습니다.")
        for char in page.chars:
            glyph = char["text"]
            require(glyph not in ("\ufffd", "\x00") and not glyph.startswith("(cid:"), "해석할 수 없는 글자가 있습니다.")
            require(FONT_NAME in char["fontname"], "예상하지 않은 글꼴이 실제 사용되었습니다.")
            require(LEFT_MARGIN - 0.1 <= char["x0"] <= char["x1"] <= PAGE_WIDTH - RIGHT_MARGIN + 0.1,
                    f"글자 {glyph!r}가 좌우 경계를 벗어났습니다.")
            require(64 <= char["top"] < char["bottom"] <= PAGE_HEIGHT - 64,
                    f"글자 {glyph!r}가 위아래 경계를 벗어났습니다.")
            require(char.get("non_stroking_color") in (0, (0,), (0, 0, 0)), "검정 이외의 글자가 있습니다.")
            rows[round(char["top"], 3)].append(char)
        require(len(rows) == 6, "제목·부제·세 장·저자명이 여섯 행에 놓이지 않았습니다.")
        row_details, actual, previous_bottom = [], [], None
        for index, (top, chars) in enumerate(sorted(rows.items())):
            chars.sort(key=lambda char: char["x0"])
            require(abs(chars[0]["x0"] - LEFT_MARGIN) < 0.1, "행의 왼쪽 정렬이 다릅니다.")
            if previous_bottom is not None:
                require(top >= previous_bottom - 0.1, "두 행의 글자 경계가 겹칩니다.")
            for left, right in zip(chars, chars[1:]):
                require(right["x0"] >= left["x1"] - 0.1, "같은 행에서 이웃한 글자 경계가 겹칩니다.")
            require(all(abs(char["size"] - expected_sizes[index]) < 0.1 for char in chars), "행의 글자 크기가 다릅니다.")
            previous_bottom = max(char["bottom"] for char in chars)
            row_text = "".join(char["text"] for char in chars)
            actual.append(row_text)
            row_details.append({"행": index + 1, "내용": row_text, "글자 크기 pt": expected_sizes[index],
                                "경계 pt": [round(chars[0]["x0"], 3), top,
                                             round(chars[-1]["x1"], 3), round(previous_bottom, 3)]})
    require(actual == expected, "pdfplumber로 추출한 행과 원문의 순서 또는 공백이 다릅니다.")
    return {
        "제목": TITLE,
        "저자": AUTHOR,
        "쪽 수": 1,
        "쪽 크기 pt": [PAGE_WIDTH, PAGE_HEIGHT],
        "원문 SHA256": hashlib.sha256(raw).hexdigest(),
        "PDF SHA256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
        "TXT SHA256": hashlib.sha256(text_path.read_bytes()).hexdigest(),
        "TXT 원문 바이트 일치": True,
        "PDF 원문 행과 공백 및 순서 일치": True,
        "시조 세 장 각각 한 행 유지": True,
        "글자 경계와 행 겹침 검사": True,
        "검정 글자만 사용": True,
        "이미지와 테두리 및 장식 없음": True,
        "내장 글꼴": font_names,
        "행 검사": row_details,
        "한계": "글자 경계와 추출 텍스트의 자동 검사입니다. 렌더 이미지 육안 검토, 실제 인쇄물과 모든 뷰어의 표시는 별도 확인 범위입니다.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "poem.txt", help="편집 원문 TXT")
    parser.add_argument("--output-root", type=Path, default=ROOT / "output", help="검사할 출력 폴더")
    parser.add_argument("--report", type=Path, help="명시한 경로에만 JSON 결과를 저장합니다. 생략하면 읽기 전용입니다.")
    args = parser.parse_args()
    result = verify(args.source, args.output_root)
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.report is not None:
        args.report.write_text(serialized, encoding="utf-8")
    print(serialized, end="")


if __name__ == "__main__":
    main()
