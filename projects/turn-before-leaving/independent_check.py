#!/usr/bin/env python3
"""‘떠나기 전에 돌리기’ 퍼즐의 독립 전체 상태 검증.

입력은 puzzles.json뿐이며, 프로젝트의 다른 풀이 구현을 읽지 않는다.
공개 함수 successors()로 다른 구현과 합법 전이 집합을 대조할 수 있다.
상태는 (현재 칸, 아홉 화살표 튜플, 누적 회전 수), 선택은 0 또는 1이다.
Python 3.10 이상에서 python independent_check.py로 읽기 전용 실행한다.
결과 파일은 --output 경로를 명시했을 때만 저장한다.
"""

from __future__ import annotations

import argparse
from collections import deque
import hashlib
from itertools import product
import json
from pathlib import Path
from typing import NamedTuple


class State(NamedTuple):
    position: int
    arrows: tuple[int, ...]
    rotations_used: int


def successors(
    state: State | tuple[int, tuple[int, ...], int],
    *,
    goal: int = 2,
    budget: int = 5,
) -> list[tuple[int, State]]:
    """합법적인 (선택, 다음 상태) 쌍을 반환한다. 목표에서는 출발하지 않는다.

    action=0이면 그대로, action=1이면 출발 칸 화살표를 시계방향으로
    정확히 90도 회전한 뒤 이동한다. 불법 이동은 새 상태를 만들지 않으며,
    화살표만 돌리고 제자리에 머무르는 것도 허용하지 않는다.
    """
    position, arrows, used = state
    if position == goal:
        return []
    result = []
    for rotate in (0, 1):
        if used + rotate > budget:
            continue
        direction = (arrows[position] + rotate) % 4
        # 좌표로 계산하여 왼쪽·오른쪽 경계를 넘어 줄바꿈하는 이동을 막는다.
        dx, dy = ((0, -1), (1, 0), (0, 1), (-1, 0))[direction]
        x, y = position % 3 + dx, position // 3 + dy
        if not (0 <= x < 3 and 0 <= y < 3):
            continue
        updated = list(arrows)
        updated[position] = direction
        result.append((rotate, State(y * 3 + x, tuple(updated), used + rotate)))
    return result


def validate_input(puzzle: dict) -> None:
    assert len(puzzle["arrows"]) == 9
    assert all(type(a) is int and 0 <= a < 4 for a in puzzle["arrows"])
    assert type(puzzle["start"]) is int and 0 <= puzzle["start"] < 9
    assert type(puzzle["goal"]) is int and 0 <= puzzle["goal"] < 9
    assert type(puzzle["budget"]) is int and puzzle["budget"] >= 0


def simulate_choices(puzzle: dict, choices: tuple[int, ...]) -> dict | None:
    """successors()를 호출하지 않는 별도의 선택열 직접 재생.

    좌표 계산 대신 고정된 이웃 칸 표를 사용한다.
    목표 도착 즉시 끝나므로 목표 도착은 마지막 선택에서 이루어져야 한다.
    """
    neighbors = (
        (None, 1, 3, None), (None, 2, 4, 0), (None, None, 5, 1),
        (0, 4, 6, None), (1, 5, 7, 3), (2, None, 8, 4),
        (3, 7, None, None), (4, 8, None, 6), (5, None, None, 7),
    )
    arrows = puzzle["arrows"].copy()
    position = puzzle["start"]
    used = 0
    cells = [position]
    steps = []
    for number, rotate in enumerate(choices, 1):
        if position == puzzle["goal"]:
            return None
        used += rotate
        if used > puzzle["budget"]:
            return None
        before = arrows[position]
        arrows[position] = (before + rotate) % 4
        target = neighbors[position][arrows[position]]
        if target is None:
            return None
        steps.append({
            "move": number, "from": position, "to": target,
            "rotate": bool(rotate), "arrow_before": before,
            "arrow_after": arrows[position], "rotations_used": used,
        })
        position = target
        cells.append(position)
    if position != puzzle["goal"]:
        return None
    return {"choices": list(choices), "cells": cells,
            "rotations_used": used, "steps": steps,
            "final_arrows": arrows}


def inspect_puzzle(puzzle: dict) -> dict:
    validate_input(puzzle)
    initial = State(puzzle["start"], tuple(puzzle["arrows"]), 0)
    states = [initial]
    indexes = {initial: 0}
    distance = {initial: 0}
    ways = {initial: 1}
    queue = deque([initial])
    edges = []
    while queue:
        state = queue.popleft()
        for action, following in successors(
            state, goal=puzzle["goal"], budget=puzzle["budget"]
        ):
            edges.append({"from_state": indexes[state], "action": action,
                          "to_state": indexes.get(following, len(states))})
            if following not in indexes:
                indexes[following] = len(states)
                states.append(following)
                distance[following] = distance[state] + 1
                ways[following] = 0
                queue.append(following)
            if distance[following] == distance[state] + 1:
                ways[following] += ways[state]

    goals = [s for s in states if s.position == puzzle["goal"]]
    shortest = min((distance[s] for s in goals), default=None)
    shortest_goals = [s for s in goals if distance[s] == shortest]
    count = sum(ways[s] for s in shortest_goals)

    # 최초 해답 길이까지 가능한 모든 이진 선택열을 빠짐없이 재생한다.
    # 이를 통해 더 짧은 길이에는 목표 도달 경로가 없다는 점도 확인한다.
    brute_counts = []
    examples = []
    if shortest is not None:
        for length in range(shortest + 1):
            successes = []
            for choices in product((0, 1), repeat=length):
                replay = simulate_choices(puzzle, choices)
                if replay is not None:
                    successes.append(replay)
            brute_counts.append(len(successes))
            if length == shortest:
                examples = successes
        assert not any(brute_counts[:-1])
        assert brute_counts[-1] == count

    graph_states = [
        {"state_id": indexes[s], "position": s.position,
         "arrows": list(s.arrows), "rotations_used": s.rotations_used,
         "minimum_moves_to_state": distance[s],
         "minimum_length_choice_prefix_count": ways[s],
         "terminal": s.position == puzzle["goal"]}
        for s in states
    ]
    return {
        "id": puzzle["id"], "name": puzzle.get("name"),
        "input": puzzle,
        "shortest_moves": shortest,
        "shortest_choice_sequence_count": count,
        "all_shortest_solutions": examples,
        "brute_force_solution_counts_by_exact_move_length": brute_counts,
        "reachable_state_count": len(states),
        "legal_transition_count": len(edges),
        "reachable_goal_state_count": len(goals),
        "maximum_minimum_moves_to_state": max(distance.values()),
        "reachable_graph": {"initial_state": 0, "states": graph_states,
                            "transitions": edges},
    }


def self_test() -> None:
    arrows = (0,) * 9
    # 왼쪽 위에서 위로 나갈 수 없지만, 회전하면 오른쪽으로 이동할 수 있다.
    state = State(0, arrows, 0)
    assert successors(state) == [(1, State(1, (1,) + (0,) * 8, 1))]
    assert state.arrows == arrows  # 원래 상태의 화살표는 바뀌지 않는다.
    # 오른쪽 경계에서 오른쪽으로 나가 다음 줄에 나타날 수 없다.
    assert successors(State(5, (1,) * 9, 0), budget=0) == []
    # 목표 칸에서는 지형상 가능한 이동도 허용하지 않는다.
    assert successors(State(2, arrows, 0)) == []
    # 예산을 다 쓰면 화살표를 그대로 두는 이동만 가능하다.
    assert successors(State(4, arrows, 5)) == [(0, State(1, arrows, 5))]
    # 앞서 바뀐 방향에서 다시 회전할 수 있으며, 그 변화는 다음 상태에 남는다.
    board = (0, 0, 0, 0, 3, 0, 0, 0, 0)
    assert successors(State(4, board, 1))[1] == (1, State(1, arrows, 2))
    # 바깥을 향해 회전한 뒤 제자리에 머무르는 선택은 없다.
    assert successors(State(0, (3,) * 9, 0)) == []


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path,
                        default=Path(__file__).with_name("puzzles.json"),
                        help="검증할 퍼즐 JSON 경로")
    parser.add_argument("--output", type=Path, default=None,
                        help="결과를 저장할 JSON 경로. 생략하면 파일을 쓰지 않는다.")
    args = parser.parse_args()
    self_test()
    source = args.input.read_bytes()
    puzzles = json.loads(source)
    results = [inspect_puzzle(puzzle) for puzzle in puzzles]
    output = {
        "method": "별도로 구현한 너비 우선 전체 상태 탐색과 모든 이진 선택열 직접 재생",
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "direction_encoding": {"0": "위", "1": "오른쪽", "2": "아래", "3": "왼쪽"},
        "cell_encoding": "y * 3 + x, 맨 위 행 y=0, 맨 왼쪽 열 x=0",
        "action_encoding": {"0": "그대로", "1": "시계방향 90도 회전"},
        "state_identity": ["position", "all_nine_arrow_directions", "rotations_used"],
        "goal_rule": "목표 칸에 도착하는 즉시 종료",
        "self_tests": "통과",
        "puzzles": results,
    }
    if args.output is not None:
        args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for result in results:
        print(f"문제 {result['id']}: 최단={result['shortest_moves']}, "
              f"최단 선택열={result['shortest_choice_sequence_count']}, "
              f"상태={result['reachable_state_count']}, "
              f"전이={result['legal_transition_count']}")
        for solution in result["all_shortest_solutions"]:
            print(f"  경로={solution['cells']} 선택열={solution['choices']} "
                  f"회전={solution['rotations_used']}")


if __name__ == "__main__":
    main()
