# Automation Opportunity Auditor

A small strategy-oriented tool for evaluating which business tasks are good candidates for automation or AI assistance.

Instead of starting with "Where can we add AI?", the tool starts with the business process itself and scores each task across:

- potential time savings
- error reduction opportunity
- rule-based repeatability
- systems/integration complexity
- data sensitivity
- amount of human judgment required

The result is a prioritized automation roadmap.

## Why this matters

Good AI and automation consulting is not about automating everything.

Some tasks are excellent automation candidates. Others should remain human-led because they involve judgment, sensitive data, low repetition, or poor economics.

This project demonstrates the kind of structured thinking needed before implementation starts.

## Example

Input:

```json
{
  "business_process": "Inbound sales",
  "tasks": [
    {
      "name": "Copy website leads into CRM",
      "minutes_per_run": 6,
      "runs_per_week": 45,
      "manual_error_rate_pct": 8,
      "rule_based_score": 5,
      "systems_touched": 2,
      "data_sensitivity": "medium",
      "human_judgment_score": 1
    }
  ]
}
```

Run:

```bash
python auditor.py sample_business_process.json
```

The output includes:

- monthly hours consumed
- impact score
- effort score
- risk score
- overall priority
- recommendation

## Recommendation classes

- **Automate now** — strong business case and manageable risk
- **Pilot** — promising, but validate with a smaller workflow first
- **Assistive AI / human-in-the-loop** — AI can help, but human judgment should stay central
- **Defer** — weak economics or high implementation/risk cost

## What this project demonstrates

- business-process analysis
- automation opportunity discovery
- simple quantitative prioritization
- AI strategy thinking
- explainable decision rules
- translating business needs into an implementation roadmap

A real consulting engagement would add stakeholder interviews, workflow observation, security/privacy requirements, ROI assumptions, and technical architecture before implementation.
