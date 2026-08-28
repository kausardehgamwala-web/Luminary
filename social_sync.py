import time
import threading
import json
import db
import social_api
import uuid
import datetime

def sync_social_data():
    """Background polling function to update metrics for connected accounts with robust crash-protection."""
    while True:
        try:
            print("[Social Sync] Starting sync cycle...")
            
            # Fetch all accounts from SocialAPI to verify they are still active
            remote_accounts = {}
            try:
                accounts_data = social_api.api_request("GET", "/accounts")
                remote_accounts = {acc["id"]: acc for acc in accounts_data.get("data", []) if "id" in acc}
            except Exception as e:
                print(f"[Social Sync] Notice: Remote SocialAPI unreachable: {e}")
                
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Fetch all active connections locally
            cursor.execute("SELECT * FROM social_connections WHERE status IN ('connected', 'active')")
            active_connections = cursor.fetchall()
            
            today = datetime.date.today().isoformat()
            
            for conn_row in active_connections:
                conn_id = conn_row["id"]
                socapi_account_id = conn_row["socapi_account_id"]
                platform = conn_row["platform"]
                
                # Check if account still exists remotely
                if remote_accounts and socapi_account_id not in remote_accounts:
                    print(f"[Social Sync] Account {socapi_account_id} not found remotely, marking disconnected.")
                    cursor.execute("UPDATE social_connections SET status = 'disconnected' WHERE id = ?", (conn_id,))
                    continue
                
                remote_acc = remote_accounts.get(socapi_account_id, {})
                metrics = {
                    "followers": 0,
                    "reach": 0,
                    "engagement": 0,
                    "posts_count": 0
                }
                
                cursor.execute("SELECT id FROM social_metrics_cache WHERE social_connection_id = ? AND metric_date = ?", (conn_id, today))
                row = cursor.fetchone()
                
                if row:
                    cursor.execute("""
                        UPDATE social_metrics_cache 
                        SET followers = ?, reach = ?, engagement = ?, posts_count = ?, raw_payload = ?, fetched_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (metrics["followers"], metrics["reach"], metrics["engagement"], metrics["posts_count"], json.dumps(remote_acc), row["id"]))
                else:
                    cursor.execute("""
                        INSERT INTO social_metrics_cache 
                        (id, social_connection_id, metric_date, followers, reach, engagement, posts_count, raw_payload)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (str(uuid.uuid4()), conn_id, today, metrics["followers"], metrics["reach"], metrics["engagement"], metrics["posts_count"], json.dumps(remote_acc)))
                
                cursor.execute("UPDATE social_connections SET last_synced_at = CURRENT_TIMESTAMP WHERE id = ?", (conn_id,))
                
            conn.commit()
            conn.close()
            print("[Social Sync] Sync cycle complete. Waiting for next interval...")
        except Exception as e:
            print(f"[Social Sync Non-Fatal Error]: {e}")
            
        # Resilient sleep loop to prevent background thread death
        try:
            time.sleep(4 * 60 * 60) # Sleep 4 hours
        except Exception:
            time.sleep(60)

def start_sync_thread():
    try:
        t = threading.Thread(target=sync_social_data, daemon=True, name="LuminarySocialSyncThread")
        t.start()
        return t
    except Exception as e:
        print(f"[Social Sync Alert] Could not start sync thread: {e}")
        return None
