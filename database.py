"""
Database Layer for CropCare Case Journal
Handles SQLite database connection, table initialization, consent-based photo storage,
and CRUD operations for triage records.
"""

import sqlite3
import json
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime
from config import DB_PATH


def get_db_connection():
    """Create a sqlite3 connection with dict-like row formatting."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database schema if tables do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        case_id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL,
        crop TEXT NOT NULL,
        confirmed_crop TEXT,
        plant_stage TEXT,
        location_type TEXT,
        weather TEXT,
        watering TEXT,
        affected_area TEXT,
        symptom_duration TEXT,
        symptoms_json TEXT,
        image_quality_passed INTEGER,
        image_metrics_json TEXT,
        top_issue_category TEXT,
        confidence_score REAL,
        triage_summary_json TEXT,
        status TEXT DEFAULT 'Under Observation',
        photo_retained INTEGER DEFAULT 0,
        image_base64 TEXT,
        user_notes TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS case_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT NOT NULL,
        created_at TEXT NOT NULL,
        observation_notes TEXT,
        status_update TEXT,
        FOREIGN KEY (case_id) REFERENCES cases (case_id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()


def save_case(
    case_id: str,
    crop: str,
    plant_stage: str,
    location_type: str,
    weather: str,
    watering: str,
    affected_area: str,
    symptom_duration: str,
    symptoms: List[str],
    image_quality_passed: bool,
    image_metrics: Dict[str, float],
    top_issue_category: str,
    confidence_score: float,
    triage_summary: Dict[str, Any],
    photo_opt_in: bool = False,
    photo_bytes: Optional[bytes] = None,
    user_notes: str = "",
    confirmed_crop: Optional[str] = None
) -> str:
    """
    Save a new triage case.
    Photo is saved ONLY if photo_opt_in is True and photo_bytes is provided.
    """
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    created_at = datetime.now().isoformat()
    symptoms_json = json.dumps(symptoms)
    image_metrics_json = json.dumps(image_metrics)
    triage_summary_json = json.dumps(triage_summary)

    image_b64 = None
    photo_retained_val = 0
    if photo_opt_in and photo_bytes:
        image_b64 = base64.b64encode(photo_bytes).decode('utf-8')
        photo_retained_val = 1

    cursor.execute("""
    INSERT INTO cases (
        case_id, created_at, crop, confirmed_crop, plant_stage, location_type,
        weather, watering, affected_area, symptom_duration, symptoms_json,
        image_quality_passed, image_metrics_json, top_issue_category,
        confidence_score, triage_summary_json, status, photo_retained,
        image_base64, user_notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        case_id,
        created_at,
        crop,
        confirmed_crop or crop,
        plant_stage,
        location_type,
        weather,
        watering,
        affected_area,
        symptom_duration,
        symptoms_json,
        1 if image_quality_passed else 0,
        image_metrics_json,
        top_issue_category,
        confidence_score,
        triage_summary_json,
        "Under Observation",
        photo_retained_val,
        image_b64,
        user_notes
    ))

    # Insert initial log entry
    cursor.execute("""
    INSERT INTO case_logs (case_id, created_at, observation_notes, status_update)
    VALUES (?, ?, ?, ?)
    """, (
        case_id,
        created_at,
        f"Case opened for {crop}. Symptoms reported: {', '.join(symptoms)}.",
        "Under Observation"
    ))

    conn.commit()
    conn.close()
    return case_id


def get_all_cases() -> List[Dict[str, Any]]:
    """Retrieve all case records sorted by creation date descending."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases ORDER BY created_at DESC")
    rows = cursor.fetchall()
    
    cases = []
    for row in rows:
        c = dict(row)
        c["symptoms"] = json.loads(c["symptoms_json"]) if c["symptoms_json"] else []
        c["image_metrics"] = json.loads(c["image_metrics_json"]) if c["image_metrics_json"] else {}
        c["triage_summary"] = json.loads(c["triage_summary_json"]) if c["triage_summary_json"] else {}
        cases.append(c)

    conn.close()
    return cases


def get_case_by_id(case_id: str) -> Optional[Dict[str, Any]]:
    """Fetch single case by ID."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    c = dict(row)
    c["symptoms"] = json.loads(c["symptoms_json"]) if c["symptoms_json"] else []
    c["image_metrics"] = json.loads(c["image_metrics_json"]) if c["image_metrics_json"] else {}
    c["triage_summary"] = json.loads(c["triage_summary_json"]) if c["triage_summary_json"] else {}
    return c


def update_case_status(case_id: str, new_status: str, notes: str = "", confirmed_crop: Optional[str] = None):
    """Update case status, confirmed crop, and add follow-up log."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    if confirmed_crop:
        cursor.execute("UPDATE cases SET status = ?, confirmed_crop = ? WHERE case_id = ?", (new_status, confirmed_crop, case_id))
    else:
        cursor.execute("UPDATE cases SET status = ? WHERE case_id = ?", (new_status, case_id))

    created_at = datetime.now().isoformat()
    cursor.execute("""
    INSERT INTO case_logs (case_id, created_at, observation_notes, status_update)
    VALUES (?, ?, ?, ?)
    """, (case_id, created_at, notes, new_status))

    conn.commit()
    conn.close()


def get_case_logs(case_id: str) -> List[Dict[str, Any]]:
    """Fetch timeline logs for a case."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM case_logs WHERE case_id = ? ORDER BY created_at ASC", (case_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_case(case_id: str):
    """Delete a case and its timeline logs."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM case_logs WHERE case_id = ?", (case_id,))
    cursor.execute("DELETE FROM cases WHERE case_id = ?", (case_id,))
    conn.commit()
    conn.close()
