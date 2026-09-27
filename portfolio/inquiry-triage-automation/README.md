# Inquiry Triage Automation

A public portfolio project showing how a small business can automatically classify and prioritize incoming inquiries using a backend API and an automation workflow.

## Problem

Small businesses often receive a mix of:

- genuine leads
- urgent customer messages
- newsletters
- low-value or spam messages
- general inquiries

When everything lands in the same inbox, high-value messages can be missed.

## Solution

This project separates **classification logic** from **workflow orchestration**:

```text
Incoming email / form
        ↓
      n8n
        ↓
Normalize payload
        ↓
POST /classify
        ↓
 FastAPI service
        ↓
SQLite audit log
        ↓
category + priority + reasons
        ↓
n8n Switch / routing
        ↓
Label • notify • escalate • archive
```

The backend can be called from n8n, Zapier, Make, a web form, or another application.

## Features

- REST API built with FastAPI
- Rule-based inquiry classification
- Priority scoring
- SQLite persistence
- Human-correction endpoint for feedback
- Recent-inquiry history
- Simple statistics endpoint
- Designed to plug into n8n through an HTTP Request node
- Easy extension point for an AI/LLM classifier

## Run locally

```bash
cd portfolio/inquiry-triage-automation
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open the API docs at:

```text
http://127.0.0.1:8000/docs
```

## Example

```bash
curl -X POST http://127.0.0.1:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "client@example.com",
    "subject": "Need help with an automation project",
    "body": "We would like a quote this week. Can you call us today?"
  }'
```

Example response:

```json
{
  "id": 1,
  "category": "urgent",
  "priority": 95,
  "reasons": [
    "urgent language detected",
    "commercial intent detected"
  ]
}
```

## n8n integration

A practical n8n workflow can use:

1. **Gmail Trigger** or **Webhook**
2. **Set / Edit Fields** to normalize sender, subject, and body
3. **HTTP Request** → `POST http://your-api/classify`
4. **Switch** on `category`
5. Route results:
   - `urgent` → label + Slack/Telegram notification
   - `lead` → CRM + priority label
   - `newsletter` → newsletter label
   - `spam` → low-priority/archive flow
   - `other` → normal inbox

## AI extension

The current classifier is intentionally deterministic and easy to inspect.

For a production version, an LLM can be inserted before or after the rules layer to:

- detect nuanced buying intent
- summarize long emails
- extract company, budget, deadline, and requested service
- return structured JSON for n8n routing

The API contract can stay the same, so the orchestration does not need to be redesigned.

## Why this project is in my portfolio

It demonstrates the combination of **backend development, APIs, databases, and business automation** rather than treating automation as a no-code-only task.
