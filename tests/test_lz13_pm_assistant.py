from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "pm_status_assistant.py"
SPEC = importlib.util.spec_from_file_location("pm_status_assistant", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def sample_facts():
    return {
        "repository": "nypucjiam-create/ENUWay",
        "sprints": [
            {"name": "Спринт 1", "commit_count": 2, "commits": []},
            {"name": "Спринт 2", "commit_count": 3, "commits": []},
        ],
        "issues": [],
    }


def test_prompt_requires_source_bound_output():
    prompt = MODULE.build_prompt(sample_facts())
    assert "Тек берілген JSON-дағы фактілерді қолдан" in prompt
    assert "commit_count" in prompt
    assert "PM тексеруі міндетті" in prompt


def test_fallback_keeps_observed_counts():
    report = MODULE.deterministic_fallback(sample_facts(), "offline")
    assert "2 коммит" in report
    assert "3 коммит" in report
    assert "ойдан" not in report


def test_two_fixed_sprints_do_not_overlap():
    first, second = MODULE.SPRINTS
    assert first.end == second.start
    assert first.start < first.end < second.end
