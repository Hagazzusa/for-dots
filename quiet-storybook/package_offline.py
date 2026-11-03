"""원본 PNG를 바꾸지 않고 작은 오프라인 사본을 새 폴더에 만듭니다."""
import argparse
import hashlib
import shutil
from pathlib import Path

FILES = ('index.html', 'style.css', 'story.js', 'README.md', 'QA.md', 'package_offline.py', 'test_story.cjs', 'build_pdf.py', 'FONT_LICENSE.txt')
IMAGES = (
    'second-cup/renders/the_second_cup_final.png',
    'a-place-for-rain/renders/a_place_for_rain_final.png',
    'morning-on-the-sill/renders/morning_on_the_sill_final.png',
)

def package(repo, output):
    repo, output = Path(repo).resolve(), Path(output).resolve()
    if output.exists():
        raise SystemExit('출력 폴더가 이미 있습니다. 새로운 폴더를 지정하세요.')
    source = Path(__file__).resolve().parent
    for item in FILES:
        if not (source / item).is_file():
            raise SystemExit(f'이야기 파일이 없습니다: {item}')
    for item in IMAGES:
        if not (repo / item).is_file():
            raise SystemExit(f'원본 이미지가 없습니다: {item}')
    (output / 'quiet-storybook').mkdir(parents=True)
    for item in FILES:
        shutil.copy2(source / item, output / 'quiet-storybook' / item)
    for item in IMAGES:
        destination = output / item
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo / item, destination)
        assert hashlib.sha256(destination.read_bytes()).digest() == hashlib.sha256((repo / item).read_bytes()).digest()
    print('완료: quiet-storybook/index.html을 브라우저로 여세요. PNG 바이트 일치 확인.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, help='세 원본 작품 폴더가 있는 저장소 루트')
    parser.add_argument('--output', required=True, help='아직 존재하지 않는 출력 폴더')
    args = parser.parse_args()
    package(args.repo, args.output)
