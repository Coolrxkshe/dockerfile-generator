# 🐳 Dockerfile Generator

> Generate production-ready Dockerfiles using local LLMs — 100% free, 100% private.

No API keys. No internet required. Runs entirely on your machine using Ollama.

---

## ✨ Features

- 🔍 Auto-detects your project language and framework
- 🐍 Supports Python, Node.js, Go, Java, Rust
- 🛡️ Validates generated Dockerfiles with quality scoring
- ⚡ Benchmark multiple AI models side by side
- 🌐 Beautiful web UI built with Streamlit
- 💻 CLI support for terminal users

---

## 🚀 Quick Start

### 1. Install Ollama
Download from [ollama.com](https://ollama.com) and install it.

### 2. Pull a model
```bash
ollama pull codellama
```

### 3. Clone this repo
```bash
git clone https://github.com/yourusername/dockerfile-generator.git
cd dockerfile-generator
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Run the web app
```bash
streamlit run app.py
```

### 6. Or use the CLI
```bash
python main.py /path/to/your/project
```

---

## 📦 Supported Languages

| Language | Frameworks Detected |
|----------|-------------------|
| Python   | FastAPI, Flask, Django |
| Node.js  | Express, Next.js, React |
| Go       | Go Modules |
| Java     | Maven, Gradle |
| Rust     | Cargo |

---

## 🛡️ Validation Rules

The tool checks your Dockerfile for:

- ❌ Missing FROM instruction
- ❌ Missing CMD or ENTRYPOINT
- ⚠️ Missing WORKDIR
- ⚠️ Using latest tag
- ⚠️ apt-get without update
- ⚠️ Multiple RUN layers
- 💡 No USER instruction (security)
- 💡 No EXPOSE instruction

---

## 🗂️ Project Structure
dockerfile-generator/
├── app.py               # Web UI (Streamlit)
├── main.py              # CLI entry point
├── config.py            # Settings
├── analyzer/            # Project detection
├── llm/                 # Ollama client
├── prompt/              # Prompt templates
├── output/              # File writer
├── validator/           # Dockerfile linter
└── models/              # Model manager

---

## 🤝 Contributing

Pull requests welcome! Please open an issue first to discuss changes.

---

## 📄 License

MIT License — free to use, modify, and distribute.