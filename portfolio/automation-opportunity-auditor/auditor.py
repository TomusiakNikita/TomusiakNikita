from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal


Sensitivity = Literal["low", "medium", "high"]


@dataclass
class Task:
    name: str
    minutes_per_run: float
    runs_per_week: float
    manual_error_rate_pct: float
    rule_based_score: int
    systems_touched: int
    data_sensitivity: Sensitivity
    human_judgment_score: int


@dataclass
class Assessment:
    name: str
    monthly_hours: float
    impact_score: int
    effort_score: int
    risk_score: int
    priority_score: int
    recommendation: str


SENSITIVITY_RISK = {
    "low": 10,
    "medium": 35,
    "high": 65,
}


def clamp(value: float) -> int:
    return round(max(0, min(value, 100)))


def assess(task: Task) -> Assessment:
    monthly_hours = task.minutes_per_run * task.runs_per_week * 4.33 / 60

    impact = clamp(
        monthly_hours * 4
        + task.manual_error_rate_pct * 1.5
        + task.rule_based_score * 8
    )

    effort = clamp(
        15
        + task.systems_touched * 10
        + (5 - task.rule_based_score) * 8
        + {"low": 0, "medium": 10, "high": 20}[task.data_sensitivity]
    )

    risk = clamp(
        SENSITIVITY_RISK[task.data_sensitivity]
        + task.human_judgment_score * 8
    )

    priority = clamp(
        impact * 0.55
        + (100 - effort) * 0.25
        + (100 - risk) * 0.20
    )

    if task.human_judgment_score >= 4 or risk >= 75:
        recommendation = "Assistive AI / human-in-the-loop"
    elif priority >= 70:
        recommendation = "Automate now"
    elif priority >= 50:
        recommendation = "Pilot"
    else:
        recommendation = "Defer"

    return Assessment(
        name=task.name,
        monthly_hours=round(monthly_hours, 1),
        impact_score=impact,
        effort_score=effort,
        risk_score=risk,
        priority_score=priority,
        recommendation=recommendation,
    )


def load_tasks(path: Path) -> tuple[str, list[Task]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    process_name = payload["business_process"]
    tasks = [Task(**item) for item in payload["tasks"]]
    return process_name, tasks


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python auditor.py <business_process.json>")

    process_name, tasks = load_tasks(Path(sys.argv[1]))
    assessments = sorted(
        (assess(task) for task in tasks),
        key=lambda item: item.priority_score,
        reverse=True,
    )

    print(
        json.dumps(
            {
                "business_process": process_name,
                "automation_roadmap": [asdict(item) for item in assessments],
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
