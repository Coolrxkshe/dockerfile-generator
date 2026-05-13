import streamlit as st
from pathlib import Path
import tempfile
import os
import ollama as ollama_lib

from analyzer import detect_project, read_project_files
from prompt import build_prompt
from llm import ask_ollama, extract_dockerfile
from output import save_dockerfile
from validator import validate_dockerfile
from models import get_installed_models, is_model_available, benchmark_models

# ── Page config ───────────────────────────────────────────
st.set_page_config(
    page_title="Dockerfile Generator",
    page_icon="🐳",
    layout="centered"
)

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2.5rem; max-width: 800px; }

/* ── App Background ── */
.stApp {
    background-color: #0c0f14;
    background-image:
        linear-gradient(180deg, #0c0f14 0%, #0e1219 100%);
}

/* scanline overlay */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,255,200,0.012) 2px,
        rgba(0,255,200,0.012) 4px
    );
    pointer-events: none;
    z-index: 0;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #080b10 !important;
    border-right: 1px solid rgba(0,230,180,0.12) !important;
}
[data-testid="stSidebar"] * { color: #8fa3b1 !important; font-family: 'DM Sans', sans-serif !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #e2eaf0 !important; letter-spacing: 0.01em !important; }

/* ── Expanders ── */
div[data-testid="stExpander"] {
    background: #111620;
    border: 1px solid rgba(0,230,180,0.1);
    border-radius: 6px;
    overflow: hidden;
}
div[data-testid="stExpander"] summary {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    color: #5ecfb1 !important;
    letter-spacing: 0.03em;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #111620;
    border: 1px solid rgba(0,230,180,0.12);
    border-top: 2px solid rgba(0,230,180,0.4);
    border-radius: 6px;
    padding: 1rem !important;
    transition: border-color 0.2s;
}
[data-testid="stMetric"]:hover {
    border-top-color: rgba(0,230,180,0.8);
}
[data-testid="stMetricLabel"] {
    color: #4a6070 !important;
    font-size: 11px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stMetricValue"] {
    color: #00e6b4 !important;
    font-size: 20px !important;
    font-weight: 600 !important;
    font-family: 'IBM Plex Mono', monospace !important;
}

/* ── Buttons ── */
.stButton > button {
    background: transparent !important;
    color: #00e6b4 !important;
    border: 1px solid rgba(0,230,180,0.5) !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    letter-spacing: 0.05em !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.18s ease !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    background: rgba(0,230,180,0.08) !important;
    border-color: #00e6b4 !important;
    box-shadow: 0 0 16px rgba(0,230,180,0.15), inset 0 0 8px rgba(0,230,180,0.04) !important;
    color: #00ffcc !important;
}
.stButton > button:active {
    transform: scale(0.98) !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    color: #5ecfb1 !important;
    border: 1px solid rgba(94,207,177,0.4) !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 13px !important;
    letter-spacing: 0.05em !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    transition: all 0.18s ease !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(94,207,177,0.08) !important;
    border-color: #5ecfb1 !important;
    box-shadow: 0 0 14px rgba(94,207,177,0.15) !important;
}

/* ── Inputs & Selects ── */
.stTextInput > div > div > input {
    background: #0d1117 !important;
    border: 1px solid rgba(0,230,180,0.15) !important;
    border-radius: 4px !important;
    color: #cce8e0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 13px !important;
    caret-color: #00e6b4;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus {
    border-color: rgba(0,230,180,0.5) !important;
    box-shadow: 0 0 0 3px rgba(0,230,180,0.08) !important;
}
.stTextInput > div > div > input::placeholder {
    color: #2e4050 !important;
}
.stSelectbox > div > div,
[data-baseweb="select"] > div {
    background: #0d1117 !important;
    border: 1px solid rgba(0,230,180,0.15) !important;
    border-radius: 4px !important;
    color: #cce8e0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Multiselect ── */
[data-baseweb="tag"] {
    background: rgba(0,230,180,0.12) !important;
    border: 1px solid rgba(0,230,180,0.3) !important;
    border-radius: 3px !important;
}
[data-baseweb="tag"] span {
    color: #00e6b4 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12px !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #0d1117 !important;
    border: 1px dashed rgba(0,230,180,0.2) !important;
    border-radius: 6px !important;
    padding: 1.2rem !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(0,230,180,0.4) !important;
}

/* ── Code blocks ── */
.stCodeBlock, code, pre {
    font-family: 'IBM Plex Mono', monospace !important;
    background: #060910 !important;
    border: 1px solid rgba(0,230,180,0.1) !important;
    border-left: 3px solid rgba(0,230,180,0.4) !important;
    border-radius: 4px !important;
    font-size: 12.5px !important;
    line-height: 1.7 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1117 !important;
    border-radius: 4px !important;
    padding: 3px !important;
    gap: 2px !important;
    border: 1px solid rgba(0,230,180,0.1) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 3px !important;
    color: #4a6070 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 500 !important;
    font-size: 12px !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    padding: 6px 18px !important;
    transition: all 0.15s ease !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,230,180,0.1) !important;
    color: #00e6b4 !important;
    border: 1px solid rgba(0,230,180,0.25) !important;
}

/* ── Alerts ── */
.stSuccess {
    background: rgba(0,100,70,0.15) !important;
    border: 1px solid rgba(0,230,180,0.25) !important;
    border-left: 3px solid #00e6b4 !important;
    border-radius: 4px !important;
}
.stError {
    background: rgba(180,30,30,0.12) !important;
    border: 1px solid rgba(255,80,80,0.2) !important;
    border-left: 3px solid #ff5050 !important;
    border-radius: 4px !important;
}
.stWarning {
    background: rgba(160,100,0,0.12) !important;
    border: 1px solid rgba(255,185,0,0.2) !important;
    border-left: 3px solid #ffb900 !important;
    border-radius: 4px !important;
}
.stInfo {
    background: rgba(0,80,180,0.12) !important;
    border: 1px solid rgba(60,140,255,0.2) !important;
    border-left: 3px solid #3c8cff !important;
    border-radius: 4px !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #00e6b4, #00aaff) !important;
    border-radius: 2px !important;
    box-shadow: 0 0 8px rgba(0,230,180,0.4) !important;
}
.stProgress > div > div {
    background: rgba(0,230,180,0.08) !important;
    border-radius: 2px !important;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid rgba(0,230,180,0.08) !important;
    margin: 1.5rem 0 !important;
}

/* ── Text ── */
p, li, label, span, .stMarkdown { color: #8fa3b1 !important; line-height: 1.7 !important; }
h1, h2, h3 { color: #ddeee8 !important; font-family: 'DM Sans', sans-serif !important; letter-spacing: -0.01em !important; }
h3 { font-size: 1.1rem !important; color: #cce8e0 !important; border-bottom: 1px solid rgba(0,230,180,0.08); padding-bottom: 0.5rem; }
.stCaption { color: #2e4050 !important; font-size: 11px !important; font-family: 'IBM Plex Mono', monospace !important; letter-spacing: 0.05em !important; }

/* ── Spinner ── */
[data-testid="stSpinner"] > div { border-top-color: #00e6b4 !important; }
</style>
""", unsafe_allow_html=True)

# ── Hero Header ───────────────────────────────────────────
st.markdown("""
<style>
@keyframes pulse-glow {
    0%, 100% { opacity: 0.6; }
    50% { opacity: 1; }
}
@keyframes flicker {
    0%, 100% { opacity: 1; }
    92% { opacity: 1; }
    93% { opacity: 0.85; }
    94% { opacity: 1; }
}
</style>
<div style="text-align:center; padding: 2.5rem 0 1.5rem; position: relative;">
    <div style="
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -60%);
        width: 320px; height: 120px;
        background: radial-gradient(ellipse, rgba(0,230,180,0.08) 0%, transparent 70%);
        pointer-events: none;
    "></div>
    <div style="
        display: inline-block;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.15em;
        color: #00e6b4;
        border: 1px solid rgba(0,230,180,0.3);
        padding: 4px 14px;
        border-radius: 2px;
        margin-bottom: 1.2rem;
        text-transform: uppercase;
        animation: pulse-glow 3s ease-in-out infinite;
    ">v1.0 · local · private</div>
    <h1 style="
        font-family: 'DM Sans', sans-serif;
        font-size: 2.6rem;
        font-weight: 600;
        color: #ddeee8;
        margin: 0 0 0.4rem;
        letter-spacing: -0.03em;
        animation: flicker 8s infinite;
    ">
        Dockerfile <span style="color: #00e6b4;">Generator</span>
    </h1>
    <p style="
        color: #2e4050;
        font-size: 13px;
        font-family: 'IBM Plex Mono', monospace;
        letter-spacing: 0.06em;
        margin: 0;
    ">powered by ollama &nbsp;·&nbsp; zero cloud &nbsp;·&nbsp; zero telemetry</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Shared data (used by sidebar + dashboard) ─────────────
langs = [
    ("🐍", "Python",  "FastAPI · Flask · Django"),
    ("🟩", "Node.js", "Express · Next.js · React"),
    ("🐹", "Go",      "Go Modules"),
    ("☕", "Java",    "Maven · Gradle"),
    ("🦀", "Rust",    "Cargo"),
]

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    installed = get_installed_models()
    installed_names = [m["name"] for m in installed]
    if not installed_names:
        installed_names = ["codellama"]

    active_model  = installed_names[0] if installed_names else "—"
    model_count   = len(installed_names)
    lang_count    = len(langs)
    is_online     = bool(installed)
    status_color  = "#00e6b4" if is_online else "#ff5050"
    status_text   = "ONLINE" if is_online else "OFFLINE"

    # ── sidebar CSS (scoped to sidebar content) ──
    st.markdown(f"""
<style>
@keyframes sb-blink {{
  0%,100% {{ opacity:1; }} 50% {{ opacity:0.25; }}
}}

/* ── brand header ── */
.sb-brand {{
  display:flex; align-items:center; gap:10px;
  padding: 0.1rem 0 1.2rem;
  border-bottom: 1px solid rgba(0,230,180,0.08);
  margin-bottom: 1.1rem;
}}
.sb-brand-icon {{
  font-size: 22px; line-height:1;
}}
.sb-brand-title {{
  font-family:'IBM Plex Mono',monospace;
  font-size:13px; font-weight:600;
  color:#cce8e0; letter-spacing:0.04em;
}}
.sb-brand-sub {{
  font-family:'IBM Plex Mono',monospace;
  font-size:9px; color:#2e4050;
  letter-spacing:0.1em; text-transform:uppercase;
  margin-top:1px;
}}

/* ── status badge ── */
.sb-status {{
  display:flex; align-items:center; gap:7px;
  background: rgba(0,0,0,0.25);
  border: 1px solid rgba(0,230,180,0.1);
  border-radius:4px; padding:6px 10px;
  margin-bottom:1.1rem;
}}
.sb-status-dot {{
  width:7px; height:7px; border-radius:50%;
  background:{status_color};
  flex-shrink:0;
  animation: sb-blink 2.2s ease-in-out infinite;
}}
.sb-status-label {{
  font-family:'IBM Plex Mono',monospace;
  font-size:10px; letter-spacing:0.1em;
  color:{status_color}; text-transform:uppercase;
}}
.sb-status-right {{
  margin-left:auto;
  font-family:'IBM Plex Mono',monospace;
  font-size:9px; color:#2e4050;
}}

/* ── stat row ── */
.sb-stats {{
  display:grid; grid-template-columns:1fr 1fr;
  gap:7px; margin-bottom:1.1rem;
}}
.sb-stat {{
  background:#090d13;
  border:1px solid rgba(0,230,180,0.09);
  border-top:2px solid rgba(0,230,180,0.3);
  border-radius:5px; padding:8px 10px;
  transition: border-top-color 0.2s;
}}
.sb-stat:hover {{ border-top-color:#00e6b4; }}
.sb-stat-val {{
  font-family:'IBM Plex Mono',monospace;
  font-size:16px; font-weight:600; color:#00e6b4;
}}
.sb-stat-lbl {{
  font-family:'IBM Plex Mono',monospace;
  font-size:9px; letter-spacing:0.1em;
  text-transform:uppercase; color:#2e4050;
  margin-top:2px;
}}

/* ── section label ── */
.sb-sec {{
  font-family:'IBM Plex Mono',monospace;
  font-size:9px; letter-spacing:0.15em;
  text-transform:uppercase; color:#2e4050;
  margin: 0 0 7px; display:flex;
  align-items:center; gap:6px;
}}
.sb-sec::after {{
  content:''; flex:1;
  height:1px; background:rgba(0,230,180,0.06);
}}

/* ── active model card ── */
.sb-active-model {{
  background:rgba(0,230,180,0.05);
  border:1px solid rgba(0,230,180,0.2);
  border-left:3px solid #00e6b4;
  border-radius:4px; padding:8px 12px;
  margin-bottom:1.1rem;
}}
.sb-active-model-name {{
  font-family:'IBM Plex Mono',monospace;
  font-size:12px; font-weight:600; color:#00e6b4;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}}
.sb-active-model-sub {{
  font-size:10px; color:#2e4050;
  font-family:'IBM Plex Mono',monospace;
  margin-top:2px;
}}

/* ── model list ── */
.sb-model-row {{
  display:flex; align-items:center;
  gap:8px; padding:6px 8px;
  border-radius:4px; margin-bottom:4px;
  background:#090d13;
  border:1px solid rgba(0,230,180,0.07);
  transition: border-color 0.15s, background 0.15s;
  cursor:default;
}}
.sb-model-row:hover {{
  border-color:rgba(0,230,180,0.25);
  background:rgba(0,230,180,0.04);
}}
.sb-model-row.active {{
  border-color:rgba(0,230,180,0.35);
  background:rgba(0,230,180,0.07);
}}
.sb-model-dot {{
  width:5px; height:5px; border-radius:50%;
  background:rgba(0,230,180,0.3); flex-shrink:0;
}}
.sb-model-row.active .sb-model-dot {{
  background:#00e6b4;
}}
.sb-model-name {{
  font-family:'IBM Plex Mono',monospace;
  font-size:11px; color:#8fa3b1; flex:1;
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
}}
.sb-model-row.active .sb-model-name {{ color:#cce8e0; }}
.sb-model-size {{
  font-family:'IBM Plex Mono',monospace;
  font-size:9px; color:#2e4050;
}}
.sb-model-badge {{
  font-size:9px; background:rgba(0,230,180,0.12);
  color:#00e6b4; border:1px solid rgba(0,230,180,0.25);
  border-radius:2px; padding:1px 5px;
  font-family:'IBM Plex Mono',monospace;
  letter-spacing:0.05em;
}}

/* ── lang rows ── */
.sb-lang-row {{
  display:flex; align-items:center;
  gap:9px; padding:7px 8px;
  border-radius:4px; margin-bottom:4px;
  border:1px solid rgba(0,230,180,0.06);
  background:#090d13;
  transition:border-color 0.15s, background 0.15s;
  cursor:default;
}}
.sb-lang-row:hover {{
  border-color:rgba(0,230,180,0.2);
  background:rgba(0,230,180,0.03);
}}
.sb-lang-icon {{ font-size:15px; width:18px; text-align:center; flex-shrink:0; }}
.sb-lang-name {{
  font-family:'DM Sans',sans-serif;
  font-size:12px; font-weight:600; color:#cce8e0;
  min-width:48px;
}}
.sb-lang-fw {{
  font-family:'IBM Plex Mono',monospace;
  font-size:9px; color:#2e4050;
  white-space:nowrap; overflow:hidden;
  text-overflow:ellipsis; flex:1;
}}

/* ── info box ── */
.sb-info {{
  background:#090d13;
  border:1px solid rgba(0,230,180,0.06);
  border-radius:4px; padding:10px 12px;
  margin-top:1rem;
}}
.sb-info-row {{
  display:flex; justify-content:space-between;
  align-items:center; padding:3px 0;
  border-bottom:1px solid rgba(0,230,180,0.04);
}}
.sb-info-row:last-child {{ border-bottom:none; }}
.sb-info-key {{
  font-family:'IBM Plex Mono',monospace;
  font-size:9px; letter-spacing:0.08em;
  text-transform:uppercase; color:#2e4050;
}}
.sb-info-val {{
  font-family:'IBM Plex Mono',monospace;
  font-size:10px; color:#5ecfb1;
}}
</style>

<!-- brand -->
<div class="sb-brand">
  <span class="sb-brand-icon">🐳</span>
  <div>
    <div class="sb-brand-title">Dockerfile Gen</div>
    <div class="sb-brand-sub">v1.0 · powered by ollama</div>
  </div>
</div>

<!-- status -->
<div class="sb-status">
  <span class="sb-status-dot"></span>
  <span class="sb-status-label">Ollama {status_text}</span>
  <span class="sb-status-right">local runtime</span>
</div>

<!-- stats -->
<div class="sb-stats">
  <div class="sb-stat">
    <div class="sb-stat-val">{model_count}</div>
    <div class="sb-stat-lbl">Models</div>
  </div>
  <div class="sb-stat">
    <div class="sb-stat-val">{lang_count}</div>
    <div class="sb-stat-lbl">Languages</div>
  </div>
</div>

<!-- active model -->
<div class="sb-sec">active model</div>
<div class="sb-active-model">
  <div class="sb-active-model-name" title="{active_model}">{active_model}</div>
  <div class="sb-active-model-sub">currently selected</div>
</div>
""", unsafe_allow_html=True)

    # ── model selector ──
    model = st.selectbox("Switch Model", installed_names, index=0, label_visibility="collapsed")

    # ── installed models list ──
    st.markdown("""<div class="sb-sec" style="margin-top:0.9rem;">installed models</div>""", unsafe_allow_html=True)
    model_rows_html = ""
    for i, m in enumerate(installed):
        is_active = (i == 0)
        active_cls = " active" if is_active else ""
        badge = '<span class="sb-model-badge">active</span>' if is_active else ""
        size = m.get("size", "")
        model_rows_html += f"""
<div class="sb-model-row{active_cls}">
  <span class="sb-model-dot"></span>
  <span class="sb-model-name" title="{m['name']}">{m['name']}</span>
  <span class="sb-model-size">{size}</span>
  {badge}
</div>"""
    if not installed:
        model_rows_html = '<div class="sb-model-row"><span class="sb-model-name" style="color:#2e4050;">no models found</span></div>'
    st.markdown(model_rows_html, unsafe_allow_html=True)

    # ── pull new model ──
    st.markdown("""<div class="sb-sec" style="margin-top:1rem;">pull new model</div>""", unsafe_allow_html=True)
    new_model = st.text_input("Model name", placeholder="e.g. mistral, llama3, gemma", label_visibility="collapsed")
    if st.button("⬇ Pull Model", use_container_width=True):
        if new_model.strip():
            with st.spinner(f"Pulling {new_model}..."):
                try:
                    ollama_lib.pull(new_model.strip())
                    st.success(f"✅ {new_model} ready!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ {e}")
        else:
            st.warning("Enter a model name.")

    # ── supported languages ──
    st.markdown("""<div class="sb-sec" style="margin-top:1rem;">supported languages</div>""", unsafe_allow_html=True)
    lang_rows_html = ""
    for icon, lang, frameworks in langs:
        lang_rows_html += f"""
<div class="sb-lang-row">
  <span class="sb-lang-icon">{icon}</span>
  <span class="sb-lang-name">{lang}</span>
  <span class="sb-lang-fw">{frameworks}</span>
</div>"""
    st.markdown(lang_rows_html, unsafe_allow_html=True)

    # ── system info ──
    st.markdown("""
<div class="sb-info" style="margin-top:1rem;">
  <div class="sb-info-row">
    <span class="sb-info-key">Mode</span>
    <span class="sb-info-val">100% local</span>
  </div>
  <div class="sb-info-row">
    <span class="sb-info-key">Privacy</span>
    <span class="sb-info-val">no telemetry</span>
  </div>
  <div class="sb-info-row">
    <span class="sb-info-key">Backend</span>
    <span class="sb-info-val">Ollama API</span>
  </div>
  <div class="sb-info-row">
    <span class="sb-info-key">Output</span>
    <span class="sb-info-val">Dockerfile</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Main tabs ─────────────────────────────────────────────
main_tab1, main_tab2 = st.tabs(["🚀 Generate", "⚡ Benchmark"])

# ════════════════════════════════════════════════════════
# TAB 1 — Generate
# ════════════════════════════════════════════════════════
with main_tab1:
    input_tab1, input_tab2 = st.tabs(["📁 Local Path", "📤 Upload Files"])
    project_path = None

    with input_tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        path_input = st.text_input(
            "path",
            placeholder=r"C:\Users\you\my-project",
            label_visibility="collapsed"
        )
        if path_input:
            if Path(path_input).exists():
                st.success(f"✅ Folder found: `{path_input}`")
                project_path = path_input
            else:
                st.error("❌ Folder not found. Check the path.")

    with input_tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("Upload requirements.txt · package.json · go.mod · pom.xml etc.")
        uploaded_files = st.file_uploader(
            "files",
            accept_multiple_files=True,
            key="generate_uploader",
            label_visibility="collapsed"
        )
        if uploaded_files:
            tmp_dir = tempfile.mkdtemp()
            for uf in uploaded_files:
                fp = os.path.join(tmp_dir, uf.name)
                with open(fp, "wb") as f:
                    f.write(uf.getbuffer())
            project_path = tmp_dir
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_btn = st.button("🚀 Generate Dockerfile", use_container_width=True)

    if generate_btn:
        if not project_path:
            st.warning("⚠️ Please provide a project path or upload files first.")
        elif not model or not model.strip():
            st.error("❌ No model selected. Pick one from the sidebar.")
        else:
            with st.spinner("🔍 Analyzing project..."):
                info  = detect_project(project_path)
                files = read_project_files(project_path)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 🔍 Project Analysis")
            c1, c2, c3 = st.columns(3)
            c1.metric("Language",  info["language"].capitalize())
            c2.metric("Framework", info["framework"].capitalize())
            c3.metric("Version",   info["version"])

            if info["language"] == "unknown":
                st.error("❌ Could not detect language. Upload a dependency file.")
                st.stop()

            with st.spinner("📝 Building prompt..."):
                prompt = build_prompt(info, files)

            with st.spinner(f"🤖 Asking {model}... (10–30 seconds)"):
                try:
                    response = ollama_lib.chat(
                        model=model.strip(),
                        messages=[{"role": "user", "content": prompt}]
                    )
                    raw = response["message"]["content"]
                except Exception as e:
                    st.error(f"❌ Ollama error: {e}")
                    st.info("Make sure Ollama is running.")
                    st.stop()

            with st.spinner("⚙️ Extracting Dockerfile..."):
                dockerfile = extract_dockerfile(raw)

            if not dockerfile:
                st.error("❌ Could not extract a valid Dockerfile.")
                with st.expander("See raw LLM response"):
                    st.code(raw)
                st.stop()

            with st.spinner("🛡️ Validating..."):
                result = validate_dockerfile(dockerfile)

            st.divider()
            st.markdown("### 🛡️ Validation Report")
            score = result["score"]
            score_label = "🟢 Excellent" if score >= 80 else "🟡 Needs improvement" if score >= 50 else "🔴 Poor"

            c1, c2 = st.columns([1, 3])
            with c1:
                st.metric("Quality Score", f"{score}/100")
            with c2:
                st.progress(score / 100)
                st.caption(score_label)

            if result["errors"]:
                for e in result["errors"]:
                    st.error(f"❌ **{e['id']}** — {e['message']}")
            if result["warnings"]:
                for w in result["warnings"]:
                    st.warning(f"⚠️ **{w['id']}** — {w['message']}")
            if result["infos"]:
                for i in result["infos"]:
                    st.info(f"💡 **{i['id']}** — {i['message']}")
            if result["passed"] and not result["warnings"]:
                st.success("✅ Perfect! No issues found.")

            st.divider()
            st.markdown("### ✅ Generated Dockerfile")
            st.code(dockerfile, language="dockerfile")

            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    label="⬇️ Download Dockerfile",
                    data=dockerfile,
                    file_name="Dockerfile",
                    mime="text/plain",
                    use_container_width=True
                )
            with c2:
                if st.button("💾 Save to folder", use_container_width=True):
                    save_dockerfile(dockerfile, project_path)
                    st.success("✅ Saved!")

            with st.expander("🔎 See prompt sent to LLM"):
                st.code(prompt)

# ════════════════════════════════════════════════════════
# TAB 2 — Benchmark
# ════════════════════════════════════════════════════════
with main_tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="
        background: rgba(0,230,180,0.04);
        border: 1px solid rgba(0,230,180,0.15);
        border-left: 3px solid rgba(0,230,180,0.5);
        border-radius: 4px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.5rem;
    ">
        <p style="margin:0; font-size:13px; color:#5ecfb1; font-family:'IBM Plex Mono',monospace; letter-spacing:0.02em;">
            ⚡ <strong style="color:#00e6b4;">benchmark</strong> — test multiple models on the same project
            and compare quality scores and speed side by side.
        </p>
    </div>
    """, unsafe_allow_html=True)

    bench_tab1, bench_tab2 = st.tabs(["📁 Local Path", "📤 Upload Files"])
    bench_path = None

    with bench_tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        bench_input = st.text_input(
            "bench_path_input",
            placeholder=r"C:\Users\you\my-project",
            key="bench_path",
            label_visibility="collapsed"
        )
        if bench_input and Path(bench_input).exists():
            bench_path = bench_input
            st.success("✅ Folder found")

    with bench_tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        bench_files = st.file_uploader(
            "bench_files",
            accept_multiple_files=True,
            key="bench_uploader",
            label_visibility="collapsed"
        )
        if bench_files:
            tmp_dir = tempfile.mkdtemp()
            for uf in bench_files:
                fp = os.path.join(tmp_dir, uf.name)
                with open(fp, "wb") as f:
                    f.write(uf.getbuffer())
            bench_path = tmp_dir
            st.success(f"✅ {len(bench_files)} file(s) uploaded")

    if installed_names:
        selected_models = st.multiselect(
            "Select models to benchmark",
            options=installed_names,
            default=installed_names[:1]
        )
    else:
        st.error("No models installed.")
        selected_models = []

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        bench_btn = st.button("⚡ Run Benchmark", use_container_width=True)

    if bench_btn:
        if not bench_path:
            st.warning("⚠️ Please provide a project path or upload files.")
        elif not selected_models:
            st.warning("⚠️ Select at least one model.")
        else:
            with st.spinner("Analyzing project..."):
                info   = detect_project(bench_path)
                files  = read_project_files(bench_path)
                prompt = build_prompt(info, files)

            st.info(f"Testing **{len(selected_models)}** model(s) on a **{info['language']}** project...")

            with st.spinner("Running benchmark... this may take a while"):
                results = benchmark_models(selected_models, prompt)

            st.divider()
            st.markdown("### 📊 Benchmark Results")
            winner = results[0]
            st.markdown(f"""
            <div style="
                background: rgba(0,230,180,0.05);
                border: 1px solid rgba(0,230,180,0.2);
                border-left: 3px solid #00e6b4;
                border-radius: 4px;
                padding: 1rem 1.25rem;
                margin-bottom: 1rem;
            ">
                <p style="margin:0; font-size:14px; color:#00e6b4; font-family:'IBM Plex Mono',monospace; letter-spacing:0.03em;">
                    🏆 <strong>best:</strong>
                    {winner['model']} — score: {winner['score']}/100 in {winner['time']}s
                </p>
            </div>
            """, unsafe_allow_html=True)

            for i, r in enumerate(results):
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
                with st.expander(
                    f"{medal} {r['model']} — {r['score']}/100 | ⏱ {r['time']}s",
                    expanded=(i == 0)
                ):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("Score",    f"{r['score']}/100")
                    c2.metric("Time",     f"{r['time']}s")
                    c3.metric("Errors",   r["errors"])
                    c4.metric("Warnings", r["warnings"])
                    st.progress(r["score"] / 100)
                    if r["success"] and r["dockerfile"]:
                        st.code(r["dockerfile"], language="dockerfile")
                        st.download_button(
                            label=f"⬇️ Download ({r['model']})",
                            data=r["dockerfile"],
                            file_name=f"Dockerfile.{r['model'].replace(':','_')}",
                            mime="text/plain",
                            key=f"dl_{r['model']}"
                        )
                    else:
                        st.error(f"Failed: {r.get('error', 'Could not extract Dockerfile')}")

# ── Footer ────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center; padding:0.75rem 0 0.25rem;">
    <p style="font-size:11px; color:#1a2530; font-family:'IBM Plex Mono',monospace; letter-spacing:0.08em; text-transform:uppercase;">
        built with streamlit &nbsp;·&nbsp; runs 100% locally &nbsp;·&nbsp; no data leaves your machine
    </p>
</div>
""", unsafe_allow_html=True)