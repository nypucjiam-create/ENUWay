"""GitHub Actions тарихынан ENUWay DORA көрсеткіштерін есептейді.

Токен міндетті емес: public репозиторий үшін GitHub API токенсіз де оқылады.
Токен қолданылса, ол тек GH_TOKEN орта айнымалысынан алынады.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import statistics
import sys
import urllib.request
from datetime import datetime
from pathlib import Path


def api_get(url: str) -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ENUWay-DORA-Lab",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
        return json.load(response)


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def collect(repo: str, workflow: str) -> list[dict]:
    url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/runs?branch=main&per_page=100"
    raw = api_get(url)
    runs = []
    for item in raw.get("workflow_runs", []):
        if item.get("status") != "completed":
            continue
        commit_time = parse_time((item.get("head_commit") or {}).get("timestamp"))
        completed_at = parse_time(item.get("updated_at"))
        lead_minutes = None
        if commit_time and completed_at:
            lead_minutes = round((completed_at - commit_time).total_seconds() / 60, 2)
        runs.append(
            {
                "run_number": item["run_number"],
                "run_id": item["id"],
                "commit_sha": item["head_sha"][:7],
                "commit_time": commit_time.isoformat() if commit_time else "",
                "completed_at": completed_at.isoformat() if completed_at else "",
                "conclusion": item.get("conclusion") or "unknown",
                "lead_time_minutes": lead_minutes,
                "url": item["html_url"],
            }
        )
    return sorted(runs, key=lambda row: row["run_number"])


def calculate(runs: list[dict]) -> dict:
    successful = [row for row in runs if row["conclusion"] == "success"]
    failed = [row for row in runs if row["conclusion"] != "success"]
    observed = [parse_time(row["completed_at"]) for row in runs if row["completed_at"]]
    if len(observed) >= 2:
        span_days = max((max(observed) - min(observed)).total_seconds() / 86400, 1)
    else:
        span_days = 1
    deployment_frequency_week = round(len(successful) / span_days * 7, 2)
    leads = [row["lead_time_minutes"] for row in successful if row["lead_time_minutes"] is not None]

    recoveries = []
    for failed_run in failed:
        failure_time = parse_time(failed_run["completed_at"])
        next_success = next(
            (
                parse_time(row["completed_at"])
                for row in runs
                if row["run_number"] > failed_run["run_number"] and row["conclusion"] == "success"
            ),
            None,
        )
        if failure_time and next_success:
            recoveries.append((next_success - failure_time).total_seconds() / 60)

    return {
        "observation_started_at": min(observed).isoformat() if observed else None,
        "observation_ended_at": max(observed).isoformat() if observed else None,
        "completed_runs": len(runs),
        "successful_deployments": len(successful),
        "failed_changes": len(failed),
        "deployment_frequency_per_week": deployment_frequency_week,
        "median_lead_time_minutes": round(statistics.median(leads), 2) if leads else None,
        "change_failure_rate_percent": round(len(failed) / len(runs) * 100, 2) if runs else None,
        "mean_time_to_restore_minutes": round(statistics.mean(recoveries), 2) if recoveries else None,
        "recovery_samples": len(recoveries),
        "data_limitation": "Қысқа оқу тарихы; нәтиже тұрақты тренд емес." if len(runs) < 10 else "",
    }


def write_csv(path: Path, runs: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(runs[0]) if runs else ["run_number"])
        writer.writeheader()
        writer.writerows(runs)


def write_svg(path: Path, metrics: dict) -> None:
    values = [
        ("Апталық жариялау", f"{metrics['deployment_frequency_per_week'] or 0:g}"),
        ("Commit-тен жеткізуге", f"{metrics['median_lead_time_minutes'] or 0:g} мин"),
        ("Сәтсіз өзгеріс үлесі", f"{metrics['change_failure_rate_percent'] or 0:g}%"),
        ("Қалпына келу уақыты", f"{metrics['mean_time_to_restore_minutes'] or 0:g} мин"),
    ]
    cards = []
    for index, (label, value) in enumerate(values):
        x = 60 + (index % 2) * 500
        y = 190 + (index // 2) * 220
        cards.append(
            f'<rect x="{x}" y="{y}" width="440" height="170" rx="20" fill="#F4F7FA"/>'
            f'<text x="{x + 28}" y="{y + 52}" class="label">{label}</text>'
            f'<text x="{x + 28}" y="{y + 120}" class="value">{value}</text>'
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1060" height="700" viewBox="0 0 1060 700">
<style>.title{{font:700 34px Arial;fill:#102A43}}.sub{{font:18px Arial;fill:#486581}}.label{{font:18px Arial;fill:#486581}}.value{{font:700 38px Arial;fill:#006D77}}.foot{{font:16px Arial;fill:#627D98}}</style>
<rect width="1060" height="700" fill="white"/>
<text x="60" y="72" class="title">ENUWay DORA бақылау тақтасы</text>
<text x="60" y="112" class="sub">GitHub Actions CI нақты тарихы · main тармағы</text>
{''.join(cards)}
<text x="60" y="660" class="foot">Бақылау: {metrics['completed_runs']} аяқталған CI іске қосылымы. Қысқа тарих тренд емес.</text>
</svg>'''
    path.write_text(svg, encoding="utf-8")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="nypucjiam-create/ENUWay")
    parser.add_argument("--workflow", default="ci.yml")
    parser.add_argument("--output-dir", type=Path, default=Path("docs/dora/data"))
    args = parser.parse_args()

    runs = collect(args.repo, args.workflow)
    metrics = calculate(runs)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "workflow-runs.csv", runs)
    (args.output_dir / "dora-metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_svg(args.output_dir.parent / "dora-dashboard.svg", metrics)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

