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
    initial_sidebar_state="collapsed",
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
    """Inject all CSS based on current theme + font size"""
    th = get_theme()
    fs = get_font_size()
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+HK:wght@300;400;500;700&family=Inter:wght@400;500;600;700;800;900&display=swap');

    /* Hide Streamlit chrome */
    #MainMenu, footer, header {{ visibility: hidden; }}
    .stDeployButton {{ display: none; }}
    section[data-testid="stSidebar"] {{ display: none !important; }}

    .stApp {{
        background: {th['bg']} !important;
        font-family: 'Noto Sans HK', 'Inter', sans-serif !important;
        font-size: {fs}px;
    }}

    .block-container {{
        padding-top: 0 !important;
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
    """Connect to Google Sheets. Falls back to local mock if not configured."""
    try:
        creds_json = st.secrets["google_sheets"]["credentials"]
        if isinstance(creds_json, str):
            creds_dict = json.loads(creds_json)
        else:
            creds_dict = dict(creds_json)
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(creds)
        sheet_id = st.secrets["google_sheets"]["spreadsheet_id"]
        return client.open_by_key(sheet_id).sheet1
    except Exception as e:
        return None


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
#   LOGIN PAGE
# ═══════════════════════════════════════════════════════════════════
def render_login():
    th = get_theme()
    inject_css()

    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown(f"""
        <div class="login-card">
          <div class="login-logo">
            <div class="login-mark">
              <svg width="24" height="24" viewBox="0 0 20 20" fill="none">
                <path d="M2 15L6 8.5l3.5 4.5 4-7L18 15H2z" fill="#111118"/>
              </svg>
            </div>
            <div>
              <div style="font-size:18px;font-weight:700;color:{th['text1']}">MarketIQ</div>
              <div style="font-size:10px;color:{th['text3']};letter-spacing:0.6px">INTELLIGENCE DASHBOARD</div>
            </div>
          </div>
          <div class="login-title">{t('login_title')}</div>
          <div class="login-sub">{t('login_sub')}</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(t("username"), key="login_u")
            password = st.text_input(t("password"), type="password", key="login_p")
            submit = st.form_submit_button(t("login_btn"))

            if submit:
                # Lockout check
                fails = st.session_state.get("login_fails", 0)
                lockout_until = st.session_state.get("lockout_until")
                if lockout_until and datetime.now() < lockout_until:
                    st.error(t("login_locked"))
                else:
                    ok, user_data, err = authenticate(username, password)
                    if ok:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = user_data.get("username", username)
                        st.session_state["role"] = user_data.get("role", "free")
                        st.session_state["region"] = user_data.get("region", "UK")
                        st.session_state["lang"] = user_data.get("language", "zh-hant")
                        st.session_state["theme"] = user_data.get("theme", "dark")
                        st.session_state["expiry_date"] = str(user_data.get("expiry_date", "2099-12-31"))
                        st.session_state["login_fails"] = 0
                        st.rerun()
                    else:
                        st.session_state["login_fails"] = fails + 1
                        if fails + 1 >= 5:
                            st.session_state["lockout_until"] = datetime.now() + timedelta(minutes=30)
                            st.error(t("login_locked"))
                        else:
                            st.error(err)

        st.markdown(f"""
        <div style="text-align:center;margin-top:18px;padding:12px;background:{th['bg2']};border-radius:9px;font-size:11px;color:{th['text3']};line-height:1.6">
          <strong style="color:{th['text2']}">測試帳號 / Demo Accounts:</strong><br>
          admin / admin123 (👑)<br>
          tesla / tesla123 (⭐ Pro)<br>
          demo / demo123 (🆓 Free)
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#   TOP BAR (Logo + Status + Theme + Language + User)
# ═══════════════════════════════════════════════════════════════════
def render_topbar():
    th = get_theme()
    status = market_status()

    us_chip = f'<div class="chip"><span class="sdot {"sdot-on" if status["us"] else "sdot-off"}"></span>{t("us_open" if status["us"] else "us_closed")}</div>'
    hk_chip = f'<div class="chip"><span class="sdot {"sdot-on" if status["hk"] else "sdot-off"}"></span>{t("hk_open" if status["hk"] else "hk_closed")}</div>'

    role_badge = {"admin": "👑 Admin", "pro": "⭐ Pro", "free": "🆓 Free"}.get(
        st.session_state.get("role", "free"), "🆓 Free"
    )

    st.markdown(f"""
    <div class="topbar">
      <div class="topbar-left">
        <div class="topbar-logo">
          <div class="tb-mark">
            <svg width="18" height="18" viewBox="0 0 20 20" fill="none">
              <path d="M2 15L6 8.5l3.5 4.5 4-7L18 15H2z" fill="#111118"/>
            </svg>
          </div>
          <div>
            <div class="tb-title">MarketIQ</div>
            <div class="tb-sub">{t('app_sub')}</div>
          </div>
        </div>
        {us_chip}
        {hk_chip}
      </div>
      <div class="topbar-right">
        <div class="chip" style="background:{th['nav_active_bg']};color:{th['nav_text_active']};border-color:{th['nav_text_active']}33">
          {role_badge} · {st.session_state.get('username','')}
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#   CONTROL PANEL (Theme / Font / Language / Logout)
# ═══════════════════════════════════════════════════════════════════
def render_controls():
    """Top-right control row above main content"""
    cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1])

    with cols[0]:
        if st.button(t("theme_dark"), key="bt_dark",
                     type="primary" if st.session_state.get("theme") == "dark" else "secondary"):
            st.session_state["theme"] = "dark"
            st.rerun()
    with cols[1]:
        if st.button(t("theme_light"), key="bt_light",
                     type="primary" if st.session_state.get("theme") == "light" else "secondary"):
            st.session_state["theme"] = "light"
            st.rerun()
    with cols[2]:
        if st.button(t("theme_eye"), key="bt_eye",
                     type="primary" if st.session_state.get("theme") == "eye" else "secondary"):
            st.session_state["theme"] = "eye"
            st.rerun()
    with cols[3]:
        if st.button("A-", key="bt_sm",
                     type="primary" if st.session_state.get("font_size") == "sm" else "secondary"):
            st.session_state["font_size"] = "sm"
            st.rerun()
    with cols[4]:
        if st.button("A", key="bt_md",
                     type="primary" if st.session_state.get("font_size", "md") == "md" else "secondary"):
            st.session_state["font_size"] = "md"
            st.rerun()
    with cols[5]:
        if st.button("A+", key="bt_lg",
                     type="primary" if st.session_state.get("font_size") == "lg" else "secondary"):
            st.session_state["font_size"] = "lg"
            st.rerun()
    with cols[6]:
        lang_options = {"繁體中文": "zh-hant", "简体中文": "zh-hans", "English": "en"}
        current_lang_label = next((k for k, v in lang_options.items()
                                   if v == st.session_state.get("lang", "zh-hant")), "繁體中文")
        new_lang = st.selectbox("Lang", options=list(lang_options.keys()),
                                index=list(lang_options.keys()).index(current_lang_label),
                                label_visibility="collapsed", key="lang_sel")
        if lang_options[new_lang] != st.session_state.get("lang"):
            st.session_state["lang"] = lang_options[new_lang]
            st.rerun()
    with cols[7]:
        if st.button(f"⏻ {t('logout')}", key="bt_logout"):
            for k in list(st.session_state.keys()):
                if k != "lockout_until":
                    del st.session_state[k]
            st.rerun()


# ═══════════════════════════════════════════════════════════════════
#   TAB 1 — GLOBAL MARKET MONITOR
# ═══════════════════════════════════════════════════════════════════
def tab_global_market():
    th = get_theme()

    # Page header
    now_str = datetime.now(pytz.timezone("Europe/London")).strftime("%d/%m/%Y %H:%M")
    st.markdown(f"""
    <div class="page-header">
      <div class="page-title">{t('app_title')}</div>
      <div class="page-sub">{t('last_update')} {now_str} London · {t('data_source')}</div>
    </div>
    """, unsafe_allow_html=True)

    # Eye-care banner
    if st.session_state.get("theme") == "eye":
        st.markdown(f'<div class="eye-banner">🍃 {t("eye_banner")}</div>', unsafe_allow_html=True)

    # Expiry warning
    try:
        exp = datetime.strptime(st.session_state.get("expiry_date", "2099-12-31"), "%Y-%m-%d").date()
        days_left = (exp - datetime.now().date()).days
        if 0 < days_left <= 7 and st.session_state.get("role") == "pro":
            st.markdown(f'<div class="expiry-banner">⚠️ {t("expiry_warn").format(days_left)}</div>', unsafe_allow_html=True)
    except Exception:
        pass

    # ── KPI ROW ──
    with st.spinner(t("loading")):
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
        # Sort sectors by absolute value for heatmap
        sorted_for_hm = sorted(sector_data.items(), key=lambda x: x[1], reverse=True)
        max_abs = max(abs(v) for _, v in sorted_for_hm) if sorted_for_hm else 1

        hm_rows = ""
        for name, val in sorted_for_hm[:8]:
            pct_width = abs(val) / max_abs * 100
            color_cls = "up" if val >= 0 else "dn"
            bar_color = th["green"] if val >= 0 else th["red"]
            hm_rows += f"""
            <div class="hm-row">
              <span class="hm-name">{name}</span>
              <div class="hm-bar-w"><div class="hm-bar" style="width:{pct_width}%;background:{bar_color}"></div></div>
              <span class="hm-val {color_cls}">{fmt_pct(val,1)}</span>
            </div>
            """

        st.markdown(f"""
        <div class="ds-card">
          <div class="card-hd"><div class="card-title">{t('sector_heatmap')}</div></div>
          <div class="hm-grid">{hm_rows}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)

    # ── BOTTOM ROW: Watchlist + Regime + VIX ──
    bot_col1, bot_col2, bot_col3 = st.columns(3)

    # Default watchlist
    default_watchlist = ["TSLA", "NVDA", "AAPL", "META", "AMZN"]
    signals = fetch_watchlist_signals(default_watchlist)

    with bot_col1:
        sig_rows = ""
        for s in signals:
            sc = s["score"]
            if sc >= 70:
                badge_cls = "b-buy"
                badge_txt = t("buy")
                dot_color = th["green"]
                sc_class = "up"
                glow = f"box-shadow:0 0 5px {th['green']}"
            elif sc >= 45:
                badge_cls = "b-watch"
                badge_txt = t("watch")
                dot_color = th["orange"]
                sc_class = ""
                glow = ""
            else:
                badge_cls = "b-avoid"
                badge_txt = t("avoid")
                dot_color = th["red"]
                sc_class = "dn"
                glow = f"box-shadow:0 0 5px {th['red']}"

            sc_color = th["green"] if sc >= 70 else (th["orange"] if sc >= 45 else th["red"])

            sig_rows += f"""
            <div class="si-row">
              <div class="si-l">
                <span class="si-dot" style="background:{dot_color};{glow}"></span>
                <span class="si-tk">{s['ticker']}</span>
                <span class="si-pr">${s['price']:.2f}</span>
              </div>
              <div class="si-r">
                <span class="si-sc" style="color:{sc_color}">{sc}</span>
                <span class="badge {badge_cls}">{badge_txt}</span>
              </div>
            </div>
            """

        st.markdown(f"""
        <div class="ds-card">
          <div class="card-hd">
            <div class="card-title">{t('watchlist_signals')}</div>
            <span class="card-pill">{t('entry_score')}</span>
          </div>
          {sig_rows}
        </div>
        """, unsafe_allow_html=True)

    with bot_col2:
        regime = compute_market_regime()
        if regime:
            regime_label = t(regime["regime"])
            regime_color = {"green": th["green"], "red": th["red"],
                          "orange": th["orange"], "blue": th["blue"]}.get(regime["color"], th["green"])

            st.markdown(f"""
            <div class="ds-card">
              <div class="card-hd"><div class="card-title">{t('market_regime')}</div></div>
              <div class="regime-state-lbl">{t('current_state')}</div>
              <div class="regime-val" style="color:{regime_color}">{regime_label}</div>
              <div class="reg-bar">
                <div class="reg-bar-hd"><span>{t('momentum')}</span><span style="color:{th['green']}">{regime['momentum']} / 100</span></div>
                <div class="reg-bar-track"><div class="reg-bar-fill" style="width:{regime['momentum']}%;background:{th['green']}"></div></div>
              </div>
              <div class="reg-bar">
                <div class="reg-bar-hd"><span>{t('breadth')}</span><span style="color:{th['blue']}">{regime['breadth']} / 100</span></div>
                <div class="reg-bar-track"><div class="reg-bar-fill" style="width:{regime['breadth']}%;background:{th['blue']}"></div></div>
              </div>
              <div class="reg-bar">
                <div class="reg-bar-hd"><span>{t('sentiment')}</span><span style="color:{th['orange']}">{regime['sentiment']} / 100</span></div>
                <div class="reg-bar-track"><div class="reg-bar-fill" style="width:{regime['sentiment']}%;background:{th['orange']}"></div></div>
              </div>
              <div class="reg-bar">
                <div class="reg-bar-hd"><span>{t('volatility')}</span><span style="color:{th['green']}">VIX {regime['vix']:.1f}</span></div>
                <div class="reg-bar-track"><div class="reg-bar-fill" style="width:{regime['volatility']}%;background:{th['green']}"></div></div>
              </div>
              <div class="ai-tip">
                <div class="ai-tip-l">{t('ai_advice')}</div>
                <div class="ai-tip-t">{t('ai_advice_text')}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

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
        bars_html = ""
        labels = ["9D", "VIX", "3M", "6M"]
        for i, (h, c, lbl) in enumerate(zip(bar_heights, bar_colors, labels)):
            bars_html += f"""
            <div class="vix-bar-c">
              <div class="vix-bar" style="height:{h}%;background:linear-gradient(180deg,{c} 0%,{c}1a 100%)"></div>
              <div class="vix-bar-l">{lbl}</div>
            </div>
            """

        rows_html = ""
        row_data = [
            ("VIX 9D", vix_9d, th["green"] if vix_9d and vix_9d < 18 else th["text1"]),
            (t("vix_spot"), vix_spot, th["orange"] if vix_spot and vix_spot > 18 else th["text1"]),
            ("VIX 3M", vix_3m, th["text1"]),
            ("VIX 6M", vix_6m, th["text1"]),
        ]
        for label, val, color in row_data:
            val_str = f"{val:.1f}" if val else "—"
            rows_html += f"""
            <div class="vix-row">
              <span class="vrt">{label}</span>
              <span class="vrv" style="color:{color}">{val_str}</span>
            </div>
            """

        st.markdown(f"""
        <div class="ds-card">
          <div class="card-hd"><div class="card-title">{t('vix_term')}</div></div>
          <div class="vix-curve">{bars_html}</div>
          <div>{rows_html}</div>
          <div class="ctag">{contango_text}</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#   PLACEHOLDER TABS (will be implemented in v1.1+)
# ═══════════════════════════════════════════════════════════════════
def tab_placeholder(name, emoji, desc):
    th = get_theme()
    st.markdown(f"""
    <div style="padding:60px 20px;text-align:center">
      <div style="font-size:48px;margin-bottom:16px">{emoji}</div>
      <div style="font-size:22px;font-weight:700;color:{th['text1']};margin-bottom:8px">{name}</div>
      <div style="font-size:13px;color:{th['text3']};max-width:400px;margin:0 auto;line-height:1.7">{desc}</div>
      <div style="display:inline-block;margin-top:20px;padding:8px 16px;background:{th['nav_active_bg']};color:{th['nav_text_active']};border-radius:8px;font-size:12px;font-weight:600">即將推出 · Coming Soon</div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#   MAIN APP ROUTER
# ═══════════════════════════════════════════════════════════════════
def main():
    # Initialize session defaults
    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"
    if "lang" not in st.session_state:
        st.session_state["lang"] = "zh-hant"
    if "font_size" not in st.session_state:
        st.session_state["font_size"] = "md"
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "current_tab" not in st.session_state:
        st.session_state["current_tab"] = "global"

    # Show login if not logged in
    if not st.session_state.get("logged_in"):
        render_login()
        return

    # Inject theme CSS
    inject_css()

    # Top bar
    render_topbar()

    # Controls (theme/font/lang/logout)
    render_controls()

    # Tab navigation as Streamlit tabs
    tabs_config = [
        ("global", t("nav_global"), "📊"),
        ("watchlist", t("nav_watchlist"), "⭐"),
        ("ai", t("nav_ai"), "🤖"),
        ("portfolio", t("nav_portfolio"), "💼"),
        ("journal", t("nav_journal"), "📓"),
        ("learn", t("nav_learn"), "📚"),
        ("settings", t("nav_settings"), "⚙️"),
    ]
    if st.session_state.get("role") == "admin":
        tabs_config.append(("admin", t("nav_admin"), "👑"))

    tab_labels = [f"{cfg[2]} {cfg[1]}" for cfg in tabs_config]
    tab_objects = st.tabs(tab_labels)

    with tab_objects[0]:
        tab_global_market()

    with tab_objects[1]:
        tab_placeholder(t("nav_watchlist"), "⭐",
                       "自選股票批量查詢、信號燈評分、入場時機評分、智能止損計算器、相關性熱力圖、組合命名儲存。\n\nWatchlist with batch query, signal scoring, entry timing, smart stop-loss calculator, correlation heatmap.")

    with tab_objects[2]:
        tab_placeholder(t("nav_ai"), "🤖",
                       "AI 投資建議（Groq LLaMA）、Morning Briefing、三層漏斗分析、交易前冷靜檢查、異常偵測警示、Telegram 推送。\n\nAI advice via Groq, Morning Briefing, top-down funnel, pre-trade checklist, anomaly alerts.")

    with tab_objects[3]:
        tab_placeholder(t("nav_portfolio"), "💼",
                       "持倉追蹤、組合風險分析、Kelly 倉位計算器、目標追蹤器。\n\nPosition tracking, risk analysis, Kelly position sizing, goal tracker.")

    with tab_objects[4]:
        tab_placeholder(t("nav_journal"), "📓",
                       "交易記錄、情緒日記、勝率統計、AI 交易教練、每週績效回顧、策略回測沙盒。\n\nTrade journal, emotion log, win-rate stats, AI coach, weekly review.")

    with tab_objects[5]:
        tab_placeholder(t("nav_learn"), "📚",
                       "個人化學習路徑、技術分析教學、模擬交易（Elite）。\n\nPersonalized learning, tutorials, paper trading.")

    with tab_objects[6]:
        tab_placeholder(t("nav_settings"), "⚙️",
                       "個人偏好設定、Telegram 推送設定、價格提示、訂閱管理。\n\nPreferences, Telegram setup, price alerts, subscription.")

    if st.session_state.get("role") == "admin" and len(tab_objects) > 7:
        with tab_objects[7]:
            tab_placeholder(t("nav_admin"), "👑",
                           "用戶管理、AI 使用監控、系統設定、登入記錄。\n\nUser management, AI usage monitoring, system settings, login logs.")


if __name__ == "__main__":
    main()
