# SLIDES.md — Bộ slide thuyết trình (≤15 phút, tối đa 12 slide)

**10 slide · ~1,240 từ lời nói · ~8:50 ở 140 từ/phút · ~10:20 nếu nói chậm 120 từ/phút.**
Còn dư ít nhất 4,5 phút so với mốc cắt cứng 15 phút.

Nguồn số liệu: `docs/RESULTS.md`, `docs/PLAN.md` (mục ràng buộc buổi trình bày),
`notebooks/01_eda.ipynb`, `notebooks/02_error_analysis.ipynb`,
`notebooks/03_calibration.ipynb`. Toàn bộ số liệu bên dưới lấy nguyên văn từ
các nguồn này — không suy diễn thêm.

Nhịp trình bày giả định: **140 từ/phút** (tốc độ nói tiếng Việt thông thường
là 130–150 từ/phút). Mốc thời gian tích luỹ ở mỗi slide được tính lại theo
số từ thực tế của phần **Nói:**.

Ràng buộc: giảng viên cho tối đa **15 phút, tính giờ nghiêm ngặt** (kể chuyện
hội đồng bảo vệ tốt nghiệp bị cắt ngang giữa câu vì hết giờ), sau đó khoảng
**3 câu hỏi trong 1–2 phút**. Giảng viên đã nói rõ hội đồng biết hết các
phương pháp chuẩn — không cần trình bày lý thuyết dài dòng, chỉ cần chứng
minh cách tiếp cận HỢP LÝ và thực nghiệm ĐÚNG.

---

## Slide 1 — Bài toán *(cộng dồn ~00:30)*

- Phát hiện gian lận thẻ tín dụng — Kaggle `mlg-ulb/creditcardfraud`
- 284,807 giao dịch, chỉ 492 gian lận (**0.173%**) — mất cân bằng cực độ
- Câu hỏi thật sự không phải "mô hình nào chính xác nhất" mà là
  **"chính sách nào tốn ít tiền nhất"**

**Nói:** Bài toán của nhóm là phát hiện gian lận thẻ tín dụng trên bộ dữ liệu
Kaggle với gần 285 nghìn giao dịch nhưng chỉ có 492 giao dịch gian lận, tức
0.173%. Với độ mất cân bằng này, nhóm xác định ngay từ đầu: không thể đánh giá
mô hình bằng accuracy, và mục tiêu thật sự phải là tối ưu chi phí, không phải
tối ưu độ chính xác.

**Hình:** không có hình, slide mở đầu.

---

## Slide 2 — HOOK: vì sao không dùng accuracy *(cộng dồn ~01:08)*

- Mô hình dự đoán "không bao giờ có gian lận" → **accuracy = 99.8%**
- Accuracy vô dụng trên dữ liệu lệch lớp này
- Nhóm tối ưu **tiền**, không tối ưu accuracy:
  `TotalCost = c_review × (TP + FP) + Σ Amount(FN)`, với `c_review = €3`

**Nói:** Nếu tụi em xây một mô hình chỉ đơn giản dự đoán "không có gian lận"
cho mọi giao dịch, accuracy vẫn đạt 99.8%. Con số này nghe rất ấn tượng nhưng
hoàn toàn vô nghĩa vì nó không bắt được giao dịch gian lận nào. Vì vậy nhóm
định nghĩa lại mục tiêu bằng đơn vị tiền tệ: chi phí kiểm tra mỗi giao dịch bị
gắn cờ là 3 euro, còn bỏ sót một giao dịch gian lận thì mất đúng số tiền của
giao dịch đó.

**Hình:** biểu đồ class distribution (linear vs log) — `01_eda.ipynb`, mục
"Class distribution".

---

## Slide 3 — Bất ngờ đầu tiên: bỏ sót gian lận là CHỦ Ý *(cộng dồn ~02:36)*

- **205/492 gian lận (42%)** có giá trị THẤP HƠN phí kiểm tra €3
- **27 giao dịch gian lận đúng €0**
- Gian lận trung vị: **€9.25**, giao dịch hợp lệ trung vị: **€22.00**
- → Chính sách tối ưu chi phí **cố ý bỏ qua ~42% số vụ gian lận**

**Nói:** Đây là phát hiện khiến cả nhóm bất ngờ nhất, và tụi em xin đi chậm ở slide này. 42% số vụ gian lận trong bộ dữ liệu — cụ thể là 205 trên 492 vụ — có giá trị nhỏ hơn 3 euro. Xin lấy một ví dụ cụ thể: giả sử có một giao dịch gian lận đúng 1 euro. Nếu mô hình bắt được nó, nhóm phải trả 3 euro cho nhân viên kiểm tra để cứu 1 euro. Tức là bắt được giao dịch đó làm nhóm mất thêm 2 euro chứ không phải tiết kiệm được tiền. Tính gộp lại cho cả 205 vụ: chi phí kiểm tra là 205 nhân 3, bằng 615 euro, trong khi tổng giá trị cứu được chỉ 181 euro. Nghĩa là kiểm tra hết nhóm này phá huỷ 434 euro giá trị. Thậm chí có 27 vụ gian lận đúng 0 euro, bắt được cũng không cứu được đồng nào. Vì vậy một chính sách tối ưu chi phí sẽ chủ động bỏ qua gần một nửa số gian lận — không phải vì mô hình yếu, mà vì đó là lựa chọn kinh tế đúng. Đây là slide nhóm muốn hội đồng nhớ nhất.

**Hình:** biểu đồ phân phối Amount theo lớp (log scale) — `01_eda.ipynb`,
mục "AC-3 — Amount distribution by class" / "🎯 The headline finding".

---

## Slide 4 — Phương pháp *(cộng dồn ~03:12)*

- 3 họ mô hình × 2 chế độ xử lý mất cân bằng: **Logistic Regression, Random
  Forest, XGBoost** × `none` / `balanced`
- Mỗi họ chọn **1 champion trên tập validation** — champion cuối cùng
  (`xgb/balanced`) được **đăng ký trước bằng văn bản** trước khi chạm vào
  tập test
- Tập test chỉ được **chấm điểm một lần** — không bao giờ chọn mô hình/ngưỡng
  dựa trên kết quả test

**Nói:** Nhóm thử nghiệm 3 họ mô hình kinh điển — Logistic Regression, Random
Forest và XGBoost — mỗi mô hình chạy hai chế độ, có và không xử lý mất cân
bằng lớp bằng class weighting. Trên tập validation, mỗi họ chọn ra một
champion. Quan trọng nhất: champion cuối cùng, xgb/balanced, được đăng ký
bằng văn bản trước khi nhóm chạm vào tập test lần nào, để đảm bảo không có
việc "chọn mô hình thắng" sau khi đã nhìn kết quả test.

**Hình:** không bắt buộc hình; có thể dùng bảng validation (6 cấu hình) nếu
còn thời gian — `docs/RESULTS.md` mục 4.

---

## Slide 5 — Kết quả 1: ML thật sự cần thiết *(cộng dồn ~04:36)*

| Chính sách | Chi phí test | So với không làm gì |
|---|---|---|
| Gắn cờ tất cả | €170,886.00 | tệ hơn 16 lần |
| **Không ML: kiểm tra nếu Amount ≥ €549** | **€12,398.63** | **tệ hơn cả không làm gì** |
| Không gắn cờ gì | €10,644.93 | — |
| **xgb/balanced (champion)** | **€2,223.93** | **−79%** |

**Nói:** Trên 56,962 giao dịch test với 98 gian lận trị giá 10,644.93 euro, nếu không làm gì cả thì nhóm mất toàn bộ số đó. Nếu đi thái cực ngược lại, gắn cờ tất cả giao dịch để không bỏ sót vụ nào, chi phí kiểm tra bùng nổ lên 170,886 euro, tệ hơn 16 lần. Nhưng hàng quan trọng nhất trong bảng này là hàng thứ hai — baseline không dùng máy học. Nhóm tự hỏi: nếu chỉ đơn giản kiểm tra mọi giao dịch có giá trị từ 549 euro trở lên, không cần mô hình gì cả, thì kết quả ra sao? Ngưỡng 549 euro này được chọn trên tập validation, không phải test, để so sánh công bằng. Kết quả là 12,398.63 euro — còn tệ hơn cả việc không làm gì. Nhóm nhấn mạnh hàng này vì nếu thiếu nó, cả đồ án không chứng minh được máy học thật sự cần thiết; hoàn toàn có khả năng một luật đơn giản đã đủ tốt. Có hàng này, nhóm mới kết luận được: với máy học, chi phí giảm còn 2,223.93 euro, tức giảm 79% so với không làm gì.

**Hình:** bảng so sánh chi phí (có thể chuyển thành bar chart) —
`docs/RESULTS.md` mục 1.

---

## Slide 6 — Kết quả 2: không thể gọi tên người thắng *(cộng dồn ~06:13)*

- Bootstrap có ghép cặp, 1,000 lần lặp
- logreg − champion: chênh lệch trung bình **€6.67**, CI [−€67.41, €93.32]
  → **không có ý nghĩa thống kê**
- Champion chỉ thắng logreg trong **53.3%** số lần lặp — như tung đồng xu
- Cỡ mẫu hiệu dụng **n_eff = 18.1** (không phải 98)

**Nói:** Đây là phần trung thực nhất của báo cáo, và nhóm xin trình bày thẳng thắn. Khi so sánh champion với Logistic Regression bằng bootstrap có ghép cặp 1,000 lần lặp — nghĩa là mỗi lần lặp cả hai mô hình đều được chấm trên cùng một mẫu lấy lại, để so sánh công bằng — chênh lệch chi phí trung bình chỉ 6.67 euro, và khoảng tin cậy 95% chạy từ âm 67.41 đến dương 93.32, tức là chứa cả số 0. Champion chỉ thắng trong 53.3% số lần lặp, gần như tung đồng xu. Lý do nằm ở cỡ mẫu hiệu dụng. Tập test có 98 gian lận, nhưng chi phí là một tổng bị chi phối bởi vài vụ gian lận rất lớn, nên về mặt thống kê 98 vụ này chỉ hành xử như khoảng 18 vụ độc lập. Chỉ cần một vụ gian lận lớn rơi vào hay rơi ra khỏi tập test là tổng chi phí đã dịch chuyển nhiều hơn khoảng cách giữa các mô hình. Nhóm xin nói rõ quan điểm: báo cáo chênh lệch 6.67 euro như một chiến thắng mới chính là cái sai. Kết luận đúng và bảo vệ được là cả ba mô hình tương đương nhau, và cả ba đều vượt trội mọi baseline. Đây là một phát hiện, không phải một thất bại.

**Hình:** không cần hình phức tạp; có thể dùng bảng bootstrap CI —
`docs/RESULTS.md` mục 2.

---

## Slide 7 — Phân tích lỗi: tỉ lệ bỏ sót ≠ chi phí bỏ sót *(cộng dồn ~07:32)*

- Champion bắt được **85/98 gian lận (86.7%)**, cứu được **€8,817.00 (82.8%)**
- Tỉ lệ bỏ sót cao nhất ở **decile 5 (40%)**
- Nhưng **chi phí** bỏ sót tập trung ở **decile 10**: mất **€1,684.00** trong
  tổng €1,827.93 bị bỏ sót
- Rate và cost **KHÔNG khớp nhau** — đây là lý do phải dùng cost objective

**Nói:** Champion bắt được 85 trong 98 gian lận, tương đương 86.7%, cứu được 8,817 euro tức 82.8% giá trị gian lận, và để mất 1,827.93 euro. Nhóm chia các vụ bỏ sót theo decile giá trị giao dịch, và kết quả cho hai câu trả lời khác nhau tuỳ cách nhìn. Nếu nhìn theo tỉ lệ bỏ sót, decile 5 tệ nhất với 40% số vụ bị bỏ sót. Nhưng nếu nhìn theo số tiền mất đi, decile 10 — nhóm giao dịch giá trị cao nhất — mới là nơi thiệt hại thật, chiếm 1,684 euro trên tổng 1,827.93 euro bị bỏ sót, tức khoảng 92% toàn bộ thiệt hại nằm gọn trong một decile duy nhất. Ý nghĩa thực tiễn rất rõ: một nhóm tối ưu theo recall sẽ dồn công sức vào decile 5, là nơi tỉ lệ lỗi cao nhất nhưng gần như không có tiền, và bỏ qua decile 10 là nơi chứa gần như toàn bộ thiệt hại. Đây chính là lý do vì sao nhóm chọn tối ưu theo chi phí thay vì theo tỉ lệ lỗi.

**Hình:** biểu đồ 2 panel "caught vs missed by Amount decile" (đếm số lượng
và tổng Amount) — `02_error_analysis.ipynb`, mục "AC-16 — missed frauds by
Amount decile (headline chart)".

---

## Slide 8 — Kết luận *(cộng dồn ~08:07)*

- ML **bắt buộc phải có**: không ML thì baseline còn tệ hơn không làm gì
- **Không thể** khẳng định một mô hình duy nhất là tốt nhất — cả 3 tương đương
- Chi phí giảm **79%** so với việc không hành động

**Nói:** Tóm lại, ba kết luận chính: một, machine learning là bắt buộc vì
baseline không dùng ML thậm chí tệ hơn không làm gì cả. Hai, nhóm không thể
và không nên khẳng định một mô hình cụ thể là tốt nhất — cả ba đều tương
đương nhau về mặt thống kê. Ba, dù vậy, việc áp dụng ML vẫn giảm được 79% chi
phí so với việc không hành động, đó là giá trị thực tế của dự án.

**Hình:** không cần hình.

---

## Slide 9 — Hướng phát triển *(cộng dồn ~08:44)*

- Kiểm chứng **hiệu chỉnh xác suất theo vùng đuôi** (tail calibration) — lý do
  Policy E (`p × Amount > c_review`) chưa thắng được ngưỡng đã tinh chỉnh
- Thu thập thêm dữ liệu gian lận thật (n_eff thấp là do quá ít mẫu gian lận)
- Thử active learning / phản hồi từ đội kiểm tra thực tế để cập nhật mô hình

**Nói:** Về hướng phát triển, nhóm đã bắt đầu điều tra vì sao Policy E — quy
tắc không cần tinh chỉnh tham số — chưa vượt được ngưỡng đã tinh chỉnh trên
validation, và manh mối nằm ở việc hiệu chỉnh xác suất bị lệch đúng tại vùng
ngưỡng quyết định, dù hiệu chỉnh tổng thể vẫn tốt. Hướng tiếp theo là kiểm tra
sâu hơn vùng đuôi này, đồng thời tìm cách tăng cỡ mẫu gian lận thật để giảm
phương sai của việc đánh giá.

**Hình:** biểu đồ reliability curve (log-spaced) nếu còn thời gian —
`03_calibration.ipynb`, mục "1. Reliability curves, log-spaced in the
low-probability region".

---

## Slide 10 — Cảm ơn / Hỏi đáp *(cộng dồn ~08:51)*

- Cảm ơn thầy/cô đã lắng nghe
- Sẵn sàng trả lời câu hỏi

**Nói:** Nhóm xin cảm ơn thầy cô đã lắng nghe và sẵn sàng trả lời các câu hỏi.

**Hình:** không cần hình.

---

*(Tổng cộng 10 slide, ước tính ~7 phút nói liên tục theo kịch bản trên —
còn dư nhiều thời gian so với giới hạn 15 phút để xử lý độ trễ khi trình
chiếu, chuyển slide, và trả lời câu hỏi mở rộng nếu hội đồng ngắt lời giữa
chừng. Có thể nói chậm hơn, thêm ví dụ, hoặc kéo dài phần Q&A chuẩn bị mà
vẫn an toàn.)*

---

## Chuẩn bị hỏi đáp

**1. "Tại sao dùng Random Forest / XGBoost? Các bạn chưa học cây quyết
định."**
Cây quyết định (CART) chia dữ liệu đệ quy theo tiêu chí như Gini impurity
hoặc entropy để tối đa hóa độ thuần của các nút con; độ sâu cây được giới hạn
để tránh overfit. Random Forest và XGBoost đều là tổ hợp nhiều cây: Random
Forest lấy trung bình nhiều cây sâu huấn luyện độc lập trên các mẫu bootstrap
khác nhau (bagging), giúp giảm phương sai; XGBoost xây cây tuần tự, mỗi cây
mới học để sửa lỗi của tổ hợp trước đó (gradient boosting). Việc lấy trung
bình/tổ hợp nhiều cây làm giảm phương sai vì sai số ngẫu nhiên của từng cây
riêng lẻ có xu hướng triệt tiêu lẫn nhau khi cộng gộp.

**2. "Vì sao mô hình bỏ qua một số giao dịch gian lận?"**
Vì mục tiêu là tối thiểu hóa TỔNG CHI PHÍ, không phải bắt hết gian lận. 42%
số vụ gian lận (205/492) có giá trị dưới €3 — phí kiểm tra — nên bắt chúng
tốn nhiều hơn số tiền cứu được; 27 vụ thậm chí đúng €0. Bỏ qua các giao dịch
này là lựa chọn kinh tế tối ưu, không phải điểm yếu của mô hình.

**3. "Tại sao không dùng accuracy?"**
Vì dữ liệu mất cân bằng cực độ (0.173% gian lận), một mô hình luôn dự đoán
"không gian lận" đạt accuracy 99.8% mà vô dụng hoàn toàn. Accuracy không phản
ánh chi phí thực tế của sai lầm, nên nhóm dùng trực tiếp hàm chi phí bằng
tiền làm thước đo.

**4. "Vì sao không kết luận được mô hình nào tốt nhất?"**
Vì cỡ mẫu hiệu dụng cho việc so sánh chi phí chỉ khoảng n_eff = 18.1 (do chỉ
có 98 gian lận test và phân phối chi phí có đuôi dài/lệch), nên khoảng tin
cậy của chênh lệch chi phí giữa các mô hình rất rộng và chứa số 0. Champion
chỉ thắng Logistic Regression trong 53.3% số lần lặp bootstrap — không đủ để
khẳng định một mô hình vượt trội.

**5. "SMOTE đặt ở đâu trong quy trình?"**
SMOTE (nếu dùng để xử lý mất cân bằng) phải được đặt BÊN TRONG mỗi fold của
cross-validation, chỉ áp dụng lên tập huấn luyện của fold đó — không bao giờ
áp dụng trước khi chia fold hoặc lên toàn bộ dữ liệu. Nếu làm sai thứ tự, các
mẫu tổng hợp từ SMOTE có thể "rò rỉ" thông tin từ tập validation/test vào tập
huấn luyện, làm kết quả đánh giá lạc quan giả tạo.
