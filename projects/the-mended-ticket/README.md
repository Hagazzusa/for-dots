# 덧댄 자리

창 쪽으로 들어 올린 낡은 왕복표. 인쇄선에 묻혀 있던 이음이 빛을 받자 드러납니다.

- [6초 무성 영상](The-Mended-Ticket.mp4)
- [창 가까이 가기 전과 후](Before-and-Against-the-Light.jpg)
- [편집 가능한 제작 코드](render.py)

## 제작과 확인

종이와 손, 창을 따로 그리고 종이의 위치·기울기·색을 바꿨습니다. 빛을 통과시키면 종이 수선 자국이 다르게 보일 수 있다는 점에서 출발했습니다. [폴저 셰익스피어 도서관의 수선 기록](https://www.folger.edu/blogs/collation/how-not-to-mend-a-tear/)을 참고했으며, 장면과 표는 새로 그렸습니다. 실제 종이의 투과율을 측정하거나 모사한 것은 아닙니다.

Python 3, Pillow, DejaVu Sans Mono, FFmpeg(libx264)가 있는 환경에서 `python3 render.py`로 다시 그릴 수 있습니다. 정지 비교만 만들려면 `python3 render.py --still`을 사용합니다.

영상은 864×576, 24fps, 144프레임입니다. 전 프레임 디코드와 축소 정지 비교로 종이와 수선 자국을 확인했습니다.
