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
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Sora:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; max-width: 780px; }

.stApp {
    background: #0a0e1a;
    background-image:
        radial-gradient(ellipse at 20% 10%, rgba(30,80,180,0.15) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 80%, rgba(0,180,140,0.1) 0%, transparent 50%);
}

[data-testid="stSidebar"] {
    background: #0d1120 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}
[data-testid="stSidebar"] * { color: #c8d0e0 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #ffffff !important; }

div[data-testid="stExpander"] {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    overflow: hidden;
}

[data-testid="stMetric"] {
    background: #111827;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 1rem !important;
}
[data-testid="stMetricLabel"] { color: #6b7280 !important; font-size: 12px !important; }
[data-testid="stMetricValue"] { color: #f9fafb !important; font-size: 22px !important; font-weight: 600 !important; }

.stButton > button {
    background: linear-gradient(135deg, #1d4ed8, #0891b2) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.2s ease !important;
    letter-spacing: 0.02em !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(29,78,216,0.4) !important;
}

[data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #065f46, #0f766e) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
[data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(6,95,70,0.4) !important;
}

.stTextInput > div > div > input,
.stSelectbox > div > div {
    background: #111827 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    color: #f9fafb !important;
    font-family: 'Sora', sans-serif !important;
}

[data-testid="stFileUploader"] {
    background: #111827 !important;
    border: 2px dashed rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}

.stCodeBlock, code {
    font-family: 'JetBrains Mono', monospace !important;
    background: #0d1120 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 10px !important;
    font-size: 13px !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #111827 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 4px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 7px !important;
    color: #6b7280 !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    padding: 6px 16px !important;
    transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
    background: #1d4ed8 !important;
    color: white !important;
}

.stSuccess { background: rgba(6,95,70,0.2) !important; border: 1px solid rgba(16,185,129,0.3) !important; border-radius: 8px !important; }
.stError   { background: rgba(127,29,29,0.2) !important; border: 1px solid rgba(239,68,68,0.3) !important; border-radius: 8px !important; }
.stWarning { background: rgba(120,53,15,0.2) !important; border: 1px solid rgba(245,158,11,0.3) !important; border-radius: 8px !important; }
.stInfo    { background: rgba(30,58,138,0.2) !important; border: 1px solid rgba(59,130,246,0.3) !important; border-radius: 8px !important; }

.stProgress > div > div > div {
    background: linear-gradient(90deg, #1d4ed8, #0891b2) !important;
    border-radius: 99px !important;
}
.stProgress > div > div {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 99px !important;
}

hr { border-color: rgba(255,255,255,0.06) !important; margin: 1.5rem 0 !important; }
p, li, label, span, .stMarkdown { color: #c8d0e0 !important; }
h1, h2, h3 { color: #f9fafb !important; }
.stCaption { color: #4b5563 !important; font-size: 12px !important; }
[data-baseweb="select"] > div {
    background: #111827 !important;
    border-color: rgba(255,255,255,0.1) !important;
    color: #f9fafb !important;
}
</style>
""", unsafe_allow_html=True)

# ── Hero Header ───────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 2rem 0 1rem;">
    <div style="font-size:52px; margin-bottom:0.5rem;">🐳</div>
    <h1 style="font-family:'Sora',sans-serif; font-size:2.2rem; font-weight:700;
               background:linear-gradient(135deg,#60a5fa,#34d399);
               -webkit-background-clip:text; -webkit-text-fill-color:transparent;
               margin:0; letter-spacing:-0.02em;">
        Dockerfile Generator
    </h1>
    <p style="color:#4b5563; font-size:14px; margin-top:0.5rem; font-family:'Sora',sans-serif;">
        Powered by local LLM (Ollama) &nbsp;·&nbsp; 100% free &nbsp;·&nbsp; 100% private
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <p style="font-size:11px; letter-spacing:0.1em; color:#4b5563;
              text-transform:uppercase; margin:0 0 1rem;">Configuration</p>
    """, unsafe_allow_html=True)

    installed = get_installed_models()
    installed_names = [m["name"] for m in installed]
    if not installed_names:
        installed_names = ["codellama"]

    model = st.selectbox("🤖 Ollama Model", installed_names, index=0)

    st.markdown("**📦 Installed Models**")
    if installed:
        for m in installed:
            st.caption(f"• {m['name']} — {m['size']}")
    else:
        st.caption("• codellama — detected")
        st.warning("Make sure Ollama is running.")

    st.divider()
    st.markdown("**⬇️ Pull a new model**")
    new_model = st.text_input("Model name", placeholder="e.g. mistral")
    if st.button("⬇️ Pull Model", use_container_width=True):
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

    st.divider()
    st.markdown("**🌐 Supported Languages**")
    langs = [
        ("🐍", "Python", "Flask · FastAPI · Django"),
        ("🟩", "Node.js", "Express · Next.js"),
        ("🐹", "Go", "Go Modules"),
        ("☕", "Java", "Maven · Gradle"),
        ("🦀", "Rust", "Cargo"),
    ]
    for icon, lang, frameworks in langs:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
            <span style="font-size:16px">{icon}</span>
            <div>
                <div style="font-size:13px;font-weight:600;color:#e5e7eb;">{lang}</div>
                <div style="font-size:11px;color:#4b5563;">{frameworks}</div>
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
    <div style="background:linear-gradient(135deg,rgba(29,78,216,0.15),rgba(8,145,178,0.15));
                border:1px solid rgba(29,78,216,0.3); border-radius:12px;
                padding:1rem 1.25rem; margin-bottom:1.5rem;">
        <p style="margin:0; font-size:13px; color:#93c5fd;">
            ⚡ <strong style="color:#bfdbfe;">Benchmark</strong> — test multiple models on the same project
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
            <div style="background:linear-gradient(135deg,rgba(6,95,70,0.2),rgba(15,118,110,0.2));
                        border:1px solid rgba(16,185,129,0.3); border-radius:10px;
                        padding:1rem 1.25rem; margin-bottom:1rem;">
                <p style="margin:0; font-size:15px; color:#6ee7b7;">
                    🏆 <strong style="color:#a7f3d0;">Best:</strong>
                    {winner['model']} — Score: {winner['score']}/100 in {winner['time']}s
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
<div style="text-align:center; padding:0.5rem 0;">
    <p style="font-size:12px; color:#374151; font-family:'Sora',sans-serif;">
        Built with Streamlit &nbsp;·&nbsp; Runs 100% locally &nbsp;·&nbsp; No data leaves your machine
    </p>
</div>
""", unsafe_allow_html=True)