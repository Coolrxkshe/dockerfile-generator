from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent / "templates"

def build_prompt(project_info: dict, file_contents: dict) -> str:
    lang = project_info.get("language", "unknown")
    framework = project_info.get("framework", "unknown")
    version = project_info.get("version", "latest")

    template_file = TEMPLATES_DIR / f"{lang}.txt"
    if not template_file.exists():
        template_file = TEMPLATES_DIR / "generic.txt"

    template = template_file.read_text()

    deps = (
        file_contents.get("requirements.txt") or
        file_contents.get("package.json") or
        file_contents.get("go.mod") or
        file_contents.get("pom.xml") or
        file_contents.get("build.gradle") or
        file_contents.get("Cargo.toml") or
        "No dependency file found."
    )

    return template.format(
        language=lang,
        framework=framework,
        version=version,
        dependencies=deps
    )