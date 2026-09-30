"""Build the internship report (.docx) from the college template and content.py.

    python build_report.py

The template's cover page, certificate pages, borders, header and footer are kept.
Personal details (<Name of Student>, <Enrolment No.>, <Name of Internal guide>, date,
branch) are left as placeholders to be filled in by hand.

Two passes: the document is built, rendered to PDF with LibreOffice to find the page
of every heading, then rebuilt with those page numbers in the contents. In Word you
can also right-click the contents and choose "Update Field" at any time.
"""
import copy
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image

import content as C

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE / "template" / "Summer_Internship_Report_Format_2026.docx"
OUT = HERE / "PinkTax_Internship_Report.docx"
MAX_FIG_H = 3.55  # inches
BULLET_ABS, NUMBER_ABS = 90, 91


# ============================================================================ helpers
def el(tag, **attrs):
    e = OxmlElement(tag)
    for k, v in attrs.items():
        e.set(qn(k), str(v))
    return e


class Builder:
    """Creates content at the end of the body, then moves it before `anchor`."""

    def __init__(self, doc):
        self.doc = doc
        self.anchor = None
        self.num_counter = 200
        self.headings = []  # (level, text)
        self._setup_numbering()
        self._setup_styles()

    # ---------------------------------------------------------------- setup
    def _setup_numbering(self):
        numbering = self.doc.part.numbering_part.element
        first_num = numbering.find(qn("w:num"))

        def abstract(aid, fmt, text, font=None):
            a = el("w:abstractNum", **{"w:abstractNumId": aid})
            a.append(el("w:multiLevelType", **{"w:val": "singleLevel"}))
            lvl = el("w:lvl", **{"w:ilvl": 0})
            lvl.append(el("w:start", **{"w:val": 1}))
            lvl.append(el("w:numFmt", **{"w:val": fmt}))
            lvl.append(el("w:lvlText", **{"w:val": text}))
            lvl.append(el("w:lvlJc", **{"w:val": "left"}))
            ppr = el("w:pPr")
            ppr.append(el("w:ind", **{"w:left": 720, "w:hanging": 360}))
            lvl.append(ppr)
            if font:
                rpr = el("w:rPr")
                rpr.append(el("w:rFonts", **{"w:ascii": font, "w:hAnsi": font, "w:hint": "default"}))
                lvl.append(rpr)
            a.append(lvl)
            first_num.addprevious(a)

        abstract(BULLET_ABS, "bullet", "•", "Times New Roman")
        abstract(NUMBER_ABS, "decimal", "%1.")
        self.numbering = numbering
        self.bullet_num = self._new_num(BULLET_ABS)

    def _new_num(self, abstract_id):
        self.num_counter += 1
        n = el("w:num", **{"w:numId": self.num_counter})
        n.append(el("w:abstractNumId", **{"w:val": abstract_id}))
        ov = el("w:lvlOverride", **{"w:ilvl": 0})
        ov.append(el("w:startOverride", **{"w:val": 1}))
        n.append(ov)
        self.numbering.append(n)
        return self.num_counter

    def _setup_styles(self):
        st = self.doc.styles
        for name, size, align, before, after in (("Heading 1", 16, WD_ALIGN_PARAGRAPH.CENTER, 0, 14),
                                                 ("Heading 2", 14, WD_ALIGN_PARAGRAPH.LEFT, 10, 6)):
            s = st[name]
            s.font.size = Pt(size)
            s.font.bold = True
            s.font.italic = False
            s.font.small_caps = False
            s.font.name = "Times New Roman"
            s.font.color.rgb = RGBColor(0, 0, 0)
            pf = s.paragraph_format
            pf.alignment = align
            pf.left_indent = Inches(0)
            pf.first_line_indent = Inches(0)
            pf.space_before = Pt(before)
            pf.space_after = Pt(after)
            pf.keep_with_next = True

    # ---------------------------------------------------------------- primitives
    def _place(self, element):
        if self.anchor is not None:
            self.anchor.addprevious(element)

    def para(self, style="Normal1"):
        p = self.doc.add_paragraph(style=style)
        self._place(p._p)
        return p

    def rich(self, p, text, size=12, italic=False, color=None):
        for tok in re.split(r"(\*\*.+?\*\*|\*[^*]+?\*)", text):
            if not tok:
                continue
            bold = tok.startswith("**")
            ital = italic or (tok.startswith("*") and not bold)
            r = p.add_run(tok.strip("*") if (bold or ital and tok.startswith("*")) else tok)
            r.bold = bold or None
            r.italic = ital or None
            r.font.size = Pt(size)
            if color:
                r.font.color.rgb = color
        return p

    def body(self, text, align=WD_ALIGN_PARAGRAPH.JUSTIFY, size=12, after=6, spacing=1.3):
        p = self.para()
        pf = p.paragraph_format
        pf.alignment = align
        pf.space_after = Pt(after)
        pf.line_spacing = spacing
        return self.rich(p, text, size=size)

    def list_(self, items, numbered=False):
        num_id = self._new_num(NUMBER_ABS) if numbered else self.bullet_num
        for it in items:
            p = self.body(it, after=3)
            ppr = p._p.get_or_add_pPr()
            numpr = el("w:numPr")
            numpr.append(el("w:ilvl", **{"w:val": 0}))
            numpr.append(el("w:numId", **{"w:val": num_id}))
            ppr.append(numpr)
            ppr.append(el("w:ind", **{"w:left": 720, "w:hanging": 360}))
        self.body("", after=0, spacing=0.6)

    def heading(self, text, level):
        p = self.para(style="Heading 1" if level == 1 else "Heading 2")
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(16 if level == 1 else 14)
        r.font.color.rgb = RGBColor(0, 0, 0)
        self.headings.append((level, text))
        return p

    def h3(self, text):
        p = self.para()
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        r = p.add_run(text)
        r.bold = True
        r.font.size = Pt(12.5)
        return p

    def page_break(self):
        p = self.para()
        p.add_run().add_break(WD_BREAK.PAGE)
        return p

    def figure(self, path, caption, width, max_h=MAX_FIG_H):
        path = (HERE / path).resolve()
        w_px, h_px = Image.open(path).size
        width = min(width, max_h * w_px / h_px)
        p = self.para()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        p.paragraph_format.space_before = Pt(4)
        p.add_run().add_picture(str(path), width=Inches(width))
        cp = self.para(style="Caption")
        cp.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.space_after = Pt(8)
        r = cp.add_run(caption)
        r.italic = True
        r.font.size = Pt(10.5)

    def table(self, caption, header, rows, widths):
        cp = self.para()
        cp.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.paragraph_format.keep_with_next = True
        cp.paragraph_format.space_before = Pt(4)
        r = cp.add_run(caption)
        r.bold = True
        r.font.size = Pt(11)
        t = self.doc.add_table(rows=1 + len(rows), cols=len(header))
        t.style = self.doc.styles["Table Grid"]
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        self._place(t._tbl)
        for i, row in enumerate([header] + rows):
            for j, val in enumerate(row):
                cell = t.cell(i, j)
                cell.width = Inches(widths[j])
                cp_ = cell.paragraphs[0]
                cp_.paragraph_format.space_after = Pt(1)
                self.rich(cp_, str(val), size=10.5)
                if i == 0:
                    for run in cp_.runs:
                        run.bold = True
                    tcpr = cell._tc.get_or_add_tcPr()
                    tcpr.append(el("w:shd", **{"w:val": "clear", "w:color": "auto", "w:fill": "E7E6E6"}))
                elif row[0] == "Total":
                    for run in cp_.runs:
                        run.bold = True
        t.autofit = False
        for j, w in enumerate(widths):
            t.columns[j].width = Inches(w)
        tblpr = t._tbl.tblPr
        tblpr.append(el("w:tblW", **{"w:w": int(sum(widths) * 1440), "w:type": "dxa"}))
        tblpr.append(el("w:tblLayout", **{"w:type": "fixed"}))
        for row in t.rows[:-1]:  # keep small tables on one page
            for cell in row.cells:
                for cpar in cell.paragraphs:
                    cpar.paragraph_format.keep_with_next = True
        for row in t.rows:
            row._tr.get_or_add_trPr().append(el("w:cantSplit"))
        trpr = t.rows[0]._tr.get_or_add_trPr()
        trpr.append(el("w:tblHeader"))
        self.body("", after=2, spacing=0.8)

    def blocks(self, items):
        for item in items:
            kind = item[0]
            if kind == "h1":
                self.heading(item[1], 1)
            elif kind == "h2":
                self.heading(item[1], 2)
            elif kind == "h3":
                self.h3(item[1])
            elif kind == "p":
                self.body(item[1])
            elif kind == "bullets":
                self.list_(item[1])
            elif kind == "numbers":
                self.list_(item[1], numbered=True)
            elif kind == "fig":
                self.figure(*item[1:])
            elif kind == "table":
                self.table(item[1], item[2], item[3], item[4])
            elif kind == "pagebreak":
                self.page_break()


def set_page_break_before(p):
    p.paragraph_format.page_break_before = True


def add_field(run_parent_p, instr):
    """Append a simple field (e.g. PAGE) to a paragraph."""
    r1 = el("w:r")
    r1.append(el("w:fldChar", **{"w:fldCharType": "begin"}))
    r2 = el("w:r")
    it = el("w:instrText", **{"xml:space": "preserve"})
    it.text = f" {instr} "
    r2.append(it)
    r3 = el("w:r")
    r3.append(el("w:fldChar", **{"w:fldCharType": "separate"}))
    r4 = el("w:r")
    t = el("w:t")
    t.text = "1"
    r4.append(t)
    r5 = el("w:r")
    r5.append(el("w:fldChar", **{"w:fldCharType": "end"}))
    for r in (r1, r2, r3, r4, r5):
        run_parent_p.append(r)


PPR_ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr",
             "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens", "kinsoku", "wordWrap",
             "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd",
             "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc",
             "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr",
             "sectPr", "pPrChange"]
TBLPR_ORDER = ["tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
               "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders", "shd",
               "tblLayout", "tblCellMar", "tblLook", "tblCaption", "tblDescription"]


def schema_sort(root):
    """Put pPr / tblPr children in the order the OOXML schema requires (last duplicate wins)."""
    for tag, order in (("w:pPr", PPR_ORDER), ("w:tblPr", TBLPR_ORDER)):
        rank = {qn("w:" + n): i for i, n in enumerate(order)}
        for pr in root.iter(qn(tag)):
            kids = list(pr)
            seen = {}
            for k in kids:
                if k.tag in rank:
                    if k.tag in seen:
                        pr.remove(seen[k.tag])
                    seen[k.tag] = k
            kids = list(pr)
            kids.sort(key=lambda k: rank.get(k.tag, len(order)))
            for k in kids:
                pr.remove(k)
                pr.append(k)


# ============================================================================ build
def build(page_numbers=None):
    doc = Document(str(TEMPLATE))
    body = doc.element.body
    ch = list(body.iterchildren())
    B = Builder(doc)

    def text_of(e):
        return "".join(t.text or "" for t in e.iter(qn("w:t")))

    def find(pred, start=0):
        for i in range(start, len(ch)):
            if pred(ch[i]):
                return i
        raise ValueError("not found")

    # ---- cover page title ------------------------------------------------------
    i_title = find(lambda e: "Topic Name" in text_of(e))
    runs = ch[i_title].findall(qn("w:r"))
    for r in runs:
        t = r.find(qn("w:t"))
        if t is not None and t.text == "Topic Name":
            t.text = C.TITLE
        for sz in r.iter(qn("w:sz")):
            sz.set(qn("w:val"), "40")
        for sz in r.iter(qn("w:szCs")):
            sz.set(qn("w:val"), "40")
    # remove two spacer paragraphs below the title so the longer title still fits one page
    for k in (i_title + 1, i_title + 2):
        if text_of(ch[k]).strip() == "":
            body.remove(ch[k])

    # ---- certificate -------------------------------------------------------------
    i_cert = find(lambda e: "<Title name>" in text_of(e))
    for t in ch[i_cert].iter(qn("w:t")):
        if t.text and "<Title name>" in t.text:
            t.text = t.text.replace("<Title name>", C.TITLE)

    # ---- abstract ----------------------------------------------------------------
    i_abs = find(lambda e: text_of(e).strip() == "ABSTRACT")
    i_abs_end = find(lambda e: e.tag == qn("w:p") and 'w:type="page"' in e.xml.replace("'", '"'), i_abs)
    for e in ch[i_abs + 1:i_abs_end]:
        body.remove(e)
    B.anchor = ch[i_abs_end]
    B.body("", after=4)
    for para in C.ABSTRACT:
        B.body(para, spacing=1.25, after=7)

    # ---- introduction --------------------------------------------------------------
    i_int = find(lambda e: text_of(e).strip() == "Introduction", i_abs_end)
    i_tbl = find(lambda e: e.tag == qn("w:tbl"), i_int)
    for e in ch[i_abs_end + 1:i_int]:
        body.remove(e)
    for e in ch[i_int + 1:i_tbl]:
        body.remove(e)
    for r in ch[i_int].iter(qn("w:r")):
        rpr = r.find(qn("w:rPr"))
        if rpr is not None:
            rpr.append(el("w:b"))
    B.anchor = ch[i_tbl]
    B.body("", after=2)
    for para in C.INTRODUCTION:
        B.body(para, spacing=1.25, after=7)
    B.page_break()

    # ---- contents ------------------------------------------------------------------
    i_sdt = find(lambda e: e.tag == qn("w:sdt"), i_tbl)
    sect2_p = ch[i_sdt + 1]  # paragraph carrying section 2's sectPr
    body.remove(ch[i_tbl])
    body.remove(ch[i_sdt])
    for r in sect2_p.findall(qn("w:r")):
        sect2_p.remove(r)
    B.anchor = sect2_p
    build_contents(B, page_numbers)

    # ---- main body (section 3) -------------------------------------------------
    i_sect2 = list(body.iterchildren()).index(sect2_p)
    for e in list(body.iterchildren())[i_sect2 + 1:]:
        if e.tag != qn("w:sectPr"):
            body.remove(e)
    B.anchor = None
    B.headings = []
    B.blocks(C.CHAPTER1)
    for d, day in enumerate(C.DAYS):
        figs = [b for b in day if b[0] == "fig"]
        if len(figs) == 2 and d not in (1, 7):
            # balance long days: first figure right after the activities, the second at the end
            rest = [b for b in day if b[0] != "fig"]
            i_after = next(i for i, b in enumerate(rest) if b[0] == "bullets") + 1
            day = rest[:i_after] + [figs[0]] + rest[i_after:] + [figs[1]]
        if d == 0:
            h = B.heading("Chapter 2: What I Learned during Internship", 1)
            set_page_break_before(h)
            B.blocks(day)
        else:
            first = B.heading(day[0][1], 2)
            set_page_break_before(first)
            B.blocks(day[1:])
    B.blocks(C.CONCLUSION)
    h = B.heading("References", 1)
    set_page_break_before(h)
    for ref in C.REFERENCES:
        p = B.body(ref, align=WD_ALIGN_PARAGRAPH.LEFT, after=6, spacing=1.15)
        pf = p.paragraph_format
        pf.left_indent = Inches(0.4)
        pf.first_line_indent = Inches(-0.4)
    # chapter 1 starts on a new page too (it follows the contents section break already)
    heads = [p for p in doc.paragraphs if p.style.name in ("Heading 1",)]
    for p in heads:
        if p.text.startswith("Chapter 3"):
            set_page_break_before(p)

    # ---- header / footer of section 3 ----------------------------------------------
    s3 = doc.sections[-1]
    for p in s3.header.paragraphs:
        for t in p._p.iter(qn("w:t")):
            if t.text and "201260107006" in t.text:
                t.text = t.text.replace("201260107006", "<Enrolment No.>")
    fp = s3.footer.paragraphs[0]
    fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    add_field(fp._p, "PAGE")
    sectpr = body.find(qn("w:sectPr"))
    tp = sectpr.find(qn("w:titlePg"))  # use the normal header/footer on the first page too
    if tp is not None:
        sectpr.remove(tp)
    pg = sectpr.find(qn("w:pgNumType"))
    if pg is None:
        pg = el("w:pgNumType")
        sectpr.append(pg)
    pg.set(qn("w:start"), "1")

    schema_sort(doc.element.body)
    doc.core_properties.title = C.TITLE
    doc.core_properties.author = ""
    doc.core_properties.subject = "Summer Internship (3170001)"
    doc.save(str(OUT))
    return B.headings


def build_contents(B, page_numbers):
    """Contents page: static front-matter lines + a real Word TOC field with cached entries."""
    p = B.para()
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(14)
    r = p.add_run("Contents")
    r.bold = True
    r.font.size = Pt(16)

    right_tab = 9800  # twips, inside the bordered contents page

    def line(text, page, level, bold=False, first=False, last=False):
        q = B.para()
        pf = q.paragraph_format
        pf.space_after = Pt(1 if level == 2 else 3)
        pf.space_before = Pt(0 if level == 2 else 6)
        pf.left_indent = Inches(0.35 if level == 1 else 0.85)
        ppr = q._p.get_or_add_pPr()
        tabs = el("w:tabs")
        tabs.append(el("w:tab", **{"w:val": "right", "w:leader": "dot", "w:pos": right_tab}))
        ppr.append(tabs)
        if first:
            add_raw(q, "begin")
            instr = el("w:r")
            it = el("w:instrText", **{"xml:space": "preserve"})
            it.text = ' TOC \\o "1-2" \\h \\z \\u '
            instr.append(it)
            q._p.append(instr)
            add_raw(q, "separate")
        run = q.add_run(text)
        run.bold = bold or None
        run.font.size = Pt(12 if level == 1 else 11.5)
        q.add_run("\t")
        pr = q.add_run(str(page))
        pr.bold = bold or None
        pr.font.size = Pt(12 if level == 1 else 11.5)
        if last:
            add_raw(q, "end")

    def add_raw(q, kind):
        r_ = el("w:r")
        r_.append(el("w:fldChar", **{"w:fldCharType": kind}))
        q._p.append(r_)

    line("Abstract", "I", 1)
    line("Introduction", "II", 1)
    line("Contents", "III", 1)
    entries = list(page_numbers.items()) if page_numbers else [(h, 0) for h in ENTRY_ORDER]
    for k, (text, page) in enumerate(entries):
        level = 1 if text.startswith(("Chapter", "References")) else 2
        line(text, page, level, bold=(level == 1), first=(k == 0), last=(k == len(entries) - 1))


ENTRY_ORDER = (
    [b[1] for b in C.CHAPTER1 if b[0] in ("h1", "h2")]
    + ["Chapter 2: What I Learned during Internship"]
    + [d[0][1] for d in C.DAYS]
    + [b[1] for b in C.CONCLUSION if b[0] in ("h1", "h2")]
    + ["References"]
)


# ============================================================================ pagination
def render_pdf(docx_path, outdir):
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(outdir),
                    str(docx_path)], check=True, capture_output=True)
    return Path(outdir) / (Path(docx_path).stem + ".pdf")


def find_pages(pdf):
    n = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True,
                                                         text=True).stdout).group(1))
    pages = []
    for i in range(1, n + 1):
        txt = subprocess.run(["pdftotext", "-f", str(i), "-l", str(i), "-layout", str(pdf), "-"],
                             capture_output=True, text=True).stdout
        pages.append(re.sub(r"\s+", " ", txt))
    start = next(i for i, t in enumerate(pages) if "Summer Internship (3170001)" in t)
    found = {}
    for entry in ENTRY_ORDER:
        key = re.sub(r"\s+", " ", entry)
        for i in range(start, len(pages)):
            if key in pages[i]:
                found[entry] = i - start + 1
                break
        else:
            found[entry] = "?"
    return found, n


if __name__ == "__main__":
    build()
    with tempfile.TemporaryDirectory() as tmp:
        pdf = render_pdf(OUT, tmp)
        pages, total = find_pages(pdf)
    build(pages)
    with tempfile.TemporaryDirectory() as tmp:
        pdf = render_pdf(OUT, tmp)
        pages2, total = find_pages(pdf)
        if "--pdf" in sys.argv:
            shutil.copy(pdf, HERE / "PinkTax_Internship_Report.pdf")
    if pages2 != pages:
        build(pages2)
    print(f"Saved {OUT.name}: {total} pages")
    for k, v in pages2.items():
        print(f"  {v:>3}  {k}")
