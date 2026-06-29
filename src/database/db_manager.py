import json
import sqlite3
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.getenv("DATABASE_PATH", "data/lead_intel.db")
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    company_name TEXT NOT NULL,
                    target_industry TEXT,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    status TEXT NOT NULL
                )
            """)
            
            # Create research_notes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS research_notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    research_notes TEXT,
                    research_summary TEXT,
                    research_sources TEXT,
                    status TEXT NOT NULL,
                    human_feedback TEXT,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            """)
            
            # Create emails table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    email_subject TEXT,
                    email_draft TEXT,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            """)
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def save_session(self, session_id: str, company_name: str, target_industry: Optional[str] = None):
        """Save session information"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now()
            
            cursor.execute("""
                INSERT OR REPLACE INTO sessions 
                (session_id, company_name, target_industry, created_at, updated_at, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                session_id, company_name, target_industry, 
                now, now, "active"
            ))
            conn.commit()
    
    def save_research_state(self, session_id: str, state: Dict[str, Any]):
        """Save research state"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now()
            
            # Convert research_sources to JSON string
            sources_json = json.dumps(state.get("research_sources", []))
            
            cursor.execute("""
                INSERT INTO research_notes 
                (session_id, research_notes, research_summary, research_sources, 
                 status, human_feedback, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                state.get("research_notes"),
                state.get("research_summary"),
                sources_json,
                state.get("research_status", "pending"),
                state.get("human_feedback"),
                now
            ))
            
            # Update session timestamp
            cursor.execute("""
                UPDATE sessions SET updated_at = ? WHERE session_id = ?
            """, (now, session_id))
            
            conn.commit()
    
    def save_email_state(self, session_id: str, state: Dict[str, Any]):
        """Save email state"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now()
            
            cursor.execute("""
                INSERT INTO emails 
                (session_id, email_subject, email_draft, status, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                state.get("email_subject"),
                state.get("email_draft"),
                state.get("email_status", "pending"),
                now
            ))
            
            # Update session status
            cursor.execute("""
                UPDATE sessions SET updated_at = ?, status = ? WHERE session_id = ?
            """, (now, "completed", session_id))
            
            conn.commit()
    
    def load_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load complete session state"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get session info
            cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
            session = cursor.fetchone()
            
            if not session:
                return None
            
            # Get latest research
            cursor.execute("""
                SELECT * FROM research_notes 
                WHERE session_id = ? 
                ORDER BY created_at DESC LIMIT 1
            """, (session_id,))
            research = cursor.fetchone()
            
            # Get latest email
            cursor.execute("""
                SELECT * FROM emails 
                WHERE session_id = ? 
                ORDER BY created_at DESC LIMIT 1
            """, (session_id,))
            email = cursor.fetchone()
            
            state = {
                "session_id": session_id,
                "company_name": session["company_name"],
                "target_industry": session["target_industry"],
                "created_at": session["created_at"],
                "updated_at": session["updated_at"],
                "status": session["status"]
            }
            
            if research:
                state.update({
                    "research_notes": research["research_notes"],
                    "research_summary": research["research_summary"],
                    "research_sources": json.loads(research["research_sources"]) if research["research_sources"] else [],
                    "research_status": research["status"],
                    "human_feedback": research["human_feedback"]
                })
            
            if email:
                state.update({
                    "email_subject": email["email_subject"],
                    "email_draft": email["email_draft"],
                    "email_status": email["status"]
                })
            
            return state

    def list_sessions(self, limit: int = 12) -> list[Dict[str, Any]]:
        """Return recent sessions for the UI explorer"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT session_id, company_name, target_industry, updated_at, status FROM sessions ORDER BY updated_at DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [
                {
                    "session_id": row["session_id"],
                    "company_name": row["company_name"],
                    "target_industry": row["target_industry"],
                    "updated_at": row["updated_at"],
                    "status": row["status"]
                }
                for row in rows
            ]
