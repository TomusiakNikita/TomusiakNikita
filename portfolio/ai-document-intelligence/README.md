# AI Document Intelligence API

A small backend project that demonstrates how an AI model can be integrated into a business system through a clean API boundary.

The service accepts unstructured business text — such as an inquiry, brief, proposal, meeting note, or operational document — and asks an OpenAI-compatible model to return validated structured JSON.

## Why this project exists

A useful AI integration is more than sending a prompt to a model.

Production systems also need:

- input validation
- stable API contracts
- structured outputs
- configuration through environment variables
- error handling
- provider boundaries
- predictable data for downstream automation

This project demonstrates those pieces in a compact form.

## Architecture

```text
Client / n8n / Web App
        ↓
POST /analyze
        ↓
      FastAPI
        ↓
OpenAI-compatible API
        ↓
 structured JSON
        ↓
 Pydantic validation
        ↓
 downstream system
```

## Extracted fields

The API returns:

- document type
- short summary
- people
- organizations
- dates
- monetary amounts
- action items
- risk flags

## Run locally

```bash
cd portfolio/ai-document-intelligence
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set your provider configuration in the environment, then run:

```bash
uvicorn app:app --reload
```

Interactive API docs:

```text
http://127.0.0.1:8000/docs
```

## Example request

```json
{
  "text": "Acme SAS would like a proposal by 15 October. Budget is around €8,000. Marie Dupont will approve the project.",
  "document_type_hint": "client brief"
}
```

## Security

- API keys are never committed to the repository.
- Secrets are read from environment variables.
- The service returns controlled errors instead of exposing provider responses directly.
- In a real client deployment, sensitive-data policies should be decided before sending documents to any external AI provider.

## What this project demonstrates

- backend API development
- AI API integration
- structured outputs
- Pydantic validation
- async HTTP requests
- configuration/secrets handling
- designing AI as one component inside a larger system
