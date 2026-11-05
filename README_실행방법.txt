2025 국민여행조사 해외여행 소비지출 대시보드

준비물: 2025_해외여행_EDA_결과.xlsx (분석용데이터 시트 포함)

1) 컴퓨터에서 실행
- streamlit_app.py와 requirements.txt를 같은 폴더에 저장
- 터미널에서: pip install -r requirements.txt
- 이어서: streamlit run streamlit_app.py
- 브라우저에 열린 화면에서 EDA 결과 엑셀 업로드

2) Streamlit Community Cloud 배포
- streamlit_app.py와 requirements.txt를 GitHub 저장소에 업로드
- Streamlit Community Cloud에서 저장소와 streamlit_app.py를 선택해 배포
- 데이터 업로드 방식이므로 자료를 코드에 포함하지 않아도 됨

참고
- 현재 대시보드는 단일 1차 해외여행 기록에 대한 가중 기술통계 뷰어입니다.
- 원본 엑셀 파일을 공개 GitHub 저장소에 올리지 마세요.
- 기간 변수를 숙박일수로 보고 하루당 지출액은 지출액/(숙박일수+1)로 근사 계산합니다.
