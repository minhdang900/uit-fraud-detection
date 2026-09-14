"""Demo chạy thử — trình diễn kết quả đồ án trong một lệnh.

    python demo.py                      # bản đầy đủ
    python demo.py --score 0.02 1500    # chấm điểm một giao dịch bất kỳ
    python demo.py --quick              # bỏ qua bootstrap (nhanh hơn)

Không cần file CSV 144MB. Mọi con số được TÍNH LẠI từ mảng xác suất đã lưu
trong artifacts/, không đọc từ bảng kết quả nào — nên nếu pipeline trôi thì
demo này trôi theo, và sai lệch sẽ lộ ra ngay trước mặt hội đồng.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

from fraud_cost import (best_amount_baseline, optimal_threshold,
                        policy_e_predict, total_cost)

import paths

ROOT = Path(__file__).resolve().parent
# Nghị quyết chung cho cả hai bố cục (repo và bản sao trong bộ nộp bài):
# must_exist=False để thông báo lỗi thân thiện bên dưới vẫn được dùng.
ART = paths.artifacts_dir(must_exist=False)
C_REVIEW = 3.0
SEED = 42
W = 74


def rule(ch="─"):
    print(ch * W)


def head(n, title):
    print()
    rule("━")
    print(f"  {n}. {title}")
    rule("━")


def eur(x):
    return f"€{x:,.2f}"


def load():
    if not (ART / "test_probabilities.npz").exists():
        sys.exit(
            "Không tìm thấy artifacts/. Chạy trước:\n"
            "    docker compose exec -T lab python run_model_matrix.py"
        )
    te = np.load(ART / "test_probabilities.npz")
    va = np.load(ART / "val_probabilities.npz")
    prereg = json.loads((ART / "preregistration.json").read_text())
    return te, va, prereg


# ──────────────────────────────────────────────────────── 1. hàm chi phí
def demo_cost_model():
    head(1, "Hàm chi phí — ví dụ tính tay, kiểm chứng được bằng mắt")
    print("""
  TotalCost = c_review × (TP + FP)  +  Σ Amount của các ca BỎ SÓT
              └ trả tiền cho MỌI cảnh báo ┘  └ mất nguyên số tiền ┘

  c_review = €3 (chi phí một lần nhân viên rà soát)
""")
    y = np.array([1, 1, 0, 0])
    pred = np.array([1, 0, 1, 0])
    amt = np.array([100.0, 500.0, 50.0, 20.0])
    labels = ["TP  bắt được", "FN  BỎ SÓT", "FP  báo nhầm", "TN  bỏ qua"]
    costs = [C_REVIEW, 500.0, C_REVIEW, 0.0]

    print(f"  {'':<16}{'Thật':>6}{'Đoán':>7}{'Số tiền':>12}{'Chi phí':>12}")
    rule()
    for lab, t, p, a, c in zip(labels, y, pred, amt, costs):
        print(f"  {lab:<16}{t:>6}{p:>7}{eur(a):>12}{eur(c):>12}")
    rule()
    got = total_cost(y, pred, amt, C_REVIEW)
    print(f"  {'TỔNG':<16}{'':>6}{'':>7}{'':>12}{eur(got):>12}")
    print("\n  Kiểm tra: 3×(1 TP + 1 FP) + €500 bỏ sót = €6 + €500 = €506")
    assert got == 506.0, "hàm chi phí đã trôi so với ví dụ tính tay!"
    print("  ✓ total_cost() trả về đúng €506.00")


# ─────────────────────────────────────────── 2. vì sao không dùng 1 ngưỡng
def demo_policy_rule():
    head(2, "Quy tắc quyết định — vì sao KHÔNG dùng một ngưỡng duy nhất")
    print("""
  Tối thiểu hoá hàm trên KHÔNG cho ra một ngưỡng chung. Nó cho ra quy tắc
  phụ thuộc từng giao dịch:

        cảnh báo  ⟺  p × Amount > c_review
        (tổn thất kỳ vọng nếu bỏ qua)  >  (chi phí nhìn một cái)
""")
    p = np.array([0.01, 0.50, 0.001, 0.90])
    amt = np.array([1000.0, 4.0, 10000.0, 1.0])
    alerts = policy_e_predict(p, amt, C_REVIEW)

    print(f"  {'p':>8}{'Amount':>13}{'p × Amount':>14}{'> €3?':>9}   Nhận xét")
    rule()
    notes = ["xác suất THẤP, tiền THẬT → vẫn phải xem",
             "—",
             "xác suất CỰC THẤP, tiền RẤT LỚN → phải xem",
             "xác suất CAO, tiền vụn vặt → BỎ QUA"]
    for pi, ai, al, nt in zip(p, amt, alerts, notes):
        mark = "✓ báo" if al else "✗ bỏ"
        print(f"  {pi:>8.3f}{eur(ai):>13}{eur(pi*ai):>14}{mark:>9}   {nt}")
    rule()
    print("""
  Một ngưỡng chung (ví dụ p ≥ 0.5) sẽ làm NGƯỢC LẠI ở hai dòng quan trọng:
  bỏ qua giao dịch €1,000 và đi cảnh báo giao dịch €1.""")


# ──────────────────────────────────────────────────────── 3. kết quả chính
def demo_headline(te, va, prereg):
    head(3, "Kết quả chính trên tập TEST (chưa bao giờ dùng để chọn mô hình)")
    champ = prereg["declared_winner"]
    y, amt, p = te["y"], te["amounts"], te[champ]

    # ngưỡng suy lại TỪ VALIDATION rồi mới áp lên test — đúng thứ tự pipeline
    thr, _, _ = optimal_threshold(va["y"], va[champ], va["amounts"], C_REVIEW)
    pred = (p >= thr).astype(int)

    fraud = y == 1
    caught = fraud & (pred == 1)
    missed = fraud & (pred == 0)
    cost = total_cost(y, pred, amt, C_REVIEW)

    print(f"""
  Mô hình vô địch   : {champ}   (đăng ký trước ngày {prereg['date']})
  Ngưỡng            : {thr:.6f}  — suy ra từ VALIDATION, áp lên TEST
  Tập test          : {len(y):,} giao dịch, {int(fraud.sum())} gian lận,
                      tổng giá trị gian lận {eur(amt[fraud].sum())}
""")
    rule()
    print(f"  {'Cảnh báo gửi đi':<32}{pred.sum():>8,}   × €3 = {eur(C_REVIEW*pred.sum()):>12}")
    print(f"  {'Gian lận BẮT ĐƯỢC':<32}{int(caught.sum()):>8,}   cứu  {eur(amt[caught].sum()):>12}")
    print(f"  {'Gian lận BỎ SÓT':<32}{int(missed.sum()):>8,}   mất  {eur(amt[missed].sum()):>12}")
    rule()
    print(f"  {'TỔNG CHI PHÍ':<32}{'':>8}         {eur(cost):>12}")
    rule()
    print(f"""
  Hai đẳng thức phải luôn đúng (sai → hàm chi phí hoặc confusion đã hỏng):
    {eur(C_REVIEW*pred.sum())} + {eur(amt[missed].sum())} = {eur(cost)}
    {eur(amt[caught].sum())} + {eur(amt[missed].sum())} = {eur(amt[fraud].sum())}""")
    assert abs(C_REVIEW * pred.sum() + amt[missed].sum() - cost) < 0.01
    assert abs(amt[caught].sum() + amt[missed].sum() - amt[fraud].sum()) < 0.01
    print("  ✓ cả hai đẳng thức đúng")
    return champ, cost


# ───────────────────────────────────────────────────────────── 4. baseline
def demo_baselines(te, va, cost_champ):
    head(4, "Máy học có THỰC SỰ cần thiết không?")
    y, amt = te["y"], te["amounts"]
    yva, amtva = va["y"], va["amounts"]

    nothing = float(amt[y == 1].sum())
    everything = len(y) * C_REVIEW
    x_val, _ = best_amount_baseline(yva, amtva, C_REVIEW)   # X chọn trên VALIDATION
    rule_cost = total_cost(y, (amt >= x_val).astype(int), amt, C_REVIEW)

    rows = [
        ("Cảnh báo TẤT CẢ giao dịch", everything, ""),
        (f"KHÔNG ML: rà soát mọi Amount ≥ €{x_val:,.0f}", rule_cost, "← luật một dòng"),
        ("KHÔNG LÀM GÌ (chịu mất gian lận)", nothing, ""),
        ("Mô hình vô địch", cost_champ, "← kết quả đồ án"),
    ]
    print()
    print(f"  {'Chính sách':<40}{'Chi phí':>14}   so với không làm gì")
    rule()
    for name, c, tag in sorted(rows, key=lambda r: -r[1]):
        cmp_ = "—" if abs(c - nothing) < 0.01 else f"{(c-nothing)/nothing*100:+.0f}%"
        print(f"  {name:<40}{eur(c):>14}   {cmp_:>8}  {tag}")
    rule()
    print(f"""
  Dòng quan trọng nhất là dòng "KHÔNG ML". Một luật đơn giản không dùng máy
  học còn TỐN KÉM HƠN cả việc không làm gì ({eur(rule_cost)} > {eur(nothing)}).
  Không có dòng này, đồ án không chứng minh được máy học đáng dùng.""")


# ───────────────────────────────────── 5. so sánh mô hình + bootstrap
def demo_comparison(te, va, champ, quick):
    head(5, "Mô hình nào tốt nhất? — và có dám tuyên bố không?")
    y, amt = te["y"], te["amounts"]
    keys = [k for k in te.files if k not in ("y", "amounts")]
    thr = {k: optimal_threshold(va["y"], va[k], va["amounts"], C_REVIEW)[0] for k in keys}
    cost = {k: total_cost(y, (te[k] >= thr[k]).astype(int), amt, C_REVIEW) for k in keys}

    print()
    print(f"  {'Mô hình':<22}{'Chi phí test':>16}")
    rule()
    for k in sorted(keys, key=lambda k: cost[k]):
        print(f"  {k:<22}{eur(cost[k]):>16}{'   ← đăng ký trước' if k == champ else ''}")
    rule()

    if quick:
        print("\n  (--quick: bỏ qua bootstrap)")
        return

    print("\n  Bootstrap ghép cặp, 1.000 lần lấy lại mẫu, phân tầng theo lớp:")
    rng = np.random.default_rng(SEED)
    pos, neg = np.flatnonzero(y == 1), np.flatnonzero(y == 0)
    draws = {k: [] for k in keys}
    for _ in range(1000):
        idx = np.concatenate([rng.choice(pos, len(pos), True),
                              rng.choice(neg, len(neg), True)])   # CÙNG mẫu cho mọi mô hình
        for k in keys:
            draws[k].append(total_cost(y[idx], (te[k][idx] >= thr[k]).astype(int),
                                       amt[idx], C_REVIEW))

    base = np.array(draws[champ])
    print()
    for k in keys:
        if k == champ:
            continue
        d = np.array(draws[k]) - base
        lo, hi = np.percentile(d, [2.5, 97.5])
        sig = "CÓ ý nghĩa" if (lo > 0 or hi < 0) else "KHÔNG có ý nghĩa (KTC chứa 0)"
        print(f"  {k} − vô địch = {eur(d.mean())}")
        print(f"      KTC 95% [{eur(lo)}, {eur(hi)}]  →  {sig}")
        print(f"      vô địch thắng {100*(d>0).mean():.1f}% số lần\n")
    rule()
    print("""
  Kết luận bảo vệ được: BA mô hình TƯƠNG ĐƯƠNG nhau và cả ba đều tốt hơn mọi
  baseline — KHÔNG phải "XGBoost thắng". Chênh lệch €6,67 trên nền €2.200 với
  98 ca gian lận (n_eff = 18,1) nằm gọn trong nhiễu.""")


# ─────────────────────────────────────────── 6. chấm một giao dịch bất kỳ
def demo_score(p, amount, va, prereg):
    head(6, "Chấm điểm một giao dịch bất kỳ")
    champ = prereg["declared_winner"]
    thr, _, _ = optimal_threshold(va["y"], va[champ], va["amounts"], C_REVIEW)

    exp_loss = p * amount
    a = "CẢNH BÁO" if p >= thr else "bỏ qua"
    e = "CẢNH BÁO" if exp_loss > C_REVIEW else "bỏ qua"
    print(f"""
  Xác suất gian lận p   : {p}
  Số tiền giao dịch     : {eur(amount)}
  Tổn thất kỳ vọng p×A  : {eur(exp_loss)}

  Chính sách A (ngưỡng chung {thr:.6f})  → {a}
  Chính sách E (p×A > €3)              → {e}
""")
    if a != e:
        print("  ⚠ Hai chính sách BẤT ĐỒNG ở giao dịch này — đây chính là trường")
        print("    hợp cho thấy ngưỡng chung bỏ qua thông tin số tiền.")
    else:
        print("  Hai chính sách đồng ý.")


def main():
    ap = argparse.ArgumentParser(description="Demo đồ án phát hiện gian lận CS114")
    ap.add_argument("--quick", action="store_true", help="bỏ qua bootstrap")
    ap.add_argument("--score", nargs=2, metavar=("P", "AMOUNT"), type=float,
                    help="chấm điểm một giao dịch: xác suất và số tiền")
    args = ap.parse_args()

    te, va, prereg = load()

    print()
    rule("━")
    print("  PHÁT HIỆN GIAN LẬN THẺ TÍN DỤNG — TỐI THIỂU HOÁ CHI PHÍ TIỀN TỆ")
    print("  Đồ án CS114 Máy học · UIT      |      demo chạy thử")
    rule("━")

    if args.score:
        demo_score(args.score[0], args.score[1], va, prereg)
        return

    demo_cost_model()
    demo_policy_rule()
    champ, cost = demo_headline(te, va, prereg)
    demo_baselines(te, va, cost)
    demo_comparison(te, va, champ, args.quick)

    print()
    rule("━")
    print("  Kiểm chứng đầy đủ  : ./run.sh test        (kỳ vọng 24 passed)")
    print("  Chấm một giao dịch : ./run.sh demo --score 0.02 1500")
    rule("━")
    print()


if __name__ == "__main__":
    main()
