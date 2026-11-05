#!/usr/bin/env python3
"""세 개의 반대 이동 퍼즐을 A4 문제지와 상태별 해설지로 만든다.

python build_pdf.py
python build_pdf.py --output-root /tmp/opposite-steps-check/output

입력 JSON은 읽기만 한다. reportlab과 fonttools가 필요하며, Noto Serif
CJK KR의 사용 글자만 내장한다. 글꼴 변환 방식은 인접 프로젝트
before-the-answer/build_pdf.py의 방식을 재사용했다.
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
import tempfile

from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont as SourceFont
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

ROOT = Path(__file__).resolve().parent
FONT_NAME = "OppositeStepsNotoSerifKR"
DEFAULT_FONT = Path("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc")
ARROWS = ["↑", "→", "↓", "←"]


def register_font(font_path: Path, characters: str, work_dir: Path) -> None:
    """CFF 한국어 글꼴의 사용 글자를 TrueType 곡선으로 변환하여 내장한다."""
    source = SourceFont(font_path, fontNumber=1, lazy=True)
    try:
        cmap = source.getBestCmap()
        missing = sorted({c for c in characters if not c.isspace() and ord(c) not in cmap})
        if missing:
            raise ValueError(f"글꼴에 없는 글자: {''.join(missing)!r}")
        options = subset.Options()
        options.recalc_timestamp = False
        subsetter = subset.Subsetter(options=options)
        subsetter.populate(text=characters)
        subsetter.subset(source)
        order, glyph_set = source.getGlyphOrder(), source.getGlyphSet()
        glyphs = {}
        for name in order:
            pen = TTGlyphPen(None)
            glyph_set[name].draw(Cu2QuPen(pen, 1.0, reverse_direction=True))
            glyphs[name] = pen.glyph()
        builder = FontBuilder(source["head"].unitsPerEm, isTTF=True)
        builder.setupGlyphOrder(order)
        builder.setupCharacterMap(source.getBestCmap())
        builder.setupGlyf(glyphs)
        builder.setupHorizontalMetrics(dict(source["hmtx"].metrics))
        builder.setupHorizontalHeader(ascent=source["hhea"].ascent, descent=source["hhea"].descent)
        builder.setupNameTable({
            "familyName": FONT_NAME, "styleName": "Regular",
            "uniqueFontIdentifier": FONT_NAME, "fullName": FONT_NAME,
            "psName": FONT_NAME,
            "copyright": "Noto CJK, SIL Open Font License 1.1. Converted subset for PDF embedding.",
        })
        builder.setupOS2(
            sTypoAscender=source["OS/2"].sTypoAscender,
            sTypoDescender=source["OS/2"].sTypoDescender,
            usWinAscent=source["OS/2"].usWinAscent,
            usWinDescent=source["OS/2"].usWinDescent,
        )
        builder.setupPost()
        builder.setupMaxp()
        builder.font["head"].created = builder.font["head"].modified = 2082844800
        converted = work_dir / f"{FONT_NAME}.ttf"
        builder.save(converted)
        pdfmetrics.registerFont(TTFont(FONT_NAME, str(converted)))
    finally:
        source.close()


class Sheet:
    """좌상단 mm 좌표를 사용하며, 그린 구성 요소와 상태를 검사 기록으로 남긴다."""
    def __init__(self, buffer: io.BytesIO, title: str, kind: str, layout: dict):
        self.width, self.height = [v * mm for v in layout["page_mm"]]
        self.canvas = Canvas(buffer, pagesize=(self.width, self.height), invariant=1, pageCompression=1)
        self.canvas.setTitle(title)
        self.canvas.setAuthor("닷돌이")
        self.canvas.setSubject("한 명이 푸는 4×4 반대 이동 종이 퍼즐" if kind == "문제" else "상태별 최단 해법")
        self.layout, self.kind = layout, kind
        self.page = 1
        self.records = []

    def text(self, text, x, y, size=10.3, align="left", gray=0, font=FONT_NAME):
        c = self.canvas
        c.setFillGray(gray)
        c.setFont(font, size)
        width = pdfmetrics.stringWidth(text, font, size)
        px, py = x * mm, self.height - y * mm
        if align == "center":
            left = px - width / 2
            c.drawCentredString(px, py, text)
        elif align == "right":
            left = px - width
            c.drawRightString(px, py, text)
        else:
            left = px
            c.drawString(px, py, text)
        # Font-derived vertical extents, in top-down page points.
        ascent = pdfmetrics.getAscent(font, size)
        descent = pdfmetrics.getDescent(font, size)
        self.records.append({"page": self.page, "kind": "text", "text": text,
                             "bbox": [left, y * mm - ascent, left + width, y * mm - descent]})

    def line(self, x1, y1, x2, y2, width=.5, gray=.55):
        c = self.canvas
        c.setStrokeGray(gray)
        c.setLineWidth(width)
        c.line(x1 * mm, self.height-y1*mm, x2*mm, self.height-y2*mm)

    def token(self, letter, x, y, diameter, filled, gray=0, font_size=None):
        """A는 원, B는 사각형. 좌표는 모양 중심이다."""
        c = self.canvas
        px, py, r = x*mm, self.height-y*mm, diameter*mm/2
        c.setLineWidth(.9 if diameter > 9 else .75)
        c.setStrokeGray(gray)
        c.setFillGray(gray if filled else 1)
        if letter == "A":
            c.circle(px, py, r, stroke=1, fill=1)
        else:
            c.rect(px-r, py-r, 2*r, 2*r, stroke=1, fill=1)
        fs = font_size or diameter*mm*.46
        self.text(letter, x, y+fs/mm*.35, fs, align="center", gray=1 if filled else gray, font="Helvetica-Bold")

    def wall(self, x, y, side):
        c = self.canvas
        c.setFillGray(self.layout["gray"]["wall"])
        c.rect(x*mm, self.height-(y+side)*mm, side*mm, side*mm, fill=1, stroke=0)

    def board(self, puzzle, x, y, cell, state=None, mini=False):
        state = puzzle["start"] if state is None else state
        c = self.canvas
        for index in puzzle["walls"]:
            row, col = divmod(index, 4)
            self.wall(x+col*cell, y+row*cell, cell)
        for n in range(5):
            self.line(x+n*cell, y, x+n*cell, y+4*cell, .65, self.layout["gray"]["grid"])
            self.line(x, y+n*cell, x+4*cell, y+n*cell, .65, self.layout["gray"]["grid"])
        self.line(x, y, x+4*cell, y, 1, 0)
        self.line(x, y+4*cell, x+4*cell, y+4*cell, 1, 0)
        self.line(x, y, x, y+4*cell, 1, 0)
        self.line(x+4*cell, y, x+4*cell, y+4*cell, 1, 0)
        for i, position in enumerate(puzzle["goal"]):
            row, col = divmod(position, 4)
            self.token("AB"[i], x+(col+.5)*cell, y+(row+.5)*cell,
                       cell*(.80 if mini else .59), False,
                       self.layout["gray"]["goal_in_solution"] if mini else 0,
                       8.5 if mini else 14)
        for i, position in enumerate(state):
            row, col = divmod(position, 4)
            self.token("AB"[i], x+(col+.5)*cell, y+(row+.5)*cell,
                       cell*(.59 if mini else .59), True, 0, 8.5 if mini else 14)
        self.records.append({"page": self.page, "kind": "board", "puzzle": puzzle["id"],
                             "state": list(state), "goal": puzzle["goal"], "walls": puzzle["walls"],
                             "bbox": [x*mm, y*mm, (x+4*cell)*mm, (y+4*cell)*mm], "mini": mini})

    def legend(self, y, solution=False):
        self.token("A", 20.5, y-1, 4.7, True, font_size=6.2)
        self.token("B", 27, y-1, 4.7, True, font_size=6.2)
        self.text("현재 말" if solution else "출발", 32, y, 9)
        gray = self.layout["gray"]["goal_in_solution"] if solution else 0
        self.token("A", 72, y-1, 5.1, False, gray, font_size=6.4)
        self.token("B", 79, y-1, 5.1, False, gray, font_size=6.4)
        self.text("목적지", 84, y, 9)
        self.wall(119, y-3.5, 5)
        self.canvas.setStrokeGray(.24)
        self.canvas.setLineWidth(.6)
        self.canvas.rect(119*mm, self.height-(y+1.5)*mm, 5*mm, 5*mm, fill=0, stroke=1)
        self.text("벽", 127, y, 9)
        self.text("A는 원 · B는 사각형", 192, y, 9, align="right")

    def footer(self):
        self.text(f"반대편으로 한 칸 · {self.kind} {self.page} / 2", 105,
                  self.layout["footer_baseline_mm"], 8, align="center")

    def next_page(self):
        self.footer()
        self.canvas.showPage()
        self.page += 1

    def save(self):
        self.footer()
        self.canvas.save()


def records_area(s, x, top, bottom, width=80):
    s.text("내가 사용한 명령", x, top, 10.3)
    s.text("A 기준으로 위 · 오른쪽 · 아래 · 왼쪽", x, top+7, 8.7)
    for y in range(int(top+19), int(bottom), 12):
        s.line(x, y, x+width, y, .45, .67)
    s.text("총", x, bottom+4, 9.5)
    s.line(x+7, bottom+4.5, x+29, bottom+4.5, .45, .5)
    s.text("회", x+32, bottom+4, 9.5)


def problems_sheet(puzzles, layout):
    buffer = io.BytesIO()
    s = Sheet(buffer, "반대편으로 한 칸", "문제", layout)
    s.text("반대편으로 한 칸", 18, 26, 26)
    s.text("한 명이 푸는 종이 퍼즐 · 문제 3개", 18, 36, 10)
    s.text("준비", 18, 49, 12)
    s.text("동전 두 개 또는 작은 말 두 개를 준비하고, A와 B를 구별해 놓으세요.", 18, 57, 10.3)
    s.text("진한 A와 B 모양 위에 각각 놓고 시작하세요.", 18, 63, 10.3)
    s.text("규칙", 18, 70, 12)
    rules = [
        ("1  A는 명령 방향으로 한 칸, B는 반대 방향으로 한 칸 움직입니다.", 79),
        ("위 ↔ 아래     오른쪽 ↔ 왼쪽", 86),
        ("2  먼저 두 말의 이동 예정 칸을 계산합니다. 벽이나 판 밖을 향하는 말은", 97),
        ("그 말만 제자리에 둡니다.", 103),
        ("3  그 결과 두 말의 예정 칸이 같거나 서로의 현재 칸을 맞바꾸려 하면", 114),
        ("두 말 모두 제자리에 둡니다.", 120),
        ("4  목적지에 도착한 말도 다음 명령을 따릅니다. 두 말이 동시에 각자의", 131),
        ("목적지에 있으면 성공입니다.", 137),
        ("5  명령 하나를 1회로 셉니다. 아무 말도 움직이지 않는 명령은 빼고 생각하세요.", 148),
    ]
    for text, y in rules:
        s.text(text, 23 if y in (86, 103, 120, 137) else 18, y, 10.3)
    s.legend(158)
    first = layout["problem_pages"][0]["puzzles"][0]
    p = puzzles[0]
    s.text(f"1  {p['title']}", 18, first["title_y_mm"], 14)
    s.board(p, first["board_x_mm"], first["board_y_mm"], layout["problem_cell_mm"])
    s.text("처음에는 횟수 제한 없이", 110, 184, 10.3)
    s.text("두 말을 목적지로 보내세요.", 110, 191, 10.3)
    s.text("최단 횟수는 해설지에서", 110, 204, 9.5)
    s.text("확인할 수 있어요.", 110, 211, 9.5)
    records_area(s, 110, 226, 257, 82)
    s.text("실제 크기 100%로 인쇄하면 한 칸이 20mm입니다.", 18, 272, 8.8)
    s.next_page()
    s.text("반대편으로 한 칸", 18, 24, 18)
    s.text("문제 2 · 3", 192, 24, 9.5, align="right")
    s.legend(36)
    for item in layout["problem_pages"][1]["puzzles"]:
        p = next(p for p in puzzles if p["id"] == item["id"])
        s.text(f"{p['id']}  {p['title']}", 18, item["title_y_mm"], 14)
        s.board(p, item["board_x_mm"], item["board_y_mm"], layout["problem_cell_mm"])
        records_area(s, 110, item["board_y_mm"]+6, item["board_y_mm"]+76, 82)
    s.text("명령은 A 기준입니다. B는 반대로 움직이며, 목적지에 도착한 말도 다음 명령을 따릅니다.", 18, 267, 9.3)
    s.save()
    return buffer.getvalue(), s.records


def state_rows(s, puzzle, solution, rows, layout, command_names):
    for index, state in enumerate(solution["states"]):
        row, col = divmod(index, 4)
        x, y = layout["solution_columns_x_mm"][col], rows[row]
        if index == 0:
            label = "0회  시작"
        else:
            command = solution["commands"][index-1]
            label = f"{index}회  {ARROWS[command]} {command_names[command]}"
        s.text(label, x, y-6, 9.4)
        s.board(puzzle, x, y, layout["solution_board_mm"]/4, state, mini=True)
        if index == len(solution["states"])-1:
            s.text("성공", x+42, y-6, 9.4, align="right")


def solutions_sheet(puzzles, solutions, command_names, layout):
    buffer = io.BytesIO()
    s = Sheet(buffer, "반대편으로 한 칸 해설", "해설", layout)
    s.text("반대편으로 한 칸 해설", 15, 25, 23)
    s.text("화살표와 방향은 모두 A에게 내리는 명령입니다. B는 반대로 움직입니다.", 15, 35, 10)
    s.legend(45, solution=True)
    for group in layout["solution_pages"][0]["groups"]:
        p = next(p for p in puzzles if p["id"] == group["id"])
        solution = next(v for v in solutions if v["id"] == p["id"])
        s.text(f"{p['id']}  {p['title']}", 15, group["title_y_mm"], 14)
        s.text(f"최단 {solution['minimum']}회", 195, group["title_y_mm"], 11, align="right")
        state_rows(s, p, solution, group["rows_y_mm"], layout, command_names)
    s.text("마지막 아래 명령에서 B는 벽에 막혀 멈추고, A만 아래로 움직입니다.", 15, 127, 9.8)
    s.text("목적지에 한 번씩 들르는 것으로는 부족합니다. 두 말이 각자 목적지에 동시에 있어야 합니다.", 15, 278, 9.1)
    s.next_page()
    p = puzzles[2]
    solution = solutions[2]
    s.text(f"3  {p['title']}", 15, 24, 19)
    s.text(f"최단 {solution['minimum']}회", 195, 24, 11, align="right")
    s.text("화살표와 방향은 A 기준입니다. 각 그림은 해당 명령을 실행한 뒤의 모습입니다.", 15, 35, 9.6)
    s.legend(45, solution=True)
    state_rows(s, p, solution, layout["solution_pages"][1]["groups"][0]["rows_y_mm"], layout, command_names)
    s.text("5회째 아래 명령에서는 A가 벽에 막혀 멈추고, B만 위로 움직입니다.", 15, 243, 9.8)
    s.text("9·10회째 오른쪽 명령에서는 B가 벽에 막혀 멈추고, A만 오른쪽으로 움직입니다.", 15, 251, 9.8)
    s.text("모든 도달 가능한 말 배치를 탐색해 최단 횟수를 확인했습니다.", 15, 266, 9.5)
    s.text("각 문제의 최단 명령열은 하나입니다.", 15, 274, 9.5)
    s.save()
    return buffer.getvalue(), s.records


def check_bounds(records, layout):
    width, height = [v*mm for v in layout["page_mm"]]
    for entry in records:
        x0, y0, x1, y1 = entry["bbox"]
        if not (8*mm <= x0 <= x1 <= width-8*mm and 8*mm <= y0 <= y1 <= height-8*mm):
            raise ValueError(f"페이지 안전 영역을 넘는 요소: {entry}")


def build(output_root: Path, font_path: Path):
    sources = {name: (ROOT/name).read_bytes() for name in ("puzzles.json", "solutions.json", "layout.json")}
    puzzle_data, solution_data, layout = [json.loads(sources[n]) for n in sources]
    puzzles, solutions = puzzle_data["puzzles"], solution_data["solutions"]
    assert puzzle_data["size"] == 4
    assert [p["id"] for p in puzzles] == [1, 2, 3]
    assert [s["id"] for s in solutions] == [1, 2, 3]
    for p, solution in zip(puzzles, solutions):
        assert solution["states"][0] == p["start"]
        assert solution["states"][-1] == p["goal"]
        assert len(solution["states"]) == len(solution["commands"])+1 == solution["minimum"]+1
    # All literal Korean text and JSON captions are checked before any PDF is written.
    characters = Path(__file__).read_text(encoding="utf-8") + "".join(v.decode("utf-8") for v in sources.values())
    output_root = output_root.resolve()
    (output_root/"pdf").mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="opposite-steps-font-") as temporary:
        register_font(font_path, characters, Path(temporary))
        problem_pdf, problem_records = problems_sheet(puzzles, layout)
        solution_pdf, solution_records = solutions_sheet(puzzles, solutions, puzzle_data["commands"], layout)
    for name, raw in sources.items():
        if (ROOT/name).read_bytes() != raw:
            raise RuntimeError(f"제작 중 입력이 바뀌었습니다: {name}")
    outputs = [("Opposite-Steps.pdf", problem_pdf, problem_records),
               ("Opposite-Steps-Solutions.pdf", solution_pdf, solution_records)]
    manifest = {"units": "points", "origin": "top left", "page_mm": layout["page_mm"], "files": {}}
    for name, raw, records in outputs:
        check_bounds(records, layout)
        path = output_root/"pdf"/name
        path.write_bytes(raw)
        manifest["files"][name] = records
        print(path)
    (output_root/"layout_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT/"output")
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT)
    args = parser.parse_args()
    build(args.output_root, args.font)


if __name__ == "__main__":
    main()
