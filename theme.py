# utils/theme.py
# ─── Theme CSS & i18n ────────────────────────────────────────────────────────

THEMES = {
    "dark": {
        "--bg":           "#141418",
        "--bg2":          "#1a1a20",
        "--card":         "#1e1e2a",
        "--card2":        "#252535",
        "--nav":          "#111118",
        "--nav-active":   "rgba(0,201,138,0.13)",
        "--nav-text":     "#9090b0",
        "--nav-act-text": "#00c98a",
        "--nav-border":   "rgba(255,255,255,0.07)",
        "--green":        "#00c98a",
        "--green2":       "rgba(0,201,138,0.13)",
        "--red":          "#f05555",
        "--red2":         "rgba(240,85,85,0.13)",
        "--blue":         "#4d9fff",
        "--blue2":        "rgba(77,159,255,0.13)",
        "--orange":       "#f0a030",
        "--orange2":      "rgba(240,160,48,0.13)",
        "--purple":       "#a888f8",
        "--purple2":      "rgba(168,136,248,0.13)",
        "--text1":        "#e8e8f0",
        "--text2":        "#a8a8c0",
        "--text3":        "#707088",
        "--border":       "rgba(255,255,255,0.09)",
        "--border2":      "rgba(255,255,255,0.05)",
    },
    "light": {
        "--bg":           "#f5f4ef",
        "--bg2":          "#eeede8",
        "--card":         "#ffffff",
        "--card2":        "#f8f7f2",
        "--nav":          "#1e2140",
        "--nav-active":   "rgba(0,160,110,0.13)",
        "--nav-text":     "#9098b8",
        "--nav-act-text": "#00a06e",
        "--nav-border":   "rgba(255,255,255,0.10)",
        "--green":        "#0a8f5c",
        "--green2":       "rgba(10,143,92,0.10)",
        "--red":          "#cc3333",
        "--red2":         "rgba(204,51,51,0.10)",
        "--blue":         "#1a6fd4",
        "--blue2":        "rgba(26,111,212,0.10)",
        "--orange":       "#c07010",
        "--orange2":      "rgba(192,112,16,0.10)",
        "--purple":       "#7050c0",
        "--purple2":      "rgba(112,80,192,0.10)",
        "--text1":        "#1a1d2e",
        "--text2":        "#4a5070",
        "--text3":        "#8890aa",
        "--border":       "rgba(0,0,0,0.09)",
        "--border2":      "rgba(0,0,0,0.05)",
    },
    "eye": {
        "--bg":           "#18180f",
        "--bg2":          "#1e1e14",
        "--card":         "#222218",
        "--card2":        "#282820",
        "--nav":          "#141410",
        "--nav-active":   "rgba(90,180,120,0.15)",
        "--nav-text":     "#909070",
        "--nav-act-text": "#5ab478",
        "--nav-border":   "rgba(255,255,240,0.07)",
        "--green":        "#5ab478",
        "--green2":       "rgba(90,180,120,0.14)",
        "--red":          "#c85050",
        "--red2":         "rgba(200,80,80,0.14)",
        "--blue":         "#5080c8",
        "--blue2":        "rgba(80,128,200,0.14)",
        "--orange":       "#c89040",
        "--orange2":      "rgba(200,144,64,0.14)",
        "--purple":       "#9878d8",
        "--purple2":      "rgba(152,120,216,0.14)",
        "--text1":        "#d4d0b8",
        "--text2":        "#a0a080",
        "--text3":        "#707058",
        "--border":       "rgba(255,255,200,0.08)",
        "--border2":      "rgba(255,255,200,0.04)",
    },
}

FONT_SIZES = {"sm": "13px", "md": "14px", "lg": "16px"}

def get_css_vars(theme: str) -> str:
    t = THEMES.get(theme, THEMES["dark"])
    return "\n".join(f"  {k}: {v};" for k, v in t.items())


def build_global_css(theme: str, font_size: str) -> str:
    css_vars = get_css_vars(theme)
    fs = FONT_SIZES.get(font_size, "14px")
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+HK:wght@300;400;500;700&family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {{
{css_vars}
  --font: 'Noto Sans HK', 'Inter', sans-serif;
  --mono: 'Inter', monospace;
  --base-size: {fs};
}}

html, body, [class*="css"] {{
  font-family: var(--font) !important;
  font-size: var(--base-size) !important;
  background-color: var(--bg) !important;
  color: var(--text1) !important;
}}

.stApp {{
  background-color: var(--bg) !important;
}}

/* Hide Streamlit chrome */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {{
  background-color: var(--nav) !important;
  border-right: 1px solid var(--nav-border) !important;
  min-width: 230px !important;
  max-width: 230px !important;
}}
section[data-testid="stSidebar"] * {{
  color: var(--nav-text) !important;
}}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {{
  background: var(--card) !important;
  border-radius: 10px !important;
  padding: 4px !important;
  gap: 4px !important;
  border: 1px solid var(--border) !important;
}}
.stTabs [data-baseweb="tab"] {{
  background: transparent !important;
  border-radius: 8px !important;
  color: var(--text2) !important;
  font-size: 13px !important;
  font-weight: 400 !important;
  padding: 8px 16px !important;
  border: none !important;
}}
.stTabs [aria-selected="true"] {{
  background: var(--green) !important;
  color: #111118 !important;
  font-weight: 700 !important;
}}
.stTabs [data-baseweb="tab-panel"] {{
  background: transparent !important;
  padding: 16px 0 !important;
}}

/* ── BUTTONS ── */
.stButton > button {{
  background: var(--card2) !important;
  color: var(--text1) !important;
  border: 1px solid var(--border) !important;
  border-radius: 9px !important;
  font-family: var(--font) !important;
  font-size: 13px !important;
  padding: 8px 16px !important;
  transition: all .15s !important;
}}
.stButton > button:hover {{
  border-color: var(--green) !important;
  color: var(--green) !important;
}}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {{
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 9px !important;
  color: var(--text1) !important;
  font-family: var(--font) !important;
  font-size: 13px !important;
}}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {{
  border-color: var(--green) !important;
  box-shadow: 0 0 0 2px var(--green2) !important;
}}

/* ── METRIC CARDS ── */
[data-testid="metric-container"] {{
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 13px !important;
  padding: 16px 18px !important;
}}
[data-testid="metric-container"] label {{
  color: var(--text3) !important;
  font-size: 11px !important;
  text-transform: uppercase !important;
  letter-spacing: .5px !important;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
  color: var(--text1) !important;
  font-size: 28px !important;
  font-weight: 800 !important;
  font-family: var(--mono) !important;
}}
[data-testid="stMetricDelta"] {{
  font-size: 13px !important;
  font-weight: 600 !important;
}}

/* ── DATAFRAMES ── */
.stDataFrame {{
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 13px !important;
  overflow: hidden !important;
}}

/* ── PLOTLY ── */
.js-plotly-plot .plotly {{
  background: transparent !important;
}}

/* ── DIVIDER ── */
hr {{
  border-color: var(--border) !important;
  margin: 12px 0 !important;
}}

/* ── ALERT BANNER ── */
.alert-banner {{
  padding: 10px 16px;
  border-radius: 9px;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
}}
.alert-red {{
  background: var(--red2);
  border: 1px solid rgba(240,85,85,.25);
  color: var(--red);
}}
.alert-orange {{
  background: var(--orange2);
  border: 1px solid rgba(240,160,48,.25);
  color: var(--orange);
}}
.alert-green {{
  background: var(--green2);
  border: 1px solid rgba(0,201,138,.25);
  color: var(--green);
}}
.alert-eye {{
  background: rgba(90,180,120,0.10);
  border: 1px solid rgba(90,180,120,.20);
  color: #8ab898;
  font-size: 12px;
}}

/* ── KPI CARD ── */
.kpi-card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 13px;
  padding: 18px;
  position: relative;
  overflow: hidden;
  transition: border-color .2s;
}}
.kpi-card:hover {{
  border-color: rgba(255,255,255,.18);
}}
.kpi-accent {{
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  border-radius: 13px 13px 0 0;
}}
.kpi-label {{
  font-size: 11px;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: .5px;
  font-weight: 500;
  margin-bottom: 8px;
}}
.kpi-value {{
  font-size: 30px;
  font-weight: 800;
  font-family: var(--mono);
  letter-spacing: -1px;
  font-variant-numeric: tabular-nums;
  color: var(--text1);
  line-height: 1;
}}
.kpi-change {{
  font-size: 13px;
  font-weight: 600;
  margin-top: 7px;
}}
.kpi-note {{
  font-size: 11px;
  color: var(--text3);
  font-weight: 400;
  margin-left: 4px;
}}

/* ── SIGNAL BADGE ── */
.badge-green {{
  background: var(--green2);
  color: var(--green);
  border: 1px solid rgba(0,201,138,.22);
  font-size: 11px; font-weight: 700;
  padding: 3px 10px; border-radius: 6px;
}}
.badge-red {{
  background: var(--red2);
  color: var(--red);
  border: 1px solid rgba(240,85,85,.22);
  font-size: 11px; font-weight: 700;
  padding: 3px 10px; border-radius: 6px;
}}
.badge-orange {{
  background: var(--orange2);
  color: var(--orange);
  border: 1px solid rgba(240,160,48,.22);
  font-size: 11px; font-weight: 700;
  padding: 3px 10px; border-radius: 6px;
}}

/* ── LOCK OVERLAY ── */
.lock-overlay {{
  position: relative;
  filter: blur(3px);
  pointer-events: none;
  user-select: none;
}}
.lock-msg {{
  text-align: center;
  padding: 20px;
  color: var(--text3);
  font-size: 13px;
}}
.lock-msg .lock-icon {{
  font-size: 24px;
  margin-bottom: 8px;
}}
.upgrade-btn {{
  background: var(--green);
  color: #111118;
  border: none;
  border-radius: 9px;
  padding: 8px 20px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  margin-top: 8px;
}}

/* ── TABLE ── */
.miq-table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}}
.miq-table th {{
  font-size: 10px;
  font-weight: 600;
  color: var(--text3);
  text-transform: uppercase;
  letter-spacing: .8px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  text-align: right;
}}
.miq-table th:first-child {{ text-align: left; }}
.miq-table td {{
  padding: 9px 12px;
  border-bottom: 1px solid var(--border2);
  text-align: right;
  font-family: var(--mono);
  font-variant-numeric: tabular-nums;
  font-size: 13px;
  color: var(--text1);
}}
.miq-table td:first-child {{
  text-align: left;
  font-family: var(--font);
  font-weight: 500;
  color: var(--text1);
}}
.miq-table tr:last-child td {{ border-bottom: none; }}
.miq-table tr:hover td {{ background: var(--card2); }}
.cell-up {{ color: var(--green) !important; font-weight: 600 !important; }}
.cell-dn {{ color: var(--red) !important; font-weight: 600 !important; }}
.cell-neu {{ color: var(--text3) !important; }}
.cell-up-bg {{ background: var(--green2) !important; border-radius: 5px; padding: 2px 7px !important; color: var(--green) !important; font-weight: 600 !important; }}
.cell-dn-bg {{ background: var(--red2) !important; border-radius: 5px; padding: 2px 7px !important; color: var(--red) !important; font-weight: 600 !important; }}

/* ── SECTION HEADER ── */
.sec-hd {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}}
.sec-title {{
  font-size: 14px;
  font-weight: 600;
  color: var(--text1);
}}
.sec-sub {{
  font-size: 11px;
  color: var(--text3);
  margin-top: 2px;
}}

/* ── USER PILL ── */
.user-pill {{
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 11px;
}}
.user-avatar {{
  width: 36px; height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--green), var(--blue));
  display: flex; align-items: center; justify-content: center;
  font-size: 14px; font-weight: 700; color: #111118;
  flex-shrink: 0;
}}
.user-name {{ font-size: 14px; font-weight: 600; color: var(--text1); }}
.user-role {{ font-size: 11px; color: var(--text3); margin-top: 2px; }}
.pro-badge {{
  background: var(--green2); color: var(--green);
  font-size: 10px; font-weight: 700;
  padding: 3px 9px; border-radius: 6px;
  border: 1px solid rgba(0,201,138,.22);
  letter-spacing: .3px;
}}

/* ── REGIME BARS ── */
.regime-bar-wrap {{ margin-bottom: 9px; }}
.regime-bar-hd {{
  display: flex; justify-content: space-between;
  font-size: 12px; color: var(--text2); margin-bottom: 5px;
}}
.regime-bar-track {{
  height: 6px; border-radius: 3px;
  background: var(--bg2); overflow: hidden;
}}
.regime-bar-fill {{ height: 100%; border-radius: 3px; }}

/* ── AI TIP ── */
.ai-tip {{
  padding: 12px 14px;
  background: var(--green2);
  border-radius: 10px;
  border-left: 3px solid var(--green);
  margin-top: 12px;
}}
.ai-tip-label {{
  font-size: 10px; color: var(--green);
  font-weight: 700; margin-bottom: 4px;
  letter-spacing: .5px; text-transform: uppercase;
}}
.ai-tip-text {{
  font-size: 13px; color: var(--text2); line-height: 1.6;
}}

/* ── PROGRESS BAR (52W) ── */
.prog-wrap {{
  background: var(--bg2);
  border-radius: 4px; height: 6px;
  overflow: hidden; margin: 4px 0;
}}
.prog-fill {{
  height: 100%; border-radius: 4px;
  background: linear-gradient(90deg, var(--red), var(--orange), var(--green));
}}

/* ── LOGIN ── */
.login-wrap {{
  max-width: 400px;
  margin: 60px auto;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 36px 32px;
}}
.login-logo {{
  text-align: center;
  margin-bottom: 28px;
}}
.login-title {{
  font-size: 22px; font-weight: 700;
  color: var(--text1); margin-bottom: 4px;
}}
.login-sub {{
  font-size: 13px; color: var(--text3);
}}

/* ── SCROLLBAR ── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: var(--text3); }}
</style>
"""
