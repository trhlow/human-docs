# Ghi chú phát hành

## v1.0.1 (26/11/2026)

- docx-layout: thêm 6 pt sau khối "Kính gửi". Khi soạn thử công văn, dòng "Kính gửi" dính sát đoạn nội dung đầu tiên; Nghị định 30/2020 không quy định khoảng này, skill chọn bằng khoảng cách giữa các đoạn văn.
- README viết lại theo bố cục của obra/superpowers: cách hoạt động, cách cài cho từng agent, quy trình, khi kết quả chưa đúng, cập nhật.
- Release đính kèm `humanize-writing.zip` và `docx-layout.zip` để tải lên claude.ai.

## v1.0.0 (26/11/2026)

Bản đầu, tách từ skill `viet-nhu-nguoi` dùng riêng thành hai skill cài được trên nhiều agent.

- `humanize-writing`: quy tắc nhóm A–E và máy quét `check.py`.
- `docx-layout`: bốn bộ định dạng `thesis`, `report`, `guide`, `admin`; mẫu của nơi nhận thắng (`template=True`). Bộ `admin` dựng thể thức văn bản hành chính theo Phụ lục I Nghị định 30/2020/NĐ-CP, thông số trích nguyên văn trong `references/profiles.md`.
- `check_docx.py` kiểm theo bộ định dạng đã chọn, tìm `check.py` ở skill bên cạnh, đo chữ bằng font Times New Roman thật trên Windows, macOS, Linux khi có.
- `table()` tự chia lại độ rộng cột để ô bảng không xuống dòng còn một chữ; đã đối chiếu với bản PDF do Word xuất.
- Sửa lỗi có từ bản cũ: dòng "CHƯƠNG n" lệch trái khoảng 0,7 cm do số chương căn giữa trong danh sách đa cấp.
- Đóng gói cho Claude Code (`/plugin`), Codex và các agent khác (`npx skills`).
