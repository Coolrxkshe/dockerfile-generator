import ollama

def get_installed_models() -> list:
    try:
        result = ollama.list()
        models = []
        for m in result.get("models", []):
            name = ""
            size = 0

            # handle both object and dict formats
            if hasattr(m, "model"):
                name = m.model
            elif hasattr(m, "name"):
                name = m.name
            elif isinstance(m, dict):
                name = m.get("model") or m.get("name", "")

            if hasattr(m, "size"):
                size = m.size
            elif isinstance(m, dict):
                size = m.get("size", 0)

            if name and name.strip():
                size_gb = round(size / 1e9, 1)
                models.append({
                    "name": name.strip(),
                    "size": f"{size_gb} GB"
                })
        return models
    except Exception:
        return []

def is_model_available(model_name: str) -> bool:
    models = get_installed_models()
    return any(m["name"].startswith(model_name) for m in models)

def pull_model(model_name: str) -> bool:
    try:
        ollama.pull(model_name)
        return True
    except Exception:
        return False