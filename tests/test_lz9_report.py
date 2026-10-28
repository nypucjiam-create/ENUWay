from pathlib import Path
import unittest

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "process" / "lz9-enuway-flow-report.docx"


class Lz9ReportTest(unittest.TestCase):
    def setUp(self):
        self.document = Document(REPORT)
        self.text = "\n".join(p.text for p in self.document.paragraphs)

    def test_required_sections_are_present(self):
        for heading in (
            "1 Жұмыс процесін баптау",
            "2 Definition of Ready және Definition of Done",
            "5 Ағын метрикалары",
            "6 Кумулятивті ағын диаграммасы және тар орын",
            "7 Ретроспектива",
            "8 Шектеулер және келесі өлшеу тәртібі",
            "9 Қорытынды",
        ):
            self.assertIn(heading, self.text)

    def test_report_contains_tables_and_both_visuals(self):
        self.assertGreaterEqual(len(self.document.tables), 4)
        self.assertEqual(len(self.document.inline_shapes), 2)


if __name__ == "__main__":
    unittest.main()
