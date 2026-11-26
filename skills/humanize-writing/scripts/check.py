"""Quét văn bản tìm dấu hiệu văn AI theo SKILL.md. Dùng: python check.py [file...] (không có file thì đọc stdin).

Mỗi dòng của tệp là một đoạn. Ngoài các mẫu từ ngữ, máy quét còn đo nhịp câu (B6): đoạn có câu dài đều nhau hoặc
nhiều câu mở cùng một từ.
"""
import re
import statistics
import sys

# (mã quy tắc, mẫu regex). Chỉ những gì bắt được bằng từ; lỗi nội dung phải đọc tay.
RULES = [
    ("A1", r"đóng vai trò (?:quan trọng|then chốt|cốt lõi|chủ chốt)|là minh chứng|bước ngoặt|mở ra (?:một )?kỷ nguyên|để lại dấu ấn|phản ánh xu hướng|góp phần (?:vào|quan trọng)|tạo tiền đề|khẳng định vị thế|ngày càng phát triển"),
    ("A1", r"đóng góp không nhỏ|mang lại giá trị (?:to lớn|đáng kể|thiết thực)|trong (?:thời đại|xu thế|kỷ nguyên) (?:số|công nghệ|hiện nay|ngày nay)"),
    ("A1", r"\b(?:stands|serves) as\b|\bis a (?:testament|reminder)\b|\b(?:crucial|pivotal|vital|key) (?:role|moment)\b|\breflects broader\b|\bsetting the stage\b|\bmarks? a shift\b|\bturning point\b|\bevolving landscape\b|\bindelible mark\b|\bdeeply rooted\b|\bin today'?s (?:fast-paced|digital)\b|\bin an era where\b"),
    ("A2", r", (?:qua đó cho thấy|từ đó góp phần|nhằm nâng cao|giúp tăng cường|thể hiện sự|mang lại giá trị)"),
    ("A2", r", (?:highlighting|underscoring|emphasizing|ensuring|reflecting|symbolizing|fostering|enhancing|contributing to)\b|\bvaluable insights\b|\bresonates? with\b"),
    ("A3", r"các chuyên gia (?:cho rằng|nhận định)|nhiều nghiên cứu (?:chỉ ra|cho thấy)|được đánh giá cao|giới quan sát|\bexperts (?:argue|say|agree)\b|\bobservers have\b|\bindustry reports\b|\bstudies show\b"),
    ("A4", r"gắn liền với|\bin connection with\b|\b(?:widely|particularly) associated with\b"),
    ("A6", r"mặc dù còn (?:một số|nhiều) (?:thách thức|hạn chế)|bất chấp những khó khăn|\bdespite these challenges\b|\bfuture outlook\b"),
    ("A7", r"(?:^|\. )(?:Tóm lại|Nhìn chung|Có thể nói|Như vậy có thể thấy|Có thể thấy rằng|Kết luận lại|Nói tóm lại|Suy cho cùng)\b|(?:^|\. )(?:In summary|In conclusion|Overall|Ultimately),|\bat the end of the day\b|\bthe bottom line\b"),
    ("A8", r"nổi bật|vượt trội|hàng đầu|đột phá|toàn diện|liền mạch|mạnh mẽ|sôi động|tuyệt vời|nằm giữa lòng|cam kết mang đến"),
    ("A8", r"\b(?:boasts|vibrant|groundbreaking|renowned|nestled|showcas\w+|exemplifies|seamless\w*|diverse array|in the heart of|cutting-edge|world-class|effortless\w*)\b"),
    ("B1", r"(?:^|\. )(?:Bên cạnh đó|Ngoài ra|Đặc biệt|Hơn nữa|Thêm vào đó|Mặt khác),|đáng chú ý|làm nổi bật|bức tranh|hành trình|hành trang|không ngừng|đa chiều|nâng tầm|trao quyền|khai phá"),
    ("B1", r"\b(?:delve\w*|tapestry|testament|underscor\w+|pivotal|crucial|intricate\w*|interplay|meticulous\w*|garner\w*|bolstered|fostering|leverag\w+|multifaceted|landscape|quietly|dependable|echoed|universally|prioritiz\w+|realm|paradigm|synergy|unlock\w*|unleash\w*|empower\w*|supercharg\w+|revolutioniz\w+|streamlin\w+)\b|(?:^|\. )(?:Additionally|Moreover|Furthermore|Notably),"),
    ("B2", r"đóng vai trò (?:là|như)|được xem như|tự hào (?:có|sở hữu)|\b(?:functions|operates) as\b"),
    ("B3", r"không chỉ\b.{1,80}?\bmà còn|không phải (?:là )?.{1,60}?\bmà là|\bnot only\b.{1,80}?\bbut\b|\bit'?s not\b.{1,60}?\bit'?s\b"),
    ("B3", r"\bKhông [^.!?]{1,30}\. Không [^.!?]{1,30}\. Chỉ\b|\bNo \w+\. No \w+\. Just\b|\b(?:less|bớt) (?:a |an )?[^,.]{1,25}, (?:more|thêm) "),
    ("B8", r"(?:^|[.!?] )(?:Vấn đề là|Điều đáng nói là|Điều thú vị là|Hãy cùng (?:tìm hiểu|khám phá)|Và đó (?:chính )?là điều|Đó mới là điều|Điểm mấu chốt là|Câu trả lời rất đơn giản)|(?:^|[.!?] )(?:Kết quả|Lý do|Điều tuyệt vời nhất|Bí quyết)\? |\bDù bạn là [^.]{1,40} hay\b"),
    ("B8", r"\b(?:here'?s the thing|let me be clear|let'?s dive in|it'?s no secret that|when it comes to|whether you'?re|and that matters|that'?s the part everyone misses)\b|(?:^|[.!?] )(?:The result|The best part|The catch|The secret)\? "),
    ("B9", r"một cách (?:hiệu quả|toàn diện|tối ưu|linh hoạt|nhanh chóng|chính xác|dễ dàng|mạnh mẽ|bền vững|liền mạch|tối đa)|tối ưu ho[áa]|nâng cao trải nghiệm|giá trị tinh thần|bài học quý báu"),
    ("B10", r"(?<!giờ )\b\d+\s*(?:–|-|đến|tới|to)\s*\d+\s*(?:phút|giờ|ngày|tuần|tháng|minutes|hours|days)\b"),
    ("C1", r"—"),
    ("C5", r"^\s*[-*•]\s*\*\*[^*]{1,40}\*\*"),
    ("C6", r"^\s*(?:#+\s*|[-*]\s*)[\U0001F300-\U0001FAFF☀-➿]"),
    ("C8", r"[\u200b\u200c\u200d\ufeff\u00ad\u2060]"),
    ("D1", r"chắc chắn rồi|dưới đây là|hy vọng (?:điều này|thông tin này)|bạn có muốn|hãy cho tôi biết|bạn hoàn toàn đúng|nếu bạn (?:muốn|cần),? (?:tôi|mình) có thể|đây là phiên bản (?:đã )?(?:sửa|chỉnh)|\b(?:certainly!|of course!|i hope this helps|would you like|let me know|you'?re absolutely right|great question)"),
    ("D2", r"thông tin (?:cụ thể )?còn hạn chế|chưa được công bố rộng rãi|dựa trên thông tin hiện có|cần lưu ý rằng|điều quan trọng là|không nên nhầm lẫn|nên được (?:hiểu|xem|coi|trình bày) (?:là|như) [^.]{1,60} thay vì|không đủ để (?:khẳng định|kết luận)"),
    ("D2", r"\bit'?s (?:important|worth) (?:to note|noting)\b|\bnot widely (?:available|documented|disclosed)\b|\bbased on available information\b|\bdoes not by itself establish\b|\bshould be (?:treated|presented|understood) as [^.]{1,60} rather than\b|\bshould not be confused with\b"),
    ("D3", r"\[(?:Điền|Insert|Describe|Company Name)[^\]]*\]|\(nếu có\)|\b20\d\d-XX-XX\b|INSERT_\w+|example\.com/\w|\{first_name\}"),
    ("D4", r"mô hình ngôn ngữ|as an ai language model|as of my last (?:knowledge|training) update"),
    ("D5", r"tinh chỉnh (?:để|nhằm)|đảm bảo tính (?:mạch lạc|nhất quán|rõ ràng)|\b(?:ensured (?:that|clarity)|streamlined|refined (?:the|for))\b"),
    ("E1", r"utm_source=|contentReference\[oaicite|\[cite: ?\d+\]"),
    ("E3", r"truy cập (?:ngày |lúc )?\d{1,2}[/.-]\d{1,2}[/.-]\d{4}|ngày truy cập|\bAccessed:? \w+\.? \d|\bRetrieved \w+ \d{1,2}, \d{4}"),
]
PATTERNS = [(code, re.compile(rx, re.IGNORECASE)) for code, rx in RULES]
UPPER = "A-ZĐÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂƠƯẠ-Ỹ"


def scan(lines):
    """Trả về [(số dòng, mã quy tắc, đoạn khớp)]."""
    hits = []
    for no, line in enumerate(lines, 1):
        for code, rx in PATTERNS:
            for m in rx.finditer(line):
                hits.append((no, code, m.group(0)))
    return hits


def sentences(par):
    return [s for s in re.split(rf"(?<=[.!?])\s+(?=[{UPPER}\"“(])", par.strip()) if len(s.split()) >= 3]


def rhythm(lines):
    """B6: đoạn từ 5 câu mà câu dài đều nhau (độ lệch chuẩn dưới 25 % độ dài trung bình), hoặc 3 câu liền nhau mở
    cùng một từ. Ngưỡng chọn để văn người viết (độ lệch thường từ 40 % trở lên) ít bị báo nhầm."""
    out = []
    for no, par in enumerate(lines, 1):
        ss = sentences(par)
        if len(ss) >= 5:
            n = [len(s.split()) for s in ss]
            if statistics.pstdev(n) < 0.25 * statistics.mean(n):
                out.append(("B6", f"dòng {no}: {len(ss)} câu dài đều nhau ({min(n)}–{max(n)} từ): {par[:50]!r}"))
        first = [s.split()[0].strip("“\"(").lower() for s in ss]
        for k in range(len(first) - 2):
            if first[k] == first[k + 1] == first[k + 2] and len(first[k]) > 1:
                out.append(("B6", f"dòng {no}: 3 câu liền nhau cùng mở bằng {first[k]!r}: {par[:50]!r}"))
                break
    return out


def selftest():
    assert scan(["Hệ thống đóng vai trò quan trọng."])[0][1] == "A1"
    assert scan(["Nó không chỉ nhanh mà còn rẻ."])[0][1] == "B3"
    assert scan(["Ngày thi — hôm qua."])[0][1] == "C1"
    assert scan(["tr. 3–4, đối tượng – quan hệ"]) == []  # gạch nối ngắn hợp lệ
    assert scan(["Hệ thống là máy chủ ASP.NET Core."]) == []
    assert scan(["Kết quả? Nhanh hơn hẳn."])[0][1] == "B8"
    assert scan(["Xử lý dữ liệu một cách hiệu quả."])[0][1] == "B9"
    assert scan(["Mất khoảng 5–10 phút."])[0][1] == "B10"
    assert scan(["a\u200bb"])[0][1] == "C8"
    assert scan(["[3] Vercel, skills. github.com/vercel-labs/skills, truy c\u1eadp 26/11/2026."])[0][1] == "E3"
    assert scan(["[4] A. Author, Title. Accessed: Nov. 26, 2026."])[0][1] == "E3"
    assert scan(["[5] Ch\u00ednh ph\u1ee7, Ngh\u1ecb \u0111\u1ecbnh 30/2020/N\u0110-CP, ng\u00e0y 05/3/2020."]) == []
    even = " ".join(["Máy chủ ghi lại câu trả lời của thí sinh sau mỗi lần gõ phím."] * 5)
    assert [c for c, _ in rhythm([even])] == ["B6", "B6"]
    varied = ("Máy chủ ghi câu trả lời. Khi thí sinh tải lại trang, trình duyệt đọc lại bài đã lưu và mở đúng phần đang làm. "
              "Thí sinh không thấy gì khác. Giám thị thì thấy trạng thái trực tuyến đổi trong vài giây trên trang theo dõi phòng thi. "
              "Hết giờ, bài được nộp.")
    assert rhythm([varied]) == [], rhythm([varied])
    print("selftest ok")


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    sources = [(p, open(p, encoding="utf-8").read().splitlines()) for p in argv] or [("stdin", sys.stdin.read().splitlines())]
    total = 0
    for name, lines in sources:
        for no, code, text in scan(lines):
            print(f"{name}:{no}: [{code}] {text}")
            total += 1
        for code, msg in rhythm(lines):
            print(f"{name}: [{code}] {msg}")
            total += 1
    print(f"{total} chỗ cần xem lại (dấu hiệu, chưa phải lỗi chắc chắn).", file=sys.stderr)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main(sys.argv[1:])
