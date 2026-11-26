from __future__ import annotations

import csv
import json
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs" / "pm-assistant"
RUN = BASE / "run"
OUT = BASE / "lz13-enuway-pm-assistant-report.docx"
FONT = "Times New Roman"
NAVY = "1F4E78"
BLUE = "D9EAF7"
LIGHT = "F4F7FA"


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=90, start=90, bottom=90, end=90) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for key, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{key}"))
        if node is None:
            node = OxmlElement(f"w:{key}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_begin, instr, fld_end])


def style_document(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(14)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    normal.paragraph_format.first_line_indent = Cm(1.25)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for style_name, size, color in (("Title", 20, NAVY), ("Heading 1", 16, NAVY), ("Heading 2", 14, NAVY)):
        style = doc.styles[style_name]
        style.font.name = FONT
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor.from_string(color)
        style._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        style.paragraph_format.keep_with_next = True
        style.paragraph_format.space_before = Pt(12)
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.first_line_indent = Cm(0)

    for section in doc.sections:
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(3)
        section.right_margin = Cm(1.5)
        section.header_distance = Cm(1)
        section.footer_distance = Cm(1)


def configure_section(section) -> None:
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(3)
    section.right_margin = Cm(1.5)
    section.header_distance = Cm(1)
    section.footer_distance = Cm(1)


def add_text(doc: Document, text: str, *, bold_prefix: str | None = None) -> None:
    p = doc.add_paragraph()
    if bold_prefix and text.startswith(bold_prefix):
        p.add_run(bold_prefix).bold = True
        p.add_run(text[len(bold_prefix) :])
    else:
        p.add_run(text)


def add_bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.left_indent = Cm(0.75)
        p.paragraph_format.first_line_indent = Cm(0)
        p.add_run(item)


def add_table(doc: Document, headers: list[str], rows: list[list[str]], widths=None) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    set_repeat_table_header(table.rows[0])
    for idx, header in enumerate(headers):
        cell = table.rows[0].cells[idx]
        cell.text = header
        set_cell_shading(cell, NAVY)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        for run in cell.paragraphs[0].runs:
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.bold = True
            run.font.name = FONT
            run.font.size = Pt(10)
    for row_index, values in enumerate(rows):
        cells = table.add_row().cells
        for col, value in enumerate(values):
            cells[col].text = str(value)
            cells[col].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cells[col])
            if row_index % 2:
                set_cell_shading(cells[col], LIGHT)
            for p in cells[col].paragraphs:
                p.paragraph_format.first_line_indent = Cm(0)
                p.paragraph_format.line_spacing = 1
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for run in p.runs:
                    run.font.name = FONT
                    run.font.size = Pt(9)
        if widths:
            for cell, width in zip(cells, widths):
                cell.width = Cm(width)


def add_title_page(doc: Document) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    for line in (
        "ҚАЗАҚСТАН РЕСПУБЛИКАСЫНЫҢ ҒЫЛЫМ ЖӘНЕ ЖОҒАРЫ БІЛІМ МИНИСТРЛІГІ",
        "Л.Н. ГУМИЛЕВ АТЫНДАҒЫ ЕУРАЗИЯ ҰЛТТЫҚ УНИВЕРСИТЕТІ",
    ):
        run = p.add_run(line + "\n")
        run.bold = True
        run.font.name = FONT
        run.font.size = Pt(14)

    doc.add_paragraph("\n\n\n")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run("ЗЕРТХАНАЛЫҚ ЖҰМЫС № 13")
    run.bold = True
    run.font.name = FONT
    run.font.size = Pt(20)
    run.font.color.rgb = RGBColor.from_string(NAVY)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    run = p.add_run("ENUWay жобасына арналған PM ИИ-ассистенті")
    run.bold = True
    run.font.name = FONT
    run.font.size = Pt(16)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.add_run("Пәні: IT-жобаларды басқару").italic = True

    doc.add_paragraph("\n\n\n")
    table = doc.add_table(rows=4, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.RIGHT
    table.autofit = False
    values = [
        ("Орындағандар:", "Альфараби, Нурай, Нурислам"),
        ("Жоба:", "ENUWay"),
        ("Тексерген:", "Самбетбаева Мадина Аралбаевна"),
        ("Оқу жылы:", "2026"),
    ]
    for row, (left, right) in zip(table.rows, values):
        row.cells[0].text = left
        row.cells[1].text = right
        row.cells[0].width = Cm(4.5)
        row.cells[1].width = Cm(9.5)
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.first_line_indent = Cm(0)
                p.paragraph_format.line_spacing = 1
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            cell._tc.get_or_add_tcPr().append(OxmlElement("w:tcBorders"))
    doc.add_paragraph("\n\n\n")
    p = doc.add_paragraph("Астана, 2026")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    p.add_run().add_break(WD_BREAK.PAGE)


def build() -> None:
    facts = json.loads((RUN / "source-data.json").read_text(encoding="utf-8"))
    metrics = json.loads((RUN / "run-metrics.json").read_text(encoding="utf-8"))
    raw_report = (RUN / "generated-status-report.md").read_text(encoding="utf-8").strip()
    with (BASE / "verification-log.csv").open(encoding="utf-8-sig", newline="") as fh:
        verification = list(csv.DictReader(fh))

    doc = Document()
    style_document(doc)
    add_title_page(doc)
    configure_section(doc.sections[0])
    doc.sections[0].different_first_page_header_footer = True

    doc.add_heading("МАЗМҰНЫ", level=1)
    contents = [
        "Кіріспе",
        "1. Автоматтандырылатын PM процесі",
        "2. Автоматтандырудың архитектурасы және іске асырылуы",
        "3. Екі спринттің нақты дерегі",
        "4. ИИ жасаған есеп және қолмен тексерілген нұсқа",
        "5. Сапаны тексеру журналы",
        "6. Уақыт тиімділігін бағалау",
        "7. Промпт және команда нұсқаулығы",
        "Қорытынды",
        "Пайдаланылған дереккөздер",
        "Қосымшалар",
    ]
    add_bullets(doc, contents)

    doc.add_heading("КІРІСПЕ", level=1)
    add_text(doc, "Зертханалық жұмыстың мақсаты — ENUWay жобасының нақты GitHub деректерінен апталық статус-есептің черновигін жасайтын, тегін және қайталанатын PM ИИ-ассистентін құру, оның сапасын фактілермен қолмен салыстыру және автоматтандырудың таза уақыт үнемін өлшеу.")
    add_text(doc, "Негізгі қағида: модель дерек көзі емес. Коммит, issue, күн және сілтеме GitHub REST API арқылы алынады; модель тек құрылымдалған фактілерден мәтін құрастырады. Жариялау алдында PM әр фактіні тексеріп, табылған қатені журналға енгізеді.")
    add_bullets(doc, [
        "екі өткен спринттің нақты дерегін автоматты жинау;",
        "жергілікті модель арқылы қазақша статус-есеп черновигін жасау;",
        "әр сан мен міндетті бөлімді бастапқы дерекпен салыстыру;",
        "қате үлесі мен тексеру уақытын есептеу;",
        "командаға промпт, іске қосу және құпиялылық нұсқаулығын беру.",
    ])

    doc.add_heading("1. АВТОМАТТАНДЫРЫЛАТЫН PM ПРОЦЕСІ", level=1)
    add_text(doc, "Таңдалған процесс — GitHub трекері мен репозиторийінен екі өткен спринт бойынша апталық статус-есеп черновигін дайындау және тәуекелді көрінетін ету. Бұл процесс апта сайын қайталанады, қолмен санақ пен сілтеме жинауға уақыт кетіреді және қате көшіруге бейім.")
    add_table(doc, ["Қадам", "Кіріс", "Нәтиже", "Бақылау"], [
        ["1. Дерек жинау", "GitHub commits және issues", "source-data.json", "API жауабы өзгертілмей сақталады"],
        ["2. Факт дайындау", "Спринт шекарасы, коммиттер, issue", "Қысқартылған JSON", "Сан кодпен есептеледі"],
        ["3. Мәтін генерациясы", "Факт JSON + промпт", "Черновик есеп", "Модель жаңа факт қоспауға міндетті"],
        ["4. Верификация", "Черновик + source-data.json", "Қате журналы", "PM әр бақылау нүктесін тексереді"],
        ["5. Жариялау", "Түзетілген есеп", "Тексерілген статус", "Автоматты жариялау жоқ"],
    ], [2.2, 4.2, 4.2, 4.0])

    doc.add_heading("2. АВТОМАТТАНДЫРУДЫҢ АРХИТЕКТУРАСЫ ЖӘНЕ ІСКЕ АСЫРЫЛУЫ", level=1)
    add_table(doc, ["GitHub REST API", "Python сценарийі", "Жергілікті модель", "PM тексеруі"], [["commits + issues", "фактіні сүзу және сақтау", "қазақша черновик", "журнал + түзетілген есеп"]])
    add_text(doc, "`scripts/pm_status_assistant.py` тек стандартты Python кітапханасын қолданады. Қоғамдық репозиторийге токенсіз сұрау жасай алады; GitHub Actions ішінде уақытша GITHUB_TOKEN тек HTTP тақырыбында қолданылады және модель промптына енгізілмейді. Сценарий Ollama-ның `/api/generate` интерфейсін және тек зертханалық өлшем үшін OpenAI-үйлесімді жергілікті llama.cpp серверін қолдайды.")
    add_text(doc, "`.github/workflows/pm-status-assistant.yml` дүйсенбі сайын 03:15 UTC-де немесе қолмен іске қосылады. Жұмыс ортасы Ollama орнатып, qwen2.5:0.5b моделін жүктейді, сценарийді орындайды және нәтижені GitHub Actions artifact ретінде сақтайды. Есеп репозиторийге автоматты commit жасамайды: бұл қате мәтінді жариялап жіберу тәуекелін азайтады.")
    add_text(doc, "Сәтсіз модель шақыруы бүкіл процесті тоқтатпайды. Детерминирленген резервтік есеп спринт коммиттері мен ашық issue санын кодпен шығарады және модель қатесін `run-metrics.json` файлына жазады.")

    doc.add_heading("3. ЕКІ СПРИНТТІҢ НАҚТЫ ДЕРЕГІ", level=1)
    sprint_rows = []
    for sprint in facts["sprints"]:
        sprint_rows.append([sprint["name"], sprint["start"], sprint["end_exclusive"], str(sprint["commit_count"])])
    add_table(doc, ["Спринт", "Басталуы", "Аяқталуы (кірмейді)", "Коммит"], sprint_rows, [2.3, 4.4, 4.4, 2.0])
    for sprint in facts["sprints"]:
        doc.add_heading(sprint["name"], level=2)
        rows = [[c["date"], c["sha"], c["message"]] for c in sprint["commits"]]
        add_table(doc, ["UTC күні", "SHA", "Коммит хабарламасы"], rows, [4.0, 2.2, 8.0])
    open_issues = [i for i in facts["issues"] if i["state"] == "open"]
    closed_issues = [i for i in facts["issues"] if i["state"] == "closed"]
    unassigned = sum(not i["assignees"] for i in open_issues)
    unlabeled = sum(not i["labels"] for i in open_issues)
    add_text(doc, f"Issue қорытындысы: барлығы {len(facts['issues'])}, ашық {len(open_issues)}, жабық {len(closed_issues)}. Ашық тапсырмалардың {unassigned}-інде орындаушы, {unlabeled}-інде белгі жоқ. Бұл сандар модельмен емес, сақталған JSON-нан код арқылы есептелді.")

    doc.add_heading("4. ИИ ЖАСАҒАН ЕСЕП ЖӘНЕ ҚОЛМЕН ТЕКСЕРІЛГЕН НҰСҚА", level=1)
    doc.add_heading("4.1 Модельдің өзгертілмеген жауабы", level=2)
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = 1
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(raw_report)
    run.font.name = "Consolas"
    run.font.size = Pt(9)
    add_text(doc, "Модель жауабы әдейі түзетілмей берілді. Ол бірінші спринттің басталу күнін бір күнге ығыстырды және екінші спринттің мәтінін аяқтамай тоқтады. Сондықтан есеп жариялауға жарамсыз болды.")
    doc.add_heading("4.2 PM тексерген қорытынды", level=2)
    add_text(doc, "Тексерілген нұсқада 1-спринт 16–30 қыркүйек аралығында 3 коммитпен, 2-спринт 30 қыркүйек–14 қазан аралығында 10 коммитпен көрсетілді. Репозиторийде 37 ашық және 1 жабық issue болды. 28 ашық тапсырмада орындаушы, 18 тапсырмада белгі болмағандықтан, олар жоспарлау тәуекелі ретінде көрсетілді.")
    add_bullets(doc, [
        "28 ашық тапсырмаға орындаушы тағайындау;",
        "18 белгісіз тапсырмаға жұмыс түрі мен басымдық белгісін беру;",
        "келесі есепте жабылған issue және қабылданған pull request санын бөлек көрсету;",
        "әр санды source-data.json және GitHub сілтемесімен тексеру.",
    ])

    doc.add_heading("5. САПАНЫ ТЕКСЕРУ ЖУРНАЛЫ", level=1)
    rows = []
    for item in verification:
        rows.append([item["ID"], item["Тексеру нысаны"], item["Нәтиже"], item["Қате түрі"], item["Түзету"]])
    add_table(doc, ["ID", "Нысан", "Нәтиже", "Қате түрі", "Түзету"], rows, [1.2, 3.8, 1.7, 3.1, 4.5])
    add_text(doc, "Он бақылау нүктесінің үшеуі дұрыс, жетеуі қате немесе толық емес болды. Қате үлесі 7/10 = 70%. Бұл көрсеткіш міндетті бөлімдерді өткізіп кетуді де қамтиды, өйткені PM үшін толық емес статус-есеп те сапа қатесі болып саналады. Қолмен тексеруге 50 секунд жұмсалды.")

    doc.add_heading("6. УАҚЫТ ТИІМДІЛІГІН БАҒАЛАУ", level=1)
    add_table(doc, ["Сценарий", "Генерация, с", "Тексеру, с", "Барлығы, с", "Қолмен салыстыру"], [
        ["Жергілікті Qwen2.5 3B", "510,613", "50", "560,613", "−480,093 с"],
        ["Детерминирленген резерв", "2,807", "50", "52,807", "+27,713 с"],
        ["Қолмен тексерілген есеп", "80,520", "—", "80,520", "базалық мән"],
    ], [3.6, 2.6, 2.5, 2.5, 3.1])
    add_text(doc, f"Нақты өлшемде модель генерациясы {metrics['model_generation_seconds']} секунд, толық сценарий {metrics['total_run_seconds']} секунд болды. Формула: таза үнем = қолмен орындау уақыты − (автоматтандыру + тексеру). 80,520 − (510,613 + 50) = −480,093 секунд. Демек, осы компьютердегі 3B модель таза уақыт үнемдемеді.")
    add_text(doc, "Тиімді шешім — сандар мен тәуекел индикаторларын детерминирленген Python кодымен дайындау, ал ИИ-ді тек қысқа мәтінді редакциялауға қолдану. GitHub Actions-тағы 0,5B модель бөлек өлшенбейінше, оның экономиясы туралы қорытынды жасалмайды.")

    doc.add_heading("7. ПРОМПТ ЖӘНЕ КОМАНДА НҰСҚАУЛЫҒЫ", level=1)
    add_text(doc, "Промпт рөлді, нақты кірісті, міндетті бес бөлімді, ойдан қоспау шектеуін және PM тексеру талабын бекітеді. Нақты орындалған мәтін `run/prompt-used.txt`, қайта қолданылатын үлгі `prompt-template.md` файлында сақталған.")
    add_text(doc, "Команда алдымен Ollama мен qwen2.5:0.5b моделін дайындайды, сценарийді іске қосады, шыққан төрт файлды ашады және барлық фактіні source-data.json арқылы тексереді. Тек содан кейін verified-status-report.md нұсқасы бөлісіледі.")
    add_text(doc, "Модельге жіберуге тыйым салынған деректер:")
    add_bullets(doc, [
        "ЖСН, телефон, жеке e-mail, нақты маршрут және геолокация;",
        "GitHub токені, құпиясөз, API кілті, cookie және session идентификаторы;",
        "тапсырыс берушінің жарияланбаған коды мен құжаттары;",
        "коммерциялық құпия және рұқсатсыз адам бағасы.",
    ])
    add_text(doc, "Зертханада тек қоғамдық репозиторий метадерегі қолданылды. Токен HTTP тақырыбынан тыс шықпайды. Модель жауабы автоматты жарияланбайды.")

    doc.add_heading("ҚОРЫТЫНДЫ", level=1)
    add_text(doc, "ЛЗ 13 бойынша ENUWay үшін жұмыс істейтін PM автоматтандыруы жасалды: GitHub API-ден нақты дерек жиналады, екі спринт өңделеді, жергілікті модель черновик жасайды, GitHub Actions апта сайын іске қосады, ал модель қатесі болғанда қауіпсіз резервтік есеп құрылады. Толық дәлел пакеті бастапқы JSON-ды, өзгертілмеген модель жауабын, он тармақтық тексеру журналын, түзетілген есепті, промпт пен құпиялылық нұсқаулығын қамтиды.")
    add_text(doc, "Сапа тексеруі модельдің 70% бақылау нүктесінде қате не толық емес нәтиже бергенін көрсетті. 3B модельдің жергілікті орындалуы таза үнем бермеді. Сондықтан ИИ ақиқат көзі ретінде емес, PM тексеретін мәтіндік үдеткіш ретінде ғана қабылданды. Детерминирленген резервтік жол 27,713 секунд үнемдеді және осы жоба үшін сенімдірек негіз болып шықты.")

    doc.add_heading("ПАЙДАЛАНЫЛҒАН ДЕРЕККӨЗДЕР", level=1)
    sources = [
        "1. ENUWay репозиторийі: https://github.com/nypucjiam-create/ENUWay",
        "2. GitHub Docs. REST API endpoints for commits: https://docs.github.com/en/rest/commits/commits",
        "3. GitHub Docs. Workflow syntax and schedule: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax",
        "4. Ollama. API / generate: https://github.com/ollama/ollama/blob/main/docs/api.md",
        "5. ЛЗ 13 тапсырмасы мен дәріс слайдтары, 13-апта.",
    ]
    for source in sources:
        p = doc.add_paragraph(source)
        p.paragraph_format.first_line_indent = Cm(0)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT

    doc.add_heading("ҚОСЫМША А. АРТЕФАКТІЛЕР ТІЗІМІ", level=1)
    add_table(doc, ["Файл", "Мақсаты"], [
        ["scripts/pm_status_assistant.py", "GitHub API және модель автоматтандыруы"],
        [".github/workflows/pm-status-assistant.yml", "Апталық cron және қолмен іске қосу"],
        ["run/source-data.json", "Нақты деректің өзгермеген көшірмесі"],
        ["run/generated-status-report.md", "Модельдің бастапқы жауабы"],
        ["verification-log.csv", "Қате және түзету журналы"],
        ["verified-status-report.md", "PM тексерген есеп"],
        ["prompt-template.md", "Қайта қолданылатын промпт"],
        ["team-instruction.md", "Команда және құпиялылық нұсқаулығы"],
    ], [7.0, 7.0])

    doc.add_heading("ҚОСЫМША Ә. ҚАЙТАЛАУ КОМАНДАЛАРЫ", level=1)
    for command in (
        "ollama pull qwen2.5:0.5b",
        "python scripts/pm_status_assistant.py --provider ollama --model qwen2.5:0.5b",
        "pytest -q tests/test_lz13_pm_assistant.py",
    ):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.line_spacing = 1
        run = p.add_run(command)
        run.font.name = "Consolas"
        run.font.size = Pt(10)

    for section in doc.sections:
        configure_section(section)
        if not section.footer.paragraphs:
            section.footer.add_paragraph()
        section.footer.paragraphs[0].clear()
        add_page_number(section.footer.paragraphs[0])
        section.first_page_footer.paragraphs[0].clear()
    doc.core_properties.title = "ЛЗ 13. ENUWay PM ИИ-ассистенті"
    doc.core_properties.subject = "IT-жобаларды басқару"
    doc.core_properties.author = "Альфараби, Нурай, Нурислам"
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
