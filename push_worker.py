"""
MarketIQ Push Worker
====================
Runs every hour via GitHub Actions.
For each active Pro/Admin user:
  1. Check if their scheduled push time matches current hour (UTC±timezone)
  2. Check if already pushed today
  3. If yes: compute 3-layer signals → AI summary → send Telegram
  4. Record push timestamp in Google Sheets

Environment variables (GitHub Secrets):
  GOOGLE_CREDENTIALS   — Service account JSON string
  SPREADSHEET_ID       — Google Sheets ID
  GROQ_API_KEY         — Groq API key
  TELEGRAM_BOT_TOKEN   — Telegram bot token
"""

import os
import json
import sys
import traceback
from datetime import datetime, date, timedelta

import pytz
import requests
import pandas as pd
import numpy as np
import gspread
from google.oauth2.service_account import Credentials

# ── Config ────────────────────────────────────────────────────────
GROQ_API_KEY       = os.environ.get("GROQ_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
SPREADSHEET_ID     = os.environ.get("SPREADSHEET_ID", "")
GOOGLE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS", "")

SECTOR_TICKERS = {
    "科技 XLK": "XLK", "通訊 XLC": "XLC", "銀行 XLF": "XLF",
    "芯片 SOXX": "SOXX", "非必需 XLY": "XLY", "能源 XLE": "XLE",
    "醫療 XLV": "XLV", "必需品 XLP": "XLP", "公用 XLU": "XLU",
}

TIMEZONE_MAP = {
    "HK": "Asia/Hong_Kong",
    "CN": "Asia/Shanghai",
    "UK": "Europe/London",
    "US": "America/New_York",
    "TW": "Asia/Taipei",
    "SG": "Asia/Singapore",
}


# ── Google Sheets ─────────────────────────────────────────────────
def get_sheet():
    try:
        creds_dict = json.loads(GOOGLE_CREDENTIALS)
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds  = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        return client.open_by_key(SPREADSHEET_ID).sheet1
    except Exception as e:
        print(f"[ERROR] Google Sheets connection failed: {e}")
        return None


def get_all_users(sheet) -> list[dict]:
    try:
        return sheet.get_all_records()
    except Exception as e:
        print(f"[ERROR] Failed to read users: {e}")
        return []


def update_cell_by_col(sheet, row_idx: int, headers: list, col_name: str, value: str):
    try:
        if col_name not in headers:
            print(f"[WARN] Column '{col_name}' not found in sheet")
            return
        col_idx = headers.index(col_name) + 1
        sheet.update_cell(row_idx, col_idx, value)
    except Exception as e:
        print(f"[WARN] Failed to update {col_name}: {e}")


# ── Time check ───────────────────────────────────────────────────
def should_push_now(user: dict) -> bool:
    """
    Check if the current UTC hour matches this user's scheduled push hour
    in their local timezone.
    """
    push_time_str = str(user.get("push_time", "")).strip()
    if not push_time_str or push_time_str == "off":
        return False

    region   = str(user.get("region", "UK")).strip()
    tz_name  = TIMEZONE_MAP.get(region, "Europe/London")
    tz       = pytz.timezone(tz_name)
    now_local = datetime.now(pytz.utc).astimezone(tz)

    try:
        # push_time stored as "HH:MM" e.g. "08:00"
        push_hour = int(push_time_str.split(":")[0])
    except Exception:
        return False

    return now_local.hour == push_hour


def already_pushed_today(user: dict) -> bool:
    last_push = str(user.get("last_push_date", "")).strip()
    return last_push == date.today().isoformat()


# ── Market Analysis ──────────────────────────────────────────────
def fetch_safe(sym: str, period: str = "3mo") -> pd.DataFrame:
    import yfinance as yf
    try:
        df = yf.download(sym, period=period, interval="1d",
                         progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.dropna()
    except Exception:
        return pd.DataFrame()


def compute_env_score() -> dict:
    """Layer 1: Market environment score"""
    try:
        vix_df = fetch_safe("^VIX", "5d")
        spy_df = fetch_safe("^GSPC", "3mo")

        vix_val = float(vix_df["Close"].iloc[-1]) if not vix_df.empty else 20

        if vix_val < 15:   vix_score = 90
        elif vix_val < 18: vix_score = 75
        elif vix_val < 22: vix_score = 55
        elif vix_val < 28: vix_score = 30
        elif vix_val < 35: vix_score = 15
        else:              vix_score = 5

        trend_score = 50
        spy_price = None
        if not spy_df.empty:
            close = spy_df["Close"].dropna()
            if isinstance(close, pd.DataFrame): close = close.iloc[:, 0]
            spy_price = float(close.iloc[-1])
            ema20 = float(close.ewm(span=20).mean().iloc[-1])
            ema50 = float(close.ewm(span=50).mean().iloc[-1]) if len(close) >= 50 else ema20
            ret_1m = (spy_price / float(close.iloc[max(0, len(close)-22)]) - 1) * 100
            if spy_price > ema20 > ema50 and ret_1m > 2:  trend_score = 90
            elif spy_price > ema20 > ema50:                trend_score = 75
            elif spy_price > ema20:                        trend_score = 55
            elif spy_price > ema50:                        trend_score = 35
            else:                                          trend_score = 15

        # Breadth
        above = 0
        for sym in list(SECTOR_TICKERS.values())[:6]:
            try:
                df_s = fetch_safe(sym, "2mo")
                if df_s.empty: continue
                c = df_s["Close"].dropna()
                if isinstance(c, pd.DataFrame): c = c.iloc[:, 0]
                if len(c) >= 20 and float(c.iloc[-1]) > float(c.ewm(span=20).mean().iloc[-1]):
                    above += 1
            except Exception:
                pass

        breadth_score = int(above / 6 * 100)
        env_score = int(vix_score * 0.40 + trend_score * 0.40 + breadth_score * 0.20)

        if   env_score >= 70: label = "Risk-On 進取 🟢";  color = "🟢"
        elif env_score >= 45: label = "Neutral 中性 🟡";  color = "🟡"
        else:                 label = "Risk-Off 防守 🔴"; color = "🔴"

        return {
            "score": env_score, "label": label, "color": color,
            "vix": round(vix_val, 1), "breadth_above": above,
            "trend_score": trend_score,
        }
    except Exception as e:
        print(f"[WARN] env score failed: {e}")
        return {"score": 50, "label": "Neutral 中性 🟡", "color": "🟡",
                "vix": 20, "breadth_above": 0, "trend_score": 50}


def compute_sector_top(n: int = 3) -> list[tuple]:
    """Layer 2: Top N sectors by 1-month return"""
    results = []
    for name, sym in SECTOR_TICKERS.items():
        try:
            df_s = fetch_safe(sym, "2mo")
            if df_s.empty or len(df_s) < 22: continue
            c = df_s["Close"].dropna()
            if isinstance(c, pd.DataFrame): c = c.iloc[:, 0]
            ret = (float(c.iloc[-1]) / float(c.iloc[max(0, len(c)-22)]) - 1) * 100
            results.append((name.split()[0], round(ret, 1)))
        except Exception:
            pass
    results.sort(key=lambda x: x[1], reverse=True)
    return results[:n]


def compute_stock_signal(sym: str) -> dict | None:
    """Layer 3: Individual stock signal"""
    try:
        df = fetch_safe(sym, "6mo")
        if df.empty or len(df) < 30:
            return None
        close = df["Close"].dropna()
        hi    = df["High"].dropna()
        lo    = df["Low"].dropna()
        if isinstance(close, pd.DataFrame): close = close.iloc[:, 0]
        if isinstance(hi,    pd.DataFrame): hi    = hi.iloc[:, 0]
        if isinstance(lo,    pd.DataFrame): lo    = lo.iloc[:, 0]

        price = float(close.iloc[-1])
        ema20 = float(close.ewm(span=20).mean().iloc[-1])
        ema50 = float(close.ewm(span=50).mean().iloc[-1]) if len(close) >= 50 else ema20

        # MACD
        macd  = close.ewm(span=12).mean() - close.ewm(span=26).mean()
        sig   = macd.ewm(span=9).mean()
        hist  = float((macd - sig).iloc[-1])
        hist_prev = float((macd - sig).iloc[-2])

        # RSI
        d   = close.diff()
        g   = d.where(d > 0, 0).ewm(alpha=1/14, adjust=False).mean()
        l   = (-d.where(d < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
        rsi = float(100 - 100 / (1 + g.iloc[-1] / max(float(l.iloc[-1]), 1e-9)))

        # ATR
        atr = float((hi - lo).ewm(alpha=1/14, adjust=False).mean().iloc[-1])

        # Score
        score = 0
        if price > ema20 > ema50: score += 30
        elif price > ema20:        score += 15
        if hist > 0 and hist_prev <= 0: score += 20
        elif hist > 0:                  score += 12
        if 45 <= rsi <= 65:  score += 20
        elif 35 <= rsi < 45: score += 10
        elif rsi > 70:       score += 5
        score = min(100, max(0, score))

        if   score >= 68: action = "LONG 做多 🟢"
        elif score >= 45: action = "WATCH 觀望 🟡"
        else:             action = "AVOID 迴避 🔴"

        stop   = round(price - atr * 2, 2)
        tgt1   = round(price + atr * 3, 2)
        rr     = round((tgt1 - price) / max(price - stop, 0.01), 1)

        return {
            "ticker": sym,
            "price":  round(price, 2),
            "score":  score,
            "action": action,
            "stop":   stop,
            "tgt1":   tgt1,
            "rr":     rr,
            "rsi":    round(rsi, 1),
            "ema20":  round(ema20, 2),
        }
    except Exception as e:
        print(f"[WARN] Stock signal failed for {sym}: {e}")
        return None


def groq_summary(env: dict, top_sectors: list, signals: list, lang: str = "zh-hant") -> str:
    """Generate one-sentence AI summary via Groq"""
    if not GROQ_API_KEY:
        return ""
    try:
        lang_inst = {
            "zh-hant": "請用繁體中文回答，一句話。",
            "zh-hans": "请用简体中文回答，一句话。",
            "en":       "Please respond in English, one sentence.",
        }.get(lang, "請用繁體中文回答，一句話。")

        top_str = "、".join(f"{n}({v:+.1f}%)" for n, v in top_sectors) if top_sectors else "無"
        long_stocks = [s for s in signals if "LONG" in s["action"]]
        watch_stocks = [s for s in signals if "WATCH" in s["action"]]

        sig_str = ""
        for s in signals[:5]:
            sig_str += f"{s['ticker']}({s['action'].split()[0]} {s['score']}分) "

        prompt = f"""
市場環境：{env['label']} VIX {env['vix']} 評分{env['score']}/100
強勢板塊：{top_str}
個股信號：{sig_str}
做多機會：{len(long_stocks)}隻  觀望：{len(watch_stocks)}隻

{lang_inst}根據以上數據，給出今日最重要的一句操作建議（含具體方向）。
"""
        r = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}",
                     "Content-Type": "application/json"},
            json={
                "model":       "llama-3.3-70b-versatile",
                "max_tokens":  120,
                "temperature": 0.3,
                "messages": [
                    {"role": "system", "content": f"你是一位精簡的市場策略師。{lang_inst}"},
                    {"role": "user",   "content": prompt},
                ],
            },
            timeout=20,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"[WARN] Groq failed: {e}")
        return ""


def format_telegram_message(
    username: str,
    env: dict,
    top_sectors: list,
    signals: list,
    ai_summary: str,
    lang: str = "zh-hant",
) -> str:
    """Format the Telegram push message"""
    now_str = datetime.now(pytz.timezone("Europe/London")).strftime("%Y-%m-%d %H:%M")

    header = {
        "zh-hant": f"📊 *MarketIQ 今日行動指令*\n👤 {username} · {now_str} London",
        "zh-hans": f"📊 *MarketIQ 今日行动指令*\n👤 {username} · {now_str} London",
        "en":      f"📊 *MarketIQ Daily Signal*\n👤 {username} · {now_str} London",
    }.get(lang, f"📊 *MarketIQ 今日行動指令*\n👤 {username} · {now_str} London")

    # Layer 1
    env_section = (
        f"\n\n*第一層 · 大環境*\n"
        f"{env['color']} {env['label']}  評分 {env['score']}/100\n"
        f"VIX {env['vix']}  板塊寬度 {env['breadth_above']}/6"
    )

    # Layer 2
    sector_lines = "  ".join(f"{n} {v:+.1f}%" for n, v in top_sectors)
    sector_section = f"\n\n*第二層 · 強勢板塊*\n🔥 {sector_lines}"

    # Layer 3
    sig_section = "\n\n*第三層 · 個股信號*\n"
    for s in signals:
        emoji = "🟢" if "LONG" in s["action"] else "🟡" if "WATCH" in s["action"] else "🔴"
        action_short = s["action"].split()[0]
        line = (
            f"{emoji} *{s['ticker']}*  ${s['price']}  "
            f"{action_short} {s['score']}分\n"
        )
        if "LONG" in s["action"]:
            line += (
                f"   止損 ${s['stop']}  目標 ${s['tgt1']}  "
                f"盈虧比 {s['rr']}x\n"
            )
        sig_section += line

    # AI summary
    ai_section = f"\n💡 *AI 建議*\n{ai_summary}" if ai_summary else ""

    # Footer
    footer = "\n\n_數據僅供參考，不構成投資建議 · MarketIQ_"

    return header + env_section + sector_section + sig_section + ai_section + footer


def send_telegram(chat_id: str, text: str) -> bool:
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id":    chat_id,
                "text":       text,
                "parse_mode": "Markdown",
            },
            timeout=15,
        )
        return r.status_code == 200
    except Exception as e:
        print(f"[WARN] Telegram send failed: {e}")
        return False


def save_signal_history(sheet, row_idx: int, headers: list,
                        signals: list, env: dict) -> None:
    """Append today's signal to signal_history column (JSON array, max 30 days)"""
    try:
        if "signal_history" not in headers:
            return
        col_idx   = headers.index("signal_history") + 1
        existing  = sheet.cell(row_idx, col_idx).value or "[]"
        try:
            history = json.loads(existing)
        except Exception:
            history = []

        today_entry = {
            "date":    date.today().isoformat(),
            "env":     env["score"],
            "signals": [
                {"ticker": s["ticker"], "action": s["action"].split()[0],
                 "score": s["score"], "price": s["price"]}
                for s in signals
            ],
        }
        history.append(today_entry)
        # Keep last 30 days only
        history = history[-30:]
        sheet.update_cell(row_idx, col_idx, json.dumps(history, ensure_ascii=False))
    except Exception as e:
        print(f"[WARN] Failed to save signal history: {e}")


# ── Main ─────────────────────────────────────────────────────────
def main():
    print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC] MarketIQ Push Worker started")

    # Validate secrets
    missing = []
    if not GOOGLE_CREDENTIALS: missing.append("GOOGLE_CREDENTIALS")
    if not SPREADSHEET_ID:     missing.append("SPREADSHEET_ID")
    if not TELEGRAM_BOT_TOKEN: missing.append("TELEGRAM_BOT_TOKEN")
    if missing:
        print(f"[ERROR] Missing secrets: {', '.join(missing)}")
        sys.exit(1)

    # Connect to Sheets
    sheet = get_sheet()
    if sheet is None:
        sys.exit(1)

    users   = get_all_users(sheet)
    headers = sheet.row_values(1)
    print(f"[INFO] Loaded {len(users)} users from Sheets")

    # Pre-compute market data once (shared across all users)
    print("[INFO] Computing market environment...")
    env = compute_env_score()
    print(f"[INFO] Env score: {env['score']} | {env['label']} | VIX {env['vix']}")

    print("[INFO] Computing sector rotation...")
    top_sectors = compute_sector_top(3)
    print(f"[INFO] Top sectors: {top_sectors}")

    pushed_count = 0
    skipped_count = 0

    for i, user in enumerate(users, start=2):  # row 2 onwards
        uname  = str(user.get("username", "")).strip()
        role   = str(user.get("role", "free")).strip().lower()
        status = str(user.get("status", "active")).strip().lower()
        tg_id  = str(user.get("telegram_chat_id", "")).strip()
        lang   = str(user.get("language", "zh-hant")).strip()
        wl_raw = str(user.get("watchlist", "")).strip()

        # Skip: free users, disabled, no Telegram
        if role not in ("pro", "admin"):
            continue
        if status != "active":
            continue
        if not tg_id:
            continue
        if not should_push_now(user):
            continue
        if already_pushed_today(user):
            print(f"[SKIP] {uname} — already pushed today")
            skipped_count += 1
            continue

        print(f"[PUSH] Processing {uname} (lang={lang}, region={user.get('region','UK')})")

        # Parse watchlist
        tickers = [s.strip().upper() for s in wl_raw.split(",") if s.strip()][:8]
        if not tickers:
            tickers = ["TSLA", "AAPL", "NVDA", "AMZN", "META"]

        # Compute individual stock signals
        signals = []
        for tk in tickers:
            sig = compute_stock_signal(tk)
            if sig:
                signals.append(sig)
        # Sort: LONG > WATCH > AVOID, then by score
        order = {"LONG": 0, "WATCH": 1, "AVOID": 2}
        signals.sort(key=lambda x: (order.get(x["action"].split()[0], 3), -x["score"]))

        # AI one-sentence summary
        ai_sum = groq_summary(env, top_sectors, signals, lang)
        print(f"[INFO] AI summary: {ai_sum[:60]}..." if ai_sum else "[INFO] No AI summary")

        # Format and send
        msg = format_telegram_message(uname, env, top_sectors, signals, ai_sum, lang)
        ok  = send_telegram(tg_id, msg)

        if ok:
            print(f"[OK] Pushed to {uname} (chat_id: {tg_id[:6]}...)")
            pushed_count += 1
            # Record push date
            update_cell_by_col(sheet, i, headers, "last_push_date",
                                date.today().isoformat())
            # Save to signal history
            save_signal_history(sheet, i, headers, signals, env)
        else:
            print(f"[FAIL] Telegram push failed for {uname}")

    print(f"\n[DONE] Pushed: {pushed_count} | Skipped: {skipped_count}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[FATAL] {e}")
        traceback.print_exc()
        sys.exit(1)
