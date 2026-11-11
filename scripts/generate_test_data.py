"""ENUWay үшін қайталанатын, жасанды тест деректерін жасайды."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


AREAS = ["Сарыарқа", "Есіл", "Алматы", "Байқоңыр"]
NAMES = ["Тест қолданушы 01", "Тест қолданушы 02", "Тест қолданушы 03"]


def generate(seed: int, count: int) -> list[dict]:
    rng = random.Random(seed)
    return [
        {
            "driver": rng.choice(NAMES),
            "origin": rng.choice(AREAS),
            "destination": "ЕҰУ",
            "travel_date": f"2026-11-{13 + index % 10:02d}",
            "departure_time": f"{7 + index % 3:02d}:{(index * 10) % 60:02d}",
            "seats_available": rng.randint(1, 4),
            "contribution_kzt": rng.choice([500, 600, 700, 800]),
        }
        for index in range(count)
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=20261112)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--output", type=Path, default=Path("tests/data/rides.json"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(generate(args.seed, args.count), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"{args.output}: {args.count} жазба, seed={args.seed}")


if __name__ == "__main__":
    main()

