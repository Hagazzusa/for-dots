"""Independent placement-first exhaustive check, without generating paths.

Run: python experiments/a_path_left_open/independent_verify.py
Reads solve.py as syntax only and search.json as a claimed result.  Enumerates
every placement of the four pieces in fixed A/B/C/D order, rejects overlaps,
then uses ordinary four-neighbor BFS on the complement.  Does not import solve.
"""
import ast
from collections import deque
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
N = 5
FULL = (1 << (N * N)) - 1
EXPECTED = {
    "A": [(0, 0), (1, 0), (2, 0)],
    "B": [(0, 0), (0, 1), (1, 1)],
    "C": [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)],
    "D": [(0, 0), (2, 0), (0, 1), (1, 1), (2, 1)],
}
NAMES = tuple(EXPECTED)
CORNERS = (1 << 0) | (1 << 24)


def bitmask(cells):
    return sum(1 << (N * y + x) for x, y in cells)


def normalize(points):
    xmin, ymin = min(x for x, y in points), min(y for x, y in points)
    return tuple(sorted((x - xmin, y - ymin) for x, y in points))


def transforms(points):
    # All signed coordinate permutations: the eight symmetries of the square.
    # This is deliberately different from solve.py's repeated rotations.
    return {
        normalize([(sx * (y if swap else x), sy * (x if swap else y))
                   for x, y in points])
        for swap in (False, True)
        for sx in (-1, 1)
        for sy in (-1, 1)
    }


def rotations_only(points):
    return {
        normalize([(x, y) for x, y in points]),
        normalize([(-y, x) for x, y in points]),
        normalize([(-x, -y) for x, y in points]),
        normalize([(y, -x) for x, y in points]),
    }


def placements(points):
    masks = set()
    for shape in transforms(points):
        for dy in range(N):
            for dx in range(N):
                translated = [(x + dx, y + dy) for x, y in shape]
                if all(0 <= x < N and 0 <= y < N for x, y in translated):
                    masks.add(bitmask(translated))
    return sorted(masks)


NEIGHBORS = {
    N * y + x: [N * ny + nx for nx, ny in
               ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))
               if 0 <= nx < N and 0 <= ny < N]
    for y in range(N) for x in range(N)
}


def connected_empty_path(empty):
    if empty & CORNERS != CORNERS:
        return False
    queue = deque([0])
    visited = {0}
    while queue:
        for neighbor in NEIGHBORS[queue.popleft()]:
            if neighbor not in visited and empty & (1 << neighbor):
                queue.append(neighbor)
                visited.add(neighbor)
    return 24 in visited


def diagram(key):
    return ["".join(next((name for name, mask in zip(NAMES, key)
                         if mask & (1 << (y * N + x))), ".")
                    for x in range(N)) for y in range(N)]


def main():
    tree = ast.parse((ROOT / "solve.py").read_text())
    source_shapes = next(ast.literal_eval(node.value) for node in tree.body
                         if isinstance(node, ast.Assign)
                         and any(isinstance(t, ast.Name) and t.id == "SHAPES"
                                 for t in node.targets))
    assert source_shapes == EXPECTED
    claimed = json.loads((ROOT / "search.json").read_text())
    assert claimed["board_size"] == N
    assert claimed["allowed_rotations"] and claimed["allowed_reflections"]
    assert {k: list(map(tuple, v)) for k, v in claimed["shapes"].items()} == EXPECTED
    all_placements = {name: placements(shape) for name, shape in EXPECTED.items()}
    eligible = {name: [m for m in values if not m & CORNERS]
                for name, values in all_placements.items()}
    checked = 0
    found = {}

    def enumerate_placements(index, occupied, chosen):
        nonlocal checked
        if index == len(NAMES):
            checked += 1
            empty = FULL ^ occupied
            assert empty.bit_count() == 9
            if connected_empty_path(empty):
                assert chosen not in found, "Duplicate placement tuple"
                found[chosen] = empty
            return
        for mask in eligible[NAMES[index]]:
            if not mask & occupied:
                enumerate_placements(index + 1, occupied | mask, chosen + (mask,))

    enumerate_placements(0, 0, ())

    def validate_example(solution):
        assert set(solution["pieces"]) == set(NAMES)
        for name, cells in solution["pieces"].items():
            assert len(cells) == len(set(map(tuple, cells))) == len(EXPECTED[name])
            assert all(0 <= x < N and 0 <= y < N for x, y in cells)
        key = tuple(bitmask(solution["pieces"][name]) for name in NAMES)
        assert key in found
        for name, mask in zip(NAMES, key):
            assert mask in all_placements[name]
        path = list(map(tuple, solution["path"]))
        assert len(path) == len(set(path)) == 9
        assert path[0] == (0, 0) and path[-1] == (4, 4)
        assert all(abs(x1 - x2) + abs(y1 - y2) == 1
                   for (x1, y1), (x2, y2) in zip(path, path[1:]))
        assert bitmask(path) == found[key]
        return key

    claimed_keys = [validate_example(s) for s in claimed["solutions"]]
    assert len(claimed_keys) == len(set(claimed_keys)), "Claimed result has duplicates"
    assert set(claimed_keys) == set(found), "Claimed result misses or adds solutions"
    assert len(found) == claimed["all_solution_count"] == 24
    assert len(set(found.values())) == claimed["distinct_path_count"] == 10
    for item in claimed["small_clue_sets"]:
        clue_mask = bitmask(item["clues"])
        matching = {k: e for k, e in found.items() if e & clue_mask == clue_mask}
        assert len(matching) == item["solution_count"]
        assert len(set(matching.values())) == item["distinct_paths"]
        assert validate_example(item["example"]) in matching

    puzzles = {}
    for name, clues in [("puzzle1", [(2, 2)]), ("puzzle2", [(1, 0), (1, 2)])]:
        clue_mask = bitmask(clues)
        matching = {k: e for k, e in found.items() if e & clue_mask == clue_mask}
        puzzles[name] = {
            "clues_xy_zero_based": clues,
            "solution_count": len(matching),
            "distinct_path_count": len(set(matching.values())),
            "diagrams": [diagram(k) for k in sorted(matching)],
        }
        puzzles[name]["individual_clue_solution_counts"] = [
            sum(bool(empty & bitmask([clue])) for empty in found.values())
            for clue in clues
        ]
        without_flips = []
        for key in matching:
            if all(normalize([(i % N, i // N) for i in range(N * N)
                              if mask & (1 << i)]) in rotations_only(EXPECTED[piece])
                   for piece, mask in zip(NAMES, key)):
                without_flips.append(key)
        puzzles[name]["solutions_without_turning_any_piece_over"] = len(without_flips)
    assert puzzles["puzzle1"]["solution_count"] == 4
    assert puzzles["puzzle2"]["solution_count"] == 1
    assert puzzles["puzzle2"]["solutions_without_turning_any_piece_over"] == 0
    report = {
        "method": "Enumerate piece placements independently, then BFS the empty cells",
        "orientation_counts": {n: len(transforms(s)) for n, s in EXPECTED.items()},
        "placement_counts": {n: len(v) for n, v in all_placements.items()},
        "corner_free_placement_counts": {n: len(v) for n, v in eligible.items()},
        "nonoverlapping_corner_free_arrangements_checked": checked,
        "valid_arrangements": len(found),
        "distinct_empty_paths": len(set(found.values())),
        "claimed_solutions_equal_independent_solutions": True,
        "claimed_small_clue_sets_checked": len(claimed["small_clue_sets"]),
        "puzzles": puzzles,
    }
    (ROOT / "independent_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
