---
name: humanize-writing
description: Rules for writing Vietnamese or English prose that reads as written by a person, not by an AI model - concrete content instead of inflated claims, no AI vocabulary or chatbot phrases, natural sentence rhythm, no invented sources - with a scanner script that flags the patterns. Quy tắc viết văn tiếng Việt hoặc tiếng Anh không mang dấu hiệu văn AI (dựa trên trang Wikipedia "Signs of AI writing" và các nghiên cứu năm 2026, kể cả tiếng Việt), kèm máy quét. Use when writing or editing prose for real readers (report, thesis, email, post, guide, PR description), when asked to "humanize", "make it sound natural", "viết lại cho tự nhiên", "bớt giọng AI", or when the skill is named. For Word (.docx) layout use the docx-layout skill together with this one. Not for code.
---

# Viết như người

Mục tiêu là văn bản rõ và cụ thể. Né từ cấm mà vẫn nói chung chung thì chưa đạt: trang Wikipedia cảnh báo rằng chỉ sửa dấu hiệu bề mặt thì vấn đề thật (nội dung rỗng, thổi phồng, nguồn bịa) vẫn còn.

Đường dẫn trong skill này tính từ thư mục chứa tệp SKILL.md này.

## Quy trình

1. Viết hoặc nhận văn bản.
2. Với văn bản dài hoặc file, chạy máy quét:
   `python scripts/check.py <file...>` (không có file thì đọc stdin; mỗi dòng là một đoạn).
   Máy quét bắt từ, dấu câu và nhịp câu (đoạn có câu dài đều nhau, nhiều câu liền nhau mở cùng một từ). Nó không bắt được lỗi nội dung.
3. Đọc lại theo nhóm A (nội dung) bên dưới, vì đây là phần máy không bắt được. Với mỗi đoạn, hỏi: đoạn này có nói điều gì
   chỉ tài liệu này mới nói được không (tên, số, ngày, việc cụ thể)? Câu thay tên dự án khác vào vẫn đúng là câu rỗng (A9).
4. Sửa. Giữ nguyên nghĩa và số liệu, không thêm thông tin không có trong bản gốc. Câu đã ổn thì để nguyên.
5. Nếu kết quả là tệp Word (.docx): dùng thêm skill docx-layout. Máy quét của skill đó chạy luôn `check.py` trên chữ của tệp.

## A. Nội dung

A1. Không thổi phồng ý nghĩa. Nói sự việc, bỏ lời đánh giá tầm quan trọng.
Cấm: "đóng vai trò quan trọng/then chốt/cốt lõi", "là minh chứng cho", "đánh dấu bước ngoặt", "mở ra kỷ nguyên", "để lại dấu ấn", "phản ánh xu hướng", "góp phần vào", "tạo tiền đề cho", "khẳng định vị thế", "ngày càng phát triển", "trong bối cảnh ... ngày nay".
EN: stands/serves as, is a testament/reminder, a crucial/pivotal/vital/significant/key role/moment, underscores/highlights its importance, reflects broader, symbolizing its enduring/lasting, contributing to the, setting the stage for, marking/shaping the, represents/marks a shift, key turning point, evolving landscape, focal point, indelible mark, deeply rooted, shaped conversations/debate about.

A2. Không gắn đuôi phân tích hời hợt vào cuối câu.
Cấm: "..., qua đó cho thấy", "..., từ đó góp phần", "..., nhằm nâng cao", "..., giúp tăng cường", "..., thể hiện sự", "..., mang lại giá trị".
EN: câu kết bằng cụm -ing (highlighting, underscoring, emphasizing, ensuring, reflecting, symbolizing, fostering, enhancing, contributing to), valuable insights, align/resonate with.
Nếu hệ quả có thật thì viết một câu riêng có số liệu hoặc ví dụ.

A3. Không quy chiếu mơ hồ. "Các chuyên gia cho rằng", "nhiều nghiên cứu chỉ ra", "được đánh giá cao", "giới quan sát", "một số ý kiến" (EN: experts argue, observers have cited, industry reports, several sources). Nêu tên nguồn hoặc bỏ câu. Không gọi một nguồn là "nhiều nguồn".

A4. Không nói mơ hồ về liên hệ. "Gắn liền với", "liên quan đến", "có mối liên hệ với" (EN: in connection with, associated with) khi lẽ ra phải nói rõ vai trò: ai làm gì.

A5. Không khoe độ phủ nguồn hay sự hiện diện. "Được nhiều báo chí đưa tin", "được liệt kê trong cơ sở dữ liệu", "có sự hiện diện mạnh mẽ trên mạng xã hội" (EN: independent coverage, featured/profiled in, maintains an active digital presence).

A6. Không kết theo khuôn "thách thức và triển vọng". Cấm "Mặc dù còn một số thách thức..., với ... hứa hẹn", "Bất chấp những khó khăn" (EN: Despite its... faces several challenges, Future Outlook). Hạn chế thì nêu cụ thể: cái gì chưa làm, vì sao, cần làm gì.

A7. Không tóm tắt lặp lại. Cấm mở đoạn bằng "Tóm lại", "Nhìn chung", "Có thể nói", "Như vậy có thể thấy" để nhắc lại điều vừa viết (EN: In summary, In conclusion, Overall). Không thêm mục "Kết luận" cho một phần ngắn.

A8. Không giọng quảng cáo. Cấm: "nổi bật", "vượt trội", "hàng đầu", "đột phá", "toàn diện", "liền mạch", "mạnh mẽ", "tối ưu" (khi không đo), "đa dạng", "phong phú", "sôi động", "tuyệt vời", "nằm giữa lòng", "cam kết mang đến".
EN: boasts, vibrant, rich, profound, showcasing, exemplifies, commitment to, nestled, in the heart of, groundbreaking, renowned, diverse array, seamless, robust.
Không tự thêm mục "Giải thưởng và ghi nhận" khi không được yêu cầu.

A9. Không viết câu ai cũng viết được. "Hệ thống giúp nâng cao hiệu quả quản lý", "giao diện thân thiện, dễ sử dụng", "đáp ứng nhu cầu thực tế" đúng với mọi đồ án nên không nói gì. Thay bằng việc cụ thể và số đo: "giám thị tạm dừng 30 thí sinh bằng một lần bấm", "200 thí sinh nộp bài không lỗi". Câu chỉ giải thích điều hiển nhiên ("lưu bài tự động rất quan trọng vì giúp không mất bài") thì cắt; bản nháp do máy viết thường cắt được một phần năm đến một phần ba mà không mất ý.

## B. Từ ngữ và ngữ pháp

B1. Tránh từ vựng AI. Một từ lẻ chưa phải lỗi, cụm nhiều từ dày đặc mới là dấu hiệu mạnh. Chỉ dùng khi đúng nghĩa đen.
VN: "Bên cạnh đó"/"Ngoài ra"/"Đặc biệt" mở câu liên tiếp, "đáng chú ý", "nhấn mạnh", "làm nổi bật", "bức tranh", "hành trình", "hành trang", "không ngừng", "chiều sâu", "đa chiều", "thúc đẩy", "tận dụng", "nâng tầm", "trao quyền", "khai phá", "tầm nhìn".
EN: additionally (mở câu), align with, boasts, bolstered, crucial, deep dive, delve, emphasizing, enduring, enhance, fostering, garner, highlight (động từ), interplay, intricate, landscape (nghĩa trừu tượng), meticulous, pivotal, robust, showcase, tapestry, testament, underscore, valuable, vibrant; lớp từ mới (từ giữa 2026): leverage, multifaceted, prioritize, quietly, steady, dependable, echoed, universally, matters, foster; động từ thổi phồng: unlock, unleash, elevate, empower, supercharge, revolutionize, streamline; danh từ to tát: realm, paradigm, synergy, ecosystem (nghĩa bóng).
Mở câu bằng "Hơn nữa", "Thêm vào đó", "Mặt khác", "Moreover", "Furthermore" liên tiếp trong một đoạn cũng là dấu hiệu.

B2. Dùng "là" và "có". Không thay bằng "đóng vai trò là", "được xem như", "đóng vai trò như", "sở hữu", "tự hào có", "mang đến" (EN: serves as, stands as, functions as, represents, boasts, features, offers, refers to). "Ông ấy là ứng viên" thay cho "ông ấy dấn thân vào chính trường với tư cách ứng viên".

B3. Không song song phủ định. Cấm "không chỉ... mà còn", "không phải X mà là Y", "không ..., không ..., chỉ có ...", "Y thay vì X" dùng để nhấn mạnh (EN: not only... but also, it's not X it's Y, Y rather than X). Chỉ được dùng "X chứ không Y" khi người đọc thật sự có thể hiểu nhầm thành Y.

B4. Không ép bộ ba. Liệt kê đúng số ý có thật. Không chuỗi ba tính từ hay ba cụm ngắn cho tròn câu.

B5. Không đổi từ đồng nghĩa liên tục để gọi cùng một đối tượng. Đã gọi là "hệ thống" thì giữ "hệ thống", đừng luân phiên "nền tảng", "giải pháp", "ứng dụng".

B6. Nhịp câu tự nhiên. Trộn câu dài và ngắn theo ý; đoạn dài ngắn khác nhau theo lượng ý, không đoạn nào cũng 3–4 câu. Văn máy đời mới cắt mọi câu về 8 đến 20 từ và chỉ dùng dấu phẩy, dấu chấm; văn máy đời trước thì câu dài đều, nối bằng "và". Cả hai đều là câu dài bằng nhau: máy quét báo đoạn từ 5 câu có độ lệch độ dài dưới 25 % độ dài trung bình. Không mở ba câu liền nhau bằng cùng một từ, không kết mỗi đoạn bằng một câu đúc kết, không câu khẩu hiệu cụt lủn.

B7. Ưu tiên từ thường: "viết" hơn "chấp bút", "dùng" hơn "tận dụng", "thử" hơn "nỗ lực", "chuyển" hơn "di dời", "mất" hơn "qua đời" (trừ khi văn cảnh cần trang trọng). Được nói khẳng định cụ thể ("là hệ thống duy nhất", "lần đầu tiên") khi đúng, và được dùng "khá", "có lẽ", "thường" khi thật sự không chắc.

B8. Không câu khởi động, câu tự khen, câu hỏi tự trả lời. "Vấn đề là...", "Điều đáng nói là...", "Hãy cùng tìm hiểu...", "Và đó chính là điều quan trọng.", "Kết quả? ...", "Dù bạn là X hay Y...", "Nhanh. Gọn. Rẻ." (mảnh câu ghép cho kịch tính), "bớt X, thêm Y" (EN: Here's the thing, Let me be clear, Let's dive in, And that matters, The result? ..., Whether you're..., less X more Y, It's the Excel of...). Bắt đầu ngay ở câu có thông tin; câu có ý thì để ý tự nói.

B9. Tiếng Việt: không Hán Việt hóa và Tây hóa câu. "Một cách hiệu quả/toàn diện/nhanh chóng" thường bỏ được hoặc thay bằng con số; "tối ưu hóa" (khi không đo) thành "làm nhanh hơn", "giảm"; "mang lại nhiều giá trị tinh thần", "bài học quý báu" thì nói ra cụ thể. Câu nhiều mệnh đề phụ nối bằng "đồng thời", "trong khi đó", "bên cạnh đó" thì tách ra. Xưng hô theo người đọc: thư gửi khách hàng là "Quý khách", "Anh/Chị", không "bạn"; viết hoa đúng tên riêng tiếng Việt ("Tết Nguyên đán").

B10. Không khoảng ước lượng giả. "Mất 5–10 phút", "tăng 20–30 %" khi đã có số đo thật thì ghi số đo ("mất 7 phút ở lần chạy ngày 22/10"). Khoảng chỉ dùng khi đúng là có biên (thời lượng theo quy định, kết quả của nhiều lần đo).

## C. Dấu câu và trình bày

C1. Không dùng dấu gạch ngang dài (—) để chèn hay nối ý. Thay bằng dấu phẩy, ngoặc đơn, dấu hai chấm, chấm phẩy hoặc tách câu. Gạch nối ngắn (–) trong khoảng số ("tr. 3–4") và cặp thuật ngữ ("đối tượng – quan hệ") vẫn dùng bình thường.
Lưu ý: từ khoảng tháng 9/2026 các mô hình mới bị chặn hẳn dấu gạch dài, nên dấu hiệu mới là ngược lại: chỉ toàn dấu phẩy và dấu chấm, đều tăm tắp. Văn người viết dùng cả chấm phẩy, ngoặc đơn, dấu hai chấm khi đúng chức năng (The Economist, 2026: văn chatbot ít dấu chấm phẩy và ngoặc đơn hơn văn người).

C2. Ngoặc kép theo quy ước sẵn có của tài liệu. Trong Markdown, code, wiki thì dùng ngoặc thẳng (" '). Trong tài liệu Word thì dùng ngoặc cong “ ” và ’, vì Word tự đổi khi người gõ; ngoặc thẳng trong .docx cho thấy chữ được dán từ nơi khác (hàm `smart_quotes` của skill docx-layout). Không trộn hai kiểu trong một văn bản.

C3. Tiêu đề viết hoa kiểu câu: "Thiết kế cơ sở dữ liệu", không "Thiết Kế Cơ Sở Dữ Liệu" (EN: sentence case, không Title Case).

C4. Không in đậm rải rác trong văn xuôi.

C5. Trong văn xuôi không dùng danh sách gạch đầu dòng có nhãn in đậm kiểu "**Hiệu năng:** ...". Viết thành đoạn, hoặc dùng bảng khi dữ liệu thật sự có dạng bảng. Danh sách chỉ dùng cho các mục thật sự song song (các bước, các mục tiêu đã đánh số trong đề cương): không đặt danh sách sau mọi tiêu đề, không phải lúc nào cũng 3–5 mục dài bằng nhau, và không thay đoạn văn bằng chuỗi danh sách nối nhau.

C6. Không emoji ở đầu tiêu đề hay mục danh sách.

C7. Đúng định dạng của nơi nhận: không Markdown (`**`, `#`, `---`, ``` ``` ```) trong văn bản dán vào Word, email thường hay wiki. Không dùng nhiều tiêu đề cấp 1.

C8. Không ký tự ẩn: dấu cách độ rộng 0 (U+200B, U+200C, U+200D), dấu gạch mềm (U+00AD), BOM (U+FEFF) trong chữ. Máy kiểm tra văn AI coi chúng là dấu hiệu văn máy. Muốn đường dẫn dài xuống dòng ở "/" thì chèn ngắt dòng thật tại chỗ cần, không rải ký tự ẩn. Dấu cách không ngắt (U+00A0, Ctrl+Shift+Space trong Word) thì được dùng, ví dụ trong "[12, tr. 13]".

## D. Lời chatbot lọt vào văn bản

D1. Không câu giao tiếp với người dùng: "Chắc chắn rồi!", "Dưới đây là...", "Hy vọng điều này hữu ích", "Bạn có muốn...", "Hãy cho tôi biết", "Bạn hoàn toàn đúng!", "Trước khi đăng, hãy kiểm tra..." (EN: Certainly!, Of course!, I hope this helps, Would you like, let me know, is there anything else, You're absolutely right).

D2. Không rào đón về nguồn: "thông tin cụ thể còn hạn chế", "chưa được công bố rộng rãi", "dựa trên thông tin hiện có", "cần lưu ý rằng", "điều quan trọng là", "... nên được hiểu là ... thay vì ...", "tự nó không chứng minh ...", "không nên nhầm lẫn với" (EN: while specific details are limited, not widely documented, based on available information, it's important to note, does not by itself establish). Từ giữa 2026 chatbot hay thêm "khung sửa sai": "X nên được hiểu là truyền thống thay vì sự thật", "điều này không đủ để khẳng định...", "nên phân biệt với..." (EN: should be treated as... rather than..., should not be confused with). Không có nguồn thì không viết câu đó; có nguồn thì nói điều nguồn nói.

D3. Không để lại chỗ trống mẫu: "[Điền tên]", "(nếu có)", "2026-XX-XX", "INSERT_SOURCE_URL", "example.com/source1".

D4. Không nhắc mốc dữ liệu huấn luyện, không "với tư cách là một mô hình AI", không câu bị cắt ngang ở cuối.

D5. Khi tóm tắt việc mình đã sửa (commit, ghi chú thay đổi), nói cụ thể đã sửa gì. Không viết "tinh chỉnh để đảm bảo rõ ràng, mạch lạc, tuân thủ chuẩn" (EN: refined, enhanced, streamlined, ensured clarity and flow, while preserving).

## E. Trích dẫn

E1. Chỉ trích nguồn có thật và đã kiểm. Sách có số trang. DOI, ISBN phải đúng. Bỏ `utm_source=` khỏi URL. Không gán cho nguồn một nhận định mà nguồn không nói.

E2. Không bịa bất cứ thông tin nào. Mỗi số liệu, ngày tháng, tên, định nghĩa, quy định hay nhận định không phải hiểu biết phổ thông phải có nguồn được trích ngay tại câu đó (theo kiểu trích dẫn của tài liệu, ví dụ IEEE "[3, tr. 15]"). Kết quả của chính người viết (số đo, kiểm thử, ảnh chụp) thì nói rõ đo khi nào, ở đâu, bằng cách nào. Không tìm được nguồn thì không viết câu đó và báo người dùng là thiếu nguồn; không "làm tròn" bằng một nguồn gần giống, không suy ra số liệu nguồn không có.

## Không được làm quá tay

- Đây là dấu hiệu, không phải bằng chứng. Văn bản đúng ngữ pháp, trang trọng hay dùng từ nối không tự động là văn AI.
- Không thay máy móc mọi từ trong danh sách bằng từ đồng nghĩa: làm vậy chỉ giấu dấu hiệu chứ không sửa được câu rỗng.
- Thuật ngữ chuyên ngành ("vai trò" trong phân quyền, "tối ưu" khi có số đo) giữ nguyên nếu đúng nghĩa.
- Không cố "lừa" máy dò AI bằng lỗi chính tả, tiếng lóng, từ viết tắt kiểu "kô", "cx": tài liệu trang trọng cần đúng chính tả. Máy dò báo nhầm khá nhiều (một nghiên cứu năm 2023 thấy chúng báo nhầm 61 % bài luận tiếng Anh của người không bản ngữ), người đọc đoán văn AI cũng không hơn đoán mò bao nhiêu; thứ người chấm nhận ra là nội dung rỗng và khuôn sáo, nên sửa thứ đó.
- Một dấu hiệu lẻ không chứng minh gì; nhiều dấu hiệu dồn trong một đoạn mới đáng sửa.

## Nguồn (đọc ngày 26/11/2026)

Wikipedia "Signs of AI writing" (bản tháng 10/2026, oldid 1387897756); hrih.si "Signs of AI writing, and how to fix each one" (tổng hợp số liệu của Pew, Reinhart và cộng sự, Kobak và cộng sự, Liang và cộng sự); chín dấu hiệu của Ruben Hassid (13/8/2026, qua ghi chú của Nicolas Deville); findskill.ai "10 dấu hiệu mùi AI" tiếng Việt; The Economist 2026 (qua tóm tắt của hrih.si).
