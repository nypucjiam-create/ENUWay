from __future__ import annotations

import csv
import json
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "ai"
OUT = OUT_DIR / "lz12-enuway-ai-evaluation-report.docx"
METRICS_PATH = ROOT / "evals" / "lz12" / "results" / "metrics.json"
COST_PATH = OUT_DIR / "lz12-cost.json"
DATASET_PATH = ROOT / "evals" / "lz12" / "dataset.jsonl"
ERRORS_PATH = ROOT / "evals" / "lz12" / "results" / "error_analysis.csv"
FIGURE_PATH = OUT_DIR / "lz12-quality-metrics.png"

FONT = "Times New Roman"
NAVY = "1F4E78"
BLUE = "D9EAF7"
LIGHT = "F4F7FA"
GRAY = "666666"
LABEL_KK = {
    "ACCOUNT": "Тіркелгі",
    "SEARCH": "Іздеу",
    "RIDE_MANAGEMENT": "Сапарды басқару",
    "BOOKING": "Бронь",
    "SAFETY": "Қауіпсіздік",
}


def style_run(run, size=14, bold=False, italic=False, color="000000"):
    run.font.name = FONT
    rfonts = run._element.get_or_add_rPr().rFonts
    for name in ("ascii", "hAnsi", "eastAsia", "cs"):
        rfonts.set(qn(f"w:{name}"), FONT)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)


def set_repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tag = OxmlElement("w:tblHeader")
    tag.set(qn("w:val"), "true")
    tr_pr.append(tag)


def keep_row(row):
    row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def borders(table, color="B7C9D6"):
    tbl_pr = table._tbl.tblPr
    node = tbl_pr.first_child_found_in("w:tblBorders")
    if node is None:
        node = OxmlElement("w:tblBorders")
        tbl_pr.append(node)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = node.find(qn(f"w:{edge}"))
        if el is None:
            el = OxmlElement(f"w:{edge}")
            node.append(el)
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:color"), color)


def configure(doc):
    section = doc.sections[0]
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(3)
    section.right_margin = Cm(1.5)
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal._element.rPr.rFonts.set(qn("w:ascii"), FONT)
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), FONT)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    normal.font.size = Pt(14)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.first_line_indent = Cm(1.25)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.space_after = Pt(0)
    for name, size in (("Title", 18), ("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 14)):
        s = doc.styles[name]
        s.font.name = FONT
        s._element.rPr.rFonts.set(qn("w:ascii"), FONT)
        s._element.rPr.rFonts.set(qn("w:hAnsi"), FONT)
        s._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        s.font.size = Pt(size)
        s.font.bold = True
        s.font.color.rgb = RGBColor(0, 0, 0)
        s.paragraph_format.first_line_indent = Cm(0)
        s.paragraph_format.space_before = Pt(12)
        s.paragraph_format.space_after = Pt(6)


def page_number(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    r = p.add_run()
    begin = OxmlElement("w:fldChar"); begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = " PAGE "
    end = OxmlElement("w:fldChar"); end.set(qn("w:fldCharType"), "end")
    r._r.extend([begin, instr, end])
    style_run(r, 12)


def paragraph(doc, text="", *, align=None, indent=True, size=14, bold=False, italic=False, color="000000", keep=False):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(1.25) if indent else Cm(0)
    p.paragraph_format.alignment = align or WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.keep_with_next = keep
    p.paragraph_format.line_spacing = 1.5
    style_run(p.add_run(text), size=size, bold=bold, italic=italic, color=color)
    return p


def heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.paragraph_format.keep_with_next = True
    style_run(p.add_run(text), 16 if level == 1 else 14, True)
    return p


def bullets(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.left_indent = Cm(0.9)
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.line_spacing = 1.25
        style_run(p.add_run(item), 14)


def table(doc, headers, rows, widths=None, font_size=10):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    borders(t)
    set_repeat_header(t.rows[0]); keep_row(t.rows[0])
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        shade(c, NAVY)
        c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = c.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.first_line_indent = Cm(0); p.paragraph_format.line_spacing = 1
        style_run(p.add_run(str(h)), font_size, True, color="FFFFFF")
        if widths: c.width = Cm(widths[i])
    for ri, values in enumerate(rows):
        row = t.add_row(); keep_row(row)
        for i, value in enumerate(values):
            c = row.cells[i]
            if ri % 2: shade(c, LIGHT)
            c.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = c.paragraphs[0]; p.paragraph_format.first_line_indent = Cm(0); p.paragraph_format.line_spacing = 1.05; p.paragraph_format.space_after = Pt(0)
            style_run(p.add_run(str(value)), font_size)
            if widths: c.width = Cm(widths[i])
    doc.add_paragraph().paragraph_format.space_after = Pt(0)
    return t


def cover(doc):
    paragraph(doc, "Л.Н. Гумилев атындағы Еуразия ұлттық университеті", align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, bold=True)
    paragraph(doc, "Ақпараттық технологиялар факультеті", align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)
    for _ in range(4): doc.add_paragraph()
    paragraph(doc, "ЗЕРТХАНАЛЫҚ ЖҰМЫС № 12", align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, size=16, bold=True)
    paragraph(doc, "ENUWay жобасындағы AI функциясын бағалау", align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, size=18, bold=True)
    paragraph(doc, "Қойылым, eval-жинақ, нақты өлшем, құн, тәуекел және ADR", align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)
    for _ in range(5): doc.add_paragraph()
    for label, value in (("Орындаушылар", "Альфараби, Нурай, Нурислам"), ("Пән", "IT жобаларын басқару"), ("Жоба", "ENUWay"), ("Оқу жылы", "2026–2027")):
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.RIGHT; p.paragraph_format.first_line_indent = Cm(0)
        style_run(p.add_run(label + ": "), 14, True); style_run(p.add_run(value), 14)
    for _ in range(3): doc.add_paragraph()
    paragraph(doc, "Астана, 2026", align=WD_ALIGN_PARAGRAPH.CENTER, indent=False)
    doc.add_page_break()


def make_figure(metrics):
    methods = ["Baseline", "Zero-shot", "Few-shot"]
    keys = ["baseline", "zero_shot", "few_shot"]
    accuracy = [metrics[k]["accuracy"] for k in keys]
    macro = [metrics[k]["macro_f1"] for k in keys]
    width, height = 1500, 780
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    regular_path = Path("C:/Windows/Fonts/arial.ttf")
    bold_path = Path("C:/Windows/Fonts/arialbd.ttf")
    regular = ImageFont.truetype(str(regular_path), 30)
    small = ImageFont.truetype(str(regular_path), 25)
    bold = ImageFont.truetype(str(bold_path), 32)
    left, right, top, bottom = 120, 1420, 100, 650
    draw.text((left, 35), "ENUWay: тәсілдердің сапасын салыстыру", font=bold, fill="#1F1F1F")
    for i in range(6):
        y = bottom - (bottom - top) * i / 5
        draw.line((left, y, right, y), fill="#D9E1E8", width=2)
        draw.text((55, y - 15), f"{i/5:.1f}", font=small, fill="#555555")
    group_width = (right - left) / 3
    bar_width = 110
    for idx, method in enumerate(methods):
        center = left + group_width * (idx + .5)
        for offset, value, color in ((-bar_width / 2, accuracy[idx], "#5B9BD5"), (bar_width / 2, macro[idx], "#70AD47")):
            x0 = center + offset - bar_width / 2
            x1 = center + offset + bar_width / 2
            y0 = bottom - value * (bottom - top)
            draw.rectangle((x0, y0, x1, bottom), fill=color)
            label = f"{value:.3f}"
            box = draw.textbbox((0, 0), label, font=small)
            draw.text((center + offset - (box[2] - box[0]) / 2, y0 - 36), label, font=small, fill="#222222")
        box = draw.textbbox((0, 0), method, font=regular)
        draw.text((center - (box[2] - box[0]) / 2, bottom + 25), method, font=regular, fill="#222222")
    draw.rectangle((980, 38, 1015, 73), fill="#5B9BD5")
    draw.text((1025, 40), "Accuracy", font=small, fill="#222222")
    draw.rectangle((1190, 38, 1225, 73), fill="#70AD47")
    draw.text((1235, 40), "Macro F1", font=small, fill="#222222")
    image.save(FIGURE_PATH)


def pct(value):
    return f"{value * 100:.1f}%".replace(".", ",")


def build():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    cost = json.loads(COST_PATH.read_text(encoding="utf-8"))
    dataset = [json.loads(x) for x in DATASET_PATH.read_text(encoding="utf-8").splitlines() if x.strip()]
    with ERRORS_PATH.open(encoding="utf-8-sig") as handle: errors = list(csv.DictReader(handle))
    make_figure(metrics)

    doc = Document(); configure(doc); page_number(doc.sections[0]); cover(doc)
    heading(doc, "АҢДАТПА")
    paragraph(doc, "Бұл есеп ENUWay қолдау өтініштерін бес санатқа автоматты бөлу мүмкіндігін тексереді. Бағалау 40 қолмен құрастырылған эталон өтініште жүргізілді. 20 кілтсөздік ереже, zero-shot және few-shot промпттары бір деректер жинағында салыстырылды. Qwen2.5-3B-Instruct Q4_K_M моделі жергілікті llama.cpp серверінде temperature=0 және seed=42 параметрлерімен нақты іске қосылды. Барлық промпт, шикі жауап, токен саны мен кідіріс сақталды.")
    paragraph(doc, f"Нәтиже: baseline macro F1 — {metrics['baseline']['macro_f1']:.3f}, zero-shot — {metrics['zero_shot']['macro_f1']:.3f}, few-shot — {metrics['few_shot']['macro_f1']:.3f}. Модель жоспарланған қабылдау шегіне жетпеді және baseline-нан нашар болды; сондықтан дәлелді шешім — AI нұсқасын әзірге енгізбеу, baseline-ды сақтау және жақсартудан кейін қайта өлшеу.")
    paragraph(doc, "Кілт сөздер: ENUWay, жасанды интеллект, жіктеу, eval, macro F1, baseline, few-shot, тәуекел, ADR.", italic=True)

    heading(doc, "МАЗМҰНЫ")
    table(doc, ["Бөлім", "Атауы"], [["1", "Жұмыстың қойылымы"], ["2", "AI функциясы және метрикалар"], ["3", "Бағалау жинағы"], ["4", "Өлшеу әдісі және нәтижелер"], ["5", "Қате талдауы"], ["6", "Құн және масштабтау"], ["7", "Тәуекелдер және адам бақылауы"], ["8", "Архитектуралық шешім"], ["9", "Қорытынды"], ["Қосымша А", "40 эталон мысал"], ["Қосымша Ә", "Қайта өндіру және артефакттар"]], [3, 14], 11)

    heading(doc, "1 ЖҰМЫСТЫҢ ҚОЙЫЛЫМЫ")
    paragraph(doc, "Мақсат — ENUWay жобасында AI нақты құндылық беретін бір функцияны таңдау, оны AI-сыз базалық шешіммен салыстыру, кемінде 30 эталон мысалда нақты өлшеу, операциялық құнын және тәуекелін есептеу, содан кейін дәлелді «жасаймыз/жасамаймыз» шешімін қабылдау.")
    bullets(doc, ["Таңдалған функция: қолдау өтінішін жауапты кезекке алдын ала санаттау.", "Санаттар: ACCOUNT, SEARCH, RIDE_MANAGEMENT, BOOKING және SAFETY.", "Шекара: модель жауап бермейді және жүйеде әрекет жасамайды.", "Қауіпсіздік қағидасы: SAFETY және UNCERTAIN әрқашан адамға беріледі."])
    heading(doc, "1.1 Міндеттер", 2)
    table(doc, ["№", "Міндет", "Дәлел"], [["1", "Бизнес және модель метрикаларын байланыстыру", "AI функция карточкасы"], ["2", "AI-сыз baseline құру", "20 ереже және код"], ["3", "≥30 эталон жинау", "40 жолдық JSONL"], ["4", "Екі промптты өлшеу", "raw JSONL және metrics.json"], ["5", "Құн мен 10× сценарийін есептеу", "cost.json"], ["6", "Тәуекел мен шешімді рәсімдеу", "risk card және ADR-004"]], [1, 9, 7], 9)

    heading(doc, "2 AI ФУНКЦИЯСЫ ЖӘНЕ МЕТРИКАЛАР")
    paragraph(doc, "Қолдау операторының міндеті — өтінішті бірінші рет дұрыс кезекке жіберу. Модель сапасы жоғарылаған сайын қате бағыттау мен қайта бөлу азаяды. Сондықтан жалпы accuracy-мен шектелмей, барлық санатты тең салмақпен есептейтін macro F1 және қауіпті өтінішті өткізіп алмауды өлшейтін SAFETY recall қолданылады.")
    table(doc, ["Метрика", "Қабылдау шегі", "Бизнеске әсері"], [["Macro F1", "≥ 0,85", "барлық кезектегі тұрақты сапа"], ["Әр санат F1", "≥ 0,75", "сирек санаттың жасырынбауы"], ["SAFETY recall", "≥ 0,90", "қауіпсіздік сигналының өткізілмеуі"], ["Дұрыс алғашқы бағыттау", "≥ 90%", "қайта бөлудің азаюы"], ["Медианалық бағыттау уақыты", "baseline-нан ≥40% төмен", "оператор уақытының үнемделуі"]], [5, 4, 8], 10)
    paragraph(doc, "Бағыттау уақытының 90 секундтық бастапқы мәні — жоспарлық болжам, модель сапасының нәтижесі емес. Ол пилотта нақты журналмен тексеріледі. Бұл айырма есепте әдейі ашық көрсетілді.")

    heading(doc, "3 БАҒАЛАУ ЖИНАҒЫ")
    paragraph(doc, "Жинақта 40 өтініш бар: әр санатқа 8 мысалдан. 10 мысал күрделі деп белгіленген: қысқа, аралас қазақша-орысша немесе контексті аз. Нақты пайдаланушы мәтіні көшірілмеді; мысалдар ENUWay талаптары мен backlog сценарийлеріне сүйеніп қолмен құрастырылды. Эталон санаттар бағаланатын модельден алынған жоқ.")
    table(doc, ["Санат", "Саны", "Мақсаты"], [[LABEL_KK[l], sum(x["gold"] == l for x in dataset), {"ACCOUNT":"кіру және профиль","SEARCH":"сапарды табу","RIDE_MANAGEMENT":"жүргізушінің жарияланымы","BOOKING":"жолаушы орны","SAFETY":"қауіп және шағым"}[l]] for l in LABEL_KK], [6, 3, 8], 10)
    paragraph(doc, "Эталонның шектеуі: қорытынды тапсыру алдында команда мүшелері алтын белгілерді дербес қарап шығуы тиіс. Бағаланатын модель эталон төрешісі бола алмайды.")

    heading(doc, "4 ӨЛШЕУ ӘДІСІ ЖӘНЕ НӘТИЖЕЛЕР")
    heading(doc, "4.1 Қайталанатын орта", 2)
    table(doc, ["Параметр", "Мән"], [["Модель", metrics["run"]["model"]], ["Орындау", "llama.cpp b12359, жергілікті CPU"], ["Temperature", "0"], ["Seed", str(metrics["run"]["seed"])], ["Максимум жауап", "4 токен"], ["Жинақ", "40 мысал"], ["Промпттар", "zero-shot және 10 мысалды few-shot"], ["Шикі дәлел", "zero_shot_raw.jsonl, few_shot_raw.jsonl"]], [6, 11], 10)
    heading(doc, "4.2 Салыстырмалы нәтиже", 2)
    table(doc, ["Тәсіл", "Accuracy", "Macro F1", "UNCERTAIN"], [[name, pct(metrics[key]["accuracy"]), f"{metrics[key]['macro_f1']:.3f}", metrics[key]["uncertain_count"]] for name, key in (("20 ережелік baseline", "baseline"), ("Zero-shot", "zero_shot"), ("Few-shot", "few_shot"))], [7, 4, 4, 3], 10)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.first_line_indent = Cm(0)
    p.add_run().add_picture(str(FIGURE_PATH), width=Cm(15.8))
    paragraph(doc, "1-сурет — Үш тәсілдің accuracy және macro F1 салыстыруы", align=WD_ALIGN_PARAGRAPH.CENTER, indent=False, size=11, italic=True)
    heading(doc, "4.3 Санаттар бойынша F1", 2)
    rows = []
    for label in LABEL_KK:
        rows.append([LABEL_KK[label], f"{metrics['baseline']['per_class'][label]['f1']:.3f}", f"{metrics['zero_shot']['per_class'][label]['f1']:.3f}", f"{metrics['few_shot']['per_class'][label]['f1']:.3f}"])
    table(doc, ["Санат", "Baseline", "Zero-shot", "Few-shot"], rows, [6, 3.5, 3.5, 3.5], 10)
    accepted = metrics["few_shot"]["macro_f1"] >= .85 and min(v["f1"] for v in metrics["few_shot"]["per_class"].values()) >= .75 and metrics["few_shot"]["per_class"]["SAFETY"]["recall"] >= .9
    paragraph(doc, "Қабылдау қорытындысы: " + ("барлық техникалық шек орындалды." if accepted else "техникалық шектер толық орындалмады; толық автоматтандыруға жіберілмейді."), bold=True)

    heading(doc, "5 ҚАТЕ ТАЛДАУЫ")
    few_errors = [r for r in errors if r.get("few_shot_pred") != r.get("gold")]
    paragraph(doc, f"Few-shot нұсқасында {len(few_errors)} қате немесе бас тарту тіркелді. Әр қате raw жауаппен байланыстырылған. Төмендегі кесте алғашқы он қатені көрсетеді; толық тізім error_analysis.csv файлында.")
    table(doc, ["ID", "Эталон", "Болжам", "Өтініш"], [[r["id"], r["gold"], r.get("few_shot_pred", ""), r["text"]] for r in few_errors[:10]], [1.3, 4, 4, 7.5], 8)
    bullets(doc, ["Қысқа мәтінде контекст жетіспесе модель UNCERTAIN қайтаруы мүмкін.", "SEARCH пен RIDE_MANAGEMENT шекарасы «маршрут» сөзінде шатасады; әрекет иесін промптта айқынырақ көрсету қажет.", "Қауіпсіздік үшін recall қабылдау шегінен төмен болса, адам тексеруі міндетті және пилот автоматты әрекет жасамайды.", "Келесі итерация: қате мысалдарды few-shot жинағына қосу, сынып анықтамасын ықшамдау және үлкенірек ашық модельді сол eval-да салыстыру."])

    heading(doc, "6 ҚҰН ЖӘНЕ МАСШТАБТАУ")
    tok = cost["tokens"]; api = cost["api"]; selfh = cost["self_hosted"]
    paragraph(doc, "Токен саны болжаммен емес, few-shot өлшеміндегі llama.cpp usage өрісінен алынды. API бағасы тек салыстыру үшін есептелді; ақылы сервис іске қосылған жоқ.")
    table(doc, ["Көрсеткіш", "Мән"], [["Орташа кіріс токені", tok["average_input_tokens"]], ["Орташа шығыс токені", tok["average_output_tokens"]], ["API үлгісі", api["model"]], ["Кіріс бағасы", f"${api['input_usd_per_million']:.2f} / 1 млн токен"], ["Шығыс бағасы", f"${api['output_usd_per_million']:.2f} / 1 млн токен"], ["1 сұрау", f"${api['cost_per_request_usd']:.8f}"], ["3 000 сұрау/ай", f"${api['monthly_cost_usd']:.4f}"], ["30 000 сұрау/ай (10×)", f"${api['ten_x_monthly_cost_usd']:.4f}"], ["Self-hosted CPX32", f"${selfh['monthly_cost_usd']:.2f}/ай, ҚҚС-сыз"], ["Теңесу нүктесі", f"{selfh['break_even_requests_per_month']:,} сұрау/ай".replace(",", " ")]], [8, 9], 10)
    paragraph(doc, f"Формула: {cost['formula']}. Тарифке қол жеткізу күні — {cost['access_date']}. API дереккөзі: {api['source']}. Сервер дереккөзі: {selfh['source']}.")
    paragraph(doc, "Экономикалық қорытынды: шағын және 10× жүктемеде API есептік жағынан арзан. Бірақ оқу өлшемі жергілікті құрылғыда төлемсіз орындалды, ал деректерді сыртқа жібермеу жеке архитектуралық артықшылық болып қалады. Теңесу нүктесі тек сервер тарифі бойынша есептелген; әкімші еңбегі мен резервтік инфрақұрылым кірмейді.")

    heading(doc, "7 ТӘУЕКЕЛДЕР ЖӘНЕ АДАМ БАҚЫЛАУЫ")
    table(doc, ["Тәуекел", "Бақылау", "Триггер / иесі"], [["SAFETY өтінішін өткізіп алу", "SAFETY және UNCERTAIN адамға", "recall < 0,90 / Альфараби"], ["Қате кезек", "оператор санатты өзгерте алады", "түзету >10% / Нурай"], ["Дербес дерек", "жергілікті модель, бүркемелеу", "дерек журналда / Нурислам"], ["Модель істемейді", "20 ережелік baseline", "p95 >2 с не uptime <99% / Нурислам"], ["Тілдік айырма", "тілдер бойынша бөлек өлшем", "айырма >10 т.п. / Нурай"], ["Prompt injection", "шығысты алты белгіге шектеу", "жарамсыз жауап / Альфараби"]], [5, 7, 5], 9)
    paragraph(doc, "Пайдаланушы интерфейсінде «AI көмегімен алдын ала санатталды» белгісі, ұсынылған санат және «Адамға жіберу» әрекеті көрсетіледі. AI броньды, аккаунтты немесе шағымды өздігінен өзгертпейді.")

    heading(doc, "8 АРХИТЕКТУРАЛЫҚ ШЕШІМ")
    paragraph(doc, "ADR-004 шешімі: жергілікті Qwen2.5-3B-Instruct few-shot нұсқасын әзірге ENUWay-ға енгізбеу. Ағымдағы өлшем қабылдау шегін орындамады және baseline-нан нашар. Сыртқы API экономикалық балама ретінде есептелді, бірақ дерек құпиялылығы бағаға ғана сүйеніп шешілмейді.")
    table(doc, ["Нұсқа", "Артықшылық", "Неге таңдалды/қабылданбады"], [["20 ереже", "қарапайым, резервке жарайды", "қазіргі шешім ретінде сақталды"], ["Сыртқы API", "арзан масштабтау", "құпиялылық бағалауына дейін қабылданбады"], ["Жергілікті Qwen 3B", "дерек сыртқа шықпайды", "өлшенді, бірақ сапасы жеткіліксіз болғандықтан енгізілмейді"], ["RAG", "білімнен жауап құрады", "жабық санаттау үшін артық күрделі"]], [4, 6, 7], 9)
    paragraph(doc, "Қайта қарау: промпт немесе модель жаңартылғаннан кейін, бірақ 19.12.2026 күнінен кеш емес. Пилот тек macro F1 ≥0,85, әр санат F1 ≥0,75 және SAFETY recall ≥0,90 болғанда басталады.")

    heading(doc, "9 ҚОРЫТЫНДЫ")
    paragraph(doc, "ЛЗ №12 талаптары бойынша бір AI функциясы таңдалды, бизнес пен модель метрикалары байланыстырылды, AI-сыз baseline жасалды, 40 эталон мысал дайындалды және екі промпт нақты жергілікті модельде өлшенді. Нәтиже әдейі әдеміленбей, шикі жауаптарымен бірге сақталды. Few-shot zero-shot-тан жақсы болғанымен, baseline-нан төмен және қабылдау шегіне жетпеді. Сондықтан инженерлік тұрғыдан дұрыс шешім — AI нұсқасын әзірге енгізбеу, 20 ережелік baseline-ды сақтау және жақсартудан кейін сол eval-ды қайта орындау.")
    bullets(doc, ["Деректер жинағы, код және raw нәтижелер репозиторийде сақталған.", "Құн нақты токен өлшемі мен ресми тарифке негізделген.", "10× сценарийі және self-hosted теңесу нүктесі есептелген.", "Тәуекел карточкасында адам бақылауы, пайдаланушыға ашықтық және провайдерге кететін дерек анықталған.", "ADR-004 нұсқаларды, салдарды және қайта қарау критерийін бекітеді."])

    doc.add_page_break(); heading(doc, "ҚОСЫМША А — 40 ЭТАЛОН МЫСАЛ")
    table(doc, ["ID", "Өтініш", "Эталон", "Күрделілік"], [[x["id"], x["text"], x["gold"], "күрделі" if x["difficulty"] == "hard" else "қалыпты"] for x in dataset], [1.2, 9.2, 4.2, 2.4], 8)

    doc.add_page_break(); heading(doc, "ҚОСЫМША Ә — ҚАЙТА ӨНДІРУ ЖӘНЕ АРТЕФАКТТАР")
    table(doc, ["Артефакт", "Орны"], [["AI функция карточкасы", "docs/ai/lz12-ai-function-card.md"], ["Eval жинағы", "evals/lz12/dataset.jsonl"], ["Өлшеу коды", "evals/lz12/run_eval.py"], ["Нақты метрикалар", "evals/lz12/results/metrics.json"], ["Шикі жауаптар", "evals/lz12/results/*_raw.jsonl"], ["Қате талдауы", "evals/lz12/results/error_analysis.csv"], ["Құн есебі", "docs/ai/lz12-cost.json"], ["Тәуекел карточкасы", "docs/ai/lz12-risk-card.md"], ["Шешім", "docs/adr/ADR-004-ai-support-classifier.md"]], [7, 10], 9)
    paragraph(doc, "Қайта іске қосу командасы:", bold=True)
    paragraph(doc, "python evals/lz12/run_eval.py --server-url http://127.0.0.1:8080 --model qwen2.5-3b-instruct-q4_k_m.gguf", indent=False, size=10)
    paragraph(doc, "Модель файлы репозиторийге салынбайды: Qwen/Qwen2.5-3B-Instruct-GGUF, qwen2.5-3b-instruct-q4_k_m.gguf. Көзі: https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF. Бағдарламалық орта: llama.cpp b12359. Модельдің көлемі — 2 104 932 768 байт. SHA-256: 626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d.", indent=False, align=WD_ALIGN_PARAGRAPH.LEFT, size=10)

    core = doc.core_properties
    core.title = "ЛЗ №12 — ENUWay AI функциясын бағалау"
    core.subject = "Eval, құн, тәуекел және ADR"
    core.author = "Альфараби, Нурай, Нурислам"
    core.keywords = "ENUWay, AI, eval, macro F1, ADR"
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
