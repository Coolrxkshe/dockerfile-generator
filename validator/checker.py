from .rules import RULES

def validate_dockerfile(content: str) -> dict:
    lines = content.strip().splitlines()

    errors   = []
    warnings = []
    infos    = []

    for rule in RULES:
        try:
            if rule["check"](lines):
                item = {
                    "id":      rule["id"],
                    "message": rule["message"]
                }
                if rule["severity"] == "error":
                    errors.append(item)
                elif rule["severity"] == "warning":
                    warnings.append(item)
                else:
                    infos.append(item)
        except Exception:
            pass

    score = 100
    score -= len(errors)   * 30
    score -= len(warnings) * 10
    score -= len(infos)    * 5
    score = max(0, score)

    return {
        "errors":   errors,
        "warnings": warnings,
        "infos":    infos,
        "score":    score,
        "passed":   len(errors) == 0
    }