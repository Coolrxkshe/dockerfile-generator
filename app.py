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

# ── Header ────────────────────────────────────────────────
st.title("🐳 Dockerfile Generator")
st.caption("Powered by local LLM (Ollama) — 100% free, 100% private")
st.divider()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")

    # Get installed models dynamically
    installed = get_installed_models()
    installed_names = [m["name"] for m in installed]

    # Always ensure fallback so dropdown is never empty
    if not installed_names:
        installed_names = ["codellama"]

    model = st.selectbox("Ollama Model", installed_names, index=0)

    # Show installed models with size
    st.markdown("**Installed Models**")
    if installed:
        for m in installed:
            st.caption(f"📦 {m['name']} — {m['size']}")
    else:
        st.caption("📦 codellama — detected")
        st.warning("Could not read model list. Make sure Ollama is running.")

    st.divider()

    # Pull new model
    st.markdown("**Pull a new model**")
    new_model = st.text_input("Model name", placeholder="e.g. mistral")
    if st.button("⬇️ Pull Model"):
        if new_model.strip():
            with st.spinner(f"Pulling {new_model}... (may take a few minutes)"):
                try:
                    ollama_lib.pull(new_model.strip())
                    st.success(f"✅ {new_model} pulled successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed: {e}")
        else:
            st.warning("Please enter a model name.")

    st.divider()
    st.markdown("**Supported Languages**")
    st.markdown("🐍 Python (Flask, FastAPI, Django)")
    st.markdown("🟩 Node.js (Express, Next.js)")
    st.markdown("🐹 Go")
    st.markdown("☕ Java (Maven, Gradle)")
    st.markdown("🦀 Rust")

# ── Main tabs ─────────────────────────────────────────────
main_tab1, main_tab2 = st.tabs(["🚀 Generate", "⚡ Benchmark Models"])

# ════════════════════════════════════════════════════════
# TAB 1 — Generate
# ════════════════════════════════════════════════════════
with main_tab1:

    input_tab1, input_tab2 = st.tabs(["📁 Use Local Path", "📤 Upload Files"])
    project_path = None

    with input_tab1:
        st.subheader("Point to a project folder")
        path_input = st.text_input(
            "Project folder path",
            placeholder=r"C:\Users\you\my-project"
        )
        if path_input:
            if Path(path_input).exists():
                st.success(f"✅ Folder found: `{path_input}`")
                project_path = path_input
            else:
                st.error("❌ Folder not found. Check the path.")

    with input_tab2:
        st.subheader("Upload your project files")
        st.caption("Upload requirements.txt, package.json, go.mod etc.")
        uploaded_files = st.file_uploader(
            "Choose files",
            accept_multiple_files=True,
            key="generate_uploader"
        )
        if uploaded_files:
            tmp_dir = tempfile.mkdtemp()
            for uf in uploaded_files:
                fp = os.path.join(tmp_dir, uf.name)
                with open(fp, "wb") as f:
                    f.write(uf.getbuffer())
            project_path = tmp_dir
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")

    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_btn = st.button("🚀 Generate Dockerfile", use_container_width=True)

    if generate_btn:
        if not project_path:
            st.warning("⚠️ Please provide a project path or upload files first.")
        elif not model or not model.strip():
            st.error("❌ No model selected. Please select a model from the sidebar.")
        else:
            # Step 1: Analyze
            with st.spinner("Analyzing project..."):
                info  = detect_project(project_path)
                files = read_project_files(project_path)

            st.subheader("🔍 Project Analysis")
            c1, c2, c3 = st.columns(3)
            c1.metric("Language",  info["language"].capitalize())
            c2.metric("Framework", info["framework"].capitalize())
            c3.metric("Version",   info["version"])

            if info["language"] == "unknown":
                st.error("❌ Could not detect language. Make sure you uploaded a dependency file.")
                st.stop()

            # Step 2: Build prompt
            with st.spinner("Building prompt..."):
                prompt = build_prompt(info, files)

            # Step 3: Ask LLM
            with st.spinner(f"Asking {model}... (10–30 seconds)"):
                try:
                    response = ollama_lib.chat(
                        model=model.strip(),
                        messages=[{"role": "user", "content": prompt}]
                    )
                    raw = response["message"]["content"]
                except Exception as e:
                    st.error(f"❌ Ollama error: {e}")
                    st.info("Make sure Ollama is running and the model is installed.")
                    st.stop()

            # Step 4: Extract
            with st.spinner("Extracting Dockerfile..."):
                dockerfile = extract_dockerfile(raw)

            if not dockerfile:
                st.error("❌ Could not extract a valid Dockerfile.")
                with st.expander("See raw LLM response"):
                    st.code(raw)
                st.stop()

            # Step 5: Validate
            with st.spinner("Validating..."):
                result = validate_dockerfile(dockerfile)

            st.divider()
            st.subheader("🛡️ Validation Report")

            score = result["score"]
            score_label = "Excellent" if score >= 80 else "Needs improvement" if score >= 50 else "Poor"

            c1, c2 = st.columns([1, 3])
            with c1:
                st.metric("Quality Score", f"{score}/100")
            with c2:
                st.progress(score / 100)
                st.caption(f"**{score_label}**")

            if result["errors"]:
                st.error(f"❌ {len(result['errors'])} Error(s)")
                for e in result["errors"]:
                    st.error(f"**{e['id']}** — {e['message']}")
            if result["warnings"]:
                st.warning(f"⚠️ {len(result['warnings'])} Warning(s)")
                for w in result["warnings"]:
                    st.warning(f"**{w['id']}** — {w['message']}")
            if result["infos"]:
                st.info(f"💡 {len(result['infos'])} Suggestion(s)")
                for i in result["infos"]:
                    st.info(f"**{i['id']}** — {i['message']}")
            if result["passed"] and not result["warnings"]:
                st.success("✅ Perfect! No issues found.")

            # Step 6: Show Dockerfile
            st.divider()
            st.subheader("✅ Generated Dockerfile")
            st.code(dockerfile, language="dockerfile")

            st.download_button(
                label="⬇️ Download Dockerfile",
                data=dockerfile,
                file_name="Dockerfile",
                mime="text/plain",
                use_container_width=True
            )

            if st.button("💾 Save to project folder", use_container_width=True):
                save_dockerfile(dockerfile, project_path)
                st.success("✅ Saved!")

            with st.expander("🔎 See prompt sent to LLM"):
                st.code(prompt)

# ════════════════════════════════════════════════════════
# TAB 2 — Benchmark
# ════════════════════════════════════════════════════════
with main_tab2:
    st.subheader("⚡ Benchmark Models Side by Side")
    st.caption("Test multiple models on the same project and compare quality scores and speed.")

    bench_tab1, bench_tab2 = st.tabs(["📁 Use Local Path", "📤 Upload Files"])
    bench_path = None

    with bench_tab1:
        bench_input = st.text_input(
            "Project folder path",
            placeholder=r"C:\Users\you\my-project",
            key="bench_path"
        )
        if bench_input and Path(bench_input).exists():
            bench_path = bench_input
            st.success("✅ Folder found")

    with bench_tab2:
        bench_files = st.file_uploader(
            "Choose files",
            accept_multiple_files=True,
            key="bench_uploader"
        )
        if bench_files:
            tmp_dir = tempfile.mkdtemp()
            for uf in bench_files:
                fp = os.path.join(tmp_dir, uf.name)
                with open(fp, "wb") as f:
                    f.write(uf.getbuffer())
            bench_path = tmp_dir
            st.success(f"✅ {len(bench_files)} file(s) uploaded")

    # Model selector for benchmark
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
            st.warning("⚠️ Please select at least one model.")
        else:
            with st.spinner("Analyzing project..."):
                info   = detect_project(bench_path)
                files  = read_project_files(bench_path)
                prompt = build_prompt(info, files)

            st.info(f"Testing {len(selected_models)} model(s) on a **{info['language']}** project...")

            with st.spinner("Running benchmark... this may take a while"):
                results = benchmark_models(selected_models, prompt)

            st.divider()
            st.subheader("📊 Benchmark Results")

            winner = results[0]
            st.success(f"🏆 Best model: **{winner['model']}** — Score: {winner['score']}/100")

            for i, r in enumerate(results):
                medal = ["🥇", "🥈", "🥉"][i] if i < 3 else f"#{i+1}"
                with st.expander(
                    f"{medal} {r['model']} — Score: {r['score']}/100 | Time: {r['time']}s",
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
                            file_name=f"Dockerfile.{r['model'].replace(':', '_')}",
                            mime="text/plain",
                            key=f"dl_{r['model']}"
                        )
                    else:
                        st.error(f"Failed: {r.get('error', 'Could not extract Dockerfile')}")

# ── Footer ────────────────────────────────────────────────
st.divider()
st.caption("Built with Streamlit · Runs 100% locally · No data leaves your machine")