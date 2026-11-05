"""대사 내부를 바꾸지 않고 두 읽기 순서를 저장합니다."""
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parent

def compose(data):
    out = [data['상태'], data['읽기 규칙'], '']
    for scene in data['실험']:
        out.extend([scene['제목'], scene['조건'], ''])
        numbered = list(enumerate(scene['행'], 1))
        for label, rows in [('위에서 아래로', numbered), ('아래에서 위로', numbered[::-1])]:
            out.append(label)
            out.extend(f'{n:02d} {line}' for n, line in rows)
            out.append('')
    return '\n'.join(out) + '\n'

if __name__ == '__main__':
    data = json.loads((ROOT / 'scenes.json').read_text())
    target = ROOT / 'output/readings.txt'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(compose(data), encoding='utf-8')
