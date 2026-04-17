# utils/charts.py
# ─── Plotly Chart Builders ────────────────────────────────────────────────────

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

THEME_COLORS = {
    "dark":  {"bg": "#1e1e2a", "grid": "rgba(255,255,255,0.05)", "tick": "#707088", "green": "#00c98a", "red": "#f05555"},
    "light": {"bg": "#ffffff", "grid": "rgba(0,0,0,0.05)",       "tick": "#8890aa", "green": "#0a8f5c", "red": "#cc3333"},
    "eye":   {"bg": "#222218", "grid": "rgba(255,255,200,0.05)", "tick": "#707058", "green": "#5ab478", "red": "#c85050"},
}


def _tc(theme): return THEME_COLORS.get(theme, THEME_COLORS["dark"])


def make_sector_bar(data: dict, period: str = "1m", theme: str = "dark", height: int = 200) -> go.Figure:
    c = _tc(theme)
    names, vals = [], []
    for name, d in data.items():
        if d and d.get(period) is not None:
            names.append(name)
            vals.append(round(d[period], 2))
    if not names:
        return go.Figure()
    colors = [c["green"] if v >= 0 else c["red"] for v in vals]
    fig = go.Figure(go.Bar(
        x=names, y=vals,
        marker_color=[f"rgba({int(col[1:3],16)},{int(col[3:5],16)},{int(col[5:7],16)},0.75)" for col in colors],
        marker_line_color=colors,
        marker_line_width=1.5,
        marker_cornerradius=5,
        text=[f"{v:+.1f}%" for v in vals],
        textposition="outside",
        textfont=dict(size=10, color=c["tick"]),
    ))
    fig.update_layout(
        paper_bgcolor=c["bg"], plot_bgcolor=c["bg"],
        height=height,
        margin=dict(l=8, r=8, t=8, b=50),
        xaxis=dict(showgrid=False, tickfont=dict(size=10, color=c["tick"]), tickangle=35),
        yaxis=dict(showgrid=True, gridcolor=c["grid"], ticksuffix="%",
                   tickfont=dict(size=10, color=c["tick"]), zeroline=True,
                   zerolinecolor=c["tick"], zerolinewidth=0.5, showline=False),
        showlegend=False,
        font=dict(family="Inter, sans-serif"),
    )
    return fig


def make_candlestick(df: pd.DataFrame, sym: str, theme: str = "dark", height: int = 360) -> go.Figure:
    if df.empty:
        return go.Figure()
    c = _tc(theme)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.72, 0.28], vertical_spacing=0.04)

    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"],
        low=df["Low"], close=df["Close"],
        increasing_line_color=c["green"], increasing_fillcolor=c["green"],
        decreasing_line_color=c["red"],   decreasing_fillcolor=c["red"],
        name=sym, line_width=1,
    ), row=1, col=1)

    # EMA 20
    if len(df) >= 20:
        ema20 = df["Close"].ewm(span=20).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=ema20, line=dict(color="#f0a030", width=1.5),
            name="EMA 20", hovertemplate="%{y:.2f}"
        ), row=1, col=1)

    # EMA 50
    if len(df) >= 50:
        ema50 = df["Close"].ewm(span=50).mean()
        fig.add_trace(go.Scatter(
            x=df.index, y=ema50, line=dict(color="#a888f8", width=1.2, dash="dot"),
            name="EMA 50", hovertemplate="%{y:.2f}"
        ), row=1, col=1)

    # Volume
    if "Volume" in df.columns:
        vol_colors = [c["green"] if df["Close"].iloc[i] >= df["Open"].iloc[i]
                      else c["red"] for i in range(len(df))]
        fig.add_trace(go.Bar(
            x=df.index, y=df["Volume"],
            marker_color=[col.replace(")", ",0.5)").replace("rgb", "rgba") for col in vol_colors],
            name="Volume", showlegend=False,
        ), row=2, col=1)

    axis_common = dict(showgrid=True, gridcolor=c["grid"],
                       showline=False, tickfont=dict(size=10, color=c["tick"]))
    fig.update_layout(
        paper_bgcolor=c["bg"], plot_bgcolor=c["bg"],
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(**axis_common, rangeslider_visible=False),
        xaxis2=dict(**axis_common),
        yaxis=dict(**axis_common),
        yaxis2=dict(**axis_common, tickformat=".2s"),
        legend=dict(font=dict(size=10, color=c["tick"]),
                    bgcolor="rgba(0,0,0,0)", orientation="h",
                    yanchor="bottom", y=1.01, xanchor="left", x=0),
        font=dict(family="Inter"),
        hovermode="x unified",
        hoverlabel=dict(bgcolor=c["bg"], font_size=11,
                        bordercolor=c["tick"]),
    )
    return fig


def make_perf_compare(histories: dict, theme: str = "dark", height: int = 280) -> go.Figure:
    """Normalized performance comparison from same start point"""
    c = _tc(theme)
    palette = [c["green"], c["red"], "#4d9fff", "#f0a030", "#a888f8",
               "#00c9ff", "#ff8c00", "#e040fb", "#00e5ff", "#69f0ae"]
    fig = go.Figure()
    for i, (name, prices) in enumerate(histories.items()):
        if not prices or len(prices) < 2:
            continue
        base = prices[0]
        if base == 0: continue
        norm = [p / base * 100 for p in prices]
        col = palette[i % len(palette)]
        fig.add_trace(go.Scatter(
            y=norm, mode="lines", name=name,
            line=dict(color=col, width=2),
            hovertemplate=f"{name}: %{{y:.1f}}<extra></extra>",
        ))
    fig.add_hline(y=100, line_dash="dash", line_color=c["tick"], line_width=0.8)
    fig.update_layout(
        paper_bgcolor=c["bg"], plot_bgcolor=c["bg"],
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, tickfont=dict(size=10, color=c["tick"]), showticklabels=False),
        yaxis=dict(showgrid=True, gridcolor=c["grid"], ticksuffix="",
                   tickfont=dict(size=10, color=c["tick"]), showline=False),
        legend=dict(font=dict(size=11, color=c["tick"]),
                    bgcolor="rgba(0,0,0,0)", orientation="h",
                    yanchor="bottom", y=1.01, xanchor="left", x=0),
        font=dict(family="Inter"),
        hovermode="x unified",
    )
    return fig


def make_correlation_heatmap(corr: pd.DataFrame, theme: str = "dark", height: int = 300) -> go.Figure:
    c = _tc(theme)
    z = corr.values
    labels = list(corr.columns)
    text = [[f"{z[i][j]:.2f}" for j in range(len(labels))] for i in range(len(labels))]

    colorscale = [
        [0.0, c["red"]],
        [0.5, c["bg"]],
        [1.0, c["green"]],
    ]
    fig = go.Figure(go.Heatmap(
        z=z, x=labels, y=labels,
        text=text, texttemplate="%{text}",
        colorscale=colorscale, zmid=0,
        zmin=-1, zmax=1,
        showscale=True,
        colorbar=dict(thickness=10, tickfont=dict(size=9, color=c["tick"])),
        textfont=dict(size=11),
    ))
    fig.update_layout(
        paper_bgcolor=c["bg"], plot_bgcolor=c["bg"],
        height=height,
        margin=dict(l=10, r=50, t=10, b=10),
        xaxis=dict(tickfont=dict(size=10, color=c["tick"])),
        yaxis=dict(tickfont=dict(size=10, color=c["tick"]), autorange="reversed"),
        font=dict(family="Inter"),
    )
    return fig


def make_bar_comparison(names: list, vals: list, label: str, theme: str = "dark", height: int = 240) -> go.Figure:
    c = _tc(theme)
    colors = [c["green"] if v >= 0 else c["red"] for v in vals]
    fig = go.Figure(go.Bar(
        x=names, y=vals,
        marker_color=[f"rgba({int(col[1:3],16)},{int(col[3:5],16)},{int(col[5:7],16)},0.75)" for col in colors],
        marker_line_color=colors,
        marker_line_width=1.5,
        marker_cornerradius=5,
        text=[f"{v:+.1f}%" for v in vals],
        textposition="outside",
        textfont=dict(size=10, color=c["tick"]),
    ))
    fig.update_layout(
        paper_bgcolor=c["bg"], plot_bgcolor=c["bg"],
        height=height,
        margin=dict(l=8, r=8, t=8, b=55),
        xaxis=dict(showgrid=False, tickfont=dict(size=10, color=c["tick"]), tickangle=35),
        yaxis=dict(showgrid=True, gridcolor=c["grid"], ticksuffix="%",
                   tickfont=dict(size=10, color=c["tick"]), zeroline=True,
                   zerolinecolor=c["tick"], zerolinewidth=0.5, showline=False),
        showlegend=False,
        title=dict(text=label, font=dict(size=13, color=c["tick"])),
        font=dict(family="Inter"),
    )
    return fig


def make_sparkline(prices: list, color: str, height: int = 50) -> go.Figure:
    if not prices or len(prices) < 2:
        return go.Figure()
    fig = go.Figure(go.Scatter(
        y=prices, mode="lines",
        line=dict(color=color, width=1.8),
        fill="tozeroy",
        fillcolor=color.replace(")", ",0.10)").replace("rgb", "rgba") if color.startswith("rgb") else color + "1a",
        hoverinfo="skip",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        height=height, margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False), yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig


def make_vix_term_bar(vix_data: dict, theme: str = "dark", height: int = 180) -> go.Figure:
    c = _tc(theme)
    names = list(vix_data.keys())
    vals  = [vix_data[n] or 0 for n in names]
    max_v = max(vals) if vals else 1
    norm  = [v / max_v for v in vals]

    colors = ["#4d9fff", "#5580e8", "#8080e8", "#a888f8"]
    fig = go.Figure(go.Bar(
        x=names, y=vals,
        marker_color=colors[:len(names)],
        marker_cornerradius=4,
        text=[f"{v:.1f}" for v in vals],
        textposition="outside",
        textfont=dict(size=11, color=c["tick"]),
    ))
    fig.update_layout(
        paper_bgcolor=c["bg"], plot_bgcolor=c["bg"],
        height=height,
        margin=dict(l=8, r=8, t=8, b=8),
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color=c["tick"])),
        yaxis=dict(showgrid=True, gridcolor=c["grid"],
                   tickfont=dict(size=10, color=c["tick"]), showline=False),
        showlegend=False,
        font=dict(family="Inter"),
    )
    return fig


def make_atr_bar(atr_data: dict, theme: str = "dark", height: int = 220) -> go.Figure:
    c = _tc(theme)
    names = list(atr_data.keys())
    vals  = [atr_data[n] for n in names]
    sorted_pairs = sorted(zip(vals, names))
    vals, names = zip(*sorted_pairs) if sorted_pairs else ([], [])
    fig = go.Figure(go.Bar(
        y=list(names), x=list(vals),
        orientation="h",
        marker_color=[c["green"] if v < 3 else c["orange"] if v < 6 else c["red"]
                      for v in vals
                      for _ in [None]
                      ] if vals else [],
        marker_cornerradius=4,
        text=[f"{v:.2f}%" for v in vals],
        textposition="outside",
        textfont=dict(size=11, color=c["tick"]),
    ))
    fig.update_layout(
        paper_bgcolor=c["bg"], plot_bgcolor=c["bg"],
        height=max(height, len(names) * 35 + 40),
        margin=dict(l=10, r=50, t=8, b=8),
        xaxis=dict(showgrid=True, gridcolor=c["grid"], ticksuffix="%",
                   tickfont=dict(size=10, color=c["tick"]), showline=False),
        yaxis=dict(showgrid=False, tickfont=dict(size=12, color=c["tick"])),
        showlegend=False,
        font=dict(family="Inter"),
    )
    return fig
