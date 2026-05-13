import time
import ollama
from llm.parser import extract_dockerfile
from validator.checker import validate_dockerfile

def benchmark_models(models: list, prompt: str) -> list:
    results = []

    for model_name in models:
        start = time.time()
        try:
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = response["message"]["content"]
            elapsed = round(time.time() - start, 1)

            dockerfile = extract_dockerfile(raw)
            if dockerfile:
                validation = validate_dockerfile(dockerfile)
                score = validation["score"]
                errors = len(validation["errors"])
                warnings = len(validation["warnings"])
            else:
                score = 0
                errors = 1
                warnings = 0
                dockerfile = ""

            results.append({
                "model":      model_name,
                "time":       elapsed,
                "score":      score,
                "errors":     errors,
                "warnings":   warnings,
                "dockerfile": dockerfile,
                "success":    bool(dockerfile)
            })

        except Exception as e:
            elapsed = round(time.time() - start, 1)
            results.append({
                "model":      model_name,
                "time":       elapsed,
                "score":      0,
                "errors":     1,
                "warnings":   0,
                "dockerfile": "",
                "success":    False,
                "error":      str(e)
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results