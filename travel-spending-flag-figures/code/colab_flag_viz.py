# ============================================================================
#  일본·베트남 국기 모티프 시각화 (코랩용)  -  그림 1 / 그림 2 / 그림 3
#  일본  : 흰 바탕 + 붉은 원(히노마루)   → 흰 막대(붉은 테두리) + 붉은 원 마커
#  베트남: 붉은 바탕 + 노란 별          → 붉은 막대 + 노란 별 마커
#  두 국기의 붉은색이 거의 같으므로 "색"이 아니라 채움(흰색/붉은색)과 마커 모양(원/별)으로
#  구분한다. 흑백 인쇄·색각 이상에서도 구분된다.
#  전제: 기존 코랩의 source, comparison, OUT 변수를 그대로 사용
#        comparison 컬럼: country, days, w, cost
# ============================================================================
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, PathPatch
from matplotlib.path import Path as MplPath
from matplotlib.legend_handler import HandlerBase
from pathlib import Path

assert "source" in globals() and "comparison" in globals() and "OUT" in globals()

PAPER = True          # True: 논문용(폭 5.9in, 글자 8pt 안팎)  /  False: 발표·보고서용(큰 크기 + 제목)
K = 1.0 if PAPER else 1.75   # 글자·선 굵기 배율

# ---------------------------------------------------------------- 색 (국기)
JP_RED    = "#BC002D"   # 일본 국기 붉은색
VN_RED    = "#DA251D"   # 베트남 국기 붉은색
VN_YELLOW = "#FFCD00"   # 베트남 국기 노란색(순황색 #FFFF00은 흰 배경에서 잘 안 보여 약간 진하게)
VN_EDGE   = "#8E1710"   # 별 테두리용 진한 적색
INK, SUB  = "#222222", "#6B6B6B"
PANEL_BG, GRID = "#F6F4F1", "#FFFFFF"

# ---------------------------------------------------------------- 한글 글꼴
def set_korean_font():
    from matplotlib import font_manager as fm
    names = {f.name for f in fm.fontManager.ttflist}
    for cand in ["NanumGothic", "NanumBarunGothic", "Noto Sans CJK KR", "Noto Sans KR",
                 "Malgun Gothic", "AppleGothic"]:
        if cand in names:
            plt.rcParams["font.family"] = cand
            break
    else:
        print("한글 글꼴이 없습니다. 코랩이면 먼저  !apt-get -qq install fonts-nanum  실행 후 런타임을 다시 시작하세요.")
    plt.rcParams["axes.unicode_minus"] = False

set_korean_font()

# ---------------------------------------------------------------- 국기 도형
STAR = MplPath.unit_regular_star(5)          # 위쪽을 향한 오각별 (외접원 반지름 1)

def star_marker(ax, x, y, diam_pts, **kw):
    """데이터 좌표 (x, y)에 지름 diam_pts(pt)의 별 마커. 막대 끝에 얹을 때 사용."""
    ax.scatter([x], [y], s=diam_pts ** 2, marker="*", **kw)

class FlagKey:
    def __init__(self, country): self.country = country

class FlagHandler(HandlerBase):
    """범례 칸에 3:2 비율의 미니 국기를 그린다."""
    def create_artists(self, legend, key, xdescent, ydescent, width, height, fontsize, trans):
        h = height * 0.98; w = min(width, h * 1.5); x0 = xdescent; y0 = ydescent + (height - h) / 2
        cx, cy = x0 + w / 2, y0 + h / 2
        if key.country == "일본":
            field = Rectangle((x0, y0), w, h, fc="white", ec=JP_RED, lw=0.9, transform=trans)
            motif = Circle((cx, cy), h * 0.30, fc=JP_RED, ec="none", transform=trans)
        else:
            field = Rectangle((x0, y0), w, h, fc=VN_RED, ec=VN_RED, lw=0.9, transform=trans)
            verts = STAR.vertices * (h * 0.36) + [cx, cy]
            motif = PathPatch(MplPath(verts, STAR.codes), fc=VN_YELLOW, ec="none", transform=trans)
        return [field, motif]

def flag_legend(ax, labels, loc="upper right", bbox=(1.0, 0.99)):
    keys = [FlagKey("일본"), FlagKey("베트남")]
    return ax.legend(keys, labels, handler_map={FlagKey: FlagHandler()}, loc=loc, bbox_to_anchor=bbox,
                     frameon=True, facecolor=PANEL_BG, edgecolor="none", framealpha=0.95,
                     fontsize=7.5 * K, handlelength=2.3, handleheight=1.35, borderpad=0.5,
                     labelspacing=0.55)

# ---------------------------------------------------------------- 축 스타일
def style_axes(ax, grid_axis="x"):
    ax.set_facecolor(PANEL_BG)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#BDB8B0"); ax.spines["bottom"].set_linewidth(0.8)
    ax.grid(axis=grid_axis, color=GRID, lw=1.1 * K, zorder=0); ax.set_axisbelow(True)
    ax.tick_params(length=0, labelsize=7.5 * K, colors=INK)

def pts_per_unit(ax, axis):
    fig = ax.figure; fig.canvas.draw()
    bb = ax.get_window_extent(); (lo, hi) = ax.get_xlim() if axis == "x" else ax.get_ylim()
    size = bb.width if axis == "x" else bb.height
    return size * 72 / fig.dpi / abs(hi - lo)

def panel_title(ax, text):
    ax.set_title(text, fontsize=9 * K, fontweight="bold", loc="left", color=INK, pad=6 * K)

def save(fig, name):
    out = Path(OUT)
    fig.savefig(out / f"{name}.png", dpi=300, bbox_inches="tight", facecolor="white")
    fig.savefig(out / f"{name}.pdf", bbox_inches="tight", facecolor="white")   # 벡터본
    print("저장:", out / f"{name}.png")

def headline(fig, text, sub=None):
    """발표용(PAPER=False)에서만 제목 + 국기색 포인트 선"""
    if PAPER:
        return
    fig.suptitle(text, fontsize=15 * K / 1.75 * 1.2, fontweight="bold", x=0.01, ha="left", y=1.02, color=INK)
    fig.add_artist(plt.Line2D([0.01, 0.075], [0.985, 0.985], color=JP_RED, lw=3, transform=fig.transFigure))
    fig.add_artist(plt.Line2D([0.075, 0.14], [0.985, 0.985], color=VN_RED, lw=3, transform=fig.transFigure))
    if sub:
        fig.text(0.01, 0.955, sub, fontsize=8.5 * K / 1.75 * 1.2, color=SUB, ha="left")

# ---------------------------------------------------------------- 막대(국기 필드) 그리기
def flag_bars(ax, y, vals, country, height, fmt="{:.1f}", label_gap=0.012, xmax=None, marker=True):
    """일본: 흰 막대 + 붉은 테두리 + 붉은 원 / 베트남: 붉은 막대 + 노란 별"""
    vals = np.asarray(vals, float)
    if country == "일본":
        ax.barh(y, vals, height=height, color="white", edgecolor=JP_RED, linewidth=1.2 * K, zorder=3)
    else:
        ax.barh(y, vals, height=height, color=VN_RED, edgecolor=VN_RED, linewidth=1.2 * K, zorder=3)
    xmax = xmax or ax.get_xlim()[1]
    ppu_x = pts_per_unit(ax, "x"); ppu_y = pts_per_unit(ax, "y")
    diam = height * ppu_y * 0.66                      # 막대 두께에 비례한 마커 지름(pt)
    for yi, v in zip(y, vals):
        if marker and v * ppu_x > diam * 1.9:         # 막대가 마커를 담을 만큼 길 때만
            cx = v - (diam / 2 + 2.0) / ppu_x
            if country == "일본":
                ax.scatter([cx], [yi], s=diam ** 2, marker="o", color=JP_RED, linewidths=0, zorder=5)
            else:
                ax.scatter([cx], [yi], s=(diam * 1.25) ** 2, marker="*", color=VN_YELLOW,
                           edgecolors=VN_EDGE, linewidths=0.5 * K, zorder=5)
        ax.text(v + xmax * label_gap, yi, fmt.format(v), va="center", ha="left",
                fontsize=7.2 * K, color=INK, zorder=6)

# ============================================================================
#  그림 3. 소비 카테고리별 지출  (Q8 세부 항목)
# ============================================================================
def load_category_data():
    def expense_col(c):
        c = str(c).strip()
        return (c in ["NAA8", "NAA8B", "AA1"]
                or bool(re.fullmatch(r"NAA8[A-J]_\d+", c))
                or bool(re.fullmatch(r"NAA8FA_\d+", c)))        # 자가용·렌트카(교통) 포함

    raw = pd.read_excel(source, engine="openpyxl", usecols=expense_col)
    raw.columns = raw.columns.str.strip()

    d = comparison[["country", "days", "w", "cost"]].copy()
    d = d[d["country"].astype(str).isin(["일본", "베트남"]) & d["days"].between(3, 7)]
    assert d.index.isin(raw.index).all(), "comparison 인덱스가 원자료 행 번호와 맞지 않습니다."
    d = d.join(raw.loc[d.index])

    def cols(prefix):
        return [c for c in d.columns if re.fullmatch(prefix + r"_\d+", c)]

    category_map = {
        "상품·회비":   cols("NAA8A") + ["NAA8B"],
        "숙박":       cols("NAA8C"),
        "식당·식음료": cols("NAA8D") + cols("NAA8E"),
        "교통":       cols("NAA8F") + cols("NAA8FA"),
        "관광·체험":   cols("NAA8G"),
        "쇼핑·귀금속": cols("NAA8H") + cols("NAA8I"),
        "기타":       cols("NAA8J"),
    }
    for cat, cs in category_map.items():
        d[cat] = d[cs].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)
    cats = list(category_map)
    d["NAA8"] = pd.to_numeric(d["NAA8"], errors="coerce")
    ok = d["NAA8"].notna()
    rate = np.isclose(d.loc[ok, cats].sum(axis=1), d.loc[ok, "NAA8"], rtol=0.01, atol=100).mean()
    print(f"Q8 카테고리 합계 일치율: {rate:.1%}")          # 기대값 100.0%
    if rate < 0.95:
        raise ValueError("세부항목 합계와 Q8 총합 일치율이 낮습니다. 변수 구조를 검토하세요.")
    d["AA1"] = pd.to_numeric(d["AA1"], errors="coerce")     # 1 전체패키지, 2 부분패키지, 3 구매 안 함
    return d, cats

def figure3():
    d, cats = load_category_data()
    groups = [("(a) 전체 여행", d), ("(b) 패키지 미구매 개별여행", d[d["AA1"] == 3])]
    fig, axes = plt.subplots(1, 2, figsize=(5.9 * (1 if PAPER else 1.85), 3.1 * (1 if PAPER else 1.85)), sharey=True)
    y = np.arange(len(cats)); H = 0.34; off = 0.2
    summary = []
    stats = []
    for title, g in groups:
        s = {}
        for country in ["일본", "베트남"]:
            p = g[g["country"].astype(str) == country]
            s[country] = (len(p), [np.average(p[c], weights=p["w"]) / 1e4 for c in cats])
            for c, v in zip(cats, s[country][1]):
                summary.append({"분석집단": title, "국가": country, "카테고리": c, "표본수": len(p), "평균지출_만원": v})
        stats.append(s)

    for ax, (title, _), s in zip(axes, groups, stats):
        xmax = max(max(s["일본"][1]), max(s["베트남"][1])) * 1.20
        style_axes(ax, "x"); ax.set_xlim(0, xmax); ax.set_ylim(len(cats) - 0.5, -0.5)
        ax.set_yticks(y); ax.set_yticklabels(cats, fontsize=8 * K, color=INK)
        ax.set_xlabel("1인당 가중평균 지출액 (만원)", fontsize=7.8 * K, color=SUB)
        panel_title(ax, title)
    fig.tight_layout(w_pad=1.2)
    for ax, s in zip(axes, stats):
        xmax = ax.get_xlim()[1]
        flag_bars(ax, y - off, s["일본"][1], "일본", H, xmax=xmax)
        flag_bars(ax, y + off, s["베트남"][1], "베트남", H, xmax=xmax)
        flag_legend(ax, [f"일본 (n={s['일본'][0]})", f"베트남 (n={s['베트남'][0]})"], loc="lower right", bbox=(1.0, 0.02))
    headline(fig, "일본·베트남 소비 카테고리별 지출 비교", "3~7일 해외여행 · 조사 가중평균 · Q8 여행지 및 이동 과정 지출")
    save(fig, "fig3_category_flag")
    plt.show()
    out = Path(OUT) / "category_expense_summary.csv"
    pd.DataFrame(summary).to_csv(out, index=False, encoding="utf-8-sig"); print("저장:", out)

# ============================================================================
#  그림 1. 여행일수별 평균 지출(선) + 표본 수(막대)
# ============================================================================
def figure1(days=(3, 4, 5, 6), small_n=30):
    d = comparison[["country", "days", "w", "cost"]].copy()
    d["country"] = d["country"].astype(str)
    res = {}
    for k in ["일본", "베트남"]:
        v, n = [], []
        for t in days:
            p = d[(d["country"] == k) & (d["days"] == t)]
            n.append(len(p)); v.append(np.average(p["cost"], weights=p["w"]) / 1e4 if len(p) else np.nan)
        res[k] = (np.array(v), np.array(n))

    fig, (a, b) = plt.subplots(1, 2, figsize=(5.9 * (1 if PAPER else 1.85), 2.7 * (1 if PAPER else 1.85)),
                               gridspec_kw={"width_ratios": [1.1, 1]})
    # ---- (a) 평균 지출: 일본=붉은 실선+원, 베트남=붉은 점선+별
    style_axes(a, "y"); a.set_xlim(2.55, 6.7); a.set_ylim(0, 215)
    a.set_xticks(days); a.set_xlabel("여행일수 (일)", fontsize=7.8 * K, color=SUB)
    a.set_ylabel("1인당 가중평균 총지출 (만원)", fontsize=7.8 * K, color=SUB)
    panel_title(a, "(a) 여행일수별 평균 지출액")
    jp, vn = res["일본"][0], res["베트남"][0]
    a.plot(days, jp, color=JP_RED, lw=2.0 * K, zorder=3)
    a.plot(days, vn, color=VN_RED, lw=2.0 * K, ls=(0, (4, 2.2)), zorder=3)
    a.scatter(days, jp, s=(8 * K) ** 2, color=JP_RED, edgecolors="white", linewidths=1.2 * K, zorder=5)
    a.scatter(days, vn, s=(13 * K) ** 2, marker="*", color=VN_YELLOW, edgecolors=VN_EDGE, linewidths=0.7 * K, zorder=5)
    for t, v, nn in zip(days, jp, res["일본"][1]):
        up = t > days[0]
        a.annotate(f"{v:.1f}" + ("†" if nn < small_n else ""), (t, v), xytext=(0, 8 * K if up else -12 * K),
                   textcoords="offset points", ha="center", fontsize=7 * K, color=JP_RED, fontweight="bold")
    for t, v, nn in zip(days, vn, res["베트남"][1]):
        up = t == days[0]
        a.annotate(f"{v:.1f}" + ("†" if nn < small_n else ""), (t, v), xytext=(0, 8 * K if up else -12 * K),
                   textcoords="offset points", ha="center", fontsize=7 * K, color=VN_EDGE, fontweight="bold")
    flag_legend(a, ["일본", "베트남"], loc="upper left", bbox=(0.0, 0.99))
    # ---- (b) 표본 수
    style_axes(b, "y"); b.set_ylim(0, max(res["일본"][1].max(), res["베트남"][1].max()) * 1.2)
    b.set_xlim(-0.6, len(days) - 0.4)
    b.set_xticks(range(len(days))); b.set_xticklabels(days); b.set_xlabel("여행일수 (일)", fontsize=7.8 * K, color=SUB)
    b.set_ylabel("관측 기록 수 (건)", fontsize=7.8 * K, color=SUB); panel_title(b, "(b) 여행일수별 표본 수")
    w = 0.36
    b.set_ylim(0, max(res["일본"][1].max(), res["베트남"][1].max()) * 1.32)
    ymax = b.get_ylim()[1]
    for k, off, fc, ec in [("일본", -w / 2, "white", JP_RED), ("베트남", w / 2, VN_RED, VN_RED)]:
        n = res[k][1]
        b.bar(np.arange(len(days)) + off, n, w, color=fc, edgecolor=ec, linewidth=1.2 * K, zorder=3)
        for i, nn in enumerate(n):
            my = nn + ymax * 0.065                       # 막대 위에 국기 마커, 그 위에 숫자
            if k == "일본":
                b.scatter([i + off], [my], s=(8 * K) ** 2, marker="o", color=JP_RED, linewidths=0, zorder=5)
            else:
                b.scatter([i + off], [my], s=(14 * K) ** 2, marker="*", color=VN_YELLOW,
                          edgecolors=VN_EDGE, linewidths=0.6 * K, zorder=5)
            b.text(i + off, my + ymax * 0.07, str(nn), ha="center", va="bottom", fontsize=7 * K, color=INK)
    flag_legend(b, ["일본", "베트남"], loc="upper right", bbox=(1.0, 0.99))
    fig.tight_layout(w_pad=1.4)
    fig.text(0.01, -0.02, f"† 표본 {small_n}건 미만 (평균이 불안정할 수 있음). 7일 여행은 국가별 표본 20건 미만이어서 제외함.",
             fontsize=6.8 * K, color=SUB, ha="left")
    headline(fig, "여행일수별 평균 지출과 표본 수", "일본·베트남 · 조사 가중평균")
    save(fig, "fig1_days_flag"); plt.show()

# ============================================================================
#  그림 2. 기간–지출 탄력성과 95% 신뢰구간 (논문 표 2의 모형 3 추정값)
# ============================================================================
ELASTICITY = {"일본": (0.7034, 0.5707, 0.8361), "베트남": (-0.0090, -0.2363, 0.2183)}   # (추정값, 하한, 상한)

def figure2():
    fig, ax = plt.subplots(figsize=(2.9 * (1 if PAPER else 2.1), 1.95 * (1 if PAPER else 2.1)))
    style_axes(ax, "x"); ax.set_xlim(-0.45, 1.25); ax.set_ylim(1.7, -0.7)
    ax.set_yticks([0, 1]); ax.set_yticklabels(["일본", "베트남"], fontsize=8.5 * K, color=INK)
    ax.set_xlabel("여행기간 탄력성 (95% 신뢰구간, HC3)", fontsize=7.6 * K, color=SUB)
    ax.axvline(0, color="#BDB8B0", lw=0.9, zorder=1)
    ax.axvline(1, color=SUB, lw=1.1 * K, ls=":", zorder=2)
    ax.text(1.03, 0.5, "탄력성=1 (총지출이 기간에 비례)", rotation=90, ha="left", va="center", fontsize=6.6 * K, color=SUB)
    for i, (k, (e, lo, hi)) in enumerate(ELASTICITY.items()):
        col = JP_RED if k == "일본" else VN_RED
        ax.plot([lo, hi], [i, i], color=col, lw=2.2 * K, solid_capstyle="round", zorder=3)
        ax.plot([lo, lo], [i - 0.09, i + 0.09], color=col, lw=1.6 * K, zorder=3)
        ax.plot([hi, hi], [i - 0.09, i + 0.09], color=col, lw=1.6 * K, zorder=3)
        if k == "일본":
            ax.scatter([e], [i], s=(9 * K) ** 2, color=JP_RED, edgecolors="white", linewidths=1.3 * K, zorder=5)
        else:
            ax.scatter([e], [i], s=(17 * K) ** 2, marker="*", color=VN_YELLOW, edgecolors=VN_EDGE, linewidths=0.8 * K, zorder=5)
        ax.annotate(f"{e:.3f}", (e, i), xytext=(0, (-11 if k == "일본" else -19) * K), textcoords="offset points",
                    ha="center", fontsize=7.5 * K, fontweight="bold", color=INK)
    fig.tight_layout()
    headline(fig, "여행기간 탄력성 비교", "일본·베트남 · 3~7일 · 연령·소득 보정")
    save(fig, "fig2_elasticity_flag"); plt.show()

# ---------------------------------------------------------------- 실행
figure1()
figure2()
figure3()
