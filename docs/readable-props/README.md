# 소품의 의미가 실제 화면에서 읽히는지 확인하기

제작 검사를 통과한 소품도 의도와 다르게 보일 수 있다. 다음 제작에서는 부품 수나 효과 강도보다 **최종 화면에 남는 식별 단서**를 먼저 확인한다. 이 노트는 공개 정물과 파생 연구를 제한적으로 살펴본 제작자의 관찰·해석이다. 일반 사용자 반응이나 문화보편적 판독성을 측정한 결과는 아니다.

## 의도와 구현과 관찰을 구분하기

| 층 | 확인할 근거 | 대신 증명하지 못하는 것 |
| --- | --- | --- |
| 생성 콘셉트 | 구도·재료감에 관한 의도 참고 | 실제 3D 구조와 기능 |
| 독립 지오메트리 | 소스·저장 메시·접촉과 내부 구조 검사 | 화면에서의 식별 가능성 |
| 실제 렌더러의 픽셀 | 최종 시점·조명·표시 크기의 출력 | 관찰자가 같은 의미를 읽는다는 보장 |
| 관찰된 의미 | 무엇으로 보였는지와 혼동한 단서 기록 | 다른 사람·시점·환경으로의 일반화 |

[Mended Corner](https://github.com/Hagazzusa/for-dots/blob/2e2630e40f859b56c0505b1e4fd1e44420b07525/mended-corner/README.md)와 [The Second Cup](https://github.com/Hagazzusa/for-dots/blob/2e2630e40f859b56c0505b1e4fd1e44420b07525/second-cup/README.md)은 생성 콘셉트를 참고하되 별도 지오메트리로 만든 작품이다. 콘셉트의 설득력이 구현의 기능·판독성을 보증하지 않는다. 해시는 파일 보존을, 닫힌 메시·접촉 검사는 지정한 기하 조건을 확인할 뿐 의미 전달을 검사하지 않는다.

## 대패를 설명하기 전에 대상을 확인하기

[Mended Corner 최종 렌더](https://github.com/Hagazzusa/for-dots/blob/2e2630e40f859b56c0505b1e4fd1e44420b07525/mended-corner/renders/mended_corner_final.png)의 **왼쪽 아래, 양끝이 둥글고 가운데 몸체가 긴 도구**가 대패 소품이다. 작은 크롭에서는 이 윤곽이 전화기 수화기처럼 읽힐 수 있다는 것이 이번 제작자의 해석이다. 중앙의 밝고 계단진 경계가 있는 수리목과는 다른 대상이다. 설명 전에 **장면 이름 + 화면 위치 + 윤곽**으로 대상을 맞추면, 재질 이름이나 이야기만으로 단정하거나 다른 장면의 소품을 섞는 일을 줄일 수 있다.

[제작 소스 246–258행](https://github.com/Hagazzusa/for-dots/blob/2e2630e40f859b56c0505b1e4fd1e44420b07525/mended-corner/build.py#L246-L258)의 `sole`·`toe`·`heel`·`cheek`는 모서리를 둥글린 직육면체다. `wedge`는 이름과 달리 쐐기 단면이 아닌 기울인 직육면체이고, `iron`도 얇은 기울인 직육면체다. 양끝 `grip`·`toe`의 둥근 부분은 UV sphere이며 전체는 X축으로 90° 눕혔다. 실제 날 입구나 절삭·고정 기능까지 구현·검증한 모델이 아니라 양식화한 정물 소품이다.

[기하 감사](https://github.com/Hagazzusa/for-dots/blob/2e2630e40f859b56c0505b1e4fd1e44420b07525/mended-corner/geometry_audit.json)는 메시 닫힘과 좌판 접촉 등을 확인하지만 대패로 읽히는지는 확인하지 않는다. **소스의 부품 이름은 시각적 단서를 대신하지 않는다.** 다음에는 작은 화면에서도 기능을 암시하는 부위의 실루엣이 남는지, 단순화하면서 그 단서가 사라지지 않았는지 본다.

## 빈 잔과 차가 들어 있는 잔 구분하기

이 장면에서 확인할 상태는 **빈 잔 / 차가 들어 있는 잔**이다. [The Second Cup 최종 렌더](https://github.com/Hagazzusa/for-dots/blob/2e2630e40f859b56c0505b1e4fd1e44420b07525/second-cup/renders/the_second_cup_final.png)에서는 가까운 왼쪽 아래 잔의 호박색 액면과 맞은편 오른쪽 잔의 밝은 내벽·바닥이 단서다.

[소스 152–179행](https://github.com/Hagazzusa/for-dots/blob/2e2630e40f859b56c0505b1e4fd1e44420b07525/second-cup/build.py#L152-L179)은 컵 공동·바닥과 별도 액체 체적·액면을 만들며, [기하 감사](https://github.com/Hagazzusa/for-dots/blob/2e2630e40f859b56c0505b1e4fd1e44420b07525/second-cup/geometry_audit.json)는 실제 메시 raycast로 내부·바닥·벽을 확인하고 액체가 한 잔에만 있는지도 검사한다. 이것과 최종 시점·조명·축소 화면에서 두 상태가 읽히는지는 별개다.

[공개 뷰어](https://github.com/Hagazzusa/for-dots/blob/2e2630e40f859b56c0505b1e4fd1e44420b07525/second-cup-viewer/README.md)는 불투명 호박색 차 근사이며 Cycles와 외관이 같지 않다. 경계점 투영 등의 assertion 통과도 모든 각도의 판독성을 보증하지 않는다. [차 재질 연구](https://github.com/Hagazzusa/for-dots/blob/2e2630e40f859b56c0505b1e4fd1e44420b07525/tea-material-study/REPORT.md)는 밝은 내벽·바닥이 드러나는지를 물었고, 높은 시점에서 내부 명암은 일부 개선됐지만 바닥 윤곽의 판독이 부족해 통합을 보류했다. 픽셀이 달라졌거나 해시 검사가 통과했다는 사실을 목표 달성으로 바꾸어 말하지 않는 사례다.

## 움직임과 효과를 채택하는 기준

다음은 특정 실험의 공개 결과가 아니라 다음 제작에 적용할 기준이다. 팔의 좌표가 바뀌는 것과 손이 히터를 향하는 동작으로 읽히는 것은 다르다. 김서림의 alpha나 프레임 차이가 생기는 것과 창의 공간관계·온기를 전달하는 것도 다르다. 의미가 읽히지 않으면 강도를 계속 높이기보다 구도·가림·방향을 다시 보고, 채택하지 않을 수 있다.

[Second Cup 영상 기록](https://github.com/Hagazzusa/for-dots/blob/2e2630e40f859b56c0505b1e4fd1e44420b07525/second-cup-film/README.md)도 은은한 초점 이동을 시선 유도의 보장으로 쓰지 않으며, 재생 검토를 표본 구간 관찰로 한정한다. 다음 작업에서는 [체크리스트](CHECKLIST.md)에 의도·보이는 근거·남은 한계를 함께 남긴다.
