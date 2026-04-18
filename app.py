"""
═══════════════════════════════════════════════════════════════════
  MarketIQ — Global Market Intelligence Dashboard
  Version: v1.0 (Core + Tab 1 Global Market Monitor)
  Author: Tesla / Built with Claude (Anthropic)
═══════════════════════════════════════════════════════════════════
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import bcrypt
import gspread
from google.oauth2.service_account import Credentials
import json
import time

# ═══════════════════════════════════════════════════════════════════
#   PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="MarketIQ Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════
#   I18N — Three Languages
# ═══════════════════════════════════════════════════════════════════
TRANSLATIONS = {
    "zh-hant": {
        "app_title": "環球市場監控",
        "app_sub": "MarketIQ INTELLIGENCE DASHBOARD",
        "login_title": "登入 MarketIQ",
        "login_sub": "環球市場智能儀表板",
        "username": "用戶名",
        "password": "密碼",
        "login_btn": "登入",
        "login_fail": "用戶名或密碼錯誤",
        "login_disabled": "帳號已停用，請聯絡管理員",
        "login_expired": "帳號已到期，請聯絡管理員續期",
        "login_locked": "登入失敗次數過多，帳號已暫時鎖定 30 分鐘",
        "logout": "登出",
        "menu_main": "主選單",
        "menu_system": "系統",
        "nav_global": "環球市場",
        "nav_watchlist": "自選股票",
        "nav_ai": "AI 交易助手",
        "nav_portfolio": "組合管理",
        "nav_journal": "交易日誌",
        "nav_learn": "學習中心",
        "nav_settings": "個人設定",
        "nav_admin": "管理控制台",
        "us_open": "美股開市中",
        "us_closed": "美股休市",
        "hk_open": "港股開市中",
        "hk_closed": "港股休市",
        "cn_open": "A股開市中",
        "cn_closed": "A股休市",
        "uk_open": "英股開市中",
        "uk_closed": "英股休市",
        "theme_dark": "☽ 深色",
        "theme_light": "☀ 淺色",
        "theme_eye": "🍃 護眼",
        "eye_banner": "護眼模式已啟動 — 暖色調 + 低對比度，適合長時間看盤",
        "last_update": "最後更新",
        "data_source": "Yahoo Finance · 5分鐘自動刷新",
        "sp500": "標普 500",
        "nasdaq": "納斯達克",
        "vix": "VIX 恐慌指數",
        "gold": "黃金 USD/oz",
        "today": "今日",
        "low_vol": "低波幅",
        "flat": "橫盤",
        "sector_compare": "板塊表現對比",
        "sector_sub": "11個主要 SPDR 板塊",
        "sector_heatmap": "板塊強弱熱力圖",
        "p_1d": "1天",
        "p_1m": "1月",
        "p_ytd": "YTD",
        "watchlist_signals": "自選股票信號燈",
        "entry_score": "入場評分 0–100",
        "buy": "買入",
        "watch": "觀望",
        "avoid": "迴避",
        "market_regime": "市場環境判斷",
        "current_state": "當前狀態",
        "risk_on": "🟢 Risk-On 趨勢市",
        "risk_off": "🔴 Risk-Off 防守市",
        "neutral": "🟡 Neutral 震盪市",
        "extreme_fear": "⚫ 極端恐慌",
        "momentum": "動能 Momentum",
        "breadth": "市場寬度 Breadth",
        "sentiment": "情緒指標 Sentiment",
        "volatility": "波幅水平 Volatility",
        "ai_advice": "AI 建議",
        "ai_advice_text": "大環境偏多，科技板塊強勢，可積極佈局強勢股，建議止損設 ATR × 2",
        "vix_term": "VIX 期限結構",
        "vix_spot": "VIX 現貨",
        "contango_text": "正向期限結構 Contango — 市場預期短期波幅平靜，中期略升",
        "backwardation_text": "逆向期限結構 Backwardation — 市場短期恐慌，中期回穩",
        "loading": "載入市場數據中...",
        "data_error": "數據加載失敗",
        "refresh": "🔄 刷新",
        "expiry_warn": "您的 Pro 訂閱將於 {} 天後到期",
        "ai_quota": "今日 AI 分析",
        "lang_zh_hant": "繁體中文",
        "lang_zh_hans": "簡體中文",
        "lang_en": "English",
    },
    "zh-hans": {
        "app_title": "环球市场监控",
        "app_sub": "MarketIQ INTELLIGENCE DASHBOARD",
        "login_title": "登入 MarketIQ",
        "login_sub": "环球市场智能仪表板",
        "username": "用户名",
        "password": "密码",
        "login_btn": "登入",
        "login_fail": "用户名或密码错误",
        "login_disabled": "账号已停用，请联系管理员",
        "login_expired": "账号已到期，请联系管理员续期",
        "login_locked": "登入失败次数过多，账号已暂时锁定 30 分钟",
        "logout": "登出",
        "menu_main": "主选单",
        "menu_system": "系统",
        "nav_global": "环球市场",
        "nav_watchlist": "自选股票",
        "nav_ai": "AI 交易助手",
        "nav_portfolio": "组合管理",
        "nav_journal": "交易日志",
        "nav_learn": "学习中心",
        "nav_settings": "个人设定",
        "nav_admin": "管理控制台",
        "us_open": "美股开市中",
        "us_closed": "美股休市",
        "hk_open": "港股开市中",
        "hk_closed": "港股休市",
        "cn_open": "A股开市中",
        "cn_closed": "A股休市",
        "uk_open": "英股开市中",
        "uk_closed": "英股休市",
        "theme_dark": "☽ 深色",
        "theme_light": "☀ 浅色",
        "theme_eye": "🍃 护眼",
        "eye_banner": "护眼模式已启动 — 暖色调 + 低对比度，适合长时间看盘",
        "last_update": "最后更新",
        "data_source": "Yahoo Finance · 5分钟自动刷新",
        "sp500": "标普 500",
        "nasdaq": "纳斯达克",
        "vix": "VIX 恐慌指数",
        "gold": "黄金 USD/oz",
        "today": "今日",
        "low_vol": "低波幅",
        "flat": "横盘",
        "sector_compare": "板块表现对比",
        "sector_sub": "11个主要 SPDR 板块",
        "sector_heatmap": "板块强弱热力图",
        "p_1d": "1天",
        "p_1m": "1月",
        "p_ytd": "YTD",
        "watchlist_signals": "自选股票信号灯",
        "entry_score": "入场评分 0–100",
        "buy": "买入",
        "watch": "观望",
        "avoid": "回避",
        "market_regime": "市场环境判断",
        "current_state": "当前状态",
        "risk_on": "🟢 Risk-On 趋势市",
        "risk_off": "🔴 Risk-Off 防守市",
        "neutral": "🟡 Neutral 震荡市",
        "extreme_fear": "⚫ 极端恐慌",
        "momentum": "动能 Momentum",
        "breadth": "市场宽度 Breadth",
        "sentiment": "情绪指标 Sentiment",
        "volatility": "波幅水平 Volatility",
        "ai_advice": "AI 建议",
        "ai_advice_text": "大环境偏多，科技板块强势，可积极布局强势股，建议止损设 ATR × 2",
        "vix_term": "VIX 期限结构",
        "vix_spot": "VIX 现货",
        "contango_text": "正向期限结构 Contango — 市场预期短期波幅平静，中期略升",
        "backwardation_text": "逆向期限结构 Backwardation — 市场短期恐慌，中期回稳",
        "loading": "载入市场数据中...",
        "data_error": "数据加载失败",
        "refresh": "🔄 刷新",
        "expiry_warn": "您的 Pro 订阅将于 {} 天后到期",
        "ai_quota": "今日 AI 分析",
        "lang_zh_hant": "繁体中文",
        "lang_zh_hans": "简体中文",
        "lang_en": "English",
    },
    "en": {
        "app_title": "Global Market Monitor",
        "app_sub": "MarketIQ INTELLIGENCE DASHBOARD",
        "login_title": "Login to MarketIQ",
        "login_sub": "Global Market Intelligence Dashboard",
        "username": "Username",
        "password": "Password",
        "login_btn": "Sign In",
        "login_fail": "Invalid username or password",
        "login_disabled": "Account disabled. Please contact admin.",
        "login_expired": "Account expired. Please contact admin to renew.",
        "login_locked": "Too many failed attempts. Account locked for 30 minutes.",
        "logout": "Logout",
        "menu_main": "Main",
        "menu_system": "System",
        "nav_global": "Global Market",
        "nav_watchlist": "Watchlist",
        "nav_ai": "AI Assistant",
        "nav_portfolio": "Portfolio",
        "nav_journal": "Trade Journal",
        "nav_learn": "Learning Hub",
        "nav_settings": "Settings",
        "nav_admin": "Admin Console",
        "us_open": "US Market Open",
        "us_closed": "US Market Closed",
        "hk_open": "HK Market Open",
        "hk_closed": "HK Market Closed",
        "cn_open": "CN Market Open",
        "cn_closed": "CN Market Closed",
        "uk_open": "UK Market Open",
        "uk_closed": "UK Market Closed",
        "theme_dark": "☽ Dark",
        "theme_light": "☀ Light",
        "theme_eye": "🍃 Eye-Care",
        "eye_banner": "Eye-care mode active — warm tones + low contrast, ideal for long sessions",
        "last_update": "Updated",
        "data_source": "Yahoo Finance · auto-refresh every 5 min",
        "sp500": "S&P 500",
        "nasdaq": "NASDAQ",
        "vix": "VIX Fear Index",
        "gold": "Gold USD/oz",
        "today": "today",
        "low_vol": "low vol",
        "flat": "flat",
        "sector_compare": "Sector Performance",
        "sector_sub": "11 main SPDR sectors",
        "sector_heatmap": "Sector Strength Heatmap",
        "p_1d": "1D",
        "p_1m": "1M",
        "p_ytd": "YTD",
        "watchlist_signals": "Watchlist Signals",
        "entry_score": "Entry Score 0–100",
        "buy": "Buy",
        "watch": "Watch",
        "avoid": "Avoid",
        "market_regime": "Market Regime",
        "current_state": "Current State",
        "risk_on": "🟢 Risk-On Trending",
        "risk_off": "🔴 Risk-Off Defensive",
        "neutral": "🟡 Neutral Range",
        "extreme_fear": "⚫ Extreme Fear",
        "momentum": "Momentum",
        "breadth": "Breadth",
        "sentiment": "Sentiment",
        "volatility": "Volatility",
        "ai_advice": "AI Recommendation",
        "ai_advice_text": "Bullish environment, tech sector strong. Position aggressively in leaders. Stop-loss = ATR × 2",
        "vix_term": "VIX Term Structure",
        "vix_spot": "VIX Spot",
        "contango_text": "Contango — market expects calm near-term, slight rise mid-term",
        "backwardation_text": "Backwardation — short-term panic, mid-term stable",
        "loading": "Loading market data...",
        "data_error": "Data load failed",
        "refresh": "🔄 Refresh",
        "expiry_warn": "Your Pro subscription expires in {} days",
        "ai_quota": "AI analysis today",
        "lang_zh_hant": "Traditional Chinese",
        "lang_zh_hans": "Simplified Chinese",
        "lang_en": "English",
    },
}

def t(key: str) -> str:
    """Translate key based on current language"""
    lang = st.session_state.get("lang", "zh-hant")
    return TRANSLATIONS.get(lang, TRANSLATIONS["zh-hant"]).get(key, key)


# ═══════════════════════════════════════════════════════════════════
#   THEME SYSTEM
# ═══════════════════════════════════════════════════════════════════
THEMES = {
    "dark": {
        "bg": "#141418", "bg2": "#1a1a20",
        "card": "#1e1e2a", "card2": "#252535",
        "nav": "#111118",
        "nav_text": "#9090b0", "nav_text_active": "#00c98a",
        "nav_active_bg": "rgba(0,201,138,0.13)",
        "nav_border": "rgba(255,255,255,0.07)",
        "green": "#00c98a", "red": "#f05555",
        "blue": "#4d9fff", "orange": "#f0a030",
        "purple": "#a888f8",
        "text1": "#e8e8f0", "text2": "#a8a8c0", "text3": "#707088",
        "border": "rgba(255,255,255,0.09)",
        "border2": "rgba(255,255,255,0.05)",
        "chart_grid": "rgba(255,255,255,0.05)",
        "chart_tick": "#707088",
    },
    "light": {
        "bg": "#f5f4ef", "bg2": "#eeede8",
        "card": "#ffffff", "card2": "#f8f7f2",
        "nav": "#1e2140",
        "nav_text": "#9098b8", "nav_text_active": "#00d090",
        "nav_active_bg": "rgba(0,208,144,0.15)",
        "nav_border": "rgba(255,255,255,0.10)",
        "green": "#0a8f5c", "red": "#cc3333",
        "blue": "#1a6fd4", "orange": "#c07010",
        "purple": "#7050c0",
        "text1": "#1a1d2e", "text2": "#4a5070", "text3": "#8890aa",
        "border": "rgba(0,0,0,0.09)",
        "border2": "rgba(0,0,0,0.05)",
        "chart_grid": "rgba(0,0,0,0.05)",
        "chart_tick": "#8890aa",
    },
    "eye": {
        "bg": "#18180f", "bg2": "#1e1e14",
        "card": "#222218", "card2": "#282820",
        "nav": "#141410",
        "nav_text": "#909070", "nav_text_active": "#5ab478",
        "nav_active_bg": "rgba(90,180,120,0.15)",
        "nav_border": "rgba(255,255,240,0.07)",
        "green": "#5ab478", "red": "#c85050",
        "blue": "#5080c8", "orange": "#c89040",
        "purple": "#9878d8",
        "text1": "#d4d0b8", "text2": "#a0a080", "text3": "#707058",
        "border": "rgba(255,255,200,0.08)",
        "border2": "rgba(255,255,200,0.04)",
        "chart_grid": "rgba(255,255,200,0.05)",
        "chart_tick": "#707058",
    },
}


def get_theme():
    """Get current theme dict"""
    return THEMES.get(st.session_state.get("theme", "dark"), THEMES["dark"])


def get_font_size():
    """Get current base font size in px"""
    sizes = {"sm": 13, "md": 14, "lg": 16}
    return sizes.get(st.session_state.get("font_size", "md"), 14)


def inject_css():
    """Inject all CSS based on current theme + font size + sidebar state"""
    th = get_theme()
    fs = get_font_size()
    collapsed = st.session_state.get("sb_collapsed", False)
    sb_w   = "60px"  if collapsed else "240px"
    sb_pad = "8px"   if collapsed else "20px 16px"
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+HK:wght@300;400;500;700&family=Inter:wght@400;500;600;700;800;900&display=swap');

    /* Hide Streamlit chrome */
    #MainMenu, footer, header {{ visibility: hidden; }}
    .stDeployButton {{ display: none; }}

    /* ── Fix expander _arrow overlap bug (all Streamlit versions) ── */
    .streamlit-expanderHeader {{
        font-size: 14px !important;
        font-weight: 600 !important;
        color: {th['text1']} !important;
        background: {th['card2']} !important;
        border-radius: 9px !important;
        padding: 10px 14px !important;
        border: 1px solid {th['border']} !important;
    }}
    .streamlit-expanderHeader p {{
        font-size: 14px !important;
        font-weight: 600 !important;
        color: {th['text1']} !important;
        margin: 0 !important;
    }}
    .streamlit-expanderContent {{
        background: {th['card']} !important;
        border: 1px solid {th['border']} !important;
        border-top: none !important;
        border-radius: 0 0 9px 9px !important;
        padding: 14px !important;
    }}
    /* Hide _arrow text in newer Streamlit */
    details > summary > span > div > p:first-child::before {{
        content: none !important;
        display: none !important;
    }}
    /* Target the _arrow span directly */
    [data-testid="stExpander"] summary {{
        list-style: none !important;
    }}
    [data-testid="stExpander"] summary::-webkit-details-marker {{
        display: none !important;
    }}
    /* Streamlit 1.32+ expander label override */
    [data-testid="stExpanderToggleIcon"] {{
        display: none !important;
    }}
    details summary div[data-testid="stMarkdownContainer"] p {{
        font-size: 14px !important;
        font-weight: 600 !important;
        color: {th['text1']} !important;
    }}

    /* ── Sidebar toggle floating button ── */
    .sb-toggle-btn {{
        position: fixed;
        top: 50%;
        left: 240px;
        transform: translateY(-50%);
        z-index: 9999;
        width: 22px;
        height: 48px;
        background: {th['card2']};
        border: 1px solid {th['border']};
        border-left: none;
        border-radius: 0 8px 8px 0;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        color: {th['text3']};
        font-size: 11px;
        transition: all .2s;
        user-select: none;
    }}
    .sb-toggle-btn:hover {{
        background: {th['card']};
        color: {th['text1']};
        width: 26px;
    }}
    .sb-collapsed .sb-toggle-btn {{
        left: 0;
    }}

    /* ── SIDEBAR ── */
    section[data-testid="stSidebar"] {{
        background: {th['nav']} !important;
        border-right: 1px solid {th['nav_border']} !important;
        min-width: {sb_w} !important;
        max-width: {sb_w} !important;
        transition: min-width .25s ease, max-width .25s ease !important;
        overflow: hidden !important;
    }}
    section[data-testid="stSidebar"] > div {{
        padding: {sb_pad} !important;
        width: {sb_w} !important;
        overflow: hidden !important;
    }}
    /* Hide sidebar collapse button completely */
    button[data-testid="collapsedControl"] {{
        display: none !important;
    }}
    /* Sidebar text color override */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {{
        color: {th['nav_text']} !important;
    }}
    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton > button {{
        background: {th['card2']} !important;
        color: {th['text2']} !important;
        border: 1px solid {th['border']} !important;
        border-radius: 8px !important;
        font-size: 12px !important;
        padding: 6px 8px !important;
        font-weight: 500 !important;
    }}
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
        background: {th['green']} !important;
        color: #111118 !important;
        border-color: {th['green']} !important;
        font-weight: 700 !important;
    }}
    /* Sidebar selectbox */
    section[data-testid="stSidebar"] .stSelectbox > div > div {{
        background: {th['card']} !important;
        border: 1px solid {th['border']} !important;
        color: {th['text1']} !important;
        font-size: 12px !important;
    }}

    .stApp {{
        background: {th['bg']} !important;
        font-family: 'Noto Sans HK', 'Inter', sans-serif !important;
        font-size: {fs}px;
    }}

    .block-container {{
        padding-top: 16px !important;
        padding-bottom: 0 !important;
        max-width: 100% !important;
    }}

    body, p, div, span, label {{
        font-family: 'Noto Sans HK', 'Inter', sans-serif !important;
        color: {th['text1']};
    }}

    /* ───── LOGIN PAGE ───── */
    .login-wrap {{
        min-height: 80vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 40px 20px;
    }}
    .login-card {{
        background: {th['card']};
        border: 1px solid {th['border']};
        border-radius: 16px;
        padding: 40px 36px;
        max-width: 400px;
        width: 100%;
        box-shadow: 0 8px 24px rgba(0,0,0,0.18);
    }}
    .login-logo {{
        display: flex; align-items: center; gap: 12px;
        margin-bottom: 28px; justify-content: center;
    }}
    .login-mark {{
        width: 44px; height: 44px; border-radius: 12px;
        background: {th['green']};
        display: flex; align-items: center; justify-content: center;
    }}
    .login-title {{
        font-size: 22px; font-weight: 700; color: {th['text1']};
        text-align: center; margin-bottom: 6px;
    }}
    .login-sub {{
        font-size: 12px; color: {th['text3']};
        text-align: center; margin-bottom: 28px;
        letter-spacing: 0.5px;
    }}

    /* Streamlit input override */
    .stTextInput > div > div > input {{
        background: {th['bg2']} !important;
        border: 1px solid {th['border']} !important;
        color: {th['text1']} !important;
        border-radius: 9px !important;
        padding: 10px 14px !important;
        font-size: {fs}px !important;
        font-family: 'Noto Sans HK', 'Inter', sans-serif !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {th['green']} !important;
        box-shadow: 0 0 0 2px {th['nav_active_bg']} !important;
    }}
    .stTextInput label {{
        color: {th['text2']} !important;
        font-size: 12px !important;
        font-weight: 500 !important;
    }}

    /* Streamlit button override */
    .stButton > button {{
        background: {th['green']} !important;
        color: #111118 !important;
        border: none !important;
        border-radius: 9px !important;
        padding: 10px 20px !important;
        font-size: {fs}px !important;
        font-weight: 700 !important;
        font-family: 'Noto Sans HK', 'Inter', sans-serif !important;
        width: 100%;
        transition: all 0.15s !important;
    }}
    .stButton > button:hover {{
        background: {th['nav_text_active']} !important;
        transform: translateY(-1px);
    }}

    /* Selectbox override */
    .stSelectbox > div > div {{
        background: {th['card']} !important;
        border: 1px solid {th['border']} !important;
        color: {th['text1']} !important;
    }}

    /* ───── DASHBOARD LAYOUT ───── */
    .topbar {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 18px 22px; background: {th['bg']};
        border-bottom: 1px solid {th['border']};
        margin: -16px -16px 0 -16px;
        flex-wrap: wrap; gap: 12px;
    }}
    .topbar-left {{ display: flex; align-items: center; gap: 16px; }}
    .topbar-logo {{
        display: flex; align-items: center; gap: 10px;
    }}
    .tb-mark {{
        width: 32px; height: 32px; border-radius: 9px;
        background: {th['green']};
        display: flex; align-items: center; justify-content: center;
    }}
    .tb-title {{ font-size: 15px; font-weight: 700; color: {th['text1']}; }}
    .tb-sub {{ font-size: 9px; color: {th['text3']}; letter-spacing: 0.6px; }}
    .topbar-right {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}

    .chip {{
        display: inline-flex; align-items: center; gap: 7px;
        background: {th['card']};
        border: 1px solid {th['border']};
        border-radius: 9px; padding: 7px 13px;
        font-size: 12px; color: {th['text2']};
    }}
    .sdot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
    .sdot-on {{ background: {th['green']}; box-shadow: 0 0 5px {th['green']}; animation: blink 2.5s infinite; }}
    .sdot-off {{ background: {th['red']}; }}
    @keyframes blink {{ 0%,100% {{ opacity: 1 }} 50% {{ opacity: 0.2 }} }}

    .page-header {{
        padding: 20px 22px 14px;
    }}
    .page-title {{ font-size: 22px; font-weight: 700; color: {th['text1']}; letter-spacing: -0.5px; }}
    .page-sub {{ font-size: 12px; color: {th['text3']}; margin-top: 3px; }}

    .eye-banner {{
        background: rgba(90,180,120,0.10);
        border: 1px solid rgba(90,180,120,0.20);
        border-radius: 9px; padding: 9px 14px;
        font-size: 12px; color: #8ab898;
        margin: 0 22px 14px;
        display: flex; align-items: center; gap: 8px;
    }}

    .expiry-banner {{
        background: rgba(240,160,48,0.10);
        border: 1px solid rgba(240,160,48,0.25);
        border-radius: 9px; padding: 9px 14px;
        font-size: 12px; color: {th['orange']};
        margin: 0 22px 14px;
        display: flex; align-items: center; gap: 8px;
    }}

    /* ───── KPI CARDS ───── */
    .kpi-card {{
        background: {th['card']};
        border: 1px solid {th['border']};
        border-radius: 13px; padding: 18px;
        position: relative; overflow: hidden;
        transition: border-color 0.2s, transform 0.15s;
    }}
    .kpi-card:hover {{ border-color: rgba(255,255,255,0.18); transform: translateY(-1px); }}
    .kpi-bar {{
        position: absolute; top: 0; left: 0; right: 0;
        height: 3px; border-radius: 13px 13px 0 0;
    }}
    .kpi-top {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 10px; }}
    .kpi-label {{
        font-size: 11px; color: {th['text3']};
        text-transform: uppercase; letter-spacing: 0.5px; font-weight: 500;
    }}
    .kpi-icon {{
        width: 30px; height: 30px; border-radius: 9px;
        display: flex; align-items: center; justify-content: center;
    }}
    .kpi-val {{
        font-size: 28px; font-weight: 800;
        color: {th['text1']}; line-height: 1;
        font-family: 'Inter', monospace;
        letter-spacing: -1px;
        font-variant-numeric: tabular-nums;
    }}
    .kpi-chg {{ font-size: 13px; font-weight: 600; margin-top: 7px; display: flex; align-items: center; gap: 4px; }}
    .up {{ color: {th['green']}; }}
    .dn {{ color: {th['red']}; }}
    .kpi-note {{ color: {th['text3']}; font-weight: 400; font-size: 11px; margin-left: 3px; }}
    .kpi-spark {{ position: absolute; bottom: 0; right: 0; width: 96px; height: 48px; opacity: 0.5; }}

    /* ───── CARDS ───── */
    .ds-card {{
        background: {th['card']};
        border: 1px solid {th['border']};
        border-radius: 13px; padding: 18px;
        height: 100%;
    }}
    .card-hd {{
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 14px;
    }}
    .card-title {{ font-size: 14px; font-weight: 600; color: {th['text1']}; }}
    .card-sub {{ font-size: 11px; color: {th['text3']}; margin-top: 3px; }}
    .card-pill {{ font-size: 11px; color: {th['text3']}; }}

    /* ───── HEATMAP ───── */
    .hm-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 5px; }}
    .hm-row {{
        display: flex; align-items: center; padding: 8px 10px;
        border-radius: 8px; background: {th['bg2']}; gap: 8px;
    }}
    .hm-name {{ font-size: 12px; color: {th['text2']}; min-width: 44px; }}
    .hm-bar-w {{
        flex: 1; height: 4px; background: {th['border']};
        border-radius: 2px; overflow: hidden;
    }}
    .hm-bar {{ height: 100%; border-radius: 2px; }}
    .hm-val {{
        font-size: 12px; font-weight: 700;
        font-family: 'Inter', monospace;
        min-width: 50px; text-align: right;
        font-variant-numeric: tabular-nums;
    }}

    /* ───── SIGNAL LIST ───── */
    .si-row {{
        display: flex; align-items: center;
        padding: 10px 0; border-bottom: 1px solid {th['border2']};
    }}
    .si-row:last-child {{ border-bottom: none; }}
    .si-l {{ display: flex; align-items: center; gap: 10px; flex: 1; }}
    .si-r {{ display: flex; align-items: center; gap: 8px; }}
    .si-dot {{ width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }}
    .si-tk {{
        font-size: 15px; font-weight: 700; color: {th['text1']};
        font-family: 'Inter', monospace; min-width: 52px;
        font-variant-numeric: tabular-nums;
    }}
    .si-pr {{
        font-size: 12px; color: {th['text3']};
        font-family: 'Inter', monospace;
        font-variant-numeric: tabular-nums;
    }}
    .si-sc {{
        font-size: 16px; font-weight: 800;
        font-family: 'Inter', monospace;
        font-variant-numeric: tabular-nums;
    }}
    .badge {{ font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 6px; }}
    .b-buy {{ background: rgba(0,201,138,0.13); color: {th['green']}; border: 1px solid rgba(0,201,138,0.25); }}
    .b-watch {{ background: rgba(240,160,48,0.13); color: {th['orange']}; border: 1px solid rgba(240,160,48,0.25); }}
    .b-avoid {{ background: rgba(240,85,85,0.13); color: {th['red']}; border: 1px solid rgba(240,85,85,0.25); }}

    /* ───── REGIME ───── */
    .regime-state-lbl {{
        font-size: 11px; color: {th['text3']};
        margin-bottom: 5px; font-weight: 600;
        letter-spacing: 0.6px; text-transform: uppercase;
    }}
    .regime-val {{ font-size: 15px; font-weight: 700; color: {th['green']}; margin-bottom: 13px; }}
    .reg-bar {{ margin-bottom: 9px; }}
    .reg-bar-hd {{
        display: flex; justify-content: space-between;
        font-size: 12px; color: {th['text2']}; margin-bottom: 5px;
    }}
    .reg-bar-hd span:last-child {{ font-weight: 700; }}
    .reg-bar-track {{
        height: 6px; border-radius: 3px;
        background: {th['bg2']}; overflow: hidden;
    }}
    .reg-bar-fill {{ height: 100%; border-radius: 3px; }}
    .ai-tip {{
        margin-top: 12px; padding: 12px 14px;
        background: rgba(0,201,138,0.08);
        border-radius: 10px;
        border-left: 3px solid {th['green']};
    }}
    .ai-tip-l {{
        font-size: 10px; color: {th['green']}; font-weight: 700;
        margin-bottom: 4px; letter-spacing: 0.5px; text-transform: uppercase;
    }}
    .ai-tip-t {{ font-size: 13px; color: {th['text2']}; line-height: 1.6; }}

    /* ───── VIX ───── */
    .vix-curve {{
        display: flex; align-items: flex-end; gap: 6px;
        height: 72px; margin: 10px 0;
    }}
    .vix-bar-c {{ display: flex; flex-direction: column; align-items: center; gap: 5px; flex: 1; }}
    .vix-bar {{ width: 100%; border-radius: 4px 4px 0 0; }}
    .vix-bar-l {{ font-size: 11px; color: {th['text3']}; font-weight: 500; }}
    .vix-row {{
        display: flex; justify-content: space-between; align-items: center;
        padding: 7px 0; border-bottom: 1px solid {th['border2']};
    }}
    .vix-row:last-child {{ border-bottom: none; }}
    .vrt {{ font-size: 13px; color: {th['text2']}; }}
    .vrv {{
        font-size: 13px; font-weight: 700;
        font-family: 'Inter', monospace;
        font-variant-numeric: tabular-nums;
    }}
    .ctag {{
        margin-top: 10px; padding: 9px 12px;
        background: rgba(77,159,255,0.10);
        border-radius: 9px; font-size: 12px; color: {th['blue']};
        line-height: 1.5;
        border: 1px solid rgba(77,159,255,0.15);
    }}

    /* Make Streamlit columns tighter */
    [data-testid="stVerticalBlock"] {{ gap: 12px !important; }}
    [data-testid="stHorizontalBlock"] {{ gap: 11px !important; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#   USER MANAGEMENT (Google Sheets + bcrypt)
# ═══════════════════════════════════════════════════════════════════
@st.cache_resource
def get_gsheet():
    """Connect to Google Sheets."""
    try:
        creds_json = st.secrets["google_sheets"]["credentials"]
        if isinstance(creds_json, str):
            creds_dict = json.loads(creds_json)
        else:
            # Streamlit toml nested table → convert to plain dict recursively
            creds_dict = {k: str(v) if not isinstance(v, dict) else dict(v)
                          for k, v in dict(creds_json).items()}
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
        return client.open_by_key(sheet_id).sheet1
    except Exception as e:
        # Store error for display in admin tab
        import streamlit as _st
        _st.session_state["gsheet_error"] = str(e)
        return None


def debug_gsheet_connection():
    """Show detailed connection diagnostics in admin tab"""
    th = get_theme()
    err = st.session_state.get("gsheet_error", "")

    # Check secrets structure
    checks = []

    # 1. Check google_sheets section exists
    try:
        _ = st.secrets["google_sheets"]
        checks.append(("✅", "Secrets 包含 [google_sheets] 區段"))
    except Exception:
        checks.append(("❌", "Secrets 缺少 [google_sheets] 區段"))

    # 2. Check spreadsheet_id
    try:
        sid = st.secrets["google_sheets"]["spreadsheet_id"]
        checks.append(("✅", f"spreadsheet_id 已設定：{sid[:20]}..."))
    except Exception:
        checks.append(("❌", "缺少 spreadsheet_id"))

    # 3. Check credentials
    try:
        creds_raw = st.secrets["google_sheets"]["credentials"]
        creds_type = type(creds_raw).__name__
        if isinstance(creds_raw, str):
            parsed = json.loads(creds_raw)
            checks.append(("✅", f"credentials 係 JSON 字串，已解析（type: {parsed.get('type','?')}）"))
        else:
            parsed = dict(creds_raw)
            checks.append(("✅", f"credentials 係 TOML 表格（type: {parsed.get('type','?')}）"))
        # Check required fields
        for field in ["type","project_id","private_key","client_email"]:
            if field in parsed:
                val = str(parsed[field])
                display = val[:30] + "..." if len(val) > 30 else val
                checks.append(("✅", f"credentials.{field} = {display}"))
            else:
                checks.append(("❌", f"credentials 缺少 {field}"))
    except Exception as ex:
        checks.append(("❌", f"credentials 解析失敗: {ex}"))

    # 4. Show connection error if any
    if err:
        checks.append(("❌", f"連接錯誤: {err}"))

    html = ""
    for icon, msg in checks:
        color = th["green"] if icon == "✅" else th["red"]
        html += (
            f'<div style="padding:7px 12px;margin-bottom:4px;'
            f'background:{th["card2"]};border-radius:7px;'
            f'font-size:12px;color:{th["text1"]}">'
            f'<span style="color:{color};margin-right:8px">{icon}</span>{msg}</div>'
        )
    st.markdown(html, unsafe_allow_html=True)


# Local fallback users for development / when Google Sheets unavailable
FALLBACK_USERS = {
    "admin": {
        "password_hash": bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode(),
        "role": "admin",
        "expiry_date": "2099-12-31",
        "region": "UK",
        "language": "zh-hant",
        "theme": "dark",
        "status": "active",
    },
    "tesla": {
        "password_hash": bcrypt.hashpw("tesla123".encode(), bcrypt.gensalt()).decode(),
        "role": "pro",
        "expiry_date": "2026-12-31",
        "region": "UK",
        "language": "zh-hant",
        "theme": "dark",
        "status": "active",
    },
    "demo": {
        "password_hash": bcrypt.hashpw("demo123".encode(), bcrypt.gensalt()).decode(),
        "role": "free",
        "expiry_date": "2099-12-31",
        "region": "HK",
        "language": "zh-hant",
        "theme": "light",
        "status": "active",
    },
}


def authenticate(username: str, password: str):
    """Returns (success: bool, user_data: dict|None, error_msg: str)"""
    sheet = get_gsheet()
    user_data = None

    if sheet is not None:
        try:
            records = sheet.get_all_records()
            for row in records:
                if row.get("username") == username:
                    user_data = row
                    break
        except Exception:
            user_data = FALLBACK_USERS.get(username)
    else:
        u = FALLBACK_USERS.get(username)
        if u:
            user_data = {"username": username, **u}

    if not user_data:
        return False, None, t("login_fail")

    if user_data.get("status", "active") != "active":
        return False, None, t("login_disabled")

    expiry_str = str(user_data.get("expiry_date", "2099-12-31"))
    try:
        expiry = datetime.strptime(expiry_str, "%Y-%m-%d").date()
        if expiry < datetime.now().date():
            return False, None, t("login_expired")
    except Exception:
        pass

    pw_hash = user_data.get("password_hash", "")
    try:
        if not bcrypt.checkpw(password.encode(), pw_hash.encode()):
            return False, None, t("login_fail")
    except Exception:
        return False, None, t("login_fail")

    return True, user_data, ""


# ═══════════════════════════════════════════════════════════════════
#   MARKET DATA (yfinance)
# ═══════════════════════════════════════════════════════════════════
SECTOR_TICKERS = {
    "科技": "XLK", "通訊": "XLC", "銀行": "XLF",
    "芯片": "SOXX", "非必需": "XLY", "REITS": "IYR",
    "國防": "ITA", "能源": "XLE", "必需品": "XLP",
    "醫療": "XLV", "公用": "XLU",
}
SECTOR_TICKERS_EN = {
    "Tech": "XLK", "Comm": "XLC", "Banks": "XLF",
    "Chips": "SOXX", "Discr": "XLY", "REITS": "IYR",
    "Defense": "ITA", "Energy": "XLE", "Staples": "XLP",
    "Health": "XLV", "Utils": "XLU",
}

KPI_TICKERS = {
    "sp500": "^GSPC",
    "nasdaq": "^IXIC",
    "vix": "^VIX",
    "gold": "GC=F",
}

VIX_TERM_TICKERS = {
    "9D": "^VIX9D",
    "VIX": "^VIX",
    "3M": "^VIX3M",
    "6M": "^VIX6M",
}


@st.cache_data(ttl=300, show_spinner=False)
def fetch_kpi_data():
    """Fetch top-row KPI data with sparkline history"""
    out = {}
    for key, sym in KPI_TICKERS.items():
        try:
            df = yf.download(sym, period="1mo", interval="1d",
                            progress=False, auto_adjust=True)
            if df.empty or len(df) < 2:
                out[key] = None
                continue
            close = df["Close"].dropna()
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]
            latest = float(close.iloc[-1])
            prev = float(close.iloc[-2])
            chg_pct = (latest - prev) / prev * 100 if prev else 0
            spark = close.tail(30).tolist()
            out[key] = {
                "value": latest,
                "change": chg_pct,
                "spark": spark,
            }
        except Exception:
            out[key] = None
    return out


@st.cache_data(ttl=300, show_spinner=False)
def fetch_sector_data(period_key="1m"):
    """Fetch sector performance for given period"""
    period_map = {"1d": "5d", "1m": "1mo", "ytd": "1y"}
    lookback = {"1d": 1, "1m": 22, "ytd": 75}
    period = period_map.get(period_key, "1mo")
    lb = lookback.get(period_key, 22)

    out = {}
    lang = st.session_state.get("lang", "zh-hant")
    tickers_dict = SECTOR_TICKERS_EN if lang == "en" else SECTOR_TICKERS

    for name, sym in tickers_dict.items():
        try:
            df = yf.download(sym, period=period, interval="1d",
                            progress=False, auto_adjust=True)
            if df.empty:
                out[name] = 0.0
                continue
            close = df["Close"].dropna()
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]
            if len(close) < 2:
                out[name] = 0.0
                continue
            start_idx = max(0, len(close) - lb - 1)
            chg = (float(close.iloc[-1]) / float(close.iloc[start_idx]) - 1) * 100
            out[name] = chg
        except Exception:
            out[name] = 0.0
    return out


@st.cache_data(ttl=300, show_spinner=False)
def fetch_vix_term():
    """Fetch VIX term structure"""
    out = {}
    for label, sym in VIX_TERM_TICKERS.items():
        try:
            df = yf.download(sym, period="5d", interval="1d",
                            progress=False, auto_adjust=True)
            if df.empty:
                out[label] = None
                continue
            close = df["Close"].dropna()
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]
            out[label] = float(close.iloc[-1])
        except Exception:
            out[label] = None
    return out


@st.cache_data(ttl=300, show_spinner=False)
def fetch_watchlist_signals(tickers: list):
    """Compute simple signal score (0-100) for watchlist"""
    out = []
    for tk in tickers:
        try:
            df = yf.download(tk, period="3mo", interval="1d",
                            progress=False, auto_adjust=True)
            if df.empty or len(df) < 30:
                continue
            close = df["Close"].dropna()
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]

            latest = float(close.iloc[-1])

            # EMA 20 vs 50
            ema20 = close.ewm(span=20).mean().iloc[-1]
            ema50 = close.ewm(span=50).mean().iloc[-1] if len(close) >= 50 else ema20
            trend_score = 35 if latest > ema20 > ema50 else (15 if latest > ema20 else 0)

            # RSI(14)
            delta = close.diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / (loss.replace(0, np.nan))
            rsi = (100 - 100 / (1 + rs)).iloc[-1]
            if pd.isna(rsi):
                rsi = 50
            mom_score = 30 if 50 < rsi < 70 else (20 if 40 < rsi <= 50 else (10 if rsi >= 70 else 5))

            # Volatility (lower = better short-term)
            atr = (df["High"] - df["Low"]).rolling(14).mean().iloc[-1]
            atr_pct = float(atr) / latest * 100 if latest else 5
            if isinstance(atr_pct, pd.Series):
                atr_pct = float(atr_pct.iloc[0])
            vol_score = 35 if atr_pct < 2 else (25 if atr_pct < 4 else 15)

            score = int(trend_score + mom_score + vol_score)
            score = max(0, min(100, score))

            out.append({
                "ticker": tk,
                "price": latest,
                "score": score,
            })
        except Exception:
            continue
    return out


@st.cache_data(ttl=600, show_spinner=False)
def compute_market_regime():
    """Compute market regime scores (Risk-On/Off)"""
    try:
        vix_data = fetch_kpi_data().get("vix")
        vix = vix_data["value"] if vix_data else 20

        spy_df = yf.download("^GSPC", period="3mo", interval="1d",
                            progress=False, auto_adjust=True)
        if spy_df.empty:
            return None
        close = spy_df["Close"].dropna()
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        # Momentum: 20-day return
        if len(close) >= 22:
            mom_pct = (float(close.iloc[-1]) / float(close.iloc[-22]) - 1) * 100
        else:
            mom_pct = 0
        momentum = max(0, min(100, int(50 + mom_pct * 5)))

        # Breadth: % of sectors above their 20-day MA
        sectors_above = 0
        sector_count = 0
        for sym in list(SECTOR_TICKERS.values())[:8]:
            try:
                d = yf.download(sym, period="2mo", interval="1d",
                              progress=False, auto_adjust=True)
                if d.empty:
                    continue
                c = d["Close"].dropna()
                if isinstance(c, pd.DataFrame):
                    c = c.iloc[:, 0]
                if len(c) < 21:
                    continue
                ma20 = c.tail(20).mean()
                if float(c.iloc[-1]) > float(ma20):
                    sectors_above += 1
                sector_count += 1
            except Exception:
                continue
        breadth = int(sectors_above / max(sector_count, 1) * 100)

        # Sentiment: inverse VIX
        sentiment = max(0, min(100, int((40 - vix) * 3 + 50)))

        # Volatility: VIX level (lower = lower bar = good)
        vol_bar = max(0, min(100, int(vix * 3)))

        # Determine regime
        avg_score = (momentum + breadth + sentiment) / 3
        if vix > 35:
            regime = "extreme_fear"
            color = "red"
        elif avg_score > 60 and vix < 22:
            regime = "risk_on"
            color = "green"
        elif avg_score < 35 or vix > 28:
            regime = "risk_off"
            color = "red"
        else:
            regime = "neutral"
            color = "orange"

        return {
            "regime": regime,
            "color": color,
            "momentum": momentum,
            "breadth": breadth,
            "sentiment": sentiment,
            "volatility": vol_bar,
            "vix": vix,
        }
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════════════
#   MARKET HOURS DETECTION
# ═══════════════════════════════════════════════════════════════════
def market_status():
    """Return status dict for US, HK, CN, UK markets"""
    now_utc = datetime.now(pytz.utc)

    def is_open(tz_str, open_h, open_m, close_h, close_m):
        tz = pytz.timezone(tz_str)
        now_local = now_utc.astimezone(tz)
        if now_local.weekday() >= 5:
            return False
        open_t = now_local.replace(hour=open_h, minute=open_m, second=0, microsecond=0)
        close_t = now_local.replace(hour=close_h, minute=close_m, second=0, microsecond=0)
        return open_t <= now_local <= close_t

    return {
        "us": is_open("America/New_York", 9, 30, 16, 0),
        "hk": is_open("Asia/Hong_Kong", 9, 30, 16, 0),
        "cn": is_open("Asia/Shanghai", 9, 30, 15, 0),
        "uk": is_open("Europe/London", 8, 0, 16, 30),
    }


# ═══════════════════════════════════════════════════════════════════
#   UI HELPERS
# ═══════════════════════════════════════════════════════════════════
def fmt_num(v, decimals=0):
    if v is None:
        return "—"
    if abs(v) >= 1000:
        return f"{v:,.{decimals}f}"
    return f"{v:.{decimals}f}"


def fmt_pct(v, decimals=2):
    if v is None:
        return "—"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.{decimals}f}%"


def make_sparkline_svg(values, color, width=96, height=48):
    """Generate inline SVG sparkline with gradient fill"""
    if not values or len(values) < 2:
        return ""
    vmin, vmax = min(values), max(values)
    rng = vmax - vmin if vmax > vmin else 1
    n = len(values)

    pts = []
    for i, v in enumerate(values):
        x = i / (n - 1) * width
        y = height - ((v - vmin) / rng) * (height - 8) - 4
        pts.append(f"{x:.1f},{y:.1f}")
    poly_pts = " ".join(pts)
    fill_pts = poly_pts + f" {width},{height} 0,{height}"

    grad_id = f"g{abs(hash(color)) % 10000}"
    return f"""
    <svg class="kpi-spark" viewBox="0 0 {width} {height}" preserveAspectRatio="none">
      <defs>
        <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stop-color="{color}" stop-opacity="0.32"/>
          <stop offset="1" stop-color="{color}" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <polygon points="{fill_pts}" fill="url(#{grad_id})"/>
      <polyline points="{poly_pts}" fill="none" stroke="{color}" stroke-width="1.8" stroke-linejoin="round"/>
    </svg>
    """


def render_kpi_card(label, value, change, color, spark_values, note=""):
    """Render a KPI card HTML"""
    th = get_theme()
    color_map = {
        "green": th["green"], "red": th["red"],
        "blue": th["blue"], "orange": th["orange"],
        "purple": th["purple"],
    }
    c = color_map.get(color, th["green"])
    bg2 = c.replace(")", ",0.13)").replace("rgb", "rgba") if c.startswith("rgb") else c + "22"

    val_color = th["text1"] if color in ("green", "blue") else c
    chg_class = "up" if (change or 0) >= 0 else "dn"
    arrow = "▲" if (change or 0) >= 0 else "▼"

    spark_svg = make_sparkline_svg(spark_values or [], c)

    return f"""
    <div class="kpi-card">
      <div class="kpi-bar" style="background:{c}"></div>
      <div class="kpi-top">
        <div class="kpi-label">{label}</div>
        <div class="kpi-icon" style="background:{c}22">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M1 11L5 7l3 3.5 4-5 3 4" stroke="{c}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
      </div>
      <div class="kpi-val" style="color:{val_color}">{value}</div>
      <div class="kpi-chg {chg_class}">{arrow} {fmt_pct(change)}<span class="kpi-note">{note}</span></div>
      {spark_svg}
    </div>
    """


# ═══════════════════════════════════════════════════════════════════
#   LOGIN PAGE — Dark gradient, cinematic style
# ═══════════════════════════════════════════════════════════════════
def render_login():
    # Language labels for switcher
    lang_opts = {"繁體中文": "zh-hant", "简体中文": "zh-hans", "English": "en"}
    lang_rev  = {v: k for k, v in lang_opts.items()}
    cur_lang  = st.session_state.get("lang", "zh-hant")

    # Full-page CSS — dark gradient background, no Streamlit chrome
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+HK:wght@300;400;500;700&family=Inter:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { margin:0; padding:0; }
    .stApp {
        background: linear-gradient(160deg, #0d1b2a 0%, #1a1a3e 40%, #0f2027 70%, #1a0a2e 100%) !important;
        min-height: 100vh;
    }
    #MainMenu, footer, header, .stDeployButton { visibility: hidden; }
    /* Hide sidebar on login page */
    section[data-testid="stSidebar"] { display: none !important; }
    button[data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stVerticalBlock"] { gap: 0 !important; }
    [data-testid="stHorizontalBlock"] { gap: 0 !important; }

    /* Language switcher row */
    .login-lang-row {
        display: flex;
        justify-content: center;
        gap: 8px;
        margin-bottom: 32px;
    }
    .lang-pill {
        padding: 5px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 500;
        cursor: pointer;
        border: 1px solid rgba(255,255,255,0.15);
        color: rgba(255,255,255,0.5);
        background: transparent;
        font-family: 'Noto Sans HK', sans-serif;
        transition: all .2s;
        text-decoration: none;
    }
    .lang-pill.active {
        background: rgba(255,255,255,0.12);
        color: #ffffff;
        border-color: rgba(255,255,255,0.35);
    }

    /* Logo circle */
    .login-logo-circle {
        width: 72px; height: 72px;
        border-radius: 50%;
        border: 2px solid rgba(255,255,255,0.25);
        display: flex; align-items: center; justify-content: center;
        margin: 0 auto 20px;
        background: rgba(255,255,255,0.06);
    }

    /* Title */
    .login-brand {
        text-align: center;
        margin-bottom: 6px;
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.5px;
        font-family: 'Inter', sans-serif;
    }
    .login-brand-sub {
        text-align: center;
        font-size: 12px;
        color: rgba(255,255,255,0.38);
        letter-spacing: 2px;
        text-transform: uppercase;
        font-family: 'Inter', sans-serif;
        margin-bottom: 36px;
    }

    /* Input fields override */
    .login-form .stTextInput > div > div > input {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
        font-size: 14px !important;
        padding: 14px 16px !important;
        font-family: 'Noto Sans HK', 'Inter', sans-serif !important;
        transition: border-color .2s !important;
    }
    .login-form .stTextInput > div > div > input:focus {
        border-color: rgba(255,255,255,0.4) !important;
        background: rgba(255,255,255,0.10) !important;
        box-shadow: none !important;
    }
    .login-form .stTextInput > div > div > input::placeholder {
        color: rgba(255,255,255,0.25) !important;
    }
    .login-form .stTextInput label {
        color: rgba(255,255,255,0.55) !important;
        font-size: 12px !important;
        font-weight: 400 !important;
        letter-spacing: 0.3px !important;
    }

    /* Submit button override */
    .login-form .stFormSubmitButton > button {
        background: #e8517a !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 20px !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        width: 100% !important;
        font-family: 'Noto Sans HK', 'Inter', sans-serif !important;
        letter-spacing: 0.3px !important;
        margin-top: 8px !important;
        transition: all .2s !important;
        cursor: pointer !important;
    }
    .login-form .stFormSubmitButton > button:hover {
        background: #d4446d !important;
        transform: translateY(-1px) !important;
    }
    .login-form .stFormSubmitButton > button:active {
        transform: translateY(0) !important;
    }

    /* Error / warning override */
    .login-form .stAlert {
        background: rgba(240,85,85,0.15) !important;
        border: 1px solid rgba(240,85,85,0.3) !important;
        border-radius: 9px !important;
        color: #ff9999 !important;
    }

    /* Forgot / footer text */
    .login-footer {
        text-align: center;
        margin-top: 20px;
        font-size: 12px;
        color: rgba(255,255,255,0.3);
        font-family: 'Noto Sans HK', sans-serif;
        line-height: 1.8;
    }
    </style>
    """, unsafe_allow_html=True)

    # Centered layout — top spacer + narrow column
    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.1, 1])
    with mid:
        # ── Language switcher ──
        lang_html = '<div class="login-lang-row">'
        for label, code in lang_opts.items():
            active = "active" if code == cur_lang else ""
            lang_html += f'<span class="lang-pill {active}" onclick="">{label}</span>'
        lang_html += "</div>"
        st.markdown(lang_html, unsafe_allow_html=True)

        # Real language selectbox (hidden label, drives session state)
        cur_label = lang_rev.get(cur_lang, "繁體中文")
        new_lang_label = st.selectbox(
            "", list(lang_opts.keys()),
            index=list(lang_opts.keys()).index(cur_label),
            key="login_lang_sel",
            label_visibility="collapsed",
        )
        if lang_opts[new_lang_label] != cur_lang:
            st.session_state["lang"] = lang_opts[new_lang_label]
            st.rerun()

        # ── Logo + brand ──
        st.markdown("""
        <div class="login-logo-circle">
          <svg width="32" height="32" viewBox="0 0 20 20" fill="none">
            <path d="M2 15L6 8.5l3.5 4.5 4-7L18 15H2z"
                  fill="none" stroke="rgba(255,255,255,0.85)" stroke-width="1.3"
                  stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="login-brand">MarketIQ</div>
        <div class="login-brand-sub">Intelligence Dashboard</div>
        """, unsafe_allow_html=True)

        # ── Login form ──
        with st.container():
            st.markdown('<div class="login-form">', unsafe_allow_html=True)
            with st.form("login_form", clear_on_submit=False):
                uname_label = {"zh-hant": "用戶名", "zh-hans": "用户名", "en": "Username"}.get(cur_lang, "用戶名")
                pass_label  = {"zh-hant": "密碼",   "zh-hans": "密码",   "en": "Password"}.get(cur_lang, "密碼")
                btn_label   = {"zh-hant": "登　入", "zh-hans": "登　入", "en": "Log In"}.get(cur_lang, "登入")

                username = st.text_input(uname_label, placeholder=uname_label, key="login_u", label_visibility="visible")
                password = st.text_input(pass_label,  placeholder=pass_label,  key="login_p", type="password", label_visibility="visible")
                submit   = st.form_submit_button(btn_label)

                if submit:
                    fails = st.session_state.get("login_fails", 0)
                    lockout_until = st.session_state.get("lockout_until")
                    if lockout_until and datetime.now() < lockout_until:
                        st.error(t("login_locked"))
                    elif not username or not password:
                        st.error({"zh-hant": "請填寫用戶名及密碼", "zh-hans": "请填写用户名及密码", "en": "Please enter username and password"}.get(cur_lang, "請填寫用戶名及密碼"))
                    else:
                        ok, user_data, err = authenticate(username, password)
                        if ok:
                            st.session_state["logged_in"]    = True
                            st.session_state["username"]     = user_data.get("username", username)
                            st.session_state["role"]         = user_data.get("role", "free")
                            st.session_state["region"]       = user_data.get("region", "UK")
                            st.session_state["lang"]         = user_data.get("language", "zh-hant")
                            st.session_state["theme"]        = user_data.get("theme", "dark")
                            st.session_state["expiry_date"]  = str(user_data.get("expiry_date", "2099-12-31"))
                            st.session_state["login_fails"]  = 0
                            st.rerun()
                        else:
                            st.session_state["login_fails"] = fails + 1
                            if fails + 1 >= 5:
                                st.session_state["lockout_until"] = datetime.now() + timedelta(minutes=30)
                                st.error(t("login_locked"))
                            else:
                                st.error(err)

            st.markdown("</div>", unsafe_allow_html=True)

        # ── Footer ──
        forgot_txt = {"zh-hant": "忘記密碼？請聯絡管理員", "zh-hans": "忘记密码？请联系管理员", "en": "Forgot password? Contact admin"}.get(cur_lang, "忘記密碼？請聯絡管理員")
        disclaimer = {"zh-hant": "數據僅供參考，不構成投資建議", "zh-hans": "数据仅供参考，不构成投资建议", "en": "For reference only. Not investment advice."}.get(cur_lang, "數據僅供參考")
        st.markdown(
            f'<div class="login-footer">'
            f'{forgot_txt}<br><br>{disclaimer}'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#   SIDEBAR — Left nav matching prototype design
# ═══════════════════════════════════════════════════════════════════
def render_sidebar():
    th = get_theme()
    uname   = st.session_state.get("username", "User")
    role_v  = st.session_state.get("role", "free")
    region  = st.session_state.get("region", "UK")
    collapsed = st.session_state.get("sb_collapsed", False)

    with st.sidebar:
        if collapsed:
            # ── Mini collapsed view — just toggle button ──
            st.markdown(
                f'<div style="display:flex;justify-content:center;padding:8px 0 12px">'
                f'<div style="width:36px;height:36px;border-radius:10px;background:{th["green"]};'
                f'display:flex;align-items:center;justify-content:center">'
                f'<svg width="18" height="18" viewBox="0 0 20 20" fill="none">'
                f'<path d="M2 15L6 8.5l3.5 4.5 4-7L18 15H2z" fill="#111118"/></svg>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            if st.button("▶", key="sb_toggle", help="展開側欄",
                         use_container_width=True):
                st.session_state["sb_collapsed"] = False
                st.rerun()
            return

        # ── Full expanded sidebar ──
        col_logo, col_toggle = st.columns([4, 1])
        with col_logo:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px;padding:2px 0 16px">'
                f'<div style="width:36px;height:36px;border-radius:10px;background:{th["green"]};'
                f'display:flex;align-items:center;justify-content:center;flex-shrink:0">'
                f'<svg width="19" height="19" viewBox="0 0 20 20" fill="none">'
                f'<path d="M2 15L6 8.5l3.5 4.5 4-7L18 15H2z" fill="#111118"/></svg></div>'
                f'<div><div style="font-size:14px;font-weight:700;color:#e8eaf8">MarketIQ</div>'
                f'<div style="font-size:9px;color:{th["nav_text"]};letter-spacing:.5px">INTELLIGENCE DASHBOARD</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        with col_toggle:
            st.markdown("<div style='padding-top:4px'>", unsafe_allow_html=True)
            collapsed = st.session_state.get("sb_collapsed", False)
            icon = "▶" if collapsed else "◀"
            if st.button(icon, key="sb_toggle", help="收起/展開側欄",
                         use_container_width=True):
                st.session_state["sb_collapsed"] = not collapsed
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f'<hr style="border:none;border-top:1px solid {th["nav_border"]};margin:0 0 14px">', unsafe_allow_html=True)

        # ── Market status ──
        status = market_status()
        for code, label_on, label_off in [
            ("us", t("us_open"), t("us_closed")),
            ("hk", t("hk_open"), t("hk_closed")),
        ]:
            is_open = status.get(code, False)
            dot_col = th["green"] if is_open else th["red"]
            label   = label_on if is_open else label_off
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;'
                f'font-size:12px;color:{th["nav_text"]};padding:3px 0">'
                f'<span style="width:7px;height:7px;border-radius:50%;'
                f'background:{dot_col};display:inline-block;flex-shrink:0;'
                f'{"box-shadow:0 0 5px "+dot_col if is_open else ""}"></span>'
                f'{label}</div>',
                unsafe_allow_html=True,
            )

        st.markdown(f'<div style="height:14px"></div>', unsafe_allow_html=True)
        st.markdown(f'<hr style="border:none;border-top:1px solid {th["nav_border"]};margin:0 0 14px">', unsafe_allow_html=True)

        # ── Theme controls ──
        st.markdown(f'<div style="font-size:10px;color:{th["nav_text"]};letter-spacing:1.2px;text-transform:uppercase;margin-bottom:7px">主題</div>', unsafe_allow_html=True)
        tc1, tc2, tc3 = st.columns(3)
        cur_theme = st.session_state.get("theme", "dark")
        with tc1:
            if st.button(t("theme_dark"), key="sb_dark", use_container_width=True,
                         type="primary" if cur_theme == "dark" else "secondary"):
                st.session_state["theme"] = "dark"; st.rerun()
        with tc2:
            if st.button(t("theme_light"), key="sb_light", use_container_width=True,
                         type="primary" if cur_theme == "light" else "secondary"):
                st.session_state["theme"] = "light"; st.rerun()
        with tc3:
            if st.button(t("theme_eye"), key="sb_eye", use_container_width=True,
                         type="primary" if cur_theme == "eye" else "secondary"):
                st.session_state["theme"] = "eye"; st.rerun()

        st.markdown(f'<div style="height:10px"></div>', unsafe_allow_html=True)

        # ── Font size — THIS is where A- A A+ actually works ──
        st.markdown(f'<div style="font-size:10px;color:{th["nav_text"]};letter-spacing:1.2px;text-transform:uppercase;margin-bottom:7px">字體大小</div>', unsafe_allow_html=True)
        fc1, fc2, fc3 = st.columns(3)
        cur_fs = st.session_state.get("font_size", "md")
        with fc1:
            if st.button("A−", key="sb_sm", use_container_width=True,
                         type="primary" if cur_fs == "sm" else "secondary"):
                st.session_state["font_size"] = "sm"; st.rerun()
        with fc2:
            if st.button("A", key="sb_md", use_container_width=True,
                         type="primary" if cur_fs == "md" else "secondary"):
                st.session_state["font_size"] = "md"; st.rerun()
        with fc3:
            if st.button("A+", key="sb_lg", use_container_width=True,
                         type="primary" if cur_fs == "lg" else "secondary"):
                st.session_state["font_size"] = "lg"; st.rerun()

        st.markdown(f'<div style="height:10px"></div>', unsafe_allow_html=True)

        # ── Language ──
        st.markdown(f'<div style="font-size:10px;color:{th["nav_text"]};letter-spacing:1.2px;text-transform:uppercase;margin-bottom:7px">語言 / Language</div>', unsafe_allow_html=True)
        lang_opts = {"繁體中文": "zh-hant", "简体中文": "zh-hans", "English": "en"}
        cur_lang  = st.session_state.get("lang", "zh-hant")
        cur_label = next((k for k, v in lang_opts.items() if v == cur_lang), "繁體中文")
        new_lang  = st.selectbox("", list(lang_opts.keys()),
                                  index=list(lang_opts.keys()).index(cur_label),
                                  key="sb_lang", label_visibility="collapsed")
        if lang_opts[new_lang] != cur_lang:
            st.session_state["lang"] = lang_opts[new_lang]; st.rerun()

        st.markdown(f'<hr style="border:none;border-top:1px solid {th["nav_border"]};margin:14px 0">', unsafe_allow_html=True)

        # ── User pill ──
        role_lbl = {"admin": "👑 ADMIN", "pro": "⭐ PRO", "free": "🆓 FREE"}.get(role_v, "FREE")
        role_col = {"admin": th["orange"], "pro": th["green"], "free": th["text3"]}.get(role_v, th["text3"])
        initial  = uname[0].upper() if uname else "U"

        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;padding:11px 12px;'
            f'background:rgba(255,255,255,0.05);border-radius:11px;'
            f'border:1px solid {th["nav_border"]};margin-bottom:12px">'
            f'<div style="width:32px;height:32px;border-radius:50%;'
            f'background:linear-gradient(135deg,{th["green"]},{th["blue"]});'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:13px;font-weight:700;color:#111118;flex-shrink:0">{initial}</div>'
            f'<div style="flex:1;min-width:0">'
            f'<div style="font-size:13px;font-weight:600;color:{th["text1"]};'
            f'white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{uname}</div>'
            f'<div style="font-size:10px;color:{th["text3"]}">{region}</div></div>'
            f'<span style="font-size:9px;font-weight:700;color:{role_col};'
            f'background:{role_col}22;padding:2px 7px;border-radius:5px;'
            f'border:1px solid {role_col}44;flex-shrink:0">{role_lbl}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Logout ──
        if st.button(f"⏻  {t('logout')}", key="sb_logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k != "lockout_until":
                    del st.session_state[k]
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
#   TOPBAR — slim bar inside main area (title + status + controls)
# ═══════════════════════════════════════════════════════════════════
def render_main_topbar():
    th  = get_theme()
    now = datetime.now(pytz.timezone("Europe/London")).strftime("%d/%m/%Y %H:%M")
    status = market_status()

    us_col  = th["green"] if status.get("us") else th["red"]
    hk_col  = th["green"] if status.get("hk") else th["red"]
    us_lbl  = t("us_open"  if status.get("us") else "us_closed")
    hk_lbl  = t("hk_open"  if status.get("hk") else "hk_closed")

    st.markdown(
        f'<div style="display:flex;align-items:center;justify-content:space-between;'
        f'flex-wrap:wrap;gap:10px;margin-bottom:18px">'
        f'<div>'
        f'<div style="font-size:22px;font-weight:700;color:{th["text1"]};letter-spacing:-.5px">'
        f'{t("app_title")}</div>'
        f'<div style="font-size:12px;color:{th["text3"]};margin-top:3px">'
        f'{t("last_update")} {now} London · {t("data_source")}</div>'
        f'</div>'
        f'<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">'
        f'<div style="display:flex;align-items:center;gap:6px;background:{th["card"]};'
        f'border:1px solid {th["border"]};border-radius:9px;padding:6px 12px;font-size:12px;color:{th["text2"]}">'
        f'<span style="width:7px;height:7px;border-radius:50%;background:{us_col};flex-shrink:0"></span>{us_lbl}</div>'
        f'<div style="display:flex;align-items:center;gap:6px;background:{th["card"]};'
        f'border:1px solid {th["border"]};border-radius:9px;padding:6px 12px;font-size:12px;color:{th["text2"]}">'
        f'<span style="width:7px;height:7px;border-radius:50%;background:{hk_col};flex-shrink:0"></span>{hk_lbl}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════
#   MAIN APP ROUTER
# ═══════════════════════════════════════════════════════════════════
def main():
    # Session defaults
    for k, v in [("theme", "dark"), ("lang", "zh-hant"), ("font_size", "md"),
                  ("logged_in", False), ("ai_calls_today", 0)]:
        if k not in st.session_state:
            st.session_state[k] = v

    # Login page (no sidebar)
    if not st.session_state.get("logged_in"):
        render_login()
        return

    # Inject CSS EVERY rerun so font-size + theme changes take effect immediately
    inject_css()

    # Sidebar (left nav)
    render_sidebar()

    # Slim topbar inside main content
    render_main_topbar()

    # Eye-care banner
    if st.session_state.get("theme") == "eye":
        th = get_theme()
        st.markdown(
            f'<div style="background:rgba(90,180,120,0.10);border:1px solid rgba(90,180,120,0.20);'
            f'border-radius:9px;padding:8px 14px;font-size:12px;color:#8ab898;'
            f'margin-bottom:12px;display:flex;align-items:center;gap:8px">'
            f'🍃 {t("eye_banner")}</div>',
            unsafe_allow_html=True,
        )

    # Expiry warning
    try:
        exp = datetime.strptime(
            st.session_state.get("expiry_date", "2099-12-31"), "%Y-%m-%d").date()
        days_left = (exp - datetime.now().date()).days
        if 0 < days_left <= 7 and st.session_state.get("role") == "pro":
            th = get_theme()
            st.markdown(
                f'<div style="background:{th["orange"]}15;border:1px solid {th["orange"]}30;'
                f'border-radius:9px;padding:8px 14px;font-size:12px;color:{th["orange"]};'
                f'margin-bottom:12px">⚠️ {t("expiry_warn").format(days_left)}</div>',
                unsafe_allow_html=True,
            )
    except Exception:
        pass

    # Tab navigation
    tabs_config = [
        ("global",    t("nav_global"),    "📊"),
        ("watchlist", t("nav_watchlist"), "⭐"),
        ("ai",        t("nav_ai"),        "🤖"),
        ("portfolio", t("nav_portfolio"), "💼"),
        ("journal",   t("nav_journal"),   "📓"),
        ("learn",     t("nav_learn"),     "📚"),
        ("settings",  t("nav_settings"),  "⚙️"),
    ]
    if st.session_state.get("role") == "admin":
        tabs_config.append(("admin", t("nav_admin"), "👑"))

    tab_labels  = [f"{cfg[2]} {cfg[1]}" for cfg in tabs_config]
    tab_objects = st.tabs(tab_labels)

    with tab_objects[0]: tab_global_market()
    with tab_objects[1]: tab_watchlist()
    with tab_objects[2]: tab_ai()
    with tab_objects[3]: tab_portfolio()
    with tab_objects[4]: tab_journal()
    with tab_objects[5]: tab_learn()
    with tab_objects[6]: tab_settings()
    if st.session_state.get("role") == "admin" and len(tab_objects) > 7:
        with tab_objects[7]: tab_admin()

    th = get_theme()
    st.markdown(
        f'<div style="text-align:center;color:{th["text3"]};font-size:11px;'
        f'margin-top:24px;padding-bottom:16px">'
        f'數據僅供參考，不構成投資建議 · MarketIQ v1.1</div>',
        unsafe_allow_html=True,
    )




# ═══════════════════════════════════════════════════════════════════
#   TAB 1 — GLOBAL MARKET MONITOR
# ═══════════════════════════════════════════════════════════════════
def tab_global_market():
    th = get_theme()
    with st.spinner(t('loading')):
        kpi = fetch_kpi_data()


        kpi_cols = st.columns(4)
        kpi_configs = [
            ("sp500", t("sp500"), "green", t("today")),
            ("nasdaq", t("nasdaq"), "blue", t("today")),
            ("vix", t("vix"), "orange", t("low_vol")),
            ("gold", t("gold"), "purple", t("flat")),
        ]
        for col, (key, label, color, note) in zip(kpi_cols, kpi_configs):
            with col:
                d = kpi.get(key)
                if d:
                    val_str = fmt_num(d["value"], decimals=1 if key in ("vix", "gold") else 0)
                    if key in ("sp500", "nasdaq"):
                        val_str = fmt_num(d["value"], 0)
                    st.markdown(
                        render_kpi_card(label, val_str, d["change"], color, d["spark"], note),
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        render_kpi_card(label, "—", 0, color, [], note),
                        unsafe_allow_html=True
                    )

        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

        # ── MID ROW: Sector Chart + Heatmap ──
        mid_col1, mid_col2 = st.columns([1.7, 1])

        sector_data = fetch_sector_data("1m")

        with mid_col1:
            st.markdown(f"""
            <div class="ds-card">
              <div class="card-hd">
                <div>
                  <div class="card-title">{t('sector_compare')}</div>
                  <div class="card-sub">{t('sector_sub')}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Plotly bar chart
            sorted_sectors = sorted(sector_data.items(), key=lambda x: x[1], reverse=True)
            names = [s[0] for s in sorted_sectors]
            values = [s[1] for s in sorted_sectors]
            colors = [th["green"] if v >= 0 else th["red"] for v in values]

            fig = go.Figure(go.Bar(
                x=names, y=values,
                marker_color=colors,
                marker_line_color=colors,
                marker_line_width=1.5,
                text=[fmt_pct(v, 1) for v in values],
                textposition="outside",
                textfont=dict(size=10, color=th["text2"], family="Inter"),
            ))
            fig.update_layout(
                paper_bgcolor=th["card"],
                plot_bgcolor=th["card"],
                height=200,
                margin=dict(l=10, r=10, t=10, b=40),
                showlegend=False,
                xaxis=dict(
                    showgrid=False,
                    tickfont=dict(size=10, color=th["chart_tick"], family="Inter"),
                    tickangle=-30,
                ),
                yaxis=dict(
                    gridcolor=th["chart_grid"],
                    tickfont=dict(size=10, color=th["chart_tick"], family="Inter"),
                    ticksuffix="%",
                    zeroline=True,
                    zerolinecolor=th["border"],
                ),
                font=dict(family="Noto Sans HK, Inter"),
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with mid_col2:
            # Sort sectors by value descending for heatmap
            sorted_for_hm = sorted(sector_data.items(), key=lambda x: x[1], reverse=True)
            max_abs = max(abs(v) for _, v in sorted_for_hm) if sorted_for_hm else 1

            st.markdown(
                f'<div class="ds-card"><div class="card-hd">'
                f'<div class="card-title">{t("sector_heatmap")}</div></div>'
                f'<div class="hm-grid">',
                unsafe_allow_html=True,
            )

            for name, val in sorted_for_hm[:8]:
                pct_w = round(abs(val) / max_abs * 100, 1)
                bar_col = th["green"] if val >= 0 else th["red"]
                txt_col = th["green"] if val >= 0 else th["red"]
                val_str = fmt_pct(val, 1)
                st.markdown(
                    f'<div class="hm-row">'
                    f'<span class="hm-name">{name}</span>'
                    f'<div class="hm-bar-w">'
                    f'<div class="hm-bar" style="width:{pct_w}%;background:{bar_col}"></div>'
                    f'</div>'
                    f'<span class="hm-val" style="color:{txt_col}">{val_str}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            st.markdown('</div></div>', unsafe_allow_html=True)

        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

        # ── BOTTOM ROW: Watchlist + Regime + VIX ──
        bot_col1, bot_col2, bot_col3 = st.columns(3)

        # Default watchlist
        default_watchlist = ["TSLA", "NVDA", "AAPL", "META", "AMZN"]
        signals = fetch_watchlist_signals(default_watchlist)

        with bot_col1:
            sig_parts = []
            for s in signals:
                sc = s["score"]
                if sc >= 70:
                    badge_cls = "b-buy"
                    badge_txt = t("buy")
                    dot_color = th["green"]
                    sc_color = th["green"]
                    glow = f"box-shadow:0 0 5px {th['green']}"
                elif sc >= 45:
                    badge_cls = "b-watch"
                    badge_txt = t("watch")
                    dot_color = th["orange"]
                    sc_color = th["orange"]
                    glow = ""
                else:
                    badge_cls = "b-avoid"
                    badge_txt = t("avoid")
                    dot_color = th["red"]
                    sc_color = th["red"]
                    glow = f"box-shadow:0 0 5px {th['red']}"

                price_str = f"{s['price']:.2f}"
                sig_parts.append(
                    f'<div class="si-row">'
                    f'<div class="si-l">'
                    f'<span class="si-dot" style="background:{dot_color};{glow}"></span>'
                    f'<span class="si-tk">{s["ticker"]}</span>'
                    f'<span class="si-pr">${price_str}</span>'
                    f'</div>'
                    f'<div class="si-r">'
                    f'<span class="si-sc" style="color:{sc_color}">{sc}</span>'
                    f'<span class="badge {badge_cls}">{badge_txt}</span>'
                    f'</div>'
                    f'</div>'
                )
            sig_inline = "".join(sig_parts)
            wl_title = t("watchlist_signals")
            entry_lbl = t("entry_score")
            st.markdown(
                f'<div class="ds-card">'
                f'<div class="card-hd">'
                f'<div class="card-title">{wl_title}</div>'
                f'<span class="card-pill">{entry_lbl}</span>'
                f'</div>'
                f'{sig_inline}'
                f'</div>',
                unsafe_allow_html=True,
            )

        with bot_col2:
            regime = compute_market_regime()
            if regime:
                regime_label = t(regime["regime"])
                regime_color = {"green": th["green"], "red": th["red"],
                              "orange": th["orange"], "blue": th["blue"]}.get(regime["color"], th["green"])

                mom_v = regime["momentum"]
                bre_v = regime["breadth"]
                sen_v = regime["sentiment"]
                vol_v = regime["volatility"]
                vix_v = f"{regime['vix']:.1f}"
                reg_title  = t("market_regime")
                cur_state  = t("current_state")
                mom_lbl    = t("momentum")
                bre_lbl    = t("breadth")
                sen_lbl    = t("sentiment")
                vol_lbl    = t("volatility")
                ai_lbl     = t("ai_advice")
                ai_txt     = t("ai_advice_text")

                st.markdown(
                    f'<div class="ds-card">'
                    f'<div class="card-hd"><div class="card-title">{reg_title}</div></div>'
                    f'<div class="regime-state-lbl">{cur_state}</div>'
                    f'<div class="regime-val" style="color:{regime_color}">{regime_label}</div>'
                    f'<div class="reg-bar">'
                    f'<div class="reg-bar-hd"><span>{mom_lbl}</span>'
                    f'<span style="color:{th["green"]}">{mom_v} / 100</span></div>'
                    f'<div class="reg-bar-track">'
                    f'<div class="reg-bar-fill" style="width:{mom_v}%;background:{th["green"]}"></div>'
                    f'</div></div>'
                    f'<div class="reg-bar">'
                    f'<div class="reg-bar-hd"><span>{bre_lbl}</span>'
                    f'<span style="color:{th["blue"]}">{bre_v} / 100</span></div>'
                    f'<div class="reg-bar-track">'
                    f'<div class="reg-bar-fill" style="width:{bre_v}%;background:{th["blue"]}"></div>'
                    f'</div></div>'
                    f'<div class="reg-bar">'
                    f'<div class="reg-bar-hd"><span>{sen_lbl}</span>'
                    f'<span style="color:{th["orange"]}">{sen_v} / 100</span></div>'
                    f'<div class="reg-bar-track">'
                    f'<div class="reg-bar-fill" style="width:{sen_v}%;background:{th["orange"]}"></div>'
                    f'</div></div>'
                    f'<div class="reg-bar">'
                    f'<div class="reg-bar-hd"><span>{vol_lbl}</span>'
                    f'<span style="color:{th["green"]}">VIX {vix_v}</span></div>'
                    f'<div class="reg-bar-track">'
                    f'<div class="reg-bar-fill" style="width:{vol_v}%;background:{th["green"]}"></div>'
                    f'</div></div>'
                    f'<div class="ai-tip">'
                    f'<div class="ai-tip-l">{ai_lbl}</div>'
                    f'<div class="ai-tip-t">{ai_txt}</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        with bot_col3:
            vix_term = fetch_vix_term()
            vix_9d = vix_term.get("9D")
            vix_spot = vix_term.get("VIX")
            vix_3m = vix_term.get("3M")
            vix_6m = vix_term.get("6M")

            vix_vals = [v or 20 for v in [vix_9d, vix_spot, vix_3m, vix_6m]]
            max_v = max(vix_vals) if vix_vals else 30
            bar_heights = [(v / max_v * 100) if max_v else 0 for v in vix_vals]

            # Determine contango or backwardation
            is_contango = (vix_6m or 0) > (vix_spot or 0)
            contango_text = t("contango_text") if is_contango else t("backwardation_text")

            bar_colors = [th["blue"], th["blue"], "#8880e8", th["purple"]]
            labels = ["9D", "VIX", "3M", "6M"]

            # Build bars HTML inline - avoid variable embedding issue
            bars_parts = []
            for h, c, lbl in zip(bar_heights, bar_colors, labels):
                h_r = round(h, 1)
                bars_parts.append(
                    f'<div class="vix-bar-c">'
                    f'<div class="vix-bar" style="height:{h_r}%;background:{c}"></div>'
                    f'<div class="vix-bar-l">{lbl}</div>'
                    f'</div>'
                )
            bars_inline = "".join(bars_parts)

            row_data = [
                ("VIX 9D", vix_9d, th["green"] if vix_9d and vix_9d < 18 else th["text1"]),
                (t("vix_spot"), vix_spot, th["orange"] if vix_spot and vix_spot > 18 else th["text1"]),
                ("VIX 3M", vix_3m, th["text1"]),
                ("VIX 6M", vix_6m, th["text1"]),
            ]
            rows_parts = []
            for label, val, color in row_data:
                val_str = f"{val:.1f}" if val else "—"
                rows_parts.append(
                    f'<div class="vix-row">'
                    f'<span class="vrt">{label}</span>'
                    f'<span class="vrv" style="color:{color}">{val_str}</span>'
                    f'</div>'
                )
            rows_inline = "".join(rows_parts)

            vix_title = t("vix_term")
            st.markdown(
                f'<div class="ds-card">'
                f'<div class="card-hd"><div class="card-title">{vix_title}</div></div>'
                f'<div class="vix-curve">{bars_inline}</div>'
                f'<div>{rows_inline}</div>'
                f'<div class="ctag">{contango_text}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )



# ═══════════════════════════════════════════════════════════════════
#   DATA HELPERS FOR ALL TABS
# ═══════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def fetch_ticker_full(sym: str):
    try:
        df = yf.download(sym, period="1y", interval="1d", progress=False, auto_adjust=True)
        if df.empty or len(df) < 10:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        close = df["Close"].dropna()
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        latest = float(close.iloc[-1])
        prev   = float(close.iloc[-2])

        def _back(n):
            idx = max(0, len(close) - n)
            return float(close.iloc[idx])

        d1d = (latest - prev) / prev * 100
        d1m = (latest / _back(22) - 1) * 100 if len(close) >= 22 else 0
        d1y = (latest / _back(252) - 1) * 100 if len(close) >= 252 else 0
        ytd = (latest / _back(75) - 1) * 100 if len(close) >= 75 else 0

        hi  = df["High"].dropna()
        lo  = df["Low"].dropna()
        if isinstance(hi, pd.DataFrame): hi = hi.iloc[:, 0]
        if isinstance(lo, pd.DataFrame): lo = lo.iloc[:, 0]
        atr = float((hi - lo).rolling(14).mean().iloc[-1])
        atr_pct = atr / latest * 100

        delta = close.diff()
        gain  = delta.where(delta > 0, 0).ewm(alpha=1/14, adjust=False).mean()
        loss  = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
        rsi_v = float(100 - 100 / (1 + gain.iloc[-1] / max(loss.iloc[-1], 1e-9)))

        ema20 = float(close.ewm(span=20).mean().iloc[-1])
        ema50 = float(close.ewm(span=50).mean().iloc[-1]) if len(close) >= 50 else ema20

        hi52  = float(hi.tail(252).max())
        lo52  = float(lo.tail(252).min())
        pos52 = (latest - lo52) / (hi52 - lo52) * 100 if hi52 != lo52 else 50

        trend = 35 if latest > ema20 > ema50 else (20 if latest > ema20 else 5)
        mom   = (30 if 50 < rsi_v < 70 else 20 if 40 < rsi_v <= 50 else
                 25 if 70 <= rsi_v < 80 else 10)
        vol_s = 35 if atr_pct < 2 else (25 if atr_pct < 4 else 15)
        score = min(100, max(0, trend + mom + vol_s))
        label = "buy" if score >= 70 else ("watch" if score >= 45 else "avoid")

        return {
            "sym": sym, "price": latest,
            "1d": d1d, "1m": d1m, "1y": d1y, "ytd": ytd,
            "atr_pct": round(atr_pct, 2),
            "rsi": round(rsi_v, 1),
            "ema20": round(ema20, 2), "ema50": round(ema50, 2),
            "hi52": round(hi52, 2), "lo52": round(lo52, 2),
            "pos52": round(pos52, 1),
            "score": score, "label": label,
            "history": close.tail(252).tolist(),
        }
    except Exception:
        return None


@st.cache_data(ttl=300, show_spinner=False)
def fetch_ohlcv_period(sym: str, period: str = "3mo") -> pd.DataFrame:
    try:
        df = yf.download(sym, period=period, interval="1d", progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return df.dropna()
    except Exception:
        return pd.DataFrame()


def make_candlestick_fig(df: pd.DataFrame, sym: str, height: int = 320):
    from plotly.subplots import make_subplots
    th = get_theme()
    if df.empty:
        return go.Figure()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.72, 0.28], vertical_spacing=0.03)
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        increasing_line_color=th["green"], increasing_fillcolor=th["green"],
        decreasing_line_color=th["red"],   decreasing_fillcolor=th["red"],
        name=sym, line_width=1,
    ), row=1, col=1)
    if len(df) >= 20:
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"].ewm(span=20).mean(),
            line=dict(color=th["orange"], width=1.5), name="EMA20"), row=1, col=1)
    if len(df) >= 50:
        fig.add_trace(go.Scatter(x=df.index, y=df["Close"].ewm(span=50).mean(),
            line=dict(color=th["purple"], width=1.2, dash="dot"), name="EMA50"), row=1, col=1)
    if "Volume" in df.columns:
        vcols = [th["green"] if df["Close"].iloc[i] >= df["Open"].iloc[i]
                 else th["red"] for i in range(len(df))]
        fig.add_trace(go.Bar(x=df.index, y=df["Volume"],
            marker_color=vcols, showlegend=False), row=2, col=1)
    ax = dict(showgrid=True, gridcolor=th["chart_grid"],
              showline=False, tickfont=dict(size=10, color=th["chart_tick"]))
    fig.update_layout(
        paper_bgcolor=th["card"], plot_bgcolor=th["card"],
        height=height, margin=dict(l=8, r=8, t=8, b=8),
        xaxis=dict(**ax, rangeslider_visible=False), xaxis2=dict(**ax),
        yaxis=dict(**ax), yaxis2=dict(**ax, tickformat=".2s"),
        legend=dict(font=dict(size=10, color=th["chart_tick"]),
                    bgcolor="rgba(0,0,0,0)", orientation="h",
                    yanchor="bottom", y=1.01, xanchor="left", x=0),
        font=dict(family="Inter"), hovermode="x unified",
    )
    return fig


def make_perf_fig(histories: dict, height: int = 260):
    th = get_theme()
    palette = [th["green"], th["red"], th["blue"], th["orange"],
               th["purple"], "#00c9ff", "#ff8c00", "#e040fb"]
    fig = go.Figure()
    for i, (name, prices) in enumerate(histories.items()):
        if not prices or len(prices) < 2 or prices[0] == 0:
            continue
        norm = [p / prices[0] * 100 for p in prices]
        fig.add_trace(go.Scatter(y=norm, mode="lines", name=name,
            line=dict(color=palette[i % len(palette)], width=2),
            hovertemplate=f"{name}: %{{y:.1f}}<extra></extra>"))
    fig.add_hline(y=100, line_dash="dash", line_color=th["chart_tick"], line_width=0.8)
    ax = dict(showgrid=True, gridcolor=th["chart_grid"],
              showline=False, tickfont=dict(size=10, color=th["chart_tick"]))
    fig.update_layout(
        paper_bgcolor=th["card"], plot_bgcolor=th["card"],
        height=height, margin=dict(l=8, r=8, t=8, b=8),
        xaxis=dict(**ax, showticklabels=False), yaxis=dict(**ax),
        legend=dict(font=dict(size=10, color=th["chart_tick"]),
                    bgcolor="rgba(0,0,0,0)", orientation="h"),
        font=dict(family="Inter"), hovermode="x unified",
    )
    return fig


def make_bar_fig(names: list, vals: list, height: int = 240):
    th = get_theme()
    colors = [th["green"] if v >= 0 else th["red"] for v in vals]
    fig = go.Figure(go.Bar(
        x=names, y=vals, marker_color=colors, marker_cornerradius=4,
        text=[f"{v:+.1f}%" for v in vals], textposition="outside",
        textfont=dict(size=10, color=th["chart_tick"]),
    ))
    ax = dict(showgrid=True, gridcolor=th["chart_grid"],
              showline=False, tickfont=dict(size=10, color=th["chart_tick"]))
    fig.update_layout(
        paper_bgcolor=th["card"], plot_bgcolor=th["card"],
        height=height, margin=dict(l=8, r=8, t=8, b=55),
        xaxis=dict(showgrid=False, tickfont=dict(size=10, color=th["chart_tick"]), tickangle=35),
        yaxis=dict(**ax, ticksuffix="%",
                   zeroline=True, zerolinecolor=th["chart_tick"], zerolinewidth=0.5),
        showlegend=False, font=dict(family="Inter"),
    )
    return fig


def sec_title(txt: str) -> str:
    th = get_theme()
    return (f'<div style="font-size:14px;font-weight:600;color:{th["text1"]};'
            f'margin-bottom:12px">{txt}</div>')


def lock_msg() -> None:
    th = get_theme()
    st.markdown(
        f'<div style="text-align:center;padding:32px;background:{th["card2"]};'
        f'border-radius:12px;border:1px solid {th["border"]};margin:8px 0">'
        f'<div style="font-size:28px;margin-bottom:10px">🔒</div>'
        f'<div style="font-size:14px;color:{th["text2"]};margin-bottom:6px">Pro 專屬功能</div>'
        f'<div style="font-size:12px;color:{th["text3"]}">升級 Pro 解鎖全部功能</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def is_pro() -> bool:
    return st.session_state.get("role", "free") in ("pro", "admin")


def groq_call(prompt: str, sys_msg: str = "") -> str:
    import requests as _req
    try:
        key = st.secrets["groq"]["api_key"]
    except Exception:
        return "⚠️ 請在 Streamlit Secrets 設定 Groq API Key（groq.api_key）"
    lang = st.session_state.get("lang", "zh-hant")
    lang_inst = {"zh-hant": "請用繁體中文回答。",
                 "zh-hans": "请用简体中文回答。",
                 "en": "Please respond in English."}.get(lang, "請用繁體中文回答。")
    system = sys_msg or f"你是一位專業股票市場分析師。{lang_inst}"
    model = "llama-3.3-70b-versatile" if is_pro() else "llama-3.1-8b-instant"
    try:
        r = _req.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": model, "max_tokens": 1024, "temperature": 0.3,
                  "messages": [{"role": "system", "content": system},
                                {"role": "user", "content": prompt}]},
            timeout=30,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ AI 分析失敗: {str(e)[:120]}"


def send_telegram_msg(chat_id: str, text: str) -> bool:
    import requests as _req
    try:
        tok = st.secrets["telegram"]["bot_token"]
        r = _req.post(f"https://api.telegram.org/bot{tok}/sendMessage",
                      json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
                      timeout=10)
        return r.status_code == 200
    except Exception:
        return False


# ═══════════════════════════════════════════════════════════════════
#   TAB 2 — WATCHLIST ANALYSIS
# ═══════════════════════════════════════════════════════════════════
def tab_watchlist():
    th = get_theme()
    st.markdown(sec_title("⭐ " + t("nav_watchlist")), unsafe_allow_html=True)

    default_wl = st.session_state.get("wl_tickers", "TSLA, AAPL, NVDA, AMZN, META")
    wl_input = st.text_input(
        "輸入股票代碼（逗號分隔，支援美股/港股/A股/英股）",
        value=default_wl,
        placeholder="例如：TSLA, AAPL, NVDA, 0700.HK, 600519.SS",
        key="wl_text_input",
    )
    c1, c2, _ = st.columns([1, 1, 5])
    with c1:
        if st.button("🔍 查詢", key="wl_run", use_container_width=True):
            st.session_state["wl_tickers"] = wl_input
    with c2:
        if st.button("✖ 清除", key="wl_clear", use_container_width=True):
            st.session_state["wl_tickers"] = ""
            st.rerun()

    tickers_raw = [s.strip().upper() for s in
                   st.session_state.get("wl_tickers", default_wl).split(",") if s.strip()]
    if not is_pro() and len(tickers_raw) > 5:
        st.warning("🔒 免費版最多5隻，升級 Pro 解鎖無限")
        tickers_raw = tickers_raw[:5]
    if not tickers_raw:
        st.info("請輸入股票代碼後點擊查詢")
        return

    # Saved portfolios (Pro)
    if is_pro():
        with st.expander("組合儲存"):
            portfolios = st.session_state.get("portfolios", {})
            for pname, ptk in portfolios.items():
                pc1, pc2 = st.columns([4, 1])
                with pc1:
                    st.markdown(f'<span style="font-size:13px;color:{th["text1"]}">📁 <b>{pname}</b>: <span style="color:{th["text3"]}">{ptk}</span></span>', unsafe_allow_html=True)
                with pc2:
                    if st.button("載入", key=f"load_{pname}"):
                        st.session_state["wl_tickers"] = ptk; st.rerun()
            pn1, pn2 = st.columns([3, 1])
            with pn1:
                new_pname = st.text_input("組合名稱", key="new_pname", placeholder="如：科技組合")
            with pn2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾 儲存", key="save_pf"):
                    if new_pname and tickers_raw:
                        portfolios[new_pname] = ", ".join(tickers_raw)
                        st.session_state["portfolios"] = portfolios
                        st.success(f"已儲存「{new_pname}」")

    st.markdown("<br>", unsafe_allow_html=True)

    # Fetch
    with st.spinner("載入中..."):
        all_data = {tk: fetch_ticker_full(tk) for tk in tickers_raw}

    # Summary table
    show_all = is_pro()
    rows_html = ""
    for tk in tickers_raw:
        d = all_data.get(tk)
        if d:
            p  = fmt_num(d["price"], 2)
            c1c = "cell-up" if d["1d"] >= 0 else "cell-dn"
            cm  = "cell-up" if d["1m"] >= 0 else "cell-dn"
            cy  = "cell-up" if d.get("ytd", 0) >= 0 else "cell-dn"
            cy1 = "cell-up" if d.get("1y",  0) >= 0 else "cell-dn"
            sc_col = "#00c98a" if d["score"]>=70 else "#f0a030" if d["score"]>=45 else "#f05555"
            lbl_cls = "b-buy" if d["label"]=="buy" else "b-watch" if d["label"]=="watch" else "b-avoid"
            lbl_txt = {"buy": t("buy"), "watch": t("watch"), "avoid": t("avoid")}.get(d["label"], "—")
            rows_html += (
                f'<tr>'
                f'<td style="font-weight:700">{tk}</td>'
                f'<td style="font-family:Inter">${p}</td>'
                f'<td><span class="{c1c}">{fmt_pct(d["1d"])}</span></td>'
                f'<td><span class="{cm}">{fmt_pct(d["1m"])}</span></td>'
                f'<td><span class="{cy}">{fmt_pct(d.get("ytd")) if show_all else "🔒"}</span></td>'
                f'<td><span class="{cy1}">{fmt_pct(d.get("1y")) if show_all else "🔒"}</span></td>'
                f'<td style="font-family:Inter;font-weight:700;color:{sc_col}">{d["score"]}</td>'
                f'<td><span class="badge {lbl_cls}">{lbl_txt}</span></td>'
                f'</tr>'
            )
        else:
            rows_html += (f'<tr><td style="font-weight:700">{tk}</td>'
                          f'<td colspan="7" style="color:{th["text3"]}">數據加載失敗</td></tr>')

    st.markdown(
        f'<div class="ds-card" style="overflow-x:auto">'
        f'<table style="width:100%;border-collapse:collapse;font-size:13px">'
        f'<thead><tr style="border-bottom:2px solid {th["border"]}">'
        + "".join(f'<th style="padding:8px 10px;font-size:10px;color:{th["text3"]};text-transform:uppercase">{h}</th>'
                  for h in ["代碼", "現價", "1天", "1月", f'YTD{"" if show_all else " 🔒"}', f'1年{"" if show_all else " 🔒"}', "評分", "信號"])
        + f'</tr></thead><tbody>{rows_html}</tbody></table></div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    if not is_pro():
        lock_msg()
        return

    # K-line + 52W
    ka, kb = st.columns([1.4, 1], gap="medium")
    with ka:
        st.markdown(sec_title("K線圖"), unsafe_allow_html=True)
        sel = st.selectbox("", tickers_raw, key="wl_ksel", label_visibility="collapsed")
        kp  = st.radio("", ["1月","3月","6月","1年"], horizontal=True, key="wl_kp", label_visibility="collapsed")
        pm  = {"1月":"1mo","3月":"3mo","6月":"6mo","1年":"1y"}
        ohlcv = fetch_ohlcv_period(sel, pm[kp])
        st.plotly_chart(make_candlestick_fig(ohlcv, sel, 310),
                        use_container_width=True, config={"displayModeBar": False}, key="wl_kline")
    with kb:
        st.markdown(sec_title("52週高低位 + 指標"), unsafe_allow_html=True)
        for tk in tickers_raw:
            d = all_data.get(tk)
            if not d: continue
            prog = d["pos52"]
            bar_col = th["green"] if prog > 60 else th["orange"] if prog > 30 else th["red"]
            sc_col  = th["green"] if d["score"]>=70 else th["orange"] if d["score"]>=45 else th["red"]
            st.markdown(
                f'<div style="padding:10px 0;border-bottom:1px solid {th["border2"]}">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:5px">'
                f'<span style="font-size:14px;font-weight:700;color:{th["text1"]};font-family:Inter">{tk}</span>'
                f'<span style="font-size:13px;font-weight:800;color:{sc_col};font-family:Inter">評分 {d["score"]}</span>'
                f'</div>'
                f'<div style="display:flex;justify-content:space-between;font-size:10px;color:{th["text3"]};margin-bottom:3px">'
                f'<span>52W低 ${fmt_num(d["lo52"],2)}</span>'
                f'<span>當前 ${fmt_num(d["price"],2)} ({prog:.0f}%)</span>'
                f'<span>52W高 ${fmt_num(d["hi52"],2)}</span></div>'
                f'<div style="height:6px;background:{th["border"]};border-radius:3px;overflow:hidden">'
                f'<div style="width:{prog}%;height:100%;background:{bar_col};border-radius:3px"></div></div>'
                f'<div style="display:flex;gap:12px;margin-top:6px;font-size:11px;color:{th["text3"]}">'
                f'<span>RSI {d["rsi"]}</span><span>ATR {d["atr_pct"]:.1f}%</span>'
                f'<span>EMA20 {fmt_num(d["ema20"],2)}</span></div></div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(sec_title("績效對比（Normalize to 100）"), unsafe_allow_html=True)
    pf_p = st.radio("", ["1月","3月","1年"], horizontal=True, key="wl_pp", label_visibility="collapsed")
    pf_n = {"1月":22,"3月":63,"1年":252}[pf_p]
    histories = {tk: d["history"][-pf_n:] for tk in tickers_raw
                 if (d := all_data.get(tk)) and d and len(d["history"]) >= pf_n}
    st.plotly_chart(make_perf_fig(histories, 250), use_container_width=True,
                    config={"displayModeBar": False}, key="wl_perf")

    st.markdown(sec_title("表現柱狀圖"), unsafe_allow_html=True)
    pb_p = st.radio("", ["1天","1月","YTD","1年"], horizontal=True, key="wl_bp", label_visibility="collapsed")
    pb_k = {"1天":"1d","1月":"1m","YTD":"ytd","1年":"1y"}[pb_p]
    bar_names = [tk for tk in tickers_raw if all_data.get(tk) and all_data[tk].get(pb_k) is not None]
    bar_vals  = [round(all_data[tk][pb_k], 2) for tk in bar_names]
    if bar_names:
        st.plotly_chart(make_bar_fig(bar_names, bar_vals, 220), use_container_width=True,
                        config={"displayModeBar": False}, key="wl_bar")

    if len(tickers_raw) >= 2:
        st.markdown(sec_title("相關性熱力圖（3個月）"), unsafe_allow_html=True)
        try:
            raw_c = yf.download(tickers_raw, period="3mo", interval="1d", progress=False, auto_adjust=True)
            closes_c = (raw_c["Close"] if isinstance(raw_c.columns, pd.MultiIndex) else raw_c).dropna()
            corr_df = closes_c.pct_change().dropna().corr().round(2)
            th2 = get_theme()
            z = corr_df.values; labels = list(corr_df.columns)
            text_z = [[f"{z[i][j]:.2f}" for j in range(len(labels))] for i in range(len(labels))]
            cfig = go.Figure(go.Heatmap(z=z, x=labels, y=labels, text=text_z, texttemplate="%{text}",
                colorscale=[[0.0,th2["red"]],[0.5,th2["card"]],[1.0,th2["green"]]],
                zmid=0, zmin=-1, zmax=1, showscale=True,
                colorbar=dict(thickness=10, tickfont=dict(size=9, color=th2["chart_tick"])),
                textfont=dict(size=11)))
            cfig.update_layout(paper_bgcolor=th2["card"], plot_bgcolor=th2["card"],
                height=max(250, len(labels)*55), margin=dict(l=8,r=48,t=8,b=8),
                xaxis=dict(tickfont=dict(size=10,color=th2["chart_tick"])),
                yaxis=dict(tickfont=dict(size=10,color=th2["chart_tick"]),autorange="reversed"),
                font=dict(family="Inter"))
            st.plotly_chart(cfig, use_container_width=True, config={"displayModeBar": False}, key="wl_corr")
        except Exception:
            st.info("相關性計算需至少2隻股票")

    st.markdown(sec_title("ATR% 波幅排行（由低到高）"), unsafe_allow_html=True)
    atr_pairs = sorted([(tk, all_data[tk]["atr_pct"]) for tk in tickers_raw
                        if all_data.get(tk) and all_data[tk].get("atr_pct")], key=lambda x: x[1])
    for tk, atr_v in atr_pairs:
        atr_col = th["green"] if atr_v < 3 else th["orange"] if atr_v < 6 else th["red"]
        pct_bar = min(atr_v / 10 * 100, 100)
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid {th["border2"]}">'
            f'<span style="font-size:14px;font-weight:700;color:{th["text1"]};font-family:Inter;min-width:60px">{tk}</span>'
            f'<div style="flex:1;height:5px;background:{th["border"]};border-radius:3px;overflow:hidden">'
            f'<div style="width:{pct_bar}%;height:100%;background:{atr_col};border-radius:3px"></div></div>'
            f'<span style="font-size:13px;font-weight:700;color:{atr_col};font-family:Inter;min-width:50px;text-align:right">{atr_v:.2f}%</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════
#   TAB 3 — AI TRADING ASSISTANT
# ═══════════════════════════════════════════════════════════════════
def tab_ai():
    th = get_theme()
    st.markdown(sec_title("🤖 " + t("nav_ai")), unsafe_allow_html=True)
    if not is_pro():
        lock_msg()
        return

    role = st.session_state.get("role", "free")
    limit = 9999 if role == "admin" else 20
    used  = st.session_state.get("ai_calls_today", 0)
    pct   = min(used / limit * 100, 100) if limit < 9999 else 0

    st.markdown(
        f'<div style="background:{th["card"]};border:1px solid {th["border"]};'
        f'border-radius:11px;padding:12px 16px;margin-bottom:14px">'
        f'<div style="font-size:12px;color:{th["text3"]};margin-bottom:6px">'
        f'今日 AI 調用：{used} / {"∞" if limit==9999 else limit} · 明日重置</div>'
        f'<div style="height:5px;background:{th["bg2"]};border-radius:3px;overflow:hidden">'
        f'<div style="width:{pct}%;height:100%;background:{th["green"]};border-radius:3px"></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    ai_tabs = st.tabs(["📰 每日簡報", "🔭 三層漏斗", "📋 交易前檢查", "💡 AI 綜合建議"])

    with ai_tabs[0]:
        wl_tks = [s.strip().upper() for s in st.session_state.get("wl_tickers","TSLA,AAPL,NVDA").split(",") if s.strip()][:5]
        if st.button("📰 生成今日簡報", key="gen_brief"):
            if used >= limit:
                st.error("今日 AI 調用已達上限")
            else:
                with st.spinner("AI 分析中..."):
                    regime = compute_market_regime() or {}
                    sector_d = fetch_sector_data("1m")
                    top_names = [k for k,_ in sorted(sector_d.items(),key=lambda x:x[1],reverse=True)[:3]]
                    lang_n = {"zh-hant":"繁體中文","zh-hans":"简体中文","en":"English"}.get(st.session_state.get("lang","zh-hant"),"繁體中文")
                    prompt = f"為{st.session_state.get('region','UK')}地區投資者用{lang_n}生成每日市場簡報。\n市場：{t(regime.get('regime','neutral'))} VIX:{regime.get('vix',20):.1f}\n強勢板塊：{','.join(top_names)}\n關注股票：{','.join(wl_tks)}\n格式：📊市場概況(2句) 🔥重點機會(3點) ⚠️風險(2點) 💡今日建議(1句)"
                    st.session_state["briefing"] = groq_call(prompt)
                    st.session_state["ai_calls_today"] = used + 1
        if "briefing" in st.session_state:
            st.markdown(
                f'<div style="background:{th["card"]};border:1px solid {th["border"]};'
                f'border-radius:13px;padding:20px;line-height:1.8;font-size:14px;'
                f'color:{th["text1"]};white-space:pre-line">{st.session_state["briefing"]}</div>',
                unsafe_allow_html=True,
            )
            tg_id = st.text_input("Telegram Chat ID", key="brief_tg", placeholder="123456789")
            if st.button("📱 推送 Telegram", key="send_brief_tg") and tg_id:
                ok = send_telegram_msg(tg_id, f"*MarketIQ 每日簡報*\n\n{st.session_state['briefing']}\n\n_僅供參考_")
                st.success("✅ 已推送" if ok else "❌ 推送失敗")

    with ai_tabs[1]:
        regime = compute_market_regime() or {}
        overall = regime.get("overall", 50)
        reg_color = th["green"] if overall >= 65 else th["orange"] if overall >= 40 else th["red"]
        st.markdown(
            f'<div style="background:{th["card"]};border:1px solid {th["border"]};border-radius:13px;padding:16px;margin-bottom:10px">'
            f'<div style="font-size:11px;color:{th["text3"]};font-weight:600;text-transform:uppercase;letter-spacing:.6px;margin-bottom:8px">第一層：大環境評分</div>'
            f'<div style="display:flex;align-items:baseline;gap:8px">'
            f'<span style="font-size:42px;font-weight:900;font-family:Inter;color:{reg_color}">{overall}</span>'
            f'<span style="font-size:13px;color:{th["text2"]}">/ 100 · {t(regime.get("regime","neutral"))}</span></div></div>',
            unsafe_allow_html=True,
        )
        sector_d2 = fetch_sector_data("1m")
        sorted_s2 = sorted(sector_d2.items(), key=lambda x: x[1], reverse=True)
        st.markdown(
            f'<div style="background:{th["card"]};border:1px solid {th["border"]};border-radius:13px;padding:16px;margin-bottom:10px">'
            f'<div style="font-size:11px;color:{th["text3"]};font-weight:600;text-transform:uppercase;letter-spacing:.6px;margin-bottom:10px">第二層：強弱板塊</div>'
            f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">',
            unsafe_allow_html=True,
        )
        for name, val in sorted_s2[:3]:
            st.markdown(f'<div style="padding:8px 12px;background:{th["nav_active_bg"]};border-radius:8px;border:1px solid {th["green"]}33"><div style="font-size:12px;color:{th["green"]}">{name}</div><div style="font-size:14px;font-weight:700;color:{th["green"]};font-family:Inter">{fmt_pct(val)}</div></div>', unsafe_allow_html=True)
        for name, val in sorted_s2[-3:]:
            st.markdown(f'<div style="padding:8px 12px;background:{th["red"]}15;border-radius:8px;border:1px solid {th["red"]}33"><div style="font-size:12px;color:{th["red"]}">{name}</div><div style="font-size:14px;font-weight:700;color:{th["red"]};font-family:Inter">{fmt_pct(val)}</div></div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)
        wl_tks3 = [s.strip().upper() for s in st.session_state.get("wl_tickers","TSLA,NVDA,AAPL").split(",") if s.strip()][:5]
        sigs3 = sorted(fetch_watchlist_signals(wl_tks3), key=lambda x: x["score"], reverse=True)
        st.markdown(f'<div style="background:{th["card"]};border:1px solid {th["border"]};border-radius:13px;padding:16px"><div style="font-size:11px;color:{th["text3"]};font-weight:600;text-transform:uppercase;letter-spacing:.6px;margin-bottom:10px">第三層：個股機會</div>', unsafe_allow_html=True)
        for s in sigs3[:3]:
            sc = s["score"]
            sc_col = th["green"] if sc>=70 else th["orange"] if sc>=45 else th["red"]
            lbl_cls = "b-buy" if sc>=70 else "b-watch" if sc>=45 else "b-avoid"
            lbl_txt = t("buy") if sc>=70 else t("watch") if sc>=45 else t("avoid")
            st.markdown(f'<div style="display:flex;align-items:center;justify-content:space-between;padding:9px 0;border-bottom:1px solid {th["border2"]}"><span style="font-size:14px;font-weight:700;color:{th["text1"]};font-family:Inter">{s["ticker"]}</span><div style="display:flex;align-items:center;gap:8px"><span style="font-size:15px;font-weight:800;color:{sc_col};font-family:Inter">{sc}/100</span><span class="badge {lbl_cls}">{lbl_txt}</span></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with ai_tabs[2]:
        st.markdown(f'<div style="font-size:13px;color:{th["text2"]};margin-bottom:16px;line-height:1.6">入市前冷靜回答以下5個問題，防止衝動交易。</div>', unsafe_allow_html=True)
        q1 = st.text_area("1️⃣ 這次交易的理由？", key="cl_q1", height=70)
        q2 = st.text_input("2️⃣ 止損位 ($)", key="cl_q2", placeholder="如：$248.00")
        q3 = st.text_input("3️⃣ 最大虧損（帳戶%）", key="cl_q3", placeholder="如：1.5%")
        q4 = st.text_input("4️⃣ 目標位 ($)", key="cl_q4", placeholder="如：$280.00")
        q5 = st.radio("5️⃣ 市場環境支持方向嗎？", ["✅ 支持", "⚠️ 中性", "❌ 不支持"], key="cl_q5")
        if st.button("📋 完成檢查", key="cl_submit", disabled=not all([q1.strip(),q2.strip(),q3.strip(),q4.strip()])):
            if used >= limit:
                st.error("今日 AI 調用已達上限")
            else:
                lang_n2 = {"zh-hant":"繁體中文","zh-hans":"简体中文","en":"English"}.get(st.session_state.get("lang","zh-hant"),"繁體中文")
                p2 = f"用{lang_n2}，30字以內回答：以下交易是否合適入市？\n理由:{q1} 止損:{q2} 最大虧損:{q3} 目標:{q4} 市場:{q5}"
                with st.spinner("分析中..."):
                    res2 = groq_call(p2)
                    st.session_state["ai_calls_today"] = used + 1
                st.success(f"**AI 建議**：{res2}")

    with ai_tabs[3]:
        if st.button("🤖 生成 AI 綜合投資建議", key="gen_full_ai"):
            if used >= limit:
                st.error("今日 AI 調用已達上限")
            else:
                with st.spinner("AI 深度分析中（10-20秒）..."):
                    reg3 = compute_market_regime() or {}
                    sd3  = fetch_sector_data("1m")
                    top3 = sorted(sd3.items(),key=lambda x:x[1],reverse=True)[:3]
                    wk3  = sorted(sd3.items(),key=lambda x:x[1])[:3]
                    wl3  = [s.strip().upper() for s in st.session_state.get("wl_tickers","TSLA,NVDA,AAPL").split(",") if s.strip()][:5]
                    sigs3b = fetch_watchlist_signals(wl3)
                    sig_str = "\n".join(f"  {s['ticker']}: 評分{s['score']} ${s['price']:.2f}" for s in sigs3b)
                    lang_n3 = {"zh-hant":"繁體中文","zh-hans":"简体中文","en":"English"}.get(st.session_state.get("lang","zh-hant"),"繁體中文")
                    p3 = f"用{lang_n3}提供完整投資建議報告。\n大環境：{t(reg3.get('regime','neutral'))} VIX:{reg3.get('vix',20):.1f} 動能:{reg3.get('momentum',50)}/100\n強勢板塊：{','.join(k+' '+fmt_pct(v) for k,v in top3)}\n弱勢板塊：{','.join(k+' '+fmt_pct(v) for k,v in wk3)}\n自選股票信號：\n{sig_str}\n請提供：1.市場總結(3句) 2.推薦板塊及理由 3.個股機會排名 4.風險提示(3點) 5.整體操作策略"
                    st.session_state["full_ai"] = groq_call(p3)
                    st.session_state["ai_calls_today"] = used + 1
        if "full_ai" in st.session_state:
            st.markdown(f'<div style="background:{th["card"]};border:1px solid {th["border"]};border-radius:13px;padding:20px;line-height:1.85;font-size:14px;color:{th["text1"]};white-space:pre-line">{st.session_state["full_ai"]}</div>', unsafe_allow_html=True)
            tg2 = st.text_input("Telegram Chat ID", key="full_ai_tg", placeholder="123456789")
            if st.button("📱 推送 Telegram", key="send_full_tg") and tg2:
                ok2 = send_telegram_msg(tg2, f"*MarketIQ AI 投資建議*\n\n{st.session_state['full_ai']}\n\n_僅供參考_")
                st.success("✅ 已推送" if ok2 else "❌ 推送失敗")


# ═══════════════════════════════════════════════════════════════════
#   TAB 4 — PORTFOLIO
# ═══════════════════════════════════════════════════════════════════
def tab_portfolio():
    th = get_theme()
    st.markdown(sec_title("💼 " + t("nav_portfolio")), unsafe_allow_html=True)
    if not is_pro():
        lock_msg()
        return

    ptabs = st.tabs(["📊 持倉追蹤", "📐 Kelly 計算器", "🎯 目標追蹤"])

    with ptabs[0]:
        positions = st.session_state.get("positions", [])
        with st.expander("新增持倉"):
            pc1,pc2,pc3,pc4 = st.columns(4)
            with pc1: new_tk  = st.text_input("代碼", key="pos_tk", placeholder="TSLA")
            with pc2: new_qty = st.number_input("股數", min_value=1, value=100, key="pos_qty")
            with pc3: new_cost = st.number_input("成本($)", min_value=0.01, value=200.0, step=0.01, key="pos_cost")
            with pc4: new_dt = st.date_input("日期", key="pos_dt")
            if st.button("新增", key="add_pos"):
                if new_tk.strip():
                    if "positions" not in st.session_state: st.session_state["positions"] = []
                    st.session_state["positions"].append({"ticker":new_tk.strip().upper(),"qty":new_qty,"cost":new_cost,"date":str(new_dt)})
                    st.rerun()
        if positions:
            rows2 = ""; total_v = total_c = 0
            for pos in positions:
                d2 = fetch_ticker_full(pos["ticker"])
                price2 = d2["price"] if d2 else pos["cost"]
                cv = price2*pos["qty"]; cc = pos["cost"]*pos["qty"]
                pnl2 = cv-cc; pnl_p = pnl2/cc*100 if cc else 0
                total_v+=cv; total_c+=cc
                pc2 = "cell-up" if pnl2>=0 else "cell-dn"
                rows2 += f'<tr><td style="font-weight:700">{pos["ticker"]}</td><td style="font-family:Inter">{pos["qty"]:,}</td><td style="font-family:Inter">${pos["cost"]:.2f}</td><td style="font-family:Inter">${price2:.2f}</td><td style="font-family:Inter">${cv:,.0f}</td><td><span class="{pc2}">${pnl2:+,.0f} ({pnl_p:+.1f}%)</span></td></tr>'
            total_pnl2 = total_v-total_c; total_pp = total_pnl2/total_c*100 if total_c else 0
            tc = "cell-up" if total_pnl2>=0 else "cell-dn"
            st.markdown(f'<div class="ds-card" style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:13px"><thead><tr style="border-bottom:2px solid {th["border"]}">'+"".join(f'<th style="padding:7px 10px;font-size:10px;color:{th["text3"]}">{h}</th>' for h in ["代碼","股數","成本","現價","市值","盈虧"])+f'</tr></thead><tbody>{rows2}</tbody><tfoot><tr style="border-top:2px solid {th["border"]}"><td colspan="4" style="padding:7px 10px;font-weight:700;color:{th["text1"]}">總計</td><td style="padding:7px 10px;font-weight:700;font-family:Inter;color:{th["text1"]}">${total_v:,.0f}</td><td style="padding:7px 10px"><span class="{tc}" style="font-weight:700">${total_pnl2:+,.0f} ({total_pp:+.1f}%)</span></td></tr></tfoot></table></div>', unsafe_allow_html=True)
            m1,m2,m3 = st.columns(3)
            m1.metric("總市值",f"${total_v:,.0f}"); m2.metric("總成本",f"${total_c:,.0f}"); m3.metric("總盈虧",f"${total_pnl2:+,.0f}",f"{total_pp:+.1f}%")
        else:
            st.info("尚未加入持倉")

    with ptabs[1]:
        st.markdown(f'<div style="font-size:13px;color:{th["text2"]};margin-bottom:14px;line-height:1.6">Kelly % = (勝率 × 盈虧比 - 敗率) / 盈虧比。建議使用半 Kelly（保守版）。</div>', unsafe_allow_html=True)
        ka,kb = st.columns(2)
        with ka: wr = st.slider("歷史勝率 (%)", 10, 90, 55, key="kelly_wr")
        with kb: ratio = st.slider("平均盈虧比", 0.5, 5.0, 2.0, step=0.1, key="kelly_ratio")
        kelly = (wr/100*ratio-(1-wr/100))/ratio
        half_k = kelly/2
        kc = th["green"] if kelly>0 else th["red"]
        st.markdown(f'<div style="background:{th["card"]};border:1px solid {th["border"]};border-radius:13px;padding:24px;text-align:center"><div style="font-size:50px;font-weight:900;color:{kc};font-family:Inter;letter-spacing:-2px">{max(0,kelly*100):.1f}%</div><div style="font-size:13px;color:{th["text2"]};margin-top:8px">Kelly 建議倉位 · 半 Kelly（保守）: {max(0,half_k*100):.1f}%</div><div style="font-size:12px;color:{th["text3"]};margin-top:6px">勝率 {wr}% · 盈虧比 {ratio:.1f}x · {"⚠️ 不建議交易" if kelly<=0 else "✅ 正期望值"}</div></div>', unsafe_allow_html=True)

    with ptabs[2]:
        target = st.number_input("每月目標盈利 ($)", value=3000, step=100, key="goal_t")
        current_pnl = st.number_input("本月已實現盈利 ($)", value=0, step=100, key="goal_c")
        pct_done = min(current_pnl/target*100,100) if target>0 else 0
        bc = th["green"] if pct_done>=100 else th["blue"] if pct_done>=60 else th["orange"]
        st.markdown(f'<div style="background:{th["card"]};border:1px solid {th["border"]};border-radius:13px;padding:24px;text-align:center"><div style="font-size:13px;color:{th["text3"]};margin-bottom:6px">本月目標進度</div><div style="font-size:48px;font-weight:900;color:{bc};font-family:Inter;letter-spacing:-2px">{pct_done:.1f}%</div><div style="font-size:13px;color:{th["text2"]};margin:8px 0 18px">${current_pnl:,.0f} / ${target:,.0f}</div><div style="height:10px;background:{th["bg2"]};border-radius:5px;overflow:hidden"><div style="width:{pct_done}%;height:100%;background:{bc};border-radius:5px"></div></div>{"<div style='font-size:20px;margin-top:14px'>🎉 目標達成！</div>" if pct_done>=100 else ""}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#   TAB 5 — TRADE JOURNAL
# ═══════════════════════════════════════════════════════════════════
def tab_journal():
    th = get_theme()
    st.markdown(sec_title("📓 " + t("nav_journal")), unsafe_allow_html=True)
    if not is_pro():
        lock_msg()
        return

    jtabs = st.tabs(["📝 記錄交易", "📊 勝率統計", "🤖 AI 教練"])

    with jtabs[0]:
        with st.expander("記錄新交易", expanded=True):
            j1,j2,j3 = st.columns(3)
            with j1:
                jtk = st.text_input("代碼", key="j_tk", placeholder="TSLA")
                jdir = st.radio("方向", ["做多 Long","做空 Short"], key="j_dir")
            with j2:
                jentry = st.number_input("入場價($)", value=200.0, step=0.01, key="j_entry")
                jexit  = st.number_input("出場價($)", value=220.0, step=0.01, key="j_exit")
            with j3:
                jqty = st.number_input("股數", min_value=1, value=100, key="j_qty")
                jemo = st.selectbox("情緒", ["😌 冷靜","😰 緊張","😤 貪婪","😱 恐懼"], key="j_emo")
            j_in  = st.text_input("入場理由", key="j_in",  placeholder="如：EMA金叉+RSI<60")
            j_out = st.text_input("出場理由", key="j_out", placeholder="如：達到目標位")
            if st.button("✅ 記錄", key="add_trade"):
                if jtk.strip():
                    mult = 1 if "Long" in jdir else -1
                    pnl = (jexit-jentry)*jqty*mult
                    if "journal" not in st.session_state: st.session_state["journal"] = []
                    st.session_state["journal"].append({"date":datetime.now().strftime("%Y-%m-%d"),"ticker":jtk.strip().upper(),"direction":jdir,"entry":jentry,"exit":jexit,"qty":jqty,"pnl":pnl,"emotion":jemo,"reason_in":j_in,"reason_out":j_out})
                    st.success(f"已記錄 {jtk.upper()} · 盈虧 ${pnl:+,.2f}")
        journal = st.session_state.get("journal", [])
        if journal:
            jrows = "".join(f'<tr><td>{x["date"]}</td><td style="font-weight:700">{x["ticker"]}</td><td style="font-size:11px">{x["direction"]}</td><td style="font-family:Inter">${x["entry"]:.2f}</td><td style="font-family:Inter">${x["exit"]:.2f}</td><td style="font-family:Inter">{x["qty"]:,}</td><td><span class="{"cell-up" if x["pnl"]>=0 else "cell-dn"}">${x["pnl"]:+,.0f}</span></td><td style="font-size:12px">{x["emotion"]}</td></tr>' for x in reversed(journal[-20:]))
            st.markdown(f'<div class="ds-card" style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:13px"><thead><tr style="border-bottom:2px solid {th["border"]}">'+"".join(f'<th style="padding:7px 10px;font-size:10px;color:{th["text3"]}">{h}</th>' for h in ["日期","代碼","方向","入場","出場","股數","盈虧","情緒"])+f'</tr></thead><tbody>{jrows}</tbody></table></div>', unsafe_allow_html=True)

    with jtabs[1]:
        journal = st.session_state.get("journal", [])
        if not journal:
            st.info("尚無交易記錄")
        else:
            wins = [x for x in journal if x["pnl"]>0]; losses = [x for x in journal if x["pnl"]<=0]
            wr = len(wins)/len(journal)*100
            avg_w = sum(x["pnl"] for x in wins)/len(wins) if wins else 0
            avg_l = sum(x["pnl"] for x in losses)/len(losses) if losses else 0
            total = sum(x["pnl"] for x in journal)
            m1,m2,m3,m4 = st.columns(4)
            m1.metric("總交易",len(journal)); m2.metric("勝率",f"{wr:.1f}%")
            m3.metric("平均盈利",f"${avg_w:,.0f}"); m4.metric("平均虧損",f"${avg_l:,.0f}")
            st.metric("總盈虧",f"${total:+,.0f}")
            if len(journal)>=3:
                from collections import defaultdict
                emo_d = defaultdict(lambda:{"n":0,"pnl":0})
                for x in journal: emo_d[x["emotion"]]["n"]+=1; emo_d[x["emotion"]]["pnl"]+=x["pnl"]
                st.markdown(sec_title("情緒 vs 盈虧"), unsafe_allow_html=True)
                for emo,s in emo_d.items():
                    avg_e = s["pnl"]/s["n"]; ec = th["green"] if avg_e>0 else th["red"]
                    st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:9px 12px;background:{th["card2"]};border-radius:8px;margin-bottom:5px"><span style="font-size:13px;color:{th["text1"]}">{emo}</span><span style="font-size:12px;color:{th["text3"]}">{s["n"]}筆</span><span style="font-size:13px;font-weight:700;color:{ec}">平均 ${avg_e:+,.0f}</span></div>', unsafe_allow_html=True)

    with jtabs[2]:
        journal = st.session_state.get("journal",[])
        if len(journal)<3:
            st.info("需要至少3筆交易記錄")
        else:
            if st.button("🤖 AI 交易教練分析", key="run_coach"):
                used2 = st.session_state.get("ai_calls_today",0)
                limit2 = 9999 if st.session_state.get("role")=="admin" else 20
                if used2>=limit2:
                    st.error("今日 AI 調用已達上限")
                else:
                    wins_c=[x for x in journal if x["pnl"]>0]; wr_c=len(wins_c)/len(journal)*100
                    avg_pnl_c=sum(x["pnl"] for x in journal)/len(journal)
                    most_emo=max({x["emotion"]:journal.count(x) for x in journal},key=lambda k:{x["emotion"]:1 for x in journal}.get(k,0)) if journal else "未知"
                    lang_nc={"zh-hant":"繁體中文","zh-hans":"简体中文","en":"English"}.get(st.session_state.get("lang","zh-hant"),"繁體中文")
                    pc=f"用{lang_nc}分析以下交易：{len(journal)}筆 勝率{wr_c:.1f}% 平均盈虧${avg_pnl_c:+,.0f} 常見情緒:{most_emo}\n請提供：1.主要行為弱點(2句) 2.具體改善建議(3點) 3.針對情緒的提示(1句) 4.鼓勵(1句)"
                    with st.spinner("分析中..."):
                        resc=groq_call(pc); st.session_state["coach_result"]=resc; st.session_state["ai_calls_today"]=used2+1
            if "coach_result" in st.session_state:
                st.markdown(f'<div style="background:{th["card"]};border:1px solid {th["border"]};border-radius:13px;padding:20px;line-height:1.85;font-size:14px;color:{th["text1"]};white-space:pre-line">{st.session_state["coach_result"]}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#   TAB 6 — LEARNING HUB
# ═══════════════════════════════════════════════════════════════════
def tab_learn():
    th = get_theme()
    st.markdown(sec_title("📚 " + t("nav_learn")), unsafe_allow_html=True)
    if not is_pro():
        lock_msg()
        return

    articles = [
        ("K線基礎：讀懂蠟燭圖","入門","10分鐘","K線是技術分析的基石。每根蠟燭包含開盤、收盤、最高、最低四個價格，反映買賣雙方的力量對比。實體越長代表方向越明確；影線越長代表曾有激烈爭奪。常見形態：錘形（底部反轉）、射擊之星（頂部反轉）、吞噬形態（趨勢反轉確認）。"),
        ("EMA均線：趨勢判斷核心","初級","15分鐘","EMA（指數移動平均線）對近期價格更敏感。EMA20金叉EMA50是做多信號；死叉則相反。多條EMA多頭排列（短線在長線上方）代表強勢趨勢。建議配合成交量確認：放量突破EMA比縮量更可靠。"),
        ("MACD：動能與趨勢","初級","20分鐘","MACD由快線(12)、慢線(26)、信號線(9)組成。MACD金叉配合柱狀圖由負轉正，是買入確認信號。頂背離（價創新高但MACD未創高）是賣出警示。逆勢使用MACD信號勝率低，需配合大趨勢方向。"),
        ("Kelly公式：科學倉位管理","中級","12分鐘","Kelly % = (勝率×盈虧比 - 敗率) / 盈虧比。建議使用半Kelly（結果÷2）避免過度倉位。公式假設你的歷史勝率和盈虧比準確，需定期重新計算。單筆最大虧損建議不超過帳戶2%。"),
        ("VIX恐慌指數詳解","中級","15分鐘","VIX < 15：市場平靜。VIX 15-25：正常波幅。VIX 25-35：市場恐慌，謹慎操作。VIX > 35：極端恐慌，逢低吸納機會。正向期限結構（Contango）代表預期恢復平靜，是風險偏好信號。"),
        ("板塊輪動策略","中級","18分鐘","景氣擴張：科技、消費。景氣頂峰：能源、原材料。景氣衰退：防禦板塊（公用、必需品、醫療）。景氣復甦：金融、工業。跟蹤資金流向和相對強度（RS）是關鍵工具。"),
        ("Mark Douglas交易心理學","高級","25分鐘","《交易心理分析》核心：用概率思維取代確定性思維。每次交易結果是隨機的，但系統性執行可產生穩定期望值。避免預測結果，專注執行系統。虧損不是失敗，而是做生意的正常成本。"),
        ("ATR止損設定法","高級","20分鐘","ATR（平均真實波幅）反映股票的正常波動。止損 = 入場價 - 2×ATR（做多）。ATR越大，倉位應越小，確保每次最大虧損不超過帳戶1-2%。建議每週重新計算ATR以適應市場波幅變化。"),
    ]

    level_colors = {"入門":th["green"],"初級":th["blue"],"中級":th["orange"],"高級":th["purple"]}
    selected = st.session_state.get("selected_article", None)
    search = st.text_input("搜尋文章", key="art_search", placeholder="如：MACD、Kelly、止損")
    filtered = [a for a in articles if not search or any(search.lower() in x.lower() for x in [a[0],a[3]])]

    if selected is not None and selected < len(filtered):
        art = filtered[selected]
        if st.button("← 返回列表", key="back_art"):
            st.session_state["selected_article"] = None; st.rerun()
        c = level_colors.get(art[1], th["green"])
        st.markdown(f'<div style="background:{th["card"]};border:1px solid {th["border"]};border-radius:13px;padding:24px"><div style="display:flex;gap:8px;align-items:center;margin-bottom:12px"><span style="font-size:11px;font-weight:700;color:{c};padding:2px 9px;border-radius:5px;border:1px solid {c}">{art[1]}</span><span style="font-size:12px;color:{th["text3"]}">⏱ {art[2]}</span></div><div style="font-size:20px;font-weight:700;color:{th["text1"]};margin-bottom:16px">{art[0]}</div><div style="font-size:14px;color:{th["text2"]};line-height:1.8">{art[3]}</div></div>', unsafe_allow_html=True)
        return

    cols2 = st.columns(2)
    for i, art in enumerate(filtered):
        with cols2[i%2]:
            c = level_colors.get(art[1], th["green"])
            if st.button(f"📖 {art[0]}", key=f"art_{i}", use_container_width=True):
                st.session_state["selected_article"] = i; st.rerun()
            st.markdown(f'<div style="background:{th["card"]};border:1px solid {th["border"]};border-radius:10px;padding:12px 14px;margin-bottom:10px"><div style="display:flex;gap:8px;align-items:center"><span style="font-size:10px;font-weight:700;color:{c};padding:2px 7px;border-radius:4px;border:1px solid {c}">{art[1]}</span><span style="font-size:11px;color:{th["text3"]}">⏱ {art[2]}</span></div><div style="font-size:12px;color:{th["text3"]};margin-top:7px;line-height:1.5">{art[3][:80]}...</div></div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#   TAB 7 — SETTINGS
# ═══════════════════════════════════════════════════════════════════
def tab_settings():
    th = get_theme()
    st.markdown(sec_title("⚙️ " + t("nav_settings")), unsafe_allow_html=True)

    s1, s2 = st.columns(2, gap="medium")
    with s1:
        with st.expander("Telegram 推送設定"):
            tg_id_s = st.text_input("你的 Telegram Chat ID", key="tg_id_s", placeholder="123456789", help="Telegram 搜尋 @userinfobot 獲取")
            if st.button("🔔 測試推送", key="test_tg_s"):
                if tg_id_s:
                    ok = send_telegram_msg(tg_id_s, f"✅ MarketIQ 推送測試成功！\n👤 {st.session_state.get('username','')}")
                    st.success("✅ 推送成功！" if ok else "❌ 推送失敗")

        with st.expander("價格提示設定"):
            wl_set = [s.strip().upper() for s in st.session_state.get("wl_tickers","TSLA,AAPL").split(",") if s.strip()][:5]
            alerts = st.session_state.get("price_alerts", {})
            for tk in wl_set:
                ac1, ac2 = st.columns(2)
                with ac1: ab = st.number_input(f"{tk} 目標價↑($)", value=float(alerts.get(tk,{}).get("above",0)), step=1.0, key=f"ab_{tk}", min_value=0.0)
                with ac2: bl = st.number_input(f"{tk} 止損價↓($)", value=float(alerts.get(tk,{}).get("below",0)), step=1.0, key=f"bl_{tk}", min_value=0.0)
            if st.button("💾 儲存提示", key="save_alerts_s"):
                new_a = {tk:{"above":st.session_state.get(f"ab_{tk}",0),"below":st.session_state.get(f"bl_{tk}",0)} for tk in wl_set if st.session_state.get(f"ab_{tk}",0)>0 or st.session_state.get(f"bl_{tk}",0)>0}
                st.session_state["price_alerts"] = new_a; st.success("已儲存")

    with s2:
        role_v = st.session_state.get("role","free")
        exp_str = st.session_state.get("expiry_date","永久")
        ai_used = st.session_state.get("ai_calls_today",0)
        ai_lim  = 9999 if role_v=="admin" else 20 if role_v=="pro" else 3
        role_lbl = {"admin":"👑 Admin","pro":"⭐ Pro","free":"🆓 Free"}.get(role_v,"🆓 Free")
        role_col = {"admin":th["orange"],"pro":th["green"],"free":th["text3"]}.get(role_v,th["text3"])
        rows_s = [("帳號",st.session_state.get("username","—")),("層級",role_lbl),("地區",st.session_state.get("region","—")),("到期日",exp_str),(f'今日 AI 調用',f'{ai_used}/{"∞" if ai_lim==9999 else ai_lim}')]
        rows_html_s = "".join(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:9px 0;border-bottom:1px solid {th["border2"]}"><span style="font-size:13px;color:{th["text2"]}">{k}</span><span style="font-size:13px;font-weight:600;color:{role_col if k=="層級" else th["text1"]}">{v}</span></div>' for k,v in rows_s)
        st.markdown(f'<div style="background:{th["card"]};border:1px solid {th["border"]};border-radius:13px;padding:18px"><div style="font-size:14px;font-weight:600;color:{th["text1"]};margin-bottom:14px">訂閱管理</div>{rows_html_s}</div>', unsafe_allow_html=True)

        # Price alert live check
        alerts_set = st.session_state.get("price_alerts",{})
        if alerts_set:
            st.markdown(f'<div style="margin-top:14px">{sec_title("📊 即時價格提示")}</div>', unsafe_allow_html=True)
            for tk, al in alerts_set.items():
                d_chk = fetch_ticker_full(tk)
                if not d_chk: continue
                price_chk = d_chk["price"]
                if al.get("above",0)>0 and price_chk>=al["above"]:
                    st.markdown(f'<div style="padding:10px 14px;background:{th["green"]}20;border:1px solid {th["green"]}40;border-radius:9px;font-size:13px;color:{th["green"]};margin-bottom:6px">🚀 {tk} 突破目標價 ${al["above"]:.2f}（現價 ${price_chk:.2f}）</div>', unsafe_allow_html=True)
                if al.get("below",0)>0 and price_chk<=al["below"]:
                    st.markdown(f'<div style="padding:10px 14px;background:{th["red"]}20;border:1px solid {th["red"]}40;border-radius:9px;font-size:13px;color:{th["red"]};margin-bottom:6px">⚠️ {tk} 跌穿止損價 ${al["below"]:.2f}（現價 ${price_chk:.2f}）</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#   TAB 8 — ADMIN CONSOLE
# ═══════════════════════════════════════════════════════════════════
def tab_admin():
    th = get_theme()
    st.markdown(sec_title("👑 " + t("nav_admin")), unsafe_allow_html=True)

    sheet = get_gsheet()
    if sheet is None:
        st.warning("Google Sheets 未連接，顯示本地測試數據")
        with st.expander("連接診斷", expanded=True):
            debug_gsheet_connection()
        users_list = [{"username":k,"role":v["role"],"expiry_date":v.get("expiry_date","—"),"status":v.get("status","active"),"region":v.get("region","UK"),"ai_calls_today":0} for k,v in FALLBACK_USERS.items()]
    else:
        try: users_list = sheet.get_all_records()
        except Exception: users_list = []

    pros=[u for u in users_list if u.get("role")=="pro"]; frees=[u for u in users_list if u.get("role")=="free"]
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("總用戶",len(users_list)); m2.metric("⭐ Pro",len(pros)); m3.metric("🆓 Free",len(frees)); m4.metric("👑 Admin",len([u for u in users_list if u.get("role")=="admin"]))

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("新增用戶"):
        ua1,ua2,ua3,ua4,ua5,ua6 = st.columns(6)
        with ua1: nu = st.text_input("用戶名", key="nu_adm")
        with ua2: np2 = st.text_input("密碼", type="password", key="np_adm")
        with ua3: nr = st.selectbox("角色", ["free","pro","admin"], key="nr_adm")
        with ua4: nd = st.number_input("天數(0=永久)", 0, 3650, 14, key="nd_adm")
        with ua5: nreg = st.selectbox("地區", ["HK","CN","UK","US"], key="nreg_adm")
        with ua6: nlang = st.selectbox("語言", ["zh-hant","zh-hans","en"], key="nlang_adm")
        if st.button("新增用戶", key="do_add_adm"):
            if nu and np2 and sheet:
                from datetime import timedelta
                exp = "永久" if nd==0 else (datetime.now().date()+timedelta(days=nd)).isoformat()
                pw_hash = bcrypt.hashpw(np2.encode(), bcrypt.gensalt()).decode()
                try:
                    sheet.append_row([nu,pw_hash,nr,exp,nreg,nlang,"dark","active",datetime.now().date().isoformat(),"",0,"","","","{}","{}"])
                    st.success(f"已新增用戶 {nu}")
                except Exception as e: st.error(f"新增失敗: {e}")
            elif not sheet: st.warning("需要 Google Sheets 連接才能新增用戶")

    st.markdown(sec_title("用戶列表"), unsafe_allow_html=True)
    if users_list:
        urows = "".join(f'<tr><td style="font-weight:600">{u.get("username","")}</td><td style="color:{"#f0a030" if u.get("role")=="admin" else th["green"] if u.get("role")=="pro" else th["text3"]};font-weight:600">{u.get("role","").upper()}</td><td>{u.get("expiry_date","—")}</td><td>{u.get("region","—")}</td><td style="font-family:Inter">{u.get("ai_calls_today",0)}</td><td style="color:{th["green"] if u.get("status","active")=="active" else th["red"]}">{u.get("status","active")}</td></tr>' for u in users_list)
        st.markdown(f'<div class="ds-card" style="overflow-x:auto"><table style="width:100%;border-collapse:collapse;font-size:13px"><thead><tr style="border-bottom:2px solid {th["border"]}">'+"".join(f'<th style="padding:7px 10px;font-size:10px;color:{th["text3"]}">{h}</th>' for h in ["用戶名","角色","到期日","地區","今日AI","狀態"])+f'</tr></thead><tbody>{urows}</tbody></table></div>', unsafe_allow_html=True)

    with st.expander("快速編輯用戶"):
        unames = [u.get("username","") for u in users_list]
        if unames:
            eu = st.selectbox("選擇用戶", unames, key="eu_adm")
            ec1,ec2,ec3 = st.columns(3)
            with ec1:
                new_role_adm = st.selectbox("新角色", ["free","pro","admin"], key="new_role_adm")
                if st.button("更新角色", key="upd_role_adm") and sheet:
                    try:
                        cell=sheet.find(eu); headers=sheet.row_values(1); col=headers.index("role")+1
                        sheet.update_cell(cell.row,col,new_role_adm); st.success(f"已更新 {eu} 角色")
                    except Exception as e: st.error(str(e))
            with ec2:
                new_exp_adm = st.text_input("新到期日", key="new_exp_adm", placeholder="YYYY-MM-DD 或 永久")
                if st.button("更新到期日", key="upd_exp_adm") and sheet:
                    try:
                        cell=sheet.find(eu); headers=sheet.row_values(1); col=headers.index("expiry_date")+1
                        sheet.update_cell(cell.row,col,new_exp_adm); st.success(f"已更新 {eu} 到期日")
                    except Exception as e: st.error(str(e))
            with ec3:
                new_st_adm = st.selectbox("帳號狀態", ["active","disabled"], key="new_st_adm")
                if st.button("更新狀態", key="upd_st_adm") and sheet:
                    try:
                        cell=sheet.find(eu); headers=sheet.row_values(1); col=headers.index("status")+1
                        sheet.update_cell(cell.row,col,new_st_adm); st.success(f"已更新 {eu} 狀態")
                    except Exception as e: st.error(str(e))


# ═══════════════════════════════════════════════════════════════════
#   MAIN APP ROUTER
# ═══════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    main()
