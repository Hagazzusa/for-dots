#!/usr/bin/env python3
"""풀이 모듈을 가져오지 않는 별도 좌표 기반 검사.
실행: python3 independent_check.py [puzzles.json]
"""
from collections import deque
import json
from pathlib import Path
import sys

DIRECTIONS = {'위': (0, -1), '오른쪽': (1, 0), '아래': (0, 1), '왼쪽': (-1, 0)}


def move(state, delta, walls, size):
    intended = []
    reasons = []
    for position, sign in zip(state, (1, -1)):
        x, y = position
        dx, dy = delta
        candidate = (x + sign * dx, y + sign * dy)
        if not (0 <= candidate[0] < size and 0 <= candidate[1] < size):
            intended.append(position)
            reasons.append('edge')
        elif candidate in walls:
            intended.append(position)
            reasons.append('wall')
        else:
            intended.append(candidate)
            reasons.append('move')
    result = tuple(intended)
    if result[0] == result[1] or result == (state[1], state[0]):
        return state, ('collision', 'collision')
    return result, tuple(reasons)


def solve(start, walls, size):
    distance, counts, previous = {start: 0}, {start: 1}, {}
    queue = deque([start])
    while queue:
        state = queue.popleft()
        for command, delta in DIRECTIONS.items():
            target, _ = move(state, delta, walls, size)
            depth = distance[state] + 1
            if target not in distance:
                distance[target] = depth
                counts[target] = counts[state]
                previous[target] = (state, command)
                queue.append(target)
            elif distance[target] == depth:
                counts[target] += counts[state]
    return distance, counts, previous


def rule_tests():
    # 같은 도착 칸, 자리 맞바꿈, 벽과 판 가장자리의 정지를 검사한다.
    assert move(((0, 1), (2, 1)), (1, 0), set(), 4)[0] == ((0, 1), (2, 1))
    assert move(((0, 1), (1, 1)), (1, 0), set(), 4)[0] == ((0, 1), (1, 1))
    assert move(((0, 0), (3, 3)), (1, 0), {(1, 0)}, 4)[0] == ((0, 0), (2, 3))
    assert move(((0, 0), (3, 3)), (0, -1), set(), 4)[0] == ((0, 0), (3, 3))
    assert move(((0, 1), (3, 3)), (0, -1), set(), 4)[0] == ((0, 0), (3, 3))


def main():
    rule_tests()
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name('puzzles.json')
    data = json.loads(path.read_text())
    size = data['size']
    coord = lambda index: (index % size, index // size)
    index = lambda p: p[1] * size + p[0]
    reports = []
    for puzzle in data['puzzles']:
        walls = set(map(coord, puzzle['walls']))
        start = tuple(map(coord, puzzle['start']))
        goal = tuple(map(coord, puzzle['goal']))
        for state in (start, goal):
            assert state[0] != state[1]
            assert all(p not in walls and 0 <= p[0] < size and 0 <= p[1] < size for p in state)
        distance, counts, previous = solve(start, walls, size)
        assert goal in distance, f"Unreachable puzzle {puzzle['id']}"
        path_commands = []
        state = goal
        while state != start:
            state, command = previous[state]
            path_commands.append(command)
        path_commands.reverse()
        trace = [{'step': 0, 'A': index(start[0]), 'B': index(start[1])}]
        state = start
        for step, command in enumerate(path_commands, 1):
            state, reasons = move(state, DIRECTIONS[command], walls, size)
            trace.append({'step': step, 'command': command, 'A': index(state[0]), 'B': index(state[1]), 'A_action': reasons[0], 'B_action': reasons[1]})
        assert state == goal
        reports.append({'id': puzzle['id'], 'shortest_moves': distance[goal], 'shortest_command_sequences': counts[goal], 'reachable_states': len(distance), 'commands': path_commands, 'trace': trace})
    print(json.dumps({'rule_tests': 'passed', 'puzzles': reports}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
