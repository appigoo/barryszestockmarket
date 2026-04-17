# utils/ai.py
# ─── Groq AI + Telegram ───────────────────────────────────────────────────────

import streamlit as st
import requests
import json

GROQ_MODELS = {
    "pro":   "llama-3.3-70b-versatile",
    "free":  "llama-3.1-8b-instant",
    "admin": "llama-3.3-70b-versatile",
}

LANG_PROMPTS = {
    "zh-hant": "請用繁體中文回答。",
    "zh-hans": "请用简体中文回答。",
    "en":       "Please respond in English.",
}


def call_groq(prompt: str, role: str = "free", lang: str = "zh-hant",
              system: str = "") -> str:
    try:
        api_key = st.secrets["groq"]["api_key"]
    except Exception:
        return "⚠️ Groq API Key 未設定"

    model = GROQ_MODELS.get(role, GROQ_MODELS["free"])
    lang_inst = LANG_PROMPTS.get(lang, LANG_PROMPTS["zh-hant"])
    sys_msg = system or f"你是一位專業的股票市場分析師。{lang_inst}"

    payload = {
        "model": model,
        "max_tokens": 1024,
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user",   "content": prompt},
        ],
        "temperature": 0.3,
    }

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}",
                     "Content-Type": "application/json"},
            json=payload, timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except requests.exceptions.Timeout:
        return "⚠️ AI 分析超時，請稍後再試"
    except Exception as e:
        return f"⚠️ AI 分析失敗: {str(e)[:100]}"


def build_market_analysis_prompt(regime: dict, sector_data: dict,
                                  watchlist_data: dict, lang: str) -> str:
    regime_name = regime.get("regime", "neutral")
    vix = regime.get("vix", 20)
    mom = regime.get("momentum", 50)

    # Top sectors
    sectors_str = ""
    for name, d in sector_data.items():
        if d and d.get("1m") is not None:
            sectors_str += f"  {name}: {d['1m']:+.1f}%\n"

    # Watchlist
    watch_str = ""
    for name, d in watchlist_data.items():
        if d:
            watch_str += f"  {name}: ${d['price']:.2f}, 1月: {d.get('1m', 0) or 0:+.1f}%\n"

    if lang == "en":
        return f"""
Analyze the current market and provide trading recommendations.

MARKET REGIME: {regime_name} (Score: {regime.get('overall', 50)}/100)
VIX: {vix}
Momentum Score: {mom}/100

SECTOR PERFORMANCE (1-month):
{sectors_str}

WATCHLIST:
{watch_str}

Provide:
1. Market environment assessment (2-3 sentences)
2. Top 3 opportunities from the watchlist with entry rationale
3. Key risks to watch
4. Specific action: aggressive / neutral / defensive
Keep it concise and actionable.
"""
    else:
        return f"""
請分析當前市場環境並提供交易建議。

市場環境：{regime_name}（評分：{regime.get('overall', 50)}/100）
VIX：{vix}
動能評分：{mom}/100

板塊1月表現：
{sectors_str}

自選股票：
{watch_str}

請提供：
1. 市場環境評估（2-3句）
2. 自選股票中最值得關注的3個機會及入場理由
3. 主要風險提示
4. 具體操作方向：進取 / 中性 / 防守
請簡潔務實，有具體可操作的建議。
"""


def build_briefing_prompt(regime: dict, top_sectors: list,
                           watchlist: list, lang: str, region: str) -> str:
    if lang == "en":
        return f"""
Generate a concise daily market briefing for a {region} investor.

Market Regime: {regime.get('regime')} | VIX: {regime.get('vix')}
Top sectors: {', '.join(top_sectors[:3])}
Watchlist focus: {', '.join(watchlist[:5])}

Format:
📊 MARKET OVERVIEW (2 sentences)
🔥 KEY OPPORTUNITIES (bullet points, max 3)
⚠️ RISKS TO WATCH (1-2 points)
💡 TODAY'S ACTION (one clear recommendation)
"""
    else:
        return f"""
為{region}地區投資者生成簡潔的每日市場簡報。

市場狀態：{regime.get('regime')} | VIX：{regime.get('vix')}
強勢板塊：{', '.join(top_sectors[:3])}
重點關注：{', '.join(watchlist[:5])}

格式：
📊 市場概況（2句）
🔥 重點機會（要點，最多3個）
⚠️ 風險提示（1-2點）
💡 今日操作建議（一句明確建議）
"""


def build_coach_prompt(trades: list, lang: str) -> str:
    if not trades:
        return ""
    summary = f"共{len(trades)}筆交易" if lang != "en" else f"{len(trades)} trades"
    wins = sum(1 for t in trades if t.get("pnl", 0) > 0)
    wr = wins / len(trades) * 100 if trades else 0
    avg_pnl = sum(t.get("pnl", 0) for t in trades) / len(trades) if trades else 0

    if lang == "en":
        return f"""
Analyze these trading statistics and identify behavioral patterns:
- Total trades: {len(trades)}
- Win rate: {wr:.1f}%
- Average P&L: ${avg_pnl:.2f}

Provide:
1. Key behavioral weakness (1-2 sentences)
2. Specific improvement tip
3. One sentence encouragement
"""
    else:
        return f"""
分析以下交易數據，找出行為模式：
- 總交易：{len(trades)}筆
- 勝率：{wr:.1f}%
- 平均盈虧：${avg_pnl:.2f}

請提供：
1. 主要行為弱點（1-2句）
2. 具體改善建議
3. 一句鼓勵
"""


# ── Telegram ──────────────────────────────────────────────────────────────────
def send_telegram(chat_id: str, text: str) -> bool:
    try:
        token = st.secrets["telegram"]["bot_token"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        resp = requests.post(url, json={
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown",
        }, timeout=10)
        return resp.status_code == 200
    except Exception:
        return False


def format_briefing_tg(briefing: str, username: str) -> str:
    return f"*MarketIQ 每日簡報*\n👤 {username}\n\n{briefing}\n\n_僅供參考，不構成投資建議_"


def format_signal_tg(ticker: str, score: int, label: str, price: float) -> str:
    emoji = "🟢" if label == "buy" else "🟡" if label == "watch" else "🔴"
    return f"{emoji} *{ticker}* 信號更新\n價格：${price:.2f}\n評分：{score}/100\n方向：{label}\n\n_MarketIQ_"
