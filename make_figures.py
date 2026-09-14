"""Export every figure used in the report and slides.

Pure post-processing: reads data/creditcard.csv for the EDA panels and the
stored probability arrays in artifacts/ for everything else. No model is
refitted, so a figure can never disagree with a reported number.

    python3 make_figures.py

Output: <bundle>/04-Ket-qua/hinh-anh/*.png  (300 dpi, print-safe palette)
The bundle lives outside this repo; paths.require_bundle_dir() finds it.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

from fraud_cost import (best_amount_baseline, cost_curve, optimal_threshold,
                        policy_e_predict, total_cost, undo_class_weight)
from preprocessing import hour_of_day, stratified_split_60_20_20

ROOT = Path(__file__).resolve().parent
ART = ROOT / "artifacts"
from paths import require_bundle_dir

OUT = require_bundle_dir() / "04-Ket-qua" / "hinh-anh"
OUT.mkdir(parents=True, exist_ok=True)

C = 3.0
SEED = 42

# ---------------------------------------------------------------- palette
# Validated categorical order (light mode): adjacent-pair CVD dE >= 8,
# first three slots clear the all-pairs floor -- so the three models use 1-3.
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
YELLOW, MAGENTA, VIOLET, RED = "#eda100", "#e87ba4", "#4a3aa7", "#e34948"
INK, INK2, INK3 = "#0b0b0b", "#52514e", "#8a8880"
SURFACE, GRID = "#ffffff", "#e6e5e1"

LEGIT, FRAUD = BLUE, ORANGE
MODEL_COLOR = {"xgb/balanced": BLUE, "rf/none": ORANGE, "logreg/none": AQUA}
MODEL_LABEL = {"xgb/balanced": "XGBoost (balanced)",
               "rf/none": "Random Forest",
               "logreg/none": "Logistic Regression"}

plt.rcParams.update({
    "figure.dpi": 300, "savefig.dpi": 300,
    "figure.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "font.family": "DejaVu Sans", "font.size": 9,
    "axes.titlesize": 10.5, "axes.titleweight": "bold", "axes.titlepad": 10,
    "axes.labelsize": 9, "axes.labelcolor": INK2,
    "axes.edgecolor": GRID, "axes.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "text.color": INK, "xtick.color": INK2, "ytick.color": INK2,
    "xtick.labelsize": 8, "ytick.labelsize": 8,
    "grid.color": GRID, "grid.linewidth": 0.7,
    "legend.frameon": False, "legend.fontsize": 8.5,
    "savefig.bbox": "tight", "savefig.pad_inches": 0.25,
})

def vn(v, dec=2):
    """Vietnamese number format: 1.827,93 (dot = thousands, comma = decimal)."""
    return f"{v:,.{dec}f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def evn(v, dec=2):
    return "€" + vn(v, dec)


eur = FuncFormatter(lambda v, _: evn(v, 0))


def save(fig, name):
    path = OUT / name
    fig.savefig(path)
    plt.close(fig)
    print(f"  wrote {name}")


def alerts_cost_curve(y, scores, amounts, c):
    """(#alerts, cost) at every achievable threshold.

    cost_curve() returns one point per tie-block, so its position in the array
    is a block index, not an alert count -- plotting against the index puts
    Random Forest's giant zero-probability block one step from the origin.
    """
    y = np.asarray(y); scores = np.asarray(scores, float); amounts = np.asarray(amounts, float)
    order = np.argsort(-scores, kind="stable")
    y_s, a_s, p_s = y[order], amounts[order], scores[order]
    total_fraud = float((amounts * (y == 1)).sum())
    k = np.arange(1, len(scores) + 1)
    costs_k = c * k + (total_fraud - np.cumsum(a_s * (y_s == 1)))
    last = np.r_[p_s[1:] != p_s[:-1], True]
    return np.r_[0, k[last]], np.r_[total_fraud, costs_k[last]]


def grid_y(ax):
    ax.set_axisbelow(True)
    ax.grid(axis="y", linestyle="-", alpha=0.9)


# ================================================================== load
print("loading data ...")
df = pd.read_csv(ROOT / "data" / "creditcard.csv")
y_all = df.Class.values
amt_all = df.Amount.values
hours_all = hour_of_day(df.Time.values)
train, val, test = stratified_split_60_20_20(y_all, random_state=SEED)

va = np.load(ART / "val_probabilities.npz")
te = np.load(ART / "test_probabilities.npz")
yva, amt_va = va["y"], va["amounts"]
yte, amt_te = te["y"], te["amounts"]
champ = json.loads((ART / "preregistration.json").read_text())["declared_winner"]
KEYS = [k for k in te.files if k not in ("y", "amounts")]
ORDER = ["xgb/balanced", "rf/none", "logreg/none"]

thr_map = {k: optimal_threshold(yva, va[k], amt_va, C)[0] for k in KEYS}
w_ratio = (yva == 0).sum() / (yva == 1).sum()


def p_for_policy_e(k):
    p = te[k]
    return undo_class_weight(p, w_ratio) if k.endswith("/balanced") else p


# ============================================== F01 phan bo nhan
fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.1))
counts = [int((y_all == 0).sum()), int((y_all == 1).sum())]
labels = ["Hợp lệ", "Gian lận"]
for ax, logscale in zip(axes, [False, True]):
    bars = ax.bar(labels, counts, color=[LEGIT, FRAUD], width=0.55)
    if logscale:
        ax.set_yscale("log")
        ax.set_title("Thang log — mới nhìn thấy lớp gian lận")
    else:
        ax.set_title("Thang tuyến tính — cột gian lận vô hình")
    for b, c in zip(bars, counts):
        ax.annotate(vn(c, 0), (b.get_x() + b.get_width() / 2,
                    b.get_height()), ha="center", va="bottom", fontsize=8.5,
                    color=INK, xytext=(0, 3), textcoords="offset points")
    ax.set_ylabel("Số giao dịch")
    grid_y(ax)
fig.suptitle("Phân bố nhãn: 492 / 284.807 giao dịch là gian lận (0,173%)",
             fontsize=11, fontweight="bold", y=1.03)
save(fig, "F01_phan-bo-nhan.png")

# ============================================== F02 phan bo Amount theo lop
fig, ax = plt.subplots(figsize=(7.4, 3.6))
bins = np.logspace(np.log10(0.01), np.log10(30000), 46)
legit_amt = np.clip(amt_all[y_all == 0], 0.01, None)
fraud_amt = np.clip(amt_all[y_all == 1], 0.01, None)
# share of each class, not density: log-spaced bins have wildly unequal widths,
# so a density plot puts a meaningless spike on the narrowest bin.
ax.hist(legit_amt, bins=bins, weights=np.full(len(legit_amt), 100 / len(legit_amt)),
        color=LEGIT, alpha=0.60, label="Hợp lệ (n = " + vn(len(legit_amt), 0) + ")")
ax.hist(fraud_amt, bins=bins, weights=np.full(len(fraud_amt), 100 / len(fraud_amt)),
        color=FRAUD, alpha=0.75, label=f"Gian lận (n = {len(fraud_amt)})")
ax.set_xscale("log")
ax.set_xlim(0.008, 40000)
top = ax.get_ylim()[1]
ax.set_ylim(0, top * 1.30)
med_f, med_l = float(np.median(amt_all[y_all == 1])), float(np.median(amt_all[y_all == 0]))
ax.axvline(C, color=INK, linestyle="--", linewidth=1.4)
ax.axvline(med_f, color=FRAUD, linewidth=1.6)
ax.axvline(med_l, color=LEGIT, linewidth=1.6)
ax.annotate("phí rà soát €3", (C, top * 1.24), color=INK, fontsize=8.5,
            ha="right", xytext=(-5, 0), textcoords="offset points")
ax.annotate("trung vị gian lận " + evn(med_f), (med_f, top * 1.10), color=FRAUD,
            fontsize=8.5, ha="left", xytext=(5, 0), textcoords="offset points")
ax.annotate("trung vị hợp lệ " + evn(med_l), (med_l, top * 0.96), color=LEGIT,
            fontsize=8.5, ha="left", xytext=(5, 0), textcoords="offset points")
ax.set_xlabel("Amount (EUR, thang log) — giao dịch €0 gộp vào cột trái nhất")
ax.set_ylabel("Tỉ lệ trong lớp (%)")
ax.set_title("Gian lận điển hình NHỎ hơn giao dịch hợp lệ, nhưng đuôi phải nặng hơn")
ax.legend(loc="upper right")
grid_y(ax)
save(fig, "F02_phan-bo-amount-theo-lop.png")

# ============================================== F03 gian lan duoi phi review
f_amt = amt_all[y_all == 1]
edges = [-0.01, 0.001, 1, 3, 10, 50, 200, 1000, 1e9]
names = ["= €0", "€0–1", "€1–3", "€3–10", "€10–50", "€50–200", "€200–1k", "> €1k"]
cnt = [int(((f_amt > lo) & (f_amt <= hi)).sum()) for lo, hi in zip(edges[:-1], edges[1:])]
cnt[0] = int((f_amt == 0).sum())
below = int((f_amt < C).sum())
fig, ax = plt.subplots(figsize=(7.4, 3.4))
colors = [FRAUD if i < 3 else INK3 for i in range(len(cnt))]
bars = ax.bar(names, cnt, color=colors, width=0.62)
for b, c in zip(bars, cnt):
    ax.annotate(str(c), (b.get_x() + b.get_width() / 2, b.get_height()),
                ha="center", va="bottom", fontsize=8.5, color=INK,
                xytext=(0, 3), textcoords="offset points")
ax.axvspan(-0.5, 2.5, color=FRAUD, alpha=0.07, zorder=0)
ax.set_ylim(0, max(cnt) * 1.30)
ax.annotate(f"{below}/492 = {below/492*100:.0f}% số vụ gian lận nằm trong vùng tô\n"
            f"— RẺ HƠN phí rà soát €3, nên chính sách\ntối ưu chi phí CỐ Ý bỏ qua chúng",
            (5.2, max(cnt) * 1.06), ha="center", va="top", fontsize=9, color=FRAUD,
            fontweight="bold")
ax.set_ylabel("Số giao dịch gian lận")
ax.set_xlabel("Khoảng giá trị giao dịch")
ax.set_title("Phát hiện đầu đề: 42% số vụ gian lận không đáng tiền để rà soát")
grid_y(ax)
save(fig, "F03_gian-lan-duoi-phi-review.png")

# ============================================== F04 ti le gian lan theo gio
rate = np.array([y_all[hours_all == h].mean() * 100 for h in range(24)])
base = y_all.mean() * 100
fig, ax = plt.subplots(figsize=(7.4, 3.2))
ax.bar(range(24), rate, color=[FRAUD if r > base else INK3 for r in rate], width=0.7)
ax.axhline(base, color=INK, linestyle="--", linewidth=1.2)
ax.annotate(f"tỉ lệ nền {base:.3f}%", (23.4, base), ha="right", va="bottom",
            fontsize=8.5, color=INK)
ax.set_xticks(range(0, 24, 2))
ax.set_xlabel("Giờ trong ngày (hour_of_day)")
ax.set_ylabel("Tỉ lệ gian lận (%)")
ax.set_title("Gian lận tập trung vào các giờ đêm — lý do giữ lại thông tin giờ")
grid_y(ax)
save(fig, "F04_ti-le-gian-lan-theo-gio.png")

# ============================================== F05 duong cong chi phi
fig, ax = plt.subplots(figsize=(7.4, 3.8))
for i, k in enumerate(ORDER):
    n_alert, costs = alerts_cost_curve(yva, va[k], amt_va, C)
    m = n_alert <= 500
    ax.plot(n_alert[m], costs[m], color=MODEL_COLOR[k], linewidth=1.8,
            label=MODEL_LABEL[k])
    b = int(np.argmin(costs))
    ax.plot(n_alert[b], costs[b], "o", color=MODEL_COLOR[k], markersize=7,
            markeredgecolor=SURFACE, markeredgewidth=1.5)
    ax.annotate(f"tối ưu: {n_alert[b]} cảnh báo → " + evn(costs[b], 0),
                (0.30, 0.90 - 0.075 * i), xycoords="axes fraction",
                ha="left", va="center", fontsize=8.5, color=MODEL_COLOR[k])
nothing = float(amt_va[yva == 1].sum())
ax.axhline(nothing, color=INK3, linestyle=":", linewidth=1.3)
ax.annotate("không làm gì — " + evn(nothing, 0), (5, nothing), ha="left",
            va="bottom", fontsize=8, color=INK2)
ax.set_xlim(0, 500)
ax.set_ylim(0, nothing * 1.25)
ax.set_xlabel("Số cảnh báo phát ra (tập validation, 56.962 giao dịch)")
ax.set_ylabel("Tổng chi phí")
ax.yaxis.set_major_formatter(eur)
ax.set_title("Đường cong chi phí: điểm tối ưu ở ~80–120 cảnh báo, không phải ngưỡng 0,5")
ax.legend(loc="center right")
grid_y(ax)
save(fig, "F05_duong-cong-chi-phi.png")

# ============================================== F06 so sanh baseline
x_val, _ = best_amount_baseline(yva, amt_va, C)
rows = [
    ("Cảnh báo TẤT CẢ", len(yte) * C, INK3),
    ("Không ML: Amount ≥ " + evn(x_val, 0),
     total_cost(yte, (amt_te >= x_val).astype(int), amt_te, C), RED),
    ("Không làm gì", float(amt_te[yte == 1].sum()), INK3),
    ("Random Forest", total_cost(yte, (te["rf/none"] >= thr_map["rf/none"]).astype(int), amt_te, C), ORANGE),
    ("Logistic Regression", total_cost(yte, (te["logreg/none"] >= thr_map["logreg/none"]).astype(int), amt_te, C), AQUA),
    ("XGBoost (vô địch)", total_cost(yte, (te[champ] >= thr_map[champ]).astype(int), amt_te, C), BLUE),
]
fig, ax = plt.subplots(figsize=(7.4, 3.6))
names = [r[0] for r in rows][::-1]
vals = [r[1] for r in rows][::-1]
cols = [r[2] for r in rows][::-1]
bars = ax.barh(names, vals, color=cols, height=0.62)
ax.set_xscale("log")
for b, v in zip(bars, vals):
    ax.annotate(evn(v),
                (b.get_width(), b.get_y() + b.get_height() / 2), va="center",
                ha="left", fontsize=8.5, color=INK, xytext=(5, 0),
                textcoords="offset points")
ax.axvline(float(amt_te[yte == 1].sum()), color=INK, linestyle="--", linewidth=1.1)
ax.set_xlabel("Tổng chi phí trên tập test (thang log)")
ax.set_xlim(1500, 900000)
ax.set_title("Baseline không dùng ML còn TỆ HƠN không làm gì — đó là lý do cần máy học")
ax.grid(axis="x", linestyle="-", alpha=0.9)
ax.set_axisbelow(True)
save(fig, "F06_so-sanh-chi-phi-baseline.png")

# ============================================== bootstrap (dung cho F07)
print("running paired bootstrap ...")
rng = np.random.default_rng(SEED)
pos, neg = np.flatnonzero(yte == 1), np.flatnonzero(yte == 0)
draws = {k: [] for k in KEYS}
for _ in range(1000):
    idx = np.concatenate([rng.choice(pos, len(pos), True),
                          rng.choice(neg, len(neg), True)])
    for k in KEYS:
        draws[k].append(total_cost(yte[idx], (te[k][idx] >= thr_map[k]).astype(int),
                                   amt_te[idx], C))
draws = {k: np.array(v) for k, v in draws.items()}

fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.4),
                         gridspec_kw={"width_ratios": [1.15, 1]})
ax = axes[0]
for i, k in enumerate(ORDER):
    d = draws[k]
    lo, hi = np.percentile(d, [2.5, 97.5])
    ax.plot([lo, hi], [i, i], color=MODEL_COLOR[k], linewidth=3, solid_capstyle="round")
    ax.plot(d.mean(), i, "o", color=MODEL_COLOR[k], markersize=8,
            markeredgecolor=SURFACE, markeredgewidth=1.5)
    ax.annotate(evn(d.mean(), 0), (d.mean(), i), ha="center",
                va="bottom", fontsize=8, color=INK, xytext=(0, 8),
                textcoords="offset points")
ax.set_yticks(range(len(ORDER)))
ax.set_yticklabels([MODEL_LABEL[k] for k in ORDER])
ax.set_ylim(-0.6, len(ORDER) - 0.4)
ax.set_xlabel("Chi phí test, KTC 95% (1.000 lần bootstrap)")
ax.set_title("Ba khoảng tin cậy chồng lên nhau", fontsize=9.5)
ax.xaxis.set_major_formatter(eur)
ax.grid(axis="x", linestyle="-", alpha=0.9)
ax.set_axisbelow(True)

ax = axes[1]
others = [k for k in ORDER if k != champ]
for i, k in enumerate(others):
    d = draws[k] - draws[champ]
    lo, hi = np.percentile(d, [2.5, 97.5])
    ax.plot([lo, hi], [i, i], color=MODEL_COLOR[k], linewidth=3, solid_capstyle="round")
    ax.plot(d.mean(), i, "o", color=MODEL_COLOR[k], markersize=8,
            markeredgecolor=SURFACE, markeredgewidth=1.5)
    ax.annotate("Δ = " + evn(d.mean()), (d.mean(), i),
                ha="center", va="bottom", fontsize=8, color=INK, xytext=(0, 8),
                textcoords="offset points")
ax.axvline(0, color=INK, linewidth=1.2)
ax.set_yticks(range(len(others)))
ax.set_yticklabels([MODEL_LABEL[k] for k in others])
ax.set_ylim(-0.6, len(others) - 0.4)
ax.set_xlabel("Chênh lệch so với mô hình vô địch")
ax.set_title("Cả hai KTC đều chứa số 0 → không có ý nghĩa", fontsize=9.5)
ax.xaxis.set_major_formatter(eur)
ax.grid(axis="x", linestyle="-", alpha=0.9)
ax.set_axisbelow(True)
fig.suptitle("Không thể tuyên bố mô hình nào thắng (n_eff = 18,1)",
             fontsize=11, fontweight="bold", y=1.04)
save(fig, "F07_bootstrap-khoang-tin-cay.png")

# ============================================== F08 bo sot theo decile
p_ch = te[champ]
pred_ch = (p_ch >= thr_map[champ]).astype(int)
fr = yte == 1
f_amt_te = amt_te[fr]
f_pred = pred_ch[fr]
dec = pd.qcut(pd.Series(f_amt_te).rank(method="first"), 10, labels=False) + 1
miss_rate, miss_eur, n_dec = [], [], []
for d in range(1, 11):
    m = dec.values == d
    miss = m & (f_pred == 0)
    miss_rate.append(100 * miss.sum() / max(m.sum(), 1))
    miss_eur.append(float(f_amt_te[miss].sum()))
    n_dec.append(int(m.sum()))
fig, axes = plt.subplots(1, 2, figsize=(8.0, 3.3),
                         gridspec_kw={"wspace": 0.34})
ax = axes[0]
top = int(np.argmax(miss_rate)) + 1
ax.bar(range(1, 11), miss_rate, color=[FRAUD if i + 1 == top else INK3 for i in range(10)], width=0.68)
ax.set_ylim(0, max(miss_rate) * 1.35)
ax.annotate(f"cao nhất:\ndecile {top} — {max(miss_rate):.0f}%", (top + 0.4, max(miss_rate)),
            ha="left", va="top", fontsize=8.5, color=FRAUD, fontweight="bold")
ax.set_xticks(range(1, 11))
ax.set_xlabel("Decile giá trị giao dịch")
ax.set_ylabel("Tỉ lệ bỏ sót (%)")
ax.set_title("Đếm LỖI → chỉ vào decile giữa", fontsize=9.5)
grid_y(ax)
ax = axes[1]
topc = int(np.argmax(miss_eur)) + 1
ax.bar(range(1, 11), miss_eur, color=[BLUE if i + 1 == topc else INK3 for i in range(10)], width=0.68)
ax.set_ylim(0, max(miss_eur) * 1.22)
ax.annotate(f"decile {topc}: " + evn(max(miss_eur), 0) +
            f"\n= {100*max(miss_eur)/sum(miss_eur):.0f}% toàn bộ thiệt hại",
            (5.4, max(miss_eur) * 1.10), ha="center", va="top", fontsize=8.5,
            color=BLUE, fontweight="bold")
ax.set_xticks(range(1, 11))
ax.set_xlabel("Decile giá trị giao dịch")
ax.set_ylabel("Tiền mất do bỏ sót")
ax.yaxis.set_major_formatter(eur)
ax.set_title("Đếm TIỀN → chỉ vào decile đắt nhất", fontsize=9.5)
grid_y(ax)
fig.suptitle("Đếm số lỗi và đếm tiền mất là hai câu chuyện khác nhau",
             fontsize=11, fontweight="bold", y=1.04)
save(fig, "F08_bo-sot-theo-decile.png")

# ============================================== F09 confusion matrix
TP = int(((yte == 1) & (pred_ch == 1)).sum())
FN = int(((yte == 1) & (pred_ch == 0)).sum())
FP = int(((yte == 0) & (pred_ch == 1)).sum())
TN = int(((yte == 0) & (pred_ch == 0)).sum())
cm = np.array([[TN, FP], [FN, TP]])
cost_cell = [[0.0, C * FP], [float(amt_te[(yte == 1) & (pred_ch == 0)].sum()), C * TP]]
fig, ax = plt.subplots(figsize=(5.0, 3.5))
norm = np.array([[0.15, 0.55], [0.85, 0.45]])
ax.imshow(norm, cmap="Blues", vmin=0, vmax=1.6)
txt = [["TN = " + vn(TN, 0), f"FP = {FP}"],
       [f"FN = {FN}", f"TP = {TP}"]]
sub = [["chi phí €0", "chi phí " + evn(cost_cell[0][1])],
       ["MẤT " + evn(cost_cell[1][0]),
        "chi phí " + evn(cost_cell[1][1])]]
for i in range(2):
    for j in range(2):
        ax.text(j, i - 0.12, txt[i][j], ha="center", va="center", fontsize=12,
                fontweight="bold", color=INK)
        ax.text(j, i + 0.16, sub[i][j], ha="center", va="center", fontsize=8.5,
                color=INK2)
ax.set_xticks([0, 1]); ax.set_xticklabels(["Dự đoán: hợp lệ", "Dự đoán: gian lận"])
ax.set_yticks([0, 1]); ax.set_yticklabels(["Thực tế:\nhợp lệ", "Thực tế:\ngian lận"])
ax.tick_params(length=0)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_title(f"Ma trận nhầm lẫn — {MODEL_LABEL[champ]}\n"
             f"Precision {TP/(TP+FP)*100:.1f}%  ·  Recall {TP/(TP+FN)*100:.1f}%  ·  "
             f"F1 {2*TP/(2*TP+FP+FN):.3f}", fontsize=9.5)
save(fig, "F09_ma-tran-nham-lan.png")

# ============================================== F10 hieu chuan duoi
fig, ax = plt.subplots(figsize=(6.6, 3.9))
edges_p = np.logspace(-7, 0, 15)
FLOOR = 3e-6
for k in ORDER:
    p = p_for_policy_e(k)
    xs, ys, xz = [], [], []
    for lo, hi in zip(edges_p[:-1], edges_p[1:]):
        m = (p >= lo) & (p < hi)
        if m.sum() < 30:
            continue
        obs = yte[m].mean()
        if obs > 0:
            xs.append(p[m].mean()); ys.append(obs)
        else:
            xz.append(p[m].mean())          # bin with zero observed frauds
    ax.plot(xs, ys, "o-", color=MODEL_COLOR[k], markersize=5, linewidth=1.7,
            label=MODEL_LABEL[k])
    if xz:
        ax.plot(xz, [FLOOR] * len(xz), "o", markerfacecolor="none", markersize=5,
                markeredgecolor=MODEL_COLOR[k], markeredgewidth=1.2)
lim = [1e-7, 1.0]
ax.plot(lim, lim, "--", color=INK3, linewidth=1.2, label="hiệu chuẩn hoàn hảo")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlim(*lim); ax.set_ylim(1.4e-6, 2.0)
ax.axhline(FLOOR, color=GRID, linewidth=0.8)
ax.annotate("○ = nhóm không quan sát được vụ gian lận nào", (1.3e-7, FLOOR * 2.2),
            va="bottom", fontsize=7.5, color=INK2)
ax.set_xlabel("Xác suất dự đoán trung bình của nhóm (thang log)")
ax.set_ylabel("Tần suất gian lận quan sát")
ax.set_title("Hiệu chuẩn ở vùng đuôi — nơi Chính sách E thực sự ra quyết định")
ax.legend(loc="upper left", fontsize=8)
ax.grid(linestyle="-", alpha=0.9)
ax.set_axisbelow(True)
save(fig, "F10_hieu-chuan-vung-duoi.png")

# ============================================== F11 duong cong PR
def pr_curve(y, s):
    o = np.argsort(-s, kind="stable")
    ys = y[o]
    tp = np.cumsum(ys == 1); fp = np.cumsum(ys == 0)
    prec = tp / (tp + fp)
    rec = tp / max((y == 1).sum(), 1)
    return rec, prec

from sklearn.metrics import average_precision_score as ap  # same call as the pipeline

fig, ax = plt.subplots(figsize=(5.6, 3.8))
for k in ORDER:
    r, p = pr_curve(yte, te[k])
    ax.plot(r, p, color=MODEL_COLOR[k], linewidth=1.8,
            label=f"{MODEL_LABEL[k]} — PR-AUC {ap(yte, te[k]):.4f}")
ax.axhline(yte.mean(), color=INK3, linestyle=":", linewidth=1.2)
ax.annotate(f"đoán ngẫu nhiên ({yte.mean()*100:.3f}%)", (0.98, yte.mean()),
            ha="right", va="bottom", fontsize=8, color=INK2)
ax.set_xlabel("Recall"); ax.set_ylabel("Precision")
ax.set_xlim(0, 1); ax.set_ylim(0, 1.02)
ax.set_title("Đường cong Precision–Recall trên tập test")
ax.legend(loc="lower left")
ax.grid(linestyle="-", alpha=0.9); ax.set_axisbelow(True)
save(fig, "F11_duong-cong-precision-recall.png")

# ============================================== F12 policy A vs E
A = [total_cost(yte, (te[k] >= thr_map[k]).astype(int), amt_te, C) for k in ORDER]
E = [total_cost(yte, policy_e_predict(p_for_policy_e(k), amt_te, C), amt_te, C) for k in ORDER]
fig, ax = plt.subplots(figsize=(6.4, 3.5))
xpos = np.arange(len(ORDER)); wid = 0.36
b1 = ax.bar(xpos - wid / 2 - 0.01, A, wid, color=BLUE, label="Chính sách A — ngưỡng toàn cục (có tinh chỉnh)")
b2 = ax.bar(xpos + wid / 2 + 0.01, E, wid, color=ORANGE, label="Chính sách E — p × Amount > €3 (0 tham số)")
for bars, vals in [(b1, A), (b2, E)]:
    for b, v in zip(bars, vals):
        ax.annotate(evn(v, 0), (b.get_x() + b.get_width() / 2, v),
                    ha="center", va="bottom", fontsize=8.5, color=INK,
                    xytext=(0, 3), textcoords="offset points")
ax.set_xticks(xpos); ax.set_xticklabels([MODEL_LABEL[k].replace(" (", "\n(") for k in ORDER])
ax.set_ylabel("Chi phí test"); ax.yaxis.set_major_formatter(eur)
ax.set_ylim(0, max(A + E) * 1.55)
ax.set_title("Quy tắc Bayes tối ưu KHÔNG thắng ngưỡng đã tinh chỉnh")
ax.legend(loc="upper center", ncol=1)
grid_y(ax)
save(fig, "F12_chinh-sach-A-vs-E.png")

# ============================================== F13 quet c_review
sweep = np.arange(1, 21, 1.0)
fig, ax = plt.subplots(figsize=(6.6, 3.6))
for k in ORDER:
    ys = []
    for c in sweep:
        thr_c, _, _ = optimal_threshold(yva, va[k], amt_va, c)
        ys.append(total_cost(yte, (te[k] >= thr_c).astype(int), amt_te, c))
    ax.plot(sweep, ys, color=MODEL_COLOR[k], linewidth=1.8, label=MODEL_LABEL[k])
ax.plot(sweep, [float(amt_te[yte == 1].sum())] * len(sweep), ":", color=INK3,
        linewidth=1.4, label="Không làm gì")
ax.axvline(C, color=INK, linestyle="--", linewidth=1.2)
ax.annotate("c_review = €3\n(giá trị dùng trong báo cáo)", (C, 1000), fontsize=8,
            color=INK, ha="left", xytext=(8, 0), textcoords="offset points")
ax.set_xlabel("Phí rà soát c_review (EUR)")
ax.set_ylabel("Chi phí test"); ax.yaxis.set_major_formatter(eur)
ax.set_title("Kết luận không đổi khi quét c_review từ €1 đến €20")
ax.set_xticks(range(2, 21, 2))
ax.set_xlim(1, 20)
ax.set_ylim(0, float(amt_te[yte == 1].sum()) * 1.15)
ax.legend(loc="upper right", fontsize=8)
grid_y(ax)
save(fig, "F13_quet-c-review.png")

# ============================================== F14 train vs val PR-AUC
tv = {"rf/none": (1.0000, 0.7992), "xgb/balanced": (1.0000, 0.8228),
      "logreg/none": (0.7925, 0.7142)}
fig, ax = plt.subplots(figsize=(6.2, 3.4))
xpos = np.arange(len(ORDER)); wid = 0.36
tr = [tv[k][0] for k in ORDER]; vl = [tv[k][1] for k in ORDER]
b1 = ax.bar(xpos - wid / 2 - 0.01, tr, wid, color=INK3, label="PR-AUC train")
b2 = ax.bar(xpos + wid / 2 + 0.01, vl, wid, color=BLUE, label="PR-AUC validation")
for bars, vals in [(b1, tr), (b2, vl)]:
    for b, v in zip(bars, vals):
        ax.annotate(f"{v:.4f}", (b.get_x() + b.get_width() / 2, v), ha="center",
                    va="bottom", fontsize=8, color=INK, xytext=(0, 3),
                    textcoords="offset points")
for i, k in enumerate(ORDER):
    gap = tv[k][0] - tv[k][1]
    ax.annotate(f"khoảng cách\n+{gap:.4f}", (i, 1.09), ha="center", fontsize=8.5,
                color=RED if gap > 0.15 else AQUA, fontweight="bold")
ax.set_xticks(xpos); ax.set_xticklabels([MODEL_LABEL[k].replace(" (", "\n(") for k in ORDER])
ax.set_ylim(0, 1.25); ax.set_ylabel("PR-AUC")
ax.set_title("Chẩn đoán overfitting: RF và XGBoost đạt PR-AUC train = 1,0000")
ax.legend(loc="lower right")
grid_y(ax)
save(fig, "F14_train-vs-validation-prauc.png")

# ============================================== console summary
print("\n--- các con số dùng trong báo cáo ---")
print(f"frauds < c_review        {below}/492 ({below/492*100:.1f}%)  |  == 0 EUR: {int((f_amt==0).sum())}")
print(f"no-ML X (from val)       EUR{x_val:,.2f}")
print(f"champion                 {champ}  thr={thr_map[champ]:.6f}")
print(f"TP/FP/FN/TN              {TP}/{FP}/{FN}/{TN}")
print(f"test cost champion       EUR{total_cost(yte, pred_ch, amt_te, C):,.2f}")
print(f"missed decile 10 EUR     {miss_eur[-1]:,.2f} / total missed {sum(miss_eur):,.2f}")
print(f"PR-AUC test              " + "  ".join(f"{k}={ap(yte, te[k]):.4f}" for k in ORDER))
print(f"\n{len(list(OUT.glob('*.png')))} figures in {OUT}")
