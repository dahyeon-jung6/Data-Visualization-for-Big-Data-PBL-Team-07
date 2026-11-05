"""2025 국민여행조사 해외여행 소비지출 Streamlit 대시보드.
실행: streamlit run streamlit_app.py
업로드: 2025_해외여행_EDA_결과.xlsx (시트: 분석용데이터)
"""
from io import BytesIO
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='2025 해외여행 소비지출 분석', page_icon='✈️', layout='wide')

AGE = {1:'15~19세', 2:'20대', 3:'30대', 4:'40대', 5:'50대', 6:'60대', 7:'70세 이상'}
INCOME = {1:'100만원 미만',2:'100~200만원 미만',3:'200~300만원 미만',4:'300~400만원 미만',5:'400~500만원 미만',6:'500~600만원 미만',7:'600만원 이상'}
METRICS = {'1인당 평균 여행지출액 (만원)':'cost', '평균 숙박일수 (박)':'nights', '하루당 평균 지출액 (만원/일)':'daily'}
REQUIRED = {'ID','BAGE','BINC1','O_TRA1_ONE_COST','O_TRA1_S_Day','WT_OVER'}

st.title('✈️ 2025년 해외여행 소비지출 대시보드')
st.caption('국민여행조사 해외여행 원자료 · 첫 번째 해외여행 기록 · 조사 가중치 WT_OVER 적용')
st.info('연구 주제: 연령대 및 가구소득 수준에 따른 해외여행 소비지출 차이 분석')

with st.expander('데이터 정의와 분석 시 주의사항', expanded=False):
    st.markdown('''
    - **분석 범위:** 업로드한 EDA 데이터의 유효한 첫 번째 해외여행 지출 기록. 전체 해외여행 경험자 또는 전체 국민의 평균과 동일하지 않을 수 있습니다.
    - **가중평균:** `WT_OVER`를 가중치로 사용하며, 표본 수(n)는 가중하지 않은 실제 관측 건수입니다.
    - **하루당 지출:** 여행 지출액 ÷ (`O_TRA1_S_Day` + 1), 즉 숙박일수 기반 근사치입니다.
    - **표본 30건 미만:** 히트맵에서 감추도록 설정할 수 있습니다. 30건은 통계적 신뢰성의 보장 기준이 아닙니다.
    - **통계적 해석:** 그래프는 기술통계로, 유의확률·신뢰구간을 새로 계산하지 않습니다. 기존 WLS 검정은 복합표본의 모든 설계 요소를 반영하지 않은 탐색적 결과입니다.
    ''')

uploaded = st.file_uploader('EDA 결과 엑셀 파일 업로드 (분석용데이터 시트)', type=['xlsx'])
if uploaded is None:
    st.warning('먼저 `2025_해외여행_EDA_결과.xlsx` 파일을 업로드하세요. 요약표만 포함된 여행기간분석 파일은 사용할 수 없습니다.')
    st.stop()

@st.cache_data(show_spinner='데이터를 읽는 중...')
def load_data(file_bytes):
    frame = pd.read_excel(BytesIO(file_bytes), sheet_name='분석용데이터', engine='openpyxl')
    missing = REQUIRED.difference(frame.columns)
    if missing:
        raise ValueError('엑셀에서 필요한 변수가 없습니다: ' + ', '.join(sorted(missing)))
    for col in ('BAGE', 'BINC1', 'O_TRA1_ONE_COST', 'O_TRA1_S_Day', 'WT_OVER'):
        frame[col] = pd.to_numeric(frame[col], errors='coerce')
    frame = frame.loc[
        frame['BAGE'].isin(AGE) & frame['BINC1'].isin(INCOME)
        & frame['O_TRA1_ONE_COST'].gt(0)
        & frame['WT_OVER'].gt(0) & np.isfinite(frame['WT_OVER'])
    ].copy()
    frame['연령대'] = frame['BAGE'].map(AGE)
    frame['가구소득'] = frame['BINC1'].map(INCOME)
    frame['cost'] = frame['O_TRA1_ONE_COST'] / 10000
    frame['nights'] = frame['O_TRA1_S_Day']
    frame['daily'] = np.where(frame['nights'].ge(0),frame['cost']/(frame['nights']+1),np.nan)
    return frame

try:
    data = load_data(uploaded.getvalue())
except Exception as exc:
    st.error(f'파일을 읽지 못했습니다: {exc}')
    st.stop()

if data.empty:
    st.error('필터 전 유효한 첫 여행 지출 자료가 없습니다.')
    st.stop()

st.sidebar.header('🔎 분석 필터')
ages = st.sidebar.multiselect('연령대', list(AGE.values()), default=list(AGE.values()))
incomes = st.sidebar.multiselect('월평균 가구소득', list(INCOME.values()), default=list(INCOME.values()))
valid_nights = data['nights'].dropna()
max_nights = max(1, int(valid_nights.max())) if not valid_nights.empty else 1
nights_range = st.sidebar.slider('숙박일수 (박)', 0, max_nights, (0, max_nights))
metric_label = st.sidebar.selectbox('차트 비교 지표', list(METRICS))
metric = METRICS[metric_label]
suppress_small = st.sidebar.checkbox('히트맵에서 표본 30건 미만 숨기기', value=True)

filtered = data.loc[
    data['연령대'].isin(ages) & data['가구소득'].isin(incomes)
    & data['nights'].between(*nights_range)
].copy()

if filtered.empty:
    st.warning('선택한 조건에 해당하는 데이터가 없습니다. 필터 범위를 넓혀 주세요.')
    st.stop()

# Each metric averages only records with a valid value and a positive weight.
def weighted_average(frame, col):
    valid = frame.loc[np.isfinite(frame[col]) & np.isfinite(frame['WT_OVER']) & frame['WT_OVER'].gt(0)]
    if valid.empty:
        return float('nan')
    return float(np.average(valid[col], weights=valid['WT_OVER']))

def group_summary(frame, cols, value):
    rows=[]
    for key, sub in frame.groupby(cols, observed=True, sort=False):
        keys=(key,) if isinstance(cols,str) else key
        r=dict(zip([cols] if isinstance(cols,str) else cols, keys))
        r.update({'표본 수':len(sub), '가중평균':weighted_average(sub,value)})
        rows.append(r)
    return pd.DataFrame(rows)

st.subheader('핵심 지표')
cols=st.columns(4)
cols[0].metric('표본 수 (n)', f'{len(filtered):,}명')
cols[1].metric('1인당 가중평균 지출', f"{weighted_average(filtered,'cost'):,.1f}만원")
cols[2].metric('가중평균 숙박일수', f"{weighted_average(filtered,'nights'):.2f}박")
cols[3].metric('가중평균 하루당 지출', f"{weighted_average(filtered,'daily'):.1f}만원")

age_summary=group_summary(filtered,'연령대',metric)
income_summary=group_summary(filtered,'가구소득',metric)
night_data=filtered.copy()
night_data['숙박구간']=pd.cut(night_data['nights'], bins=[-0.1,0,2,4,6,9,float('inf')], labels=['0박','1~2박','3~4박','5~6박','7~9박','10박 이상'])
night_summary=group_summary(night_data,'숙박구간',metric)

left,right=st.columns(2)
with left:
    st.subheader('연령대별 비교')
    if not age_summary.empty:
        fig=px.bar(age_summary,x='연령대',y='가중평균',text='가중평균',hover_data=['표본 수'],category_orders={'연령대':list(AGE.values())},labels={'가중평균':metric_label})
        fig.update_traces(texttemplate='%{text:.1f}',textposition='outside')
        fig.update_layout(template='plotly_white',showlegend=False)
        st.plotly_chart(fig,use_container_width=True)
with right:
    st.subheader('월평균 가구소득별 비교')
    if not income_summary.empty:
        fig=px.bar(income_summary,x='가구소득',y='가중평균',text='가중평균',hover_data=['표본 수'],category_orders={'가구소득':list(INCOME.values())},labels={'가중평균':metric_label})
        fig.update_traces(texttemplate='%{text:.1f}',textposition='outside')
        fig.update_layout(template='plotly_white',xaxis_tickangle=-35,showlegend=False)
        st.plotly_chart(fig,use_container_width=True)

st.subheader('숙박기간별 비교')
if not night_summary.empty:
    fig=px.line(night_summary,x='숙박구간',y='가중평균',markers=True,hover_data=['표본 수'],category_orders={'숙박구간':['0박','1~2박','3~4박','5~6박','7~9박','10박 이상']},labels={'가중평균':metric_label})
    fig.update_layout(template='plotly_white')
    st.plotly_chart(fig,use_container_width=True)

st.subheader('연령 × 소득 교차 비교')
cross=group_summary(filtered,['연령대','가구소득'],metric)
if not cross.empty:
    heat=cross.pivot(index='연령대',columns='가구소득',values='가중평균').reindex(index=list(AGE.values()),columns=list(INCOME.values()))
    counts=cross.pivot(index='연령대',columns='가구소득',values='표본 수').reindex(index=list(AGE.values()),columns=list(INCOME.values())).fillna(0)
    if suppress_small:
        heat=heat.where(counts>=30)
    fig=px.imshow(heat,text_auto='.1f',aspect='auto',color_continuous_scale='Blues',labels={'x':'가구소득','y':'연령대','color':metric_label})
    fig.update_layout(template='plotly_white',xaxis_tickangle=-35)
    st.plotly_chart(fig,use_container_width=True)
    n_small=int((counts<30).sum().sum())
    st.caption(f'선택된 필터에서 표본 30건 미만인 교차집단: {n_small}개 (49개 조합 기준). 표본이 없는 집단은 원래 비어 있습니다.')

st.subheader('집계 결과 다운로드')
report_tabs=st.tabs(['연령대별','가구소득별','숙박기간별','연령×소득'])
for tab, table in zip(report_tabs,[age_summary,income_summary,night_summary,cross]):
    with tab:
        st.dataframe(table.round(2),use_container_width=True,hide_index=True)
        st.download_button('CSV 다운로드',data=table.to_csv(index=False).encode('utf-8-sig'),file_name='2025_해외여행_'+str(['연령대','가구소득','숙박기간','연령소득'][report_tabs.index(tab)])+'_집계.csv',mime='text/csv',key='download_'+str(report_tabs.index(tab)))

st.caption('자료: 2025년 국민여행조사 해외여행 원자료. 본 대시보드는 기술통계 탐색 용도로 제작되었습니다.')
