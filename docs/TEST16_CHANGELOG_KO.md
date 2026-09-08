# test16 — 2026-09-08

사용자 인게임 대조 결과: test15A는 공격하지 않고 서 있음. test15B는 적극적으로 공격함. A/B의 ESP 차이는 DoroRace 남녀 높이 0.42/1.0뿐이었다. 이 결과는 해당 조건에서 크기 설정이 공격 행동을 바꾼다는 근거이며, 충돌 캡슐이 직접 원인이라는 증명은 아니다.

test16은 공격이 확인된 B의 Race height=1.0과 전투 코드를 보존하고, 배치 참조 0100080B의 XSCL 및 Setup의 SetScale을 0.42로 바꾼 비교본이다. UI2의 숫자 ID 진단창을 포함하며 제목은 test16, 현재 scale도 표시한다. 의상·스켈레톤·모델·음성·레시피는 변경하지 않았다.

설치 시 기존 A/B 및 UI2 패치를 끄고 test16 하나만 활성화한다. UI2 스크립트가 덮어쓰면 scale을 1.0으로 되돌리므로 함께 활성화하지 않는다. 같은 원본 테스트 세이브에서 작은 크기, 공격/타격, 투명벽, 문 통과를 확인한다. 실패하면 test16 상태창으로 현재 배율과 전투 상태를 확인한다.

컴파일 성공, 43개 레코드와 기존 FormID 유지, B 대비 ESP의 유일한 변경이 ACHR XSCL인 것을 확인했다. 자산 바이트 동일성과 ZIP/manifest 검증도 통과했다. 게임에서 작은 크기로 공격하는지는 아직 확인 전이다.

재현: tools/build_test16.py --prepare → Papyrus 컴파일 출력 build/test16_compile → tools/build_test16.py --package. 이전 버전 prepare/package 도구로 현재 산출물을 재생성하지 않는다.

패키징 사고 기록: 최초 실행에서 Path.with_suffix 사용으로 파일명이 잘려 build/DoroFollower_FO4_test_0.2.zip에 test16 데이터가 기록되었다. 옛 0.2 ZIP은 덮어써졌고 검색한 데스크톱/MO2 다운로드 경로에서 같은 이름의 백업은 찾지 못했다. 해당 파일은 혼동 방지를 위해 build/test16_packaging_misnamed_copy.zip으로 옮겼다. 설치본과 test14/test15 ZIP은 변경하지 않았다. 빌더는 전체 폴더명에 .zip을 붙이도록 수정했고 올바른 test16 이름으로 재생성·검증했다.
