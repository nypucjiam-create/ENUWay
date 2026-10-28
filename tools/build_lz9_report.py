from pathlib import Path
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "process" / "lz9-enuway-flow-report.docx"
CFD_IMAGE = ROOT / "docs" / "process" / ".qa" / "CFD.png"
SUMMARY_IMAGE = ROOT / "docs" / "process" / ".qa" / "Шолу.png"


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=90, start=100, bottom=90, end=100):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_cell_border(cell, color="D9D9D9", size="6"):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = borders.find(qn(f"w:{edge}"))
        if tag is None:
            tag = OxmlElement(f"w:{edge}")
            borders.append(tag)
        tag.set(qn("w:val"), "single")
        tag.set(qn("w:sz"), size)
        tag.set(qn("w:color"), color)


def set_run_font(run, name="Times New Roman", size=14, bold=False, italic=False, color="000000"):
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), name)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)


def add_field(paragraph, instruction):
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, text, end])
    set_run_font(run, size=12)


def add_heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.paragraph_format.space_before = Pt(10 if level == 1 else 6)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    set_run_font(r, size=14, bold=True)
    return p


def add_body(doc, text, bold_lead=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Cm(1.25)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(3)
    if bold_lead and text.startswith(bold_lead):
        r1 = p.add_run(bold_lead)
        set_run_font(r1, bold=True)
        r2 = p.add_run(text[len(bold_lead):])
        set_run_font(r2)
    else:
        r = p.add_run(text)
        set_run_font(r)
    return p


def add_bullets(doc, items):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.left_indent = Cm(1.25)
        p.paragraph_format.first_line_indent = Cm(-0.5)
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(item)
        set_run_font(r)


def add_table(doc, headers, rows, widths=None, font_size=10):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.rows[0]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
    for index, header in enumerate(headers):
        cell = table.rows[0].cells[index]
        cell.text = ""
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_shading(cell, "1F4E78")
        set_cell_border(cell)
        set_cell_margins(cell)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(str(header))
        set_run_font(r, size=font_size, bold=True, color="FFFFFF")
        if widths:
            cell.width = Cm(widths[index])
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for index, value in enumerate(row):
            cell = cells[index]
            cell.text = ""
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_border(cell)
            set_cell_margins(cell)
            if row_index % 2:
                set_cell_shading(cell, "F2F6FA")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if index == 0 or isinstance(value, (int, float)) else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(str(value))
            set_run_font(r, size=font_size)
            if widths:
                cell.width = Cm(widths[index])
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


doc = Document()
section = doc.sections[0]
section.top_margin = Cm(2)
section.bottom_margin = Cm(2)
section.left_margin = Cm(3)
section.right_margin = Cm(1.5)
section.different_first_page_header_footer = True

styles = doc.styles
styles["Normal"].font.name = "Times New Roman"
styles["Normal"]._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
styles["Normal"]._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
styles["Normal"].font.size = Pt(14)
for style_name in ("Title", "Heading 1", "Heading 2"):
    style = styles[style_name]
    style.font.name = "Times New Roman"
    style._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    style._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    style.font.color.rgb = RGBColor(0, 0, 0)

footer_p = section.footer.paragraphs[0]
footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
add_field(footer_p, "PAGE")

for text, size, bold, after in [
    ("ҚАЗАҚСТАН РЕСПУБЛИКАСЫ БІЛІМ ЖӘНЕ ҒЫЛЫМ МИНИСТРЛІГІ", 14, True, 12),
    ("Л.Н. Гумилев атындағы Еуразия ұлттық университеті", 14, False, 2),
    ("Ақпараттық технологиялар факультеті", 14, False, 2),
    ("Ақпараттық жүйелер кафедрасы", 14, False, 80),
    ("ЕСЕП", 16, True, 3),
    ("ЗЕРТХАНАЛЫҚ ЖҰМЫС № 9", 16, True, 18),
    ("Пән: IT жобаларын басқару", 14, False, 12),
    ("Тақырыбы: «ENUWay жұмыс процесі және екі спринттің ағын метрикалары»", 14, True, 72),
]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(after)
    r = p.add_run(text)
    set_run_font(r, size=size, bold=bold)

for text in [
    "Орындағандар: Альфараби, Нурай, Нурислам",
    "Тобы: АЖ - 45",
    "Тексерген: Самбетбаева М.А.",
]:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run(text)
    set_run_font(r)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
p.paragraph_format.space_before = Pt(75)
r = p.add_run("Астана, 2026 жыл")
set_run_font(r)
p.add_run().add_break(WD_BREAK.PAGE)

title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title.paragraph_format.space_after = Pt(12)
r = title.add_run("ENUWay жұмыс ағынын өлшеу есебі")
set_run_font(r, size=16, bold=True)

add_body(doc, "№ 9 зертханалық жұмыстың мақсаты - ENUWay жобасының нақты жұмыс процесін бекіту, екі спринттің ағын метрикаларын салыстыру және бір өлшенетін жақсарту әрекетінің нәтижесін талдау. GitHub Projects тақтасында тарихи Done карточкалары болмағандықтан, есеп Git commit тарихынан қалпына келтірілген дәлелді деректерді пайдаланады. Бұл шектеу барлық кестелерде ашық көрсетілген.")

add_heading(doc, "1 Жұмыс процесін баптау", 1)
add_body(doc, "Тақта нақты жұмыс күйін көрсететін алты кезеңнен тұрады. Waiting кезеңі сыртқы шешім, дерек немесе қолжетімділік күтілетін жұмысты In Progress-тен бөліп көрсетеді. WIP шектеулері командаға жаңа жұмысты бастамас бұрын аяқталмаған жұмысты бітіруге көмектеседі.")
add_table(
    doc,
    ["Кезең", "Мақсаты", "WIP шегі", "Шығу шарты"],
    [
        ["Backlog", "Жоспарланған жұмыс", "Шектеусіз", "Басымдық және DoR"],
        ["Ready", "Бастауға дайын", "6", "Орындаушының capacity бар"],
        ["In Progress", "Нақты орындалуда", "Әр адамға 2, командаға 6", "Review немесе Waiting"],
        ["Waiting", "Сыртқы кедергіні күту", "2", "Кедергі жойылды"],
        ["Review", "Қабылдау бойынша тексеру", "3", "DoD немесе түзету"],
        ["Done", "Қабылданған нәтиже", "Шектеусіз", "Қайтарылмайды"],
    ],
    widths=[2.8, 5.4, 4.0, 4.2],
)
add_body(doc, "Карточка нақты кезеңге өткен күні тақтада сол күні жылжытылады. In Progress → Waiting өтуі үшін кедергі, оның иесі және қайта тексеру күні жазылады. In Progress → Review өтуі үшін нәтиже сілтемесі мен қабылдау критерийлерінің дәлелі қажет. Review → Done тек DoD толық орындалғанда рұқсат етіледі.")

add_heading(doc, "2 Definition of Ready және Definition of Done", 1)
add_heading(doc, "2.1 Definition of Ready", 2)
add_bullets(doc, [
    "пайдаланушы немесе тапсырыс беруші үшін күтілетін нәтиже анық жазылған;",
    "қабылдау критерийлері өлшенетін және тексерілетін;",
    "бағалау, басымдық, спринт және жауапты адам көрсетілген;",
    "тәуелділіктер мен қажетті қолжетімділіктер анықталған;",
    "орындауды бастауға кедергі жоқ.",
])
add_heading(doc, "2.2 Definition of Done", 2)
add_bullets(doc, [
    "барлық қабылдау критерийлері орындалған және дәлелі тіркелген;",
    "тиісті тесттер сәтті орындалған;",
    "нәтижені тапсырманы орындамаған екінші команда мүшесі тексерген;",
    "нәтиже қолжетімді стендте, прототипте немесе репозиторийдегі ашылатын артефакт түрінде көрсетіледі;",
    "құжаттама мен сілтемелер жаңартылған;",
    "ашық ақау немесе шешілмеген блокер жоқ.",
])

add_heading(doc, "3 Екі спринттің жоспары және нәтижесі", 1)
add_table(
    doc,
    ["Спринт", "Кезең", "Пайдаланушы нәтижесі түріндегі мақсат", "Көрсетілген нәтиже"],
    [
        ["1", "16.09–29.09.2026", "ENUWay шешімінің жұмыс кеңістігі мен пилоттық зерттеу жоспарын көрсетуге дайын ету", "Workspace, GitHub байланыстары, сұхбат жоспары, жеткізу шешімі"],
        ["2", "30.09–13.10.2026", "Тапсырыс беруші MVP талаптарын, жеткізу жоспарын және аяқталу болжамын бірге бағалай алады", "ЛЗ 4 талаптар пакеті, ЛЗ 5 жоспары, ЛЗ 6 болжамы"],
    ],
    widths=[1.5, 3.4, 6.8, 5.2],
)

add_heading(doc, "4 Деректерді қалпына келтіру әдісі", 1)
add_body(doc, "Ағымдағы ENUWay GitHub Projects тақтасында Backlog күйінде 8, Ready күйінде 1, Review күйінде 1 карточка бар, ал In Progress және Done бос. Сондықтан tracker transition тарихынан екі аяқталған спринтті тікелей есептеу мүмкін емес. Команда бекіткен ретроспективті тәсілде In Progress уақыты ретінде жұмысты бастаған алғашқы commit, Done уақыты ретінде нәтижені аяқтаған соңғы commit алынды.")
add_body(doc, "Backlog күйінің басталуы спринттің бірінші күні деп қабылданды. Ready және Review уақыты Git тарихымен дәлелденбейді, сондықтан есепте n.a. ретінде көрсетілді. Осылайша дерек толық емес, бірақ мәндер ойдан қосылмайды.")
add_table(
    doc,
    ["ID", "Нәтиже", "Спринт", "Cycle time, сағ", "Жауапты"],
    [
        ["S1-01", "Workspace және GitHub байланыстары", "1", "13,60", "Нурислам"],
        ["S1-02", "Сұхбат жоспары және жеткізу шешімі", "1", "0,38", "Нурай"],
        ["S2-01", "ЛЗ 4 талаптар пакеті", "2", "0,65", "Альфараби"],
        ["S2-02", "ЛЗ 5 жеткізу жоспары", "2", "0,28", "Нурай"],
        ["S2-03", "ЛЗ 6 ықтималдық болжамы", "2", "2,83", "Нурислам"],
    ],
    widths=[1.8, 7.2, 2.0, 3.0, 3.0],
)

doc.add_page_break()
add_heading(doc, "5 Ағын метрикалары", 1)
add_body(doc, "Throughput - спринт ішінде Done күйіне жеткен элементтер саны. Cycle time - In Progress пен Done арасындағы уақыт. p85 - элементтердің 85 пайызы осы уақыттан кешікпей аяқталған шек. Орташа WIP уақытпен өлшеніп, барлық cycle time сағаттарының спринттің 336 сағатына қатынасы ретінде есептелді.")
add_table(
    doc,
    ["Метрика", "Спринт 1", "Спринт 2", "Өзгеріс"],
    [
        ["Throughput, элемент", "2", "3", "+1"],
        ["Орташа cycle time, сағ", "6,99", "1,25", "−5,74"],
        ["p85 cycle time, сағ", "11,62", "2,17", "−9,45"],
        ["Throughput, элемент/күн", "0,14", "0,21", "+0,07"],
        ["Уақытпен өлшенген орташа WIP", "0,042", "0,011", "−0,030"],
    ],
    widths=[7.0, 3.2, 3.2, 3.2],
)
add_body(doc, "Little’s Law тексеруі: WIP ≈ throughput/күн × орташа cycle time/24. Спринт 1 үшін 0,042 ≈ 0,143 × 6,99/24 = 0,042. Спринт 2 үшін 0,011 ≈ 0,214 × 1,25/24 = 0,011. Айырмашылық тек дөңгелектеуден пайда болады.")

if SUMMARY_IMAGE.exists():
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(SUMMARY_IMAGE), width=Inches(6.25))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run("1-сурет – Екі спринттің метрикаларын салыстыру")
    set_run_font(r, size=11, italic=True)

add_heading(doc, "6 Кумулятивті ағын диаграммасы және тар орын", 1)
add_body(doc, "CFD Спринт 1 элементтерінің 17 қыркүйекте аяқталғанын көрсетеді. Спринт 2-де екі элемент 1 қазанда, үшінші элемент 8 қазанда аяқталған. 2-спринтте бір элементтің Backlog жолағы 8 қазанға дейін сақталды. Сондықтан көрінетін тар орын In Progress ішінде емес, жұмысты бастауға дейінгі күтуде болды.")
if CFD_IMAGE.exists():
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(CFD_IMAGE), width=Inches(6.25))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run("2-сурет – Спринт 1 және Спринт 2 CFD")
    set_run_font(r, size=11, italic=True)

add_heading(doc, "7 Ретроспектива", 1)
add_body(doc, "Спринт 1 ретроспективасы Continue, Stop, Start форматында өткізілді. Команда commit арқылы дәлелдеуді жалғастыруды, бірнеше нәтижені бір үлкен жұмыс ретінде қарастыруды тоқтатуды және пакеттерді жеке қабылданатын элементтерге бөлуді бастауды белгіледі.")
add_body(doc, "Қабылданған әрекет: Спринт 2 жұмысын кемінде үш бөлек қабылданатын нәтижеге бөліп, әр нәтижені жеке соңғы commit-пен жабу. Иесі - Альфараби. Мерзімі - 13.10.2026. Өлшемі - кемінде 3 аяқталған элемент және әр элементке start/finish commit дәлелі.", bold_lead="Қабылданған әрекет:")
add_body(doc, "Әрекет өлшемі орындалды: Спринт 2-де үш бөлек нәтиже бар. Throughput өсті және cycle time қысқарды. Алайда бұл өзгерісті тек ретроспектива әрекетімен түсіндіруге болмайды, себебі элементтердің көлемі әртүрлі және board transition тарихы жоқ.")

add_heading(doc, "8 Шектеулер және келесі өлшеу тәртібі", 1)
add_bullets(doc, [
    "GitHub Projects тарихи transition дерегін бермегендіктен, Ready және Review уақыты есептелмеді;",
    "CFD-дегі Backlog басталуы спринт шекарасы ретінде қабылданды;",
    "метрикалар орындалған жұмысты дәлелдейді, бірақ карточкалардың сол күні қозғалғанын дәлелдемейді;",
    "келесі спринттерде карточка нақты кезең ауысқан күні жылжытылып, CSV немесе API арқылы экспортталады.",
])

add_heading(doc, "9 Қорытынды", 1)
add_body(doc, "ENUWay үшін нақты кезеңдері, WIP шектеулері және өту саясаттары бар жұмыс процесі анықталды. DoR және DoD репозиторийде жазылды. Екі спринттің дәлелді Git деректерінен throughput, орташа және p85 cycle time, уақытпен өлшенген WIP және CFD есептелді. Спринт 2-де throughput 3 элементке өсті, cycle time қысқарды, ал тар орын жұмысты бастауға дейінгі Backlog күтуінде байқалды. Есеп деректің шектеулерін жасырмайды және болашақта GitHub Projects-тен тікелей өлшеуге арналған тәртіпті бекітеді.")

add_heading(doc, "Пайдаланылған артефактілер", 1)
add_bullets(doc, [
    "GitHub Project: https://github.com/users/nypucjiam-create/projects/3",
    "ENUWay репозиторийі: https://github.com/nypucjiam-create/ENUWay",
    "lz9-tracker-export.csv және lz9-event-log.csv",
    "lz9-flow-metrics.xlsx",
    "dor-dod.md және retrospective.md",
])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(OUTPUT)
print(OUTPUT)
