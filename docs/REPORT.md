# Phát hiện gian lận thẻ tín dụng theo hướng tối thiểu hoá chi phí

**Đồ án môn học CS114 — Máy học · Trường Đại học Công nghệ Thông tin, ĐHQG-HCM**

---

## 1. Tóm tắt đề tài

Đồ án xây dựng một hệ thống phát hiện gian lận thẻ tín dụng (credit card fraud
detection) trên bộ dữ liệu ULB/Kaggle `mlg-ulb/creditcardfraud` gồm 284.807 giao
dịch, trong đó chỉ có 492 giao dịch gian lận (0,173%).

Điểm khác biệt của đồ án là **hàm mục tiêu**. Thay vì tối ưu accuracy hay
F1-score, nhóm tối ưu trực tiếp **chi phí tiền tệ kỳ vọng**:

```
TotalCost = c_review × (TP + FP) + Σ (Amount của các FN)
```

trong đó `c_review = 3 EUR` là chi phí để một nhân viên rà soát một giao dịch bị
cảnh báo (trả cho **mọi** cảnh báo, vì tại thời điểm rà soát ta chưa biết nhãn),
còn mỗi giao dịch gian lận bị bỏ sót gây thiệt hại đúng bằng số tiền của nó.

Từ hàm mục tiêu này nảy ra **phát hiện chính của đồ án**: **205 trên 492 giao
dịch gian lận (42%) có giá trị nhỏ hơn chính phí rà soát 3 EUR**, và 27 giao dịch
có giá trị đúng bằng 0 EUR. Một chính sách tối ưu về chi phí do đó **cố ý bỏ qua
gần một nửa số vụ gian lận** — rà soát một vụ gian lận 1 EUR tốn 3 EUR, tức là lỗ
2 EUR để "bắt" được nó.

Nhóm huấn luyện 3 họ mô hình (hồi quy logistic — logistic regression, rừng ngẫu
nhiên — random forest, XGBoost) × 2 cách xử lý mất cân bằng (không xử lý / dùng
`class_weight='balanced'`), tổng cộng 6 cấu hình. Kết quả trên tập test:

- Cả ba mô hình đều **giảm ~79% chi phí** so với việc không làm gì (2.223,93 EUR
  so với 10.644,93 EUR).
- Một quy tắc không dùng máy học ("rà soát mọi giao dịch ≥ 549 EUR") tốn
  **12.398,63 EUR — tệ hơn cả việc không làm gì**. Đây là bằng chứng cho thấy máy
  học thực sự cần thiết ở đây.
- **Không thể tuyên bố mô hình nào thắng.** Khoảng cách giữa mô hình đăng ký
  trước (xgb/balanced) và hồi quy logistic chỉ là **6,67 EUR** trên nền 2.200 EUR,
  và mô hình vô địch chỉ thắng trong **53,3%** số lần bootstrap — tức gần như tung
  đồng xu. Kết luận trung thực và bảo vệ được là: *ba mô hình tương đương nhau, và
  cả ba đều tốt hơn mọi baseline*.

---

## 2. Giới thiệu bài toán & dataset

### 2.1. Bài toán

Phân loại nhị phân: với mỗi giao dịch, quyết định **cảnh báo** (đưa sang bộ phận
rà soát) hay **bỏ qua**. Bài toán có ba đặc điểm khiến các thước đo quen thuộc
không dùng được:

1. **Mất cân bằng cực đoan** (0,173% dương tính). Một mô hình luôn trả lời "hợp
   lệ" đạt accuracy 99,83% mà vô dụng hoàn toàn.
2. **Chi phí bất đối xứng**. Một FP tốn 3 EUR cố định; một FN tốn từ 0 EUR đến
   2.125,87 EUR.
3. **Chi phí là một tổng đuôi nặng (heavy-tailed sum)**, nên phương sai của ước
   lượng rất lớn — phần 6.7 sẽ định lượng điều này.

### 2.2. Dataset

| Thuộc tính | Giá trị |
|---|---|
| Số dòng | 284.807 |
| Số cột | 31 |
| Giá trị thiếu (null) | 0 |
| Giao dịch gian lận | 492 (0,173%) |
| Khoảng thời gian `Time` | 172.792 giây = **48,0 giờ** |
| Đơn vị `Amount` | EUR |

Các cột `V1`–`V28` là **thành phần chính đã ẩn danh** (anonymised PCA
components) — bộ dữ liệu gốc không công bố ý nghĩa của chúng. Hai cột còn lại là
`Time` (giây tính từ giao dịch đầu tiên) và `Amount` (số tiền). Nhãn là `Class`.

**Lưu ý quan trọng, phải nói rõ:** `V1`–`V28` được fit PCA trên **toàn bộ 48
giờ**. Vì vậy, một phép chia theo thời gian (temporal split) **không thể loại bỏ
được look-ahead** — thông tin tương lai đã nằm sẵn trong chính hệ cơ sở đặc trưng
trước khi ta chạm vào dữ liệu. Nhóm báo cáo phép kiểm tra ngày 1 → ngày 2 thuần
tuý như một **kiểm tra dịch chuyển phân phối (distribution-shift check)**, không
bao giờ như một biện pháp khắc phục rò rỉ dữ liệu.

---

## 3. EDA + biểu đồ

Toàn bộ phần này nằm trong `notebooks/01_eda.ipynb`.

### 3.1. Phân bố lớp

Biểu đồ cột số lượng theo lớp phải vẽ ở **thang log** mới thấy được lớp gian lận —
ở thang tuyến tính cột gian lận gần như vô hình. Đó là hình minh hoạ trực quan cho
lý do accuracy vô dụng ở bài toán này.

### 3.2. Phân bố `Amount` theo lớp

| | Gian lận | Hợp lệ |
|---|---|---|
| count | 492 | 284.315 |
| mean | 122,21 EUR | 88,29 EUR |
| **median** | **9,25 EUR** | **22,00 EUR** |
| std | 256,42 EUR | 250,10 EUR |
| max | 2.125,87 EUR | 25.691,16 EUR |

Giả định ban đầu của nhóm ("gian lận có số tiền nhỏ hơn") **sai ở giá trị trung
bình**. Giao dịch gian lận **điển hình** thì nhỏ (trung vị 9,25 EUR, chưa bằng nửa
trung vị 22,00 EUR của giao dịch hợp lệ), nhưng **trung bình** lại lớn hơn vì đuôi
phải rất nặng. Không mô tả được bằng "nhỏ hơn" hay "lớn hơn" — phân bố **lưỡng cực
về mặt chi phí**. Histogram `Amount` thang log theo lớp là hình thể hiện rõ nhất.

### 3.3. Phát hiện đầu đề

**205 / 492 giao dịch gian lận (42%) có giá trị dưới 3 EUR; 27 giao dịch đúng
bằng 0 EUR.**

Hệ quả trực tiếp: chính sách tối ưu chi phí **cố ý** bỏ qua chúng. Với giao dịch
0 EUR, tổn thất kỳ vọng khi bỏ qua là 0 EUR còn rà soát tốn 3 EUR — không quy tắc
hợp lý nào nên cảnh báo. Đây là câu trả lời cho "tại sao mô hình bỏ sót hẳn một số
vụ gian lận?".

### 3.4. Tỉ lệ gian lận theo giờ trong ngày

Tỉ lệ gian lận theo `hour_of_day` cao hơn mức nền chung ở các giờ đêm — lý do nhóm
giữ lại thông tin giờ (mã hoá theo chu kỳ) thay vì vứt bỏ hoàn toàn cột `Time`.

### 3.5. Các hằng số đã kiểm chứng

| Hằng số | Giá trị |
|---|---|
| Tổng `Amount` gian lận (baseline "không làm gì") | **60.127,97 EUR** |
| Baseline "cảnh báo tất cả" | 284.807 × 3 EUR = **854.421 EUR** (**tệ hơn 14,2×** so với không làm gì) |
| Hệ số biến thiên CV của `Amount` gian lận | 2,100 |
| **n_eff cho tập test 98 gian lận** | **18,1** |
| Ngày 1 | 281 gian lận |
| Ngày 2 | 211 gian lận |

---

## 4. Tiền xử lý dữ liệu

Mã nguồn: `preprocessing.py` (có unit test trong `tests/test_preprocessing.py`).

1. **Bỏ hẳn cột `Time` thô làm đặc trưng.** Dưới phép chia ngẫu nhiên, `Time` cho
   phép mô hình học thuộc vị trí các "cụm" gian lận — rò rỉ thật sự, và nó làm hỏng
   luôn phép kiểm tra theo thời gian.
2. **Thay bằng `hour_of_day = (Time // 3600) % 24`, mã hoá theo chu kỳ**
   (`sin`/`cos`). Nếu chia tỉ lệ tuyến tính, 23:00 và 00:00 sẽ nằm ở hai đầu đối
   lập của miền giá trị dù chỉ cách nhau một giờ.
3. **`log1p(Amount)`** rồi chuẩn hoá. `V1`–`V28` giữ nguyên vì đã là đầu ra PCA.
4. **Chia tầng (stratified) 60/20/20** với `random_state=42`. Ở tỉ lệ dương tính
   0,173%, chia tầng là bắt buộc — chia ngẫu nhiên thuần có thể để lại một tập gần
   như không có giao dịch gian lận nào.
5. **`StandardScaler` chỉ fit trên tập train.** Có assert kiểm tra
   `scaler.n_samples_seen_ == len(train)` ngay trong `run_model_matrix.py` để bắt
   lỗi rò rỉ.

Tập test cuối cùng: **56.962 dòng, 98 giao dịch gian lận, tổng giá trị gian lận
10.644,93 EUR**.

---

## 5. Mô hình và thông số

Ma trận 3 họ × 2 nhánh xử lý mất cân bằng, tất cả để **ở tham số mặc định** và
đều có `random_state=42` (`run_model_matrix.py`):

| Họ mô hình | Tham số |
|---|---|
| Hồi quy logistic (logistic regression) | `max_iter=1000` |
| Rừng ngẫu nhiên (random forest) | `n_estimators=100`, `n_jobs=-1` |
| XGBoost | `tree_method='hist'`, `eval_metric='aucpr'` |

Hai nhánh: `none` (không xử lý) và `balanced` (`class_weight='balanced'`; với
XGBoost là `scale_pos_weight` bằng tỉ lệ lớp).

### 5.1. Hai chính sách quyết định

- **Chính sách A** — ngưỡng toàn cục `t*` được dò trên tập validation để tối
  thiểu hoá `TotalCost`. Phép dò được cài bằng sort + cumsum, và **chỉ đánh giá
  tại các ngưỡng thực sự đạt được** (`np.unique`): rừng ngẫu nhiên 100 cây chỉ
  sinh ra ~101 giá trị xác suất khác nhau, nên một cực tiểu kiểu "top-k" nằm giữa
  một khối giá trị trùng nhau là **không quy tắc ngưỡng nào thực hiện được**.
- **Chính sách E** — quy tắc phụ thuộc số tiền: `cảnh báo ⟺ p × Amount >
  c_review`. Đây là **quy tắc tối ưu Bayes cho đúng hàm mục tiêu này**, và **không
  có tham số tự do nào**. Diễn giải: "tổn thất kỳ vọng khi để lọt là xác suất ×
  số tiền; nếu nó vượt 3 EUR thì hãy trả 3 EUR".

Chính sách A là trường hợp đặc biệt của E khi thay mọi `Amount` bằng một hằng số
`Ā`, với `t = c_review / Ā`. Ví dụ ngưỡng `t* = 0,0677` của logreg/none tương
đương giả định mọi giao dịch đều đáng **44,30 EUR**.

**Lưu ý bắt buộc:** `class_weight='balanced'` thổi phồng xác suất dự đoán lên
khoảng nghịch đảo tỉ lệ lớp. Trước khi áp dụng Chính sách E cho nhánh `balanced`,
nhóm hiệu chỉnh dịch chuyển tiên nghiệm bằng `fraud_cost.undo_class_weight`. Bỏ
qua bước này thì mô hình sẽ cảnh báo trên một phần rất lớn tập test — **âm thầm,
với một con số chi phí trông vẫn hợp lý**.

### 5.2. Đăng ký trước mô hình vô địch

Sau khi xếp hạng **chỉ trên tập validation**, nhóm ghi nhà vô địch ra đĩa
(`artifacts/preregistration.json`, ngày 2026-09-13) **trước khi chấm tập test lần
đầu tiên**. Test được `predict_proba` đúng một lần cho mỗi mô hình; mọi phân tích
sau đó là hậu xử lý trên mảng đã lưu.

---

## 6. Kết quả và phân tích

### 6.1. Kết quả trên tập validation (6 cấu hình)

| Cấu hình | Chi phí val | PR-AUC | Tỉ lệ cảnh báo |
|---|---|---|---|
| logreg/none | 3.419,35 EUR | 0,7142 | 0,160% |
| logreg/balanced | 3.561,31 EUR | 0,6686 | 0,186% |
| rf/none | 3.382,76 EUR | 0,7992 | 0,139% |
| rf/balanced | 3.390,00 EUR | 0,7981 | 0,144% |
| xgb/none | 3.160,05 EUR | 0,8200 | 0,276% |
| **xgb/balanced** | **3.052,05 EUR** | **0,8228** | 0,212% |

Mỗi họ chọn một đại diện tốt nhất: **xgb/balanced, rf/none, logreg/none**. Nhóm cố
ý **không** lấy top-3 toàn cục — làm vậy có thể chọn ra ba biến thể của cùng một
thuật toán, vi phạm yêu cầu "tối thiểu 3 mô hình" trong khi trông như vẫn thoả.

### 6.2. Máy học có xứng đáng không?

| Chính sách | Chi phí test | So với không làm gì |
|---|---|---|
| Cảnh báo tất cả | 170.886,00 EUR | tệ hơn 16× |
| **Không dùng ML: rà soát `Amount ≥ 549 EUR`** | **12.398,63 EUR** | **tệ hơn cả không làm gì** |
| Không làm gì | 10.644,93 EUR | — |
| logreg/none | 2.231,31 EUR | −79% |
| rf/none | 2.453,93 EUR | −77% |
| **xgb/balanced (vô địch)** | **2.223,93 EUR** | **−79%** |

Ngưỡng `X = 549 EUR` được chọn **trên tập validation**, y hệt ngưỡng của mô hình —
không bao giờ trên test. Dòng quan trọng nhất là dòng baseline không-ML: thiếu nó,
đồ án **không thể** khẳng định máy học là cần thiết; có nó, khẳng định đó đứng vững.

### 6.3. Câu hỏi 3 — Phân tích precision, recall, F1-score

Confusion matrix của mô hình vô địch (xgb/balanced) trên tập test tại ngưỡng
Chính sách A:

| | Dự đoán: hợp lệ | Dự đoán: gian lận |
|---|---|---|
| **Thực tế: hợp lệ** | TN = 56.817 | FP = 47 |
| **Thực tế: gian lận** | FN = 13 | TP = 85 |

| Thước đo | Giá trị |
|---|---|
| Precision | 85/132 = **64,4%** |
| Recall | 85/98 = **86,7%** |
| F1-score | **0,739** |
| Accuracy | **99,89%** |
| PR-AUC (test) | **0,8693** |

**Accuracy 99,89% là con số vô nghĩa**, đưa vào đây chỉ để chứng minh điều đó: mô
hình luôn trả lời "hợp lệ" đã đạt 99,83%. Precision 64,4% nghĩa là cứ 3 cảnh báo
thì khoảng 1 là báo động giả — chấp nhận được, vì mỗi báo động giả chỉ tốn 3 EUR
trong khi một vụ gian lận bắt được có thể đáng hàng trăm EUR. Đó là lý do nhóm tối
ưu chi phí chứ không tối ưu F1: **F1 coi một FP và một FN nặng như nhau, hàm chi
phí thì không**.

PR-AUC trên tập test của ba mô hình: xgb/balanced **0,8693**, rf/none **0,8689**,
logreg/none **0,7406**.

### 6.4. Câu hỏi 4 — Phân tích confusion matrix: model hay nhầm class nào?

Bài toán là nhị phân nên không có ma trận đa lớp; câu hỏi thực chất là **nhầm
theo hướng nào**.

- **Hướng FN (bỏ sót gian lận):** 13/98 vụ, chiếm 13,3% của lớp gian lận.
- **Hướng FP (báo nhầm giao dịch hợp lệ):** 47 vụ trên 56.864 giao dịch hợp lệ,
  tức chỉ **0,083%** của lớp hợp lệ.

Tính theo tỉ lệ trong lớp, mô hình **nhầm nhiều hơn theo hướng bỏ sót gian lận**
(13,3% so với 0,083%); tính theo số tuyệt đối thì FP nhiều hơn FN (47 so với 13).
Đáng chú ý: **trung vị `Amount` của các FP là 1,00 EUR**, so với 22,00 EUR của toàn
bộ giao dịch hợp lệ. Báo động giả tập trung vào những giao dịch **rất nhỏ** — ma sát
rơi vào các khoản mua vặt chứ không vào giao dịch lớn mà khách hàng cần xử lý gấp.
Đây là **quan sát thực nghiệm**, không phải hệ quả tất yếu.

Hai mô hình còn lại phát ra 80 cảnh báo (rf/none) và 110 cảnh báo (logreg/none),
so với 132 cảnh báo của mô hình vô địch.

### 6.5. Câu hỏi 5 — Phân tích lỗi

Chi tiết trong `notebooks/02_error_analysis.ipynb`.

| Chỉ số | Giá trị |
|---|---|
| Gian lận bắt được | 85/98 (**86,7%**) |
| Giá trị thu hồi được | **8.817,00 EUR** (82,8% của 10.644,93 EUR) |
| Giá trị mất do bỏ sót | **1.827,93 EUR** |

Biểu đồ đầu đề là **gian lận bỏ sót theo decile của `Amount`**, và nó phải đọc
bằng hai bảng cạnh nhau:

- **Decile 5 có tỉ lệ bỏ sót cao nhất: 40%.**
- **Nhưng decile 10 mới là nơi mất tiền: 1.684,00 EUR trên tổng 1.827,93 EUR** —
  tức **92% toàn bộ thiệt hại do bỏ sót nằm ở decile đắt nhất**.

Đây là bài học phương pháp luận trung tâm của đồ án: **đếm số lỗi và đếm tiền mất
là hai câu chuyện khác nhau**. Một biểu đồ false-negative thuần theo số lượng sẽ chỉ
thẳng vào decile 5 và khiến ta tối ưu sai chỗ; muốn giảm chi phí phải xử lý decile 10.

### 6.6. Câu hỏi 6 — So sánh train vs validation: overfitting hay underfitting?

So sánh bằng **PR-AUC**, không dùng chi phí. Lý do phải nói rõ: ngưỡng `t*` được
chọn trên chính tập validation đó, nên precision/recall/F1/chi phí *tại* `t*` trên
validation bị thiên lệch lạc quan. PR-AUC độc lập với ngưỡng nên không dính lỗi
này.

| Mô hình | PR-AUC train | PR-AUC val | Khoảng cách |
|---|---|---|---|
| rf/none | 1,0000 | 0,7992 | **+0,2008** |
| xgb/balanced | 1,0000 | 0,8228 | **+0,1772** |
| logreg/none | 0,7925 | 0,7142 | **+0,0784** |

**Chẩn đoán:** rừng ngẫu nhiên và XGBoost **overfit rõ rệt** — cả hai đạt PR-AUC
train đúng bằng 1,0000, nghĩa là cây không cắt tỉa đã cô lập được từng dòng gian lận
riêng lẻ trong tập train; khoảng cách ~0,18–0,20 chính là phần "học thuộc lòng"
không tổng quát hoá được.

Hồi quy logistic **không overfit** (khoảng cách +0,0784) nhưng cũng **không underfit
hẳn**: PR-AUC train 0,7925 thấp hơn hẳn hai mô hình kia, cho thấy mô hình tuyến tính
không tách hết cấu trúc dữ liệu, nhưng 0,7142 trên validation vẫn dùng được. Nó là
mô hình **thiên lệch cao — phương sai thấp** trong bộ ba.

Đáng chú ý: overfit nhiều nhất (rf) **không** đồng nghĩa tệ nhất trên test — rf/none
vẫn giảm 77% chi phí; còn mô hình overfit ít nhất (logreg) có chi phí test gần như
bằng mô hình tốt nhất.

### 6.7. Câu hỏi 8 — Những điều gì ảnh hưởng đến kết quả?

**(a) Cỡ mẫu hiệu dụng — yếu tố lớn nhất.** Tập test có 98 giao dịch gian lận,
nhưng vì chi phí là một **tổng đuôi nặng** với CV = 2,100, cỡ mẫu hiệu dụng cho
đại lượng chi phí chỉ là **n_eff = 18,1**, không phải 98. Đây là lý do gốc khiến
không thể phân biệt được ba mô hình (phần 7.1).

**(b) Giá trị `c_review`.** Nhóm quét `c_review` từ 1 đến 20 EUR. Có một điểm
tinh tế: `c_review` nằm **bên trong** công thức của Chính sách E, nên quét nó
**làm thay đổi chính chính sách đó**, chứ không chỉ thay đổi cách đánh giá. Ngoài
ra, quét `c_review` từ 3 lên 20 EUR **tương đương** (sai khác một hằng số cộng)
với việc giữ nguyên 3 EUR trong khi tỉ lệ thu hồi trên vụ gian lận bắt được **giảm
từ 100% xuống 15%**.

**(c) Cách xử lý mất cân bằng.** `class_weight='balanced'` giúp XGBoost
(3.160,05 → 3.052,05 EUR trên validation) nhưng **làm hại** hồi quy logistic
(3.419,35 → 3.561,31 EUR, PR-AUC rơi từ 0,7142 xuống 0,6686). Không có kết luận
chung kiểu "cân bằng lớp thì tốt hơn".

**(d) Hiệu chuẩn xác suất (calibration).** Xem phần 7.3 — đây là lý do Chính sách
E thua.

**(e) Giới hạn đã biết, nêu rõ chứ không giấu.** Mô hình chi phí không tính chi
phí ma sát/khách hàng rời bỏ do báo động giả. Khoản này **không thể** hấp thụ bằng
cách chỉnh `c_review`, vì nó chỉ tác động lên FP. Thêm ma sát sẽ **đẩy ngưỡng tối
ưu lên cao hơn**, nên kết luận "ngưỡng tối ưu thấp hơn 0,5 rất nhiều" là kết luận
thận trọng theo hướng sai — cần nói ra.

---

## 7. So sánh mô hình

### 7.1. Câu hỏi 1 & 2 — Model nào tốt nhất, chênh lệch nhau bao nhiêu?

Bootstrap ghép cặp, 1.000 lần lặp phân tầng theo lớp, mọi mô hình được chấm trên
**cùng một mẫu lặp lại**:

| Mô hình | Chi phí trung bình | KTC 95% |
|---|---|---|
| xgb/balanced | 2.234,70 EUR | [529,92 ; 4.413,90] |
| logreg/none | 2.241,36 EUR | [535,84 ; 4.444,43] |
| rf/none | 2.474,28 EUR | [697,00 ; 4.605,12] |

Chênh lệch ghép cặp so với mô hình đăng ký trước:

| So sánh | Δ trung bình | KTC 95% | Kết luận |
|---|---|---|---|
| logreg/none − vô địch | **6,67 EUR** | [−67,41 ; 93,32] | **không có ý nghĩa thống kê** |
| rf/none − vô địch | 239,59 EUR | [−145,01 ; 928,43] | **không có ý nghĩa thống kê** |

**Câu trả lời cho Câu hỏi 1: không thể nêu tên mô hình tốt nhất.** Mô hình đăng
ký trước chỉ thắng hồi quy logistic trong **53,3%** số lần bootstrap — về mặt
thống kê đó là tung đồng xu.

**Câu trả lời cho Câu hỏi 2: 6,67 EUR** giữa mô hình đứng nhất và đứng nhì (trên
nền 2.200 EUR, tức 0,3%), và **239,59 EUR** giữa nhất và ba. Cả hai khoảng tin
cậy đều chứa số 0.

Đây đúng là điều kế hoạch đã dự báo: với 98 gian lận và chi phí đuôi nặng
(n_eff = 18,1), khoảng cách 6,67 EUR nằm sâu trong vùng nhiễu. Nhóm đã **cam kết
trước** sẽ báo cáo "không có khác biệt có ý nghĩa" như một kết quả hợp lệ, thay vì
tô vẽ nó thành một chiến thắng.

> **Khẳng định bảo vệ được là: "ba mô hình tương đương nhau, và cả ba đều tốt hơn
> mọi baseline", chứ không phải "XGBoost thắng".**

### 7.2. Câu hỏi 7 — Model nào phù hợp với dữ liệu?

Vì ba mô hình không phân biệt được về chi phí, tiêu chí chọn phải chuyển sang các
yếu tố khác:

| Tiêu chí | logreg/none | rf/none | xgb/balanced |
|---|---|---|---|
| Chi phí test | 2.231,31 EUR | 2.453,93 EUR | **2.223,93 EUR** |
| PR-AUC test | 0,7406 | 0,8689 | **0,8693** |
| Khoảng cách train→val | **+0,0784** | +0,2008 | +0,1772 |
| Thời gian huấn luyện | **0,2 s** | 5,8 s | 1,1 s |
| Khả năng giải thích | **cao** | thấp | thấp |

**Khuyến nghị của nhóm: hồi quy logistic (logreg/none).** Chi phí không phân biệt
được với mô hình tốt nhất (chênh 6,67 EUR, không có ý nghĩa thống kê), huấn luyện
nhanh hơn ~29 lần, overfit ít hơn hẳn, và giải thích được. Khi hai lựa chọn không
phân biệt được về kết quả, nên chọn cái đơn giản hơn.

Ngược lại, nếu ưu tiên chất lượng **xếp hạng** (để dùng cho các ngưỡng vận hành khác
trong tương lai) thì PR-AUC 0,8693 của XGBoost vượt rõ 0,7406 của hồi quy logistic —
khác biệt này là thật, chỉ là nó không chuyển thành chênh lệch chi phí ở điểm vận
hành cụ thể này.

### 7.3. So sánh Chính sách A và Chính sách E

| Mô hình | Chính sách A | Chính sách E | E − A (bootstrap ghép cặp) |
|---|---|---|---|
| xgb/balanced | 2.223,93 EUR | 2.316,64 EUR | +100,95 EUR, không có ý nghĩa |
| rf/none | 2.453,93 EUR | 2.415,60 EUR | −16,52 EUR, không có ý nghĩa |
| logreg/none | 2.231,31 EUR | 2.431,08 EUR | **+199,23 EUR, CÓ ý nghĩa — E tệ hơn** |

**Chính sách E đã không thắng.** Quy tắc tối ưu Bayes về mặt lý thuyết hoá ra
không phân biệt được với một ngưỡng đã dò đối với hai mô hình, và **tệ hơn có ý
nghĩa thống kê** với hồi quy logistic. Nhóm nêu điều này thẳng, không tô vẽ.

**Tại sao?** (`notebooks/03_calibration.ipynb`)

Hiệu chuẩn **tổng hợp** thì tốt cho cả ba mô hình — tỉ lệ (p dự đoán trung
bình / tỉ lệ gian lận quan sát) lần lượt là 0,71× / 1,04× / 1,02×. Vậy
miscalibration đơn giản **không** giải thích được.

Nhưng Chính sách E không so `p` với một ngưỡng chung; nó so `p` với ngưỡng **riêng
cho từng giao dịch** `c_review / Amount_i` — 0,3 cho giao dịch 10 EUR, nhưng 0,003
cho giao dịch 1.000 EUR. Tách hiệu chuẩn theo từng decile, tỉ lệ dao động từ
**0,23× đến 2,47×**: hiệu chuẩn tổng hợp tốt chỉ có nghĩa là các sai lệch cục bộ
triệt tiêu lẫn nhau khi lấy trung bình.

Tại đúng biên quyết định của mỗi mô hình:

| Mô hình | Tỉ lệ hiệu chuẩn tại biên | n |
|---|---|---|
| xgb/balanced | 0,77× | **chỉ 10 — quá ít để tin** |
| rf/none | 1,46× | 360 |
| logreg/none | 0,70× | 345 |

**Cảnh báo phải nêu: con số 0,77× của XGBoost dựa trên chỉ 10 quan sát và không
đáng tin.** Nhóm báo cáo nó kèm cỡ mẫu chứ không dùng nó để lập luận.

Nhóm đã thử hiệu chuẩn lại (recalibration). Kết quả: **làm Chính sách E tệ hơn
cho 2 trên 3 mô hình.** Giải thích trung thực là **hiệu chuẩn ở đuôi cộng với
khan hiếm dữ liệu**: ở tỉ lệ nền 0,173%, đơn giản là không có đủ giao dịch gian
lận để ước lượng `p` đủ chính xác ở những vùng xác suất mà Chính sách E cần.

Điều vẫn còn giá trị: Chính sách E **không có tham số tự do nào**, trong khi ngưỡng
của Chính sách A được fit trên validation. Việc E theo kịp một ngưỡng đã dò (xgb,
rf) mà không cần dò gì cả là quan sát thật — nhưng không phải kết quả "E thắng A"
mà kế hoạch hy vọng.

---

## 8. Kết luận

1. **Máy học là cần thiết, và điều đó đã được chứng minh chứ không phải giả
   định.** Baseline không-ML "rà soát mọi giao dịch ≥ 549 EUR" tốn 12.398,63 EUR,
   **tệ hơn cả việc không làm gì** (10.644,93 EUR). Cả ba mô hình đều giảm khoảng
   79% chi phí, về mức ~2.230 EUR.

2. **Không thể tuyên bố mô hình nào thắng.** Chênh lệch 6,67 EUR giữa hai mô hình
   đầu bảng, khoảng tin cậy [−67,41 ; 93,32] chứa số 0, tỉ lệ thắng 53,3% trong
   bootstrap — đó là tung đồng xu. Với n_eff = 18,1, đây là kết quả **đã được dự
   báo trước**, không phải thất bại của phương pháp. Một báo cáo nói "chúng tôi
   không phân biệt được các mô hình, và đây là lý do thống kê" mạnh hơn một báo cáo
   trao vương miện cho một mô hình.

3. **Chính sách tối ưu Bayes đã thua.** Chính sách E không thắng Chính sách A, và
   thua có ý nghĩa thống kê với hồi quy logistic. Nguyên nhân là hiệu chuẩn ở đuôi
   (dao động 0,23×–2,47× theo decile) chứ không phải miscalibration tổng hợp. Hiệu
   chuẩn lại còn làm mọi thứ tệ hơn cho 2/3 mô hình.

4. **Phát hiện đáng nhớ nhất: 42% số vụ gian lận rẻ hơn phí rà soát.** Một chính
   sách tối ưu chi phí **cố ý** bỏ qua gần một nửa số vụ gian lận — hệ quả trực
   tiếp, không tránh được, của việc lấy tiền làm hàm mục tiêu, và là câu trả lời
   cho bất kỳ ai hỏi tại sao recall không phải 100%.

5. **Đếm lỗi khác với đếm tiền mất.** Decile 5 có tỉ lệ bỏ sót cao nhất (40%)
   nhưng decile 10 mới gây ra 1.684,00 EUR trên tổng 1.827,93 EUR thiệt hại.

---

## 9. Hướng phát triển

1. **Tăng cỡ mẫu hiệu dụng** — hạn chế ràng buộc nhất. Muốn phân biệt hai mô hình
   chênh nhau 6,67 EUR cần dữ liệu lớn hơn nhiều bậc, hoặc thiết kế đánh giá giảm
   phương sai (ví dụ chọn ngưỡng bằng out-of-fold CV 5 fold, nâng n_eff cho **bước
   chọn** từ ~18 lên ~73 — dù n_eff cho **bước đánh giá** vẫn không đổi).

2. **Hiệu chuẩn có trọng số theo chi phí.** Platt và isotonic tối ưu log-loss trên
   toàn bộ phân bố, trong khi Chính sách E chỉ cần `p` chính xác trong một dải hẹp.
   Một phương pháp hiệu chuẩn đặt trọng số theo `Amount` là hướng tự nhiên, chưa thử.

3. **Đưa chi phí ma sát của FP vào mô hình.** Hiện mô hình giả định một báo động
   giả chỉ tốn đúng 3 EUR công rà soát; bổ sung chi phí trải nghiệm khách hàng sẽ
   đẩy ngưỡng tối ưu lên và có thể đảo ngược thứ hạng.

4. **Huấn luyện nhạy chi phí (cost-sensitive training).** Truyền
   `sample_weight = Amount` cho lớp gian lận và `c_review` cho lớp hợp lệ, tối ưu
   hàm mục tiêu ngay tại lúc huấn luyện thay vì chỉ ở khâu ra quyết định.

5. **Tinh chỉnh siêu tham số.** Toàn bộ đồ án chạy ở tham số mặc định. Với khoảng
   cách train→val +0,2008 của rừng ngẫu nhiên, việc giới hạn `max_depth` /
   `min_samples_leaf` là hướng rõ ràng.

6. **Kiểm tra dịch chuyển phân phối theo thời gian** (ngày 1: 281 gian lận → ngày
   2: 211 gian lận). Phải gọi đúng tên: đây **chỉ là** kiểm tra dịch chuyển phân
   phối, không phải biện pháp chống rò rỉ, vì `V1`–`V28` đã được fit PCA trên cả
   48 giờ. Chỉ có một lần chuyển ngày nên kết quả chỉ mang tính định hướng.

---

## 10. Phụ lục (code)

Toàn bộ mã nguồn nằm trong repo của đồ án. Các con số trong báo cáo này đều tái
tạo được bằng cách chạy `run.sh`.

### 10.1. Module Python

| File | Nội dung |
|---|---|
| `fraud_cost.py` | Hàm chi phí `total_cost`, đường cong chi phí an toàn với giá trị trùng `cost_curve`, `optimal_threshold`, `policy_e_predict` (Chính sách E), `undo_class_weight` (hiệu chỉnh dịch chuyển tiên nghiệm), `best_amount_baseline` (baseline không-ML) |
| `preprocessing.py` | `hour_of_day`, `cyclic_encode_hour`, `stratified_split_60_20_20` |
| `modeling.py` | `select_champion_per_family` — chọn một đại diện cho mỗi họ thuật toán |
| `run_model_matrix.py` | Bước 4: fit 6 cấu hình → chấm validation → **ghi đăng ký trước** → chỉ khi đó mới chấm test |
| `analyse_results.py` | Bước 5/6: baseline, Chính sách A vs E, bootstrap ghép cặp. Thuần hậu xử lý, không fit lại |

### 10.2. Notebook

| File | Nội dung |
|---|---|
| `notebooks/00_cost_model_demo.ipynb` | Minh hoạ hàm chi phí trên ví dụ tính tay |
| `notebooks/01_eda.ipynb` | Bước 1 — EDA, các biểu đồ ở phần 3, các hằng số đã kiểm chứng |
| `notebooks/02_error_analysis.ipynb` | Bước 7 — biểu đồ bỏ sót theo decile, bảng train vs val, phân tích FP, feature importance |
| `notebooks/03_calibration.ipynb` | Bước 6b — hiệu chuẩn ở đuôi: tại sao Chính sách E thua |

### 10.3. Kiểm thử

| File | Nội dung |
|---|---|
| `tests/test_fraud_cost.py` | Unit test hàm chi phí trên fixture tính tay, **có dòng điểm số trùng nhau** — một fixture không có giá trị trùng sẽ không bắt được lỗi này, và lỗi đó im lặng |
| `tests/test_preprocessing.py` | Kiểm tra `hour_of_day` quấn đúng ở ranh giới ngày, chia tầng giữ đúng tỉ lệ |
| `tests/test_modeling.py` | Kiểm tra chọn đúng một đại diện cho mỗi họ |

### 10.4. Artefact

| File | Nội dung |
|---|---|
| `artifacts/preregistration.json` | Tuyên bố nhà vô địch **có ghi ngày (2026-09-13)**, chọn trên validation, trước mọi lần chấm test |
| `artifacts/val_probabilities.npz` | Vector xác suất validation của cả 6 cấu hình |
| `artifacts/test_probabilities.npz` | Vector xác suất test của 3 mô hình đại diện |
| `artifacts/validation_results.csv`, `artifacts/test_results.csv` | Bảng kết quả ở phần 6.1 và 6.2 |

### 10.5. Hàm cốt lõi

Toàn bộ đồ án xoay quanh đúng ba dòng này (`fraud_cost.py`):

```python
def total_cost(y_true, y_pred, amounts, c_review):
    alerts = int(y_pred.sum())
    missed = (y_true == 1) & (y_pred == 0)
    return c_review * alerts + float(amounts[missed].sum())
```

và quy tắc tối ưu Bayes tương ứng (Chính sách E):

```python
def policy_e_predict(probabilities, amounts, c_review):
    return (probabilities * amounts > c_review).astype(int)
```
