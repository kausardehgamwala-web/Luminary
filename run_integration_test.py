import json
import sqlite3
import os
import sys
import base64
import urllib.request
from pathlib import Path

# Load API key
env_path = Path(__file__).resolve().parent / ".env"
api_key = None
if env_path.exists():
    for line in env_path.read_text(encoding="utf-8-sig").splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            if k.strip() == "SOCAPI_API_KEY":
                api_key = v.strip()

if not api_key:
    print("Error: SOCAPI_API_KEY not found in .env")
    sys.exit(1)

print(f"Using API Key: {api_key[:10]}...")

# Standard User-Agent to bypass Cloudflare signature blocks
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"

def api_request(method, endpoint, data=None):
    url = f"https://api.social-api.ai/v1{endpoint}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }
    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        if hasattr(e, 'read'):
            print(f"Error {method} {endpoint}: {e.read().decode('utf-8')}")
        else:
            print(f"Error {method} {endpoint}: {e}")
        raise e

def upload_media_bytes(file_bytes, file_name, mime_type):
    url = "https://api.social-api.ai/v1/media/upload"
    boundary = b"----WebKitFormBoundaryTest"
    part_header = (
        b"--" + boundary + b"\r\n" +
        b"Content-Disposition: form-data; name=\"file\"; filename=\"" + file_name.encode("utf-8") + b"\"\r\n" +
        b"Content-Type: " + mime_type.encode("utf-8") + b"\r\n\r\n"
    )
    part_footer = b"\r\n--" + boundary + b"--\r\n"
    body = part_header + file_bytes + part_footer
    
    req = urllib.request.Request(url, data=body, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary.decode('utf-8')}")
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", USER_AGENT)
    
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))

def sync_accounts_to_db(accounts):
    conn = sqlite3.connect("luminary.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get profile ID (default client 1)
    cursor.execute("SELECT id FROM social_profiles WHERE client_id = '1'")
    profile = cursor.fetchone()
    if profile:
        profile_id = profile["id"]
    else:
        import uuid
        profile_id = str(uuid.uuid4())
        cursor.execute("INSERT INTO social_profiles (id, client_id, brand_name) VALUES (?, '1', 'Client 1 Brand')", (profile_id,))
        
    for acc in accounts:
        acc_id = acc["id"]
        platform = acc["platform"]
        username = acc.get("username", acc.get("name", "Unknown"))
        display_name = acc.get("name", "Unknown")
        
        # Check if already exists
        cursor.execute("SELECT id FROM social_connections WHERE socapi_account_id = ?", (acc_id,))
        exists = cursor.fetchone()
        
        if not exists:
            import uuid
            conn_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO social_connections 
                (id, social_profile_id, client_id, platform, socapi_account_id, username, display_name, status) 
                VALUES (?, ?, '1', ?, ?, ?, ?, 'connected')
            """, (conn_id, profile_id, platform, acc_id, username, display_name))
            print(f"Synced new connected account: {platform} ({username})")
        else:
            # Update status to connected
            cursor.execute("UPDATE social_connections SET status = 'connected' WHERE socapi_account_id = ?", (acc_id,))
            print(f"Updated status for connected account: {platform} ({username})")
            
    conn.commit()
    conn.close()

def main():
    print("\n--- 1. Fetching Accounts from SocialAPI ---")
    try:
        resp = api_request("GET", "/accounts")
        accounts = resp.get("data", [])
        print(f"Found {len(accounts)} accounts on SocialAPI profile.")
        if not accounts:
            print("No accounts connected. Please go to Luminary and connect an account first to complete the test.")
            return
            
        sync_accounts_to_db(accounts)
    except Exception as e:
        print("Failed to sync accounts:", e)
        return

    # Select first account for testing
    test_acc = accounts[0]
    print(f"\n--- 2. Initiating Publish Test to: {test_acc['platform']} ({test_acc.get('username')}) ---")

    test_files = [
        {"name": "test_image.png", "type": "image/png", "content": b"fake image bytes data for testing"},
        {"name": "test_video.mp4", "type": "video/mp4", "content": b"fake video bytes data for testing"},
        {"name": "test_doc.docx", "type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document", "content": b"fake docx bytes data for testing"},
        {"name": "test_ppt.ppt", "type": "application/vnd.ms-powerpoint", "content": b"fake ppt bytes data for testing"}
    ]

    for tf in test_files:
        print(f"\nTesting file: {tf['name']} ({tf['type']})")
        try:
            print("Uploading to SocialAPI /media/upload...")
            media_resp = upload_media_bytes(tf["content"], tf["name"], tf["type"])
            media_id = media_resp.get("media_id")
            print(f"Uploaded successfully. Media ID: {media_id}")
            
            print(f"Publishing post to {test_acc['platform']}...")
            post_req = {
                "text": f"Luminary Automated Test: {tf['name']} upload",
                "publish_now": True,
                "targets": [{"account_id": test_acc["id"]}],
                "media_ids": [media_id]
            }
            
            post_resp = api_request("POST", "/posts", post_req)
            print("Publish request success!")
            print(json.dumps(post_resp, indent=2))
        except Exception as e:
            print(f"Outcome: FAILED for {tf['name']}. Details above.")

if __name__ == "__main__":
    main()
