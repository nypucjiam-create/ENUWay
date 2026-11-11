from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
FONT = "Times New Roman"
NAVY = "1F4E78"
PALE = "DCE6F1"
LIGHT = "F3F6F9"
BORDER = "D9D9D9"


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=90, start=110, bottom=90, end=110) -> None:
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


def set_table_borders(table) -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = borders.find(qn(f"w:{edge}"))
        if node is None:
            node = OxmlElement(f"w:{edge}")
            borders.append(node)
        node.set(qn("w:val"), "single")
        node.set(qn("w:sz"), "4")
        node.set(qn("w:color"), BORDER)


def set_repeat_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    marker = OxmlElement("w:tblHeader")
    marker.set(qn("w:val"), "true")
    tr_pr.append(marker)


def keep_row_together(row) -> None:
    """Prevent a table row from being split across two pages."""
    tr_pr = row._tr.get_or_add_trPr()
    tr_pr.append(OxmlElement("w:cantSplit"))


def style_run(run, size=14, bold=False, italic=False, color="000000") -> None:
    run.font.name = FONT
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), FONT)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), FONT)
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), FONT)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)


def configure_document(doc: Document) -> None:
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
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for name, size in (("Title", 18), ("Heading 1", 16), ("Heading 2", 14)):
        style = doc.styles[name]
        style.font.name = FONT
        style._element.rPr.rFonts.set(qn("w:ascii"), FONT)
        style._element.rPr.rFonts.set(qn("w:hAnsi"), FONT)
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.first_line_indent = Cm(0)
        style.paragraph_format.space_before = Pt(12)
        style.paragraph_format.space_after = Pt(6)


def add_page_number(section) -> None:
    paragraph = section.footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.first_line_indent = Cm(0)
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_char1, instr, fld_char2])
    style_run(run, size=12)


def add_cover(doc: Document, lab: str, title: str, subtitle: str) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    style_run(p.add_run("Л.Н. Гумилев атындағы Еуразия ұлттық университеті"), 14, True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    style_run(p.add_run("Ақпараттық технологиялар факультеті"), 14)

    for _ in range(5):
        doc.add_paragraph()

    p = doc.add_paragraph(style="Title")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    style_run(p.add_run(lab), 16, True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    style_run(p.add_run(title), 18, True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    style_run(p.add_run(subtitle), 14)

    for _ in range(5):
        doc.add_paragraph()

    for label, value in (
        ("Орындаушылар", "Альфараби, Нурай, Нурислам"),
        ("Пән", "IT жобаларын басқару"),
        ("Оқу жылы", "2026–2027"),
    ):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.first_line_indent = Cm(0)
        style_run(p.add_run(f"{label}: "), 14, True)
        style_run(p.add_run(value), 14)

    for _ in range(3):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    style_run(p.add_run("Астана 2026"), 14)
    doc.add_page_break()


def add_heading(doc: Document, text: str, level=1) -> None:
    p = doc.add_paragraph(style=f"Heading {level}")
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.add_run(text)


def add_para(doc: Document, text: str, bold_lead: str | None = None) -> None:
    p = doc.add_paragraph()
    if bold_lead and text.startswith(bold_lead):
        style_run(p.add_run(bold_lead), 14, True)
        style_run(p.add_run(text[len(bold_lead) :]), 14)
    else:
        style_run(p.add_run(text), 14)


def add_bullets(doc: Document, items: list[str]) -> None:
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.left_indent = Cm(0.75)
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.line_spacing = 1.25
        style_run(p.add_run(item), 14)


def add_table(doc: Document, headers: list[str], rows: list[list[str]], widths: list[float] | None = None) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)
    set_repeat_header(table.rows[0])
    keep_row_together(table.rows[0])
    for index, header in enumerate(headers):
        cell = table.rows[0].cells[index]
        set_cell_shading(cell, NAVY)
        set_cell_margins(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.line_spacing = 1.0
        style_run(p.add_run(header), 10, True, color="FFFFFF")
        if widths:
            cell.width = Cm(widths[index])
    for row_index, values in enumerate(rows):
        row = table.add_row()
        keep_row_together(row)
        cells = row.cells
        for index, value in enumerate(values):
            cell = cells[index]
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if row_index % 2:
                set_cell_shading(cell, LIGHT)
            p = cell.paragraphs[0]
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.0
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if len(value) > 18 else WD_ALIGN_PARAGRAPH.CENTER
            style_run(p.add_run(str(value)), 10)
            if widths:
                cell.width = Cm(widths[index])
    doc.add_paragraph()


def add_contents(doc: Document, items: list[str]) -> None:
    add_heading(doc, "Мазмұны", 1)
    for index, item in enumerate(items, 1):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Cm(0)
        style_run(p.add_run(f"{index}. {item}"), 14)
    doc.add_page_break()


def build_lz10(metrics: dict) -> Path:
    doc = Document()
    configure_document(doc)
    add_cover(
        doc,
        "№ 10 зертханалық жұмыс",
        "ENUWay CI CD пайплайны және DORA бақылау тақтасы",
        "Автоматты сапа қақпалары, жеткізу метрикалары және релиз жоспары",
    )
    add_contents(
        doc,
        [
            "Жұмыстың мақсаты мен көлемі",
            "Тексерілетін ENUWay инкременті",
            "CI CD пайплайны",
            "Негізгі тармақты қорғау",
            "DORA анықтамалары және дерек көзі",
            "Нақты метрикалар мен талдау",
            "Жақсарту жоспары",
            "Релиз жоспары және кері қайтару",
            "Қорытынды және сәйкестік",
        ],
    )

    add_heading(doc, "1 Жұмыстың мақсаты мен көлемі")
    add_para(doc, "Жұмыстың мақсаты — ENUWay өзгерістерін қайталанатын автоматты тексерулер арқылы жеткізу, репозиторийдің нақты тарихынан төрт DORA көрсеткішін есептеу және тәуекелі басқарылатын релиз тәртібін бекіту. Нәтижесінде жұмыс істейтін GitHub Actions пайплайны, қайта орындалатын DORA скрипті, бақылау тақтасы, негізгі тармақ саясаты, релиз және кері қайтару чек-листері дайындалды.")

    add_heading(doc, "2 Тексерілетін ENUWay инкременті")
    add_para(doc, "Пайплайн бос құжат репозиторийіне емес, жұмыс істейтін оқу инкрементіне қосылды. Инкремент US-03 сапар іздеу, US-05 сапар құру, US-06 орын санын шектеу және US-08 броньдау талаптарын орындайтын Python сервисінен тұрады.")
    add_bullets(doc, ["Flask негізіндегі HTTP интерфейсі және health-check;", "артық, қайталанған және тексерілмеген броньды тоқтататын домендік ережелер;", "11 автоматты тест және 60% міндетті қамту шегі;", "Docker арқылы қайталанатын құрастыру;", "жасанды тест деректерін тұрақты seed арқылы генерациялау."])

    add_heading(doc, "3 CI CD пайплайны")
    add_table(
        doc,
        ["Қадам", "Мақсаты", "Сәтсіз болса"],
        [
            ["Checkout және Python", "бірдей орта дайындау", "пайплайн тоқтайды"],
            ["Ruff", "код сапасын тексеру", "merge рұқсат етілмейді"],
            ["pytest және coverage", "мінез-құлық пен 60% шекті тексеру", "релиз жасалмайды"],
            ["Compile және test data", "құрастыру мен қайталанатын деректі тексеру", "артефакт жасалмайды"],
            ["Docker build", "жеткізу бейнесін құрастыру", "жариялау тоқтайды"],
            ["Trivy және gitleaks", "жоғары осалдық пен құпияны табу", "quality gate қызыл"],
            ["Upload artifact", "commit SHA-ға байланған архив жариялау", "жариялау сәтсіз"],
        ],
        [3.2, 8.0, 5.0],
    )
    add_para(doc, "Пайплайнның уақыт шегі 10 минут. GitHub Actions ішіндегі әр іске қосылым commit SHA және нәтижемен сақталады. Бұл тарих DORA есептеуінің бастапқы дерегі болып табылады.")

    add_heading(doc, "4 Негізгі тармақты қорғау")
    add_para(doc, "Команда саясаты бойынша main тармағына тікелей push жасалмайды. Өзгеріс pull request, кемінде бір approval және CI / quality-gate міндетті тексеруі арқылы енгізіледі. Тармақ өмірі үш күннен аспайды. Қауіпсіздікке, жеке дерекке немесе броньға әсер ететін өзгеріс жеке risk review алады.")

    add_heading(doc, "5 DORA анықтамалары және дерек көзі")
    add_table(
        doc,
        ["Көрсеткіш", "ENUWay анықтамасы", "Дерек"],
        [
            ["Жариялау жиілігі", "main CI өтіп, нұсқаланған архив жарияланды", "GitHub Actions API"],
            ["Жеткізу уақыты", "commit-тен сәтті CI аяқталғанға дейін", "commit және run уақыты"],
            ["Сәтсіз өзгеріс үлесі", "main CI сәтсіз немесе 24 сағатта түзету қажет", "run conclusion"],
            ["Қалпына келу уақыты", "сәтсіз CI-дан келесі жасыл CI-ға дейін", "run тарихы және incident log"],
        ],
        [3.5, 8.3, 4.5],
    )
    add_para(doc, "scripts/dora.py GitHub API-дан тек ENUWay main тармағының CI тарихын алады. Public репозиторий үшін токен міндетті емес; қолданылса, ол GH_TOKEN орта айнымалысынан оқылады және кодқа жазылмайды.")

    add_heading(doc, "6 Нақты метрикалар мен талдау")
    def value(key, suffix=""):
        raw = metrics.get(key)
        return "дерек жоқ" if raw is None else f"{raw}{suffix}"
    add_table(
        doc,
        ["Көрсеткіш", "Мән", "Бағалау"],
        [
            ["Аяқталған CI", value("completed_runs"), "қысқа бақылау терезесі"],
            ["Сәтті жариялау", value("successful_deployments"), "нақты GitHub тарихы"],
            ["Апталық жиілік", value("deployment_frequency_per_week"), "бастапқы бақылау"],
            ["Медианалық жеткізу уақыты", value("median_lead_time_minutes", " мин"), "commit → жасыл CI"],
            ["Сәтсіз өзгеріс үлесі", value("change_failure_rate_percent", "%"), "қысқа тарихта құбылмалы"],
            ["Орташа қалпына келу", value("mean_time_to_restore_minutes", " мин"), "мақсат < 60 мин"],
        ],
        [5.0, 4.2, 7.1],
    )
    add_para(doc, "Оннан аз run бойынша командаға тұрақты DORA деңгейін беру дұрыс емес. Сондықтан ағымдағы деңгей «бастапқы бақылау, дерек жеткіліксіз» деп белгіленді. Бұл шектеу есептен жасырылмайды және 27.11.2026 күні қайта есептеледі.")

    add_heading(doc, "7 Жақсарту жоспары")
    add_table(
        doc,
        ["Жақсарту", "Иесі", "Мерзімі", "Күтілетін әсер"],
        [
            ["PR кезінде 10 минуттан аспайтын міндетті CI", "Альфараби", "20.11.2026", "сәтсіз өзгеріс 0–20%, feedback p95 < 10 мин"],
            ["Health smoke-тест және 6 сағаттық тексеру", "Нурислам", "24.11.2026", "анықтау < 20 мин, MTTR < 60 мин"],
        ],
        [7.0, 2.8, 3.0, 6.0],
    )
    add_para(doc, "Алғашқы төрт аптада capacity-дің 15%-ы сенімділікке бөлінеді. Сәтсіз өзгеріс үлесі 20%-дан асса, уақытша 25%-ға өседі; екі өлшеуде 10%-дан төмен болса, 10%-ға қайтарылады.")

    add_heading(doc, "8 Релиз жоспары және кері қайтару")
    add_table(
        doc,
        ["Нұсқа", "Терезе", "Жауапты", "Мақсат"],
        [
            ["0.1", "13.11.2026 15:00", "Альфараби", "іздеу, құру, броньдау"],
            ["0.2", "20.11.2026 15:00", "Нурай", "UAT түзетулері"],
            ["0.3", "27.11.2026 15:00", "Нурислам", "мониторинг және пилот кандидаты"],
        ],
        [2.0, 4.2, 3.2, 8.0],
    )
    add_para(doc, "Кері қайтару шешімін Альфараби 10 минут ішінде жеке қабылдайды. Триггерлер: health-check екі рет өтпеді, бронь жоғалды немесе қайталанды, қате үлесі 5%-дан асты, қауіпсіздік тәуекелі анықталды. Алдыңғы жасыл артефакт қалпына келтіріліп, үш негізгі smoke-тест пен 30 минуттық бақылау орындалады.")

    add_heading(doc, "9 Қорытынды және сәйкестік")
    add_para(doc, "ЛЗ 10 артефактілері әдістемедегі міндетті құрамды қамтиды: жұмыс істейтін CI, төрт DORA көрсеткіші, нақты репозиторий дерегі, екі сандық жақсарту, релиз жоспары және кері қайтару чек-листі. Action нұсқасы мен импорт жолына байланысты алғашқы қызыл run-дар жасырылмай, нақты инцидент және DORA change failure дерегі ретінде тіркелді.")
    add_para(doc, "ЖИ қолданылуы: OpenAI Codex код пен құжаттың бастапқы нұсқасын, тексеру сценарийлерін және пішімдеуді дайындауға қолданылды. Нақты GitHub run нәтижелері API арқылы алынған; команда мазмұн мен допущениелерді қорғауға дейін тексереді.")

    add_page_number(doc.sections[0])
    path = ROOT / "docs" / "dora" / "lz10-enuway-ci-dora-report.docx"
    doc.save(path)
    return path


def build_lz11(metrics: dict) -> Path:
    doc = Document()
    configure_document(doc)
    add_cover(
        doc,
        "№ 11 зертханалық жұмыс",
        "ENUWay тестілеу жоспары UAT және инцидентті талдау",
        "Сапа стратегиясы, қабылдау хаттамасы, postmortem және runbook",
    )
    add_contents(
        doc,
        [
            "Мақсат және тексерілетін инкремент",
            "Тестілеу стратегиясы",
            "Тест деректері және орталар",
            "Нефункционалдық талаптарды тексеру",
            "UAT сценарийлері",
            "Қабылдау хаттамасы және ескертулер",
            "Кінәсіз postmortem",
            "Үш жүйелік әрекет",
            "Runbook және мониторинг",
            "Қорытынды және шектеу",
        ],
    )

    add_heading(doc, "1 Мақсат және тексерілетін инкремент")
    add_para(doc, "Мақсат — ENUWay сапасын релизден кейін емес, талап пен әзірлеу сәтінен басқару. Тексерілетін инкремент сапарды бағытпен іздеуді, сапар құруды, 1–4 орын шегін, тексерілген аккаунттың броньдауын және артық броньды болдырмауды қамтиды.")

    add_heading(doc, "2 Тестілеу стратегиясы")
    add_table(
        doc,
        ["Деңгей", "Үлес", "Құрал", "Іске қосу"],
        [
            ["Модульдік", "45%", "pytest", "әр commit және PR"],
            ["Интеграциялық API", "25%", "Flask test client", "әр commit және PR"],
            ["Сквозной", "10%", "Playwright", "релиз кандидаты"],
            ["Жүктемелік", "10%", "k6", "релиз кандидаты"],
            ["Қолмен және UAT", "10%", "хаттама", "әр инкремент"],
        ],
        [4.2, 2.2, 5.0, 6.0],
    )
    add_para(doc, "Қайталанатын функционалдық тексерулердің автоматтандыру мақсаты — кемінде 80%. CI quality gate құрамында Ruff, pytest, 60% қамту шегі, Docker build, Trivy және gitleaks бар. Қазіргі автоматты қамту CI run журналында өлшенеді.")

    add_heading(doc, "3 Тест деректері және орталар")
    add_para(doc, "Тест ортасында нақты студенттің аты, телефоны, e-mail-ы немесе сапар тарихы қолданылмайды. scripts/generate_test_data.py seed=20261112 арқылы 20 жасанды жазбаны қайталанатын түрде жасайды. Бұл бір ақауды әр қатысушыда бірдей дерекпен қайта көрсетуге мүмкіндік береді.")
    add_table(
        doc,
        ["Орта", "Мақсат", "Дерек", "Жауапты"],
        [
            ["Локалдық", "әзірлеу", "жасанды", "әр әзірлеуші"],
            ["CI", "сапа қақпасы", "әр run жаңа seed", "GitHub Actions"],
            ["Оқу стенді", "UAT және жүктеме", "жасанды тұрақты seed", "Альфараби"],
            ["Алдын ала өндірістік", "smoke және релиз кандидаты", "анонимденген не жасанды", "Нурислам"],
        ],
        [4.2, 5.0, 5.7, 3.2],
    )

    add_heading(doc, "4 Нефункционалдық талаптарды тексеру")
    add_table(
        doc,
        ["Талап", "Сценарий", "Өту шарты"],
        [
            ["NFT-PERF-01", "30 VU арқылы іздеу", "3 минут, p95 < 800 мс"],
            ["NFT-REL-01", "жүктемедегі қате", "қате үлесі < 1%"],
            ["NFT-SEC-01", "тексерілмеген бронь", "0 рұқсатсыз бронь"],
            ["NFT-DATA-01", "тест дерегі", "0 нақты жеке дерек"],
        ],
        [4.0, 7.0, 7.0],
    )

    add_heading(doc, "5 UAT сценарийлері")
    scenarios = [
        ["UAT-01", "Бағыт бойынша сапар табу", "сәйкес сапар, уақыт және бос орын көрінеді"],
        ["UAT-02", "Нәтиже жоқ іздеу", "түсінікті бос күй және келесі әрекет"],
        ["UAT-03", "Жарамды сапар құру", "бір сапар жасалып, тізімде көрінеді"],
        ["UAT-04", "Міндетті өріс бос", "сапар жасалмайды, өріс белгіленеді"],
        ["UAT-05", "5 орын енгізу", "1–4 шегі көрсетіледі"],
        ["UAT-06", "Бос орынға қосылу", "бронь расталып, орын 1-ге азаяды"],
        ["UAT-07", "Орын жоқ кезде бронь", "бронь жоқ, сан теріс емес"],
        ["UAT-08", "Тексерілмеген аккаунт", "бронь жоқ, тексеру ұсынылады"],
        ["UAT-09", "Қайталанған бронь", "екінші бронь және азаю жоқ"],
        ["UAT-10", "Бөтен сапарды өзгерту", "өзгеріс жоқ, рұқсат қатесі"],
    ]
    add_table(doc, ["ID", "Пайдаланушы әрекеті", "Өту критерийі"], scenarios, [2.2, 7.5, 8.0])

    add_heading(doc, "6 Қабылдау хаттамасы және ескертулер")
    add_para(doc, "13.11.2026 күні 14:00–14:40 сыртқы UAT сессиясына арналған хаттама дайындалды. Әзірлеушілер нұсқау бермей, тек уақыт пен ескертуді жазады. Ішкі dry run кезінде 10 сценарийдің 8-і өтті, 2-еуі өтпеді: бос нәтижеде келесі әрекет жоқ және бөтен сапарға рөлдік тыйым әлі іске асырылмаған.")
    add_table(
        doc,
        ["Issue", "Ескерту", "Басымдық", "Иесі", "Мерзімі"],
        [
            ["#34", "бос нәтижеге келесі әрекет", "P2", "Нурай", "18.11.2026"],
            ["#35", "бөтен сапарды өзгертуге тыйым", "P1", "Альфараби", "17.11.2026"],
            ["#36", "демоға сапар құру нысаны", "P2", "Нурислам", "20.11.2026"],
        ],
        [2.2, 7.0, 2.2, 3.0, 3.0],
    )

    add_heading(doc, "7 Кінәсіз postmortem")
    add_para(doc, "Инцидент: CI пайплайнының алғашқы іске қосылымдары сәтсіз аяқталды. Пайдаланушы сервисіне әсер болған жоқ, себебі бұл оқу релизіне дейінгі quality gate болды. Дегенмен артефакт жарияланбады және main тармағы уақытша қызыл күйде қалды.")
    add_table(
        doc,
        ["Уақыт GMT+5", "Оқиға"],
        [
            ["12.11.2026 03:41", "CI #1 басталды; Trivy action тегі табылмады"],
            ["12.11.2026 03:44", "тег түзетілді, бірақ v префиксі болмады"],
            ["12.11.2026 03:45", "action жүктелді; тест импорт жолы анықталды"],
            ["12.11.2026 03:48", "python-docx қосылды; Linux PYTHONPATH айырмасы қалды"],
            ["12.11.2026 03:50", "PYTHONPATH түзетіліп, қалпына келтіру run-ы басталды"],
        ],
        [5.0, 13.5],
    )
    add_para(doc, "Факторлар жүйе қасиеті ретінде жазылды: сыртқы action тегінің бар-жоғын main-ға дейін тексеретін қақпа болмады; локалдық Windows орта нүктені import жолына қосқан, Linux CI қоспаған; workflow бірден көптеген қадаммен қосылды. Не сработало: annotation нақты қатені көрсетті, локал тесттер мінез-құлықты растады, әр түзету жеке commit болды және API хронологияны сақтады.")

    add_heading(doc, "8 Үш жүйелік әрекет")
    add_table(
        doc,
        ["Issue", "Әрекет", "Иесі", "Мерзімі", "Өлшем"],
        [
            ["#37", "Action нұсқаларын автоматты жаңарту", "Альфараби", "17.11.2026", "қолжетімсіз tag main-ға түспейді"],
            ["#38", "PR CI-ды міндетті status check ету", "Нурай", "18.11.2026", "қызыл CI бар PR merge болмайды"],
            ["#39", "Failure хабарламасы және MTTR есебі", "Нурислам", "20.11.2026", "анықтау < 10, MTTR < 60 мин"],
        ],
        [2.0, 6.5, 2.8, 3.0, 5.2],
    )

    add_heading(doc, "9 Runbook және мониторинг")
    add_para(doc, "Runbook сервис health-check екі рет өтпегенде қолданылады. Incident commander — Нурислам. Диагностика curl, docker ps және docker logs арқылы жүргізіледі; соңғы жасыл SHA қайта іске қосылып, health және үш негізгі smoke-тест тексеріледі. 15 минутта себеп табылмаса командаға, 30 минутта тапсырыс берушіге эскалация жасалады.")
    add_para(doc, "Docker daemon қолжетімсіз орта үшін әдістемедегі балама іске асырылды: GitHub Actions availability workflow әр 6 сағат сайын қолжетімділікті тексереді. Нақты стенд URL пайда болғанда тексеру сол мекенжайға ауыстырылады. Runbook-ты компонентті жазбаған адам сыртқы UAT кезінде уақытпен тексереді.")

    add_heading(doc, "10 Қорытынды және шектеу")
    add_para(doc, "ЛЗ 11 пакетінде тест деңгейлері, автоматтандыру үлесі, анонимденген дерек ережесі, орталар, төрт НФТ-мен байланысқан тексеру, 10 UAT сценарийі, қабылдау хаттамасы, нақты CI инцидентінің кінәсіз postmortem есебі, үш backlog әрекеті және runbook бар.")
    add_para(doc, "Әдістеменің сыртқы UAT талабы құжатпен алмастырылмайды. Ішкі dry run нәтижесі дайындық дәлелі ғана; толық қабылдау үшін басқа команда немесе нақты тапсырыс беруші сессия өткізіп, қатысушылар мен нәтижелерді хаттамаға енгізуі керек. Бұл шектеу әдейі жасырылмайды.")
    add_para(doc, "ЖИ қолданылуы: OpenAI Codex тест коды, сценарийлер, құжаттың бастапқы нұсқасы және пішімдеуді дайындауға қолданылды. Нақты сыртқы UAT қатысушылары жасалмады; олар тек факті бойынша енгізіледі.")

    add_page_number(doc.sections[0])
    path = ROOT / "docs" / "qa" / "lz11-enuway-testing-uat-operations.docx"
    doc.save(path)
    return path


def main() -> None:
    metrics_path = ROOT / "docs" / "dora" / "data" / "dora-metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.exists() else {}
    print(build_lz10(metrics))
    print(build_lz11(metrics))


if __name__ == "__main__":
    main()
