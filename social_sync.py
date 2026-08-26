import time
import threading
import json
import db
import social_api
import uuid
import datetime

def sync_social_data():
    """Background polling function to update metrics for connected accounts."""
    while True:
        print("[Social Sync] Starting sync cycle...")
        
        try:
            # Fetch all accounts from SocialAPI to verify they are still active
            try:
                accounts_data = social_api.api_request("GET", "/accounts")
                remote_accounts = {acc["id"]: acc for acc in accounts_data.get("data", [])}
            except Exception as e:
                print(f"[Social Sync] Failed to fetch accounts from SocialAPI: {e}")
                remote_accounts = {}
                
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Fetch all active connections locally
            cursor.execute("SELECT * FROM social_connections WHERE status = 'connected'")
            active_connections = cursor.fetchall()
            
            today = datetime.date.today().isoformat()
            
            for conn_row in active_connections:
                conn_id = conn_row["id"]
                socapi_account_id = conn_row["socapi_account_id"]
                platform = conn_row["platform"]
                
                # Check if account still exists remotely
                if socapi_account_id not in remote_accounts and remote_accounts:
                    # Account might be disconnected remotely
                    print(f"[Social Sync] Account {socapi_account_id} not found remotely, marking disconnected.")
                    cursor.execute("UPDATE social_connections SET status = 'disconnected' WHERE id = ?", (conn_id,))
                    continue
                
                remote_acc = remote_accounts.get(socapi_account_id, {})
                
                # Since we don't have full metric API paths yet, we avoid faking data.
                # We record 0 or nulls instead of faking.
                metrics = {
                    "followers": 0,
                    "reach": 0,
                    "engagement": 0,
                    "posts_count": 0
                }
                
                # Check if entry for today exists
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
                
                # Update last_synced_at on the connection
                cursor.execute("UPDATE social_connections SET last_synced_at = CURRENT_TIMESTAMP WHERE id = ?", (conn_id,))
                
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[Social Sync] Error: {e}")
            
        print("[Social Sync] Sync cycle complete. Waiting 4 hours...")
        time.sleep(4 * 60 * 60) # Sleep 4 hours

def start_sync_thread():
    t = threading.Thread(target=sync_social_data, daemon=True)
    t.start()
    return t
