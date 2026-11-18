import json
import sys
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = ROOT / "evals" / "lz12"
sys.path.insert(0, str(EVAL_DIR))

from run_eval import LABELS, baseline_predict, compute_metrics  # noqa: E402


class Lz12EvalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = [json.loads(line) for line in (EVAL_DIR / "dataset.jsonl").read_text(encoding="utf-8").splitlines() if line]

    def test_dataset_has_required_size_and_unique_ids(self):
        self.assertGreaterEqual(len(self.rows), 30)
        self.assertEqual(len(self.rows), len({row["id"] for row in self.rows}))

    def test_all_labels_balanced_and_hard_examples_present(self):
        counts = Counter(row["gold"] for row in self.rows)
        self.assertEqual(set(counts), set(LABELS))
        self.assertEqual(len(set(counts.values())), 1)
        self.assertGreaterEqual(sum(row["difficulty"] == "hard" for row in self.rows), 6)

    def test_no_direct_personal_data_fields(self):
        forbidden = {"name", "phone", "email", "license_plate", "user_id"}
        for row in self.rows:
            self.assertFalse(forbidden.intersection(row))

    def test_baseline_and_metric_pipeline(self):
        measured = []
        for row in self.rows:
            measured.append({**row, "pred": baseline_predict(row["text"])["label"]})
        metrics = compute_metrics(measured, "pred")
        self.assertEqual(metrics["n"], len(self.rows))
        self.assertGreater(metrics["macro_f1"], 0)
        self.assertLessEqual(metrics["macro_f1"], 1)

    def test_real_run_has_raw_evidence_for_both_prompts(self):
        results = EVAL_DIR / "results"
        metrics = json.loads((results / "metrics.json").read_text(encoding="utf-8"))
        self.assertEqual(metrics["run"]["model"], "qwen2.5-3b-instruct-q4_k_m.gguf")
        self.assertEqual(metrics["run"]["temperature"], 0)
        self.assertEqual(metrics["run"]["seed"], 42)
        for mode in ("zero_shot", "few_shot"):
            raw = [json.loads(line) for line in (results / f"{mode}_raw.jsonl").read_text(encoding="utf-8").splitlines() if line]
            self.assertEqual(len(raw), len(self.rows))
            self.assertTrue(all(item["engine"] == "completions-v4-letter" for item in raw))
            self.assertEqual(metrics[mode]["n"], len(self.rows))

    def test_cost_formula_and_ten_x_scenario(self):
        cost = json.loads((ROOT / "docs" / "ai" / "lz12-cost.json").read_text(encoding="utf-8"))
        api = cost["api"]
        expected = (
            cost["tokens"]["average_input_tokens"] * api["input_usd_per_million"] / 1_000_000
            + cost["tokens"]["average_output_tokens"] * api["output_usd_per_million"] / 1_000_000
        )
        self.assertAlmostEqual(api["cost_per_request_usd"], expected, places=8)
        self.assertEqual(api["ten_x_requests"], api["monthly_requests"] * 10)
        self.assertAlmostEqual(api["ten_x_monthly_cost_usd"], api["monthly_cost_usd"] * 10, places=3)


if __name__ == "__main__":
    unittest.main()
