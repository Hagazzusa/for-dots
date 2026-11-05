"""읽기 전용 검사. 문학적 자연스러움은 판정하지 않습니다."""
from pathlib import Path
import json
import hashlib
ROOT = Path(__file__).resolve().parent

def verify():
    data = json.loads((ROOT / 'scenes.json').read_text())
    actual = (ROOT / 'output/readings.txt').read_text().splitlines()
    checks=[]
    assert len(data['실험']) == 3
    for scene, length in zip(data['실험'], [12,15,12]):
        lines = scene['행']
        assert len(lines) == length
        start = actual.index(scene['제목'])
        forward = actual.index('위에서 아래로', start) + 1
        backward = actual.index('아래에서 위로', forward) + 1
        assert actual[forward:forward+length] == [f'{i+1:02d} {line}' for i,line in enumerate(lines)]
        assert actual[backward:backward+length] == [f'{i+1:02d} {lines[i]}' for i in range(length-1,-1,-1)]
        assert all(':' in x and '\n' not in x for x in lines)
        checks.append({'시험':scene['id'],'행 수':length,'두 순서 대사 보존':True})
    original=data['실험'][0]['행']; control=data['실험'][2]['행']
    assert [i+1 for i,(a,b) in enumerate(zip(original,control)) if a!=b]==[1,12]
    manifest=ROOT/'manifest.json'
    if manifest.exists():
        for name,entry in json.loads(manifest.read_text()).items():
            raw=(ROOT/name).read_bytes()
            assert len(raw)==entry['bytes'] and hashlib.sha256(raw).hexdigest()==entry['sha256'], name
    return {'검사':checks,'대조에서 변경한 원래 행':[1,12],'한계':'순서와 원문 보존만 검사합니다. 사건의 인과·대화 자연스러움·문학적 성취는 자동 판정하지 않습니다.'}

if __name__ == '__main__':
    print(json.dumps(verify(),ensure_ascii=False,indent=2))
