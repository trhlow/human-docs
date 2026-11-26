# Bộ định dạng: thông số và nguồn

Mọi bộ dùng khổ A4 dọc, phông Times New Roman màu đen, lề trên 2 cm, dưới 2 cm, trái 3 cm, phải 1,5 cm. Bốn số lề này là cận dưới của khoảng NĐ 30/2020 cho phép (Phụ lục I, Mục I.3: trên, dưới 20–25 mm; trái 30–35 mm; phải 15–20 mm), nên cùng một bộ lề dùng được cho cả văn bản hành chính. Thông số nằm trong `PROFILES` của `scripts/word_style.py`; `check_docx.py` đọc cùng bảng đó.

Mẫu của nơi nhận luôn thắng. Các bộ dưới đây chỉ dùng khi không có mẫu.

## thesis: đồ án, khóa luận, luận văn

| Thông số | Giá trị |
|---|---|
| Cỡ chữ nội dung | 13 pt; Heading 1 14 pt |
| Giãn dòng, cách đoạn | 1,5 dòng; sau đoạn 6 pt |
| Thụt đầu dòng | 0 |
| Tiêu đề | "CHƯƠNG 1: TÊN CHƯƠNG" (in hoa, đậm, căn giữa), "1.1 Tên mục", "1.1.1 Tên tiểu mục" (đậm, căn trái), Word đánh số |

Nguồn: mặc định của skill, không lấy từ một quy định cụ thể nào; lề, cỡ chữ, giãn dòng nằm trong khoảng NĐ 30 cho phép. Trường có quy định thì làm theo quy định đó (lề, cỡ chữ, cách đánh số chương, trang bìa), và báo cho người dùng biết những điểm đã khác bộ này.

## report: báo cáo, đề xuất, kế hoạch trong công ty

| Thông số | Giá trị |
|---|---|
| Cỡ chữ nội dung | 13 pt; Heading 1 14 pt |
| Giãn dòng, cách đoạn | 1,5 dòng; sau đoạn 6 pt |
| Thụt đầu dòng | 1,27 cm |
| Tiêu đề | "1. Tên phần", "1.1. Tên mục", "1.1.1. Tên tiểu mục" (đậm, căn trái, viết hoa kiểu câu), Word đánh số |

Nguồn: mặc định của skill, không lấy từ một quy định cụ thể nào. Cỡ chữ, thụt đầu dòng, cách đoạn và giãn dòng lấy trong khoảng NĐ 30 quy định cho phần nội dung văn bản hành chính (Phụ lục I, II.6.e, trích ở dưới), để báo cáo nội bộ trông cùng một lối với văn bản hành chính. Cách đánh số tiêu đề là quy ước của skill.

## guide: tài liệu hướng dẫn, quy trình

Cùng thông số với `report`. Khác ở cách viết: các bước làm theo thứ tự dùng `ws.steps` (Word đánh số 1., 2., ...), lệnh và mã dùng `ws.code`, ảnh chụp màn hình dùng `ws.picture` và chỉ chụp vùng cần nói tới.

## admin: văn bản hành chính theo Nghị định 30/2020/NĐ-CP

Nguồn: Phụ lục I "Thể thức, kỹ thuật trình bày văn bản hành chính và bản sao văn bản", kèm theo Nghị định số 30/2020/NĐ-CP ngày 05/3/2020 của Chính phủ về công tác văn thư. Bản đã đọc: tệp PDF phụ lục trên vanban.vcci.com.vn (`hm_content/uploads/van-ban/ND_30-2020-ND-CP_Phu_luc.pdf`), đọc ngày 26/11/2026. Skill chưa xác minh được tình trạng hiệu lực của Nghị định tại thời điểm viết: trước khi dùng cho văn bản chính thức, kiểm tra trên Cổng thông tin điện tử Chính phủ hoặc Cơ sở dữ liệu quốc gia về văn bản pháp luật xem Nghị định còn hiệu lực và có được sửa đổi không.

Trích nguyên văn các quy định skill dùng:

- Khổ giấy (I.1): "Khổ A4 (210 mm x 297 mm)."
- Kiểu trình bày (I.2): "Theo chiều dài của khổ A4. Trường hợp nội dung văn bản có các bảng, biểu nhưng không được làm thành các phụ lục riêng thì văn bản có thể được trình bày theo chiều rộng."
- Định lề (I.3): "Cách mép trên và mép dưới 20 - 25 mm, cách mép trái 30 - 35 mm, cách mép phải 15 - 20 mm."
- Phông chữ (I.4): "Phông chữ tiếng Việt Times New Roman, bộ mã ký tự Unicode theo Tiêu chuẩn Việt Nam TCVN 6909:2001, màu đen."
- Số trang (I.7): "Được đánh từ số 1, bằng chữ số Ả Rập, cỡ chữ 13 đến 14, kiểu chữ đứng, được đặt canh giữa theo chiều ngang trong phần lề trên của văn bản, không hiển thị số trang thứ nhất."
- Nội dung (II.6.e): "Nội dung văn bản được trình bày bằng chữ in thường, được canh đều cả hai lề, kiểu chữ đứng; cỡ chữ từ 13 đến 14; khi xuống dòng, chữ đầu dòng lùi vào 1 cm hoặc 1,27 cm; khoảng cách giữa các đoạn văn tối thiểu là 6pt; khoảng cách giữa các dòng tối thiểu là dòng đơn, tối đa là 1,5 lines."
- Phần, chương (II.6.đ): từ "Phần", "Chương" và số thứ tự (chữ số La Mã) "trên một dòng riêng, canh giữa, bằng chữ in thường, cỡ chữ từ 13 đến 14, kiểu chữ đứng, đậm"; tiêu đề ngay dưới, "canh giữa, bằng chữ in hoa". Mục, tiểu mục giống vậy, số thứ tự dùng chữ số Ả Rập.
- Điều (II.6.đ): "Từ “Điều”, số thứ tự và tiêu đề của điều được trình bày bằng chữ in thường, lùi đầu dòng 1 cm hoặc 1,27 cm. Số thứ tự của điều dùng chữ số Ả Rập, sau số thứ tự có dấu chấm (.); cỡ chữ bằng cỡ chữ của phần lời văn, kiểu chữ đứng, đậm." Khoản: số Ả Rập, sau có dấu chấm; điểm: chữ cái tiếng Việt, sau có dấu đóng ngoặc đơn.

Thành phần thể thức và hàm dựng:

| Ô (sơ đồ Mục IV) | Thành phần | Quy định (Mục II, bảng Mục V) | Trong skill |
|---|---|---|---|
| 1 | Quốc hiệu, Tiêu ngữ | Quốc hiệu in hoa, 12–13, đứng, đậm, phía trên bên phải; Tiêu ngữ in thường, 13–14, đứng, đậm, canh giữa dưới Quốc hiệu, kẻ dưới "có độ dài bằng độ dài của dòng chữ"; hai dòng cách nhau dòng đơn | `admin_header`, cột phải |
| 2 | Tên cơ quan ban hành | Chủ quản in hoa 12–13 đứng; cơ quan ban hành in hoa 12–13 đứng đậm, kẻ dưới dài "từ 1/3 đến 1/2 độ dài của dòng chữ" | `admin_header`, cột trái; `rule_ratio` mặc định 1/3 |
| 3 | Số, ký hiệu | Canh giữa dưới tên cơ quan; "Số" in thường cỡ 13, ký hiệu in hoa cỡ 13; số nhỏ hơn 10 thêm số 0 phía trước | `admin_header(number=...)` |
| 4 | Địa danh, ngày tháng | Cùng dòng với số, ký hiệu; in thường, 13–14, nghiêng; canh giữa dưới Quốc hiệu, Tiêu ngữ; ngày nhỏ hơn 10 và tháng 1, 2 thêm số 0 | `admin_header(place_date=...)` |
| 5a | Tên loại, trích yếu | Canh giữa; tên loại in hoa 13–14 đứng đậm; trích yếu in thường 13–14 đứng đậm, kẻ dưới 1/3–1/2 dòng chữ | `admin_header(doc_type=..., summary=...)` |
| 5b | Trích yếu công văn | Sau "V/v", in thường 12–13 đứng, canh giữa dưới số và ký hiệu, cách 6 pt | `admin_header(vv=...)` |
| 7a, 7b | Quyền hạn, chức vụ, họ tên người ký | "TM.", "Q.", "KT.", "TL.", "TUQ." và chức vụ in hoa 13–14 đứng đậm; họ tên in thường 13–14 đứng đậm, canh giữa | `admin_signature(authority=..., name=...)` |
| 9a | Kính gửi | In thường 13–14 đứng; một nơi nhận cùng dòng; nhiều nơi thì mỗi nơi một dòng, gạch đầu dòng thẳng hàng dưới dấu hai chấm, cuối dòng ";", dòng cuối "." | `admin_header(to=[...])` hoặc `kinh_gui` |
| 9b | Nơi nhận | "Nơi nhận" cỡ 12, nghiêng, đậm, sát lề trái, ngang hàng dòng chức vụ người ký; danh sách cỡ 11 đứng, mỗi nơi một dòng có gạch đầu dòng, cuối ";"; dòng cuối "Lưu: VT, ..." kết thúc bằng "." | `admin_signature(recipients=..., archive=...)` |

Chú thích của bảng Mục V: "Cỡ chữ trong cùng một văn bản tăng, giảm phải thống nhất, ví dụ: Quốc hiệu cỡ chữ 13, Tiêu ngữ cỡ chữ 14, địa danh và ngày, tháng, năm văn bản cỡ chữ 14 hoặc Quốc hiệu cỡ chữ 12, Tiêu ngữ cỡ chữ 13, địa danh và ngày, tháng, năm văn bản cỡ chữ 13." Skill dùng bộ 13/14/14 khi nội dung cỡ 14, bộ 12/13/13 khi nội dung cỡ 13.

Những chỗ Nghị định cho một khoảng hoặc không ghi số, skill tự chọn (sửa được khi người dùng muốn khác):

- Cỡ chữ nội dung 14 (khoảng 13–14), giãn dòng đơn (khoảng đơn đến 1,5), cách sau đoạn 6 pt (tối thiểu 6 pt), thụt đầu dòng 1,27 cm (1 hoặc 1,27 cm).
- Vị trí khối "Kính gửi" (`indent_cm=2.5`) và khoảng trống ký tên (`signature_space_pt=72`): sơ đồ Mục IV chỉ vẽ vị trí tương đối.
- Ô 1–4 và 7, 9b đặt trong bảng không viền hai cột, cột phải vừa Quốc hiệu trên một dòng. Nghị định không quy định cách dựng trong Word, chỉ quy định vị trí.

Các mẫu trình bày đầy đủ (Mẫu 1.1 Nghị quyết đến 1.10 Giấy nghỉ phép, Mẫu 1.4 "Văn bản có tên loại" dùng cho báo cáo, tờ trình, thông báo, kế hoạch..., Mẫu 1.5 Công văn) nằm ở Phụ lục III của Nghị định; quy tắc viết hoa (tên người, địa danh, cơ quan) nằm ở Phụ lục II. Khi làm một loại văn bản cụ thể, đối chiếu với mẫu tương ứng ở Phụ lục III.
