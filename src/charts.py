"""Système visuel commun : tokens, style Plotly, figures éditoriales, fiches d'indicateurs.

Direction « Données, éditorialement » : papier ivoire, encre noire, filets gris chaud,
rouge en signal. Palette catégorielle validée (contraste, daltonisme) sur fond #F5F3EE.
"""
from __future__ import annotations

import html

import plotly.graph_objects as go
import streamlit as st

from referentiels import CATEGORIES, COULEURS_CATEGORIES, COULEURS_OPERATEURS

PAPER = "#F5F3EE"
PAPER_2 = "#ECE9E2"
INK = "#181818"
INK_2 = "#66645F"
RULE = "#D8D5CE"
ACCENT = "#CC1505"
BLUE = "#315C9B"
GREEN = "#3F8A4E"
OCHRE = "#C99A1E"
NEUTRE = "#B9B5AC"
SERIES = [BLUE, ACCENT, GREEN, OCHRE]
SEQ = ["#EEF1F6", "#C9D4E6", "#97AACC", "#6481B2", "#315C9B", "#22426F", "#142944"]
SOURCE = "Source : ANFR, data.gouv.fr. Traitement : M. Louet."

CONFIG = {"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"]}

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Inter+Tight:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
:root {{
  --paper:{PAPER}; --paper-2:{PAPER_2}; --ink:{INK}; --ink-2:{INK_2}; --rule:{RULE}; --accent:{ACCENT};
}}
html, body, .stMarkdown p, .stMarkdown li, td, th {{ font-family: 'Inter', sans-serif; }}
h1, h2, h3, h4 {{ font-family: 'Inter Tight', sans-serif !important; color: var(--ink); text-wrap: balance; }}
h1 {{ font-size: clamp(2.2rem, 4.2vw, 3.6rem) !important; font-weight: 700 !important;
      letter-spacing: -0.03em; line-height: 1.0 !important; padding: 0 0 .4rem 0 !important; }}
h2 {{ font-size: 1.75rem !important; font-weight: 600 !important; letter-spacing: -0.02em;
      margin-top: 2.6rem !important; padding-top: .9rem !important; border-top: 1px solid var(--ink); }}
h3 {{ font-size: 1.2rem !important; font-weight: 600 !important; letter-spacing: -0.01em; }}
.block-container {{ padding-top: 1.6rem; max-width: 1240px; }}
.stMarkdown p, .stMarkdown li {{ max-width: 68ch; font-size: 1.02rem; line-height: 1.55; }}
::selection {{ background: var(--accent); color: var(--paper); }}
a {{ color: var(--ink); text-underline-offset: 3px; text-decoration-color: var(--accent); }}
:focus-visible {{ outline: 2px solid var(--accent) !important; outline-offset: 2px; }}
* {{ scrollbar-color: var(--rule) transparent; }}
td, .num {{ font-variant-numeric: tabular-nums; }}
[data-testid="stSidebar"] {{ border-right: 1px solid var(--rule); }}
[data-testid="stSidebarNav"] a span {{ font-family: 'Inter Tight', sans-serif; font-size: .98rem; }}
hr {{ border-color: var(--rule) !important; }}
[data-testid="stIconMaterial"] {{ font-family: 'Material Symbols Rounded' !important; }}
[data-baseweb="tag"] {{ background: var(--ink) !important; border-radius: 2px !important; }}
[data-baseweb="tag"] span {{ color: var(--paper) !important; font-size: .8rem; }}
[data-testid="stExpander"] details {{ border-radius: 0; border-color: var(--rule); }}

.head {{ font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: .06em; text-transform: uppercase;
        color: var(--ink-2); display: flex; justify-content: space-between; gap: 1rem; flex-wrap: wrap;
        border-bottom: 1px solid var(--rule); padding-bottom: .45rem; margin-bottom: 2rem; }}
.stMarkdown p.lead {{ font-size: 1.32rem; line-height: 1.4; max-width: 52ch; text-wrap: pretty; color: var(--ink); margin: .2rem 0 1.4rem 0; }}
.fig {{ display: flex; gap: .8rem; align-items: baseline; margin: 1.8rem 0 .2rem 0; }}
.fig .n {{ font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: .06em; color: var(--accent);
           text-transform: uppercase; white-space: nowrap; }}
.fig .t {{ font-family: 'Inter Tight', sans-serif; font-size: 1.12rem; font-weight: 600; color: var(--ink); }}
.stMarkdown p.note {{ font-size: .9rem; line-height: 1.45; color: var(--ink); max-width: 72ch; margin: .1rem 0 .2rem 0; }}
.note b {{ font-weight: 600; }}
.src {{ font-family: 'IBM Plex Mono', monospace; font-size: 10.5px; letter-spacing: .04em; color: var(--ink-2);
        margin-bottom: 1.2rem; }}
.kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 0 28px; margin: .6rem 0 1rem 0; }}
.kpi {{ border-top: 1px solid var(--ink); padding: .55rem 0 .9rem 0; }}
.kpi .l {{ font-family: 'IBM Plex Mono', monospace; font-size: 11px; letter-spacing: .06em; text-transform: uppercase;
           color: var(--ink-2); min-height: 2.6em; }}
.kpi .v {{ font-family: 'Inter Tight', sans-serif; font-size: 2.1rem; font-weight: 600; letter-spacing: -0.02em;
           line-height: 1.1; font-variant-numeric: tabular-nums; color: var(--ink); }}
.kpi .d {{ font-size: .82rem; color: var(--ink-2); margin-top: .15rem; font-variant-numeric: tabular-nums; }}
.kpi .d.up {{ color: var(--accent); }}
.flag {{ border: 1px solid var(--accent); padding: .7rem .9rem; margin: .6rem 0 1rem 0; max-width: 78ch; font-size: .95rem; }}
.steps {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 0 20px; }}
.steps div {{ border-top: 1px solid var(--rule); padding-top: .5rem; font-size: .9rem; color: var(--ink-2); }}
.steps b {{ display: block; font-family: 'Inter Tight', sans-serif; color: var(--ink); font-size: 1rem; }}
</style>
"""


def style(fig: go.Figure, height: int = 380, legend: bool = True) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=4, r=12, t=36 if legend else 12, b=8),
        font=dict(family="Inter, sans-serif", size=12.5, color=INK),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=legend,
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="left", x=0, title=None,
                    font=dict(size=12, color=INK_2)),
        hoverlabel=dict(bgcolor=PAPER, bordercolor=INK, font=dict(family="Inter, sans-serif", size=12, color=INK)),
        bargap=0.28,
        colorway=SERIES,
    )
    fig.update_xaxes(showgrid=False, linecolor=INK, linewidth=1, ticks="outside", tickcolor=RULE,
                     tickfont=dict(color=INK_2), title_font=dict(size=12, color=INK_2))
    fig.update_yaxes(gridcolor=RULE, gridwidth=1, zeroline=False, linecolor="rgba(0,0,0,0)",
                     tickfont=dict(color=INK_2), title_font=dict(size=12, color=INK_2))
    fig.update_traces(marker_line_width=2, marker_line_color=PAPER, selector=dict(type="bar"))
    return fig


def figure(num: str, titre: str) -> None:
    st.markdown(f"<div class='fig'><span class='n'>Fig. {num}</span><span class='t'>{html.escape(titre)}</span></div>",
                unsafe_allow_html=True)


def note(texte: str, source: bool = True) -> None:
    """Phrase « à remarquer » sous une figure (HTML autorisé), puis la source."""
    st.markdown((f"<p class='note'>{texte}</p>" if texte else "") + (f"<div class='src'>{SOURCE}</div>" if source else ""),
                unsafe_allow_html=True)


def plot(fig: go.Figure, height: int = 380, legend: bool = True) -> None:
    st.plotly_chart(style(fig, height, legend), width="stretch", config=CONFIG)


def kpis(items: list[tuple[str, str, str | None, bool]]) -> None:
    """Fiche d'indicateurs : (libellé, valeur, commentaire, signal)."""
    cells = "".join(
        f"<div class='kpi'><div class='l'>{html.escape(l)}</div><div class='v'>{html.escape(v)}</div>"
        f"<div class='d{' up' if s else ''}'>{html.escape(d) if d else '&nbsp;'}</div></div>"
        for l, v, d, s in items
    )
    st.markdown(f"<div class='kpis'>{cells}</div>", unsafe_allow_html=True)


def flag(texte: str) -> None:
    st.markdown(f"<div class='flag'>{texte}</div>", unsafe_allow_html=True)


__all__ = ["style", "figure", "note", "plot", "kpis", "flag", "CSS", "SEQ", "SERIES", "PAPER", "INK", "INK_2", "RULE",
           "ACCENT", "BLUE", "GREEN", "OCHRE", "NEUTRE", "CONFIG", "CATEGORIES", "COULEURS_CATEGORIES",
           "COULEURS_OPERATEURS"]


def head(section: str, perimetre: str, export: str) -> None:
    """Titre courant de magazine : rubrique, périmètre, date de l'export."""
    d = f"{export[6:]}.{export[4:6]}.{export[:4]}"
    st.markdown(
        f"<div class='head'><span>Infrastructures mobiles · {html.escape(section)}</span>"
        f"<span>{html.escape(perimetre)}</span><span>Registre ANFR · {d}</span></div>",
        unsafe_allow_html=True,
    )
