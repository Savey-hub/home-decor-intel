# -*- coding: utf-8 -*-
"""
Generate two Word versions of the 家装建材家具行业竞争情报月报:
  1) 汇报稿 (brief, 8-12 pages)  -> report_brief.docx
  2) 详报   (detail, 20-30 pages) -> report_detail.docx
Every table is followed by a natural-language description
(structure ratio + YoY direction + differentiation + action implication).
Data rule: every figure carries source; unverifiable = 待核实; no fabrication.
"""
import json, os, re, sys
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data")
CURRENT_MONTH = "2026-09"
CURRENT_MONTH_CN = "2026年9月"

def load(p):
    with open(os.path.join(D, p), encoding="utf-8") as f:
        return json.load(f)

macro    = load("macro_realestate.json")
plat     = load("platform_dynamics.json")
policy   = load("industry_policy.json")
mh       = load("v2/monthly_highlights.json")
dd       = load("sources/layerC_doudian_compass.json")
chanmama = load("sources/r6_chanmama_furniture_30d.json")
juliang  = load("sources/r6_juliangsuanshu_keywords.json")
srcidx   = load("v2/data_sources_index.json")

# ---------- CJK typography helpers ----------
EASTASIA = "微软雅黑"
EASTASIA_BODY = "宋体"

def set_cell_font(cell, size=10, bold=False, ea=EASTASIA_BODY, color=None, align=None):
    for p in cell.paragraphs:
        if align is not None:
            p.alignment = align
        if not p.runs:
            p.add_run("")
        for r in p.runs:
            r.font.size = Pt(size)
            r.font.bold = bold
            r.font.name = "Arial"
            r._element.rPr.rFonts.set(qn('w:eastAsia'), ea)
            if color:
                r.font.color.rgb = color

def style_doc_defaults(doc):
    st = doc.styles['Normal']
    st.font.name = "Arial"
    st.font.size = Pt(11)
    st.element.rPr.rFonts.set(qn('w:eastAsia'), EASTASIA_BODY)
    # 1.5 line spacing default
    pf = st.paragraph_format
    pf.line_spacing = 1.5

def _set_run_ea(run, ea):
    run.font.name = "Arial"
    rpr = run._element.get_or_add_rPr()
    rf = rpr.find(qn('w:rFonts'))
    if rf is None:
        rf = OxmlElement('w:rFonts'); rpr.append(rf)
    rf.set(qn('w:eastAsia'), ea)

def add_title(doc, text, size=22):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.font.size = Pt(size); r.font.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
    _set_run_ea(r, EASTASIA)
    return p

def add_subtitle(doc, text, size=11):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(text)
    r.font.size = Pt(size); r.font.color.rgb = RGBColor(0x66, 0x66, 0x66)
    _set_run_ea(r, EASTASIA_BODY)
    return p

def h1(doc, text):
    p = doc.add_heading(level=1)
    r = p.add_run(text)
    r.font.size = Pt(16); r.font.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
    _set_run_ea(r, EASTASIA)
    return p

def h2(doc, text):
    p = doc.add_heading(level=2)
    r = p.add_run(text)
    r.font.size = Pt(13.5); r.font.bold = True
    r.font.color.rgb = RGBColor(0x2E, 0x5B, 0x9A)
    _set_run_ea(r, EASTASIA)
    return p

def h3(doc, text):
    p = doc.add_heading(level=3)
    r = p.add_run(text)
    r.font.size = Pt(12); r.font.bold = True
    r.font.color.rgb = RGBColor(0x3F, 0x3F, 0x3F)
    _set_run_ea(r, EASTASIA)
    return p

def para(doc, text, size=11, indent=True, color=None, bold=False):
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    if indent:
        p.paragraph_format.first_line_indent = Pt(size*2)
    r = p.add_run(text)
    r.font.size = Pt(size); r.font.bold = bold
    if color: r.font.color.rgb = color
    _set_run_ea(r, EASTASIA_BODY)
    return p

def desc(doc, text):
    """Natural-language interpretation paragraph after a table (shaded)."""
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.first_line_indent = Pt(22)
    p.paragraph_format.space_before = Pt(3)
    r = p.add_run("解读：")
    r.font.size = Pt(10.5); r.font.bold = True
    r.font.color.rgb = RGBColor(0x2E, 0x5B, 0x9A)
    _set_run_ea(r, EASTASIA)
    r2 = p.add_run(text)
    r2.font.size = Pt(10.5); r2.font.color.rgb = RGBColor(0x33,0x33,0x33)
    _set_run_ea(r2, EASTASIA_BODY)
    # light shading
    shd = OxmlElement('w:shd'); shd.set(qn('w:val'),'clear'); shd.set(qn('w:fill'),'F2F6FB')
    p._p.get_or_add_pPr().append(shd)
    return p

def bullet(doc, text, size=11):
    p = doc.add_paragraph(style=None)
    p.paragraph_format.line_spacing = 1.4
    p.paragraph_format.left_indent = Pt(18)
    r = p.add_run("• " + text)
    r.font.size = Pt(size)
    _set_run_ea(r, EASTASIA_BODY)
    return p

def shade_row(row, fill="1F3864"):
    for c in row.cells:
        shd = OxmlElement('w:shd'); shd.set(qn('w:val'),'clear'); shd.set(qn('w:fill'),fill)
        c._tc.get_or_add_tcPr().append(shd)

def make_table(doc, headers, rows, widths=None, header_fill="1F3864",
               header_color=RGBColor(0xFF,0xFF,0xFF), fsize=9.5):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0]
    for i, htext in enumerate(headers):
        hdr.cells[i].text = htext
        set_cell_font(hdr.cells[i], size=fsize, bold=True, ea=EASTASIA,
                      color=header_color, align=WD_ALIGN_PARAGRAPH.CENTER)
    shade_row(hdr, header_fill)
    for r_i, rowdata in enumerate(rows):
        cells = t.add_row().cells
        for i, val in enumerate(rowdata):
            cells[i].text = str(val)
            set_cell_font(cells[i], size=fsize, bold=False, ea=EASTASIA_BODY,
                          align=WD_ALIGN_PARAGRAPH.CENTER if i>0 else WD_ALIGN_PARAGRAPH.LEFT)
        if r_i % 2 == 1:
            for c in cells:
                shd = OxmlElement('w:shd'); shd.set(qn('w:val'),'clear'); shd.set(qn('w:fill'),'F4F6F9')
                c._tc.get_or_add_tcPr().append(shd)
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    return t

def add_source_line(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run(text)
    r.font.size = Pt(8.5); r.font.italic = True
    r.font.color.rgb = RGBColor(0x88,0x88,0x88)
    _set_run_ea(r, EASTASIA_BODY)
    return p

def page_break(doc):
    doc.add_page_break()

# =========================================================
#  SHARED CONTENT PIECES
# =========================================================
ASOF = macro.get("asOf", "2026-09-16")
WINDOW_START = plat.get("windowStart", "2026-08-18")
WINDOW_END = plat.get("windowEnd", ASOF)
WINDOW = f"近30天（{WINDOW_START} 至 {WINDOW_END}）"
MONTH_LABEL = f"{CURRENT_MONTH_CN}（自然月至今）"

DATE_FIELDS = ("monthBucket", "publishDate", "effectiveDate", "date", "issueDate", "captured_at", "scrapedAt")

def _extract_month(value):
    """Return YYYY-MM from a date-like value without inferring absent dates."""
    if value is None:
        return None
    text = str(value)
    match = re.search(r"(20\d{2})[-/年](\d{1,2})(?:[-/月]|$)", text)
    if not match:
        return None
    return f"{match.group(1)}-{int(match.group(2)):02d}"

def item_month(item, effective_rule=False):
    """Classify by monthBucket, then rule-effective date, then known date fields.

    For rule records, effectiveDate wins over an earlier publication date. If a
    legacy rule lacks effectiveDate, an explicit dated effective statement is
    used before falling back to publication, issue, or capture dates.
    """
    bucket = _extract_month(item.get("monthBucket"))
    if bucket:
        return bucket
    if effective_rule:
        effective = _extract_month(item.get("effectiveDate"))
        if effective:
            return effective
        rule_text = " ".join(str(item.get(k, "")) for k in ("title", "summary"))
        match = re.search(r"(20\d{2})[-/年](\d{1,2})(?:[-/月]\d{1,2}日?)?[^。；;]{0,12}生效", rule_text)
        if match:
            return f"{match.group(1)}-{int(match.group(2)):02d}"
    for field in DATE_FIELDS[1:]:
        month = _extract_month(item.get(field))
        if month:
            return month
    return None

def in_current_month(item, effective_rule=False):
    return item_month(item, effective_rule=effective_rule) == CURRENT_MONTH

def current_items(items, effective_rule=False):
    return [item for item in items if in_current_month(item, effective_rule=effective_rule)]

def flatten_lists(mapping):
    rows = []
    for value in mapping.values():
        if isinstance(value, list):
            rows.extend(x for x in value if isinstance(x, dict))
    return rows

def dated_source_month(source, *fallback_values):
    """Classify source metadata after standard date fields have been checked."""
    month = item_month(source)
    if month:
        return month
    for value in fallback_values:
        month = _extract_month(value)
        if month:
            return month
    return None

def add_empty_month_notice(doc, subject):
    para(doc, f"本月无新增：截至{ASOF}，未取得可核实的{CURRENT_MONTH_CN}{subject}。以下不以历史数据替代。",
         indent=False, color=RGBColor(0x8A, 0x63, 0x00))

def yoy_word(v):
    """translate a numeric yoy string into Chinese direction words."""
    if v is None or v == "" or v == "待核实":
        return "待核实"
    import re
    m = re.search(r'-?\d+\.?\d*', str(v).replace(',',''))
    if not m: return str(v)
    n = float(m.group())
    if n <= -10: return f"大幅下滑（{v}）"
    if n <= -5:  return f"明显下滑（{v}）"
    if n < -0.5: return f"小幅下滑（{v}）"
    if n <= 0.5: return f"基本持平（{v}）"
    if n < 5:    return f"小幅上涨（{v}）"
    if n < 10:   return f"明显上涨（{v}）"
    return f"大幅上涨（{v}）"

# ---- cover ----
def cover(doc, subtitle):
    for _ in range(3): doc.add_paragraph()
    add_title(doc, "家装建材家具行业", 26)
    add_title(doc, "竞争情报月报", 26)
    doc.add_paragraph()
    add_subtitle(doc, subtitle, 14)
    doc.add_paragraph()
    add_subtitle(doc, f"当月窗口：{CURRENT_MONTH_CN}1日至{ASOF}；非当月资料仅列历史参考", 11)
    add_subtitle(doc, f"数据截止：{ASOF}", 11)
    add_subtitle(doc, "覆盖子行业：家具 · 装修 · 建材 · 卫浴厨房 · 全屋智能 · 全屋定制 · 灯具光源 · 电工五金", 10)
    doc.add_paragraph(); doc.add_paragraph()
    add_subtitle(doc, "数据来源：国家统计局 · CBMF/CBMCA/CBDA · 平台公告 · 抖店罗盘 · 蝉妈妈 · 巨量算数 · 上市公司公告 · 权威媒体", 9)
    add_subtitle(doc, "编制原则：当月与历史严格分区；每条数据保留来源与日期；不可核实项标『待核实』；严禁编造", 9)
    page_break(doc)

# ---- current-month classification and overview ----
def current_macro_records():
    return current_items(flatten_lists(macro.get("macro", {})))

def current_realestate_records():
    return current_items(flatten_lists(macro.get("realEstate", {})))

def current_platform_records():
    rows = []
    for platform_key, items in plat.get("platforms", {}).items():
        for item in current_items(items):
            if item.get("type") != "待核实":
                rows.append(dict(item, _platform=platform_key))
    rows.extend(dict(item, _platform="crossPlatform") for item in current_items(plat.get("crossPlatform", [])))
    return rows

def current_policy_records():
    return current_items(policy.get("policy", []), effective_rule=True)

def current_industry_merchant_records():
    rows = [dict(item, _kind="行业") for item in current_items(policy.get("industry", []))]
    rows.extend(dict(item, _kind="商家") for item in current_items(policy.get("merchant", [])))
    return rows

def current_social_records():
    rows = []
    if dated_source_month(dd, dd.get("scrapedAt"), dd.get("coverage", {}).get("dateRange")) == CURRENT_MONTH:
        rows.append({
            "date": dd.get("scrapedAt", ""),
            "title": "抖店罗盘类目概览与类目挖掘",
            "summary": dd.get("summary") or dd.get("note", ""),
            "source": dd.get("source", "抖店罗盘"),
            "url": dd.get("sourceUrl", ""),
        })
    if dated_source_month(chanmama, chanmama.get("captured_at"), chanmama.get("window")) == CURRENT_MONTH:
        rows.append({
            "date": chanmama.get("captured_at", ""),
            "title": "蝉妈妈家具建材品牌榜",
            "summary": chanmama.get("metric_note", ""),
            "source": chanmama.get("source_name", "蝉妈妈"),
            "url": chanmama.get("source", ""),
        })
    if dated_source_month(juliang, juliang.get("captured_at"), juliang.get("window")) == CURRENT_MONTH:
        rows.append({
            "date": juliang.get("captured_at", ""),
            "title": "巨量算数九月报告检索核验",
            "summary": juliang.get("currentMonthVerification", {}).get("result") or juliang.get("summary") or juliang.get("metric_note", ""),
            "source": juliang.get("source_name", "巨量算数"),
            "url": juliang.get("url", ""),
        })
    return rows

def current_rule_records():
    return current_items(policy.get("platformRules", []), effective_rule=True)

def _record_date(item):
    for field in DATE_FIELDS:
        if item.get(field):
            return str(item[field])
    return "待核实"

def _classification_date(item, effective_rule=False):
    if effective_rule and item_month(item, effective_rule=True) == CURRENT_MONTH:
        effective = item.get("effectiveDate")
        if effective:
            return str(effective)
        if not in_current_month(item):
            return f"{CURRENT_MONTH}（标题注明生效）"
    return _record_date(item)

def _record_title(item):
    return str(item.get("title") or item.get("metric") or "未命名事项")

def _record_source(item):
    return str(item.get("source") or item.get("issuer") or "待核实")

def _record_summary(item):
    return str(item.get("summary") or item.get("note") or item.get("impact") or "")

def _overview_groups():
    return [
        ("宏观", current_macro_records(), False),
        ("房地产", current_realestate_records(), False),
        ("平台", current_platform_records(), False),
        ("政策", current_policy_records(), True),
        ("行业/商家", current_industry_merchant_records(), False),
        ("社媒", current_social_records(), False),
        ("平台规则", current_rule_records(), True),
    ]

def section_monthly(doc, detail=False):
    h1(doc, f"一、{CURRENT_MONTH_CN}专区（自然月1日至今）")
    para(doc, f"本专区仅陈列按统一月份规则归入{CURRENT_MONTH}的内容。识别顺序以monthBucket为最高优先级，再读取发布日、日期、印发日与采集时间；"
              "规则类事项若在9月正式生效，则优先按生效月归入9月。8月及更早内容不在本章混排。", indent=True)
    para(doc, mh.get("monthlySummary", ""), indent=True)
    numerals = "一二三四五六七"
    for index, (label, items, is_rule) in enumerate(_overview_groups()):
        h2(doc, f"1.{numerals[index]}　{label}（{len(items)}条）")
        if not items:
            add_empty_month_notice(doc, f"{label}数据")
            continue
        rows = [[_classification_date(item, effective_rule=is_rule), _record_title(item)[:44], _record_source(item)[:28]] for item in items]
        make_table(doc, ["归类日期", "9月事项", "来源"], rows, widths=[2.6, 9.2, 3.6], fsize=9)
        desc(doc, f"本表仅含{CURRENT_MONTH_CN}归类记录，共{len(items)}条；表内数量与表述均来自已加载数据源，未以历史记录补足。")
        if detail:
            for item in items:
                para(doc, f"【{_classification_date(item, effective_rule=is_rule)}】{_record_title(item)}", bold=True, size=10.5, indent=False)
                if _record_summary(item):
                    para(doc, _record_summary(item), size=10.5)
                add_source_line(doc, f"来源：{_record_source(item)}　{item.get('url', '')}")
    page_break(doc)

# ---- macro and real estate: current month only ----
def section_macro(doc, detail=False):
    h1(doc, f"二、{CURRENT_MONTH_CN}宏观与房地产")
    para(doc, f"本章只使用归类月份为{CURRENT_MONTH}的记录；指标统计期可能早于9月，但仅在9月发布时进入本章。", indent=True)

    h2(doc, "2.1　宏观需求与线上零售")
    rs = current_items(macro.get("macro", {}).get("retailSales", []))
    if rs:
        rows = [[x.get("metric", ""), x.get("value", "待核实"), x.get("yoy", "待核实"), x.get("publishDate", "待核实")] for x in rs]
        make_table(doc, ["指标", "数值", "同比", "发布日"], rows, widths=[6.5, 3.5, 3.0, 3.0])
        add_source_line(doc, "来源：各行所列国家统计局或转载页；URL保存在结构化数据中。")
        desc(doc, f"本表共{len(rs)}项9月发布数据。已核实数值与『待核实』标记均按源数据原样呈现；运营判断应同时观察总量、家具与建材的方向分化。")
    else:
        add_empty_month_notice(doc, "宏观需求数据")

    h2(doc, "2.2　供给与行业景气")
    supply = []
    for key in ("wholesale", "supplyChain"):
        supply.extend(current_items(macro.get("macro", {}).get(key, [])))
    if supply:
        rows = [[x.get("metric", ""), x.get("value", "待核实"), x.get("yoy", "待核实"), x.get("publishDate", "待核实")] for x in supply]
        make_table(doc, ["指标", "数值", "同比/变化", "发布日"], rows, widths=[6.5, 3.5, 3.0, 3.0])
        add_source_line(doc, "来源：国家统计局、中国建筑材料联合会/流通协会及表内结构化来源。")
        desc(doc, f"本表共{len(supply)}项9月发布的供给或景气记录。不同指标统计期与口径不一，仅作同指标趋势判断，不做跨口径直接换算。")
    else:
        add_empty_month_notice(doc, "供给与行业景气数据")

    h2(doc, "2.3　房地产")
    real_estate = current_realestate_records()
    if real_estate:
        rows = [[x.get("metric", _record_title(x)), x.get("value", "待核实"), x.get("yoy", "待核实"), _record_date(x)] for x in real_estate]
        make_table(doc, ["指标/事项", "数值", "同比/变化", "归类日期"], rows, widths=[6.5, 3.5, 3.0, 3.0])
        desc(doc, f"本表共{len(real_estate)}项9月房地产记录，全部按统一月份规则筛选。")
    else:
        add_empty_month_notice(doc, "房地产数据或政策")

    if detail:
        h2(doc, "2.4　本月数据边界")
        para(doc, "房地产历史统计、房价和前期政策未进入本月正文；如需参考，仅应放入明确标注的历史参考章节。", indent=False)
    page_break(doc)

# ---- social and paid-source intelligence: current month only ----
def section_social(doc, detail=False):
    h1(doc, f"六、{CURRENT_MONTH_CN}社媒与经营情报")
    social = current_social_records()
    if not social:
        add_empty_month_notice(doc, "社媒或经营情报")
        page_break(doc)
        return

    rows = [[_record_date(item), _record_title(item), _record_source(item)] for item in social]
    make_table(doc, ["采集日期", "数据集", "来源"], rows, widths=[2.8, 8.4, 4.2])
    desc(doc, f"本表共{len(social)}项9月核验结果；区间值与指数均保留原口径，不换算为精确GMV或销量。")
    if detail:
        for item in social:
            para(doc, _record_summary(item), size=10.5)
            add_source_line(doc, f"来源：{_record_source(item)}　{item.get('url', '')}")

        h2(doc, "6.1　抖店罗盘近7天概览")
        metric_names = {"payGmv":"支付金额", "itemsSold":"销量", "buyers":"支付人数", "orders":"订单数",
                        "onlineSku":"在线商品数", "activeSku":"动销商品数", "pricePerItem":"件单价", "arpu":"客单价"}
        metric_rows = [[metric_names.get(key, key), value.get("range", "待核实"), value.get("wow", "待核实")]
                       for key, value in dd.get("coreMetrics", {}).items()]
        make_table(doc, ["指标", "区间", "较上周期"], metric_rows, widths=[4.5, 5.5, 4.5])
        add_source_line(doc, f"来源：抖店罗盘；窗口 {dd.get('coverage', {}).get('dateRange', '待核实')}；采集日 {dd.get('scrapedAt', '待核实')}")
        desc(doc, dd.get("note", "按页面已核验口径展示。"))

        sub_rows = [[s.get("rank", ""), s.get("name", ""), s.get("gmvRange", "待核实"),
                     s.get("share", "待核实"), s.get("unitPrice", s.get("pricePerItem", "待核实"))]
                    for s in dd.get("subCategories", [])[:10]]
        make_table(doc, ["排名", "子类目", "GMV区间", "占比", "件单价"], sub_rows,
                   widths=[1.2, 4.0, 3.6, 2.6, 3.0], fsize=8.8)
        desc(doc, "子类目排名按当前智能家居/五金/工具窗口展示；与8月家装建材快照口径不同，不做跨期增减比较。")

        opportunities = dd.get("categoryMining", {}).get("potentialCategories", [])
        if opportunities:
            h2(doc, "6.2　类目挖掘机会")
            opportunity_rows = [[x.get("name", ""), x.get("gmvRange", "待核实"), x.get("growth", "待核实"),
                                 x.get("demandSupplyIndex", "待核实"), x.get("topPriceBand", "待核实")]
                                for x in opportunities]
            make_table(doc, ["类目", "支付金额", "增速", "需求供给比", "主力价格带"], opportunity_rows,
                       widths=[4.2, 3.4, 2.4, 2.6, 2.8], fsize=8.8)
            desc(doc, "机会类目来自同一核验窗口；优先结合增速、需求供给比与体量综合判断，不以单一高增速替代规模判断。")

        h2(doc, "6.3　蝉妈妈家具建材品牌榜")
        cm_rows = [[x.get("rank", ""), x.get("brand", ""), x.get("category_volume_band", "待核实"),
                    x.get("sales_index", "待核实"), x.get("linked_influencers", "待核实")]
                   for x in chanmama.get("ranking", [])[:15]]
        make_table(doc, ["排名", "品牌", "类目销量区间", "销售额指数", "关联达人"], cm_rows,
                   widths=[1.2, 4.4, 3.2, 3.2, 2.4], fsize=8.5)
        add_source_line(doc, f"来源：{chanmama.get('source_name', '蝉妈妈')}；采集日 {chanmama.get('captured_at', '待核实')}")
        desc(doc, "销售额指数为第三方估算的比较指标，只用于同一窗口内横向观察，不等同真实GMV。")
    page_break(doc)

# ---- explicitly separated historical reference ----
def section_doudian(doc, detail=False):
    h1(doc, "八、历史参考（非2026年9月新增）")
    para(doc, "本章只读取数据文件中明确保存的历史快照；9月17日新数据不在此重复展示。", indent=False,
         color=RGBColor(0x8A, 0x00, 0x00), bold=True)
    history = (dd.get("historySnapshots") or [{}])[0]
    coverage = history.get("coverage", {})
    h2(doc, f"8.1　抖店罗盘历史快照（{coverage.get('dateRange', '待核实')}）")
    if not history:
        add_empty_month_notice(doc, "可用历史快照")
    elif not detail:
        rows = [["抖店罗盘", history.get("capturedAt", "待核实"), coverage.get("dateRange", "待核实"), "历史参考"],
                ["巨量算数", "历史窗口", juliang.get("window", "待核实"), "历史参考"]]
        make_table(doc, ["数据源", "采集日", "数据窗口", "归属"], rows, widths=[3.0, 3.2, 7.2, 2.0], fsize=9)
        desc(doc, "历史快照与9月当前数据严格分区；抖店罗盘跨类目窗口不做直接比较，巨量算数旧指数不作为9月新增。")
    else:
        cm = history.get("coreMetrics", {})
        label = {"payGmv":"支付GMV", "itemsSold":"销量件数", "buyers":"支付买家数", "orders":"订单数",
                 "onlineSku":"在线商品数", "activeSku":"动销商品数", "pricePerItem":"件单价", "arpu":"客单价"}
        metric_rows = [[label.get(key, key), value.get("range", "待核实"), value.get("wow", "待核实")]
                       for key, value in cm.items()]
        make_table(doc, ["指标", "数量级区间", "较上周期"], metric_rows, widths=[4.5, 6.0, 4.0])
        desc(doc, "该表为8月历史快照，仅保留原始区间和环比方向，不与9月不同类目窗口直接对比。")

        sub_rows = [[s.get("rank", ""), s.get("name", ""), s.get("gmvRange", "待核实"),
                     s.get("share", "待核实"), s.get("unitPrice", "待核实"), s.get("arpu", "待核实")]
                    for s in history.get("subCategories", [])[:12]]
        make_table(doc, ["排名", "子类目", "GMV区间", "占比", "件单价", "客单价"], sub_rows,
                   widths=[1.3, 3.3, 3.4, 2.4, 2.3, 2.3], fsize=8.5)
        desc(doc, "历史子类目结构只用于回看当时大盘构成，不替代九月当前类目结果。")

    h2(doc, "8.2　巨量算数历史指数窗口")
    jl_rows = [[x.get("keyword", ""), x.get("search_index", {}).get("avg_display", "待核实"),
                x.get("search_index", {}).get("yoy", "待核实"), x.get("search_index", {}).get("mom", "待核实"),
                x.get("composite_index", {}).get("avg_display", "待核实")]
               for x in juliang.get("keywords", [])]
    make_table(doc, ["关键词", "搜索指数均值", "同比", "环比", "综合指数均值"], jl_rows,
               widths=[3.0, 3.2, 2.3, 2.3, 3.4], fsize=9)
    add_source_line(doc, f"来源：{juliang.get('source_name', '巨量算数')}；历史窗口 {juliang.get('window', '待核实')}")
    desc(doc, "九月检索未发现可核实的新报告，因此本表明确标为历史窗口；相对指数不换算为交易额。")
    page_break(doc)

# ---- platform dynamics: current month only ----
def section_platform(doc, detail=False):
    h1(doc, f"三、{CURRENT_MONTH_CN}电商平台竞争动态")
    para(doc, f"本章仅汇总归类月份为{CURRENT_MONTH}的平台动态；近30天窗口中的8月事项不在此处混排。", indent=True)
    platmeta = {"jd": "京东", "douyin": "抖音", "pdd": "拼多多", "xhs": "小红书",
                "tmall_taobao": "淘宝天猫", "shipinhao": "视频号", "kuaishou": "快手"}
    section_no = 1
    total = 0
    for key, name in platmeta.items():
        items = [item for item in current_items(plat.get("platforms", {}).get(key, []))
                 if item.get("type") != "待核实"]
        if not items:
            continue
        h2(doc, f"3.{section_no}　{name}（{len(items)}条）")
        section_no += 1
        rows = [[_record_date(item), _record_title(item)[:42], item.get("category", "通用")] for item in items]
        make_table(doc, ["日期", "动态标题", "子行业"], rows, widths=[2.4, 10.2, 2.6], fsize=9)
        desc(doc, f"{name}本月共有{len(items)}条已核实动态。表内仅呈现9月记录，具体影响需结合各条原文与平台口径判断。")
        total += len(items)
        if detail:
            for item in items:
                para(doc, _record_title(item), bold=True, size=10.5, indent=False)
                para(doc, item.get("summary", ""), size=10.5)
                add_source_line(doc, f"来源：{item.get('source', '待核实')}　{item.get('url', '')}")
    cross_platform = current_items(plat.get("crossPlatform", []))
    if cross_platform:
        h2(doc, f"3.{section_no}　跨平台趋势（{len(cross_platform)}条）")
        rows = [[_record_date(item), _record_title(item)[:42], item.get("category", "通用")] for item in cross_platform]
        make_table(doc, ["日期", "趋势标题", "子行业"], rows, widths=[2.4, 10.2, 2.6], fsize=9)
        desc(doc, f"本表共{len(cross_platform)}条9月跨平台趋势，未混入此前月份记录。")
        total += len(cross_platform)
    if total == 0:
        add_empty_month_notice(doc, "电商平台动态")
    page_break(doc)

# ---- policy and standards: current month only ----
def section_policy(doc, detail=False):
    h1(doc, f"四、{CURRENT_MONTH_CN}政策与标准")
    para(doc, "政策类记录执行统一月份规则；若规则在9月正式生效，即使8月发布，也归入9月。", indent=True)
    pol = current_policy_records()
    if not pol:
        add_empty_month_notice(doc, "政策或标准")
        page_break(doc)
        return
    rows = [[_classification_date(item, effective_rule=True), item.get("effectiveDate", ""), _record_title(item)[:40],
             "/".join(item.get("subIndustry", []))[:18]] for item in pol]
    make_table(doc, ["发布/归类日", "生效日", "政策/标准", "涉及子行业"], rows,
               widths=[2.4, 2.8, 7.2, 3.2], fsize=8.8)
    add_source_line(doc, "来源：国家市场监管总局、商务部等表内所列发布机构。")
    desc(doc, f"本表共{len(pol)}项9月政策/标准；其中8月发布、9月生效的规则按生效月纳入，避免遗漏本月实际执行事项。")
    if detail:
        for item in pol:
            para(doc, _record_title(item), bold=True, size=10.5, indent=False)
            para(doc, item.get("summary", ""), size=10.5)
            if item.get("impact"):
                para(doc, "影响：" + item["impact"], size=10.5, color=RGBColor(0x8A, 0x63, 0x00))
            add_source_line(doc, f"来源：{_record_source(item)}　{item.get('url', '')}")
    page_break(doc)

# ---- industry and merchant: current month only ----
def section_merchant(doc, detail=False):
    h1(doc, f"五、{CURRENT_MONTH_CN}行业与商家动态")
    para(doc, f"本章仅汇总归类月份为{CURRENT_MONTH}的协会、展会、行业研究和商家事项。", indent=True)
    items = current_industry_merchant_records()
    if not items:
        add_empty_month_notice(doc, "行业或商家动态")
        page_break(doc)
        return
    rows = [[_record_date(item), item.get("_kind", ""), item.get("brand", item.get("issuer", ""))[:18],
             _record_title(item)[:38]] for item in items]
    make_table(doc, ["日期", "类型", "主体", "动态"], rows, widths=[2.3, 1.8, 3.8, 7.7], fsize=8.8)
    add_source_line(doc, "来源：行业协会、展会主办方、公司公告与表内所列媒体。")
    desc(doc, f"本表共{len(items)}项9月行业/商家动态；行业事项与企业事项并列展示，未引入更早月份业绩作为本月新增。")
    if detail:
        for item in items:
            para(doc, f"{item.get('_kind', '')}｜{_record_title(item)}", bold=True, size=10.5, indent=False)
            para(doc, item.get("summary", ""), size=10.5)
            add_source_line(doc, f"来源：{_record_source(item)}　{item.get('url', '')}")
    page_break(doc)

# ---- platform rules: current month only ----
def section_platform_rules(doc, detail=False):
    h1(doc, f"七、{CURRENT_MONTH_CN}平台规则")
    para(doc, "本章单列平台经营、广告与履约规则。9月生效规则按生效月进入本章，8月发布且仍属8月的规则不混入。", indent=True)
    rules = current_rule_records()
    if not rules:
        add_empty_month_notice(doc, "平台规则")
        page_break(doc)
        return
    rows = [[_classification_date(item, effective_rule=True), item.get("platform", ""), _record_title(item)[:36],
             item.get("status", ""), item.get("relevance", "")] for item in rules]
    make_table(doc, ["发布/归类日", "平台", "规则", "状态", "相关性"], rows,
               widths=[2.4, 3.0, 7.0, 2.0, 1.3], fsize=8.5)
    add_source_line(doc, "来源：抖店、京准通、巨量千川等表内所列规则中心。")
    desc(doc, f"本表共{len(rules)}项9月生效或发布的平台规则；规则日期以实际生效优先，避免把8月发布、9月执行的事项误放入历史区。")
    if detail:
        for item in rules:
            para(doc, f"{item.get('platform', '')}｜{_record_title(item)}", bold=True, size=10.5, indent=False)
            para(doc, item.get("summary", ""), size=10.5)
            add_source_line(doc, f"来源：{_record_source(item)}　{item.get('url', '')}")
    page_break(doc)

# ---- source depth report ----
def section_sources(doc):
    h1(doc, "九、附录：数据源采集深度报告")
    para(doc, "公开版仅披露数据源名称、公开链接、采集深度、采集量与核验时间；账号、鉴权方式、内部入口和详细权限信息不进入报告。", indent=True)
    para(doc, "采集深度分级：0=未取到/阻塞，1=浅层（仅标题/目录），2=中层（关键指标/结构化摘要），3=深层（完整明细/多页/可下载表）。",
         indent=True, size=10)
    public_sources = [s for s in srcidx.get("sources", []) if str(s.get("layer", "")).upper() != "D"]
    rows = []
    for s in public_sources:
        rows.append([s.get("layer", ""), s.get("name", "")[:28], str(s.get("depth", "")),
                     str(s.get("count", ""))[:18], str(s.get("timestamp", ""))[:20]])
    make_table(doc, ["层", "数据源", "深度", "采集量", "核验时间"], rows,
               widths=[1.2, 5.2, 1.4, 3.4, 4.6], fsize=8.5)
    sm = srcidx["summary"]
    desc(doc, f"公开清单共{len(public_sources)}个数据源：深层采集{sm['depth3']}个、中层{sm['depth2']}个、浅层{sm['depth1']}个、"
              f"阻塞{sm['depth0_blocked']}个。未公开账号、鉴权或受限系统元数据。")
    page_break(doc)

# ---- board conclusion ----
def section_conclusion(doc):
    h1(doc, "十、总体结论与天猫运营建议")
    h2(doc, "10.1　本月核心判断")
    para(doc, mh.get("monthlySummary", ""), size=11, indent=False)
    counts = [(label, len(items)) for label, items, _ in _overview_groups()]
    para(doc, "9月专区记录量：" + "；".join(f"{label}{count}条" for label, count in counts) + "。", size=10.5, indent=False)
    if not current_realestate_records():
        para(doc, "房地产：本月无新增可核实记录，不以8月及更早数据补位。", size=10.5, indent=False)
    if not current_social_records():
        para(doc, "社媒：本月无新增可核实记录，旧蝉妈妈、旧巨量算数和抖店罗盘仅列入历史参考。", size=10.5, indent=False)

    h2(doc, "10.2　对天猫家装运营的行动建议")
    actions = [
        ("守住需求基本盘", "9月发布的8月数据表明社零总额同比增长0.4%，家具类同比下降7.9%，建筑及装潢材料类同比下降11.8%；资源配置应优先面向可验证的存量需求。"),
        ("承接智能家居政策", "商务部等8部门行动方案覆盖全屋智能体验、互联互通、补贴和送新收旧，平台可据此检查商品池、体验场景与履约链路。"),
        ("前置双11经营", "抖音与快手已在9月启动双11招商，京东也推进双十一商家大会；应按已核实节奏跟踪竞品招商与商家资源变化。"),
        ("完成信息描述合规校准", "家居产品与家装建材电商信息描述国家标准9月1日起实施，需校准商品字段、素材与宣称一致性。"),
        ("不以旧数据冒充新增", "本月房地产仍无新增可核实记录；社媒与经营情报仅采用9月17日已核验结果，历史快照只用于对照，不参与9月新增判断。"),
    ]
    for name, text in actions:
        para(doc, f"● {name}：{text}", size=11, indent=False)

    h2(doc, "10.3　后续补采重点")
    for item in [
        "抖店罗盘、蝉妈妈：继续按周更新同口径窗口；巨量算数仅在出现9月新报告时补充指数，不以旧窗口数值代替。",
        "房地产：补采9月发布的销售、投资、开工、房价或住房政策记录。",
        "平台规则：继续核对发布日与生效日，优先记录monthBucket，避免跨月误分。",
    ]:
        bullet(doc, item, size=10.5)

# =========================================================
#  BUILD BRIEF (汇报稿 8-12页)
# =========================================================
def build_brief(path):
    doc = Document()
    style_doc_defaults(doc)
    for s in doc.sections:
        s.page_width = Cm(21); s.page_height = Cm(29.7)
        s.top_margin = Cm(2.2); s.bottom_margin = Cm(2.2)
        s.left_margin = Cm(2.2); s.right_margin = Cm(2.2)
    cover(doc, "汇报稿（精要版）")
    section_monthly(doc, detail=False)
    section_macro(doc, detail=False)
    section_platform(doc, detail=False)
    section_policy(doc, detail=False)
    section_merchant(doc, detail=False)
    section_social(doc, detail=False)
    section_platform_rules(doc, detail=False)
    section_doudian(doc, detail=False)
    section_conclusion(doc)
    doc.save(path)
    return path

# =========================================================
#  BUILD DETAIL (详报 20-30页)
# =========================================================
def build_detail(path):
    doc = Document()
    style_doc_defaults(doc)
    for s in doc.sections:
        s.page_width = Cm(21); s.page_height = Cm(29.7)
        s.top_margin = Cm(2.2); s.bottom_margin = Cm(2.2)
        s.left_margin = Cm(2.2); s.right_margin = Cm(2.2)
    cover(doc, "详报（完整版）")
    h1(doc, "报告摘要（Executive Summary）")
    para(doc, mh.get("monthlySummary", ""), indent=True)
    para(doc, "本报告按2026年9月与历史参考严格分区。9月专区覆盖宏观、房地产、平台、政策、行业/商家、社媒、平台规则七类；"
              "抖店罗盘与蝉妈妈采用9月17日已核验数据，巨量算数记录9月报告检索结果而不复用旧指数；8月及更早快照只进入历史参考。"
              "每张数据表后均附自然语言解读，所有数据保留来源与日期，不可核实项标『待核实』。", indent=True)
    page_break(doc)
    section_monthly(doc, detail=True)
    section_macro(doc, detail=True)
    section_platform(doc, detail=True)
    section_policy(doc, detail=True)
    section_merchant(doc, detail=True)
    section_social(doc, detail=True)
    section_platform_rules(doc, detail=True)
    section_doudian(doc, detail=True)
    section_sources(doc)
    section_conclusion(doc)
    doc.save(path)
    return path

if __name__ == "__main__":
    outdir = sys.argv[1] if len(sys.argv) > 1 else ROOT
    os.makedirs(outdir, exist_ok=True)
    b = build_brief(os.path.join(outdir, "家装建材家具行业竞争情报月报_汇报稿.docx"))
    print("BRIEF ->", b)
    d = build_detail(os.path.join(outdir, "家装建材家具行业竞争情报月报_详报.docx"))
    print("DETAIL ->", d)
