"""Quét một tệp .docx theo SKILL.md của docx-layout. Dùng: python check_docx.py [--profile thesis|report|guide|admin] file.docx [...]

Chỉ bắt những gì đọc được từ XML: màu chữ, font, nền màu, in đậm ngoài tiêu đề, căn lề, style tiêu đề và đánh số,
hàng tiêu đề bảng, ô bảng xuống dòng còn một chữ, trang ngang, gạch đầu dòng, ký tự ẩn, ngoặc thẳng, thuộc tính tệp,
và chạy luôn máy quét văn phong check.py (skill humanize-writing, nếu có cài) trên chữ của tệp. Bảng xấu hay ảnh mờ vẫn phải xem bằng mắt trên bản PDF.
Phần trước tiêu đề đầu tiên (trang bìa, mục lục) được bỏ qua, trừ bộ admin (văn bản hành chính không có trang bìa).
Dòng thể thức (style "Thể thức - ...") và bảng không viền dùng để dàn trang không bị đòi căn đều hay cấm in đậm.
"""
import os
import sys

import docx
from docx.image.image import Image
from docx.oxml.ns import qn
from docx.shared import Emu

FONT = "Times New Roman"
MONO = {"consolas", "courier new", "cascadia mono", "lucida console"}
CODE_FILL = {"F2F2F2", "EEEEEE", "EFEFEF", "F5F5F5"}
HEADINGS = ("heading", "title", "caption", "toc", "table of figures")
LAYOUT_STYLE = "thể thức"  # word_style.LAYOUT, viết thường
CAPTION = __import__("re").compile(r"^(Bảng|Hình|Table|Figure)\s+(PL\.)?\d")
REFERENCE = __import__("re").compile(r"^\[\d+\]")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def style_chain(doc, style_id):
    """Style và các style cha, gần nhất trước."""
    chain, seen = [], set()
    while style_id and style_id not in seen:
        seen.add(style_id)
        el = doc.styles.element.find(f'{W}style[@{W}styleId="{style_id}"]')
        if el is None:
            break
        chain.append(el)
        based = el.find(f"{W}basedOn")
        style_id = based.get(f"{W}val") if based is not None else None
    return chain


def para_style_id(p_el):
    ps = p_el.find(f"{W}pPr/{W}pStyle")
    return ps.get(f"{W}val") if ps is not None else "Normal"


def style_name(doc, style_id):
    el = doc.styles.element.find(f'{W}style[@{W}styleId="{style_id}"]')
    name = el.find(f"{W}name") if el is not None else None
    return (name.get(f"{W}val") if name is not None else style_id).lower()


def inherited(doc, p_el, path):
    """Giá trị của pPr/<path> trên đoạn, hoặc từ style của nó."""
    own = p_el.find(f"{W}pPr/{path}")
    if own is not None:
        return own
    for st in style_chain(doc, para_style_id(p_el)):
        el = st.find(f"{W}pPr/{path}")
        if el is not None:
            return el
    return None


def run_font(doc, r_el, p_el):
    for el in [r_el.find(f"{W}rPr/{W}rFonts")] + [st.find(f"{W}rPr/{W}rFonts") for st in style_chain(doc, para_style_id(p_el))]:
        if el is not None and el.get(f"{W}ascii"):
            return el.get(f"{W}ascii")
    return None


def is_bold(doc, r_el, p_el):
    for el in [r_el.find(f"{W}rPr/{W}b")] + [st.find(f"{W}rPr/{W}b") for st in style_chain(doc, para_style_id(p_el))]:
        if el is not None:
            return el.get(f"{W}val") not in ("0", "false")
    return False


def text(el):
    """Chữ của phần tử; ngắt dòng (w:br) và tab tính như dấu cách."""
    return "".join((e.text or "") if e.tag == f"{W}t" else " " for e in el.iter(f"{W}t", f"{W}br", f"{W}tab")
                   if not (e.tag == f"{W}tab" and e.getparent().tag != f"{W}r"))


_FONTS = {}


def width_pt(word, size, bold):
    """Width of a word in Times New Roman, from the Windows font file when PyMuPDF has it, else 0.41 em a character
    (the average measured on a Word PDF of Vietnamese text)."""
    if bold not in _FONTS:
        _FONTS[bold] = None
        try:
            import pymupdf
        except ImportError:  # no PyMuPDF: estimate
            pymupdf = None
        for path in _font_files(bold) if pymupdf else []:
            if os.path.exists(path):
                _FONTS[bold] = pymupdf.Font(fontfile=path)
                break
    font = _FONTS[bold]
    return font.text_length(word, fontsize=size) if font else 0.41 * size * len(word)


def _font_files(bold):
    win = os.path.join(os.environ.get("WINDIR", "C:/Windows"), "Fonts", "timesbd.ttf" if bold else "times.ttf")
    mac = "Times New Roman Bold.ttf" if bold else "Times New Roman.ttf"
    linux = "Times_New_Roman_Bold.ttf" if bold else "Times_New_Roman.ttf"
    return [win, "/System/Library/Fonts/Supplemental/" + mac, "/Library/Fonts/" + mac,
            "/usr/share/fonts/truetype/msttcorefonts/" + linux]


def layout_table(tbl_el):
    """Bảng dàn trang: mọi viền đặt nil/none (word_style._layout_table), như khối Quốc hiệu và khối chữ ký."""
    borders = tbl_el.find(f"{W}tblPr/{W}tblBorders")
    return borders is not None and len(borders) > 0 and all(b.get(f"{W}val") in ("nil", "none") for b in borders)


def words_of(text):
    import re
    return [w for w in re.split("[ \t\n\u200b]+", text.strip()) if w]  # a no-break space joins, as in Word


def lines(text, avail_pt, size, bold=False):
    """Lines a cell paragraph takes and words on its last line; breaks between words and after hyphens, as Word."""
    import re
    space = width_pt(" ", size, bold)
    n, current, last = 0, None, 0
    for word in words_of(text):
        for k, part in enumerate(re.split(r"(?<=-)(?=.)", word)):
            w = width_pt(part, size, bold)
            gap = space if k == 0 else 0
            if current is not None and current + gap + w > avail_pt:
                n, current, last = n + 1, w, 1
            else:
                current, last = (w if current is None else current + gap + w), (last + 1 if k == 0 else last)
    return n + (current is not None), last


INVISIBLE = {"\u200b": "U+200B", "\u200c": "U+200C", "\u200d": "U+200D", "\ufeff": "U+FEFF", "\u00ad": "U+00AD", "\u2060": "U+2060"}
LONG_DASH_BULLETS = {"–", "—", "―", "\uf02d"}  # –, —, ―, gạch của font Symbol
TYPED_BULLET = __import__("re").compile(r"^\s*[-–—•+*·▪●]\s")


def _prose_module():
    """check.py của skill humanize-writing: cùng thư mục (bản cũ) hoặc thư mục skill bên cạnh."""
    here = os.path.dirname(os.path.abspath(__file__))
    for base in dict.fromkeys((here, os.path.dirname(os.path.realpath(__file__)))):
        for d in (base, os.path.join(base, "..", "..", "humanize-writing", "scripts")):
            if os.path.exists(os.path.join(d, "check.py")):
                sys.path.insert(0, d)
                import check
                return check
    return None


def check(path, profile="thesis"):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from word_style import PROFILES
    prof = PROFILES[profile]
    doc = docx.Document(path)
    issues = []
    add = lambda code, msg: issues.append((code, msg))

    # F1: màu chữ đặt trực tiếp (thân, đầu trang, chân trang, chú thích) và trong những style tài liệu thực sự dùng.
    def not_black(color):
        return color is not None and ((color.get(f"{W}val") or "auto").upper() not in ("000000", "AUTO") or color.get(f"{W}themeColor"))

    parts = [doc.element] + [s.header._element for s in doc.sections] + [s.footer._element for s in doc.sections]
    used = set()
    for root in parts:
        for c in root.iter(f"{W}color"):
            if not_black(c):
                add("F1", f"Chữ màu {c.get(f'{W}val')} {c.get(f'{W}themeColor') or ''}: {text(c.getparent().getparent())[:50]!r}")
                break
        for tag in ("pStyle", "rStyle", "tblStyle"):
            used |= {e.get(f"{W}val") for e in root.iter(f"{W}{tag}")}
    used.add("Normal")
    for sid in sorted(used):
        for st in style_chain(doc, sid):
            c = st.find(f"{W}rPr/{W}color")
            if not_black(c):
                add("F1", f"Style {st.get(f'{W}styleId')} có màu chữ {c.get(f'{W}val')} {c.get(f'{W}themeColor') or ''}")
                break

    # F1, F2: style Normal và Heading.
    counts = {}
    for p in doc.paragraphs:
        if len(p.text) > 80:
            counts[p.style.name] = counts.get(p.style.name, 0) + 1
    normal = doc.styles[max(counts, key=counts.get)] if counts else doc.styles["Normal"]
    defaults = doc.styles.element.find(f"{W}docDefaults/{W}rPrDefault/{W}rPr/{W}rFonts")
    if normal.font.name is None and defaults is not None:
        normal.font.name = defaults.get(f"{W}ascii")
    if (normal.font.name or "").lower() != FONT.lower():
        add("F1", f"{normal.name} (style thân bài) dùng font {normal.font.name!r}, không phải {FONT}")
    pf = normal.paragraph_format
    if pf.alignment is None or pf.alignment != 3:  # 3 = JUSTIFY
        add("F2", f"{normal.name} (style thân bài) không căn đều hai bên (alignment = {pf.alignment})")
    lo, hi = prof["line_range"]
    line = pf.line_spacing if isinstance(pf.line_spacing, float) else None  # số đo pt (Exactly) thì không so được
    if pf.line_spacing is None or (line is not None and not lo - 0.01 <= line <= hi + 0.01):
        add("F2", f"{normal.name} (style thân bài) giãn dòng {pf.line_spacing}, bộ {profile} cần {lo}–{hi}")
    if pf.space_after is None or round(pf.space_after.pt) < 6:
        add("F2", f"{normal.name} (style thân bài) cách sau đoạn {pf.space_after.pt if pf.space_after else None} pt, cần từ 6 pt")
    if prof["size_range"] and normal.font.size and not prof["size_range"][0] <= normal.font.size.pt <= prof["size_range"][1]:
        add("F1", f"{normal.name} (style thân bài) cỡ {normal.font.size.pt:g} pt, bộ {profile} cần {prof['size_range'][0]}–{prof['size_range'][1]}")
    if profile == "admin":  # NĐ 30/2020 Phụ lục I, Mục I.1 và I.3: A4; lề trên, dưới 20–25, trái 30–35, phải 15–20 mm
        for s in doc.sections:
            w, h = round(s.page_width.mm), round(s.page_height.mm)
            if sorted((w, h)) != [210, 297]:
                add("F1", f"Khổ giấy {w} x {h} mm, NĐ 30 quy định A4 (210 x 297 mm)")
            for side, val, a, b in (("trên", s.top_margin, 20, 25), ("dưới", s.bottom_margin, 20, 25),
                                    ("trái", s.left_margin, 30, 35), ("phải", s.right_margin, 15, 20)):
                if not a - 0.5 <= val.mm <= b + 0.5:
                    add("F1", f"Lề {side} {val.mm:.1f} mm, NĐ 30 quy định {a}–{b} mm")
    for level in (1, 2, 3) if prof["levels"] else ():
        try:
            st = doc.styles[f"Heading {level}"]
        except KeyError:
            add("F3", f"Thiếu style Heading {level}")
            continue
        fonts = st.element.find(f"{W}rPr/{W}rFonts")
        if fonts is not None and (fonts.get(f"{W}asciiTheme") or fonts.get(f"{W}hAnsiTheme")):
            add("F1", f"Heading {level} còn lấy font theo theme (asciiTheme), không phải {FONT}")
        if st.element.find(f"{W}pPr/{W}numPr/{W}numId") is None:
            add("F3", f"Heading {level} chưa gắn danh sách đa cấp (số chương, mục phải do Word đánh)")

    # Đoạn trong thân bài, sau tiêu đề đầu tiên.
    body = doc.element.body
    started = not prof["levels"]  # admin: không có trang bìa, kiểm từ đầu
    section_portrait = []
    paragraphs = []
    for el in body.iter(f"{W}p"):
        paragraphs.append(el)
    sect_orients = []
    for el in paragraphs:
        sp = el.find(f"{W}pPr/{W}sectPr")
        if sp is not None:
            sect_orients.append(sp)
    sect_orients.append(body.find(f"{W}sectPr"))
    sect_index = 0

    def section_info(sp):
        pg = sp.find(f"{W}pgSz")
        mar = sp.find(f"{W}pgMar")
        w, h = int(pg.get(f"{W}w")), int(pg.get(f"{W}h"))
        left, right = int(mar.get(f"{W}left", 1440)), int(mar.get(f"{W}right", 1440))
        return w > h, (w - left - right) / 1440  # ngang?, bề rộng khổ chữ (inch)

    rels = doc.part.rels
    manual_number = __import__("re").compile(r"^(CHƯƠNG\s+\d+|\d+(\.\d+)+\.?\s)", __import__("re").IGNORECASE)
    for el in paragraphs:
        in_table = any(a.tag == f"{W}tc" for a in el.iterancestors())
        sid = para_style_id(el)
        sname = style_name(doc, sid)
        outline = inherited(doc, el, f"{W}outlineLvl")
        is_heading = any(sname.startswith(h) for h in HEADINGS) or sid.lower().startswith("heading") or             (outline is not None and outline.get(f"{W}val") not in ("9", None))
        if is_heading and sname.startswith("heading"):
            started = True
        landscape, width_in = section_info(sect_orients[min(sect_index, len(sect_orients) - 1)])
        if el.find(f"{W}pPr/{W}sectPr") is not None:
            sect_index += 1
        if not started:
            continue
        tbl = next((a for a in el.iterancestors() if a.tag == f"{W}tbl"), None)
        if sname.startswith(LAYOUT_STYLE) or (tbl is not None and layout_table(tbl)):
            continue
        t = text(el).strip()
        fill = inherited(doc, el, f"{W}shd")
        fonts = {(run_font(doc, r, el) or FONT).lower() for r in el.iter(f"{W}r") if text(r).strip()}
        is_code = bool(fonts) and fonts <= MONO
        if fill is not None and (fill.get(f"{W}fill") or "auto").upper() not in ("AUTO", "FFFFFF") and not is_code:
            add("F5", f"Đoạn có nền màu {fill.get(f'{W}fill')} mà không phải mã nguồn: {t[:50]!r}")
        if is_code and (fill is None or (fill.get(f"{W}fill") or "").upper() not in CODE_FILL):
            pass  # mã không nền là được
        for f in fonts - MONO:
            if f != FONT.lower():
                add("F1", f"Font {f!r} trong đoạn: {t[:50]!r}")
                break
        if is_heading:
            if sname.startswith("heading") and manual_number.match(t) and el.find(f"{W}pPr/{W}numPr") is None:
                add("F3", f"Tiêu đề gõ số tay (Word đã đánh số): {t[:50]!r}")
            continue
        has_drawing = el.find(f".//{W}drawing") is not None
        bold_runs = [text(r) for r in el.iter(f"{W}r") if text(r).strip() and is_bold(doc, r, el)]
        first_row = in_table and next((a for a in el.iterancestors() if a.tag == f"{W}tr"), None) is not None and \
            next(a for a in el.iterancestors() if a.tag == f"{W}tbl").find(f"{W}tr") is next(a for a in el.iterancestors() if a.tag == f"{W}tr")
        if bold_runs and not first_row and not CAPTION.match(t):
            add("F8", f"In đậm ngoài tiêu đề: {bold_runs[0][:40]!r} trong {t[:50]!r}")
        if not in_table and not has_drawing and t and not is_code and not CAPTION.match(t) and not REFERENCE.match(t):
            jc = inherited(doc, el, f"{W}jc")
            if jc is None or jc.get(f"{W}val") != "both":
                add("F2", f"Đoạn nội dung không căn đều hai bên ({jc.get(f'{W}val') if jc is not None else 'left'}): {t[:50]!r}")
        if has_drawing:
            for blip in el.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}blip"):
                rid = blip.get(qn("r:embed"))
                ext = next(el.iter("{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}extent"), None)
                if rid not in rels or ext is None:
                    continue
                img = Image.from_blob(rels[rid].target_part.blob)
                ratio = img.px_width / img.px_height
                shown_in = int(ext.get("cx")) / 914400
                if img.px_width >= 1000 and shown_in < 0.6 * width_in:
                    add("F6", f"Ảnh {img.px_width}x{img.px_height} px chỉ rộng {shown_in:.1f} in trên khổ chữ {width_in:.1f} in: có thể khó đọc")

    # F6: không quay trang. Sơ đồ rộng thì vẽ lại theo chiều dọc hoặc tách hình.
    n_land = sum(section_info(sp)[0] for sp in sect_orients if sp is not None)
    if n_land and not prof["landscape_ok"]:
        add("F6", f"{n_land} section trang ngang: giữ mọi trang dọc, vẽ lại sơ đồ rộng theo chiều dọc hoặc tách thành nhiều hình")

    # F9: gạch đầu dòng ngắn, do Word đánh, thụt vừa phải.
    try:
        numbering = doc.part.numbering_part.element
    except NotImplementedError:  # tệp không có numbering.xml
        numbering = None
    used_nums = {e.get(f"{W}val") for e in body.iter(f"{W}numId")}
    for sid in used:
        for st in style_chain(doc, sid):
            e = st.find(f"{W}pPr/{W}numPr/{W}numId")
            if e is not None:
                used_nums.add(e.get(f"{W}val"))
    if numbering is not None:
        abstract_of = {n.get(f"{W}numId"): n.find(f"{W}abstractNumId").get(f"{W}val") for n in numbering.findall(f"{W}num")}
        for a in numbering.findall(f"{W}abstractNum"):
            if a.get(f"{W}abstractNumId") not in {abstract_of.get(n) for n in used_nums}:
                continue
            for lvl in a.findall(f"{W}lvl"):
                fmt, txt = lvl.find(f"{W}numFmt"), lvl.find(f"{W}lvlText")
                if fmt is None or fmt.get(f"{W}val") != "bullet" or txt is None:
                    continue
                ch = txt.get(f"{W}val") or ""
                ind = lvl.find(f"{W}pPr/{W}ind")
                left = int(ind.get(f"{W}left") or ind.get(f"{W}start") or 0) if ind is not None else 0
                if ch in LONG_DASH_BULLETS:
                    add("F9", f"Gạch đầu dòng là {ch!r} (gạch dài): dùng gạch ngắn \"-\" hoặc \"•\"")
                if left > 1440 and lvl.get(f"{W}ilvl") == "0":
                    add("F9", f"Danh sách cấp 1 thụt {left / 567:.1f} cm: chữ của gạch đầu dòng nên cách lề không quá 2,5 cm")
    for el in paragraphs:
        t = text(el)
        tbl = next((a for a in el.iterancestors() if a.tag == f"{W}tbl"), None)
        if style_name(doc, para_style_id(el)).startswith(LAYOUT_STYLE) or (tbl is not None and layout_table(tbl)):
            if t.lstrip().startswith("- "):  # NĐ 30 II.9.d: nơi nhận có gạch đầu dòng gõ đúng như mẫu
                t = t.lstrip()[2:]
        if TYPED_BULLET.match(t) and inherited(doc, el, f"{W}numPr") is None and                 not ({(run_font(doc, r, el) or FONT).lower() for r in el.iter(f"{W}r") if text(r).strip()} <= MONO):
            add("F9", f"Gõ tay ký tự đầu dòng thay vì dùng danh sách của Word: {t[:50]!r}")
        bad = sorted({INVISIBLE[c] for c in t if c in INVISIBLE})
        if bad:
            add("C8", f"Ký tự ẩn {', '.join(bad)} (máy kiểm tra coi là dấu hiệu văn máy): {t.replace(chr(0x200b), '|')[:50]!r}")
        fonts = {(run_font(doc, r, el) or FONT).lower() for r in el.iter(f"{W}r") if text(r).strip()}
        if ('"' in t or "'" in t) and not REFERENCE.match(t) and not (fonts and fonts <= MONO) and not any(
                a.tag == f"{W}tc" for a in el.iterancestors()):
            add("C2", f"Ngoặc thẳng trong tài liệu Word (Word tự đổi thành “ ” khi gõ): {t[:50]!r}")

    # F11: thuộc tính tệp không để lộ công cụ sinh ra tệp.
    cp = doc.core_properties
    for field in ("author", "last_modified_by", "comments", "title", "subject", "keywords"):
        v = getattr(cp, field) or ""
        if "python-docx" in v.lower() or "docx4j" in v.lower() or "generated" in v.lower():
            add("F11", f"Thuộc tính tệp {field} = {v!r}: đặt tên người viết, xoá chú thích của công cụ")
    if not (cp.author or "").strip():
        add("F11", "Thuộc tính tệp chưa có tác giả")

    # Văn phong: máy quét check.py trên chữ của tệp (bỏ khối mã).
    prose = _prose_module()
    if prose is None:
        print("Không thấy check.py của skill humanize-writing: bỏ qua phần quét văn phong.", file=sys.stderr)
    else:
        texts = []
        for el in paragraphs:
            fonts = {(run_font(doc, r, el) or FONT).lower() for r in el.iter(f"{W}r") if text(r).strip()}
            texts.append("" if fonts and fonts <= MONO else text(el))
        for no, code, hit in prose.scan(texts):
            if code == "C8":  # đã báo một lần cho mỗi đoạn ở trên
                continue
            add(code, f"Văn phong: {hit!r} trong {texts[no - 1][:60]!r}")
        for code, msg in prose.rhythm(texts):
            add(code, msg)

    # F4, F7: bảng.
    for ti, tbl in enumerate(doc.tables, 1):
        trs = tbl._tbl.findall(f"{W}tr")
        if not trs or layout_table(tbl._tbl):
            continue
        if len(trs) == 1 and len(trs[0].findall(f"{W}tc")) == 1:
            # Bảng một ô là một khung (hộp lệnh, ô lưu ý): chỉ khối mã nguồn được tô nền.
            tc = trs[0].find(f"{W}tc")
            fills = {(e.get(f"{W}fill") or "auto").upper() for e in tc.iter(f"{W}shd")} - {"AUTO", "FFFFFF"}
            fonts = {(run_font(doc, r, p) or FONT).lower() for p in tc.iter(f"{W}p") for r in p.iter(f"{W}r") if text(r).strip()}
            if fills and not (fonts and fonts <= MONO):
                add("F5", f"Khung (bảng {ti}) có nền {sorted(fills)[0]} mà không phải mã nguồn: {text(tc).strip()[:50]!r}")
            continue
        for tc in trs[0].findall(f"{W}tc"):
            for p in tc.findall(f"{W}p"):
                t = text(p).strip()
                if not t:
                    continue
                jc = inherited(doc, p, f"{W}jc")
                if jc is None or jc.get(f"{W}val") != "center":
                    add("F4", f"Bảng {ti}: ô tiêu đề {t!r} chưa căn giữa")
                if not all(is_bold(doc, r, p) for r in p.iter(f"{W}r") if text(r).strip()):
                    add("F4", f"Bảng {ti}: ô tiêu đề {t!r} chưa in đậm")
        for shd in tbl._tbl.iter(f"{W}shd"):
            if (shd.get(f"{W}fill") or "auto").upper() not in ("AUTO", "FFFFFF"):
                add("F4", f"Bảng {ti} có ô tô nền {shd.get(f'{W}fill')}")
                break
        size = doc.styles["Normal"].font.size
        pt = size.pt if size else 12
        for ri, tr in enumerate(trs):
            for tc in tr.findall(f"{W}tc"):
                tcw = tc.find(f"{W}tcPr/{W}tcW")
                if tcw is None or tcw.get(f"{W}type") != "dxa":
                    continue
                avail = int(tcw.get(f"{W}w")) / 20 - 10.8  # Word's cell margins: 0.19 cm a side
                for p in tc.findall(f"{W}p"):
                    t = text(p).strip()
                    sz = next((r.find(f"{W}rPr/{W}sz") for r in p.iter(f"{W}r") if r.find(f"{W}rPr/{W}sz") is not None), None)
                    if sz is None:
                        sz = next((st.find(f"{W}rPr/{W}sz") for st in style_chain(doc, para_style_id(p)) if st.find(f"{W}rPr/{W}sz") is not None), None)
                    cell_pt = int(sz.get(f"{W}val")) / 2 if sz is not None else pt
                    bold = any(is_bold(doc, r, p) for r in p.iter(f"{W}r") if text(r).strip())
                    n, last = lines(t, avail, cell_pt, bold)
                    if n >= 2 and last == 1 and len(t.split()) >= 3:
                        add("F7", f"Bảng {ti}: ô {t[:50]!r} xuống dòng còn một chữ (ô rộng {avail:.0f} pt)")
                    elif ri == 0 and n >= 2 and len(words_of(t)) <= 2:
                        add("F7", f"Bảng {ti}: tiêu đề cột {t!r} bị tách hai dòng")
                    parts = [x for w in words_of(t) for x in __import__("re").split(r"(?<=-)(?=.)", w)]  # Word ngắt sau "-"
                    if any(width_pt(x, cell_pt, bold) > avail for x in parts):
                        add("F7", f"Bảng {ti}: chữ dài hơn bề rộng ô, bị bẻ giữa từ: {t[:50]!r}")
    return issues


def selftest():
    import tempfile
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import word_style as ws
    tmp = tempfile.mkdtemp()
    wide = os.path.join(tmp, "wide.png")
    _png(wide, 3000, 1000)

    for profile in ("thesis", "report", "guide"):
        good = docx.Document()
        ws.setup(good, profile)
        good.add_paragraph("Tổng quan", style="Heading 1")
        good.add_paragraph("Bài toán", style="Heading 2")
        good.add_paragraph("Nội dung căn đều hai bên, chữ đen.")
        ws.table(good, [["Việc", "Ai làm", "Cách kiểm tra"], ["Cắm dây LAN vào máy chủ", "Người ở trường", "Máy có Internet"]], caption="Bảng 1.1. Việc")
        # Tiêu đề cột vừa khít bề rộng ô: làm tròn sang twip không được đẩy nó xuống dòng.
        ws.table(good, [["Bộ", "Dùng cho", "Cỡ chữ", "Giãn dòng", "Đánh số tiêu đề"],
                        ["thesis", "Đồ án, khóa luận, luận văn", "13 pt", "1,5", "CHƯƠNG 1: / 1.1 / 1.1.1"],
                        ["report", "Báo cáo, đề xuất trong công ty", "13 pt", "1,5", "1. / 1.1. / 1.1.1."],
                        ["admin", "Văn bản hành chính", "14 pt", "Đơn", "Gõ tay theo Nghị định"]], caption="Bảng 1.2. Bộ")
        ws.code(good, ["dotnet build"])
        ws.picture(good, wide, "Hình 1.1. Sơ đồ rộng")
        good.add_paragraph(ws.smart_quotes('Sau hình, máy chủ ghi "bài làm" của thí sinh.'))
        ws.bullets(good, ["Máy chủ chạy MySQL", "Máy thí sinh chỉ cần trình duyệt"])
        ws.steps(good, ["Mở trang quản trị", "Bấm Tạo kỳ thi"])
        ws.metadata(good, author="Người viết", title="Mẫu")
        path = os.path.join(tmp, f"good-{profile}.docx")
        good.save(path)
        found = check(path, profile)
        assert found == [], (profile, found)
        assert round(good.sections[0].page_width.mm) == 210 and round(good.sections[0].left_margin.mm) == 30

    admin = docx.Document()
    ws.setup(admin, "admin")
    ws.admin_header(admin, "Cục Văn thư và Lưu trữ nhà nước", "Số: 05/VTLTNN-VP", "Hà Nội, ngày 05 tháng 01 năm 2020",
                    parent="Bộ Nội vụ", vv="nâng bậc lương năm 2019", to=["Vụ Tổ chức cán bộ", "Văn phòng Bộ"])
    admin.add_paragraph("Văn phòng Bộ đề nghị các đơn vị gửi danh sách trước ngày 15 tháng 01 năm 2020.")
    admin.add_paragraph("Điều 1. Phạm vi điều chỉnh", style="Heading 3")
    ws.admin_signature(admin, ["KT. Cục trưởng", "Phó Cục trưởng"], "Nguyễn Văn A", ["Như trên"], "VT, VP")
    ws.metadata(admin, author="Người viết", title="Công văn")
    path = os.path.join(tmp, "good-admin.docx")
    admin.save(path)
    found = check(path, "admin")
    assert found == [], found
    hdr = admin.sections[0]
    assert hdr.different_first_page_header_footer and "PAGE" in hdr.header._element.xml

    # Mẫu thắng: setup(template=True) không đổi style mẫu đã có.
    tpl = docx.Document()
    tpl.styles["Normal"].font.name = "Arial"
    tpl.styles["Normal"].paragraph_format.line_spacing = 1.0
    ws.setup(tpl, "thesis", template=True)
    assert tpl.styles["Normal"].font.name == "Arial" and tpl.styles["Normal"].paragraph_format.line_spacing == 1.0
    assert tpl.styles["Code"] is not None

    bad = docx.Document()
    bad.add_paragraph("Tổng quan", style="Heading 1")  # style gốc: màu xanh, font theme, không đánh số
    p = bad.add_paragraph("Nội dung có ")
    p.add_run("chữ đậm").bold = True
    t = bad.add_table(rows=2, cols=2)
    t.cell(0, 0).text = "Việc"
    bad.add_paragraph("- gạch gõ tay, đường\u200bdẫn, ngoặc \"thẳng\"")
    ws.bullets(bad, ["mục"], char="–")
    bad.core_properties.author = "python-docx"
    bad_path = os.path.join(tmp, "bad.docx")
    bad.save(bad_path)
    codes = {c for c, _ in check(bad_path)}
    assert {"F1", "F2", "F3", "F4", "F8", "F9", "F11", "C2", "C8"} <= codes, codes
    admin_msgs = [m for c, m in check(bad_path, "admin") if c == "F1"]
    assert any("Lề phải" in m for m in admin_msgs) and any("A4" in m for m in admin_msgs), admin_msgs
    print("selftest ok")


def _png(path, w, h):
    import struct
    import zlib
    raw = b"".join(b"\x00" + b"\xff" * (w * 3) for _ in range(h))
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def main(argv):
    if argv == ["--selftest"]:
        return selftest()
    profile = "thesis"
    if argv[:1] == ["--profile"]:
        profile, argv = argv[1], argv[2:]
    total = 0
    for path in argv:
        for code, msg in check(path, profile):
            print(f"{path}: [{code}] {msg}")
            total += 1
    print(f"{total} chỗ cần xem lại (bộ định dạng {profile}).", file=sys.stderr)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main(sys.argv[1:])
