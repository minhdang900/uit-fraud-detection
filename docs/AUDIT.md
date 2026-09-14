# Kiểm toán đồ án — 14/09/2026

Một lượt kiểm toán độc lập toàn bộ đồ án: **kiểm chứng lại từ đầu** thay vì đọc
tài liệu, rồi ghi lại đúng những gì tìm thấy.

Nguyên tắc: không nhận một con số nào là đúng chỉ vì nó được viết ra. Mọi kết quả
dưới đây đều được chạy lại và đối chiếu.

---

## 1. Kết luận ngắn

| | |
|---|---|
| **Tính đúng đắn khoa học** | ✅ Đạt — mọi con số công bố tái lập chính xác |
| **Tính toàn vẹn thực nghiệm** | ✅ Đạt, sau khi vá một lỗ hổng nghiêm trọng (A-2) |
| **Độ phủ yêu cầu môn học** | ✅ Đạt — đủ 10 mục, đủ 8 câu hỏi, đủ 3 mô hình |
| **Bộ nộp** | ✅ Đủ, sau khi dọn rác và đồng bộ lại mã nguồn |
| **Bài thuyết trình** | ❌ **Chưa đạt — vượt trần 15 phút** (A-3) |

Một việc còn lại chặn đường nộp: **cắt bộ slide**. Mọi việc khác đã xử lý xong.

---

## 2. Những gì đã kiểm chứng được

Đây là phần quan trọng nhất của bản kiểm toán: các khẳng định của đồ án **đứng vững**
khi bị kiểm tra lại.

| # | Khẳng định | Cách kiểm | Kết quả |
|---|---|---|---|
| V1 | Bộ test xanh | `./run.sh test` | ✅ 18/18 lúc bắt đầu → **41 passed, 1 xfailed** sau khi bổ sung |
| V2 | Pipeline tái lập được | Chạy lại `run_model_matrix.py` từ CSV gốc | ✅ **Mọi con số trùng khít**: val €3.052,05 · test €2.223,93 · PR-AUC 0,8228 |
| V3 | Kết quả ổn định qua các lần chạy | So sánh SHA-256 artifact trước/sau | ✅ **Mảng xác suất trùng từng byte**; chỉ `fit_seconds` (đồng hồ treo tường) khác |
| V4 | Chi phí tách đúng hai phần | `verify_results.reproduce_headline()` | ✅ €396,00 + €1.827,93 = €2.223,93 · €8.817,00 + €1.827,93 = €10.644,93 |
| V5 | Bootstrap và baseline đúng | Chạy lại `analyse_results.py` | ✅ €6,67 · 53,3% · €239,59 · 77,1% · baseline không-ML €12.398,63 — trùng `RESULTS.md` |
| V6 | Không rò rỉ tập test | Đọc mã + assert trong pipeline | ✅ Scaler assert `n_samples_seen_ == len(train)`; ngưỡng luôn suy từ validation |
| V7 | Đủ 3 họ mô hình | `select_champion_per_family` + test | ✅ Bảo đảm bằng cấu trúc, không bằng may mắn |
| V8 | Hình trong báo cáo đầy đủ | Đối chiếu tham chiếu ↔ đĩa | ✅ **14/14**, không thiếu, không thừa |
| V9 | Đủ yêu cầu đề bài | Đối chiếu `07_YEU-CAU-DO-AN.md` | ✅ 10 mục (qua Phụ lục A/B + bản gốc ở `05-Tai-lieu`), 8 câu hỏi (Phụ lục B) |
| V10 | CI chạy được | `git ls-files artifacts/` | ✅ Artifact được commit nên test tái lập chạy được trên CI |

**Nhận xét.** Đây là mức độ tái lập hiếm thấy ở đồ án môn học: chạy lại toàn bộ
pipeline cùng seed cho ra **mảng xác suất giống hệt từng byte**. Phần lớn đồ án
không kiểm được điều này vì không lưu xác suất thô.

---

## 3. Lỗi tìm thấy

### A-2 · NGHIÊM TRỌNG · Bản đăng ký trước tự huỷ bằng chứng của chính nó — ĐÃ SỬA

`run_model_matrix.py` ghi đè `artifacts/preregistration.json` **mỗi lần chạy**,
kèm `date` của ngày chạy.

Vì sao nghiêm trọng: toàn bộ giá trị của bản đăng ký trước nằm ở chỗ nó **được viết
ra trước khi chấm test**. Một file tự cập nhật theo mỗi lần chạy sẽ **luôn** khớp với
kết quả mới nhất — nên nó không chứng minh được gì cả. Tệ hơn: chạy lại sẽ **xoá mất
ngày gốc 2026-09-13**, đúng thứ duy nhất mà báo cáo đang viện dẫn ở trang đầu.

Phát hiện bằng cách chạy lại pipeline rồi `git status`: file đổi.

**Đã sửa.** Ghi một lần; từ lần sau chuyển sang **đối chiếu**. Nếu validation đổi ý
về nhà vô địch, chương trình **dừng và báo lỗi** thay vì âm thầm làm mới hồ sơ.
Muốn lập hồ sơ mới phải truyền `--rewrite-preregistration` một cách có ý thức.
Kèm 6 test trong `tests/test_preregistration.py`.

Kiểm chứng: chạy lại `run_model_matrix.py` → in ra
`pre-registration exists (dated 2026-09-13) -- verifying, not rewriting`, và
`git status` sạch.

### A-3 · NGHIÊM TRỌNG · Bài nói vượt trần 15 phút — CHƯA SỬA, CẦN NHÓM QUYẾT

Bộ slide đang nộp có **30 slide, ~2.929 âm tiết**:

| Nhịp nói | Tổng | So với trần 15:00 |
|---|---|---|
| 140 âm tiết/phút (chậm, rõ) | ~20:55 | **vượt 5:55** |
| 170 âm tiết/phút (bình thường) | ~17:13 | **vượt 2:13** |
| 190 âm tiết/phút (nhanh) | ~15:24 | **vượt 0:24** |

Kịch bản còn ghi sai ràng buộc là *"15–20 phút"* và câu mở đầu nói *"trong 18 phút
tới"*. Không nguồn nào cho 20 phút. Đề cương và lời giảng viên Buổi 03 đều nói
**tối đa 15 phút, bấm giờ nghiêm**, kèm ví dụ *"đúng 15 phút là đồng hồ reo, không
cho trình bày nữa"*.

Hệ quả nếu không sửa: bị cắt ngang ở khoảng slide 22–25, tức **mất trọn phần Kết quả
3, Kết luận và Hướng phát triển** — đúng những nội dung giảng viên nói là quan trọng.

Đáng chú ý: bản slide gốc (`05-Tai-lieu/05_Slide-ban-goc-10-slide.md`) **đạt chuẩn**
— 10 slide, ~8:50–10:20. Bản 30 slide là bước lùi về mặt tuân thủ.

**Đã làm:** sửa lại phát biểu ràng buộc cho đúng, thêm **phương án cắt định lượng**
(cắt ~1.000 âm tiết → còn ~13:41) ở đầu `Kich-ban-thuyet-trinh.md`, và thêm test
`test_the_talk_fits_inside_the_fifteen_minute_cap` (đang `xfail`) để lỗi này không
bị quên. **Việc cắt nội dung nào là quyết định của nhóm**, không nên tự động hoá.

### A-1 · CAO · README khai báo đồ án chưa xong — ĐÃ SỬA

Mục *Status* trong `README.md` để trống ba ô: ma trận mô hình, đánh giá, báo cáo +
slide — trong khi cả ba **đã hoàn thành**. Mục *Layout* ghi "11 tests" (thực tế 18)
và "notebooks/ smoke test" (thực tế 4 notebook).

Vì sao quan trọng: README là file đầu tiên người chấm mở. Nó đang tự khai là đồ án
dở dang, trái ngược với nội dung thật.

**Đã sửa:** cập nhật đúng trạng thái, thêm bảng kết quả đầu đề, thêm mục demo.

### A-4 · TRUNG BÌNH · Rác trình soạn thảo trong bộ nộp — ĐÃ SỬA

Bộ nộp còn `.~lock.BaoCao_CS114_FraudDetection.pdf#`, `soffice-temp.tmp`
(bản PDF trung gian 38 trang, 3,1 MB), hai file lock LibreOffice, và `.DS_Store`.

File lock còn sót cũng là dấu hiệu tài liệu **có thể đang mở và chưa lưu**.

**Đã sửa:** xoá toàn bộ (đã kiểm bản PDF thật 40 trang còn nguyên vẹn trước khi xoá),
và thêm test `test_no_editor_lock_or_temp_files_are_left_in_the_bundle` chặn tái diễn.

### A-5 · TRUNG BÌNH · Bản sao mã nguồn trong bộ nộp bị cũ — ĐÃ SỬA

`03-Source-code/` trong bộ nộp thiếu `demo.py`, thiếu `tests/test_preregistration.py`, và
`run_model_matrix.py` là bản **trước** khi vá A-2 — trong khi `00-DOC-TRUOC-TIEN.md`
đã mô tả các file đó. Bộ nộp mô tả một thứ, chứa một thứ khác.

**Đã sửa:** đồng bộ lại toàn bộ mã nguồn, xác nhận bằng đối chiếu SHA-256.

### A-6 · THẤP · `conftest.py` rỗng 0 byte — ĐÃ SỬA

File rỗng trông như tạo nhầm, nhưng **chính sự tồn tại của nó** là thứ đưa thư mục
gốc vào `sys.path` để `tests/` import được `fraud_cost`. Xoá đi là hỏng cả bộ test.

**Đã sửa:** thêm docstring giải thích, để không ai "dọn dẹp" nó.

### A-7 · THẤP · `.venv/` là stub hỏng — ĐÃ SỬA (tài liệu)

`.venv/bin/python` trỏ tới Python 3.9 của Xcode, không có thư viện nào. Làm theo
README cũ sẽ gặp lỗi khó hiểu. **Đã sửa:** README hướng dẫn xoá và tạo lại bằng
Python 3.11, kèm `PYTHONPATH=.`.

### A-9 · THAY ĐỔI CẤU TRÚC · Bộ nộp chuyển ra ngoài repo — ĐÃ LÀM

Bộ nộp trước ở `07-Do-an-Fraud-Detection/NOP_BAI/`, nay chuyển thành
**`ML/08-Nop-bai/`** — ngang hàng với các thư mục `00-`…`07-` của môn học.

Lý do: bộ nộp là *sản phẩm*, không phải *mã nguồn*. Nó chứa PDF sinh ra và một
bản sao đông lạnh của code; để chung repo là mời gọi hai bản trôi khỏi nhau.

Việc chuyển làm hỏng hai đường dẫn, trong đó **một cái hỏng im lặng**:

| Chỗ hỏng | Hậu quả nếu không sửa |
|---|---|
| `make_figures.py` ghi vào `ROOT/NOP_BAI/...` | Tạo thư mục rỗng mới trong repo rồi ghi 14 hình vào đó; bộ nộp giữ hình cũ |
| `tests/test_submission.py` có `skipif` | **10 test canh bộ nộp lặng lẽ ngừng chạy** — tệ hơn là đỏ, vì không ai biết |

Ngoài ra container chỉ bind-mount thư mục repo, nên sau khi chuyển thì **bên trong
Docker không nhìn thấy bộ nộp nữa**.

**Đã sửa:** thêm `paths.py` giải đường dẫn ở một chỗ duy nhất (ưu tiên `$NOP_BAI_DIR`,
rồi trường hợp đang chạy từ bản sao trong bộ nộp, rồi thư mục ngang hàng);
`make_figures.py` dùng `require_bundle_dir()` nên **dừng hẳn** thay vì ghi nhầm chỗ;
`docker-compose.yml` mount bộ nộp vào `/nop-bai` kèm biến `NOP_BAI_DIR`. Kiểm chứng:
`./run.sh test` → 41 passed, **0 skipped** (các test canh bộ nộp vẫn chạy thật).

### A-8 · THÔNG TIN · `fit_seconds` không tất định

`validation_results.csv` chứa thời gian fit đo bằng đồng hồ treo tường, nên file này
**luôn** khác sau mỗi lần chạy lại. Đây là trường duy nhất như vậy; chi phí, ngưỡng,
tỉ lệ cảnh báo và PR-AUC đều trùng khít. Giữ nguyên vì bảng *Fit* trong `RESULTS.md`
lấy từ đó — chỉ cần biết mà đừng tưởng là pipeline trôi.

---

## 4. Một phát hiện đã rút lại

**Ban đầu tôi báo "F12 là hình mồ côi, không được trích dẫn". Sai.**

`F12_chinh-sach-A-vs-E.png` **có** được trích dẫn, ở mục 5.7. Lỗi nằm ở biểu thức
tìm kiếm của tôi: lớp ký tự chỉ nhận chữ thường nên không khớp chữ hoa trong `A-vs-E`.

Ghi lại ở đây vì đây đúng là kiểu lỗi mà bản kiểm toán phải tự bắt được — và vì
`test_no_figure_is_shipped_without_being_referenced` nay dùng biểu thức có chữ hoa,
kèm bình luận giải thích chính cái bẫy này.

---

## 5. Còn lại phải làm

| Việc | Ai quyết | Chặn nộp? |
|---|---|---|
| **Cắt slide về ≤15 phút** (A-3) | Nhóm | ✅ **Có** |
| Điền tên + MSSV vào báo cáo và `00-DOC-TRUOC-TIEN.md` | Nhóm | ✅ Có |
| Sinh lại `.pptx` sau khi cắt, rồi tập nói có bấm giờ | Nhóm | ✅ Có |
| Gỡ dấu `xfail` sau khi cắt xong | Bất kỳ ai | Không |
| Xác nhận lại với giảng viên: hạn nộp, PA1/PA2, lịch bốc thăm | Nhóm | Không |
