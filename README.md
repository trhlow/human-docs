# human-docs

Hai skill cho AI agent (Claude Code, Codex, Cursor, Gemini CLI, GitHub Copilot và các công cụ đọc chuẩn Agent Skills):

- **humanize-writing**: quy tắc viết văn tiếng Việt và tiếng Anh không mang dấu hiệu văn AI (nội dung cụ thể thay cho lời thổi phồng, không từ vựng và câu kiểu chatbot, nhịp câu tự nhiên, không bịa nguồn), kèm máy quét `check.py`.
- **docx-layout**: trình bày tệp Word bằng python-docx theo bộ định dạng của từng loại tài liệu, hoặc theo mẫu của nơi nhận (mẫu luôn thắng), kèm máy quét `check_docx.py`.

| Bộ định dạng | Dùng cho |
|---|---|
| `thesis` | Đồ án, khóa luận, luận văn khi trường không phát mẫu |
| `report` | Báo cáo, đề xuất, kế hoạch trong công ty |
| `guide` | Tài liệu hướng dẫn, quy trình |
| `admin` | Văn bản hành chính theo Nghị định 30/2020/NĐ-CP (công văn, quyết định, tờ trình, thông báo...) |

Thông số và nguồn của từng bộ: [skills/docx-layout/references/profiles.md](skills/docx-layout/references/profiles.md). Thông số của bộ `admin` trích nguyên văn từ Phụ lục I của Nghị định; ba bộ còn lại là mặc định của skill, nằm trong khoảng Nghị định cho phép.

## Cài đặt

### Claude Code

Trong Claude Code, gõ hai lệnh (gửi riêng từng lệnh):

```
/plugin marketplace add trhlow/human-docs
/plugin install human-docs@human-docs
```

Hoặc từ terminal:

```bash
claude plugin marketplace add trhlow/human-docs
claude plugin install human-docs@human-docs
```

Skill của plugin có tên `/human-docs:humanize-writing` và `/human-docs:docx-layout`; Claude cũng tự gọi khi việc đang làm khớp mô tả.

### Codex, Cursor, Gemini CLI, GitHub Copilot, OpenCode và các agent khác

Dùng CLI [skills](https://github.com/vercel-labs/skills) (cần Node.js 22.20 trở lên):

```bash
npx skills add trhlow/human-docs            # cài vào dự án hiện tại, chọn agent khi được hỏi
npx skills add trhlow/human-docs -g         # cài cho mọi dự án
npx skills add trhlow/human-docs -g -a codex   # chỉ cho Codex (vào ~/.agents/skills)
npx skills add trhlow/human-docs --skill docx-layout   # chỉ một skill
```

Codex cũng đọc được plugin của repo này (`.agents/plugins/marketplace.json`, `plugin.json`): `codex plugin marketplace add trhlow/human-docs`, rồi cài plugin `human-docs` từ danh sách plugin của Codex. Cách này chưa được thử trên máy thật; cách `npx skills` ở trên thì có.

### Chép tay

Chép hai thư mục trong `skills/` vào thư mục skill của agent (ví dụ `~/.claude/skills/` cho Claude Code, `~/.agents/skills/` cho Codex). Giữ hai thư mục nằm cạnh nhau để `check_docx.py` tìm được `check.py`.

### claude.ai

Nén từng thư mục trong `skills/` thành tệp .zip rồi tải lên phần Skills của claude.ai. Các script cần bật chức năng chạy mã.

## Yêu cầu

- Python 3 và `python-docx` (`pip install python-docx`) để dựng và kiểm tệp Word.
- `pymupdf` (`pip install pymupdf`), không bắt buộc: có thì máy quét đo bề rộng chữ bằng font Times New Roman thật để báo ô bảng xuống dòng còn một chữ.
- Microsoft Word (Windows) hoặc LibreOffice để xuất PDF và xem trang.

## Dùng thử

- "Viết lại đoạn giới thiệu này cho tự nhiên, bớt giọng AI."
- "Làm báo cáo tiến độ dự án tháng 11 thành tệp Word."
- "Soạn công văn của phòng Hành chính gửi các phòng ban về lịch nghỉ Tết, theo Nghị định 30."
- "Trình bày lại đồ án này theo mẫu của khoa" (kèm tệp mẫu .docx).

Kiểm tra thủ công:

```bash
python skills/humanize-writing/scripts/check.py bai-viet.txt
python skills/docx-layout/scripts/check_docx.py --profile admin cong-van.docx
python skills/docx-layout/scripts/check_docx.py --selftest
```

---

## English

Two agent skills, installable in Claude Code, Codex and any tool that reads the Agent Skills format:

- **humanize-writing**: rules for Vietnamese and English prose without AI tells, with a pattern scanner.
- **docx-layout**: Word layout with python-docx by document type: `thesis`, `report`, `guide`, `admin` (Vietnamese administrative documents per Decree 30/2020/ND-CP). A recipient's template always wins over the built-in profile. Includes a checker.

Install in Claude Code with `/plugin marketplace add trhlow/human-docs` then `/plugin install human-docs@human-docs`; in other agents with `npx skills add trhlow/human-docs` (add `-g` for all projects, `-a codex` to target one agent). Requires Python 3 and `python-docx`; `pymupdf` is optional.

The skill text is in Vietnamese; the trigger descriptions are bilingual, so English requests work too.

## Giấy phép

MIT. Xem [LICENSE](LICENSE).
