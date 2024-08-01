# RFP 파일 처리 및 제안서 생성기

이 프로젝트는 RFP(Request For Proposal) 파일을 업로드하여 변환된 텍스트를 미리보고, 변환된 텍스트를 다운로드하거나 제안서를 생성할 수 있는 웹 애플리케이션입니다.

## 기능

- **RFP 파일 업로드**: 사용자는 `.hwp` 파일을 업로드하여 텍스트로 변환할 수 있습니다.
- **미리보기**: 변환된 텍스트의 앞 500자와 끝 500자를 미리 볼 수 있으며, 중간 부분은 중략 처리됩니다.
- **텍스트 다운로드**: 변환된 텍스트를 `.txt` 파일로 다운로드할 수 있습니다.
- **제안서 생성기**: 제안서 생성을 위한 사용자 정의 입력 양식을 제공하며, 생성된 제안서를 `.pptx` 파일로 다운로드할 수 있습니다.
- **전시연출총괄표 생성기**: 사용자 정의 입력을 통해 엑셀 파일로 전시연출총괄표를 생성할 수 있습니다.

## 설치 및 실행

### 1. 리포지토리 클론