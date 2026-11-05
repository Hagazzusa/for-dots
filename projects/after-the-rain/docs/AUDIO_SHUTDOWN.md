# 오디오 종료 준비

## 관찰된 문제

Godot 4.6.3 / Dummy 드라이버의 작은 독립 실험에서, 합성 무음 WAV 두 개를 재생한 뒤 `stop()`, `stream=null`, `queue_free()`를 실행해도 Playback과 WAV 약한 참조가 즉시 사라지지 않았습니다. 12회 모두 중지 직후 각각 두 개가 살아 있었습니다.

| 조건 · 각 3회 | 잔류 경고 | 관찰 후 종료 |
|---|---:|---|
| 시작 직후 중지·즉시 quit | 2/3회 | 해당 없음 |
| 믹싱 갱신 확인 후 중지·즉시 quit | 3/3회 | 해당 없음 |
| 시작 직후 중지·실제 해제 관찰 | 0/3회 | 중지 후 90.4–97.4ms |
| 믹싱 갱신 확인 후 중지·실제 해제 관찰 | 0/3회 | 중지 후 99.5–103.8ms |

고정 sleep이나 경고 필터 없이 프레임 경계에서 약한 참조의 소멸을 확인했습니다. 이 수치는 다른 드라이버의 안전한 대기시간이 아닙니다. 게임의 모든 간헐 종료 경고를 같은 원인으로 확정하거나 실제 청취/오디오 품질을 검사한 결과도 아닙니다.

## 책임과 종료 흐름

- 저장된 `AppShutdown` 노드는 현재 메인 장면일 때만 창 닫기 요청을 받습니다. 같은 씬을 테스트나 다른 장면에 삽입해도 앱의 닫기 정책을 임의로 바꾸지 않습니다.
- 세션은 종료 준비 명령을 주입합니다. 종료 요청은 한 번만 수락하며, 새 플레이어 입력과 게임 갱신을 멈춥니다. 기존 일시 정지 상태에서도 종료 조정자는 처리됩니다.
- Ambience, 라디오, 차 히터는 각자 활성 Playback의 약한 참조를 모은 뒤 재생을 중지하고 스트림을 비운 뒤 오디오 노드 해제를 예약합니다. 3D 플레이어의 내부 대기 재생 참조도 노드 해제와 함께 놓도록 하기 위함입니다. 종료 상태에서는 자기 API로 새 재생을 시작하지 않습니다.
- 조정자는 Playback 참조가 실제 해제되면 quit합니다. 캐시가 참조할 수 있는 WAV 해제를 조건으로 삼지 않습니다. 기본 2초의 실시간 진단 한도를 넘으면 남은 개수를 경고하고 종료합니다. 무한 대기나 반복 닫기에 따른 기한 연장은 없습니다.
- 정상 플레이·일시 정지·재시작에는 이 대기 흐름을 넣지 않습니다. 테스트에서 고의로 유지한 참조도 제한 시간 뒤 종료 콜백에 도달하는지 확인합니다.

이 경로는 단일 메인 장면의 정상 창 닫기 요청을 대상으로 합니다. 기존 메인 장면을 살려둔 채 current_scene만 교체하는 범용 장면 전환 관리자는 아닙니다. OS 강제 종료, 프로세스 kill, 엔진의 강제 종료 플래그, 다른 드라이버/새 엔진까지 보편적으로 경고를 없앤다는 보장은 아닙니다. 이미 player에서 분리된 과거 playback을 모든 상황에서 열거한다는 주장도 하지 않습니다.

## 작은 재현 스크립트

프로젝트 폴더에서 다음 명령을 실행할 수 있습니다. 외부 오디오 파일이나 녹음을 사용하지 않습니다. `immediate` 조건은 의도적으로 종료 경고를 재현할 수 있으므로 일반 회귀 묶음에 자동으로 넣지 않았습니다.

```
godot --headless --audio-driver Dummy --verbose --path . --script tools/diagnostics/audio_lifetime_probe.gd -- immediate
godot --headless --audio-driver Dummy --verbose --path . --script tools/diagnostics/audio_lifetime_probe.gd -- drain
godot --headless --audio-driver Dummy --verbose --path . --script tools/diagnostics/audio_lifetime_probe.gd -- immediate warmed
godot --headless --audio-driver Dummy --verbose --path . --script tools/diagnostics/audio_lifetime_probe.gd -- drain warmed
```

`warmed`는 믹싱 시간의 갱신을 먼저 관찰합니다. `drain`의 2초 한도는 진단이 무한히 계속되지 않도록 할 뿐, 그 시간만큼 항상 기다리는 방식이 아닙니다. 원시 실험 로그는 프로젝트에 포함하지 않습니다.

## 엔진 근거

4.6.3의 `AudioStreamPlayerInternal::stop_basic`은 서버에 중지를 요청하고 자체 playback 목록을 비웁니다. AudioServer는 fade-out-to-deletion 뒤 주 스레드의 지연 정리에서 참조를 해제합니다. PlaybackWAV는 원본 WAV를 참조합니다. AudioStreamPlayer3D는 play에서 별도의 setplayback 참조를 저장하며 stop만으로 비우지 않으므로 종료 준비에서 노드도 해제합니다.

- [AudioStreamPlayer 내부](https://github.com/godotengine/godot/blob/4.6.3-stable/scene/audio/audio_stream_player_internal.cpp)
- [AudioServer](https://github.com/godotengine/godot/blob/4.6.3-stable/servers/audio/audio_server.cpp)
- [AudioStreamPlayer3D](https://github.com/godotengine/godot/blob/4.6.3-stable/scene/3d/audio_stream_player_3d.cpp)
- [AudioStreamWAV](https://github.com/godotengine/godot/blob/4.6.3-stable/scene/resources/audio_stream_wav.cpp)

## 통합 검증

- 최종 코드 전체 회귀 묶음 46개가 통과했습니다. 새 종료 검사는 정상·일시 정지·이미 무음인 게임, 중복 요청, 새 재생 차단, 빈 오디오 목록, 고의로 유지한 참조의 timeout, 비유한 설정의 유한 기한 보정을 포함한 41개 검사를 통과했습니다. timeout 검사 한 번의 경고는 의도한 진단 출력이며 판정에서 오류를 숨기는 필터를 추가하지 않았습니다.
- 격리 PCK는 런타임 파일 186개로 빌드·일반 시작·소스 테스트 플래그 검증을 통과했습니다. 진단 재현 도구와 테스트 픽스처는 PCK에 포함하지 않습니다.
- 네이티브 Compatibility/Dummy 실행에서 일반 시작 후 Space로 일시 정지하고 창의 닫기 버튼을 눌렀습니다. 종료 완료 신호가 timeout=false, 남은 Playback=0을 보고했고 창이 사라졌습니다. 그 실행의 종료 리소스 잔류나 스크립트 오류는 없었습니다. 드라이버의 기존 V-Sync 미지원 경고는 별개이며 실제 소리를 듣고 평가한 검증은 아닙니다.
