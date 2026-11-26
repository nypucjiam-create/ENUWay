"""ENUWay PM assistant: GitHub facts -> local-model weekly status draft.

The script deliberately separates immutable source facts from model prose.  It can
use Ollama (the scheduled default) or an OpenAI-compatible local llama.cpp server.
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "docs" / "pm-assistant" / "run"
REPOSITORY = "nypucjiam-create/ENUWay"


@dataclass(frozen=True)
class Sprint:
    name: str
    start: str
    end: str


SPRINTS = (
    Sprint("Спринт 1", "2026-09-16T00:00:00Z", "2026-09-30T00:00:00Z"),
    Sprint("Спринт 2", "2026-09-30T00:00:00Z", "2026-10-14T00:00:00Z"),
)


def _request_json(url: str, token: str | None = None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "ENUWay-LZ13-PM-assistant",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def _github_list(path: str, params: dict[str, str], token: str | None) -> list[dict[str, Any]]:
    params = {**params, "per_page": "100"}
    url = f"https://api.github.com/repos/{REPOSITORY}/{path}?{urllib.parse.urlencode(params)}"
    payload = _request_json(url, token)
    if not isinstance(payload, list):
        raise RuntimeError(f"GitHub API returned an unexpected value for {path}")
    return payload


def collect_github_facts(token: str | None = None) -> dict[str, Any]:
    sprints: list[dict[str, Any]] = []
    for sprint in SPRINTS:
        commits = _github_list(
            "commits",
            {"since": sprint.start, "until": sprint.end, "sha": "main"},
            token,
        )
        compact_commits = [
            {
                "sha": item["sha"][:7],
                "date": item["commit"]["committer"]["date"],
                "author": item["commit"]["author"].get("name") or "Белгісіз",
                "message": item["commit"]["message"].splitlines()[0],
                "url": item["html_url"],
            }
            for item in commits
        ]
        sprints.append(
            {
                "name": sprint.name,
                "start": sprint.start,
                "end_exclusive": sprint.end,
                "commit_count": len(compact_commits),
                "commits": compact_commits,
            }
        )

    issues = _github_list("issues", {"state": "all", "direction": "asc"}, token)
    compact_issues = []
    for item in issues:
        if "pull_request" in item:
            continue
        compact_issues.append(
            {
                "number": item["number"],
                "title": item["title"],
                "state": item["state"],
                "created_at": item["created_at"],
                "closed_at": item.get("closed_at"),
                "updated_at": item["updated_at"],
                "labels": [label["name"] for label in item.get("labels", [])],
                "assignees": [a["login"] for a in item.get("assignees", [])],
                "url": item["html_url"],
            }
        )

    return {
        "repository": REPOSITORY,
        "collected_at_utc": datetime.now(UTC).isoformat(),
        "source": "GitHub REST API",
        "sprints": sprints,
        "issues": compact_issues,
    }


def build_prompt(facts: dict[str, Any]) -> str:
    open_issues = [issue for issue in facts["issues"] if issue["state"] == "open"]
    closed_issues = [issue for issue in facts["issues"] if issue["state"] == "closed"]
    recently_updated_open = sorted(
        open_issues, key=lambda issue: issue["updated_at"], reverse=True
    )[:10]
    compact = {
        "repository": facts["repository"],
        "sprints": facts["sprints"],
        "issue_summary": {
            "open_count": len(open_issues),
            "closed_count": len(closed_issues),
            "recently_updated_open": recently_updated_open,
        },
    }
    return f"""Сен ENUWay жобасының PM-ассистентісің. Төмендегі GitHub деректерінен қазақ тілінде қысқа статус-есеп жаз.

Міндетті бөлімдер: 1) қысқаша қорытынды; 2) Спринт 1 фактілері; 3) Спринт 2 фактілері; 4) ашық мәселелер мен тәуекелдер; 5) келесі әрекеттер.
Ережелер:
- Тек берілген JSON-дағы фактілерді қолдан.
- Сан, күн, жауапты немесе сілтемені ойдан қоспа.
- Коммит санын JSON-дағы commit_count өрісінен ал.
- Дерек жеткіліксіз болса, «дерек жеткіліксіз» деп жаз.
- Бұл тек черновик екенін және PM тексеруі міндетті екенін соңында көрсет.

JSON:
{json.dumps(compact, ensure_ascii=False, indent=2)}
"""


def generate_ollama(prompt: str, model: str, endpoint: str) -> str:
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(
        endpoint.rstrip("/") + "/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=600) as response:
        data = json.loads(response.read().decode("utf-8"))
    return str(data["response"]).strip()


def generate_llamacpp(prompt: str, model: str, endpoint: str) -> str:
    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 350,
        }
    ).encode()
    req = urllib.request.Request(
        endpoint.rstrip("/") + "/v1/chat/completions",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=600) as response:
        data = json.loads(response.read().decode("utf-8"))
    return str(data["choices"][0]["message"]["content"]).strip()


def deterministic_fallback(facts: dict[str, Any], reason: str) -> str:
    lines = [
        "# ENUWay автоматты статус-есебінің қауіпсіз резервтік нұсқасы",
        "",
        f"> Жергілікті модель жауабы алынбады: {reason}",
        "",
    ]
    for sprint in facts["sprints"]:
        lines.extend(
            [
                f"## {sprint['name']}",
                f"GitHub API бойынша негізгі тармақта {sprint['commit_count']} коммит бар.",
                "",
            ]
        )
    open_issues = [issue for issue in facts["issues"] if issue["state"] == "open"]
    lines.extend(
        [
            "## Ашық мәселелер",
            f"Ашық issue саны: {len(open_issues)}.",
            "",
            "Бұл резервтік есеп, жариялау алдында PM тексеруі міндетті.",
        ]
    )
    return "\n".join(lines)


def run(args: argparse.Namespace) -> dict[str, Any]:
    started = time.perf_counter()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.offline_source:
        facts = json.loads(Path(args.offline_source).read_text(encoding="utf-8"))
        source_mode = "offline-replay"
    else:
        facts = collect_github_facts(os.getenv("GITHUB_TOKEN"))
        source_mode = "live-github-api"

    prompt = build_prompt(facts)
    model_started = time.perf_counter()
    model_error = None
    try:
        if args.provider == "ollama":
            report = generate_ollama(prompt, args.model, args.endpoint)
        elif args.provider == "llamacpp":
            report = generate_llamacpp(prompt, args.model, args.endpoint)
        else:
            raise RuntimeError("model provider was disabled")
    except (OSError, RuntimeError, KeyError, urllib.error.URLError) as exc:
        model_error = f"{type(exc).__name__}: {exc}"
        report = deterministic_fallback(facts, model_error)
    model_seconds = round(time.perf_counter() - model_started, 3)

    (out_dir / "source-data.json").write_text(
        json.dumps(facts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (out_dir / "prompt-used.txt").write_text(prompt, encoding="utf-8")
    (out_dir / "generated-status-report.md").write_text(report + "\n", encoding="utf-8")
    metrics = {
        "repository": facts["repository"],
        "source_mode": source_mode,
        "provider": args.provider,
        "model": args.model,
        "model_error": model_error,
        "model_generation_seconds": model_seconds,
        "total_run_seconds": round(time.perf_counter() - started, 3),
        "generated_at_utc": datetime.now(UTC).isoformat(),
    }
    (out_dir / "run-metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--provider", choices=("ollama", "llamacpp", "none"), default="ollama")
    parser.add_argument("--model", default="qwen2.5:0.5b")
    parser.add_argument("--endpoint", default="http://127.0.0.1:11434")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUT))
    parser.add_argument("--offline-source", help="Replay a saved source-data.json file")
    return parser.parse_args()


if __name__ == "__main__":
    print(json.dumps(run(parse_args()), ensure_ascii=False, indent=2))
