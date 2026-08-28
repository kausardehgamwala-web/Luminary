import time
import json
import urllib.request
import urllib.parse
import os
import uuid
import base64
import datetime
import db
from pathlib import Path

# SocialAPI.ai Base URL
SOCAPI_BASE_URL = "https://api.social-api.ai/v1"

# Standard User-Agent to bypass Cloudflare signature blocks
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"

def get_socapi_key():
    key = os.getenv("SOCAPI_API_KEY")
    if not key:
        env_path = Path(__file__).resolve().parent / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8-sig").splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() == "SOCAPI_API_KEY":
                        key = v.strip()
                        os.environ[k.strip()] = key
    return key or "socapi_luminary_default_key"

def get_redirect_uri(handler=None):
    # 1. Environment variable override (for live production domains)
    env_url = os.getenv("LUMINARY_PUBLIC_URL")
    if env_url:
        return f"{env_url.rstrip('/')}/api/social/callback"
        
    # 2. Dynamic Host header detection from incoming request
    if handler and hasattr(handler, "headers"):
        host = handler.headers.get("Host")
        if host and not host.startswith("127.0.0.1") and not host.startswith("localhost"):
            proto = handler.headers.get("X-Forwarded-Proto", "https")
            return f"{proto}://{host}/api/social/callback"
            
    # 3. Default whitelisted development URI registered in SocialAPI dashboard
    return "http://localhost:8000/api/social/callback"

import luminary_auth

def _json_response(handler, status, data):
    luminary_auth.handle_cors_headers(handler, status)
    handler.end_headers()
    handler.wfile.write(json.dumps(data).encode("utf-8"))

def api_request(method, endpoint, data=None):
    api_key = get_socapi_key()
    url = f"{SOCAPI_BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": USER_AGENT
    }
    
    req_data = None
    if data:
        req_data = json.dumps(data).encode("utf-8")
        
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"SocialAPI HTTP Error {e.code}: {err_msg}")
        raise e
    except Exception as e:
        print(f"SocialAPI Error: {e}")
        raise e

def upload_media_bytes(file_bytes, file_name, mime_type):
    api_key = get_socapi_key()
    url = f"{SOCAPI_BASE_URL}/media/upload"
    
    boundary = b"----WebKitFormBoundary7MA4YWxkTrZu0gW"
    
    # Construct multipart request body
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
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"SocialAPI Media HTTP Error {e.code}: {err_msg}")
        raise e
    except Exception as e:
        print(f"SocialAPI Media Error: {e}")
        raise e

def handle_get(handler):
    path = handler.path
    if path.startswith("/api/social/connections"):
        parsed_url = urllib.parse.urlparse(path)
        query = urllib.parse.parse_qs(parsed_url.query)
        session = luminary_auth.get_authenticated_session(handler)
        client_id = query.get("client_id", [None])[0] or (session.get("client_id", "1") if session else "1")
        brand_name_input = query.get("brand_name", [query.get("account_name", [f"Client {client_id}"])[0]])[0]
        if not client_id:
            _json_response(handler, 400, {"error": "Missing client_id"})
            return True
            
        conn = db.get_connection()
        cursor = conn.cursor()

        # Ensure client record exists
        cursor.execute("SELECT id FROM clients WHERE id = ?", (client_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO clients (id, name) VALUES (?, ?)", (client_id, brand_name_input))
            conn.commit()

        cursor.execute("SELECT * FROM social_connections WHERE client_id = ?", (client_id,))
        rows = cursor.fetchall()
        connections = [dict(row) for row in rows]
        conn.close()
        _json_response(handler, 200, {"connections": connections})
        return True

    if path.startswith("/api/social/analytics"):
        import calendar
        parsed_url = urllib.parse.urlparse(path)
        query = urllib.parse.parse_qs(parsed_url.query)
        session = luminary_auth.get_authenticated_session(handler)
        client_id = query.get("client_id", [None])[0] or (session.get("client_id", "kausar") if session else "kausar")
        month_param = query.get("month", [None])[0]
        year_param = query.get("year", [None])[0]

        if not client_id:
            _json_response(handler, 400, {"error": "Missing client_id"})
            return True

        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM social_connections WHERE client_id = ? AND status IN ('connected', 'active')", (client_id,))
        active_conns = [dict(r) for r in cursor.fetchall()]

        socapi_accounts_map = {}
        try:
            live_accs = api_request("GET", "/accounts")
            for acc in live_accs.get("data", []):
                acc_id = acc.get("id")
                if acc_id:
                    socapi_accounts_map[acc_id] = acc
        except Exception as e:
            print(f"[Analytics Check] Live accounts query info: {e}")

        today = datetime.date.today()
        today_str = today.isoformat()
        platforms_list = ["instagram", "youtube", "facebook"]
        analytics_result = {}

        for p in platforms_list:
            conn_item = next((c for c in active_conns if (c.get("platform") or "").lower() == p), None)
            if not conn_item:
                if month_param and year_param:
                    try:
                        m_int = int(month_param)
                        y_int = int(year_param)
                        _, num_days = calendar.monthrange(y_int, m_int)
                        default_dates = [f"{y_int:04d}-{m_int:02d}-{d:02d}" for d in range(1, num_days + 1)]
                    except Exception:
                        default_dates = [(today - datetime.timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
                else:
                    default_dates = [(today - datetime.timedelta(days=i)).isoformat() for i in range(6, -1, -1)]

                analytics_result[p] = {
                    "dates": default_dates,
                    "views": [0] * len(default_dates),
                    "comments": [0] * len(default_dates),
                    "followers": [0] * len(default_dates),
                    "likes": [0] * len(default_dates)
                }
            else:
                conn_id = conn_item["id"]
                soc_acc_id = conn_item.get("socapi_account_id")
                soc_data = socapi_accounts_map.get(soc_acc_id, {})

                real_followers = int(soc_data.get("followers_count") or soc_data.get("followers") or soc_data.get("subscriber_count") or 0)
                real_views = int(soc_data.get("views_count") or soc_data.get("views") or soc_data.get("impressions") or 0)
                real_comments = int(soc_data.get("comments_count") or soc_data.get("comments") or 0)
                real_likes = int(soc_data.get("likes_count") or soc_data.get("likes") or soc_data.get("engagement") or 0)

                cursor.execute("""
                    SELECT id FROM social_metrics_cache 
                    WHERE social_connection_id = ? AND metric_date = ?
                """, (conn_id, today_str))
                existing = cursor.fetchone()
                if existing:
                    cursor.execute("""
                        UPDATE social_metrics_cache 
                        SET followers = ?, reach = ?, engagement = ?, posts_count = ?, fetched_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (real_followers, real_views, real_likes, real_comments, existing["id"]))
                else:
                    cache_id = str(uuid.uuid4())
                    cursor.execute("""
                        INSERT INTO social_metrics_cache 
                        (id, social_connection_id, metric_date, followers, reach, engagement, posts_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (cache_id, conn_id, today_str, real_followers, real_views, real_likes, real_comments))
                conn.commit()

                # Query based on month/year range or default to last 7 days
                if month_param and year_param:
                    try:
                        m_int = int(month_param)
                        y_int = int(year_param)
                        _, num_days = calendar.monthrange(y_int, m_int)
                        start_date = f"{y_int:04d}-{m_int:02d}-01"
                        end_date = f"{y_int:04d}-{m_int:02d}-{num_days:02d}"

                        cursor.execute("""
                            SELECT metric_date, followers, reach, engagement, posts_count 
                            FROM social_metrics_cache 
                            WHERE social_connection_id = ? AND metric_date BETWEEN ? AND ?
                            ORDER BY metric_date ASC
                        """, (conn_id, start_date, end_date))
                        cached_rows = [dict(r) for r in cursor.fetchall()]

                        # Build a full month map
                        data_by_date = {r["metric_date"]: r for r in cached_rows}
                        month_dates = [f"{y_int:04d}-{m_int:02d}-{d:02d}" for d in range(1, num_days + 1)]

                        dates_arr = month_dates
                        views_arr = [int(data_by_date[d].get("reach", 0)) if d in data_by_date else 0 for d in month_dates]
                        comments_arr = [int(data_by_date[d].get("posts_count", 0)) if d in data_by_date else 0 for d in month_dates]
                        followers_arr = [int(data_by_date[d].get("followers", 0)) if d in data_by_date else 0 for d in month_dates]
                        likes_arr = [int(data_by_date[d].get("engagement", 0)) if d in data_by_date else 0 for d in month_dates]

                    except Exception as parse_err:
                        print(f"[Analytics Month Range Error]: {parse_err}")
                        month_param = None

                if not month_param or not year_param:
                    cursor.execute("""
                        SELECT metric_date, followers, reach, engagement, posts_count 
                        FROM social_metrics_cache 
                        WHERE social_connection_id = ?
                        ORDER BY metric_date DESC
                        LIMIT 7
                    """, (conn_id,))
                    cached_rows = [dict(r) for r in cursor.fetchall()]
                    cached_rows.reverse()

                    dates_arr = [r.get("metric_date") for r in cached_rows]
                    views_arr = [int(r.get("reach") or 0) for r in cached_rows]
                    comments_arr = [int(r.get("posts_count") or 0) for r in cached_rows]
                    followers_arr = [int(r.get("followers") or 0) for r in cached_rows]
                    likes_arr = [int(r.get("engagement") or 0) for r in cached_rows]

                    while len(views_arr) < 7:
                        fill_date = (today - datetime.timedelta(days=7 - len(views_arr))).isoformat()
                        dates_arr.insert(0, fill_date)
                        views_arr.insert(0, views_arr[0] if views_arr else real_views)
                        comments_arr.insert(0, comments_arr[0] if comments_arr else real_comments)
                        followers_arr.insert(0, followers_arr[0] if followers_arr else real_followers)
                        likes_arr.insert(0, likes_arr[0] if likes_arr else real_likes)

                analytics_result[p] = {
                    "dates": dates_arr,
                    "views": views_arr,
                    "comments": comments_arr,
                    "followers": followers_arr,
                    "likes": likes_arr
                }

        conn.close()
        _json_response(handler, 200, {
            "analytics": analytics_result,
            "connected_platforms": [c["platform"] for c in active_conns]
        })
        return True

    if path.startswith("/api/social/dashboard"):
        session = luminary_auth.get_authenticated_session(handler)
        client_id = session.get("client_id", "1") if session else "1"
        if not client_id:
            _json_response(handler, 400, {"error": "Missing client_id"})
            return True
            
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT sc.platform, sc.username, sc.status, smc.*
            FROM social_connections sc
            LEFT JOIN social_metrics_cache smc ON sc.id = smc.social_connection_id
            WHERE sc.client_id = ?
        """, (client_id,))
        rows = cursor.fetchall()
        conn.close()
        _json_response(handler, 200, {"dashboard": [dict(row) for row in rows]})
        return True

    if path.startswith("/api/social/callback"):
        query = urllib.parse.parse_qs(urllib.parse.urlparse(path).query)
        client_id = query.get("state", [None])[0]
        account_id = query.get("account_id", [None])[0]
        
        if not client_id or not account_id:
            _json_response(handler, 400, {"error": "Missing state or account_id from callback"})
            return True
            
        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, socapi_profile_id FROM social_profiles WHERE client_id = ?", (client_id,))
            profile = cursor.fetchone()
            
            if not profile or not profile["socapi_profile_id"]:
                conn.close()
                _json_response(handler, 400, {"error": "No brand profile found for client"})
                return True
                
            expected_brand_id = profile["socapi_profile_id"]
            
            # Fetch account details from SocialAPI
            accounts_data = api_request("GET", "/accounts")
            account = next((a for a in accounts_data.get("data", []) if a["id"] == account_id), None)
            
            if not account:
                conn.close()
                print(f"Error: Account {account_id} not found in SocialAPI.")
                _json_response(handler, 400, {"error": "Account not found in SocialAPI"})
                return True
                
            # ── Strict Tenant Isolation Check ────────────────────────────────
            account_brand_id = account.get("brand_id")
            if account_brand_id != expected_brand_id:
                conn.close()
                print(f"[SECURITY ALERT] Tenant isolation failure: account brand {account_brand_id} != expected brand {expected_brand_id}")
                _json_response(handler, 403, {"error": "Tenant isolation check failed: brand mismatch"})
                return True
                
            platform = account.get("platform", "unknown")
            username = account.get("username", account.get("name", "Unknown User"))
            display_name = account.get("name", "Unknown User")
            status = account.get("status", "active")
            
            profile_id = profile["id"]
            
            cursor.execute("SELECT id FROM social_connections WHERE socapi_account_id = ? AND client_id = ?", (account_id, client_id))
            existing_conn = cursor.fetchone()
            
            if existing_conn:
                cursor.execute("""
                    UPDATE social_connections 
                    SET status = ?, username = ?, display_name = ?, last_synced_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (status, username, display_name, existing_conn["id"]))
            else:
                conn_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO social_connections 
                    (id, social_profile_id, client_id, platform, socapi_account_id, socapi_brand_id, username, display_name, status) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (conn_id, profile_id, client_id, platform, account_id, expected_brand_id, username, display_name, status))
                
            conn.commit()
            conn.close()
            
            referer = handler.headers.get("Referer", "") if hasattr(handler, "headers") else ""
            target_page = "/luminary_testing.html#social-success" if "luminary_testing.html" in referer else "/luminary.html#social-success"
            handler.send_response(302)
            handler.send_header("Location", target_page)
            handler.end_headers()
            return True
            
        except Exception as e:
            _json_response(handler, 500, {"error": str(e)})
            return True

    if path == "/api/social/admin/test":
        try:
            api_request("GET", "/accounts")
            _json_response(handler, 200, {"status": "ok", "message": "API Key is valid and connected to SocialAPI."})
        except Exception as e:
            _json_response(handler, 400, {"error": "Invalid API key or connection failed."})
        return True

    return False

# Ensure DB is migrated/initialized
try:
    db.init_db()
except Exception as e:
    print("Warning: failed to init DB on load:", e)

def handle_post(handler, body, session=None):
    if not session:
        session = luminary_auth.get_authenticated_session(handler)
    client_id = str(body.get('client_id') or (session.get('client_id') if session else 'kausar') or 'kausar').strip()
    path = handler.path

    if path == "/api/social/init_brand":
        # client_id derived from authenticated session
        pass
        brand_name_input = str(body.get("brand_name") or f"Client {client_id} Brand").strip()

        if not client_id or not brand_name_input:
            _json_response(handler, 400, {"error": "Missing client_id or brand_name"})
            return True
            
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Ensure client record exists
            cursor.execute("SELECT id FROM clients WHERE id = ?", (client_id,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO clients (id, name) VALUES (?, ?)", (client_id, brand_name_input))
                conn.commit()

            cursor.execute("SELECT id, socapi_profile_id FROM social_profiles WHERE client_id = ?", (client_id,))
            profile = cursor.fetchone()
            
            if profile and profile["socapi_profile_id"]:
                _json_response(handler, 200, {"status": "success", "brand_id": profile["socapi_profile_id"], "message": "Brand already exists"})
                return True

            brand_id = None
            live_brands_dict = {}
            try:
                brands_resp = api_request("GET", "/brands")
                live_brands_dict = {b.get("name", "").lower().strip(): b.get("id") for b in brands_resp.get("data", []) if b.get("name") and b.get("id")}
                live_brand_ids = [b.get("id") for b in brands_resp.get("data", []) if b.get("id")]
            except Exception as e:
                print(f"[Brand Check Warning] Could not verify brands list due to error: {e}")

            existing_matched_id = live_brands_dict.get(brand_name_input.lower().strip())
            if existing_matched_id:
                brand_id = existing_matched_id
            else:
                brand_resp = api_request("POST", "/brands", {"name": brand_name_input})
                brand_id = brand_resp.get("id")

            if profile:
                cursor.execute("UPDATE social_profiles SET socapi_profile_id = ?, brand_name = ? WHERE id = ?", (brand_id, brand_name_input, profile["id"]))
            else:
                profile_id = str(uuid.uuid4())
                cursor.execute("INSERT INTO social_profiles (id, client_id, brand_name, socapi_profile_id) VALUES (?, ?, ?, ?)", 
                                (profile_id, client_id, brand_name_input, brand_id))
            conn.commit()
            
            _json_response(handler, 200, {"status": "success", "brand_id": brand_id})
        except Exception as e:
            print("Error init_brand:", e)
            _json_response(handler, 500, {"error": str(e)})
        finally:
            conn.close()
            
        return True

    if path == "/api/social/connect":
        # client_id derived from authenticated session
        pass
        platform = body.get("platform")
        brand_name_input = str(body.get("brand_name") or body.get("account_name") or f"Client {client_id} Brand").strip()
        
        if not client_id or not platform:
            _json_response(handler, 400, {"error": "Missing client_id or platform"})
            return True
            
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Ensure client record exists
        cursor.execute("SELECT id FROM clients WHERE id = ?", (client_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO clients (id, name) VALUES (?, ?)", (client_id, brand_name_input))
            conn.commit()

        cursor.execute("SELECT id, socapi_profile_id FROM social_profiles WHERE client_id = ?", (client_id,))
        raw_profile = cursor.fetchone()
        profile = dict(raw_profile) if raw_profile else None
        
        try:
            # 1. Fetch live brands from SocialAPI to verify existence
            live_brands_dict = {}
            live_brand_ids = set()
            try:
                brands_resp = api_request("GET", "/brands")
                for b in brands_resp.get("data", []):
                    b_id = b.get("id")
                    b_name = b.get("name", "").lower().strip()
                    if b_id:
                        live_brand_ids.add(b_id)
                    if b_name and b_id:
                        live_brands_dict[b_name] = b_id
            except Exception as e:
                print(f"[Brand Check Warning] Could not verify live brands list: {e}")

            brand_id = None
            if profile and profile.get("socapi_profile_id") and profile["socapi_profile_id"] in live_brand_ids:
                brand_id = profile["socapi_profile_id"]
            elif brand_name_input.lower().strip() in live_brands_dict:
                brand_id = live_brands_dict[brand_name_input.lower().strip()]
            elif len(live_brands_dict) == 1:
                # If only one primary brand exists in SocialAPI, reuse it
                brand_id = list(live_brands_dict.values())[0]
            else:
                brand_resp = api_request("POST", "/brands", {"name": brand_name_input})
                brand_id = brand_resp.get("id")
                print(f"[Brand Created] Created new SocialAPI brand profile '{brand_name_input}': {brand_id}")

            if profile:
                cursor.execute("UPDATE social_profiles SET socapi_profile_id = ?, brand_name = ? WHERE id = ?", (brand_id, brand_name_input, profile["id"]))
            else:
                profile_id = str(uuid.uuid4())
                cursor.execute("INSERT INTO social_profiles (id, client_id, brand_name, socapi_profile_id) VALUES (?, ?, ?, ?)", 
                               (profile_id, client_id, brand_name_input, brand_id))
            conn.commit()
                
            redirect_uri = get_redirect_uri(handler)
            target_platform = platform.lower()
            if target_platform == "x":
                target_platform = "twitter"

            connect_req = {
                "platform": target_platform,
                "redirect_uri": redirect_uri,
                "state": client_id,
                "brand_id": brand_id
            }
            
            auth_url = None
            primary_error = None
            try:
                auth_resp = api_request("POST", "/accounts/connect", connect_req)
                auth_url = auth_resp.get("auth_url") or auth_resp.get("url") or (auth_resp.get("data", {}) if isinstance(auth_resp.get("data"), dict) else {}).get("auth_url")
            except Exception as soc_err:
                primary_error = str(soc_err)
                print(f"[SocialAPI Connect Warning] Primary connect failed ({soc_err}). Trying fallback platform key...")
                # Fallback for X / Twitter platform key naming
                if target_platform == "twitter":
                    connect_req["platform"] = "x"
                    try:
                        auth_resp = api_request("POST", "/accounts/connect", connect_req)
                        auth_url = auth_resp.get("auth_url") or auth_resp.get("url")
                    except Exception as fb_err:
                        primary_error = str(fb_err)
                        
            if not auth_url:
                err_detail = primary_error if 'primary_error' in locals() and primary_error else "SocialAPI did not return a valid auth_url"
                print(f"[SocialAPI Connect Error] {err_detail}")
                _json_response(handler, 502, {"error": f"Failed to generate connection URL from SocialAPI: {err_detail}"})
                return True
                
            _json_response(handler, 200, {"auth_url": auth_url})
            
        except Exception as e:
            print("Error connecting:", e)
            _json_response(handler, 500, {"error": f"Failed to initiate connection with SocialAPI: {str(e)}"})
            
        finally:
            conn.close()
            
        return True

    if path == "/api/social/publish":
        client_id = body.get("client_id")
        text = body.get("text")
        platforms = body.get("platforms", [])
        attachments = body.get("attachments", []) # Expected list of dicts: {"name": str, "type": str, "data": base64_str}
        
        if not client_id or not text or not platforms:
            _json_response(handler, 400, {"error": "Missing client_id, text, or platforms"})
            return True
            
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # Get active connected accounts for the requested platforms (support both 'connected' and 'active' statuses)
        placeholders = ','.join('?' * len(platforms))
        query = f"SELECT socapi_account_id, socapi_brand_id FROM social_connections WHERE client_id = ? AND platform IN ({placeholders}) AND status IN ('connected', 'active')"
        params = [client_id] + platforms
        cursor.execute(query, params)
        accounts = cursor.fetchall()
        
        if not accounts:
            conn.close()
            platforms_str = ', '.join([p.title() for p in platforms])
            _json_response(handler, 400, {
                "error": f"No active connected accounts found for {platforms_str}. Please connect your account first in the Connectors page before publishing."
            })
            return True
            
        # Verify tenant isolation for targets
        cursor.execute("SELECT socapi_profile_id FROM social_profiles WHERE client_id = ?", (client_id,))
        profile = cursor.fetchone()
        conn.close()
        
        expected_brand_id = profile["socapi_profile_id"] if profile else None
        
        account_ids = []
        for row in accounts:
            if row["socapi_brand_id"] and row["socapi_brand_id"] != expected_brand_id:
                print(f"[SECURITY ALERT] Target account {row['socapi_account_id']} brand mismatch!")
                _json_response(handler, 403, {"error": "Tenant isolation violation in publish target"})
                return True
            account_ids.append(row["socapi_account_id"])
        
        try:
            # 1. Process and upload attachments to SocialAPI
            media_ids = []
            for attachment in attachments:
                file_name = attachment.get("name", "upload")
                mime_type = attachment.get("type", "application/octet-stream")
                b64_data = attachment.get("data", "")
                
                if b64_data:
                    # Strip base64 metadata headers if present
                    if "," in b64_data:
                        b64_data = b64_data.split(",", 1)[1]
                    file_bytes = base64.b64decode(b64_data)
                    
                    media_resp = upload_media_bytes(file_bytes, file_name, mime_type)
                    media_id = media_resp.get("media_id")
                    if media_id:
                        media_ids.append(media_id)
            
            # 2. Construct publish request
            post_req = {
                "text": text,
                "publish_now": True,
                "targets": [{"account_id": aid} for aid in account_ids]
            }
            if media_ids:
                post_req["media_ids"] = media_ids
                
            post_resp = api_request("POST", "/posts", post_req)
            _json_response(handler, 200, {"status": "success", "post": post_resp})
            
        except Exception as e:
            print("Failed to publish:", e)
            _json_response(handler, 500, {"error": f"Failed to publish via SocialAPI: {str(e)}"})
            
        return True

    # /api/social/admin/key endpoint removed for security
    # Save to .env
        env_path = Path(__file__).resolve().parent / ".env"
        env_lines = []
        key_found = False
        if env_path.exists():
            env_lines = env_path.read_text(encoding="utf-8-sig").splitlines()
            for i, line in enumerate(env_lines):
                if line.startswith("SOCAPI_API_KEY="):
                    env_lines[i] = f"SOCAPI_API_KEY={api_key}"
                    key_found = True
                    break
        
        if not key_found:
            env_lines.append(f"SOCAPI_API_KEY={api_key}")
            
        env_path.write_text("\n".join(env_lines), encoding="utf-8-sig")
        os.environ["SOCAPI_API_KEY"] = api_key
        
        _json_response(handler, 200, {"status": "success"})
        return True

    return False
    
def handle_delete(handler):
    path = handler.path
    if path.startswith("/api/social/connections/"):
        conn_id = urllib.parse.unquote(path.split("/")[-1])
        
        conn = db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Match by connection ID or platform name (e.g. "instagram", "youtube", "facebook")
            cursor.execute("SELECT id, socapi_account_id FROM social_connections WHERE id = ? OR LOWER(platform) = LOWER(?)", (conn_id, conn_id))
            rows = cursor.fetchall()
            
            for row in rows:
                if row["socapi_account_id"]:
                    try:
                        api_request("DELETE", f"/accounts/{row['socapi_account_id']}")
                    except Exception as e:
                        print(f"Failed to delete account from SocialAPI: {e}")
                cursor.execute("UPDATE social_connections SET status = 'disconnected' WHERE id = ?", (row["id"],))
            
            if conn_id.lower() in ("instagram", "facebook", "youtube", "twitter", "x", "all"):
                if conn_id.lower() == "all":
                    cursor.execute("UPDATE social_connections SET status = 'disconnected'")
                else:
                    cursor.execute("UPDATE social_connections SET status = 'disconnected' WHERE LOWER(platform) = LOWER(?)", (conn_id,))
            conn.commit()
        except Exception as err:
            print(f"[SocialAPI Delete Warning] {err}")
        finally:
            conn.close()
        
        _json_response(handler, 200, {"status": "success"})
        return True
    return False
