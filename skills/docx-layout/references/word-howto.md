# Trình bày Word bằng python-docx: cách làm và các bẫy

Mã dựng sẵn: `scripts/word_style.py` (`setup`, `table`, `picture`, `bullets`, `steps`, `code`, `metadata`, `smart_quotes`, `admin_header`, `admin_signature`, `kinh_gui`). Máy quét: `scripts/check_docx.py`.
Có mẫu của nơi nhận thì dựng trên mẫu đó (`setup(doc, bộ, template=True)`): chỉ dùng và sửa style của mẫu, không thay bằng style mới.

## Style

- Style Heading của Word lấy font và màu từ theme (`asciiTheme`, `themeColor`): phải xóa các thuộc tính theme, chỉ đặt tên font thì chưa đủ. `word_style._black_font` làm việc này.
- Đánh số chương, mục bằng danh sách đa cấp gắn vào Heading 1–3 (`lvlText` ví dụ "CHƯƠNG %1:", "%1.%2", "%1.%2.%3"), không gõ số tay. Tiêu đề không số (MỞ ĐẦU, KẾT LUẬN, TÀI LIỆU THAM KHẢO) dùng style riêng có `outlineLvl` 0 để vẫn vào mục lục.
- Kiểu Hyperlink mặc định màu xanh: đổi sang đen. Mẫu có sẵn đôi khi còn run màu (đỏ, xanh) không thấy được vì không có chữ: quét toàn bộ `w:color` trong thân bài và chân trang.
- Style dựa trên Normal thừa hưởng thụt đầu dòng của Normal. Khi Normal thụt 1,27 cm (bộ `report`, `admin`) thì tiêu đề, chú thích, ô bảng phải đặt thụt 0 rõ ràng (`_paragraph_format` làm việc này).
- Phần tử trong `w:pPr` và `w:tblPr` phải đúng thứ tự của đặc tả OOXML, nếu không Word có thể báo tệp hỏng: chèn bằng `word_style._insert`, không `append`.

## Danh sách

- Ký hiệu: "-" (U+002D) font Times New Roman, hoặc "•". Gạch "–" (U+2013) rộng 0,5 em, gấp rưỡi gạch thường, nhìn như gạch dài.
- Thụt: ký hiệu ở vị trí thụt đầu dòng của đoạn văn (Normal thụt 1,27 cm thì `w:left` 1077, `w:hanging` 357), chữ cách ký hiệu 0,63 cm. Đặt thụt trên cả từng đoạn của danh sách để không phụ thuộc thứ tự ưu tiên giữa style và numbering.
- Danh sách đánh số (`steps`) tạo một `w:num` mới có `startOverride` mỗi lần gọi, để mỗi danh sách bắt đầu lại từ 1.
- Mẫu có sẵn có thể đã có style danh sách gắn với numbering của mẫu. Thêm một style cùng `styleId` thì Word vẫn dùng style của mẫu: sửa `lvlText` của numbering mà style của mẫu trỏ tới, hoặc đặt `styleId` mới.
- Dò trong PDF: `page.get_text("rawdict")` của PyMuPDF cho mã ký tự của ký hiệu đầu dòng; 0x2013 là gạch dài.

## Bảng

- Layout phải là fixed (`table.autofit = False`), và phải đặt cả `tblGrid` (`table.columns[j].width`), không chỉ `cell.width`. Nếu không, Word tự co giãn cột theo chữ và mọi bề rộng đã tính đều mất.
- Lề trong của ô là 0,19 cm mỗi bên. Bề rộng chữ thật trong ô bằng bề rộng ô trừ 0,38 cm.
- Muốn biết Word ngắt dòng ở đâu thì đo chữ bằng font thật: `pymupdf.Font(fontfile=...).text_length(chữ, fontsize=13)`. `check_docx.width_pt` tìm tệp font Times New Roman ở chỗ cài mặc định trên Windows, macOS và Linux (gói ttf-mscorefonts-installer); không thấy thì ước lượng 0,41 em mỗi ký tự, sai nhiều hơn.
- Word ngắt được sau dấu gạch nối trong một từ ("đầu-cuối"), không ngắt ở dấu cách không ngắt (U+00A0). Sau "/" thì Word chỉ đôi khi ngắt, không trông cậy được.
- Chọn độ rộng cột: `table()` tự làm khi không truyền `widths_cm`. `column_widths` cho điểm xuất phát (cột không hẹp hơn chữ dài nhất của nó), rồi `fit_widths` chuyển bề rộng giữa từng cặp cột (bước 1 mm, tối đa 3 cm, giữ tổng) và giữ cách chia có ít ô lẻ một chữ nhất, rồi đến bảng thấp nhất. Phải thử cả bước xa: một ô chỉ hết lẻ khi bề rộng vượt qua một ngưỡng, các bước 1 mm ở giữa không đổi gì. Kết quả vẫn phải xem trên PDF: dòng nằm sát mép trong vài điểm có thể ngắt khác.
- Ô vẫn lẻ một chữ ở mọi cách chia thì sửa câu chữ của ô cho ngắn hoặc dài ra, giữ nguyên nghĩa.
- Đường dẫn dài (URL, API) trong ô: mô phỏng việc xuống dòng bằng font thật và chèn ngắt dòng thật (`\n` trong `run.text` thành `w:br`) ở dấu "/" cuối cùng còn vừa dòng. Không chèn U+200B.
- Trích dẫn "[12, tr. 13]" không được tách dòng: thay các dấu cách bên trong bằng U+00A0.
- Căn giữa cả cột chỉ khi mọi ô trong cột đều ngắn (số, mã).
- Bảng đến 15 hàng không bị tách trang: `table()` đặt "keep with next" cho đoạn trong mọi hàng trừ hàng cuối. Mọi hàng có `cantSplit` để một hàng không vắt sang hai trang. Bảng dài hơn thì được tách, hàng tiêu đề lặp lại ở trang sau.
- Word không có khoảng cách sau bảng: đoạn kế tiếp dính sát đường viền dưới. `table()` thêm một đoạn đệm rỗng cao đúng 6 pt (bằng khoảng cách giữa các đoạn văn). Đây là ngoại lệ duy nhất của quy tắc không dùng dòng trống để giãn cách.
- Bảng dùng để dàn trang (khối Quốc hiệu, khối chữ ký): `_layout_table` đặt mọi viền `nil`; `check_docx` nhận ra và bỏ qua các quy tắc của bảng dữ liệu.

## Ảnh

- Khổ chữ A4 với lề 2 / 2 / 3 / 1,5 cm là 16,5 × 25,7 cm. Chừa khoảng 2,5 cm cho chú thích dưới hình. Bề rộng hình = min(16,5, (25,7 − 2,5) × tỉ lệ rộng/cao), không quá cỡ gốc ở 96 dpi (`picture` làm việc này).
- Cỡ chữ in ra của sơ đồ (chữ `fontSize` px trong công cụ vẽ, xuất ảnh với hệ số phóng `s`): `pt = fontSize × 0,75 × bề_rộng_in_inch × 96 / (bề_rộng_ảnh_px / s)`. Dưới 8 pt là khó đọc. Ví dụ: ERD rộng 3600 px (xuất với s = 2) đặt rộng 16,5 cm thì chữ 12 px chỉ còn khoảng 3 pt; vẽ lại thành 2 cột bảng, chỉ ghi tên cột, tách thành hai hình thì chữ lên khoảng 8 pt.
- Bề rộng sơ đồ (đơn vị draw.io) nên không quá khoảng 900 để chữ 12 px còn từ 8 pt khi đặt rộng 16,5 cm.
- Cách vẽ lại cho khổ dọc: bố cục từ trên xuống, ít cột; sơ đồ tuần tự dài thì tách theo pha; sơ đồ kiến trúc nằm ngang thì xếp các tầng chồng lên nhau.
- Tách hình thì số hình phía sau đổi: sửa mọi chỗ trong bài gọi "Hình 3.x" bằng số cứng.
- Khi phải có trang ngang (mẫu bắt buộc, hoặc bảng biểu trong văn bản hành chính): section ngang (đổi `w`/`h`, `orient="landscape"`), bỏ `pgNumType w:start` ở các section sau để số trang không về 1, và đầu trang, chân trang riêng cho trang ngang.

## Ký tự, ngoặc và thuộc tính tệp

- Không ký tự ẩn (U+200B/C/D, U+00AD, U+FEFF, U+2060) trong chữ của tài liệu. Khi viết mã Python có các ký tự này, viết dạng thoát `"\u200b"` để còn thấy được trong mã nguồn.
- Ngoặc kép, nháy đơn trong .docx là ngoặc cong (`smart_quotes`), trừ khối mã. Tài liệu tham khảo kiểu IEEE giữ nguyên tên bài như nguồn.
- `metadata(doc, author, title)`: tác giả, người sửa cuối, tiêu đề, xóa chú thích "generated by python-docx".

## Xuất PDF và kiểm tra

- Windows có Microsoft Word: cập nhật trường và xuất PDF qua COM (`Documents.Open`, `Fields.Update`, `TablesOfContents.Update`, `ExportAsFixedFormat(path, 17)`). Không điều khiển Word khi người dùng đang mở Word: giao tệp .docx và nói người dùng tự cập nhật trường, xuất PDF, không dừng lại chờ. Sau khi xuất, xem thời gian sửa của tệp PDF để chắc là đang xem bản mới.
- Không có Word: `soffice --headless --convert-to pdf file.docx` của LibreOffice. LibreOffice có thể ngắt dòng, ngắt trang khác Word một chút, nên chỗ nào sát giới hạn (ô bảng lẻ một chữ, ảnh cuối trang) vẫn phải xem lại trong Word nếu người nhận dùng Word.
- Dò ô lẻ một chữ trên bản PDF: `page.find_tables()` của PyMuPDF, tách chữ của ô theo dòng, báo ô có dòng cuối một chữ. Chữ có gạch dưới có thể bị tách thành dòng riêng khi trích, đó là báo nhầm.
- Xem tận mắt ít nhất một trang có danh sách, một trang bảng dài, một trang có hình lớn; với văn bản hành chính thì trang đầu (khối Quốc hiệu, số ký hiệu) và trang có chữ ký.
