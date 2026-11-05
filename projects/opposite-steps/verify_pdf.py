#!/usr/bin/env python3
"""PDF의 글자·내장 글꼴·보드 좌표·해설 상태·재현성을 검사한다.

python verify_pdf.py
python verify_pdf.py --output-root /tmp/opposite-steps-check/output
python verify_pdf.py --compare-root /tmp/opposite-steps-check/output

시각 검사를 대체하지 않는다. tmp/pdfs/의 모든 쪽 PNG를 별도로 확인한다.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

import pdfplumber
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
MM = 72/25.4


def normalize(text):
    return re.sub(r"\s+", "", text)


def scalar(color):
    return color[0] if isinstance(color, (tuple, list)) and len(color) == 1 else color


def inside(item, box, tolerance=.02):
    x0, y0, x1, y1 = box
    return (item["x0"] >= x0-tolerance and item["x1"] <= x1+tolerance
            and item["top"] >= y0-tolerance and item["bottom"] <= y1+tolerance)


def cell_index(item, box):
    x0, y0, x1, y1 = box
    cell = (x1-x0)/4
    cx = (item["x0"]+item["x1"])/2
    cy = (item["top"]+item["bottom"])/2
    col, row = int((cx-x0)/cell), int((cy-y0)/cell)
    assert 0 <= col < 4 and 0 <= row < 4
    assert abs(cx-(x0+(col+.5)*cell)) < .02
    assert abs(cy-(y0+(row+.5)*cell)) < .02
    return row*4+col


def inspect_board(page, board, puzzle, expected_state, layout):
    box = board["bbox"]
    assert board["state"] == expected_state
    assert board["goal"] == puzzle["goal"]
    assert board["walls"] == puzzle["walls"]
    expected_side = (layout["solution_board_mm"] if board["mini"] else 4*layout["problem_cell_mm"])*MM
    assert abs(box[2]-box[0]-expected_side) < .001
    assert abs(box[3]-box[1]-expected_side) < .001
    shapes = {"A": [i for i in page.curves if inside(i, box)],
              "B": [i for i in page.rects if inside(i, box)]}
    for token, objects in shapes.items():
        current = [i for i in objects if i["fill"] and scalar(i["non_stroking_color"]) == 0]
        goals = [i for i in objects if i["fill"] and scalar(i["non_stroking_color"]) == 1]
        assert len(current) == len(goals) == 1, (token, current, goals)
        index = "AB".index(token)
        assert cell_index(current[0], box) == expected_state[index]
        assert cell_index(goals[0], box) == puzzle["goal"][index]
        goal_gray = layout["gray"]["goal_in_solution"] if board["mini"] else 0
        assert scalar(goals[0]["stroking_color"]) == goal_gray
        # Each actual black shape contains the matching white label.
        letters = [ch for ch in page.chars if inside(ch, [current[0]["x0"],current[0]["top"],current[0]["x1"],current[0]["bottom"]])
                   and scalar(ch["non_stroking_color"]) == 1]
        assert [ch["text"] for ch in letters] == [token]
    walls = [i for i in shapes["B"] if i["fill"] and scalar(i["non_stroking_color"]) == layout["gray"]["wall"]]
    assert sorted(cell_index(i, box) for i in walls) == sorted(puzzle["walls"])
    return {"puzzle": puzzle["id"], "state": expected_state, "current_shapes": "circle A / square B", "walls": len(walls)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT/"output")
    parser.add_argument("--compare-root", type=Path)
    parser.add_argument("--report", type=Path, default=ROOT/"qa_layout.json")
    args = parser.parse_args()
    layout = json.loads((ROOT/"layout.json").read_text())
    puzzles = {v["id"]: v for v in json.loads((ROOT/"puzzles.json").read_text())["puzzles"]}
    solution_data = json.loads((ROOT/"solutions.json").read_text())
    solutions = {v["id"]: v for v in solution_data["solutions"]}
    manifest = json.loads((args.output_root/"layout_manifest.json").read_text())
    report = {"status": "passed", "checks": ["A4 page size", "two pages per file", "embedded Korean TrueType font and Unicode map",
               "all authored text recoverable", "all text and shapes inside 8mm safe boundary",
               "no unintended text overlap", "3 playable 80mm boards", "24 solution 42mm boards",
               "actual vector piece positions match source states", "actual walls and goals match source JSON",
               "every command label matches solution JSON"], "files": {}}
    for filename, page_count in layout["expected_pdf_pages"].items():
        path = args.output_root/"pdf"/filename
        reader = PdfReader(path)
        assert len(reader.pages) == page_count
        records = manifest["files"][filename]
        boards = [v for v in records if v["kind"] == "board"]
        is_solution = filename.endswith("Solutions.pdf")
        if is_solution:
            assert Counter(v["puzzle"] for v in boards) == {1:4, 2:8, 3:12}
        else:
            assert Counter(v["puzzle"] for v in boards) == {1:1, 2:1, 3:1}
        observed_states = Counter()
        pages = []
        with pdfplumber.open(path) as document:
            for number, page in enumerate(document.pages, 1):
                assert abs(page.width-210*MM) < .01 and abs(page.height-297*MM) < .01
                body = page.extract_text()
                (ROOT/"tmp"/"pdfs").mkdir(parents=True, exist_ok=True)
                (ROOT/"tmp"/"pdfs"/f"{path.stem}-{number}.txt").write_text(body+"\n", encoding="utf-8")
                assert "\ufffd" not in body and "\x00" not in body
                text = normalize(body)
                page_records = [v for v in records if v["page"] == number]
                page_boards = [v for v in page_records if v["kind"] == "board"]
                for item in page_records:
                    if item["kind"] == "text":
                        assert normalize(item["text"]) in text, (filename, number, item["text"])
                for obj in page.chars+page.rects+page.curves+page.lines:
                    assert inside(obj, [8*MM, 8*MM, page.width-8*MM, page.height-8*MM]), (filename, number, obj)
                outside_text = [v for v in page_records if v["kind"] == "text" and not any(
                    b["bbox"][0] <= v["bbox"][0] and v["bbox"][2] <= b["bbox"][2]
                    and b["bbox"][1] <= v["bbox"][1] and v["bbox"][3] <= b["bbox"][3] for b in page_boards)]
                for idx, a in enumerate(outside_text):
                    for b in outside_text[idx+1:]:
                        ax, ay, ar, ab = a["bbox"]
                        bx, by, br, bb = b["bbox"]
                        assert min(ar,br)-max(ax,bx) <= .1 or min(ab,bb)-max(ay,by) <= .1, (a,b)
                korean_fonts = []
                for font_ref in reader.pages[number-1]["/Resources"]["/Font"].values():
                    font = font_ref.get_object()
                    if "OppositeStepsNotoSerifKR" in str(font.get("/BaseFont")):
                        assert "/FontFile2" in font["/FontDescriptor"]
                        assert "/ToUnicode" in font
                        korean_fonts.append(str(font["/BaseFont"]))
                assert korean_fonts
                checked = []
                for board in page_boards:
                    pid = board["puzzle"]
                    step = observed_states[pid]
                    expected_state = solutions[pid]["states"][step] if is_solution else puzzles[pid]["start"]
                    checked.append(inspect_board(page, board, puzzles[pid], expected_state, layout))
                    if is_solution:
                        label = "0회 시작" if step == 0 else f"{step}회 {'↑→↓←'[solutions[pid]['commands'][step-1]]} {solution_data['commands'][solutions[pid]['commands'][step-1]]}"
                        assert normalize(label) in text
                    observed_states[pid] += 1
                pages.append({"page": number, "characters": len(page.chars), "boards": checked, "font_embedded": True, "bounds_ok": True})
        all_text = normalize(" ".join(p.extract_text() for p in reader.pages))
        if is_solution:
            for value in (3,7,11):
                assert f"최단{value}회" in all_text
            assert normalize("각 문제의 최단 명령열은 하나입니다.") in all_text
        else:
            for required in ["동전 두 개", "A와 B를 구별", "진한 A와 B", "그 말만 제자리에", "두 말 모두 제자리에",
                             "두 말이 동시에 각자의 목적지에 있으면 성공", "명령 하나를 1회", "아무 말도 움직이지 않는 명령", "횟수 제한 없이"]:
                assert normalize(required) in all_text, required
            for value in (3,7,11):
                assert f"최단{value}회" not in all_text
        same = None
        if args.compare_root:
            same = path.read_bytes() == (args.compare_root/"pdf"/filename).read_bytes()
            assert same, f"재생성 PDF가 다릅니다: {filename}"
        report["files"][filename] = {"pages": pages, "bytes": path.stat().st_size,
          "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "regeneration_byte_identical": same}
    if args.compare_root:
        assert (args.output_root/"layout_manifest.json").read_bytes() == (args.compare_root/"layout_manifest.json").read_bytes()
        report["checks"].append("separate rebuild is byte identical for both PDFs and layout manifest")
    # A rerun may retain a manual review only for the exact same PDF and PNG bytes.
    if args.report.exists():
        prior = json.loads(args.report.read_text())
        visual = prior.get("visual_review")
        if visual and all(
            entry["pdf_sha256"] == report["files"][entry["pdf"]]["sha256"]
            and (ROOT/entry["render"]).exists()
            and hashlib.sha256((ROOT/entry["render"]).read_bytes()).hexdigest() == entry["render_sha256"]
            for entry in visual["reviewed_pages"]
        ):
            report["visual_review"] = visual
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("PASS: 4 pages, 3 problem boards, 24 solution states, embedded Korean font, text, bounds, vector geometry" + (", byte-identical rebuild" if args.compare_root else ""))


if __name__ == "__main__":
    main()
