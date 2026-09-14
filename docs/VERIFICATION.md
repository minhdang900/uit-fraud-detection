# Cách kiểm chứng và đánh giá kết quả

Tài liệu này trả lời hai câu hỏi khác nhau:

1. **Kiểm chứng (verify):** các con số trong báo cáo có đúng và tái lập được không?
2. **Đánh giá (evaluate):** kết quả đó có TỐT không, và tốt theo nghĩa nào?

---

## Phần 1 — Kiểm chứng: chạy một lệnh

```bash
./run.sh test
```

Kết quả mong đợi: **41 passed, 1 xfailed**. Nếu thấy bất kỳ FAILED nào, có gì đó
đã trôi — đừng nộp báo cáo cho tới khi hiểu vì sao.

> `1 xfailed` là **có chủ đích**: đó là test thời lượng bài nói, đang ghi nhận một
> lỗi đã biết và chưa sửa (bộ slide 30 trang vượt trần 15 phút — xem Tiêu chí 5).
> Khi nào cắt slide xong, test đó sẽ chuyển sang XPASS và **làm cả bộ đỏ** để buộc
> gỡ dấu `xfail` — cố ý như vậy, để lỗi không bị quên.

Bộ test chia làm sáu nhóm, mỗi nhóm bảo vệ một thứ khác nhau:

| Nhóm | Số test | Bảo vệ điều gì |
|---|---|---|
| `test_fraud_cost.py` | 8 | Hàm chi phí đúng về mặt toán học |
| `test_preprocessing.py` | 3 | Tiền xử lý và chia tập đúng |
| `test_modeling.py` | 2 | Chọn champion không làm mất họ mô hình nào |
| `test_preregistration.py` | 6 | Chạy lại **không âm thầm ghi đè** bản đăng ký trước |
| `test_demo.py` | 7 | Con số demo in ra khớp con số báo cáo |
| `test_results_reproducible.py` | 5 | **Số trong báo cáo vẫn là số pipeline tạo ra** |
| `test_submission.py` | 10 (+1 xfail) | Bộ nộp đủ file, không thiếu hình, không lẫn rác |

Ba nhóm đầu chứng minh *code đúng*. Ba nhóm sau quan trọng hơn khi đi bảo vệ:
chúng chứng minh *quy trình đúng*, *báo cáo đúng*, và *bộ nộp đúng*.

## Phần 1b — Chạy demo trước hội đồng

```bash
./run.sh demo                    # toàn bộ câu chuyện kết quả
./run.sh demo --score 0.02 1500  # chấm một giao dịch bất kỳ
```

Demo **không đọc bảng kết quả nào** — nó tính lại từ mảng xác suất thô, kể cả
ngưỡng (suy từ validation rồi mới áp lên test). Nếu có gì trôi, demo sẽ in ra số
khác báo cáo và `test_demo.py` sẽ đỏ trước khi điều đó xảy ra trên máy chiếu.

Demo cũng **không cần file CSV 144 MB**, nên chạy được trên máy mượn.

### Kiểm chứng thủ công từng con số

```bash
docker compose exec -T lab python -c "
from verify_results import reproduce_headline
for k, v in reproduce_headline().items(): print(f'{k:<20} {v}')"
```

Mọi con số dưới đây được tính lại từ mảng xác suất thô, **không** đọc từ bảng
kết quả đã lưu. Ngưỡng được suy ra lại từ tập validation rồi mới áp lên test —
đúng thứ tự pipeline đã dùng.

| Đại lượng | Giá trị | Xuất hiện ở đâu trong báo cáo |
|---|---|---|
| champion | `xgb/balanced` | §5, §7.1 |
| chi phí test | €2,223.93 | §6, §7.1, slide 5 |
| số gian lận test | 98 | cơ sở của n_eff = 18.1 |
| bắt được | 85 (86.7%) | §6.3, slide 7 |
| cứu được | €8,817.00 | §6.5 |
| mất | €1,827.93 | §6.5, slide 7 |
| chi phí kiểm tra | €396.00 (132 alert) | §6.4 |

**Hai đẳng thức phải luôn đúng** (test tự kiểm tra):
- `€396.00 + €1,827.93 = €2,223.93` — chi phí tách đúng thành hai phần
- `€8,817.00 + €1,827.93 = €10,644.93` — mỗi euro gian lận hoặc cứu được hoặc mất

Nếu một trong hai sai, hoặc hàm chi phí hoặc cách đếm confusion matrix đã hỏng,
và **mọi** con số phía sau đều sai theo.

### Chạy lại toàn bộ từ đầu

```bash
docker compose exec -T lab python run_model_matrix.py   # ~15 giây
docker compose exec -T lab python analyse_results.py
```

Sau đó chạy lại `./run.sh test`. Nếu vẫn 18 passed, toàn bộ chuỗi tái lập được.

### Chạy lại notebook

```bash
for nb in 01_eda 02_error_analysis 03_calibration; do
  docker compose exec -T lab python -m jupyter nbconvert --to notebook --execute \
    --ExecutePreprocessor.timeout=900 --output /tmp/$nb.ipynb notebooks/$nb.ipynb
done
```

Không được có lỗi ở bất kỳ cell nào.

---

## Phần 2 — Đánh giá: kết quả này tốt hay không?

Kiểm chứng nói "số đúng". Đánh giá nói "số đó có ý nghĩa gì". Đây là phần hội
đồng sẽ hỏi.

### Tiêu chí 1 — ML có thực sự cần thiết không? ✅ CÓ

| Chính sách | Chi phí |
|---|---|
| Gắn cờ tất cả | €170,886.00 |
| **Không ML: Amount ≥ €549** | **€12,398.63** |
| Không làm gì | €10,644.93 |
| **Champion** | **€2,223.93** |

Hàng quan trọng nhất là hàng thứ hai. Một luật đơn giản không dùng ML còn **tệ
hơn cả việc không làm gì**. Không có hàng này, đồ án không chứng minh được máy
học đáng dùng. Có hàng này, kết luận giảm 79% chi phí mới có sức nặng.

### Tiêu chí 2 — có chọn được mô hình tốt nhất không? ❌ KHÔNG, và đó là kết quả

| So sánh | Chênh lệch | CI 95% | Kết luận |
|---|---|---|---|
| logreg − champion | €6.67 | [−67.41, 93.32] | không có ý nghĩa |
| rf − champion | €239.59 | [−145.01, 928.43] | không có ý nghĩa |

Champion chỉ thắng **53.3%** số lần bootstrap. Cỡ mẫu hiệu dụng là **18.1**,
không phải 98.

**Cách đánh giá đúng:** đây KHÔNG phải thất bại. Báo cáo chênh lệch €6.67 như
một chiến thắng mới là sai. Kết luận bảo vệ được: *ba mô hình tương đương, cả
ba đều tốt hơn mọi baseline*.

### Tiêu chí 3 — tính toàn vẹn của thực nghiệm ✅

| Kiểm tra | Bằng chứng |
|---|---|
| Test không dùng để chọn mô hình | `artifacts/preregistration.json` có ngày, ghi champion trước khi chấm test |
| Không rò rỉ qua scaler | `run_model_matrix.py` assert `n_samples_seen_ == len(train)` |
| Ngưỡng chọn trên validation | `verify_results.py` suy lại ngưỡng từ validation |
| Đủ 3 họ mô hình | `select_champion_per_family` có test chứng minh top-3 toàn cục sẽ loại bỏ logreg |

### Tiêu chí 4 — các giới hạn đã nêu rõ chưa? ✅

Bốn điều báo cáo tự nêu ra, không né tránh:
1. Không kết luận được mô hình nào tốt nhất (n_eff = 18.1)
2. Policy E — luật tối ưu về lý thuyết — **thua** trên thực nghiệm
3. Hiệu chỉnh xác suất ở biên quyết định của xgb chỉ dựa trên **n=10**, quá ít để tin
4. V1–V28 là PCA fit trên cả 48 giờ, nên chia theo thời gian **không** loại bỏ được look-ahead

Một báo cáo tự nêu giới hạn của mình mạnh hơn một báo cáo giấu chúng đi.

### Tiêu chí 5 — bài nói có vừa khung giờ không? ❌ CHƯA

| Nhịp nói | Tổng | So với trần cứng 15:00 |
|---|---|---|
| 140 âm tiết/phút (chậm, rõ) | ~20:55 | **vượt 5:55** |
| 170 âm tiết/phút (bình thường) | ~17:13 | **vượt 2:13** |
| 190 âm tiết/phút (nhanh) | ~15:24 | **vượt 0:24** |

Bộ 30 slide hiện tại vượt giờ ở **mọi** nhịp nói. Giảng viên nói rõ *"đúng 15 phút
là đồng hồ reo, không cho trình bày nữa"* — nên đây không phải lỗi nhỏ: phần Kết
luận sẽ bị cắt mất.

**Cách đánh giá đúng:** nội dung đạt, *đóng gói* chưa đạt. Phương án cắt cụ thể
(≈1.000 âm tiết, về 13:41) nằm ở đầu file `../08-Nop-bai/02-Slide/Kich-ban-thuyet-trinh.md`.
Test `test_the_talk_fits_inside_the_fifteen_minute_cap` canh điều kiện này.

---

## Phần 2b — Kiểm toán độc lập

`docs/AUDIT.md` ghi lại một lượt kiểm toán toàn bộ đồ án: những gì đã kiểm chứng
được, những lỗi tìm thấy, và những gì còn lại. Đọc file đó trước khi nộp.

---

## Phần 3 — Dấu hiệu có vấn đề

Nếu gặp bất kỳ điều nào dưới đây, dừng lại và điều tra:

| Dấu hiệu | Nghĩa là gì |
|---|---|
| `./run.sh test` có FAILED | Số trong báo cáo không còn khớp pipeline |
| `test_submission.py` đỏ | Bộ nộp thiếu hình, thiếu thư mục, hoặc lẫn file tạm |
| Chạy lại `run_model_matrix.py` mà `preregistration.json` đổi ngày | Bản đăng ký trước đã bị ghi đè — bằng chứng toàn vẹn mất hiệu lực |
| `reviews + lost ≠ cost` | Hàm chi phí hoặc confusion matrix hỏng |
| Chi phí test **thấp hơn** chi phí validation nhiều | Có thể đã chọn ngưỡng trên test — rò rỉ |
| Accuracy ≈ 99.8% được nêu như thành tích | Đang đánh giá sai độ đo |
| Champion khác `xgb/balanced` | Pre-registration không còn hiệu lực, phải giải thích |
| Policy E bỗng thắng đậm | Kiểm tra lại: có áp `undo_class_weight` cho nhánh reweighted không |

---

## Phần 4 — Kiểm tra trước khi nộp

- [ ] `./run.sh test` → 41 passed, 1 xfailed
- [ ] 3 notebook chạy hết, 0 lỗi
- [ ] Số trong `docs/REPORT.md` khớp `reproduce_headline()`
- [ ] Số trong `docs/SLIDES.md` khớp `docs/RESULTS.md`
- [ ] `artifacts/preregistration.json` có ngày trước kết quả test
- [ ] **Cắt slide về ≤15:00** (hiện 17–21 phút) rồi tập nói có bấm giờ
- [ ] `./run.sh demo` chạy sạch, số khớp báo cáo
- [ ] Mỗi thành viên bảo vệ được ít nhất một hình mình phụ trách
- [ ] Chuẩn bị câu trả lời CART (chưa học cây quyết định nhưng dùng RF/XGBoost)
