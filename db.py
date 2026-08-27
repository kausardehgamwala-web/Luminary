from datetime import datetime, timezone
import sqlite3
import uuid
import json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "luminary.db"

def get_connection():
    # Return a connection with row_factory set to sqlite3.Row for dict-like access
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Create clients table (since Luminary lacks a formal clients table currently)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # One row per client/brand, mirrors a SocialAPI.ai "social profile"
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS social_profiles (
        id TEXT PRIMARY KEY,
        client_id TEXT NOT NULL,
        socapi_profile_id TEXT,
        brand_name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (client_id) REFERENCES clients(id)
    );
    """)

    # One row per connected platform account under a client
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS social_connections (
        id TEXT PRIMARY KEY,
        social_profile_id TEXT NOT NULL,
        client_id TEXT NOT NULL,
        platform TEXT NOT NULL,
        socapi_account_id TEXT NOT NULL,
        socapi_brand_id TEXT,
        username TEXT,
        display_name TEXT,
        status TEXT DEFAULT 'connected',
        connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_synced_at TIMESTAMP,
        FOREIGN KEY (social_profile_id) REFERENCES social_profiles(id),
        FOREIGN KEY (client_id) REFERENCES clients(id)
    );
    """)

    # Schema Migration Check: Ensure socapi_brand_id exists on existing databases
    cursor.execute("PRAGMA table_info(social_connections)")
    columns = [row["name"] for row in cursor.fetchall()]
    if "socapi_brand_id" not in columns:
        cursor.execute("ALTER TABLE social_connections ADD COLUMN socapi_brand_id TEXT")
        
    # Persistent Security & Content Safety Audit Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS security_audit_logs (
        id TEXT PRIMARY KEY,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        client_id TEXT NOT NULL,
        category TEXT NOT NULL,
        severity TEXT NOT NULL,
        reason TEXT NOT NULL,
        blocked_content TEXT
    );
    """)

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS generation_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        client_id TEXT NOT NULL,
        deliverable_type TEXT NOT NULL,
        template_id TEXT,
        model_name TEXT,
        duration_seconds REAL,
        qc_score REAL,
        qc_passed_first_attempt INTEGER,
        revisions_count INTEGER
    );
    ''')
    conn.commit()

    # Cached/normalized metrics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS social_metrics_cache (
        id TEXT PRIMARY KEY,
        social_connection_id TEXT NOT NULL,
        metric_date DATE NOT NULL,
        followers INTEGER,
        reach INTEGER,
        engagement INTEGER,
        posts_count INTEGER,
        raw_payload TEXT,
        fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (social_connection_id) REFERENCES social_connections(id)
    );
    """)

    # Cached inbox items (comments/DMs/reviews)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS social_inbox_cache (
        id TEXT PRIMARY KEY,
        social_connection_id TEXT NOT NULL,
        socapi_item_id TEXT NOT NULL,
        type TEXT,
        content TEXT,
        author TEXT,
        received_at TIMESTAMP,
        synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (social_connection_id) REFERENCES social_connections(id)
    );
    """)

    conn.commit()
    
    # Ensure there is a default client for testing purposes
    cursor.execute("SELECT id FROM clients LIMIT 1")
    if not cursor.fetchone():
        default_client_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO clients (id, name) VALUES (?, ?)", (default_client_id, "Default Luminary Client"))
        
        # Also create a default social profile
        default_profile_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO social_profiles (id, client_id, brand_name) VALUES (?, ?, ?)", 
                       (default_profile_id, default_client_id, "Luminary Brand"))
        conn.commit()

    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")


def log_security_audit(client_id: str, category: str, severity: str, reason: str, blocked_content: str = "") -> str:
    """Persistently records a blocked security/safety event into SQLite."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        log_id = f"sec_log_{uuid.uuid4().hex[:12]}"
        cursor.execute(
            """
            INSERT INTO security_audit_logs (id, client_id, category, severity, reason, blocked_content)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (log_id, str(client_id or "anonymous"), str(category), str(severity), str(reason), str(blocked_content)[:1500])
        )
        conn.commit()
        conn.close()
        return log_id
    except Exception as ex:
        print(f"[Audit Log Error]: Failed to write security audit to SQLite: {ex}")
        return ""

def get_security_audit_logs(limit: int = 50, client_id: str = None) -> list:
    """Fetches recent security audit logs from SQLite."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if client_id:
            cursor.execute(
                "SELECT * FROM security_audit_logs WHERE client_id = ? ORDER BY timestamp DESC LIMIT ?",
                (str(client_id), limit)
            )
        else:
            cursor.execute("SELECT * FROM security_audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        logs = [dict(r) for r in rows]
        conn.close()
        return logs
    except Exception as ex:
        print(f"[Audit Log Fetch Error]: {ex}")
        return []


def log_generation_metric(client_id: str, deliverable_type: str, template_id: str, model_name: str, duration_seconds: float, qc_score: float, qc_passed_first_attempt: bool, revisions_count: int = 0):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            '''
            INSERT INTO generation_metrics 
            (timestamp, client_id, deliverable_type, template_id, model_name, duration_seconds, qc_score, qc_passed_first_attempt, revisions_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                datetime.now(timezone.utc).isoformat(),
                str(client_id),
                str(deliverable_type),
                str(template_id),
                str(model_name),
                float(duration_seconds),
                float(qc_score),
                1 if qc_passed_first_attempt else 0,
                int(revisions_count)
            )
        )
        conn.commit()

def get_generation_metrics_summary(limit: int = 50) -> dict:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), AVG(duration_seconds), AVG(qc_score), SUM(qc_passed_first_attempt) FROM generation_metrics")
        total, avg_dur, avg_score, first_pass_count = cursor.fetchone()
        
        cursor.execute("SELECT id, timestamp, client_id, deliverable_type, template_id, model_name, duration_seconds, qc_score, qc_passed_first_attempt, revisions_count FROM generation_metrics ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        
        recent = []
        for r in rows:
            recent.append({
                "id": r[0], "timestamp": r[1], "client_id": r[2], "deliverable_type": r[3],
                "template_id": r[4], "model_name": r[5], "duration_seconds": r[6], "qc_score": r[7],
                "qc_passed_first_attempt": bool(r[8]), "revisions_count": r[9]
            })
            
        return {
            "total_generations": total or 0,
            "avg_duration_seconds": round(avg_dur or 0, 2),
            "avg_qc_score": round(avg_score or 0, 2),
            "first_pass_success_rate": round((first_pass_count or 0) / max(total or 1, 1) * 100, 1),
            "recent_runs": recent
        }
