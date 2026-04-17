# utils/auth.py
# ─── Authentication & User Management via Google Sheets ──────────────────────

import streamlit as st
import bcrypt
import json
from datetime import datetime, date
import pytz

# ── Google Sheets connection ──────────────────────────────────────────────────
def _get_sheet():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds_dict = json.loads(st.secrets["google_sheets"]["credentials"])
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        gc = gspread.authorize(creds)
        sh = gc.open_by_key(st.secrets["google_sheets"]["spreadsheet_id"])
        return sh.sheet1
    except Exception as e:
        st.error(f"Google Sheets 連接失敗: {e}")
        return None


@st.cache_data(ttl=60)
def load_all_users() -> list[dict]:
    ws = _get_sheet()
    if not ws:
        return []
    try:
        records = ws.get_all_records()
        return records
    except Exception:
        return []


def find_user(username: str) -> dict | None:
    users = load_all_users()
    for u in users:
        if str(u.get("username", "")).strip().lower() == username.strip().lower():
            return u
    return None


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def check_expiry(user: dict) -> str:
    """Returns: 'ok' | 'expired' | 'expiring_soon'"""
    expiry = str(user.get("expiry_date", "")).strip()
    if expiry.lower() in ("永久", "permanent", ""):
        return "ok"
    try:
        exp = datetime.strptime(expiry, "%Y-%m-%d").date()
        today = date.today()
        if exp < today:
            return "expired"
        if (exp - today).days <= 7:
            return "expiring_soon"
        return "ok"
    except Exception:
        return "ok"


def days_until_expiry(user: dict) -> int | None:
    expiry = str(user.get("expiry_date", "")).strip()
    if expiry.lower() in ("永久", "permanent", ""):
        return None
    try:
        exp = datetime.strptime(expiry, "%Y-%m-%d").date()
        return (exp - date.today()).days
    except Exception:
        return None


def authenticate(username: str, password: str) -> tuple[bool, str, dict | None]:
    """Returns (success, error_key, user_dict)"""
    user = find_user(username)
    if not user:
        return False, "login_wrong", None
    if not verify_password(password, str(user.get("password_hash", ""))):
        return False, "login_wrong", None
    if str(user.get("status", "active")).lower() == "disabled":
        return False, "login_disabled", None
    expiry_status = check_expiry(user)
    if expiry_status == "expired":
        return False, "login_expired", None
    return True, "", user


def get_ai_limit(role: str) -> int:
    limits = {"admin": 9999, "pro": 20, "free": 3}
    return limits.get(role, 3)


def can_use_ai(user: dict) -> bool:
    role = user.get("role", "free")
    limit = get_ai_limit(role)
    used = int(user.get("ai_calls_today", 0))
    reset_date = str(user.get("ai_calls_reset", ""))
    today_str = date.today().isoformat()
    if reset_date != today_str:
        return True
    return used < limit


def increment_ai_calls(username: str):
    """Increment AI call count in Google Sheets"""
    ws = _get_sheet()
    if not ws:
        return
    try:
        records = ws.get_all_records()
        headers = ws.row_values(1)
        ai_col = headers.index("ai_calls_today") + 1
        reset_col = headers.index("ai_calls_reset") + 1
        today_str = date.today().isoformat()
        for i, row in enumerate(records, start=2):
            if str(row.get("username", "")).lower() == username.lower():
                current_reset = str(row.get("ai_calls_reset", ""))
                if current_reset != today_str:
                    ws.update_cell(i, ai_col, 1)
                    ws.update_cell(i, reset_col, today_str)
                else:
                    current = int(row.get("ai_calls_today", 0))
                    ws.update_cell(i, ai_col, current + 1)
                load_all_users.clear()
                break
    except Exception:
        pass


def update_last_login(username: str):
    ws = _get_sheet()
    if not ws:
        return
    try:
        records = ws.get_all_records()
        headers = ws.row_values(1)
        if "last_login" not in headers:
            return
        col = headers.index("last_login") + 1
        tz = pytz.timezone("Europe/London")
        now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        for i, row in enumerate(records, start=2):
            if str(row.get("username", "")).lower() == username.lower():
                ws.update_cell(i, col, now)
                load_all_users.clear()
                break
    except Exception:
        pass


# ── Admin Functions ───────────────────────────────────────────────────────────

def admin_add_user(username, password, role, days, region, language):
    ws = _get_sheet()
    if not ws:
        return False, "Sheet connection failed"
    try:
        from datetime import timedelta
        hashed = hash_password(password)
        if days == 0:
            expiry = "永久"
        else:
            expiry = (date.today() + timedelta(days=days)).isoformat()
        ws.append_row([
            username, hashed, role, expiry, region, language,
            "dark", "active",
            date.today().isoformat(), "", 0, "", "", "", "{}", "{}"
        ])
        load_all_users.clear()
        return True, ""
    except Exception as e:
        return False, str(e)


def admin_update_expiry(username, new_expiry):
    ws = _get_sheet()
    if not ws:
        return False
    try:
        records = ws.get_all_records()
        headers = ws.row_values(1)
        col = headers.index("expiry_date") + 1
        for i, row in enumerate(records, start=2):
            if str(row.get("username", "")).lower() == username.lower():
                ws.update_cell(i, col, new_expiry)
                load_all_users.clear()
                return True
    except Exception:
        pass
    return False


def admin_update_role(username, new_role):
    ws = _get_sheet()
    if not ws:
        return False
    try:
        records = ws.get_all_records()
        headers = ws.row_values(1)
        col = headers.index("role") + 1
        for i, row in enumerate(records, start=2):
            if str(row.get("username", "")).lower() == username.lower():
                ws.update_cell(i, col, new_role)
                load_all_users.clear()
                return True
    except Exception:
        pass
    return False


def admin_toggle_status(username, status):
    ws = _get_sheet()
    if not ws:
        return False
    try:
        records = ws.get_all_records()
        headers = ws.row_values(1)
        col = headers.index("status") + 1
        for i, row in enumerate(records, start=2):
            if str(row.get("username", "")).lower() == username.lower():
                ws.update_cell(i, col, status)
                load_all_users.clear()
                return True
    except Exception:
        pass
    return False


def save_watchlist(username: str, tickers: str):
    ws = _get_sheet()
    if not ws:
        return
    try:
        records = ws.get_all_records()
        headers = ws.row_values(1)
        if "watchlist" not in headers:
            return
        col = headers.index("watchlist") + 1
        for i, row in enumerate(records, start=2):
            if str(row.get("username", "")).lower() == username.lower():
                ws.update_cell(i, col, tickers)
                load_all_users.clear()
                break
    except Exception:
        pass


def save_portfolios(username: str, portfolios: dict):
    ws = _get_sheet()
    if not ws:
        return
    try:
        records = ws.get_all_records()
        headers = ws.row_values(1)
        if "portfolios" not in headers:
            return
        col = headers.index("portfolios") + 1
        for i, row in enumerate(records, start=2):
            if str(row.get("username", "")).lower() == username.lower():
                ws.update_cell(i, col, json.dumps(portfolios, ensure_ascii=False))
                load_all_users.clear()
                break
    except Exception:
        pass


def save_price_alerts(username: str, alerts: dict):
    ws = _get_sheet()
    if not ws:
        return
    try:
        records = ws.get_all_records()
        headers = ws.row_values(1)
        if "price_alerts" not in headers:
            return
        col = headers.index("price_alerts") + 1
        for i, row in enumerate(records, start=2):
            if str(row.get("username", "")).lower() == username.lower():
                ws.update_cell(i, col, json.dumps(alerts, ensure_ascii=False))
                load_all_users.clear()
                break
    except Exception:
        pass
