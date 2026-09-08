# 0.2.6 RC1

사용자가 test17에서 공격 정상화 및 투명벽 축소를 확인했다.
해당 스켈레톤/외형/충돌은 바이트 단위로 보존한다.

진단 함수와 메뉴 2개, 테스트 Idle 실행, 카운터, Debug.Trace를 제거한다.
이전 세이브의 구형 씬 정리는 마이그레이션 동작이므로 유지한다.
기존 FormID 및 사용하지 않는 구형 퀘스트/씬 레코드는 삭제하지 않는다.

사용자 요청에 따라 공격력은 도그밋 기준으로 변경한다.
Fallout4.esm의 DogmeatRace UNWP는 000C2C2B UnarmedDogmeat,
일반 ATKD 배율 1.0, 강공격 1.5와 2.0이다.
도로롱의 PRPS UnarmedDamage 100은 0으로 바꾸고 기존 세이브도 Setup에서 정리한다.
DoroRace UNWP는 도그밋 무기로 변경. 따라서 원래 야오과이 무기의 부가 효과도 사라진다.
도그밋 무기를 참조하므로 해당 무기를 수정하는 다른 모드의 영향도 받는다.

NPC 공격 데이터의 템플릿 상속 비트 0x800 및 TPTA 공격 항목을 해제하고
ATKR을 DoroRace로 연결한다. 그 외 템플릿은 유지한다.
DoroRace의 20개 공격 이벤트/확률/플래그/거리/각도는 그대로 두고 피해 배율만 변경한다.
일반 1, 강공격 1.5, 회전 플래그가 있는 강공격 2, 특수 저피해 공격 0.1.
이는 도그밋의 피해 범위를 야오과이 동작에 대응시킨 것이며 완전한 DPS 동일화는 아니다.

기존 PC Level Mult 1.0, 최소 1은 유지하고 최대 100 → 65535로 변경한다.
Auto-calc stats를 추가로 켜거나 별도 레벨별 공격력을 부여하지 않는다.
레벨과 실제 피해의 기존 세이브 적용은 게임 검증 대상이다.

빌드: build_release_026.py --prepare → Papyrus 컴파일(build/release026_compile)
→ build_release_026.py --package 0.
원본은 사용자 검증 test17 ZIP. 검증 보고서와 SHA256은 출력 ZIP에 포함한다.
전체 자산을 다시 내보내지 않으며 공개 업로드/커밋/푸시는 하지 않는다.

레코드 필드 해석은 로컬 원본 Fallout4.esm과 TES5Edit의
Core/wbDefinitionsFO4.pas(dev-4.1.5) ACBS/ATKD/WEAP 정의를 대조했다.
메뉴/스크립트 정리와 밸런스 변경 후 인게임 테스트 전이므로 RC1로 표시한다.
