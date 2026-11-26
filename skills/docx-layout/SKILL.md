---
name: docx-layout
description: Lay out Word (.docx) documents with python-docx using a profile per document type - thesis (đồ án, luận văn), report (báo cáo, đề xuất), guide (hướng dẫn, quy trình), admin (văn bản hành chính theo Nghị định 30/2020/NĐ-CP: công văn, quyết định, tờ trình, thông báo) - or the recipient's own template, which always wins. Times New Roman black text, auto-numbered heading styles, uncoloured tables, portrait pages, readable diagrams, real Word lists, clean file properties, plus a checker script. Trình bày tệp Word theo bộ định dạng của từng loại tài liệu hoặc theo mẫu của nơi nhận. Use when creating or editing a .docx report, thesis, guide or Vietnamese administrative document, when asked to "trình bày lại báo cáo", "định dạng Word", "làm công văn", or when the skill is named. Use together with humanize-writing for the prose.
---

# Trình bày tài liệu Word

Đường dẫn trong skill này tính từ thư mục chứa tệp SKILL.md này. Mã dựng sẵn: `scripts/word_style.py`. Máy quét: `scripts/check_docx.py`. Cần Python 3 và `python-docx` (`pip install python-docx`); `pymupdf` không bắt buộc, có thì đo chữ bằng font thật.

Chữ trong tài liệu viết theo skill humanize-writing. Nếu skill đó được cài cạnh skill này, `check_docx.py` tự chạy máy quét văn phong của nó trên chữ của tệp.

## Quy trình

1. Chọn cách trình bày, theo thứ tự:
   - Người dùng có mẫu của nơi nhận (mẫu của trường, khoa, công ty, cơ quan): dựng trên mẫu đó, `docx.Document("mau.docx")` rồi `ws.setup(doc, <bộ gần nhất>, template=True)`. Mẫu thắng ở mọi điểm nó quy định; nhóm F dưới đây chỉ áp dụng cho những điểm mẫu không nói.
   - Không có mẫu: chọn bộ định dạng theo loại tài liệu (bảng dưới). Không rõ loại tài liệu thì hỏi người dùng tài liệu gửi cho ai, có mẫu không.
   - Không có mẫu và không khớp bộ nào: dùng `report`, và nói với người dùng là đang dùng bộ mặc định.
2. Đọc `references/profiles.md` (thông số và nguồn của từng bộ) và `references/word-howto.md` (các bẫy của python-docx) trước khi dựng tệp.
3. Dựng tệp bằng `word_style.py` (cách gọi ở đầu tệp).
4. Kiểm tra: `python scripts/check_docx.py --profile <bộ> <file.docx>`.
5. Mở tệp bằng Word, cập nhật mục lục và các trường số (Update Field), xuất PDF và xem từng trang như người đọc sẽ xem (cách xuất ở cuối `references/word-howto.md`). Máy quét không thay được việc nhìn trang: ảnh mờ, bảng xấu, trang trống chỉ thấy khi xem.

| Bộ | Dùng cho | Điểm chính |
|---|---|---|
| `thesis` | Đồ án, khóa luận, luận văn khi trường không phát mẫu | Tiêu đề "CHƯƠNG 1: ..." / 1.1 / 1.1.1 đánh số tự động, cỡ 13, giãn dòng 1,5 |
| `report` | Báo cáo công việc, đề xuất, kế hoạch trong công ty | Tiêu đề 1. / 1.1. / 1.1.1., đoạn thụt đầu dòng 1,27 cm |
| `guide` | Tài liệu hướng dẫn, quy trình | Như `report`; các bước dùng `ws.steps`, lệnh dùng `ws.code` |
| `admin` | Văn bản hành chính theo NĐ 30/2020/NĐ-CP | Thể thức Quốc hiệu, số ký hiệu, nơi nhận, chữ ký (`admin_header`, `admin_signature`), cỡ 14, số trang ở lề trên |

`admin` chỉ dựng thể thức văn bản hành chính theo Phụ lục I của Nghị định. Loại văn bản khác (ví dụ văn bản quy phạm pháp luật, văn bản của tổ chức Đảng) thì hỏi người dùng mẫu hoặc quy định họ phải theo.

## F. Quy tắc trình bày

F1. Chữ: Times New Roman, màu đen (000000) ở mọi nơi, kể cả tiêu đề (style Heading của Word mặc định màu xanh: phải đổi), chú thích, mục lục, đầu trang. NĐ 30 cũng quy định phông Times New Roman, màu đen cho văn bản hành chính. Cỡ chữ theo bộ định dạng hoặc mẫu. Mã nguồn được dùng font đơn cách (Consolas, Courier New).

F2. Đoạn văn nội dung căn đều hai bên (Justify), giãn dòng và cách đoạn theo bộ định dạng. Không căn đều: tiêu đề, chú thích hình và bảng, ô bảng, đoạn chứa ảnh, trang bìa, mục lục, các dòng thể thức của văn bản hành chính.

F3. Tiêu đề dùng style Heading có tên. Với `thesis`, `report`, `guide`: số chương, mục do Word đánh (danh sách đa cấp gắn vào Heading 1–3), không gõ tay. Phần không đánh số (MỞ ĐẦU, KẾT LUẬN, TÀI LIỆU THAM KHẢO, PHỤ LỤC) dùng style "Heading 1 Không số" để vẫn vào mục lục. Với `admin`: chữ "Chương I", "Mục 1", "Điều 1." gõ tay đúng như NĐ 30 quy định, style Heading chỉ để định dạng và vào mục lục. Chú thích dùng style Caption ("Hình 1.1. ...", "Bảng 1.1. ..."). Mọi tiêu đề có "keep with next".

F4. Bảng không màu: viền đen mảnh (style Table Grid), không tô nền ô nào. Hàng tiêu đề in đậm, căn giữa cả ngang lẫn dọc, lặp lại khi bảng sang trang. Nội dung ô căn trái (số căn phải hoặc giữa), không in đậm. Bảng không viền chỉ dùng để dàn trang (khối Quốc hiệu, khối chữ ký).

F5. Không tô màu nền cho khung, ô lưu ý, đoạn trích. Ngoại lệ là khối mã nguồn hoặc lệnh: nền xám nhạt (F2F2F2), font đơn cách. Ô lưu ý thì dùng viền mảnh hoặc chỉ cần chữ "Lưu ý:" ở đầu đoạn.

F6. Mặc định mọi trang dọc và chữ trong ảnh đọc được khi in. Trang ngang bắt người đọc xoay giấy hoặc xoay màn hình; sơ đồ rộng thì vẽ lại cho khổ dọc. Ngoại lệ: mẫu của nơi nhận cho phép, hoặc văn bản hành chính có bảng biểu (NĐ 30 cho phép trình bày theo chiều rộng).
- Ảnh rộng tối đa bằng khổ chữ; nếu như vậy ảnh cao quá phần trang còn lại thì thu theo chiều cao để ảnh và chú thích nằm gọn trong một trang.
- Chữ trong sơ đồ in ra từ 8 pt trở lên (`ws.picture(..., text_px=12, dpi_scale=2)` cảnh báo khi nhỏ hơn). Sơ đồ quá rộng (ERD, sơ đồ lớp, sơ đồ tuần tự dài) thì xếp các khối theo chiều dọc, bớt chi tiết không cần cho ý của hình, hoặc tách thành nhiều hình nhỏ.
- Ảnh chụp màn hình chỉ chụp vùng cần nói tới. Không phóng ảnh quá cỡ gốc đến mức mờ, không bóp méo tỉ lệ.

F7. Bảng không xuống dòng kỳ cục: đặt độ rộng từng cột theo nội dung, tổng bằng khổ chữ. Không để dòng cuối của ô chỉ còn một chữ, không để chữ trong tiêu đề cột bị bẻ giữa từ; gặp thì nới cột, thu cột khác hoặc viết gọn nội dung ô. Bảng quá rộng thì bớt cột hoặc tách bảng.

F8. Chỉ in đậm tiêu đề, hàng tiêu đề bảng, nhãn trang bìa và các thành phần thể thức mà NĐ 30 quy định in đậm. Không in đậm từ ngữ trong đoạn văn, ô bảng, danh sách để nhấn mạnh.

F9. Danh sách dùng định dạng danh sách của Word (`ws.bullets`, `ws.steps`), không gõ tay "•", "-" hay "1." ở đầu dòng. Ký hiệu đầu dòng là gạch ngắn "-" hoặc chấm tròn "•", không dùng gạch dài "–" hay "—" (rộng gấp rưỡi trở lên, trông như gạch ngang). Ngoại lệ: nơi nhận và "Kính gửi" của văn bản hành chính gõ "- " đúng như mẫu của NĐ 30. Không dùng dòng trống để giãn cách: dùng khoảng cách đoạn.

F10. Kiểm tra trước khi giao: chạy `check_docx.py`, cập nhật trường trong Word, xuất PDF xem từng trang: chữ đen hết chưa, bảng có ô nào lẻ một chữ không, ảnh có đọc được chữ không, có trang trống không. Thiếu chỗ vì quá số trang thì cắt chữ, không thu nhỏ font hay lề.

F11. Thuộc tính tệp (File > Info) không để lộ công cụ: python-docx mặc định ghi tác giả "python-docx". Đặt tác giả là người viết, tiêu đề là tên tài liệu (`ws.metadata`). Hỏi người dùng tên tác giả, không tự đặt.

## Không bịa thông tin trong thể thức

Số, ký hiệu văn bản, tên cơ quan, chức vụ, họ tên người ký, nơi nhận, ngày tháng là thông tin của người dùng. Thiếu thì hỏi, không điền tên hay số giả. Chỗ người dùng muốn để trống thì để dấu chấm như mẫu của Nghị định ("Số:     /QĐ-..."), không để "[Điền tên]".
