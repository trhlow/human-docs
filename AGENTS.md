# human-docs: hướng dẫn cho người và agent sửa repo này

## Nếu bạn là AI agent

Đọc hết phần này trước khi sửa gì.

Skill trong repo này được người khác cài và dùng để soạn đồ án, báo cáo, công văn thật. Một thông số sai (lề, cỡ chữ, cách đánh số) hay một nguồn bịa sẽ đi vào tài liệu của họ. Vì vậy:

1. Không thêm thông số trình bày nào không có nguồn. Thông số lấy từ quy định thì ghi tên văn bản, số mục và trích nguyên văn trong `skills/docx-layout/references/profiles.md`. Thông số skill tự chọn thì ghi rõ là mặc định của skill và nằm trong khoảng nào.
2. Không viết lại quy định theo trí nhớ. Đọc văn bản gốc (bản PDF, cổng văn bản của cơ quan ban hành), không dựa vào bài tóm tắt.
3. Không đưa dữ liệu cá nhân vào repo: tên người, đường dẫn máy riêng, tên dự án của người dùng.
4. Chữ tiếng Việt trong skill, README, ghi chú phát hành viết theo skill `humanize-writing` và chạy `check.py` trước khi commit.
5. Cho người dùng xem toàn bộ thay đổi và được họ đồng ý trước khi mở pull request.

## Cấu trúc

```
skills/humanize-writing/   SKILL.md, scripts/check.py
skills/docx-layout/        SKILL.md, references/, scripts/word_style.py, scripts/check_docx.py
.claude-plugin/            marketplace.json, plugin.json (Claude Code; các agent khác cài qua npx skills)
```

Hai skill phải nằm cạnh nhau: `check_docx.py` tìm `check.py` ở `../../humanize-writing/scripts`. Đường dẫn trong SKILL.md tính từ thư mục chứa SKILL.md, không ghi `~/.claude/...`. Frontmatter của SKILL.md phải là YAML hợp lệ (không để `: ` trong `description` không có ngoặc), vì nhiều agent đọc YAML chặt hơn Claude Code.

## Kiểm tra trước khi commit

```bash
python skills/humanize-writing/scripts/check.py --selftest
python skills/docx-layout/scripts/check_docx.py --selftest
claude plugin validate --strict .
```

GitHub Actions chạy hai lệnh Python ở trên trên Windows, macOS và Linux sau mỗi lần push.

Thay đổi về trình bày (`word_style.py`, bộ định dạng) còn phải dựng một tệp mẫu, xuất PDF bằng Word hoặc LibreOffice và xem trang. Máy quét không thấy được ảnh mờ, khoảng trắng lạ hay dòng lệch tâm.

## Phát hành

1. Sửa nội dung trong `skills/` thì tăng `version` trong `.claude-plugin/plugin.json`. Claude Code lưu plugin theo số phiên bản, giữ số cũ thì người đã cài không nhận được bản mới. Chỉ sửa README hay tệp ngoài `skills/` thì không cần.
2. Commit, push, rồi tạo release có tag `vX.Y.Z`. Ghi chú phát hành nói sửa gì, vì sao, đã kiểm thế nào; đính kèm `humanize-writing.zip` và `docx-layout.zip` (mỗi tệp chứa một thư mục skill, chỉ gồm tệp đã commit).
