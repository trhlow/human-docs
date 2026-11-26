# human-docs

human-docs là bộ skill cho AI agent viết tài liệu tiếng Việt: viết văn như người viết, không mang giọng chatbot, và trình bày tệp Word đúng thể thức, từ đồ án, báo cáo đến công văn theo Nghị định 30/2020/NĐ-CP.

## Cách hoạt động

Bạn nhờ agent viết một đoạn giới thiệu, sửa một chương đồ án hay soạn một công văn. Agent thấy việc này khớp mô tả của skill nên tự gọi skill, bạn không cần gõ lệnh gì.

Với phần chữ, agent không chỉ đổi những từ "nghe giống AI". Nó đọc từng đoạn và hỏi: đoạn này có nói điều gì mà chỉ tài liệu này mới nói được không, có tên, số, ngày, việc cụ thể không? Câu thay tên dự án khác vào mà vẫn đúng là câu rỗng, nên phải viết lại. Sau đó máy quét `check.py` bắt phần máy bắt được: từ vựng kiểu chatbot, cấu trúc "không chỉ... mà còn", dấu gạch dài, câu dài đều nhau như đúc. Số liệu và nguồn không có thì agent báo là thiếu, không tự điền.

Với tệp Word, agent hỏi trước bạn có mẫu của nơi nhận không, ví dụ mẫu của khoa, của công ty. Có mẫu thì dựng trên mẫu đó. Không có thì chọn bộ định dạng theo loại tài liệu: đồ án, báo cáo, hướng dẫn hay văn bản hành chính. Agent dựng tệp bằng python-docx, chạy `check_docx.py` để tìm chữ màu, tiêu đề gõ số tay, ô bảng xuống dòng còn một chữ, lề sai quy định, rồi xuất PDF xem từng trang. Có những lỗi chỉ thấy được khi nhìn trang, như ảnh mờ hay trang trống.

Cần một tài liệu mới hoàn toàn mà bạn chưa có mẫu, chưa có nội dung? Agent hỏi bạn vài câu, rồi xin phép đọc thư mục dự án đang mở: README, tài liệu, cấu hình, lịch sử git, tệp số liệu, không đụng tới `.env`, khóa hay mật khẩu. Muốn chạy lệnh để lấy số đo như chạy test, nó liệt kê từng lệnh và xin phép thêm lần nữa. Trước khi viết, bạn nhận một bảng thông tin ghi rõ mỗi con số lấy từ tệp nào, lệnh nào, cùng dàn ý; bạn đồng ý thì nó mới dựng tệp.

Với công văn, quyết định, tờ trình, skill dựng đủ phần thể thức: Quốc hiệu, tên cơ quan, số ký hiệu, ngày tháng, "Kính gửi", chữ ký, nơi nhận. Vị trí và cỡ chữ của từng phần trích từ Phụ lục I của Nghị định. Tên cơ quan, số văn bản, người ký là thông tin của bạn: agent hỏi, hoặc để dấu chấm như mẫu của Nghị định, không đặt tên giả.

## Cài đặt

Mỗi công cụ cài riêng. Dùng nhiều công cụ thì cài cho từng cái.

### Claude Code

- Thêm marketplace của repo này:

  ```bash
  /plugin marketplace add trhlow/human-docs
  ```

- Cài plugin (gửi riêng, sau lệnh trên):

  ```bash
  /plugin install human-docs@human-docs
  ```

Từ terminal thì dùng `claude plugin marketplace add trhlow/human-docs` và `claude plugin install human-docs@human-docs`. Hai skill có tên `/human-docs:humanize-writing` và `/human-docs:docx-layout`; Claude cũng tự gọi khi việc đang làm khớp mô tả.

### Codex

Cài bằng CLI [skills](https://github.com/vercel-labs/skills) (cần Node.js 22.20 trở lên). Skill vào `~/.agents/skills`, thư mục Codex đọc:

```bash
npx skills add trhlow/human-docs -g -a codex
```

### Cursor, Gemini CLI, GitHub Copilot, OpenCode, Antigravity

- Cài cho mọi dự án, chọn agent khi được hỏi:

  ```bash
  npx skills add trhlow/human-docs -g
  ```

- Hoặc chỉ định agent: `-a cursor`, `-a gemini-cli`, `-a github-copilot`, `-a opencode`, `-a antigravity`. Bỏ `-g` để chỉ cài vào dự án hiện tại. Chỉ cần một skill thì thêm `--skill docx-layout` hoặc `--skill humanize-writing`.

### Chép tay

Chép hai thư mục trong `skills/` vào thư mục skill của agent, ví dụ `~/.claude/skills/` cho Claude Code, `~/.agents/skills/` cho Codex. Giữ hai thư mục nằm cạnh nhau để `check_docx.py` tìm được `check.py` và quét luôn văn phong.

### claude.ai

Tải `humanize-writing.zip` và `docx-layout.zip` ở trang [Releases](https://github.com/trhlow/human-docs/releases/latest) rồi đưa lên phần Skills của claude.ai. Script chỉ chạy được khi bật chức năng chạy mã.

### Yêu cầu

- Python 3 và `python-docx` (`pip install python-docx`) để dựng và kiểm tệp Word.
- `pymupdf` (`pip install pymupdf`), không bắt buộc: có thì máy quét đo bề rộng chữ bằng font Times New Roman thật, đoán đúng chỗ Word ngắt dòng trong ô bảng.
- Microsoft Word (Windows) hoặc LibreOffice để xuất PDF và xem trang.

## Khi kết quả chưa đúng

- Máy quét văn phong báo dấu hiệu, chưa phải lỗi chắc chắn. Văn trang trọng hay dùng từ nối không tự động là văn AI; nhiều dấu hiệu dồn trong một đoạn mới đáng sửa.
- Tệp Word khác yêu cầu của trường hay cơ quan: đưa tệp mẫu cho agent. Mẫu luôn thắng bộ định dạng dựng sẵn.
- Ô bảng vẫn còn một chữ ở dòng cuối sau khi tự chia cột: sửa câu chữ của ô cho ngắn hoặc dài ra.
- Lỗi của skill hoặc script: mở issue tại https://github.com/trhlow/human-docs/issues, kèm tệp .docx (đã bỏ thông tin riêng) và lệnh đã chạy.

## Bên trong có gì

### Skill

Viết:
- `humanize-writing`: quy tắc nhóm A–E (nội dung, từ ngữ, dấu câu, lời chatbot lọt vào, trích dẫn), tiếng Việt và tiếng Anh, kèm `scripts/check.py`.

Trình bày Word:
- `docx-layout`: quy tắc nhóm F (chữ, đoạn, tiêu đề, bảng, ảnh, danh sách, thuộc tính tệp), bốn bộ định dạng, kèm `scripts/word_style.py` và `scripts/check_docx.py`.

### Bộ định dạng

| Bộ | Dùng cho | Điểm chính |
|---|---|---|
| `thesis` | Đồ án, khóa luận, luận văn khi trường không phát mẫu | "CHƯƠNG 1: ..." / 1.1 / 1.1.1 do Word đánh số, cỡ 13, giãn dòng 1,5 |
| `report` | Báo cáo, đề xuất, kế hoạch trong công ty | 1. / 1.1. / 1.1.1., đoạn thụt đầu dòng 1,27 cm |
| `guide` | Tài liệu hướng dẫn, quy trình | Như `report`, các bước đánh số bằng `steps` |
| `admin` | Văn bản hành chính theo Nghị định 30/2020/NĐ-CP | Đủ thể thức, cỡ 14, số trang ở lề trên, không hiện ở trang đầu |

Thông số và nguồn của từng bộ ở [skills/docx-layout/references/profiles.md](skills/docx-layout/references/profiles.md). Thông số của `admin` trích nguyên văn từ Phụ lục I của Nghị định, ghi số mục. Ba bộ còn lại là mặc định của skill, nằm trong khoảng Nghị định cho phép, và được ghi rõ là mặc định.

## Nguyên tắc

- Không bịa: số liệu, nguồn, tên, số văn bản không có thì hỏi hoặc để trống, không điền cho đủ.
- Mẫu của nơi nhận thắng: bộ định dạng dựng sẵn chỉ lấp chỗ mẫu không nói.
- Có nguồn cho từng thông số: thông số nào lấy từ quy định thì ghi quy định và số mục; thông số nào skill tự chọn thì ghi là tự chọn.
- Nhìn trang trước khi giao: máy quét không thay được việc xem bản PDF.
- Sửa nội dung, không chỉ sửa bề mặt: đổi từ đồng nghĩa cho câu rỗng thì câu vẫn rỗng.

## Đóng góp

Thấy lỗi thì mở issue. Muốn thêm loại tài liệu hay sửa thông số thì dùng mẫu "Đề xuất quy tắc", kèm văn bản gốc của quy định. Trước khi sửa code, đọc [AGENTS.md](AGENTS.md): quy tắc nguồn cho thông số và các lệnh kiểm tra nằm ở đó. Người tham gia làm theo [bộ quy tắc ứng xử](CODE_OF_CONDUCT.md).

## Cập nhật

- Claude Code: `claude plugin marketplace update human-docs`, rồi `claude plugin update human-docs@human-docs` và khởi động lại Claude Code.
- Cài bằng `npx skills`: `npx skills update`.

## Giấy phép

MIT. Xem [LICENSE](LICENSE).

## English

human-docs gives coding agents two skills for Vietnamese (and English) documents. `humanize-writing` keeps prose free of AI tells: concrete content over inflated claims, no chatbot phrasing, natural rhythm, no invented sources, plus a pattern scanner. `docx-layout` lays out Word files with python-docx by document type: `thesis`, `report`, `guide`, and `admin` for Vietnamese administrative documents per Decree 30/2020/ND-CP. A recipient's template always wins. It also ships a checker.

Install in Claude Code with `/plugin marketplace add trhlow/human-docs`, then `/plugin install human-docs@human-docs`. In Codex, Cursor, Gemini CLI, GitHub Copilot and other agents, run `npx skills add trhlow/human-docs -g` (add `-a <agent>` to target one). It requires Python 3 and `python-docx`; `pymupdf` is optional. The skill text is in Vietnamese, but the trigger descriptions are bilingual, so English requests work too.
