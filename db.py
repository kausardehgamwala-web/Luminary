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
