import re

def extract_dockerfile(text: str) -> str:
    match = re.search(r"```(?:dockerfile)?\s*(FROM[\s\S]+?)```", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    if "FROM" in text:
        return text.strip()
    return ""