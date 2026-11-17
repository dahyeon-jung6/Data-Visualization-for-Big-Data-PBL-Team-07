# 방문국가에 따른 해외여행 기간과 소비지출 관계 — 논문 그림

「방문국가에 따른 해외여행 기간과 소비지출 관계의 차이 분석: 2025년 국민여행조사를 중심으로」(ICT플랫폼학회)에 쓰이는 그림과 그림 생성 코드입니다.
일본은 **흰 바탕 + 붉은 원(히노마루)**, 베트남은 **붉은 바탕 + 노란 별**로 표현했습니다. 두 국기의 붉은색이 거의 같으므로 색이 아니라 채움(흰색/붉은색)과 마커 모양(원/별)으로 구분합니다(흑백 인쇄·색각 이상에서도 구분됨).

## 그림
| 파일 | 내용 |
|---|---|
| `figures/fig1_days_flag.png/.pdf` | 그림 1. 여행일수별 평균 지출(a)과 표본 수(b) |
| `figures/fig2_elasticity_flag.png/.pdf` | 그림 2. 여행기간 탄력성과 95% 신뢰구간 |
| `figures/fig3_category_flag.png/.pdf` | 그림 3. 소비 카테고리별 지출 (전체 / 개별여행) |

PNG는 300dpi, PDF는 벡터본입니다.

## 코드
`code/colab_flag_viz.py` — Google Colab에서 기존 분석 셀 다음에 실행합니다.
- 필요한 변수: `source`(원자료 xlsx 경로), `OUT`(저장 폴더), `comparison`(열: `country`, `days`, `w`, `cost`)
- `PAPER = True`(논문용) / `False`(발표용 큰 크기)
- 한글 글꼴: `!apt-get -qq install fonts-nanum` 후 런타임 재시작
- 그림 2는 논문 표 2의 추정값(`ELASTICITY`)을 직접 입력해 사용합니다.

## 데이터
`data/category_expense_summary.csv` — 카테고리별 가중평균 지출(만원) 요약.
원자료(2025 국민여행조사)는 이 저장소에 포함하지 않았습니다. 한국문화관광연구원 이용 조건에 따라 직접 내려받아 사용하세요.
