"""네 시각에 배정되는 물건과 발견 장소를 모두 검사한다."""
from itertools import permutations
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
TIMES = ("17:00", "17:10", "17:20", "17:30")
ITEMS = ("열쇠", "수첩", "목도리", "우산")
PLACES = ("빵집", "놀이터", "작은도서관", "자전거 가게")
CLUES = (
    "수첩은 목도리보다 정확히 10분 먼저 접수됐다.",
    "작은도서관에서 주운 물건은 빵집에서 주운 물건보다 정확히 20분 늦게 접수됐다.",
    "자전거 가게에서 주운 물건은 놀이터에서 주운 물건보다 늦게 접수됐다.",
    "열쇠는 수첩보다 먼저 접수됐다.",
    "우산은 자전거 가게에서 발견됐다.",
)


def pass_clues(items, places):
    """시각은 10분 간격이므로 순열의 인덱스를 비교한다."""
    item, place = items.index, places.index
    return (
        item("목도리") - item("수첩") == 1,
        place("작은도서관") - place("빵집") == 2,
        place("자전거 가게") > place("놀이터"),
        item("열쇠") < item("수첩"),
        item("우산") == place("자전거 가게"),
    )


def main():
    problem = (HERE / "README.md").read_text(encoding="utf-8")
    solution = (HERE / "solution.md").read_text(encoding="utf-8")
    for label, values in (("접수 시각", TIMES), ("물건", ITEMS), ("발견 장소", PLACES)):
        assert f"**{label}** · " + ", ".join(values) in problem
    assert tuple(re.findall(r"^\d+\. (.+)$", problem, re.M)) == CLUES
    candidates = [
        (items, places, pass_clues(items, places))
        for items in permutations(ITEMS)
        for places in permutations(PLACES)
    ]
    assert len(candidates) == 576
    answers = [(items, places) for items, places, checks in candidates if all(checks)]
    assert len(answers) == 1
    drops = [sum(all(checks[:i] + checks[i + 1:]) for _, _, checks in candidates) for i in range(5)]
    assert drops == [6, 8, 3, 3, 6]
    rows = tuple(re.findall(r"^\| (17:\d\d) \| ([^|]+) \| ([^|]+) \|$", solution, re.M))
    assert rows == tuple(zip(TIMES, *answers[0]))
    assert not any(all(value in line for value in row) for line in problem.splitlines() for row in rows)
    print(f"{len(candidates)}개 배정 · 해답 {len(answers)}개 · 단서 하나씩 제외: {drops}")


if __name__ == "__main__":
    main()
