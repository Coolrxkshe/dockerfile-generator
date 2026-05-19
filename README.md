# 🐳 Dockerfile Generator

> **AI-powered Dockerfile generation using local LLMs — 100% free, 100% private, zero cloud dependency.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green.svg)](https://ollama.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌍 Real World Use — Why This Project Matters

Every developer who builds a web app eventually needs to **containerize** it using Docker.
Writing a Dockerfile manually requires knowing:

- Which base image to use
- How to install dependencies efficiently
- How to structure layers for caching
- Security best practices (non-root users, minimal images)
- Production vs development differences

**Most developers get this wrong.** They copy-paste from Stack Overflow, end up with 2GB images, security vulnerabilities, and broken builds.

This tool solves that problem — you just point it at your project and it generates a production-ready Dockerfile in seconds using AI that runs entirely on your machine.

### Who uses this?

| User | Problem Solved |
|------|---------------|
| **Junior Developers** | Don't know Docker — tool generates it for them |
| **Startup Teams** | No DevOps engineer — tool replaces one for basic containerization |
| **Open Source Contributors** | Want to add Docker support to any GitHub repo |
| **DevOps Engineers** | Use the Optimizer to improve existing Dockerfiles |
| **Students** | Learn Docker best practices by seeing AI explanations |
| **Freelancers** | Deliver dockerized apps to clients faster |

---

## ✨ Features

### 🚀 Generate Tab
- Auto-detects your project language and framework
- Supports **Python** (Flask, FastAPI, Django), **Node.js** (Express, Next.js), **Go**, **Java**, **Rust**
- Generates production-ready Dockerfile in seconds
- Quality validation with score out of 100
- Download or save directly to your project folder

### 🔧 Optimize Tab
- Paste any existing Dockerfile — even a bad one
- AI rewrites it: smaller, faster, more secure
- Shows **before vs after** side by side
- Explains every change made and why
- Line-by-line diff view
- Estimated image size savings (e.g. 85% smaller)

### 🐙 Compose Tab
- Generates full `docker-compose.yml`
- Includes App + Database + Redis + Nginx — all wired together
- Choose which services to include with checkboxes
- Download or save the compose file
- Explains what each service does in plain English

### 🐙 GitHub URL Input
- Paste any public GitHub repo URL
- Tool clones it, analyzes it, generates the Dockerfile
- Works on any public project in the world
- Example repos: Flask, FastAPI, Express

### 🧪 Dockerfile Tester
- Actually **builds** the generated Dockerfile using Docker Engine
- Shows real live build logs
- Reports image size if build succeeds
- If build fails — AI suggests the exact fix
- No other free tool does this

### 🤖 AI Chat with Dockerfile
- After generating, chat with your Dockerfile
- Ask: "How do I add a health check?"
- Ask: "How do I make this more secure?"
- Ask: "How do I run this on port 8080?"
- Quick question buttons for common queries
- Full conversation history with bubble UI

### ⚡ Benchmark Tab
- Test multiple AI models on the same project
- Compare quality scores and speed side by side
- 🥇🥈🥉 medals for ranking
- Download Dockerfile from any model

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3.11 |
| AI / LLM | Ollama + CodeLlama / LLaMA3 |
| Web UI | Streamlit |
| CLI | Typer + Rich |
| Git cloning | GitPython |
| Docker testing | Docker SDK (subprocess) |
| YAML generation | PyYAML |
| Packaging | pip + venv |
| Version Control | Git + GitHub |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- [Ollama](https://ollama.com) installed
- Docker Desktop (for Tester feature)

### 1. Clone the repo
```bash
git clone https://github.com/Coolrxkshe/dockerfile-generator.git
cd dockerfile-generator
```

### 2. Install Ollama and pull a model
```bash
# Download Ollama from ollama.com, then:
ollama pull codellama
```

### 3. Setup Python environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Run the web app
```bash
streamlit run app.py
```

### 5. Or use the CLI
```bash
python main.py /path/to/your/project
```

### Windows one-click setup
Double click `install.bat` then `run.bat`

---

## 📦 Project Structure

```
dockerfile-generator/
│
├── app.py                  # Web UI (Streamlit) — main entry point
├── main.py                 # CLI entry point
├── config.py               # Settings (model name, Ollama URL)
├── requirements.txt        # Python dependencies
├── setup.py                # pip installable package
├── install.bat             # Windows one-click installer
├── run.bat                 # Windows one-click launcher
├── Makefile                # Mac/Linux commands
│
├── analyzer/               # Detects language & framework
│   ├── detector.py         # Reads project files, identifies stack
│   └── reader.py           # Reads package.json, requirements.txt etc.
│
├── llm/                    # Ollama integration
│   ├── client.py           # Sends prompts, gets responses
│   └── parser.py           # Extracts Dockerfile from LLM output
│
├── prompt/                 # Prompt engineering
│   ├── builder.py          # Builds smart prompts from project info
│   └── templates/          # Per-language prompt templates
│       ├── python.txt
│       ├── node.txt
│       ├── go.txt
│       ├── java.txt
│       └── generic.txt
│
├── validator/              # Dockerfile quality checker
│   ├── checker.py          # Runs 10 validation rules
│   └── rules.py            # Rule definitions (security, best practices)
│
├── composer/               # Docker Compose generator
│   ├── generator.py        # Builds compose YAML
│   └── templates.py        # Service templates per framework
│
├── optimizer/              # Dockerfile optimizer
│   └── docker_optimizer.py # Before/after optimization + diff
│
├── chat/                   # AI chat feature
│   └── docker_chat.py      # Contextual chat with Dockerfile
│
├── github_reader/          # GitHub repo cloner
│   └── repo_reader.py      # Clones public repos for analysis
│
├── models/                 # Model management
│   ├── manager.py          # Lists installed Ollama models
│   └── benchmark.py        # Benchmarks multiple models
│
├── tester/                 # Dockerfile build tester
│   └── docker_tester.py    # Runs docker build, captures logs
│
└── output/                 # File writer
    └── writer.py           # Saves Dockerfile to disk
```

---

## 🌐 Deployment Options

### Option 1 — Streamlit Cloud (FREE, recommended)
1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. Set main file as `app.py`
5. Your app is live at `yourname.streamlit.app`

> ⚠️ Note: Streamlit Cloud doesn't have Ollama installed. For cloud deployment you'll need to switch the LLM backend to an API like Groq (free) or OpenAI.

### Option 2 — Run locally (current setup, fully private)
```bash
streamlit run app.py
# Opens at http://localhost:8501
```
Best for: privacy, no internet, free forever, fast.

### Option 3 — Docker (run anywhere)
```bash
docker build -t dockerfile-generator .
docker run -p 8501:8501 dockerfile-generator
```

### Option 4 — Railway / Render (paid cloud)
- Push to GitHub
- Connect to [Railway](https://railway.app) or [Render](https://render.com)
- Set start command: `streamlit run app.py`
- Add environment variable: `OLLAMA_URL=your-ollama-server`

### Option 5 — VPS (DigitalOcean, AWS, etc.)
```bash
# On your server:
git clone your-repo
pip install -r requirements.txt
ollama serve &
ollama pull codellama
streamlit run app.py --server.port 80
```

---

## 🔮 What's Next (Roadmap)

- [ ] `.dockerignore` auto-generator
- [ ] Dockerfile Explainer (explain each line in plain English)
- [ ] ZIP upload support (upload whole project as .zip)
- [ ] VS Code Extension
- [ ] PyPI package (`pip install dockergen`)
- [ ] Cloud deployment with Groq API backend
- [ ] Multi-stage build optimizer
- [ ] Docker image size estimator

---

## 🤝 Contributing

Pull requests are welcome! Please open an issue first to discuss changes.

1. Fork the repo
2. Create a branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m "Add my feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👨‍💻 Built By

Built with ❤️ using Python, Streamlit, and Ollama.
Runs 100% locally — no data ever leaves your machine.

---

<div align="center">
  <strong>⭐ Star this repo if it helped you!</strong>
</div>