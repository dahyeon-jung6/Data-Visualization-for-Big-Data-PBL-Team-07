
from pathlib import Path
import json
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(
    page_title="해외여행 기간과 소비지출",
    page_icon="✈️",
    layout="wide"
)

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"

# ── 국기 모티프 팔레트 ─────────────────────────────────────────
# 일본: 흰 바탕 + 붉은 원(히노마루) / 베트남: 붉은 바탕 + 노란 별
# 두 국기의 붉은색이 거의 같으므로 색이 아니라 채움(흰색/붉은색)과
# 마커 모양(원/별)으로 구분한다. (흑백 인쇄·색각 이상에서도 구분됨)
JP_RED = "#BC002D"
VN_RED = "#DA251D"
VN_YELLOW = "#FFCD00"
VN_EDGE = "#8E1710"
INK = "#222222"
SUB = "#6B6B6B"
PANEL_BG = "#F6F4F1"

STYLE = {
    "일본": {
        "color": JP_RED,
        "text": JP_RED,
        "symbol": "circle",
        "dash": "solid",
        "fill": "#FFFFFF",
        "marker_fill": JP_RED,
        "marker_line": "#FFFFFF",
    },
    "베트남": {
        "color": VN_RED,
        "text": VN_EDGE,
        "symbol": "star",
        "dash": "dash",
        "fill": VN_RED,
        "marker_fill": VN_YELLOW,
        "marker_line": VN_EDGE,
    },
}
SMALL_N = 30  # 표본이 이보다 적으면 † 표시


def style_fig(fig, height):
    fig.update_layout(
        plot_bgcolor=PANEL_BG,
        paper_bgcolor="white",
        height=height,
        font=dict(color=INK),
        margin=dict(t=25, b=50),
    )
    fig.update_xaxes(gridcolor="white", gridwidth=1.5, zeroline=False,
                     linecolor="#BDB8B0", ticks="")
    fig.update_yaxes(gridcolor="white", gridwidth=1.5, zeroline=False,
                     ticks="")
    return fig


def flag_banner():
    """제목 옆에 쓰는 미니 국기(CSS)"""
    st.markdown(
        """
        <div style="display:flex;gap:10px;align-items:center;margin-bottom:4px">
          <div style="width:42px;height:28px;background:#fff;border:2px solid #BC002D;
                      display:flex;align-items:center;justify-content:center;">
            <div style="width:14px;height:14px;border-radius:50%;background:#BC002D"></div>
          </div>
          <div style="width:42px;height:28px;background:#DA251D;border:2px solid #DA251D;
                      display:flex;align-items:center;justify-content:center;
                      color:#FFCD00;font-size:18px;line-height:1">★</div>
          <span style="color:#6B6B6B;font-size:0.9rem">일본 · 베트남</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data():
    duration = pd.read_csv(DATA / "duration.csv")
    models = pd.read_csv(DATA / "models.csv")
    slopes = pd.read_csv(DATA / "slopes.csv")
    sensitivity = pd.read_csv(DATA / "sensitivity.csv")
    meta = json.loads(
        (DATA / "meta.json").read_text(encoding="utf-8")
    )
    return duration, models, slopes, sensitivity, meta

duration, models, slopes, sensitivity, meta = load_data()

flag_banner()
st.title("✈️ 여행기간이 길어질 때, 소비지출은 두 나라에서 같을까?")
st.caption(
    "2025년 국민여행조사 | 일본·베트남 비교 | "
    "ICT플랫폼학회 2026 동계학술대회 연구"
)

st.info(
    "핵심 질문: 일본과 베트남에서 여행기간과 "
    "총지출액의 관계는 어떻게 다르게 나타날까?"
)

c1, c2, c3 = st.columns(3)
c1.metric("전체 유효 기록", f"{meta['n_all']:,}건")
c2.metric("일본·베트남 비교 기록", f"{meta['n_comparison']:,}건")
c3.metric("회귀분석 대상 기간", "3~7일")

st.divider()

selected = st.multiselect(
    "비교할 방문국가를 선택하세요",
    ["일본", "베트남"],
    default=["일본", "베트남"]
)

if not selected:
    st.warning("하나 이상의 국가를 선택해 주세요.")
    st.stop()

shown = duration[duration["country"].isin(selected)]

left, right = st.columns([1.5, 1])

with left:
    st.subheader("① 여행일수별 평균 지출액")
    st.caption(
        "3~6일 · 조사 가중평균 · 단위: 만원"
    )

    fig = go.Figure()

    for country in selected:
        part = shown[
            shown["country"] == country
        ].sort_values("days")

        s = STYLE[country]
        vals = part["mean_cost"] / 10000
        labels = [
            f"{v:.1f}" + ("†" if n < SMALL_N else "")
            for v, n in zip(vals, part["n"])
        ]

        fig.add_trace(go.Scatter(
            x=part["days"],
            y=vals,
            name=country,
            mode="lines+markers+text",
            text=labels,
            textposition=(
                "top center"
                if country == "일본"
                else "bottom center"
            ),
            textfont=dict(color=s["text"], size=13),
            line=dict(
                color=s["color"],
                width=3.5,
                dash=s["dash"]
            ),
            marker=dict(
                color=s["marker_fill"],
                symbol=s["symbol"],
                size=14 if country == "일본" else 20,
                line=dict(color=s["marker_line"], width=2)
            ),
            customdata=part["n"],
            hovertemplate=(
                "여행일수: %{x}일<br>"
                "평균 지출액: %{y:.1f}만원<br>"
                "기록 수: %{customdata}건"
                "<extra></extra>"
            )
        ))

    style_fig(fig, 440)
    fig.update_layout(
        xaxis=dict(
            title="여행일수 (일)",
            dtick=1
        ),
        yaxis=dict(
            title="1인당 평균 지출액 (만원)",
            rangemode="tozero"
        ),
        legend_title_text="방문국가",
    )
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("② 여행일수별 표본 수")
    st.caption("3~6일 · 실제 관측 기록 수")

    fig_n = go.Figure()

    all_days = sorted(shown["days"].unique())
    ymax = float(shown["n"].max()) if len(shown) else 1.0
    offsets = {"일본": -0.19, "베트남": 0.19}

    for country in selected:
        part = shown[
            shown["country"] == country
        ].sort_values("days")

        s = STYLE[country]
        off = offsets[country] if len(selected) > 1 else 0.0
        xs = part["days"] + off

        # 막대: 일본 = 흰 바탕 + 붉은 테두리 / 베트남 = 붉은 바탕
        fig_n.add_trace(go.Bar(
            x=xs,
            y=part["n"],
            width=0.34,
            name=country,
            showlegend=False,
            marker=dict(
                color=s["fill"],
                line=dict(color=s["color"], width=2)
            ),
            hoverinfo="skip"
        ))

        # 막대 위 국기 마커(원/별) + 건수
        fig_n.add_trace(go.Scatter(
            x=xs,
            y=part["n"] + ymax * 0.07,
            name=country,
            mode="markers+text",
            text=part["n"].astype(str),
            textposition="top center",
            textfont=dict(color=INK, size=13),
            marker=dict(
                color=s["marker_fill"],
                symbol=s["symbol"],
                size=13 if country == "일본" else 20,
                line=dict(
                    color=s["marker_line"] if country == "베트남" else s["color"],
                    width=1.5
                )
            ),
            customdata=part["n"],
            hovertemplate=(
                f"{country}<br>"
                "기록 수: %{customdata}건<extra></extra>"
            )
        ))

    style_fig(fig_n, 440)
    fig_n.update_layout(
        xaxis=dict(
            title="여행일수",
            tickmode="array",
            tickvals=all_days,
            ticktext=[f"{int(d)}일" for d in all_days],
            range=[min(all_days) - 0.6, max(all_days) + 0.6]
        ),
        yaxis=dict(
            title="표본 수 (건)",
            range=[0, ymax * 1.35]
        ),
        legend_title_text="방문국가",
    )
    st.plotly_chart(fig_n, use_container_width=True)

st.caption(
    "두 그래프는 3~6일 여행의 집계값입니다. "
    f"†는 표본 {SMALL_N}건 미만으로 평균이 불안정할 수 있음을 뜻합니다. "
    "7일 여행은 국가별 표본 수가 20건 미만이므로 "
    "상세 그래프에서 표시하지 않았습니다."
)

st.divider()

st.subheader("③ 여행기간–지출 탄력성 비교")
st.caption(
    "3~7일 여행 · 연령·가구소득 보정 · "
    "WLS+HC3 탐색적 회귀분석"
)

fig_beta = go.Figure()

for country in selected:
    row = slopes[
        slopes["country"] == country
    ].iloc[0]

    s = STYLE[country]

    fig_beta.add_trace(go.Scatter(
        x=[row["beta"]],
        y=[country],
        mode="markers+text",
        name=country,
        text=[f"{row['beta']:.3f}"],
        textposition="bottom center",
        textfont=dict(color=INK, size=14),
        marker=dict(
            size=17 if country == "일본" else 26,
            color=s["marker_fill"],
            symbol=s["symbol"],
            line=dict(
                color=s["marker_line"] if country == "베트남" else "#FFFFFF",
                width=2
            )
        ),
        error_x=dict(
            type="data",
            symmetric=False,
            array=[row["high"] - row["beta"]],
            arrayminus=[row["beta"] - row["low"]],
            width=8,
            thickness=3,
            color=s["color"]
        ),
        hovertemplate=(
            f"{country}<br>"
            "탄력성: %{x:.3f}<extra></extra>"
        )
    ))

fig_beta.add_vline(
    x=0,
    line_color="#BDB8B0",
    line_width=1
)
fig_beta.add_vline(
    x=1,
    line_dash="dot",
    line_color=SUB,
    annotation_text="비례 관계: 1"
)

style_fig(fig_beta, 350)
fig_beta.update_layout(
    xaxis_title="기간–지출 탄력성 및 95% 신뢰구간",
    yaxis_title="방문국가",
    showlegend=False,
    margin=dict(t=25, b=50, l=60),
)
fig_beta.update_yaxes(autorange="reversed")

st.plotly_chart(fig_beta, use_container_width=True)

st.write(
    "탄력성은 여행일수가 1% 다른 기록에서 "
    "총지출액이 평균적으로 몇 % 다른지를 "
    "나타내는 회귀계수입니다."
)

st.write(
    f"국가별 관계 차이 검정: "
    f"HC3 p-value = {meta['interaction_p']:.3g}"
)

st.warning(
    "이 결과는 인과효과가 아닙니다. "
    "조사 가중치는 적용했지만 층화·집락을 포함한 "
    "완전한 복합표본 설계 기반 추론은 아닙니다."
)

st.divider()

st.subheader("④ 전체 표본 모형 비교")
st.caption(
    "전체 2,295건 · 방문국가 추가 전후 비교"
)

b0 = float(models.iloc[0]["beta"])
b1 = float(models.iloc[1]["beta"])

a, b = st.columns(2)
a.metric("연령·소득 보정", f"{b0:.4f}")
b.metric("방문국가 추가 보정", f"{b1:.4f}")

st.write(
    "방문국가를 추가했을 때 전체 표본의 "
    f"기간 탄력성은 {b0:.4f}에서 {b1:.4f}로 "
    "소폭 변화했습니다. "
    "큰 감소가 나타났다고 해석하지 않습니다."
)

st.divider()

st.subheader("⑤ 기간 범위 민감도 분석")
st.caption(
    "기간을 더 좁게 제한하면 "
    "국가별 차이에 대한 검정 결과도 달라집니다."
)

st.dataframe(
    sensitivity,
    use_container_width=True,
    hide_index=True
)

with st.expander("연구 방법 · 데이터 출처 · 해석 한계"):
    st.markdown("""
    - **자료:** 2025년 국민여행조사 해외여행 원자료
    - **대상:** 첫 번째 해외여행의 유효 지출 기록
    - **방문국가:** 첫 번째 방문국가 기준
    - **분석 방법:** 로그-로그 WLS 회귀분석, HC3 표준오차
    - **가중치:** WT_OVER
    - **국가별 회귀:** 연령·가구소득 보정
    - **통계적 한계:** 복합표본 설계를 완전히 반영하지 않음
    - **해석 범위:** 관찰된 연관성으로 인과적 효과가 아님
    - **시각화:** 3~6일 집계값
    - **국가별 탄력성:** 3~7일 분석값
    """)

poster_path = BASE / "assets" / "poster_core.pdf"

if poster_path.exists():
    st.download_button(
        "📄 포스터 핵심 그래프 PDF",
        data=poster_path.read_bytes(),
        file_name="ICT_2025_해외여행_포스터.pdf",
        mime="application/pdf"
    )

st.caption(
    "출처: 문화체육관광부·한국문화관광연구원, "
    "2025년 국민여행조사 해외여행 원자료. "
    "공개 대시보드에는 집계 결과만 사용합니다."
)
