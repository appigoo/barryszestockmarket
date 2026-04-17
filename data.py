# utils/data.py
# ─── Market Data via yfinance ─────────────────────────────────────────────────

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz

# ── Ticker Maps ───────────────────────────────────────────────────────────────
MACRO_TICKERS = {
    "美元指數": "DX-Y.NYB",
    "2年美債":  "^IRX",
    "10年美債": "^TNX",
    "TLT":     "TLT",
    "垃圾債 HYG":"HYG",
}
INDEX_TICKERS = {
    "標普500":  "^GSPC",
    "納指":     "^IXIC",
    "道指":     "^DJI",
    "黃金":     "GC=F",
    "WTI原油":  "CL=F",
    "VIX":     "^VIX",
    "IGV":     "IGV",
    "羅素2000": "^RUT",
    "比特幣":   "BTC-USD",
}
SECTOR_TICKERS = {
    "通訊服務": "XLC",
    "非必需品": "XLY",
    "必需品":   "XLP",
    "能源":     "XLE",
    "銀行":     "XLF",
    "公用事業": "XLU",
    "REITS":   "IYR",
    "科技":     "XLK",
    "醫療":     "XLV",
    "國防":     "ITA",
    "保險":     "KIE",
}
FACTOR_TICKERS = {
    "芯片 SOXX":    "SOXX",
    "羅素價值 IWD": "IWD",
    "羅素成長 IWF": "IWF",
    "前7大科技":    "MAGS",
    "等權指數 RSP": "RSP",
}
VIX_TICKERS = {
    "VIX 9D":  "^VIX9D",
    "VIX":     "^VIX",
    "VIX 3M":  "^VIX3M",
    "VIX 6M":  "^VIX6M",
}

ALL_TICKERS = {**MACRO_TICKERS, **INDEX_TICKERS, **SECTOR_TICKERS, **FACTOR_TICKERS}

MARKET_HOURS = {
    "US":  {"name": "美股", "open": "09:30", "close": "16:00", "tz": "America/New_York"},
    "HK":  {"name": "港股", "open": "09:30", "close": "16:00", "tz": "Asia/Hong_Kong"},
    "CN":  {"name": "A股",  "open": "09:30", "close": "15:00", "tz": "Asia/Shanghai"},
    "UK":  {"name": "英股", "open": "08:00", "close": "16:30", "tz": "Europe/London"},
}


# ── Helpers ───────────────────────────────────────────────────────────────────
def _safe_float(val):
    try:
        return float(val)
    except Exception:
        return None


def _pct(a, b):
    if a is None or b is None or b == 0:
        return None
    return (a - b) / b * 100


def _flatten(df) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


# ── Market Status ─────────────────────────────────────────────────────────────
def get_market_status() -> dict:
    status = {}
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    for code, info in MARKET_HOURS.items():
        tz = pytz.timezone(info["tz"])
        now_local = now_utc.astimezone(tz)
        weekday = now_local.weekday()
        if weekday >= 5:
            status[code] = {"name": info["name"], "open": False, "time": now_local.strftime("%H:%M")}
            continue
        h, m = map(int, info["open"].split(":"))
        open_t = now_local.replace(hour=h, minute=m, second=0)
        h2, m2 = map(int, info["close"].split(":"))
        close_t = now_local.replace(hour=h2, minute=m2, second=0)
        is_open = open_t <= now_local <= close_t
        status[code] = {"name": info["name"], "open": is_open, "time": now_local.strftime("%H:%M")}
    return status


# ── Single Ticker ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_one(sym: str, period: str = "1y") -> dict | None:
    try:
        df = yf.download(sym, period=period, interval="1d",
                         auto_adjust=True, progress=False)
        df = _flatten(df).dropna()
        if len(df) < 5:
            return None
        close = df["Close"]
        latest = _safe_float(close.iloc[-1])
        prev   = _safe_float(close.iloc[-2])
        if latest is None or prev is None:
            return None

        def _back(n): return _safe_float(close.iloc[max(0, len(close)-n)])

        return {
            "price": latest,
            "1d":  _pct(latest, prev),
            "1w":  _pct(latest, _back(6)),
            "1m":  _pct(latest, _back(22)),
            "1y":  _pct(latest, _back(252)),
            "qtd": _pct(latest, _back(63)),
            "ytd": _pct(latest, _back(75)),
            "history": close.tail(252).tolist(),
            "dates":   [str(d.date()) for d in close.tail(252).index],
            "sym": sym,
        }
    except Exception:
        return None


@st.cache_data(ttl=300)
def fetch_batch(ticker_map: dict) -> dict:
    syms = list(ticker_map.values())
    result = {}
    try:
        raw = yf.download(syms, period="1y", interval="1d",
                          group_by="ticker", auto_adjust=True, progress=False)
        for name, sym in ticker_map.items():
            try:
                df = _flatten(raw[sym] if len(syms) > 1 else raw).dropna()
                if len(df) < 5:
                    result[name] = None
                    continue
                close = df["Close"]
                latest = _safe_float(close.iloc[-1])
                prev   = _safe_float(close.iloc[-2])
                if latest is None:
                    result[name] = None
                    continue
                def _back(n): return _safe_float(close.iloc[max(0, len(close)-n)])
                result[name] = {
                    "price": latest,
                    "1d":  _pct(latest, prev),
                    "1w":  _pct(latest, _back(6)),
                    "1m":  _pct(latest, _back(22)),
                    "1y":  _pct(latest, _back(252)),
                    "qtd": _pct(latest, _back(63)),
                    "ytd": _pct(latest, _back(75)),
                    "history": close.tail(60).tolist(),
                    "sym": sym,
                }
            except Exception:
                result[name] = None
    except Exception:
        for name in ticker_map:
            result[name] = None
    return result


@st.cache_data(ttl=300)
def fetch_ohlcv(sym: str, period: str = "3mo") -> pd.DataFrame:
    try:
        df = yf.download(sym, period=period, interval="1d",
                         auto_adjust=True, progress=False)
        return _flatten(df).dropna()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_vix_term() -> dict:
    result = {}
    for name, sym in VIX_TICKERS.items():
        d = fetch_one(sym, "5d")
        result[name] = d["price"] if d else None
    return result


# ── Technical Indicators ──────────────────────────────────────────────────────
def compute_ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/period, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    h, l, c = df["High"], df["Low"], df["Close"]
    tr = pd.concat([
        h - l,
        (h - c.shift()).abs(),
        (l - c.shift()).abs()
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1/period, adjust=False).mean()


def compute_macd(series: pd.Series, fast=12, slow=26, signal=9):
    ema_f = series.ewm(span=fast, adjust=False).mean()
    ema_s = series.ewm(span=slow, adjust=False).mean()
    macd  = ema_f - ema_s
    sig   = macd.ewm(span=signal, adjust=False).mean()
    hist  = macd - sig
    return macd, sig, hist


# ── Signal Score (0-100) ──────────────────────────────────────────────────────
def compute_signal_score(sym: str) -> dict:
    """Returns score (0-100), label, and component scores"""
    try:
        df = fetch_ohlcv(sym, "6mo")
        if df.empty or len(df) < 50:
            return {"score": 50, "label": "neutral", "components": {}}

        close = df["Close"]
        ema20 = compute_ema(close, 20)
        ema50 = compute_ema(close, 50)
        rsi   = compute_rsi(close)
        atr   = compute_atr(df)

        latest = float(close.iloc[-1])
        e20    = float(ema20.iloc[-1])
        e50    = float(ema50.iloc[-1])
        rsi_v  = float(rsi.iloc[-1])
        atr_v  = float(atr.iloc[-1])
        atr_pct = atr_v / latest * 100

        # Trend score (0-40)
        trend = 0
        if latest > e20: trend += 20
        if latest > e50: trend += 10
        if e20 > e50:    trend += 10

        # Momentum score (0-40)
        mom = 0
        if 40 < rsi_v < 70:  mom = 40
        elif 30 < rsi_v <= 40: mom = 20
        elif 70 <= rsi_v < 80: mom = 25
        elif rsi_v >= 80:      mom = 10
        else:                  mom = 5

        # Volatility score (0-20) — lower vol = higher score
        vol = 20 if atr_pct < 2 else (15 if atr_pct < 4 else (10 if atr_pct < 6 else 5))

        score = trend + mom + vol

        # 1m performance bonus
        d1m = None
        if len(close) >= 22:
            d1m = (latest / float(close.iloc[-22]) - 1) * 100
            if d1m and d1m > 5: score = min(100, score + 5)
            elif d1m and d1m < -5: score = max(0, score - 5)

        if score >= 65:   label = "buy"
        elif score >= 40: label = "watch"
        else:             label = "avoid"

        return {
            "score": score,
            "label": label,
            "components": {
                "trend": trend,
                "momentum": mom,
                "volatility": vol,
                "rsi": round(rsi_v, 1),
                "atr_pct": round(atr_pct, 2),
                "ema20": round(e20, 2),
                "ema50": round(e50, 2),
                "1m_perf": round(d1m, 2) if d1m else None,
            }
        }
    except Exception:
        return {"score": 50, "label": "neutral", "components": {}}


# ── Market Regime ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def compute_market_regime() -> dict:
    try:
        vix_d  = fetch_one("^VIX", "5d")
        spy_d  = fetch_one("^GSPC", "3mo")
        vix_v  = vix_d["price"] if vix_d else 20

        # Momentum: SPY 1m
        mom_score = 50
        if spy_d:
            perf_1m = spy_d["1m"] or 0
            if perf_1m > 5:   mom_score = 80
            elif perf_1m > 2: mom_score = 65
            elif perf_1m > 0: mom_score = 55
            elif perf_1m > -3: mom_score = 40
            else:              mom_score = 20

        # Volatility: VIX
        if vix_v < 15:   vol_score = 85
        elif vix_v < 20: vol_score = 70
        elif vix_v < 25: vol_score = 50
        elif vix_v < 35: vol_score = 25
        else:            vol_score = 5

        # Sentiment: crude proxy
        sent_score = 55

        # Breadth: use RSP vs SPY proxy
        breadth_score = 60

        overall = int((mom_score * 0.35 + vol_score * 0.30 +
                       sent_score * 0.20 + breadth_score * 0.15))

        if overall >= 65:   regime = "risk_on"
        elif overall >= 40: regime = "neutral"
        elif overall >= 20: regime = "risk_off"
        else:               regime = "panic"

        return {
            "regime": regime,
            "overall": overall,
            "momentum": mom_score,
            "volatility": vol_score,
            "sentiment": sent_score,
            "breadth": breadth_score,
            "vix": round(vix_v, 1),
        }
    except Exception:
        return {
            "regime": "neutral",
            "overall": 50,
            "momentum": 50,
            "volatility": 50,
            "sentiment": 50,
            "breadth": 50,
            "vix": 20.0,
        }


# ── 52-Week Range ─────────────────────────────────────────────────────────────
def compute_52w_range(sym: str) -> dict | None:
    try:
        df = fetch_ohlcv(sym, "1y")
        if df.empty:
            return None
        high = float(df["High"].max())
        low  = float(df["Low"].min())
        current = float(df["Close"].iloc[-1])
        pct = (current - low) / (high - low) * 100 if high != low else 50
        return {"high": high, "low": low, "current": current, "pct": round(pct, 1)}
    except Exception:
        return None


# ── Correlation Matrix ────────────────────────────────────────────────────────
@st.cache_data(ttl=300)
def compute_correlation(tickers: list[str], period: str = "3mo") -> pd.DataFrame | None:
    try:
        raw = yf.download(tickers, period=period, interval="1d",
                          auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            closes = raw["Close"]
        else:
            closes = raw[["Close"]]
        closes = closes.dropna()
        if closes.empty:
            return None
        returns = closes.pct_change().dropna()
        return returns.corr().round(2)
    except Exception:
        return None


# ── Format Helpers ────────────────────────────────────────────────────────────
def fmt_price(val, name="") -> str:
    if val is None: return "—"
    if val > 10000:  return f"{val:,.0f}"
    elif val > 100:  return f"{val:.1f}"
    elif val > 1:    return f"{val:.2f}"
    else:            return f"{val:.4f}"


def fmt_pct(val, decimals=2) -> str:
    if val is None: return "—"
    return f"{val:+.{decimals}f}%"


def color_class(val) -> str:
    if val is None: return "cell-neu"
    if val > 0:     return "cell-up-bg"
    if val < 0:     return "cell-dn-bg"
    return "cell-neu"


def up_dn(val) -> str:
    if val is None: return ""
    return "up" if val >= 0 else "dn"
