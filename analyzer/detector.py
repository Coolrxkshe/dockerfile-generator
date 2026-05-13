from pathlib import Path

def detect_project(path: str) -> dict:
    p = Path(path)
    files = [f.name for f in p.iterdir() if f.is_file()]

    language = "unknown"
    framework = "unknown"
    version = "latest"

    # Python
    if "requirements.txt" in files or "pyproject.toml" in files:
        language = "python"
        version = "3.11"
        content = ""
        if (p / "requirements.txt").exists():
            content = (p / "requirements.txt").read_text(errors="ignore").lower()
        if "fastapi" in content:
            framework = "fastapi"
        elif "flask" in content:
            framework = "flask"
        elif "django" in content:
            framework = "django"
        else:
            framework = "generic python"

    # Node.js
    elif "package.json" in files:
        language = "node"
        version = "18"
        content = (p / "package.json").read_text(errors="ignore").lower()
        if "express" in content:
            framework = "express"
        elif "next" in content:
            framework = "nextjs"
        elif "react" in content:
            framework = "react"
        else:
            framework = "generic node"

    # Go
    elif "go.mod" in files:
        language = "go"
        version = "1.21"
        framework = "go module"

    # Java
    elif "pom.xml" in files:
        language = "java"
        version = "17"
        framework = "maven"
    elif "build.gradle" in files:
        language = "java"
        version = "17"
        framework = "gradle"

    # Rust
    elif "Cargo.toml" in files:
        language = "rust"
        version = "latest"
        framework = "cargo"

    return {
        "language": language,
        "framework": framework,
        "version": version,
        "files": files
    }