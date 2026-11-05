# 글꼴 출처와 재현 조건

SVG의 모든 문자는 `Noto Sans CJK KR, sans-serif`로 지정했다. 제작 환경의 Fontconfig 조회에서 실제 선택된 파일은 `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc`, 패밀리는 **Noto Sans CJK KR**, 스타일은 **Regular**였다. 08에 지정한 `font-weight="300"`도 이 환경에서는 설치된 Regular 스타일로 대체된다. 얇은 웨이트가 설치된 다른 환경은 숫자 굵기가 달라질 수 있다.

설치된 `fonts-noto-cjk` 패키지의 저작권 기록을 확인했다.

- 원본 프로젝트: https://github.com/notofonts/noto-cjk
- 글꼴 라이선스: **SIL Open Font License 1.1**
- 패키지에 기재된 글꼴 저작권: 2010–2012, Google Corporation
- 확인 근거: 제작 환경의 `/usr/share/doc/fonts-noto-cjk/copyright`, `Files: *` 항목. Debian 패키징 코드의 별도 라이선스와 글꼴 라이선스는 구분했다.

이 작품 폴더에는 글꼴 파일을 복사하거나 임베드하지 않았다. PNG는 렌더된 그림이며 별도 글꼴 설치가 필요 없다. SVG는 문자를 편집 가능하게 유지했으며, Noto Sans CJK KR이 없으면 일반 sans-serif로 대체된다. 한글을 지원하지 않는 대체 글꼴에서는 글자가 네모로 보이거나 누락될 수 있고, 글자 폭·행 위치·굵기가 달라질 수 있다.

재현하려면 Noto Sans CJK KR Regular와 Inkscape를 준비한 뒤 `bash render.sh`를 실행한다. 원본을 보고 수정하려면 `next_stop.svg`, 동일한 완성 외관을 보려면 `next_stop.png`를 사용한다.
