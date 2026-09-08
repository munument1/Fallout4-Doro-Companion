# 0.2.6 RC2 — RC1 전투 회귀 복원

사용자는 처음 test17을 실행해 구형 메뉴를 봤다고 정정했고, RC1에서는 메뉴가
정상이나 전투를 하지 않는다고 확인했다. 따라서 메뉴 정리는 적용됐으며 RC1 전투
변경 중 무엇이 회귀를 일으켰는지는 아직 분리되지 않았다.

RC2는 test17을 기준으로 구성한다. RACE 전체, 공격 무기, ATKR, TPTA,
공격 데이터 템플릿 비트, PRPS 공격력은 test17과 동일하다.
ESP 차이는 MESG 2개 진단 버튼 제거와 ACBS 최대 레벨 100→65535뿐이다.
모든 모델/스켈레톤/충돌/의상/음성은 test17과 바이트 단위 동일하다.
전투 함수 7개의 코드도 진단 로그/카운터를 제외하면 test17과 동일함을 검사한다.

RC1에서 SetValue로 남긴 UnarmedDamage 0을 복구하기 위해 최초 Setup에서
기본값이 0인 경우 100으로 복원하고 migration 완료 플래그를 저장한다.
메뉴/진단 제거와 플레이어 레벨 1배 연동/상한 해제는 유지한다.

Papyrus 컴파일, 레코드/자산/전투 코드 비교, ZIP 및 매니페스트 검사 통과.
RC2 인게임 검증은 남아 있다. 우선 test17 정상 세이브에서 확인하고,
RC1 저장 세이브의 복구 여부는 별도로 확인한다. 세이브 삭제를 요구하지 않는다.

빌드: build_release_026_rc2.py --prepare → release026_rc2_compile 폴더로
Papyrus 컴파일 → build_release_026_rc2.py --package.
출력: build/DoroFollower_FO4_0.2.6_RC2.zip.
