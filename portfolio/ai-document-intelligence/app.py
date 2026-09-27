from __future__ import annotations

import json
import os

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError


app = FastAPI(
    title="AI Document Intelligence API",
    version="1.0.0",
    description="Turn unstructured business text into validated structured data.",
)


class DocumentRequest(BaseModel):
    text: str = Field(min_length=20, max_length=30_000)
    document_type_hint: str | None = Field(default=None, max_length=120)


class DocumentAnalysis(BaseModel):
    document_type: str
    summary: str
    people: list[str] = []
    organizations: list[str] = []
    dates: list[str] = []
    amounts: list[str] = []
    action_items: list[str] = []
    risk_flags: list[str] = []


def provider_config() -> tuple[str, str, str]:
    base_url = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    api_key = os.getenv("AI_API_KEY", "")
    model = os.getenv("AI_MODEL", "")

    if not api_key or not model:
        raise HTTPException(
            status_code=503,
            detail="AI provider is not configured. Set AI_API_KEY and AI_MODEL.",
        )

    return base_url, api_key, model


def system_prompt() -> str:
    return (
        "You extract structured information from business documents. "
        "Return only valid JSON with exactly these keys: "
        "document_type, summary, people, organizations, dates, amounts, "
        "action_items, risk_flags. "
        "Use arrays of strings for every list field. "
        "Do not invent facts that are not present in the document."
    )


@app.get("/health")
def health() -> dict[str, bool | str]:
    return {
        "status": "ok",
        "provider_configured": bool(
            os.getenv("AI_API_KEY") and os.getenv("AI_MODEL")
        ),
    }


@app.post("/analyze", response_model=DocumentAnalysis)
async def analyze_document(request: DocumentRequest) -> DocumentAnalysis:
    base_url, api_key, model = provider_config()

    hint = (
        f"Document type hint: {request.document_type_hint}\n\n"
        if request.document_type_hint
        else ""
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt()},
            {
                "role": "user",
                "content": f"{hint}Document:\n{request.text}",
            },
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0,
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail="The configured AI provider could not complete the request.",
        ) from exc

    try:
        provider_data = response.json()
        content = provider_data["choices"][0]["message"]["content"]
        parsed = json.loads(content)
        return DocumentAnalysis.model_validate(parsed)
    except (KeyError, IndexError, TypeError, json.JSONDecodeError, ValidationError) as exc:
        raise HTTPException(
            status_code=502,
            detail="The AI provider returned an invalid structured response.",
        ) from exc
