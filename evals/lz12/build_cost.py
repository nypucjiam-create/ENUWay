#!/usr/bin/env python3
"""Нақты eval токендерінен API және self-hosted құнын есептеу."""

from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METRICS = Path(__file__).with_name("results") / "metrics.json"
OUTPUT = ROOT / "docs" / "ai" / "lz12-cost.json"

# 19.11.2026 күніндегі ресми жарияланған стандарт тарифтер.
API_MODEL = "gpt-6-luna"
API_INPUT_PER_M = 0.10
API_OUTPUT_PER_M = 0.50
API_SOURCE = "https://developers.openai.com/api/docs/pricing"
SELF_HOSTED_MODEL = "Hetzner CPX32, Germany/Finland, IPv4-сыз, ҚҚС-сыз"
SELF_HOSTED_MONTHLY_USD = 41.99
SELF_HOSTED_SOURCE = "https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/"
BASE_REQUESTS = 3_000


def main() -> None:
    metrics = json.loads(METRICS.read_text(encoding="utf-8"))
    usage = metrics["few_shot"]["usage_total"]
    n = metrics["few_shot"]["n"]
    avg_in = usage["prompt_tokens"] / n
    avg_out = usage["completion_tokens"] / n
    per_request = avg_in / 1_000_000 * API_INPUT_PER_M + avg_out / 1_000_000 * API_OUTPUT_PER_M
    base_cost = per_request * BASE_REQUESTS
    ten_x_cost = per_request * BASE_REQUESTS * 10
    break_even = math.ceil(SELF_HOSTED_MONTHLY_USD / per_request)
    result = {
        "access_date": "2026-11-19",
        "measured_on": metrics["run"],
        "tokens": {
            "evaluation_requests": n,
            "prompt_tokens_total": usage["prompt_tokens"],
            "completion_tokens_total": usage["completion_tokens"],
            "average_input_tokens": round(avg_in, 2),
            "average_output_tokens": round(avg_out, 2),
            "tokenizer": "Qwen2.5 GGUF ішіндегі ашық tokenizer, llama.cpp usage есебі",
        },
        "api": {
            "model": API_MODEL,
            "input_usd_per_million": API_INPUT_PER_M,
            "output_usd_per_million": API_OUTPUT_PER_M,
            "source": API_SOURCE,
            "cost_per_request_usd": round(per_request, 8),
            "monthly_requests": BASE_REQUESTS,
            "monthly_cost_usd": round(base_cost, 4),
            "ten_x_requests": BASE_REQUESTS * 10,
            "ten_x_monthly_cost_usd": round(ten_x_cost, 4),
        },
        "self_hosted": {
            "configuration": SELF_HOSTED_MODEL,
            "monthly_cost_usd": SELF_HOSTED_MONTHLY_USD,
            "source": SELF_HOSTED_SOURCE,
            "break_even_requests_per_month": break_even,
            "note": "Бұл — есептік сервер тарифі; нақты сервер жалға алынған жоқ. Eval бар ноутбукте тегін орындалды.",
        },
        "formula": "requests × (avg_input_tokens × input_price/1M + avg_output_tokens × output_price/1M)",
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
