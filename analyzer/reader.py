from pathlib import Path

def read_project_files(path: str) -> dict:
    p = Path(path)
    result = {}

    targets = [
        "requirements.txt", "package.json", "go.mod",
        "pyproject.toml", "Pipfile", ".python-version",
        "pom.xml", "build.gradle", "Cargo.toml"
    ]

    for name in targets:
        f = p / name
        if f.exists():
            result[name] = f.read_text(errors="ignore")

    return result