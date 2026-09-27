from __future__ import annotations

import os
import sqlite3
from contextlib import closing
from enum import Enum
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("TRIAGE_DB", BASE_DIR / "triage.db"))

app = FastAPI(
    title="Inquiry Triage API",
    version="1.0.0",
    description="Classify and prioritize incoming business inquiries for automation workflows.",
)


class Category(str, Enum):
    urgent = "urgent"
    lead = "lead"
    newsletter = "newsletter"
    spam = "spam"
    other = "other"


class InquiryIn(BaseModel):
    sender: str = Field(min_length=1, max_length=320)
    subject: str = Field(default="", max_length=500)
    body: str = Field(min_length=1, max_length=20_000)


class FeedbackIn(BaseModel):
    category: Category


class TriageOut(BaseModel):
    id: int
    category: Category
    priority: int
    reasons: list[str]


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    with closing(connect()) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS inquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                category TEXT NOT NULL,
                priority INTEGER NOT NULL,
                reasons TEXT NOT NULL,
                corrected_category TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        db.commit()


def contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)


def classify(inquiry: InquiryIn) -> tuple[Category, int, list[str]]:
    text = f"{inquiry.subject} {inquiry.body}".lower()

    urgent_terms = (
        "urgent",
        "asap",
        "today",
        "immediately",
        "deadline",
        "emergency",
        "call me",
    )
    lead_terms = (
        "quote",
        "proposal",
        "price",
        "pricing",
        "budget",
        "project",
        "hire",
        "looking for",
        "need help",
        "consultation",
    )
    newsletter_terms = (
        "unsubscribe",
        "newsletter",
        "weekly digest",
        "view in browser",
        "email preferences",
    )
    spam_terms = (
        "crypto opportunity",
        "guaranteed income",
        "casino",
        "lottery",
        "you won",
        "free money",
    )

    reasons: list[str] = []
    priority = 30

    has_urgent = contains_any(text, urgent_terms)
    has_lead = contains_any(text, lead_terms)
    has_newsletter = contains_any(text, newsletter_terms)
    has_spam = contains_any(text, spam_terms)

    if has_urgent:
        priority += 45
        reasons.append("urgent language detected")

    if has_lead:
        priority += 20
        reasons.append("commercial intent detected")

    if has_newsletter:
        priority -= 20
        reasons.append("newsletter markers detected")

    if has_spam:
        priority = 5
        reasons.append("spam markers detected")

    if has_spam:
        category = Category.spam
    elif has_newsletter and not has_lead:
        category = Category.newsletter
    elif has_urgent:
        category = Category.urgent
    elif has_lead:
        category = Category.lead
    else:
        category = Category.other
        reasons.append("no strong routing signal detected")

    priority = max(0, min(priority, 100))
    return category, priority, reasons


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/classify", response_model=TriageOut)
def classify_inquiry(inquiry: InquiryIn) -> TriageOut:
    category, priority, reasons = classify(inquiry)

    with closing(connect()) as db:
        cursor = db.execute(
            """
            INSERT INTO inquiries
                (sender, subject, body, category, priority, reasons)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                inquiry.sender,
                inquiry.subject,
                inquiry.body,
                category.value,
                priority,
                " | ".join(reasons),
            ),
        )
        db.commit()
        inquiry_id = int(cursor.lastrowid)

    return TriageOut(
        id=inquiry_id,
        category=category,
        priority=priority,
        reasons=reasons,
    )


@app.get("/inquiries")
def list_inquiries(limit: int = Query(default=20, ge=1, le=100)) -> list[dict]:
    with closing(connect()) as db:
        rows = db.execute(
            """
            SELECT id, sender, subject, category, priority,
                   corrected_category, created_at
            FROM inquiries
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


@app.post("/feedback/{inquiry_id}")
def correct_category(inquiry_id: int, feedback: FeedbackIn) -> dict:
    with closing(connect()) as db:
        cursor = db.execute(
            """
            UPDATE inquiries
            SET corrected_category = ?
            WHERE id = ?
            """,
            (feedback.category.value, inquiry_id),
        )
        db.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Inquiry not found")

    return {
        "id": inquiry_id,
        "corrected_category": feedback.category.value,
        "status": "saved",
    }


@app.get("/stats")
def stats() -> dict:
    with closing(connect()) as db:
        total = db.execute("SELECT COUNT(*) FROM inquiries").fetchone()[0]
        rows = db.execute(
            """
            SELECT category, COUNT(*) AS count
            FROM inquiries
            GROUP BY category
            ORDER BY count DESC
            """
        ).fetchall()

    return {
        "total": total,
        "by_category": {row["category"]: row["count"] for row in rows},
    }
