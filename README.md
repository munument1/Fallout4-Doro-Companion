# Fallout Doro Companion

Fallout 4용 도로롱 독립 동료와 플레이어 머리 탈을 개발하는 작업 저장소입니다.

현재 상태는 **0.2.4 테스트 버전 작업 중**입니다. 게임에서 외형은 표시되지만 대화가 시작되지 않는 문제가 남아 있습니다. 완성된 배포판이 아닙니다.

- 레드 로켓 주유소에서 만나는 별도 동료
- 야오과이 뼈대와 애니메이션을 사용하고 도그밋 정도의 크기로 조정
- 원래의 닫힌 입 모양 유지
- 도그밋 및 다른 동료와 함께 다니는 독립 영입 방식 지향
- 플레이어용 도로롱 머리 탈: 화학작업대 무료 제작 지향

## 저장 범위

`tools/`에는 Python 제작·검사 도구와 Papyrus 소스를 보관합니다. 초기 실험 및 이전 버전 도구도 포함되므로 모든 스크립트가 최신 빌드 절차는 아닙니다.

게임에서 추출한 자산, 참고 모드 원본, 변환된 모델·텍스처·음성, Blender 작업 파일, 빌드 ZIP, 외부 라이브러리는 이 공개 저장소에 포함하지 않습니다. 해당 파일은 기존 로컬 작업 폴더에 남아 있습니다. 따라서 이 저장소만으로 완전한 모드를 빌드할 수는 없습니다.

## 주요 소스

- `tools/build_doro_plugin.py`: 동료 플러그인 생성
- `tools/doro_dialogue.py`: 대화 퀘스트·씬·토픽 생성
- `tools/DoroCompanionScript.psc`: 영입 상태·추적·전투 지원
- `tools/DoroDialogueQuestScript.psc`: 대화 단계별 명령 전달
- `tools/build_costume_plugin.py`: 의상 제작 레코드 생성
- `tools/build_costume_meshes.py`: 의상 모델 변환

개발 환경은 Windows, Blender 5.2.1, PyNifly 28.2, Fallout 4 및 Creation Kit의 Papyrus 컴파일러입니다. 일부 도구에 로컬 절대 경로가 있으며 다른 환경에서는 수정이 필요합니다. `build/gorilla_records.json` 등 로컬 추출 데이터와 `tools/deps/`의 외부 의존성도 별도로 필요합니다.

자세한 현황과 다음 확인 사항은 [작업 기록](docs/STATUS.md)을 참고하세요.
