#!/usr/bin/env python3
# Force restart
import asyncio
import os
import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.agents.researcher import ResearcherAgent
from src.agents.writer import WriterAgent
from src.database.db_manager import DatabaseManager
from src.utils.validators import validate_company_name
from src.utils.mailer import SMTPMailer

load_dotenv()

app = Flask(__name__, static_folder="static", template_folder="templates")
db = DatabaseManager()


def run_async(coro):
    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(coro)


def serialize_datetime(value: Any) -> Any:
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def serialize_state(state: Dict[str, Any]) -> Dict[str, Any]:
    return {k: serialize_datetime(v) for k, v in state.items()}


@app.route("/")
def index() -> Any:
    return render_template("index.html")


@app.route("/api/research", methods=["POST"])
def research() -> Any:
    payload = request.get_json() or {}
    company_name = (payload.get("company_name") or "").strip()
    target_industry = (payload.get("target_industry") or "").strip() or None
    max_attempts = int(payload.get("max_attempts") or 3)

    if not company_name:
        return jsonify({"error": "Company name is required."}), 400

    if not validate_company_name(company_name):
        return jsonify({"error": "Invalid company name format."}), 400

    if not os.getenv("GEMINI_API_KEY") or not os.getenv("TAVILY_API_KEY"):
        return jsonify({"error": "Missing GEMINI_API_KEY or TAVILY_API_KEY in .env."}), 500

    session_id = str(uuid.uuid4())

    async def do_research():
        researcher = ResearcherAgent()
        return await researcher.research_company(company_name=company_name, target_industry=target_industry)

    research_result = run_async(do_research())

    if research_result.get("research_status") == "failed":
        return jsonify({"error": research_result.get("error_message", "Research failed.")}), 500

    session_state = {
        "session_id": session_id,
        "company_name": company_name,
        "target_industry": target_industry,
        "research_notes": research_result.get("research_notes"),
        "research_summary": research_result.get("research_summary"),
        "research_sources": research_result.get("research_sources", []),
        "research_status": research_result.get("research_status"),
        "research_timestamp": serialize_datetime(research_result.get("research_timestamp")),
        "status": "research_complete",
    }

    db.save_session(session_id, company_name, target_industry)
    db.save_research_state(session_id, {
        **session_state,
        "human_feedback": None,
        "research_status": research_result.get("research_status", "pending"),
    })

    return jsonify(serialize_state(session_state))


@app.route("/api/email", methods=["POST"])
def email() -> Any:
    payload = request.get_json() or {}
    session_id = payload.get("session_id")
    target_role = (payload.get("target_role") or "CEO").strip()

    if not session_id:
        return jsonify({"error": "session_id is required."}), 400

    session = db.load_session_state(session_id)
    if not session:
        return jsonify({"error": "Session not found."}), 404

    research_summary = session.get("research_summary")
    research_notes = session.get("research_notes")
    company_name = session.get("company_name")

    if not research_summary or not research_notes:
        return jsonify({"error": "Research results are required before generating email."}), 400

    async def do_email():
        writer = WriterAgent()
        return await writer.draft_email(
            company_name=company_name,
            research_summary=research_summary,
            research_notes=research_notes,
            target_role=target_role,
        )

    email_result = run_async(do_email())

    if email_result.get("email_status") == "failed":
        return jsonify({"error": email_result.get("error_message", "Email drafting failed.")}), 500

    db.save_email_state(session_id, {
        "email_subject": email_result.get("email_subject"),
        "email_draft": email_result.get("email_draft"),
        "email_status": email_result.get("email_status", "drafted"),
    })

    response = {
        "session_id": session_id,
        "email_subject": email_result.get("email_subject"),
        "email_draft": email_result.get("email_draft"),
        "email_status": email_result.get("email_status", "drafted"),
    }
    return jsonify(response)


@app.route("/api/send_email", methods=["POST"])
def send_email() -> Any:
    payload = request.get_json() or {}
    session_id = payload.get("session_id")
    recipient_email = payload.get("recipient_email")

    if not session_id or not recipient_email:
        return jsonify({"error": "session_id and recipient_email are required."}), 400

    session = db.load_session_state(session_id)
    if not session:
        return jsonify({"error": "Session not found."}), 404

    email_draft = session.get("email_draft")
    email_subject = session.get("email_subject")

    if not email_draft:
        return jsonify({"error": "Email draft not found in this session."}), 400

    mailer = SMTPMailer()
    result = mailer.send_email(
        recipient=recipient_email,
        subject=email_subject or "Outreach",
        body=email_draft
    )

    if not result.get("success"):
        return jsonify({"error": result.get("error")}), 500

    return jsonify({"message": "Email sent successfully!"}), 200


@app.route("/api/sessions", methods=["GET"])
def sessions() -> Any:
    return jsonify(db.list_sessions(limit=20))


@app.route("/api/session/<session_id>", methods=["GET"])
def get_session(session_id: str) -> Any:
    state = db.load_session_state(session_id)
    if not state:
        return jsonify({"error": "Session not found."}), 404
    return jsonify(serialize_state(state))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8501)), debug=True)
