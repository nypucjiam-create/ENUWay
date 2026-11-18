#!/usr/bin/env python3
"""ENUWay ЛЗ12: baseline және жергілікті LLM жіктеуін қайталама өлшеу."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import time
import urllib.request
from collections import Counter
from pathlib import Path

LABELS = ["ACCOUNT", "SEARCH", "RIDE_MANAGEMENT", "BOOKING", "SAFETY"]
LABEL_DESCRIPTIONS = {
    "ACCOUNT": "кіру, тіркелгі, профиль, ENU поштасы, құпиясөз немесе сессия",
    "SEARCH": "жолаушының сапарды, бағытты, жүргізушіні немесе сүзгіні іздеуі",
    "RIDE_MANAGEMENT": "жүргізушінің өз сапарын құруы, өзгертуі немесе өшіруі",
    "BOOKING": "орынды брондау, бронь мәртебесі немесе броньнан бас тарту",
    "SAFETY": "қауіп, шағым, қорқыту, алаяқтық, деректердің таралуы немесе SOS",
}

BASELINE_RULES = [
    ("SAFETY", ["қауіпті", "қорқ", "sos", "шағым"]),
    ("ACCOUNT", ["құпиясөз", "аккаунт", "сессия", "авториза"]),
    ("BOOKING", ["бронд", "бронь", "booking", "орын алып"]),
    ("RIDE_MANAGEMENT", ["жария", "жүргізуші ретінде", "жүргізушімін", "создать маршрут"]),
    ("SEARCH", ["ізде", "найти поездку", "сүзгі", "картадан"]),
]

FEW_SHOT = [
    ("Құпиясөзімді ұмыттым", "ACCOUNT"),
    ("Профильдегі телефонды өзгерту керек", "ACCOUNT"),
    ("Ертең ENU-ға баратын көлік керек", "SEARCH"),
    ("Бағытты картадан таба алмадым", "SEARCH"),
    ("Жариялаған сапарымның уақытын өзгертемін", "RIDE_MANAGEMENT"),
    ("Жүргізушімін, жаңа маршрут қосамын", "RIDE_MANAGEMENT"),
    ("Броньнан бас тарту батырмасы істемейді", "BOOKING"),
    ("Орынды брондадым, мәртебесі қандай?", "BOOKING"),
    ("Жүргізуші агрессия көрсетті", "SAFETY"),
    ("Менің жеке деректерім тарап кетті", "SAFETY"),
]

LETTER_TO_LABEL = {"A": "ACCOUNT", "B": "SEARCH", "C": "RIDE_MANAGEMENT", "D": "BOOKING", "E": "SAFETY", "U": "UNCERTAIN"}
LABEL_TO_LETTER = {value: key for key, value in LETTER_TO_LABEL.items()}


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def baseline_predict(text: str) -> dict:
    normalized = text.casefold()
    scores = {label: sum(1 for term in terms if term in normalized) for label, terms in BASELINE_RULES}
    ranked = sorted(scores.items(), key=lambda item: (-item[1], LABELS.index(item[0])))
    label, score = ranked[0]
    if score == 0:
        return {"label": "UNCERTAIN", "confidence": 0.0, "raw": scores}
    ties = sum(1 for value in scores.values() if value == score)
    confidence = 0.55 if ties > 1 else min(0.95, 0.55 + 0.15 * score)
    return {"label": label, "confidence": confidence, "raw": scores}


def prompt_for(text: str, mode: str) -> str:
    definitions = "\n".join(f"{LABEL_TO_LETTER[key]} = {key}: {value}" for key, value in LABEL_DESCRIPTIONS.items())
    examples = ""
    if mode == "few_shot":
        examples = "\nМысалдар:\n" + "\n".join(f"{t} -> {LABEL_TO_LETTER[l]}" for t, l in FEW_SHOT)
    return f"""ENUWay өтінішін жікте. Тек бір латын әрпін жаз: A, B, C, D, E немесе U.
{definitions}
{examples}
Ереже: қауіп, қорқыту, шағым, алаяқтық, SOS не дерек таралуы болса E таңда. Жүргізуші өз жарияланымын өзгертсе C, жолаушы орынмен әрекет етсе D. Мүлде дерек болмаса U.
Мәтін: {text}
Әріп:"""


def call_server(server_url: str, model: str, prompt: str, seed: int) -> tuple[str, dict, float]:
    payload = {
        "model": model,
        "prompt": prompt,
        "temperature": 0,
        "seed": seed,
        "max_tokens": 4,
        "stop": ["\n"],
    }
    request = urllib.request.Request(
        server_url.rstrip("/") + "/v1/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    with urllib.request.urlopen(request, timeout=180) as response:
        body = json.loads(response.read().decode("utf-8"))
    elapsed_ms = (time.perf_counter() - started) * 1000
    raw = body["choices"][0]["text"].strip()
    return raw, body.get("usage", {}), elapsed_ms


def normalize_label(raw: str) -> str:
    cleaned = raw.strip().upper()
    if cleaned and cleaned[0] in LETTER_TO_LABEL:
        return LETTER_TO_LABEL[cleaned[0]]
    upper = re.sub(r"[^A-Z_]", " ", raw.upper())
    for label in LABELS + ["UNCERTAIN"]:
        if re.search(rf"\b{re.escape(label)}\b", upper):
            return label
    return "UNCERTAIN"


def compute_metrics(rows: list[dict], pred_key: str) -> dict:
    total = len(rows)
    correct = sum(row["gold"] == row[pred_key] for row in rows)
    per_class = {}
    f1_values = []
    for label in LABELS:
        tp = sum(row["gold"] == label and row[pred_key] == label for row in rows)
        fp = sum(row["gold"] != label and row[pred_key] == label for row in rows)
        fn = sum(row["gold"] == label and row[pred_key] != label for row in rows)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        f1_values.append(f1)
        per_class[label] = {"support": sum(row["gold"] == label for row in rows), "precision": round(precision, 4), "recall": round(recall, 4), "f1": round(f1, 4)}
    return {
        "n": total,
        "accuracy": round(correct / total, 4),
        "macro_f1": round(sum(f1_values) / len(f1_values), 4),
        "uncertain_count": sum(row[pred_key] == "UNCERTAIN" for row in rows),
        "per_class": per_class,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path(__file__).with_name("dataset.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).with_name("results"))
    parser.add_argument("--server-url", default=None)
    parser.add_argument("--model", default="qwen2.5-3b-instruct-q4_k_m.gguf")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    source = load_jsonl(args.dataset)
    rows = []
    for item in source:
        base = baseline_predict(item["text"])
        rows.append({**item, "baseline_pred": base["label"], "baseline_confidence": base["confidence"]})

    report = {
        "run": {
            "dataset": str(args.dataset), "seed": args.seed, "temperature": 0,
            "model": args.model if args.server_url else None,
            "server_url": args.server_url,
        },
        "baseline": compute_metrics(rows, "baseline_pred"),
    }

    if args.server_url:
        for mode in ("zero_shot", "few_shot"):
            raw_path = args.output_dir / f"{mode}_raw.jsonl"
            cached = {}
            if raw_path.exists():
                try:
                    cached = {entry["id"]: entry for entry in load_jsonl(raw_path)}
                except (json.JSONDecodeError, KeyError):
                    cached = {}
            with raw_path.open("w", encoding="utf-8") as raw_file:
                for row in rows:
                    prompt = prompt_for(row["text"], mode)
                    previous = cached.get(row["id"])
                    if previous and previous.get("prompt") == prompt and previous.get("engine") == "completions-v4-letter":
                        raw = previous["raw"]
                        usage = previous.get("usage", {})
                        elapsed_ms = previous.get("elapsed_ms", 0.0)
                        pred = previous.get("prediction", normalize_label(raw))
                    else:
                        raw, usage, elapsed_ms = call_server(args.server_url, args.model, prompt, args.seed)
                        pred = normalize_label(raw)
                    row[f"{mode}_pred"] = pred
                    row[f"{mode}_raw"] = raw
                    row[f"{mode}_usage"] = usage
                    row[f"{mode}_elapsed_ms"] = round(elapsed_ms, 1)
                    raw_file.write(json.dumps({"id": row["id"], "gold": row["gold"], "engine": "completions-v4-letter", "prompt": prompt, "raw": raw, "prediction": pred, "usage": usage, "elapsed_ms": round(elapsed_ms, 1)}, ensure_ascii=False) + "\n")
            report[mode] = compute_metrics(rows, f"{mode}_pred")
            usage_totals = Counter()
            for row in rows:
                usage_totals.update({key: value for key, value in row[f"{mode}_usage"].items() if isinstance(value, (int, float))})
            report[mode]["usage_total"] = dict(usage_totals)
            report[mode]["latency_ms_mean"] = round(sum(row[f"{mode}_elapsed_ms"] for row in rows) / len(rows), 1)

    (args.output_dir / "metrics.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = ["id", "difficulty", "language", "gold", "baseline_pred"]
    for mode in ("zero_shot", "few_shot"):
        if f"{mode}_pred" in rows[0]:
            fields += [f"{mode}_pred", f"{mode}_raw", f"{mode}_elapsed_ms"]
    fields += ["text", "note"]
    with (args.output_dir / "error_analysis.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
