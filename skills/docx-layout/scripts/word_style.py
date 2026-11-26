"""Dựng tài liệu Word theo SKILL.md của docx-layout bằng python-docx. Thông số từng bộ định dạng: references/profiles.md.

    import sys; sys.path.insert(0, "<thư mục skill docx-layout>/scripts")
    import docx, word_style as ws
    doc = docx.Document()                      # có mẫu: docx.Document("mau.docx") rồi ws.setup(doc, "thesis", template=True)
    ws.setup(doc, "thesis")                    # "thesis" | "report" | "guide" | "admin"
    doc.add_paragraph("Tổng quan", style="Heading 1")          # thesis -> CHƯƠNG 1: TỔNG QUAN; report -> 1. Tổng quan
    doc.add_paragraph("Bài toán", style="Heading 2")           # -> 1.1 Bài toán
    doc.add_paragraph("Nội dung ...")                          # Normal: căn đều hai bên
    ws.table(doc, [["Việc", "Ai làm"], ["Cắm dây LAN", "Người ở trường"]], caption="Bảng 1.1. Việc cần làm")
    ws.picture(doc, "erd.png", "Hình 1.1. Sơ đồ ERD", text_px=12)  # cảnh báo khi chữ trong ảnh in ra dưới 8 pt
    ws.bullets(doc, ["Máy chủ chạy MySQL", "Máy thí sinh chỉ cần trình duyệt"])
    ws.steps(doc, ["Mở trang quản trị", "Bấm Tạo kỳ thi"])  # danh sách đánh số 1., 2., ...
    ws.code(doc, ["dotnet build", "dotnet test"])
    ws.metadata(doc, author="Tên người viết", title="Báo cáo")
    doc.save("bao-cao.docx")

Văn bản hành chính (NĐ 30/2020): ws.setup(doc, "admin"), rồi ws.admin_header(...), nội dung, ws.admin_signature(...).
Mục lục, số trang và trường SEQ do Word điền khi mở tệp và Update Field.
"""
import docx
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.image.image import Image
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Emu, Pt, RGBColor

FONT = "Times New Roman"
MONO = "Consolas"
BLACK = RGBColor(0, 0, 0)
CODE_FILL = "F2F2F2"
NUM_ID = 9017  # id riêng cho danh sách đa cấp của tiêu đề, khó trùng với id có sẵn trong mẫu
UNNUMBERED = "Heading 1 Không số"
SHORT = 25  # ô ngắn hơn chừng này ký tự không được xuống dòng

# Lề (trên, dưới, trái, phải) cm trên khổ A4 dọc. NĐ 30/2020 Phụ lục I, Mục I.3 cho phép trên, dưới 2–2,5; trái 3–3,5;
# phải 1,5–2: cả bốn bộ dùng cận dưới. line_range, size_range: khoảng check_docx chấp nhận cho style thân bài.
PROFILES = {
    # Đồ án, khóa luận, luận văn khi trường không phát mẫu. Mặc định của skill, không phải quy định chung.
    "thesis": dict(margins_cm=(2, 2, 3, 1.5), body_pt=13, line=1.5, after=6, indent_cm=0,
                   levels=("CHƯƠNG %1:", "%1.%2", "%1.%2.%3"), h1_caps=True, h1_center=True,
                   line_range=(1.5, 1.5), size_range=None, landscape_ok=False),
    # Báo cáo, đề xuất, kế hoạch trong công ty. Thụt đầu dòng 1,27 cm như phần nội dung của NĐ 30 (II.6.e).
    "report": dict(margins_cm=(2, 2, 3, 1.5), body_pt=13, line=1.5, after=6, indent_cm=1.27,
                   levels=("%1.", "%1.%2.", "%1.%2.%3."), h1_caps=False, h1_center=False,
                   line_range=(1.0, 1.5), size_range=None, landscape_ok=False),
    # Văn bản hành chính theo NĐ 30/2020: cỡ 13–14, căn đều, thụt 1 hoặc 1,27 cm, cách đoạn từ 6 pt, giãn dòng từ đơn
    # đến 1,5 (II.6.e); được trình bày khổ ngang khi có bảng biểu (I.2). Phần, Chương, Mục, Điều gõ tay theo II.6.đ.
    "admin": dict(margins_cm=(2, 2, 3, 1.5), body_pt=14, line=1.0, after=6, indent_cm=1.27,
                  levels=None, h1_caps=False, h1_center=True,
                  line_range=(1.0, 1.5), size_range=(13, 14), landscape_ok=True),
}
PROFILES["guide"] = PROFILES["report"]  # hướng dẫn, quy trình: cùng thông số với report; các bước dùng steps()


def _black_font(style_or_run_font, name=FONT, size=None, bold=None, caps=None):
    f = style_or_run_font
    f.name = name
    f.color.rgb = BLACK
    if size is not None:
        f.size = Pt(size)
    if bold is not None:
        f.bold = bold
    if caps is not None:
        f.all_caps = caps
    rpr = f._element.get_or_add_rPr()
    fonts = rpr.get_or_add_rFonts()
    # Các style Heading của Word lấy font và màu từ theme: thuộc tính theme thắng tên font, nên phải xoá đi.
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
        fonts.attrib.pop(qn(attr), None)
    for attr in ("w:eastAsia", "w:cs"):
        fonts.set(qn(attr), name)
    color = rpr.find(qn("w:color"))
    if color is not None:
        for attr in ("w:themeColor", "w:themeShade", "w:themeTint"):
            color.attrib.pop(qn(attr), None)


# Các phần tử đứng sau w:shd và w:outlineLvl trong w:pPr: Word cần đúng thứ tự của đặc tả, nên chèn trước phần tử đầu tiên có mặt.
_AFTER_SHD = ("tabs", "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE",
              "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents",
              "suppressOverlap", "jc", "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl", "divId",
              "cnfStyle", "rPr", "sectPr", "pPrChange")
_AFTER_OUTLINE = ("divId", "cnfStyle", "rPr", "sectPr", "pPrChange")


def _insert(ppr, el, after):
    for child in ppr:
        if child.tag in {qn(f"w:{n}") for n in after}:
            child.addprevious(el)
            return
    ppr.append(el)


def _style(doc, name, base="Normal"):
    try:
        return doc.styles[name]
    except KeyError:
        s = doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        s.base_style = doc.styles[base]
        return s


def _paragraph_format(style, align, line=1.5, before=0, after=6, keep_next=False):
    pf = style.paragraph_format
    pf.alignment = align
    pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE if line != 1 else WD_LINE_SPACING.SINGLE
    pf.line_spacing = line
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.keep_with_next = keep_next
    pf.first_line_indent = Cm(0)  # không thừa hưởng thụt đầu dòng của Normal


def _numbering(doc, texts):
    """Danh sách đa cấp (ví dụ CHƯƠNG 1: / 1.1 / 1.1.1) gắn vào Heading 1–3 (Word tự đánh số, mục lục lấy số theo)."""
    numbering = doc.part.numbering_part.element
    if numbering.find(f'{qn("w:num")}[@{qn("w:numId")}="{NUM_ID}"]') is not None:
        return
    lvl = "".join(
        f'<w:lvl w:ilvl="{i}"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:pStyle w:val="Heading{i + 1}"/>'
        f'<w:lvlText w:val="{text}"/><w:lvlJc w:val="{jc}"/><w:suff w:val="space"/>'
        f'<w:pPr><w:ind w:left="0" w:firstLine="0"/></w:pPr></w:lvl>'
        for i, (text, jc) in enumerate((t, "left") for t in texts)
    )
    abstract = parse_xml(f'<w:abstractNum {nsdecls("w")} w:abstractNumId="{NUM_ID}"><w:multiLevelType w:val="multilevel"/>{lvl}</w:abstractNum>')
    first_num = numbering.find(qn("w:num"))
    if first_num is not None:
        first_num.addprevious(abstract)  # mọi abstractNum phải đứng trước các num
    else:
        numbering.append(abstract)
    numbering.append(parse_xml(f'<w:num {nsdecls("w")} w:numId="{NUM_ID}"><w:abstractNumId w:val="{NUM_ID}"/></w:num>'))


def _has_style(doc, name):
    try:
        doc.styles[name]
        return True
    except KeyError:
        return False


def setup(doc, profile="thesis", template=False):
    """Khổ A4 dọc, lề, Normal, Heading 1–3, Heading 1 Không số, Caption, Code theo PROFILES[profile].

    template=True: tài liệu mở từ mẫu của nơi nhận. Mẫu thắng: không đổi khổ giấy, lề hay style nào mẫu đã có, chỉ
    thêm Caption và Code nếu mẫu thiếu."""
    p = PROFILES[profile]
    body_pt = p["body_pt"]
    if template:
        if not _has_style(doc, "Caption"):
            _paragraph_format(_style(doc, "Caption"), WD_ALIGN_PARAGRAPH.CENTER, line=1, before=3, after=6)
        if not _has_style(doc, "Code"):
            _code_style(doc)
        return doc

    top, bottom, left, right = p["margins_cm"]
    for s in doc.sections:
        s.page_width, s.page_height = Cm(21), Cm(29.7)
        s.top_margin, s.bottom_margin, s.left_margin, s.right_margin = Cm(top), Cm(bottom), Cm(left), Cm(right)

    normal = doc.styles["Normal"]
    _black_font(normal.font, size=body_pt, bold=False)
    _paragraph_format(normal, WD_ALIGN_PARAGRAPH.JUSTIFY, line=p["line"], after=p["after"])
    normal.paragraph_format.first_line_indent = Cm(p["indent_cm"])

    if p["levels"]:
        _numbering(doc, p["levels"])
        h1 = WD_ALIGN_PARAGRAPH.CENTER if p["h1_center"] else WD_ALIGN_PARAGRAPH.LEFT
        specs = [("Heading 1", body_pt + 1, h1, p["h1_caps"], 12, 12),
                 ("Heading 2", body_pt, WD_ALIGN_PARAGRAPH.LEFT, False, 12, 6),
                 ("Heading 3", body_pt, WD_ALIGN_PARAGRAPH.LEFT, False, 6, 6)]
    else:
        # admin: Phần, Chương (H1) và Mục, Tiểu mục (H2) canh giữa, đậm; Điều (H3) đậm, lùi đầu dòng (NĐ 30 II.6.đ).
        # Chữ "Chương I", "Điều 1." người viết gõ, nên không gắn danh sách đánh số.
        specs = [("Heading 1", body_pt, WD_ALIGN_PARAGRAPH.CENTER, False, 12, 6),
                 ("Heading 2", body_pt, WD_ALIGN_PARAGRAPH.CENTER, False, 12, 6),
                 ("Heading 3", body_pt, WD_ALIGN_PARAGRAPH.JUSTIFY, False, 6, 6)]
    for level, (name, size, align, caps, before, after) in enumerate(specs):
        s = doc.styles[name]
        _black_font(s.font, size=size, bold=True, caps=caps)
        s.font.italic = False
        _paragraph_format(s, align, line=p["line"], before=before, after=after, keep_next=True)
        if p["levels"]:
            numpr = s.element.get_or_add_pPr().get_or_add_numPr()
            numpr.get_or_add_ilvl().val = level
            numpr.get_or_add_numId().val = NUM_ID
    if not p["levels"]:
        doc.styles["Heading 3"].paragraph_format.first_line_indent = Cm(p["indent_cm"])

    plain = _style(doc, UNNUMBERED, base="Heading 1")
    _black_font(plain.font, size=body_pt + 1, bold=True, caps=True)
    _paragraph_format(plain, WD_ALIGN_PARAGRAPH.CENTER, before=12, after=12, keep_next=True)
    ppr = plain.element.get_or_add_pPr()
    ppr.get_or_add_numPr().get_or_add_numId().val = 0  # numId 0: tắt số thừa hưởng từ Heading 1
    if ppr.find(qn("w:outlineLvl")) is None:  # vẫn vào mục lục ở cấp 1
        _insert(ppr, ppr.makeelement(qn("w:outlineLvl"), {qn("w:val"): "0"}), _AFTER_OUTLINE)

    caption = _style(doc, "Caption")
    _black_font(caption.font, size=body_pt, bold=False)
    caption.font.italic = False
    _paragraph_format(caption, WD_ALIGN_PARAGRAPH.CENTER, line=1, before=3, after=6)

    _code_style(doc)

    for name in ("Title", "Subtitle", "TOC Heading", "Header", "Footer", "List Paragraph",
                 "toc 1", "toc 2", "toc 3", "table of figures"):
        try:
            _black_font(doc.styles[name].font)
        except KeyError:
            pass
    if profile == "admin":
        _admin_page_numbers(doc, body_pt)
    return doc


def _code_style(doc):
    code = _style(doc, "Code")
    _black_font(code.font, name=MONO, size=10, bold=False)
    _paragraph_format(code, WD_ALIGN_PARAGRAPH.LEFT, line=1, before=0, after=0)
    cppr = code.element.get_or_add_pPr()
    if cppr.find(qn("w:shd")) is None:
        _insert(cppr, parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{CODE_FILL}"/>'), _AFTER_SHD)


def _admin_page_numbers(doc, pt):
    """NĐ 30 I.7: số trang chữ số Ả Rập, cỡ 13–14, đứng, canh giữa ở lề trên, không hiện ở trang thứ nhất."""
    for s in doc.sections:
        s.different_first_page_header_footer = True
        p = s.header.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        for kind, extra in (("begin", ""), (None, " PAGE "), ("end", "")):
            r = p.add_run()
            r.font.size = Pt(pt)
            if kind:
                r._r.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="{kind}"/>'))
            else:
                r._r.append(parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve">{extra}</w:instrText>'))


def text_width_cm(section):
    return Emu(section.page_width - section.left_margin - section.right_margin).cm


def _cm(text, pt, bold=False):
    """Bề rộng chữ in ra (cm), đo bằng font Times New Roman thật khi có PyMuPDF (xem check_docx.width_pt)."""
    from check_docx import width_pt
    return width_pt(text, pt, bold) / 72 * 2.54


def column_widths(rows, total_cm, pt):
    """Chia bề rộng theo nội dung: cột có chữ dài rộng hơn, không cột nào hẹp hơn chữ dài nhất của nó. Chỉ là điểm
    xuất phát: sau khi dựng vẫn chạy check_docx (F7) và xem PDF, rồi chỉnh tay cột hay chữ của ô còn lẻ một chữ."""
    pad = 0.38 + 0.1  # lề trong của ô Table Grid 0,19 cm mỗi bên, cộng chút dự phòng
    cols = max(len(r) for r in rows)
    def cells(c):
        return [(r[c] if c < len(r) else "", i == 0) for i, r in enumerate(rows)]

    # Ô ngắn (đến SHORT ký tự, như tiêu đề cột hay "Người ở trường") phải nằm trọn một dòng; ô dài thì ít nhất vừa chữ dài nhất.
    need = [max([_cm(w, pt, b) for t, b in cells(c) for w in t.split()] + [_cm(t, pt, b) for t, b in cells(c) if len(t) <= SHORT] + [0.3]) + pad
            for c in range(cols)]
    want = [min(max(_cm(t, pt, b) for t, b in cells(c)), 25) + pad for c in range(cols)]
    free = total_cm - sum(need)
    extra = [max(w - n, 0) for w, n in zip(want, need)]
    if free <= 0 or sum(extra) == 0:
        scale = total_cm / sum(need)
        return [n * scale for n in need]
    share = min(1, free / sum(extra))
    widths = [n + e * share for n, e in zip(need, extra)]
    rest = total_cm - sum(widths)
    return [w + rest * w / sum(widths) for w in widths]


def _score(rows, widths, pt):
    """(số ô lẻ một chữ ở dòng cuối + tiêu đề cột ngắn bị tách dòng, tổng số dòng): càng nhỏ càng tốt."""
    from check_docx import lines
    bad = height = 0
    for r, row in enumerate(rows):
        tallest = 1
        for c, t in enumerate(row):
            n, last = lines(t, (widths[c] - 0.38) / 2.54 * 72, pt, r == 0)
            bad += (n >= 2 and last == 1 and len(t.split()) >= 3) or (r == 0 and n >= 2 and len(t.split()) <= 2)
            tallest = max(tallest, n)
        height += tallest
    return bad, height


def fit_widths(rows, widths, pt, step=0.1, reach=3.0, rounds=20):
    """Chuyển bề rộng giữa hai cột (bước 1 mm, tối đa reach cm, giữ tổng bề rộng) chừng nào bớt được ô lẻ một chữ hay
    bảng thấp đi. Thử cả bước xa vì một ô chỉ hết lẻ khi vượt qua một ngưỡng. Cột không hẹp hơn chữ dài nhất của nó.
    Ô vẫn lẻ một chữ sau bước này thì sửa câu chữ của ô."""
    need = [max([_cm(w, pt, r == 0) for r, row in enumerate(rows) if c < len(row) for w in row[c].split()] + [0.3]) + 0.48
            for c in range(len(widths))]
    rows = [list(r) + [""] * (len(widths) - len(r)) for r in rows]
    best = _score(rows, widths, pt)
    for _ in range(rounds):
        found = None
        for i in range(len(widths)):
            for j in range(len(widths)):
                for k in range(1, int(reach / step) + 1):
                    d = k * step
                    if i == j or widths[j] - d < need[j]:
                        break
                    cand = list(widths)
                    cand[i] += d
                    cand[j] -= d
                    score = _score(rows, cand, pt)
                    if score < best:
                        best, found = score, cand
        if found is None:
            break
        widths = found
    return widths


NUMERIC = __import__("re").compile(r"^[\d.,%/:+-]{1,8}$")


def table(doc, rows, caption=None, widths_cm=None, pt=13):
    """Bảng không màu (Table Grid), hàng đầu là tiêu đề: đậm, căn giữa, lặp khi sang trang."""
    if caption:
        doc.add_paragraph(caption, style="Caption").paragraph_format.keep_with_next = True
    t = doc.add_table(rows=len(rows), cols=max(len(r) for r in rows))
    t.style = doc.styles["Table Grid"]
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False  # python-docx ghi w:tblLayout fixed đúng chỗ: độ rộng cột được giữ
    widths = widths_cm or fit_widths(rows, column_widths(rows, text_width_cm(doc.sections[-1]), pt), pt)
    numeric = [all(NUMERIC.match(r[c]) for r in rows[1:] if c < len(r) and r[c]) for c in range(len(widths))]
    for r, values in enumerate(rows):
        row = t.rows[r]
        if r == 0:
            row._tr.get_or_add_trPr().append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
        for c, cell in enumerate(row.cells):
            cell.width = Cm(widths[c])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            run = p.add_run(values[c] if c < len(values) else "")
            run.bold = r == 0
            pf = p.paragraph_format
            pf.alignment = WD_ALIGN_PARAGRAPH.CENTER if r == 0 or numeric[c] else WD_ALIGN_PARAGRAPH.LEFT
            pf.line_spacing, pf.space_before, pf.space_after = 1.0, Pt(3), Pt(3)
            pf.first_line_indent = Cm(0)
    for c, w in enumerate(widths):
        t.columns[c].width = Cm(w)
    return t


def code(doc, lines):
    """Khối mã: font đơn cách trên nền xám nhạt, ngoại lệ duy nhất của quy tắc không tô nền."""
    for line in lines:
        doc.add_paragraph(line, style="Code")


MIN_TEXT_PT = 8  # chữ trong hình in ra nhỏ hơn chừng này thì khó đọc


def picture(doc, path, caption, text_px=None, dpi_scale=1):
    """Ảnh trên trang dọc, rộng tối đa bằng khổ chữ, ảnh và chú thích gọn trong một trang. Không bao giờ quay trang.

    text_px: cỡ chữ nhỏ nhất trong sơ đồ (px của công cụ vẽ, draw.io mặc định 12); dpi_scale: hệ số khi xuất ảnh
    (draw.io -s 2 thì 2). Có hai số này thì in cảnh báo khi chữ in ra nhỏ hơn MIN_TEXT_PT: khi đó vẽ lại sơ đồ theo
    chiều dọc hoặc tách thành nhiều hình, đừng thu nhỏ hay quay ngang."""
    img = Image.from_file(path)
    ratio = img.px_width / img.px_height
    section = doc.sections[-1]
    usable_w = section.page_width - section.left_margin - section.right_margin
    usable_h = section.page_height - section.top_margin - section.bottom_margin - Cm(2.5)  # chỗ cho chú thích
    native_w = Emu(int(img.px_width / 96 * 914400))  # không phóng quá cỡ gốc ở 96 dpi
    w = min(usable_w, native_w, Emu(int(usable_h * ratio)))
    if text_px:
        printed = text_px * 0.75 * (Emu(w).inches * 96) / (img.px_width / dpi_scale)
        if printed < MIN_TEXT_PT:
            import sys
            msg = f"Cảnh báo: chữ trong {path} in ra chỉ {printed:.1f} pt (< {MIN_TEXT_PT} pt): vẽ lại theo chiều dọc hoặc tách hình"
            try:
                print(msg, file=sys.stderr)
            except UnicodeEncodeError:  # cửa sổ lệnh cp1252 của Windows
                print(msg.encode("ascii", "backslashreplace").decode(), file=sys.stderr)
    p = doc.add_paragraph()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.first_line_indent = 0
    p.add_run().add_picture(path, width=w)
    doc.add_paragraph(caption, style="Caption")
    return p


BULLET_ID = 9018
STEPS_ID = 9019


def _list(doc, items, abstract_id, fmt, text, restart):
    """Danh sách của Word (numbering), không gõ tay ký tự đầu dòng. Ký hiệu thẳng hàng với thụt đầu dòng của đoạn văn
    (0 nếu đoạn không thụt), chữ cách ký hiệu 0,63 cm như danh sách mặc định của Word. Thụt đặt cả trên từng đoạn để
    không phụ thuộc thứ tự ưu tiên giữa style và numbering."""
    numbering = doc.part.numbering_part.element
    fli = doc.styles["Normal"].paragraph_format.first_line_indent
    dash = int((fli or 0) / 635)  # EMU -> twip
    if numbering.find(f'{qn("w:abstractNum")}[@{qn("w:abstractNumId")}="{abstract_id}"]') is None:
        abstract = parse_xml(
            f'<w:abstractNum {nsdecls("w")} w:abstractNumId="{abstract_id}"><w:multiLevelType w:val="singleLevel"/>'
            f'<w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="{fmt}"/><w:lvlText w:val="{text}"/>'
            f'<w:lvlJc w:val="left"/><w:pPr><w:ind w:left="{dash + 357}" w:hanging="357"/></w:pPr>'
            f'<w:rPr><w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}"/></w:rPr></w:lvl></w:abstractNum>')
        first_num = numbering.find(qn("w:num"))
        if first_num is not None:
            first_num.addprevious(abstract)  # mọi abstractNum phải đứng trước các num
        else:
            numbering.append(abstract)
    num_id = abstract_id
    if restart:  # mỗi danh sách đánh số bắt đầu lại từ 1
        num_id = max([int(n.get(qn("w:numId"))) for n in numbering.findall(qn("w:num"))] + [STEPS_ID]) + 1
    if numbering.find(f'{qn("w:num")}[@{qn("w:numId")}="{num_id}"]') is None:
        override = '<w:lvlOverride w:ilvl="0"><w:startOverride w:val="1"/></w:lvlOverride>' if restart else ""
        numbering.append(parse_xml(f'<w:num {nsdecls("w")} w:numId="{num_id}"><w:abstractNumId w:val="{abstract_id}"/>{override}</w:num>'))
    out = []
    for item in items:
        p = doc.add_paragraph(item)
        numpr = p._p.get_or_add_pPr().get_or_add_numPr()
        numpr.get_or_add_ilvl().val = 0
        numpr.get_or_add_numId().val = num_id
        p.paragraph_format.left_indent = Emu((dash + 357) * 635)
        p.paragraph_format.first_line_indent = Emu(-357 * 635)
        out.append(p)
    return out


def bullets(doc, items, char="-"):
    """Gạch đầu dòng ngắn "-" (hoặc "•"), không dùng "–", "—": gạch dài trông dài hơn hẳn gạch đầu dòng thường."""
    return _list(doc, items, BULLET_ID, "bullet", char, restart=False)


def steps(doc, items):
    """Danh sách đánh số 1., 2., ... cho các bước (tài liệu hướng dẫn, quy trình). Mỗi lần gọi đánh lại từ 1."""
    return _list(doc, items, STEPS_ID, "decimal", "%1.", restart=True)


def metadata(doc, author, title=""):
    """Thuộc tính tệp (File > Info): python-docx mặc định ghi tác giả "python-docx" và chú thích "generated by
    python-docx", ai mở Properties cũng thấy tệp do máy sinh ra."""
    import datetime
    cp = doc.core_properties
    cp.author = cp.last_modified_by = author
    cp.title = title
    cp.comments = cp.subject = cp.keywords = cp.category = ""
    now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None, microsecond=0)
    if not cp.created or cp.created.year < 2020:
        cp.created = now
    cp.modified = now
    cp.revision = max(cp.revision or 1, 1)


# Văn bản hành chính: NĐ 30/2020/NĐ-CP, Phụ lục I. Vị trí theo sơ đồ Mục IV (ô 1–4 ở đầu trang, 5a giữa trang, 7a/7b
# bên phải và 9b bên trái phía cuối), cỡ chữ theo Mục II và bảng Mục V.
LAYOUT = "Thể thức"  # tiền tố tên style các dòng thể thức: check_docx không đòi căn đều hay cấm in đậm ở các dòng này
_TABLE_AFTER_BORDERS = ("shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption", "tblDescription")
CELL_PAD_CM = 0.38  # lề trong mặc định của ô: 0,19 cm mỗi bên


def _sizes(body_pt):
    """Chú thích 1 của bảng Mục V: cỡ chữ tăng giảm phải thống nhất, ví dụ Quốc hiệu 13, Tiêu ngữ 14, địa danh 14,
    hoặc Quốc hiệu 12, Tiêu ngữ 13, địa danh 13. Tên cơ quan 12–13, V/v 12–13, tên loại và trích yếu 13–14."""
    big = body_pt >= 14
    return dict(qh=13 if big else 12, tn=14 if big else 13, date=14 if big else 13, org=13 if big else 12,
                vv=13 if big else 12, title=14 if big else 13, number=13)


def _layout_table(doc, widths_cm, rows=1):
    """Bảng không viền dùng để dàn trang (hai khối đặt cạnh nhau). Viền nil ghi rõ để check_docx nhận ra."""
    t = doc.add_table(rows=rows, cols=len(widths_cm))
    t.autofit = False
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    edges = "".join(f'<w:{e} w:val="nil"/>' for e in ("top", "left", "bottom", "right", "insideH", "insideV"))
    _insert(t._tbl.tblPr, parse_xml(f'<w:tblBorders {nsdecls("w")}>{edges}</w:tblBorders>'), _TABLE_AFTER_BORDERS)
    for c, w in enumerate(widths_cm):
        t.columns[c].width = Cm(w)
        for row in t.rows:
            row.cells[c].width = Cm(w)
            row.cells[c].vertical_alignment = WD_ALIGN_VERTICAL.TOP
    return t


def _line(container, text, pt, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.CENTER, before=0, style=None):
    """Một dòng thể thức. Ô bảng mới có sẵn một đoạn rỗng: dùng đoạn đó cho dòng đầu."""
    paras = container.paragraphs
    if not hasattr(container, "sections") and len(paras) == 1 and not paras[0].runs:
        p = paras[0]
    else:
        p = container.add_paragraph()
    if style:
        p.style = style
    pf = p.paragraph_format
    pf.alignment = align
    pf.first_line_indent = Cm(0)
    pf.line_spacing, pf.space_before, pf.space_after = 1.0, Pt(before), Pt(0)
    r = p.add_run(text)
    r.font.size, r.bold, r.italic = Pt(pt), bold, italic
    return p


def _rule(container, width_cm, box_cm, style=None):
    """Đường kẻ ngang nét liền dài width_cm, đặt cân đối dưới dòng chữ phía trên (viền dưới của một đoạn rỗng)."""
    p = container.add_paragraph()
    if style:
        p.style = style
    side = max((box_cm - width_cm) / 2, 0)
    pf = p.paragraph_format
    pf.left_indent, pf.right_indent, pf.first_line_indent = Cm(side), Cm(side), Cm(0)
    pf.line_spacing_rule, pf.line_spacing = WD_LINE_SPACING.EXACTLY, Pt(2)
    pf.space_before = pf.space_after = Pt(0)
    border = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="1" w:color="000000"/></w:pBdr>')
    _insert(p._p.get_or_add_pPr(), border, ("shd",) + _AFTER_SHD)
    return p


def _layout_style(doc, name):
    s = _style(doc, f"{LAYOUT} - {name}")
    _paragraph_format(s, WD_ALIGN_PARAGRAPH.CENTER, line=1, before=0, after=0)
    return s


def _admin_widths(doc, sz):
    """Cột phải vừa Quốc hiệu trên một dòng (đo bằng font thật khi có), cột trái là phần còn lại của khổ chữ."""
    right = _cm("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM", sz["qh"], bold=True) + CELL_PAD_CM + 0.3
    return [text_width_cm(doc.sections[-1]) - right, right]


def admin_header(doc, issuer, number, place_date, parent=None, doc_type=None, summary=None, vv=None, to=None,
                 rule_ratio=1 / 3):
    """Ô 1–5 và 9a của sơ đồ Mục IV. issuer, parent: tên cơ quan ban hành và chủ quản (in hoa); number: "Số: 15/QĐ-BNV";
    place_date: "Hà Nội, ngày 05 tháng 01 năm 2020"; doc_type, summary: tên loại và trích yếu (văn bản có tên loại);
    vv: trích yếu công văn (không kèm "V/v"); to: danh sách nơi "Kính gửi". rule_ratio: đường kẻ dưới tên cơ quan và
    dưới trích yếu dài 1/3 đến 1/2 dòng chữ (II.2.b, II.5.b)."""
    sz = _sizes(doc.styles["Normal"].font.size.pt)
    widths = _admin_widths(doc, sz)
    t = _layout_table(doc, widths, rows=2)
    left, right = t.rows[0].cells
    box = [w - CELL_PAD_CM for w in widths]

    if parent:  # II.2.b: chủ quản in hoa, đứng, không đậm; cơ quan ban hành in hoa, đứng, đậm, cách nhau dòng đơn
        _line(left, parent.upper(), sz["org"])
    _line(left, issuer.upper(), sz["org"], bold=True)
    _rule(left, min(_cm(issuer.upper(), sz["org"], True), box[0]) * rule_ratio, box[0])
    # II.1: Quốc hiệu in hoa 12–13 đậm; Tiêu ngữ 13–14 đậm, kẻ dưới dài bằng dòng chữ
    _line(right, "CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM", sz["qh"], bold=True)
    motto = "Độc lập - Tự do - Hạnh phúc"
    _line(right, motto, sz["tn"], bold=True)
    _rule(right, _cm(motto, sz["tn"], True), box[1])

    # Hàng 2: số, ký hiệu (II.3.c, cỡ 13) cùng dòng với địa danh, ngày tháng (II.4.c, nghiêng 13–14)
    left, right = t.rows[1].cells
    _line(left, number, sz["number"], before=6)
    if vv:  # II.5.b: "V/v" in thường 12–13, đứng, canh giữa dưới số và ký hiệu, cách 6 pt
        _line(left, f"V/v {vv}", sz["vv"], before=6)
    _line(right, place_date, sz["date"], italic=True, before=6)

    if doc_type:  # II.5.b: tên loại in hoa đậm, trích yếu in thường đậm, kẻ dưới 1/3–1/2 dòng chữ
        st = _layout_style(doc, "Tên loại")
        _line(doc, doc_type.upper(), sz["title"], bold=True, before=18, style=st)
        if summary:
            _line(doc, summary, sz["title"], bold=True, style=st)
            text_w = text_width_cm(doc.sections[-1])
            _rule(doc, min(_cm(summary, sz["title"], True), text_w) * rule_ratio, text_w, style=st)
    if to:
        kinh_gui(doc, to)
    return t


def kinh_gui(doc, recipients, indent_cm=2.5):
    """Ô 9a (II.9.d): "Kính gửi:" in thường 13–14, đứng. Một nơi nhận: cùng dòng. Nhiều nơi: mỗi nơi một dòng, gạch đầu
    dòng thẳng hàng dưới dấu hai chấm, cuối dòng ";", dòng cuối ".". indent_cm: vị trí khối, Nghị định không ghi số."""
    pt = doc.styles["Normal"].font.size.pt
    st = _layout_style(doc, "Kính gửi")
    if len(recipients) == 1:
        p = _line(doc, f"Kính gửi: {recipients[0]}.", pt, align=WD_ALIGN_PARAGRAPH.LEFT, before=12, style=st)
        p.paragraph_format.left_indent = Cm(indent_cm)
        return
    p = _line(doc, "Kính gửi:", pt, align=WD_ALIGN_PARAGRAPH.LEFT, before=12, style=st)
    p.paragraph_format.left_indent = Cm(indent_cm)
    colon = indent_cm + _cm("Kính gửi", pt)
    for i, name in enumerate(recipients):
        end = "." if i == len(recipients) - 1 else ";"
        q = _line(doc, f"- {name}{end}", pt, align=WD_ALIGN_PARAGRAPH.LEFT, style=st)
        q.paragraph_format.left_indent = Cm(colon)


def admin_signature(doc, authority, name, recipients, archive, signature_space_pt=72):
    """Ô 7a, 7b và 9b. authority: các dòng quyền hạn, chức vụ, ví dụ ["KT. GIÁM ĐỐC", "PHÓ GIÁM ĐỐC"] (in hoa, đậm
    13–14, II.7.đ); name: họ tên người ký (in thường, đậm, canh giữa); recipients: các nơi nhận; archive: phần sau
    "Lưu:", ví dụ "VT, TCCB". "Nơi nhận:" cỡ 12 nghiêng đậm sát lề trái, danh sách cỡ 11 đứng (II.9.d).
    signature_space_pt: khoảng trống cho chữ ký và dấu, Nghị định không ghi số."""
    sz = _sizes(doc.styles["Normal"].font.size.pt)
    t = _layout_table(doc, _admin_widths(doc, sz))
    left, right = t.rows[0].cells
    _line(left, "Nơi nhận:", 12, bold=True, italic=True, align=WD_ALIGN_PARAGRAPH.LEFT, before=12)
    for r in recipients:
        _line(left, f"- {r};", 11, align=WD_ALIGN_PARAGRAPH.LEFT)
    _line(left, f"- Lưu: {archive}.", 11, align=WD_ALIGN_PARAGRAPH.LEFT)
    for i, a in enumerate(authority):
        _line(right, a.upper(), sz["title"], bold=True, before=12 if i == 0 else 0)
    _line(right, name, sz["title"], bold=True, before=signature_space_pt)
    return t


def smart_quotes(text):
    """Ngoặc kép thẳng thành ngoặc cong như Word tự đổi khi gõ (AutoFormat). Dùng cho chữ đưa vào .docx, không cho mã."""
    import re
    text = re.sub(r'(^|[\s(\[{“‘—–-])"', r"\1“", text)
    text = text.replace('"', "”")
    text = re.sub(r"(^|[\s(\[{“])'", r"\1‘", text)
    return text.replace("'", "’")
