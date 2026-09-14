/* Đồ án CS114 — slide bảo vệ 15-20 phút. Sinh bằng pptxgenjs.
   Chạy từ thư mục 03-Source-code:  node make_slides.js
   Cần: npm install pptxgenjs   ·   hình lấy từ ../04-Ket-qua/hinh-anh/ */
const pptxgen = require("pptxgenjs");
const p = new pptxgen();

p.layout = "LAYOUT_WIDE";                       // 13.333 x 7.5 in
p.author = "Nhóm CS114";
p.title = "Phát hiện gian lận thẻ tín dụng theo hướng tối thiểu hoá chi phí";

const NAVY = "1E2761", ICE = "CADCFC", ORANGE = "EB6834";
const INK = "1A1A1A", MUTED = "5A6070", WHITE = "FFFFFF", LIGHT = "F2F5FB";
const GREEN = "1BAF7A", RED = "C0392B";
const HEAD = "Cambria", BODY = "Calibri";
const W = 13.333, H = 7.5, M = 0.62;

let n = 0;
const num = () => (++n);

/* ---------------------------------------------------------------- dark slide */
function darkSlide() {
  const s = p.addSlide();
  s.background = { color: NAVY };
  return s;
}

/* ------------------------------------------------------------- section divider */
function divider(idx, title, subtitle) {
  const s = darkSlide();
  num();
  s.addShape(p.ShapeType.ellipse, { x: M, y: 2.75, w: 1.05, h: 1.05, fill: { color: ORANGE } });
  s.addText(String(idx), {
    x: M, y: 2.75, w: 1.05, h: 1.05, align: "center", valign: "middle",
    fontFace: HEAD, fontSize: 40, bold: true, color: WHITE, isTextBox: true, margin: 0,
  });
  s.addText(title, {
    x: M + 1.5, y: 2.72, w: W - M - 1.9, h: 0.85, align: "left", valign: "middle",
    fontFace: HEAD, fontSize: 34, bold: true, color: WHITE, isTextBox: true, margin: 0,
  });
  s.addText(subtitle, {
    x: M + 1.5, y: 3.6, w: W - M - 1.9, h: 0.5, align: "left", valign: "top",
    fontFace: BODY, fontSize: 15, color: ICE, isTextBox: true, margin: 0,
  });
  return s;
}

/* --------------------------------------------------------------- content slide */
function slide(sectionIdx, sectionName, title) {
  const s = p.addSlide();
  s.background = { color: WHITE };
  const i = num();
  s.addShape(p.ShapeType.ellipse, { x: M, y: 0.4, w: 0.4, h: 0.4, fill: { color: NAVY } });
  s.addText(String(sectionIdx), {
    x: M, y: 0.4, w: 0.4, h: 0.4, align: "center", valign: "middle",
    fontFace: BODY, fontSize: 13, bold: true, color: WHITE, isTextBox: true, margin: 0,
  });
  s.addText(sectionName.toUpperCase(), {
    x: M + 0.55, y: 0.4, w: 9.5, h: 0.4, valign: "middle",
    fontFace: BODY, fontSize: 11, bold: true, color: MUTED, charSpacing: 1.4,
    isTextBox: true, margin: 0,
  });
  s.addText(title, {
    x: M, y: 0.92, w: W - 2 * M, h: 0.72, valign: "middle",
    fontFace: HEAD, fontSize: 27, bold: true, color: NAVY, isTextBox: true, margin: 0,
  });
  s.addText(String(i), {
    x: W - M - 0.6, y: H - 0.34, w: 0.6, h: 0.26, align: "right",
    fontFace: BODY, fontSize: 10, color: MUTED, isTextBox: true, margin: 0,
  });
  return s;
}

/* ------------------------------------------------------------------ components */
function stat(s, x, y, w, value, label, valColor) {
  s.addShape(p.ShapeType.roundRect, {
    x, y, w, h: 1.5, rectRadius: 0.09, fill: { color: LIGHT },
  });
  s.addText(value, {
    x: x + 0.18, y: y + 0.16, w: w - 0.36, h: 0.72, align: "center", valign: "middle",
    fontFace: HEAD, fontSize: 32, bold: true, color: valColor || NAVY, isTextBox: true, margin: 0,
  });
  s.addText(label, {
    x: x + 0.18, y: y + 0.88, w: w - 0.36, h: 0.5, align: "center", valign: "top",
    fontFace: BODY, fontSize: 11.5, color: MUTED, isTextBox: true, margin: 0,
  });
}

function bullets(s, x, y, w, h, items, size) {
  s.addText(
    items.map((t, i) => ({
      text: t, options: { bullet: { code: "2013" }, breakLine: i !== items.length - 1 },
    })),
    {
      x, y, w, h, valign: "top", fontFace: BODY, fontSize: size || 15, color: INK,
      lineSpacingMultiple: 1.12, paraSpaceAfter: 8, isTextBox: true, margin: 0,
    }
  );
}

function card(s, x, y, w, h, heading, body, accent) {
  s.addShape(p.ShapeType.roundRect, { x, y, w, h, rectRadius: 0.08, fill: { color: LIGHT } });
  s.addText(heading, {
    x: x + 0.22, y: y + 0.16, w: w - 0.44, h: 0.36, valign: "middle",
    fontFace: BODY, fontSize: 14, bold: true, color: accent || NAVY, isTextBox: true, margin: 0,
  });
  s.addText(body, {
    x: x + 0.22, y: y + 0.54, w: w - 0.44, h: h - 0.72, valign: "top",
    fontFace: BODY, fontSize: 12.5, color: INK, lineSpacingMultiple: 1.1,
    isTextBox: true, margin: 0,
  });
}

function fig(s, file, x, y, w, h, caption) {
  s.addImage({ path: "../04-Ket-qua/hinh-anh/" + file, x, y, w, h, sizing: { type: "contain", w, h } });
  if (caption) {
    s.addText(caption, {
      x, y: y + h + 0.04, w, h: 0.3, align: "center",
      fontFace: BODY, fontSize: 10, italic: true, color: MUTED, isTextBox: true, margin: 0,
    });
  }
}

function keyline(s, y, text, color) {
  s.addShape(p.ShapeType.roundRect, {
    x: M, y, w: W - 2 * M, h: 0.62, rectRadius: 0.08, fill: { color: color || NAVY },
  });
  s.addText(text, {
    x: M + 0.25, y, w: W - 2 * M - 0.5, h: 0.62, valign: "middle",
    fontFace: BODY, fontSize: 14.5, bold: true, color: WHITE, isTextBox: true, margin: 0,
  });
}

/* ============================================================== 1. TITLE */
{
  const s = darkSlide();
  num();
  s.addText("ĐỒ ÁN MÔN HỌC CS114 — MÁY HỌC", {
    x: M + 0.3, y: 1.55, w: W - 2 * M - 0.6, h: 0.4,
    fontFace: BODY, fontSize: 13, bold: true, color: ORANGE, charSpacing: 2,
    isTextBox: true, margin: 0,
  });
  s.addText("Phát hiện gian lận thẻ tín dụng\ntheo hướng tối thiểu hoá chi phí", {
    x: M + 0.3, y: 2.05, w: W - 2 * M - 0.6, h: 1.7,
    fontFace: HEAD, fontSize: 40, bold: true, color: WHITE, lineSpacingMultiple: 1.08,
    isTextBox: true, margin: 0,
  });
  s.addText("Chúng tôi không tối ưu accuracy. Chúng tôi tối ưu tiền.", {
    x: M + 0.3, y: 3.95, w: W - 2 * M - 0.6, h: 0.45,
    fontFace: BODY, fontSize: 18, italic: true, color: ICE, isTextBox: true, margin: 0,
  });
  s.addText(
    "Bộ dữ liệu ULB / Kaggle · 284.807 giao dịch · 492 gian lận (0,173%)\n" +
    "Trường Đại học Công nghệ Thông tin, ĐHQG-HCM · Tháng 9, 2026",
    {
      x: M + 0.3, y: 5.35, w: W - 2 * M - 0.6, h: 0.9,
      fontFace: BODY, fontSize: 13, color: ICE, lineSpacingMultiple: 1.25,
      isTextBox: true, margin: 0,
    }
  );
  s.addNotes(
    "Chào thầy cô và các bạn. Nhóm em trình bày đồ án phát hiện gian lận thẻ tín dụng. " +
    "Điểm khác biệt của đồ án nằm ngay ở câu phụ đề: nhóm không tối ưu accuracy, nhóm tối ưu tiền. " +
    "Trong 18 phút tới em sẽ đi qua sáu phần: tổng quan, công trình liên quan, xây dựng dữ liệu, " +
    "phương pháp và thực nghiệm, kết quả, và cuối cùng là ứng dụng cùng kết luận."
  );
}

/* ============================================================== DIVIDER 1 */
divider(1, "TỔNG QUAN", "Bối cảnh · Phát biểu bài toán Input → Output · Đóng góp của nhóm")
  .addNotes("Phần một: tổng quan.");

/* ---- 1.1 bối cảnh */
{
  const s = slide(1, "Tổng quan", "Vì sao accuracy là thước đo sai cho bài toán này");
  stat(s, M, 1.78, 3.9, "0,173%", "tỉ lệ gian lận — 492 / 284.807 giao dịch", NAVY);
  stat(s, M + 4.15, 1.78, 3.9, "99,83%", "accuracy của mô hình luôn trả lời “hợp lệ”", ORANGE);
  stat(s, M + 8.3, 1.78, 3.85, "€0 – €2.125", "khoảng chi phí của MỘT vụ gian lận bị bỏ sót", NAVY);
  fig(s, "F01_phan-bo-nhan.png", 3.35, 3.5, 6.6, 2.8);
  keyline(s, 6.42, "Một FP tốn một hằng số. Một FN tốn đúng số tiền của giao dịch. Hai loại lỗi này không quy về cùng đơn vị bằng cách đếm.");
  s.addNotes(
    "Ba con số này định hình toàn bộ đồ án. Thứ nhất, chỉ 0,173% giao dịch là gian lận. " +
    "Thứ hai, hệ quả trực tiếp: một mô hình chỉ cần trả lời 'hợp lệ' cho mọi giao dịch đã đạt accuracy 99,83% " +
    "mà không bắt được vụ nào. Thứ ba, và đây là điểm quan trọng nhất — chi phí của một lỗi không cố định: " +
    "bỏ sót một giao dịch có thể mất 0 euro, cũng có thể mất hơn 2.100 euro. " +
    "Nhìn biểu đồ bên dưới: ở thang tuyến tính bên trái, cột gian lận gần như vô hình. " +
    "Phải chuyển sang thang log mới thấy nó. Đó là hình ảnh trực quan cho lý do accuracy vô dụng ở đây."
  );
}

/* ---- 1.2 Input -> Output */
{
  const s = slide(1, "Tổng quan", "Phát biểu bài toán: Input → Output");
  card(s, M, 1.78, 5.9, 1.55, "INPUT — mỗi giao dịch",
    "V1…V28  (28 thành phần PCA đã ẩn danh hoá)\nAmount  (số tiền, EUR)   ·   Time  (giây)", NAVY);
  card(s, M + 6.2, 1.78, 5.95, 1.55, "OUTPUT — một quyết định nhị phân",
    "ŷᵢ = 1  →  CẢNH BÁO, chuyển sang bộ phận rà soát\nŷᵢ = 0  →  BỎ QUA", ORANGE);

  s.addText("Hàm mục tiêu — thay accuracy bằng tiền", {
    x: M, y: 3.62, w: W - 2 * M, h: 0.34, fontFace: BODY, fontSize: 14, bold: true,
    color: MUTED, isTextBox: true, margin: 0,
  });
  s.addShape(p.ShapeType.roundRect, {
    x: M, y: 4.0, w: W - 2 * M, h: 0.95, rectRadius: 0.08, fill: { color: NAVY },
  });
  s.addText("TotalCost  =  c_review × (TP + FP)  +  Σ Amountᵢ    (i ∈ FN)", {
    x: M, y: 4.0, w: W - 2 * M, h: 0.95, align: "center", valign: "middle",
    fontFace: "Cambria", fontSize: 24, bold: true, color: WHITE, isTextBox: true, margin: 0,
  });
  s.addText("Đọc bằng lời: phí rà soát × số cảnh báo phát ra, cộng với số tiền mất vì gian lận lọt lưới. Nhóm dùng c_review = €3, và quét từ €1 đến €20 để kiểm tra kết luận có phụ thuộc con số này không.", {
    x: M, y: 5.12, w: W - 2 * M, h: 0.6, fontFace: BODY, fontSize: 14, color: INK,
    isTextBox: true, margin: 0,
  });

  const yy = 5.85;
  const cols = [["TP — bắt được", "€3"], ["FN — bỏ sót", "Amountᵢ"], ["FP — báo nhầm", "€3"], ["TN", "€0"]];
  cols.forEach((c, i) => {
    const x = M + i * ((W - 2 * M) / 4);
    const w = (W - 2 * M) / 4 - 0.18;
    s.addShape(p.ShapeType.roundRect, { x, y: yy, w, h: 0.85, rectRadius: 0.07, fill: { color: LIGHT } });
    s.addText(c[0], {
      x: x + 0.15, y: yy + 0.08, w: w - 0.3, h: 0.3, fontFace: BODY, fontSize: 12,
      color: MUTED, isTextBox: true, margin: 0,
    });
    s.addText(c[1], {
      x: x + 0.15, y: yy + 0.36, w: w - 0.3, h: 0.4, fontFace: HEAD, fontSize: 17, bold: true,
      color: i === 1 ? ORANGE : NAVY, isTextBox: true, margin: 0,
    });
  });
  s.addNotes(
    "Đây là phát biểu hình thức. Đầu vào là 28 thành phần PCA đã ẩn danh cùng số tiền và thời gian. " +
    "Đầu ra là một quyết định nhị phân cho từng giao dịch: cảnh báo hay bỏ qua. " +
    "Điểm khác biệt nằm ở hàm mục tiêu. Thay vì accuracy, nhóm tối thiểu hoá tổng chi phí bằng tiền: " +
    "phí rà soát ba euro nhân cho mọi cảnh báo phát ra — trả cho cả cảnh báo đúng lẫn sai, vì tại thời điểm " +
    "rà soát ta chưa biết nhãn — cộng với toàn bộ số tiền của những vụ gian lận bị bỏ sót. " +
    "Bốn ô dưới cùng là bảng chi phí đầy đủ. Chú ý ô thứ hai: đó là ô duy nhất không phải hằng số."
  );
}

/* ---- 1.3 hệ quả */
{
  const s = slide(1, "Tổng quan", "Hệ quả: quy tắc tối ưu KHÔNG phải là một ngưỡng");
  s.addShape(p.ShapeType.roundRect, {
    x: M, y: 1.78, w: W - 2 * M, h: 0.9, rectRadius: 0.08, fill: { color: ORANGE },
  });
  s.addText("cảnh báo  ⟺  pᵢ × Amountᵢ  >  c_review", {
    x: M, y: 1.78, w: W - 2 * M, h: 0.9, align: "center", valign: "middle",
    fontFace: HEAD, fontSize: 26, bold: true, color: WHITE, isTextBox: true, margin: 0,
  });
  s.addText("“Tổn thất kỳ vọng khi để lọt là xác suất nhân số tiền. Nếu nó vượt €3 thì hãy trả €3.”", {
    x: M, y: 2.82, w: W - 2 * M, h: 0.4, align: "center",
    fontFace: BODY, fontSize: 14, italic: true, color: MUTED, isTextBox: true, margin: 0,
  });

  const rows = [
    ["p = 0,01", "Amount = €1.000", "p × A = €10,00", "Ngưỡng 0,5: BỎ QUA", "Tối ưu: CẢNH BÁO"],
    ["p = 0,90", "Amount = €1", "p × A = €0,90", "Ngưỡng 0,5: CẢNH BÁO", "Tối ưu: BỎ QUA"],
  ];
  rows.forEach((r, i) => {
    const y = 3.42 + i * 1.0;
    s.addShape(p.ShapeType.roundRect, { x: M, y, w: W - 2 * M, h: 0.82, rectRadius: 0.07, fill: { color: LIGHT } });
    const colw = (W - 2 * M) / 5;
    r.forEach((t, j) => {
      const isVerdict = j >= 3;
      s.addText(t, {
        x: M + j * colw + 0.2, y, w: colw - 0.3, h: 0.82, valign: "middle",
        fontFace: BODY, fontSize: 13, bold: isVerdict, isTextBox: true, margin: 0,
        color: j === 3 ? RED : j === 4 ? GREEN : INK,
      });
    });
  });
  keyline(s, 5.7, "Ngưỡng toàn cục làm NGƯỢC LẠI với quy tắc tối ưu ở cả hai dòng — đó là lý do đồ án so sánh trực tiếp hai chính sách này.");
  s.addText("Một ngưỡng toàn cục t chỉ là trường hợp đặc biệt khi thay MỌI Amount bằng một hằng số Ā, với t = c_review / Ā.", {
    x: M, y: 6.5, w: W - 2 * M, h: 0.4, fontFace: BODY, fontSize: 13, color: MUTED,
    italic: true, isTextBox: true, margin: 0,
  });
  s.addNotes(
    "Khi cực tiểu hoá hàm chi phí đó, kết quả không phải một ngưỡng duy nhất, mà là một quy tắc phụ thuộc từng giao dịch: " +
    "cảnh báo khi xác suất nhân số tiền vượt phí rà soát. " +
    "Hai dòng ví dụ cho thấy điều này không hề tầm thường. Dòng một: xác suất chỉ 1% nhưng giao dịch một nghìn euro, " +
    "tổn thất kỳ vọng là mười euro, đáng để trả ba euro đi kiểm tra — nhưng ngưỡng 0,5 sẽ bỏ qua. " +
    "Dòng hai thì ngược lại: xác suất 90% nhưng chỉ một euro, kiểm tra là lỗ — vậy mà ngưỡng 0,5 lại cảnh báo. " +
    "Nói cách khác, ngưỡng toàn cục làm ngược lại ở cả hai dòng."
  );
}

/* ---- 1.4 đóng góp */
{
  const s = slide(1, "Tổng quan", "Đóng góp của nhóm");
  s.addText("Nhóm nói thẳng điều KHÔNG phải đóng góp: cả hàm chi phí lẫn quy tắc p × A > c đều đã có từ Bahnsen 2013, và đã được áp lên chính bộ dữ liệu này năm 2020. Đóng góp của nhóm là thực nghiệm và phương pháp luận.", {
    x: M, y: 1.75, w: W - 2 * M, h: 0.62, fontFace: BODY, fontSize: 13.5, italic: true,
    color: MUTED, lineSpacingMultiple: 1.1, isTextBox: true, margin: 0,
  });
  const items = [
    ["1", "So sánh đối chứng sạch — và kết quả ÂM",
      "Quy tắc Bayes áp đặt vs ngưỡng tinh chỉnh theo CÙNG hàm chi phí. Mọi công trình trước đều đổi thêm một biến khác cùng lúc; nhóm giữ mọi thứ cố định và thấy quy tắc Bayes KHÔNG thắng."],
    ["2", "Định lượng bất định cho một độ đo tiền tệ",
      "Chi phí là tổng đuôi nặng ⇒ cỡ mẫu hiệu dụng n_eff = 18,1 chứ không phải 98. Đủ để bác bỏ mọi tuyên bố xếp hạng mô hình."],
    ["3", "Baseline không-ML chứng minh máy học là cần thiết",
      "“Rà soát mọi giao dịch ≥ €549” tốn €12.398,63 — TỆ HƠN cả việc không làm gì (€10.644,93)."],
    ["4", "42% số vụ gian lận rẻ hơn phí rà soát",
      "205/492 vụ dưới €3, trong đó 27 vụ đúng €0 ⇒ chính sách tối ưu chi phí CỐ Ý bỏ qua gần một nửa số vụ."],
  ];
  items.forEach((it, i) => {
    const y = 2.52 + i * 1.13;
    s.addShape(p.ShapeType.ellipse, { x: M, y: y + 0.06, w: 0.46, h: 0.46, fill: { color: i === 0 ? ORANGE : NAVY } });
    s.addText(it[0], {
      x: M, y: y + 0.06, w: 0.46, h: 0.46, align: "center", valign: "middle",
      fontFace: BODY, fontSize: 14, bold: true, color: WHITE, isTextBox: true, margin: 0,
    });
    s.addText(it[1], {
      x: M + 0.68, y, w: W - 2 * M - 0.68, h: 0.36, valign: "middle",
      fontFace: BODY, fontSize: 15, bold: true, color: NAVY, isTextBox: true, margin: 0,
    });
    s.addText(it[2], {
      x: M + 0.68, y: y + 0.37, w: W - 2 * M - 0.68, h: 0.68, valign: "top",
      fontFace: BODY, fontSize: 12.5, color: INK, lineSpacingMultiple: 1.08,
      isTextBox: true, margin: 0,
    });
  });
  s.addNotes(
    "Nhóm xin nói thẳng trước: hàm chi phí và quy tắc p nhân Amount không phải phát minh của nhóm — " +
    "Bahnsen và cộng sự đã đưa ra từ 2013, và năm 2020 đã có người áp lên đúng bộ dữ liệu này. " +
    "Đóng góp của nhóm nằm ở bốn điểm. Điểm một, và là điểm nhóm tự tin nhất: một so sánh đối chứng sạch " +
    "cho kết quả âm. Điểm hai: định lượng bất định — cỡ mẫu hiệu dụng chỉ 18. " +
    "Điểm ba: một baseline không dùng máy học còn tệ hơn không làm gì. " +
    "Điểm bốn: 42% số vụ gian lận rẻ hơn phí rà soát."
  );
}

/* ============================================================== DIVIDER 2 */
divider(2, "CÁC CÔNG TRÌNH LIÊN QUAN", "Hướng tiếp cận hiện tại · Các bộ dữ liệu đã có · GAP")
  .addNotes("Phần hai: các công trình liên quan.");

/* ---- 2.1 hướng tiếp cận + dataset */
{
  const s = slide(2, "Công trình liên quan", "Bốn hướng tiếp cận, và các bộ dữ liệu công khai");
  card(s, M, 1.75, 3.85, 1.62, "Lý thuyết nền — học nhạy chi phí",
    "Elkan (IJCAI 2001): mọi ma trận chi phí 2×2 chỉ có MỘT bậc tự do ⇒ quy về chỉnh ngưỡng trên xác suất đã hiệu chuẩn.", NAVY);
  card(s, M + 4.1, 1.75, 3.85, 1.62, "Chi phí phụ thuộc từng mẫu",
    "Bahnsen 2013–2016: đúng hàm chi phí và đúng quy tắc p×A>c của đồ án. Almhaithawi 2020 áp lên chính tập ULB.", ORANGE);
  card(s, M + 8.2, 1.75, 3.9, 1.62, "Mất cân bằng & hiệu chuẩn",
    "SMOTE (2002); Dal Pozzolo 2015: lấy mẫu lại làm LỆCH xác suất hậu nghiệm; Platt / isotonic / Niculescu-Mizil.", NAVY);

  s.addText("Bộ dữ liệu công khai — vì sao nhóm chọn ULB", {
    x: M, y: 3.6, w: W - 2 * M, h: 0.34, fontFace: BODY, fontSize: 14, bold: true,
    color: MUTED, isTextBox: true, margin: 0,
  });
  const rows = [
    ["Bộ dữ liệu", "Kích thước", "Tỉ lệ gian lận", "Có Amount?", "Thật / Tổng hợp"],
    ["ULB / Kaggle  ← nhóm dùng", "284.807", "0,172%", "Có (EUR)", "THẬT"],
    ["IEEE-CIS (Vesta)", "590.540", "3,5%", "Có", "Thật"],
    ["PaySim", "6.362.620", "0,13%", "Có", "Tổng hợp"],
    ["BankSim", "594.643", "1,21%", "Có (EUR)", "Tổng hợp"],
    ["Sparkov", "1.852.394", "~0,5%", "Có (USD)", "Tổng hợp"],
  ];
  s.addTable(rows.map((r, ri) => r.map((c, ci) => ({
    text: c,
    options: {
      bold: ri === 0 || (ri === 1 && ci === 0),
      color: ri === 0 ? WHITE : ri === 1 ? NAVY : INK,
      fill: { color: ri === 0 ? NAVY : ri === 1 ? ICE : WHITE },
      align: ci === 0 ? "left" : "center",
    },
  }))), {
    x: M, y: 3.98, w: W - 2 * M, colW: [3.9, 2.0, 2.0, 1.9, 2.29],
    rowH: 0.35, fontFace: BODY, fontSize: 12, valign: "middle",
    border: { type: "solid", color: "DDE2EC", pt: 0.5 },
  });
  s.addText("ULB là bộ dữ liệu THẬT duy nhất vừa công khai không cần đăng ký, vừa có cột Amount — điều kiện bắt buộc để định nghĩa được hàm chi phí phụ thuộc từng giao dịch.", {
    x: M, y: 6.25, w: W - 2 * M, h: 0.5, fontFace: BODY, fontSize: 13, color: INK,
    italic: true, isTextBox: true, margin: 0,
  });
  s.addNotes(
    "Tài liệu chia thành bốn hướng. Nền tảng lý thuyết là định lý ngưỡng của Elkan năm 2001. " +
    "Hướng gần nhất với đồ án là chi phí phụ thuộc từng mẫu của Bahnsen — đây chính là nơi hàm chi phí " +
    "và quy tắc p nhân Amount của nhóm đã có sẵn. Hướng thứ ba là mất cân bằng và hiệu chuẩn. " +
    "Về dữ liệu: nhóm chọn ULB vì đây là bộ dữ liệu thật duy nhất vừa công khai vừa có cột số tiền. " +
    "Không có cột Amount thì không định nghĩa được hàm chi phí, nên ba bộ tổng hợp phía dưới không dùng được " +
    "cho câu hỏi của nhóm."
  );
}

/* ---- 2.2 GAP */
{
  const s = slide(2, "Công trình liên quan", "GAP — cái gì chưa ai làm");
  s.addShape(p.ShapeType.roundRect, { x: M, y: 1.75, w: 6.0, h: 4.05, rectRadius: 0.08, fill: { color: LIGHT } });
  s.addText("ĐÃ CÓ  —  nhóm KHÔNG nhận là mới", {
    x: M + 0.25, y: 1.9, w: 5.5, h: 0.36, fontFace: BODY, fontSize: 13, bold: true,
    color: MUTED, charSpacing: 1, isTextBox: true, margin: 0,
  });
  bullets(s, M + 0.25, 2.35, 5.5, 3.3, [
    "Hàm chi phí c(TP+FP) + ΣAmount(FN)  →  Bahnsen 2013, nguyên văn",
    "Quy tắc p·A > c (Chính sách E)  →  BMR trong Bahnsen 2013",
    "Áp khung này lên chính tập ULB  →  Almhaithawi 2020",
    "“AUC cao ≠ tiết kiệm tiền”  →  Chambi Condori 2026, trên chính tập ULB",
    "Chọn ngưỡng bằng cực tiểu hoá chi phí trên validation",
    "PR-AUC thay ROC-AUC dưới mất cân bằng  →  Davis & Goadrich 2006",
  ], 12.5);

  s.addShape(p.ShapeType.roundRect, { x: M + 6.35, y: 1.75, w: 5.75, h: 4.05, rectRadius: 0.08, fill: { color: NAVY } });
  s.addText("CHƯA CÓ  —  chỗ nhóm đứng vào", {
    x: M + 6.6, y: 1.9, w: 5.25, h: 0.36, fontFace: BODY, fontSize: 13, bold: true,
    color: ORANGE, charSpacing: 1, isTextBox: true, margin: 0,
  });
  s.addText([
    { text: "So sánh đối chứng sạch giữa quy tắc BMR áp đặt và ngưỡng tinh chỉnh theo CÙNG hàm chi phí. Mỗi công trình đã có đều đổi thêm một biến khác cùng lúc.", options: { bullet: { code: "2013" }, breakLine: true } },
    { text: "Báo cáo khoảng tin cậy cho các độ đo tiền tệ — khảo sát 2025 nêu ở mức nguyên tắc, chưa ai định lượng.", options: { bullet: { code: "2013" }, breakLine: true } },
    { text: "Hiệu chuẩn riêng ở vùng đuôi xác suất thấp — nơi Chính sách E thực sự ra quyết định.", options: { bullet: { code: "2013" }, breakLine: true } },
    { text: "Gắn c_review với số liệu vận hành thực — mọi giá trị trong tài liệu đều là giả định.", options: { bullet: { code: "2013" } } },
  ], {
    x: M + 6.6, y: 2.35, w: 5.25, h: 3.3, fontFace: BODY, fontSize: 12.5, color: WHITE,
    lineSpacingMultiple: 1.12, paraSpaceAfter: 9, isTextBox: true, margin: 0,
  });
  keyline(s, 6.0, "Đồ án KHÔNG đề xuất hàm chi phí hay quy tắc mới. Đóng góp là thực nghiệm và phương pháp luận.", ORANGE);
  s.addNotes(
    "Đây là slide nhóm muốn trung thực nhất. Cột trái là những thứ đã có và nhóm không nhận là mới — " +
    "hàm chi phí, quy tắc p nhân Amount, thậm chí cả việc áp lên đúng bộ dữ liệu này, đều đã được công bố. " +
    "Cột phải là bốn khoảng trống thật. Quan trọng nhất là dòng đầu: chưa ai làm một so sánh đối chứng sạch " +
    "giữa quy tắc Bayes áp đặt và một ngưỡng được tinh chỉnh theo cùng hàm chi phí đó. " +
    "Các công trình trước hoặc thêm SMOTE, hoặc học vùng quyết định thay vì áp đặt công thức, " +
    "hoặc so với ngưỡng tối ưu F1 chứ không phải tối ưu chi phí."
  );
}

/* ============================================================== DIVIDER 3 */
divider(3, "XÂY DỰNG DỮ LIỆU", "Tiền xử lý · Phân bố nhãn · Phân bố giá trị giao dịch · Phát hiện đầu đề")
  .addNotes("Phần ba: xây dựng dữ liệu.");

/* ---- 3.1 tiền xử lý */
{
  const s = slide(3, "Xây dựng dữ liệu", "Tiền xử lý và chia tập — năm quyết định, mỗi cái chống một lỗi");
  bullets(s, M, 1.78, 6.5, 3.4, [
    "Bỏ hẳn Time thô — dưới phép chia ngẫu nhiên nó cho mô hình học thuộc vị trí các “cụm” gian lận",
    "Thay bằng hour_of_day, mã hoá theo chu kỳ (sin, cos) — để 23:00 và 00:00 không nằm ở hai đầu đối lập",
    "log1p(Amount) rồi chuẩn hoá; V1–V28 giữ nguyên vì đã là đầu ra PCA",
    "Chia tầng 60/20/20 — ở tỉ lệ 0,173%, chia ngẫu nhiên thuần có thể để lại một tập gần như không có gian lận",
    "StandardScaler CHỈ fit trên train, có assert kiểm tra ngay trong pipeline để bắt rò rỉ",
  ], 13.5);

  const rows = [
    ["Tập", "Số dòng", "Số gian lận", "Giá trị gian lận"],
    ["Train (60%)", "170.883", "295", "—"],
    ["Validation (20%)", "56.962", "99", "€11.090,12"],
    ["Test (20%)", "56.962", "98", "€10.644,93"],
  ];
  s.addTable(rows.map((r, ri) => r.map((c, ci) => ({
    text: c,
    options: {
      bold: ri === 0 || ri === 3,
      color: ri === 0 ? WHITE : ri === 3 ? NAVY : INK,
      fill: { color: ri === 0 ? NAVY : ri === 3 ? ICE : WHITE },
      align: ci === 0 ? "left" : "center",
    },
  }))), {
    x: M + 6.9, y: 1.95, w: 5.2, colW: [1.7, 1.15, 1.2, 1.15],
    rowH: 0.42, fontFace: BODY, fontSize: 12.5, valign: "middle",
    border: { type: "solid", color: "DDE2EC", pt: 0.5 },
  });
  s.addShape(p.ShapeType.roundRect, { x: M + 6.9, y: 3.95, w: 5.2, h: 1.6, rectRadius: 0.08, fill: { color: LIGHT } });
  s.addText("Lưu ý bắt buộc về rò rỉ", {
    x: M + 7.12, y: 4.08, w: 4.76, h: 0.3, fontFace: BODY, fontSize: 13, bold: true, color: RED,
    isTextBox: true, margin: 0,
  });
  s.addText("V1–V28 được fit PCA trên TOÀN BỘ 48 giờ. Một phép chia theo thời gian KHÔNG thể loại bỏ look-ahead. Nhóm báo cáo kiểm tra ngày 1 → ngày 2 chỉ như kiểm tra dịch chuyển phân phối.", {
    x: M + 7.12, y: 4.4, w: 4.76, h: 1.05, fontFace: BODY, fontSize: 12, color: INK,
    lineSpacingMultiple: 1.08, isTextBox: true, margin: 0,
  });
  keyline(s, 5.85, "Thứ tự train → validation → (ghi đăng ký trước) → test được cưỡng chế bằng mã nguồn, không phải bằng lời hứa.");
  s.addNotes(
    "Năm quyết định tiền xử lý, mỗi cái chống một lỗi cụ thể. Đáng nói nhất là quyết định một: " +
    "nhóm bỏ hẳn cột Time thô, vì dưới phép chia ngẫu nhiên nó cho phép mô hình học thuộc vị trí các cụm gian lận — " +
    "đó là rò rỉ thật. Thay vào đó nhóm giữ lại giờ trong ngày, mã hoá theo chu kỳ. " +
    "Bảng bên phải là kết quả chia tập: tập test có 98 vụ gian lận trị giá 10.644 euro — " +
    "hai con số này sẽ xuất hiện lại ở mọi slide kết quả. " +
    "Ô đỏ là một hạn chế nhóm phải nêu thẳng: các đặc trưng PCA được fit trên cả 48 giờ, " +
    "nên chia theo thời gian không loại bỏ được look-ahead."
  );
}

/* ---- 3.2 phân bố Amount */
{
  const s = slide(3, "Xây dựng dữ liệu", "Phân bố giá trị giao dịch — biến quyết định của bài toán");
  fig(s, "F02_phan-bo-amount-theo-lop.png", M, 1.72, 7.5, 4.4);
  const rows = [
    ["", "Gian lận", "Hợp lệ"],
    ["count", "492", "284.315"],
    ["mean", "€122,21", "€88,29"],
    ["median", "€9,25", "€22,00"],
    ["max", "€2.125,87", "€25.691,16"],
  ];
  s.addTable(rows.map((r, ri) => r.map((c, ci) => ({
    text: c,
    options: {
      bold: ri === 0 || ri === 3,
      color: ri === 0 ? WHITE : ri === 3 ? NAVY : INK,
      fill: { color: ri === 0 ? NAVY : ri === 3 ? ICE : WHITE },
      align: ci === 0 ? "left" : "center",
    },
  }))), {
    x: M + 7.8, y: 1.85, w: 4.3, colW: [1.3, 1.5, 1.5],
    rowH: 0.4, fontFace: BODY, fontSize: 12.5, valign: "middle",
    border: { type: "solid", color: "DDE2EC", pt: 0.5 },
  });
  s.addText("Giả định ban đầu của nhóm — “gian lận có số tiền nhỏ hơn” — SAI ở giá trị trung bình.", {
    x: M + 7.8, y: 4.05, w: 4.3, h: 0.6, fontFace: BODY, fontSize: 13.5, bold: true,
    color: ORANGE, lineSpacingMultiple: 1.1, isTextBox: true, margin: 0,
  });
  s.addText("Giao dịch gian lận ĐIỂN HÌNH thì nhỏ (trung vị €9,25, chưa bằng nửa trung vị €22,00 của giao dịch hợp lệ), nhưng TRUNG BÌNH lại lớn hơn vì đuôi phải rất nặng.\n\nKhông mô tả được bằng “nhỏ hơn” hay “lớn hơn” — phân bố lưỡng cực về mặt chi phí.", {
    x: M + 7.8, y: 4.7, w: 4.3, h: 1.9, fontFace: BODY, fontSize: 12.5, color: INK,
    lineSpacingMultiple: 1.1, isTextBox: true, margin: 0,
  });
  s.addNotes(
    "Đây là mục nhóm đầu tư nhiều nhất trong phần dữ liệu, vì Amount chính là biến quyết định chi phí của một lỗi. " +
    "Giả định ban đầu của nhóm là gian lận thì số tiền nhỏ hơn. Giả định đó sai — nhưng sai một cách thú vị. " +
    "Trung vị gian lận là 9,25 euro, thật sự nhỏ hơn trung vị 22 euro của giao dịch hợp lệ. " +
    "Nhưng trung bình lại lớn hơn: 122 so với 88. Lý do là đuôi phải rất nặng. " +
    "Nghĩa là không thể mô tả bằng một câu 'nhỏ hơn' hay 'lớn hơn' — phân bố lưỡng cực về mặt chi phí."
  );
}

/* ---- 3.3 phát hiện đầu đề */
{
  const s = slide(3, "Xây dựng dữ liệu", "Phát hiện đầu đề: bỏ sót gian lận là một lựa chọn KINH TẾ");
  fig(s, "F03_gian-lan-duoi-phi-review.png", M, 1.7, 8.0, 4.5);
  stat(s, M + 8.35, 1.78, 3.75, "205 / 492", "vụ gian lận rẻ hơn phí rà soát €3  (41,7%)", ORANGE);
  stat(s, M + 8.35, 3.45, 3.75, "27 vụ", "có giá trị đúng €0 — bắt được cũng không cứu được đồng nào", NAVY);
  s.addShape(p.ShapeType.roundRect, { x: M + 8.35, y: 5.12, w: 3.75, h: 1.35, rectRadius: 0.08, fill: { color: NAVY } });
  s.addText("Rà soát hết 205 vụ này:\n205 × €3 = €615 chi phí\nchỉ cứu được €181\n→ PHÁ HUỶ €434 giá trị", {
    x: M + 8.55, y: 5.24, w: 3.35, h: 1.15, fontFace: BODY, fontSize: 13, bold: true,
    color: WHITE, lineSpacingMultiple: 1.12, isTextBox: true, margin: 0,
  });
  s.addNotes(
    "Đây là slide nhóm muốn hội đồng nhớ nhất, nên em xin đi chậm. " +
    "42% số vụ gian lận trong bộ dữ liệu — cụ thể là 205 trên 492 — có giá trị nhỏ hơn ba euro. " +
    "Lấy một ví dụ cụ thể: một giao dịch gian lận đúng một euro. Nếu mô hình bắt được nó, " +
    "nhóm phải trả ba euro cho nhân viên kiểm tra để cứu một euro. Bắt được làm nhóm mất thêm hai euro. " +
    "Tính gộp cho cả 205 vụ: chi phí kiểm tra 615 euro, tổng giá trị cứu được chỉ 181 euro — " +
    "phá huỷ 434 euro giá trị. Thậm chí có 27 vụ đúng không euro. " +
    "Vì vậy một chính sách tối ưu chi phí sẽ chủ động bỏ qua gần một nửa số gian lận. " +
    "Không phải vì mô hình yếu, mà vì đó là lựa chọn kinh tế đúng. Đây cũng là câu trả lời " +
    "cho câu hỏi tại sao recall của nhóm không phải 100%."
  );
}

/* ============================================================== DIVIDER 4 */
divider(4, "PHƯƠNG PHÁP & THỰC NGHIỆM", "Ma trận mô hình · Tính toàn vẹn thực nghiệm · Hai chính sách quyết định")
  .addNotes("Phần bốn: phương pháp và thực nghiệm.");

/* ---- 4.1 ma trận mô hình + toàn vẹn */
{
  const s = slide(4, "Phương pháp", "Ma trận 3 họ × 2 nhánh, và một quy trình chống tự lừa mình");
  const rows = [
    ["Họ mô hình", "Tham số (mặc định)", "Nhánh none", "Nhánh balanced"],
    ["Hồi quy logistic", "max_iter=1000", "✓", "class_weight='balanced'"],
    ["Random Forest", "n_estimators=100", "✓", "class_weight='balanced'"],
    ["XGBoost", "tree_method='hist', eval_metric='aucpr'", "✓", "scale_pos_weight"],
  ];
  s.addTable(rows.map((r, ri) => r.map((c, ci) => ({
    text: c,
    options: {
      bold: ri === 0, color: ri === 0 ? WHITE : INK,
      fill: { color: ri === 0 ? NAVY : WHITE },
      align: ci >= 2 ? "center" : "left",
    },
  }))), {
    x: M, y: 1.8, w: 7.4, colW: [1.9, 2.7, 1.0, 1.8],
    rowH: 0.42, fontFace: BODY, fontSize: 11.5, valign: "middle",
    border: { type: "solid", color: "DDE2EC", pt: 0.5 },
  });
  s.addText("Vì sao để tham số mặc định? Với 98 gian lận test, ngay cả chênh lệch giữa các THUẬT TOÁN cũng không phân biệt được. Tinh chỉnh chỉ tạo ra khác biệt nhỏ hơn nữa nằm sâu trong vùng nhiễu — và làm tăng rủi ro overfit lên chính tập validation. Đây là lựa chọn có chủ ý.", {
    x: M, y: 3.75, w: 7.4, h: 1.0, fontFace: BODY, fontSize: 12.5, color: INK,
    italic: true, lineSpacingMultiple: 1.1, isTextBox: true, margin: 0,
  });

  s.addShape(p.ShapeType.roundRect, { x: M + 7.75, y: 1.8, w: 4.35, h: 3.9, rectRadius: 0.08, fill: { color: NAVY } });
  s.addText("Thứ tự được CƯỠNG CHẾ bằng mã nguồn", {
    x: M + 7.97, y: 1.95, w: 3.9, h: 0.36, fontFace: BODY, fontSize: 13, bold: true,
    color: ORANGE, isTextBox: true, margin: 0,
  });
  ["1  Fit 6 cấu hình trên TRAIN",
   "2  Chấm VALIDATION, chọn 1 đại diện mỗi họ",
   "3  GHI đăng ký trước ra đĩa (có ngày)",
   "4  Chỉ khi đó mới chấm TEST — đúng một lần"].forEach((t, i) => {
    s.addText(t, {
      x: M + 7.97, y: 2.45 + i * 0.55, w: 3.9, h: 0.5, valign: "middle",
      fontFace: BODY, fontSize: 12.5, bold: i === 2, color: i === 2 ? ORANGE : WHITE,
      isTextBox: true, margin: 0,
    });
  });
  s.addText("Bất biến: KHÔNG tham số nào — mô hình, ngưỡng, siêu tham số — được chọn dựa trên kết quả test. Có 6 test chặn việc âm thầm ghi đè bản đăng ký khi chạy lại.", {
    x: M + 7.97, y: 4.75, w: 3.9, h: 0.8, fontFace: BODY, fontSize: 12, italic: true,
    color: ICE, lineSpacingMultiple: 1.1, isTextBox: true, margin: 0,
  });
  keyline(s, 5.95, "Chọn 1 đại diện mỗi HỌ, không phải top-3 toàn cục — top-3 có thể trả về ba biến thể của cùng một thuật toán.");
  s.addNotes(
    "Nhóm chạy ma trận ba họ mô hình nhân hai nhánh xử lý mất cân bằng, tất cả để ở tham số mặc định. " +
    "Đó là lựa chọn có chủ ý, không phải thiếu sót: với 98 gian lận test, ngay cả chênh lệch giữa các thuật toán " +
    "cũng không phân biệt được, nên tinh chỉnh chỉ tạo ra nhiễu. " +
    "Bên phải là phần nhóm coi trọng nhất về mặt phương pháp: thứ tự bốn bước được cưỡng chế bằng mã nguồn. " +
    "Nhà vô địch được ghi ra đĩa kèm ngày, trước khi nhóm chạm vào tập test lần nào. " +
    "Và nhóm chọn một đại diện mỗi họ chứ không phải top-3 toàn cục — vì top-3 có thể trả về ba biến thể " +
    "của cùng một thuật toán, thoả yêu cầu ba mô hình trên hình thức nhưng vi phạm tinh thần của nó."
  );
}

/* ---- 4.2 hai chính sách */
{
  const s = slide(4, "Phương pháp", "Hai chính sách quyết định — và đường cong chi phí");
  const t = [
    ["", "Chính sách A", "Chính sách E"],
    ["Quy tắc", "p ≥ t*", "p × Amount > c_review"],
    ["Tham số tự do", "1  (t*, dò trên validation)", "0"],
    ["Cơ sở", "Định lý ngưỡng Elkan", "Bayes Minimum Risk"],
    ["Cần xác suất hiệu chuẩn?", "Không — chỉ cần thứ hạng", "CÓ — giá trị tuyệt đối"],
  ];
  s.addTable(t.map((r, ri) => r.map((c, ci) => ({
    text: c,
    options: {
      bold: ri === 0 || ci === 0, color: ri === 0 ? WHITE : INK,
      fill: { color: ri === 0 ? NAVY : ci === 2 && ri === 4 ? "FDEDE5" : WHITE },
      align: ci === 0 ? "left" : "center",
    },
  }))), {
    x: M, y: 1.82, w: 6.2, colW: [2.1, 2.0, 2.1],
    rowH: 0.46, fontFace: BODY, fontSize: 11.5, valign: "middle",
    border: { type: "solid", color: "DDE2EC", pt: 0.5 },
  });
  s.addShape(p.ShapeType.roundRect, { x: M, y: 4.35, w: 6.2, h: 1.05, rectRadius: 0.07, fill: { color: LIGHT } });
  s.addText("Ngưỡng t* = 0,0677 của logistic tương đương giả định MỌI giao dịch đều đáng €44,30 — đó là con số Ā ngầm định, sắc hơn nhiều so với nói “ngưỡng tương đương giá trị trung bình”.", {
    x: M + 0.22, y: 4.45, w: 5.76, h: 0.9, fontFace: BODY, fontSize: 12, color: INK,
    lineSpacingMultiple: 1.08, isTextBox: true, margin: 0,
  });
  s.addShape(p.ShapeType.roundRect, { x: M, y: 5.6, w: 6.2, h: 1.05, rectRadius: 0.07, fill: { color: "FDEDE5" } });
  s.addText("Bẫy im lặng: class_weight='balanced' thổi phồng p. Phải gỡ trọng số (undo_class_weight) TRƯỚC khi áp Chính sách E — nếu không, mô hình cảnh báo tràn lan với một con số chi phí trông vẫn hợp lý.", {
    x: M + 0.22, y: 5.7, w: 5.76, h: 0.9, fontFace: BODY, fontSize: 12, color: RED,
    bold: true, lineSpacingMultiple: 1.08, isTextBox: true, margin: 0,
  });
  fig(s, "F05_duong-cong-chi-phi.png", M + 6.5, 1.9, 5.6, 4.5);
  s.addNotes(
    "Nhóm so sánh hai chính sách. Chính sách A là ngưỡng toàn cục, có một tham số tự do được dò trên validation. " +
    "Chính sách E là quy tắc p nhân Amount, không có tham số tự do nào. " +
    "Khác biệt then chốt ở dòng cuối: A chỉ cần thứ hạng đúng, còn E cần giá trị tuyệt đối của xác suất đúng — " +
    "nghĩa là E biến hiệu chuẩn từ tuỳ chọn thành bắt buộc. " +
    "Ô đỏ là một bẫy im lặng nhóm suýt mắc: class_weight balanced thổi phồng xác suất, " +
    "phải gỡ trọng số trước khi áp Chính sách E. " +
    "Biểu đồ bên phải là đường cong chi phí trên validation: cực tiểu nằm ở khoảng 80 đến 120 cảnh báo " +
    "trên gần 57 nghìn giao dịch — rất xa ngưỡng 0,5 mặc định."
  );
}

/* ============================================================== DIVIDER 5 */
divider(5, "KẾT QUẢ & PHÂN TÍCH", "Máy học có cần thiết? · Ai thắng? · Phân tích lỗi · Vì sao quy tắc Bayes thua")
  .addNotes("Phần năm: kết quả và phân tích. Đây là phần dài nhất.");

/* ---- 5.1 ML cần thiết */
{
  const s = slide(5, "Kết quả", "Kết quả 1 — máy học thực sự cần thiết, và nhóm CHỨNG MINH điều đó");
  fig(s, "F06_so-sanh-chi-phi-baseline.png", M, 1.72, 7.9, 4.15);
  s.addShape(p.ShapeType.roundRect, { x: M + 8.25, y: 1.85, w: 3.85, h: 2.15, rectRadius: 0.08, fill: { color: "FDEDE5" } });
  s.addText("Hàng quan trọng nhất", {
    x: M + 8.47, y: 1.98, w: 3.4, h: 0.3, fontFace: BODY, fontSize: 12.5, bold: true,
    color: RED, isTextBox: true, margin: 0,
  });
  s.addText("Một luật KHÔNG dùng máy học — “rà soát mọi giao dịch ≥ €549” — tốn €12.398,63.\n\nTệ hơn cả việc KHÔNG LÀM GÌ (€10.644,93).", {
    x: M + 8.47, y: 2.32, w: 3.4, h: 1.55, fontFace: BODY, fontSize: 12.5, color: INK,
    lineSpacingMultiple: 1.12, isTextBox: true, margin: 0,
  });
  stat(s, M + 8.25, 4.2, 3.85, "−79%", "chi phí, so với không làm gì — cả BA mô hình đều đạt", GREEN);
  s.addText("Ngưỡng €549 được chọn TRÊN VALIDATION, y hệt ngưỡng của mô hình — không bao giờ trên test.", {
    x: M + 8.25, y: 5.9, w: 3.85, h: 0.6, fontFace: BODY, fontSize: 11.5, italic: true,
    color: MUTED, lineSpacingMultiple: 1.08, isTextBox: true, margin: 0,
  });
  s.addNotes(
    "Trên 56.962 giao dịch test với 98 gian lận trị giá 10.644 euro: nếu không làm gì, nhóm mất toàn bộ số đó. " +
    "Nếu đi thái cực ngược lại, gắn cờ tất cả, chi phí bùng lên 170 nghìn euro, tệ hơn 16 lần. " +
    "Nhưng hàng quan trọng nhất là hàng thứ hai. Nhóm tự hỏi: nếu chỉ đơn giản rà soát mọi giao dịch " +
    "từ 549 euro trở lên, không cần mô hình gì cả, thì sao? Ngưỡng này được chọn trên validation, không phải test, " +
    "để so sánh công bằng. Kết quả là 12.398 euro — còn tệ hơn cả việc không làm gì. " +
    "Nhóm nhấn mạnh hàng này vì nếu thiếu nó, cả đồ án không chứng minh được máy học là cần thiết."
  );
}

/* ---- 5.2 không ai thắng */
{
  const s = slide(5, "Kết quả", "Kết quả 2 — không thể gọi tên người thắng, và đó CHÍNH LÀ kết quả");
  fig(s, "F07_bootstrap-khoang-tin-cay.png", M, 1.75, 8.1, 3.9);
  stat(s, M + 8.45, 1.85, 3.65, "€6,67", "chênh lệch giữa mô hình nhất và nhì, trên nền €2.200", ORANGE);
  stat(s, M + 8.45, 3.52, 3.65, "53,3%", "tỉ lệ mô hình vô địch thắng — gần như tung đồng xu", NAVY);
  stat(s, M + 8.45, 5.19, 3.65, "n_eff = 18,1", "cỡ mẫu hiệu dụng thật sự, không phải 98", NAVY);
  s.addText("Bootstrap ghép cặp, 1.000 lần lặp: mỗi lần lặp cả ba mô hình được chấm trên CÙNG một mẫu lấy lại. Cả hai khoảng tin cậy của chênh lệch đều chứa số 0.", {
    x: M, y: 5.8, w: 8.1, h: 0.55, fontFace: BODY, fontSize: 12.5, color: INK,
    isTextBox: true, margin: 0,
  });
  keyline(s, 6.38, "Khẳng định bảo vệ được: “ba mô hình tương đương, cả ba đều tốt hơn mọi baseline” — KHÔNG phải “XGBoost thắng”.", ORANGE);
  s.addNotes(
    "Đây là phần trung thực nhất của báo cáo. Khi so sánh mô hình vô địch với hồi quy logistic bằng bootstrap " +
    "ghép cặp một nghìn lần lặp — nghĩa là mỗi lần lặp cả hai mô hình đều được chấm trên cùng một mẫu lấy lại — " +
    "chênh lệch trung bình chỉ 6,67 euro, và khoảng tin cậy 95% chạy từ âm 67 đến dương 93, chứa cả số không. " +
    "Vô địch chỉ thắng trong 53,3% số lần lặp. " +
    "Lý do nằm ở cỡ mẫu hiệu dụng: tập test có 98 gian lận, nhưng vì chi phí là một tổng bị chi phối bởi " +
    "vài vụ rất lớn, 98 vụ này chỉ hành xử như khoảng 18 vụ độc lập. " +
    "Nhóm xin nói rõ quan điểm: báo cáo chênh lệch 6,67 euro như một chiến thắng mới chính là cái sai. " +
    "Đây là một phát hiện, không phải một thất bại."
  );
}

/* ---- 5.3 confusion matrix */
{
  const s = slide(5, "Kết quả", "Precision, Recall, F1 — và mô hình nhầm theo hướng nào");
  fig(s, "F09_ma-tran-nham-lan.png", M, 1.72, 5.4, 4.6);
  const t = [
    ["Thước đo", "Giá trị", "Diễn giải"],
    ["Precision", "64,4%", "cứ 3 cảnh báo thì ~1 là báo động giả"],
    ["Recall", "86,7%", "bắt được 85/98 vụ gian lận"],
    ["F1-score", "0,739", "F1 coi FP và FN nặng NHƯ NHAU — chi phí thì không"],
    ["Accuracy", "99,89%", "VÔ NGHĨA: mô hình hằng số đã đạt 99,83%"],
    ["PR-AUC", "0,8693", "độ đo phù hợp dưới mất cân bằng cực đoan"],
  ];
  s.addTable(t.map((r, ri) => r.map((c, ci) => ({
    text: c,
    options: {
      bold: ri === 0 || ci === 1, color: ri === 0 ? WHITE : ri === 4 && ci === 1 ? RED : INK,
      fill: { color: ri === 0 ? NAVY : ri === 4 ? "FDEDE5" : WHITE },
      align: ci === 1 ? "center" : "left",
    },
  }))), {
    x: M + 5.7, y: 1.85, w: 6.4, colW: [1.5, 1.2, 3.7],
    rowH: 0.44, fontFace: BODY, fontSize: 12, valign: "middle",
    border: { type: "solid", color: "DDE2EC", pt: 0.5 },
  });
  s.addText("Nhầm theo hướng nào?", {
    x: M + 5.7, y: 4.6, w: 6.4, h: 0.32, fontFace: BODY, fontSize: 13.5, bold: true,
    color: NAVY, isTextBox: true, margin: 0,
  });
  bullets(s, M + 5.7, 4.95, 6.4, 1.5, [
    "FN: 13/98 = 13,3% của lớp gian lận   ·   FP: 47/56.864 = 0,083% của lớp hợp lệ",
    "Theo tỉ lệ trong lớp: nhầm nhiều hơn theo hướng BỎ SÓT. Theo số tuyệt đối: FP nhiều hơn.",
    "Trung vị Amount của các FP là €1,00 — ma sát rơi vào khoản mua vặt, không vào giao dịch lớn.",
  ], 12);
  s.addNotes(
    "Mô hình vô địch bắt được 85 trên 98 vụ, precision 64,4%, recall 86,7%. " +
    "Accuracy 99,89% được đưa vào bảng chỉ để bác bỏ nó: mô hình hằng số đã đạt 99,83%. " +
    "Precision 64,4% nghĩa là cứ ba cảnh báo thì khoảng một là báo động giả — chấp nhận được, " +
    "vì mỗi báo động giả chỉ tốn ba euro trong khi một vụ bắt được có thể đáng hàng trăm. " +
    "Đó chính là lý do nhóm tối ưu chi phí chứ không tối ưu F1: F1 coi một FP và một FN nặng như nhau. " +
    "Một quan sát thú vị ở dòng cuối: trung vị số tiền của các báo động giả chỉ một euro, " +
    "nghĩa là ma sát rơi vào những khoản mua vặt chứ không vào giao dịch lớn."
  );
}

/* ---- 5.4 phân tích lỗi */
{
  const s = slide(5, "Kết quả", "Phân tích lỗi — đếm LỖI và đếm TIỀN là hai câu chuyện khác nhau");
  fig(s, "F08_bo-sot-theo-decile.png", M, 1.72, 8.1, 4.5);
  stat(s, M + 8.45, 1.85, 3.65, "€8.817,00", "giá trị thu hồi được — 82,8% của €10.644,93", GREEN);
  stat(s, M + 8.45, 3.52, 3.65, "€1.827,93", "giá trị mất do bỏ sót", ORANGE);
  s.addShape(p.ShapeType.roundRect, { x: M + 8.45, y: 5.19, w: 3.65, h: 1.5, rectRadius: 0.08, fill: { color: NAVY } });
  s.addText("Decile 5 tệ nhất theo TỈ LỆ (40%).\nDecile 10 tệ nhất theo TIỀN: €1.684 / €1.828 = 92% toàn bộ thiệt hại.", {
    x: M + 8.67, y: 5.32, w: 3.2, h: 1.25, fontFace: BODY, fontSize: 12.5, color: WHITE,
    lineSpacingMultiple: 1.12, isTextBox: true, margin: 0,
  });
  s.addText("Một nhóm tối ưu theo recall sẽ dồn công sức vào decile 5 — nơi tỉ lệ lỗi cao nhất nhưng gần như không có tiền.", {
    x: M, y: 6.4, w: 8.1, h: 0.45, fontFace: BODY, fontSize: 13, italic: true, bold: true,
    color: ORANGE, isTextBox: true, margin: 0,
  });
  s.addNotes(
    "Nhóm chia các vụ bỏ sót theo decile giá trị giao dịch, và kết quả cho hai câu trả lời khác nhau tuỳ cách nhìn. " +
    "Nếu nhìn theo tỉ lệ bỏ sót, decile 5 tệ nhất với 40%. " +
    "Nhưng nếu nhìn theo số tiền mất đi, decile 10 — nhóm giá trị cao nhất — mới là nơi thiệt hại thật: " +
    "1.684 euro trên tổng 1.828, tức khoảng 92% toàn bộ thiệt hại nằm gọn trong một decile duy nhất. " +
    "Ý nghĩa thực tiễn rất rõ: một nhóm tối ưu theo recall sẽ dồn công sức vào decile 5, nơi tỉ lệ lỗi cao nhất " +
    "nhưng gần như không có tiền, và bỏ qua decile 10 là nơi chứa gần như toàn bộ thiệt hại."
  );
}

/* ---- 5.5 overfitting */
{
  const s = slide(5, "Kết quả", "Overfitting hay underfitting — đo bằng PR-AUC, không đo bằng chi phí");
  fig(s, "F14_train-vs-validation-prauc.png", M, 1.75, 6.6, 4.3);
  s.addShape(p.ShapeType.roundRect, { x: M + 7.0, y: 1.85, w: 5.1, h: 1.15, rectRadius: 0.08, fill: { color: LIGHT } });
  s.addText("Vì sao KHÔNG dùng chi phí để so train vs val?", {
    x: M + 7.22, y: 1.96, w: 4.66, h: 0.3, fontFace: BODY, fontSize: 12.5, bold: true,
    color: NAVY, isTextBox: true, margin: 0,
  });
  s.addText("Ngưỡng t* được chọn trên chính tập validation đó, nên mọi thước đo TẠI t* bị thiên lệch lạc quan. PR-AUC độc lập với ngưỡng nên không dính lỗi này.", {
    x: M + 7.22, y: 2.28, w: 4.66, h: 0.65, fontFace: BODY, fontSize: 12, color: INK,
    lineSpacingMultiple: 1.08, isTextBox: true, margin: 0,
  });
  s.addText("Chẩn đoán", {
    x: M + 7.0, y: 3.2, w: 5.1, h: 0.32, fontFace: BODY, fontSize: 13.5, bold: true,
    color: NAVY, isTextBox: true, margin: 0,
  });
  bullets(s, M + 7.0, 3.55, 5.1, 2.5, [
    "RF và XGBoost OVERFIT rõ: PR-AUC train đúng bằng 1,0000 — cây không cắt tỉa đã cô lập từng dòng gian lận trong train.",
    "Logistic KHÔNG overfit (+0,0784) nhưng cũng không underfit hẳn — thiên lệch cao, phương sai thấp.",
    "Overfit nhiều nhất (RF) KHÔNG đồng nghĩa tệ nhất trên test — RF vẫn giảm 77% chi phí.",
  ], 12);
  s.addNotes(
    "Nhóm so sánh train và validation bằng PR-AUC chứ không bằng chi phí, và lý do phải nói rõ: " +
    "ngưỡng được chọn trên chính tập validation đó, nên mọi thước đo tại ngưỡng đó bị thiên lệch lạc quan. " +
    "PR-AUC độc lập với ngưỡng nên không dính lỗi này. " +
    "Chẩn đoán: Random Forest và XGBoost overfit rõ rệt, cả hai đạt PR-AUC train đúng bằng một — " +
    "nghĩa là cây không cắt tỉa đã cô lập được từng dòng gian lận riêng lẻ trong tập train. " +
    "Hồi quy logistic thì ngược lại, khoảng cách chỉ 0,078. " +
    "Điều đáng chú ý: mô hình overfit nhiều nhất không phải mô hình tệ nhất trên test."
  );
}

/* ---- 5.6 policy E thua */
{
  const s = slide(5, "Kết quả", "Kết quả 3 — quy tắc Bayes tối ưu đã THUA, và nhóm nói thẳng");
  fig(s, "F12_chinh-sach-A-vs-E.png", M, 1.72, 5.9, 3.5);
  fig(s, "F10_hieu-chuan-vung-duoi.png", M + 6.2, 1.72, 5.9, 3.5);
  s.addShape(p.ShapeType.roundRect, { x: M, y: 5.35, w: 5.9, h: 1.4, rectRadius: 0.08, fill: { color: "FDEDE5" } });
  s.addText("E không thắng A ở mô hình nào; thua CÓ Ý NGHĨA THỐNG KÊ với hồi quy logistic (+€199,23, KTC [132,51 ; 266,36]).", {
    x: M + 0.22, y: 5.48, w: 5.46, h: 1.15, fontFace: BODY, fontSize: 13, color: INK,
    lineSpacingMultiple: 1.12, isTextBox: true, margin: 0,
  });
  s.addShape(p.ShapeType.roundRect, { x: M + 6.2, y: 5.35, w: 5.9, h: 1.4, rectRadius: 0.08, fill: { color: NAVY } });
  s.addText("Vì sao? Hiệu chuẩn TỔNG HỢP thì tốt (0,71× / 1,04× / 1,02×) — nhưng tách theo decile của Amount, tỉ lệ dao động 0,39× đến 2,14×. Sai lệch cục bộ triệt tiêu nhau khi lấy trung bình.", {
    x: M + 6.42, y: 5.48, w: 5.46, h: 1.15, fontFace: BODY, fontSize: 12.5, color: WHITE,
    lineSpacingMultiple: 1.12, isTextBox: true, margin: 0,
  });
  s.addNotes(
    "Đây là kết quả âm mà nhóm coi là đóng góp chính. Chính sách E — quy tắc tối ưu Bayes về mặt lý thuyết — " +
    "không thắng được một ngưỡng đã dò ở bất kỳ mô hình nào, và thua có ý nghĩa thống kê với hồi quy logistic. " +
    "Nhóm đã đi tìm nguyên nhân. Hiệu chuẩn tổng hợp thì tốt cho cả ba mô hình, nên miscalibration đơn giản " +
    "không giải thích được. Nhưng Chính sách E không so xác suất với một ngưỡng chung — nó so với một ngưỡng " +
    "riêng cho từng giao dịch, bằng ba euro chia cho số tiền. Với giao dịch mười euro thì ngưỡng là 0,3, " +
    "còn giao dịch một nghìn euro thì ngưỡng chỉ 0,003. " +
    "Tách hiệu chuẩn theo decile của số tiền, tỉ lệ dao động từ 0,39 đến 2,14 lần. " +
    "Nhóm cũng đã thử hiệu chuẩn lại bằng Platt và isotonic — kết quả còn tệ hơn cho hai trên ba mô hình. " +
    "Giải thích trung thực là khan hiếm dữ liệu ở vùng đuôi."
  );
}

/* ---- 5.7 độ nhạy c_review */
{
  const s = slide(5, "Kết quả", "Kết luận có phụ thuộc con số €3 không? — quét c_review từ €1 đến €20");
  fig(s, "F13_quet-c-review.png", M + 3.1, 1.78, 7.1, 4.4);
  s.addText("Nhóm không có số liệu vận hành thật cho c_review, nên thay vì cố định một con số, nhóm báo cáo ĐỘ NHẠY.", {
    x: M, y: 6.35, w: W - 2 * M, h: 0.45, align: "center",
    fontFace: BODY, fontSize: 13.5, italic: true, color: MUTED, isTextBox: true, margin: 0,
  });
  s.addNotes(
    "Câu hỏi tự nhiên: kết luận có phụ thuộc con số ba euro nhóm tự đặt ra không? " +
    "Nhóm quét c_review từ một đến hai mươi euro. Thứ hạng ba mô hình không đổi, và cả ba luôn nằm dưới " +
    "đường không làm gì trên toàn dải quét. " +
    "Có một điểm tinh tế đáng nêu: c_review nằm bên trong công thức của Chính sách E, " +
    "nên quét nó làm thay đổi chính chính sách đó, chứ không chỉ thay đổi cách đánh giá."
  );
}

/* ---- 5.8 khuyến nghị */
{
  const s = slide(5, "Kết quả", "Vậy chọn mô hình nào? — chọn cái đơn giản hơn");
  const t = [
    ["Tiêu chí", "Logistic Regression", "Random Forest", "XGBoost (balanced)"],
    ["Chi phí test", "€2.231,31", "€2.453,93", "€2.223,93"],
    ["PR-AUC test", "0,7406", "0,8689", "0,8693"],
    ["Khoảng cách train→val", "+0,0784", "+0,2008", "+0,1772"],
    ["Thời gian huấn luyện", "0,2 s", "5,8 s", "1,1 s"],
    ["Khả năng giải thích", "cao", "thấp", "thấp"],
  ];
  s.addTable(t.map((r, ri) => r.map((c, ci) => ({
    text: c,
    options: {
      bold: ri === 0 || ci === 1, color: ri === 0 ? WHITE : INK,
      fill: { color: ri === 0 ? NAVY : ci === 1 ? ICE : WHITE },
      align: ci === 0 ? "left" : "center",
    },
  }))), {
    x: M, y: 1.85, w: W - 2 * M, colW: [3.0, 3.05, 3.0, 3.04],
    rowH: 0.46, fontFace: BODY, fontSize: 13, valign: "middle",
    border: { type: "solid", color: "DDE2EC", pt: 0.5 },
  });
  s.addShape(p.ShapeType.roundRect, { x: M, y: 4.85, w: W - 2 * M, h: 1.05, rectRadius: 0.08, fill: { color: NAVY } });
  s.addText("Khuyến nghị: HỒI QUY LOGISTIC — chi phí không phân biệt được với mô hình tốt nhất (chênh €6,67), huấn luyện nhanh hơn ~29 lần, overfit ít hơn hẳn, và giải thích được.", {
    x: M + 0.28, y: 4.85, w: W - 2 * M - 0.56, h: 1.05, valign: "middle",
    fontFace: BODY, fontSize: 15, bold: true, color: WHITE, lineSpacingMultiple: 1.1,
    isTextBox: true, margin: 0,
  });
  s.addText("Ngược lại, nếu ưu tiên chất lượng XẾP HẠNG cho các ngưỡng vận hành khác trong tương lai: PR-AUC 0,8693 của XGBoost vượt rõ 0,7406 — khác biệt này là THẬT, chỉ là nó không chuyển thành chênh lệch chi phí ở điểm vận hành cụ thể này.", {
    x: M, y: 6.05, w: W - 2 * M, h: 0.7, fontFace: BODY, fontSize: 13, italic: true,
    color: MUTED, lineSpacingMultiple: 1.1, isTextBox: true, margin: 0,
  });
  s.addNotes(
    "Vì ba mô hình không phân biệt được về chi phí, tiêu chí chọn phải chuyển sang các yếu tố khác. " +
    "Nhóm khuyến nghị hồi quy logistic: chi phí chênh 6,67 euro so với mô hình tốt nhất và không có ý nghĩa " +
    "thống kê, nhưng huấn luyện nhanh hơn khoảng 29 lần, overfit ít hơn hẳn, và giải thích được. " +
    "Khi hai lựa chọn không phân biệt được về kết quả, nên chọn cái đơn giản hơn. " +
    "Ngược lại, nếu sau này cần dùng mô hình ở nhiều ngưỡng vận hành khác nhau thì PR-AUC của XGBoost " +
    "vượt rõ — khác biệt đó là thật, chỉ là nó không chuyển thành tiền ở điểm vận hành cụ thể này."
  );
}

/* ============================================================== DIVIDER 6 */
divider(6, "ỨNG DỤNG, KẾT LUẬN & HƯỚNG PHÁT TRIỂN", "Ứng dụng thực tế · Kết luận · Hạn chế · Hướng phát triển")
  .addNotes("Phần sáu, phần cuối.");

/* ---- 6.1 ứng dụng */
{
  const s = slide(6, "Ứng dụng & kết luận", "Ứng dụng thực tế — và một thứ KHÔNG nên làm");
  card(s, M, 1.78, 3.9, 2.05, "Một quy tắc vận hành triển khai được",
    "132 cảnh báo trên 56.962 giao dịch trong 2 ngày ≈ 66 cảnh báo/ngày — nằm trong sức của MỘT nhân viên rà soát. Mô hình tối ưu recall sẽ phát hàng nghìn cảnh báo và làm sập hàng đợi.", NAVY);
  card(s, M + 4.15, 1.78, 3.9, 2.05, "Một cách định cỡ đội rà soát",
    "Đường cong chi phí trả lời trực tiếp “nên rà soát bao nhiêu mỗi ngày”: cực tiểu ở 79–121 cảnh báo, và đường cong khá PHẲNG quanh đó ⇒ tổ chức có khoảng linh hoạt.", NAVY);
  card(s, M + 8.3, 1.78, 3.8, 2.05, "Một khung đánh giá tái sử dụng được",
    "fraud_cost.py không phụ thuộc bộ dữ liệu này. Bất kỳ bài toán nào có chi phí lỗi phụ thuộc từng mẫu — thu hồi nợ, bảo hiểm, kiểm định chất lượng — đều dùng lại được.", NAVY);

  s.addShape(p.ShapeType.roundRect, { x: M, y: 4.15, w: W - 2 * M, h: 1.75, rectRadius: 0.08, fill: { color: "FDEDE5" } });
  s.addText("Điều KHÔNG nên làm: đem thẳng mô hình này vào sản xuất", {
    x: M + 0.28, y: 4.3, w: W - 2 * M - 0.56, h: 0.34, fontFace: BODY, fontSize: 14.5,
    bold: true, color: RED, isTextBox: true, margin: 0,
  });
  bullets(s, M + 0.28, 4.68, W - 2 * M - 0.56, 1.1, [
    "V1–V28 là PCA fit trên đúng 48 giờ đó — không tái tạo được cho giao dịch mới",
    "Bộ dữ liệu không có định danh thẻ ⇒ thiếu hẳn nhóm đặc trưng quan trọng nhất theo Bahnsen 2016",
    "c_review = €3 là giả định của nhóm, không phải số liệu vận hành",
  ], 12.5);
  keyline(s, 6.1, "Cái tái sử dụng được là PHƯƠNG PHÁP, không phải trọng số mô hình.");
  s.addNotes(
    "Kết quả của đồ án chuyển thành ba thứ dùng được ngay, và một thứ không nên làm. " +
    "Thứ nhất, một quy tắc vận hành: 132 cảnh báo trong hai ngày, tức khoảng 66 mỗi ngày, " +
    "hoàn toàn nằm trong sức của một nhân viên. Thứ hai, đường cong chi phí trả lời trực tiếp " +
    "câu hỏi nên rà soát bao nhiêu giao dịch mỗi ngày, và nó khá phẳng quanh cực tiểu nên tổ chức có " +
    "khoảng linh hoạt. Thứ ba, khung đánh giá tái sử dụng được cho bất kỳ bài toán nào có chi phí lỗi " +
    "phụ thuộc từng mẫu. " +
    "Còn điều không nên làm là đem thẳng mô hình này vào sản xuất — vì ba lý do trong ô đỏ."
  );
}

/* ---- 6.2 kết luận */
{
  const s = slide(6, "Ứng dụng & kết luận", "Kết luận — năm điểm");
  const items = [
    ["Máy học là CẦN THIẾT, và điều đó đã được chứng minh", "Baseline không-ML tốn €12.398,63 — tệ hơn cả không làm gì. Cả ba mô hình giảm ~79% chi phí."],
    ["KHÔNG thể tuyên bố mô hình nào thắng", "Chênh €6,67, KTC chứa số 0, tỉ lệ thắng 53,3%. Với n_eff = 18,1 đây là kết quả ĐÃ ĐƯỢC DỰ BÁO."],
    ["Quy tắc tối ưu Bayes đã THUA", "Nguyên nhân là hiệu chuẩn ở đuôi (0,39×–2,14× theo decile), không phải miscalibration tổng hợp."],
    ["42% số vụ gian lận rẻ hơn phí rà soát", "Chính sách tối ưu chi phí CỐ Ý bỏ qua gần một nửa số vụ — hệ quả không tránh được của việc lấy tiền làm hàm mục tiêu."],
    ["Đếm lỗi khác với đếm tiền mất", "Decile 5 tệ nhất theo tỉ lệ (40%), nhưng decile 10 gây ra 92% thiệt hại."],
  ];
  items.forEach((it, i) => {
    const y = 1.75 + i * 0.99;
    s.addShape(p.ShapeType.ellipse, { x: M, y: y + 0.08, w: 0.4, h: 0.4, fill: { color: i === 1 ? ORANGE : NAVY } });
    s.addText(String(i + 1), {
      x: M, y: y + 0.08, w: 0.4, h: 0.4, align: "center", valign: "middle",
      fontFace: BODY, fontSize: 13, bold: true, color: WHITE, isTextBox: true, margin: 0,
    });
    s.addText(it[0], {
      x: M + 0.62, y, w: W - 2 * M - 0.62, h: 0.34, valign: "middle",
      fontFace: BODY, fontSize: 15, bold: true, color: NAVY, isTextBox: true, margin: 0,
    });
    s.addText(it[1], {
      x: M + 0.62, y: y + 0.35, w: W - 2 * M - 0.62, h: 0.55, valign: "top",
      fontFace: BODY, fontSize: 12.5, color: INK, lineSpacingMultiple: 1.05,
      isTextBox: true, margin: 0,
    });
  });
  s.addNotes(
    "Năm kết luận. Một: máy học là cần thiết và điều đó đã được chứng minh chứ không giả định. " +
    "Hai: không thể tuyên bố mô hình nào thắng, và với cỡ mẫu hiệu dụng 18 thì đây là kết quả đã được dự báo trước. " +
    "Ba: quy tắc tối ưu Bayes đã thua, nguyên nhân là hiệu chuẩn ở đuôi. " +
    "Bốn: 42% số vụ gian lận rẻ hơn phí rà soát, nên chính sách tối ưu cố ý bỏ qua chúng. " +
    "Năm: đếm lỗi và đếm tiền là hai câu chuyện khác nhau."
  );
}

/* ---- 6.3 hạn chế + hướng phát triển */
{
  const s = slide(6, "Ứng dụng & kết luận", "Hạn chế — nêu thẳng — và hướng phát triển");
  s.addShape(p.ShapeType.roundRect, { x: M, y: 1.78, w: 6.0, h: 4.35, rectRadius: 0.08, fill: { color: "FDEDE5" } });
  s.addText("HẠN CHẾ", {
    x: M + 0.25, y: 1.92, w: 5.5, h: 0.34, fontFace: BODY, fontSize: 13, bold: true,
    color: RED, charSpacing: 1.4, isTextBox: true, margin: 0,
  });
  bullets(s, M + 0.25, 2.35, 5.5, 3.6, [
    "Không kết luận được mô hình nào tốt nhất (n_eff = 18,1) — giới hạn cơ bản của dữ liệu",
    "Chính sách E thua, và nhóm chỉ CHẨN ĐOÁN được nguyên nhân chứ chưa CHỨNG MINH",
    "Tỉ lệ hiệu chuẩn tại biên của XGBoost dựa trên n = 10 — quá ít để tin; nhóm báo cáo kèm cỡ mẫu",
    "V1–V28 fit PCA trên cả 48 giờ ⇒ chia theo thời gian không loại bỏ được look-ahead",
    "c_review = €3 là giả định; mô hình chi phí bỏ qua ma sát khách hàng do FP",
    "Toàn bộ đồ án chạy ở tham số mặc định (có chủ ý, nhưng vẫn là một chiều chưa khám phá)",
  ], 12);

  s.addShape(p.ShapeType.roundRect, { x: M + 6.35, y: 1.78, w: 5.75, h: 4.35, rectRadius: 0.08, fill: { color: NAVY } });
  s.addText("HƯỚNG PHÁT TRIỂN", {
    x: M + 6.6, y: 1.92, w: 5.25, h: 0.34, fontFace: BODY, fontSize: 13, bold: true,
    color: ORANGE, charSpacing: 1.4, isTextBox: true, margin: 0,
  });
  s.addText([
    { text: "Tăng cỡ mẫu hiệu dụng — chọn ngưỡng bằng out-of-fold CV 5 fold nâng n_eff cho BƯỚC CHỌN từ ~18 lên ~73", options: { bullet: { code: "2013" }, breakLine: true } },
    { text: "Hiệu chuẩn có TRỌNG SỐ THEO CHI PHÍ — Platt và isotonic tối ưu log-loss trên toàn dải, còn E chỉ cần p đúng trong một dải hẹp. Chưa ai thử.", options: { bullet: { code: "2013" }, breakLine: true } },
    { text: "Đưa chi phí ma sát của FP vào mô hình và đo lại xem thứ hạng có đảo không", options: { bullet: { code: "2013" }, breakLine: true } },
    { text: "Huấn luyện nhạy chi phí: sample_weight = Amount cho lớp gian lận", options: { bullet: { code: "2013" }, breakLine: true } },
    { text: "Lặp lại thí nghiệm A-vs-E trên IEEE-CIS (3,5% gian lận) — nếu E thắng ở đó, giả thuyết “khan hiếm dữ liệu ở đuôi” được củng cố", options: { bullet: { code: "2013" } } },
  ], {
    x: M + 6.6, y: 2.35, w: 5.25, h: 3.6, fontFace: BODY, fontSize: 12, color: WHITE,
    lineSpacingMultiple: 1.1, paraSpaceAfter: 8, isTextBox: true, margin: 0,
  });
  s.addText("Một báo cáo tự nêu giới hạn của mình mạnh hơn một báo cáo giấu chúng đi.", {
    x: M, y: 6.3, w: W - 2 * M, h: 0.4, align: "center", fontFace: BODY, fontSize: 13,
    italic: true, color: MUTED, isTextBox: true, margin: 0,
  });
  s.addNotes(
    "Nhóm liệt kê hạn chế đầy đủ, không né tránh. Nghiêm trọng nhất là hai dòng đầu: " +
    "không kết luận được mô hình nào tốt nhất, và Chính sách E thua mà nhóm mới chỉ chẩn đoán được nguyên nhân " +
    "chứ chưa chứng minh. Dòng ba cũng quan trọng: tỉ lệ hiệu chuẩn tại biên quyết định của XGBoost " +
    "chỉ dựa trên mười quan sát, nhóm báo cáo kèm cỡ mẫu và không dùng nó để lập luận. " +
    "Về hướng phát triển, hai hướng nhóm thấy hứa hẹn nhất là hiệu chuẩn có trọng số theo chi phí — " +
    "theo khảo sát của nhóm thì chưa ai thử — và lặp lại thí nghiệm này trên IEEE-CIS, " +
    "nơi tỉ lệ gian lận cao gấp hai mươi lần nên có nhiều dữ liệu hơn hẳn ở vùng đuôi."
  );
}

/* ============================================================== THANK YOU */
{
  const s = darkSlide();
  num();
  s.addText("Cảm ơn thầy cô đã lắng nghe", {
    x: M + 0.3, y: 2.1, w: W - 2 * M - 0.6, h: 0.9,
    fontFace: HEAD, fontSize: 38, bold: true, color: WHITE, isTextBox: true, margin: 0,
  });
  s.addText("Nhóm sẵn sàng trả lời câu hỏi.", {
    x: M + 0.3, y: 3.05, w: W - 2 * M - 0.6, h: 0.5,
    fontFace: BODY, fontSize: 17, color: ICE, isTextBox: true, margin: 0,
  });
  const facts = [
    ["€2.223,93", "chi phí test của mô hình vô địch"],
    ["−79%", "so với không làm gì"],
    ["n_eff = 18,1", "lý do không ai thắng"],
    ["205 / 492", "vụ gian lận rẻ hơn phí rà soát"],
  ];
  facts.forEach((f, i) => {
    const x = M + 0.3 + i * 3.02;
    s.addText(f[0], {
      x, y: 4.5, w: 2.85, h: 0.55, fontFace: HEAD, fontSize: 24, bold: true,
      color: ORANGE, isTextBox: true, margin: 0,
    });
    s.addText(f[1], {
      x, y: 5.05, w: 2.85, h: 0.6, fontFace: BODY, fontSize: 12, color: ICE,
      lineSpacingMultiple: 1.1, isTextBox: true, margin: 0,
    });
  });
  s.addText("Toàn bộ số liệu tái lập được bằng một lệnh:  ./run.sh test  →  24 passed  ·  demo trực tiếp:  python3 demo.py", {
    x: M + 0.3, y: 6.35, w: W - 2 * M - 0.6, h: 0.4,
    fontFace: BODY, fontSize: 12.5, italic: true, color: ICE, isTextBox: true, margin: 0,
  });
  s.addNotes(
    "Nhóm xin cảm ơn thầy cô đã lắng nghe và sẵn sàng trả lời các câu hỏi. " +
    "Bốn con số trên màn hình là những gì nhóm mong hội đồng nhớ lại."
  );
}

p.writeFile({ fileName: "Slide_CS114_FraudDetection.pptx" }).then(() => {
  console.log("wrote Slide_CS114_FraudDetection.pptx —", n, "slides");
});
