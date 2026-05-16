import ollama

OPTIMIZER_PROMPT = """You are a Docker expert. Analyze this Dockerfile and rewrite it to be:
1. Smaller image size (use slim/alpine base images)
2. More secure (non-root user, no unnecessary packages)
3. Better layer caching (copy dependency files before source code)
4. Fewer layers (combine RUN commands with &&)
5. Production ready (proper CMD format, no dev tools)

Original Dockerfile:
```dockerfile
{dockerfile}
```

Respond ONLY in this exact format, nothing else:

OPTIMIZED:
```dockerfile
<your optimized dockerfile here>
```

CHANGES:
- <change 1>
- <change 2>
- <change 3>
- <change 4>
- <change 5>

SAVINGS:
<estimated size reduction, e.g. "~60% smaller image (from ~900MB to ~180MB)">
"""

def optimize_dockerfile(dockerfile: str, model: str = "codellama") -> dict:
    prompt = OPTIMIZER_PROMPT.format(dockerfile=dockerfile)

    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response["message"]["content"]
    return parse_optimizer_response(raw)


def parse_optimizer_response(raw: str) -> dict:
    import re

    # Extract optimized dockerfile
    optimized = ""
    match = re.search(r"OPTIMIZED:.*?```dockerfile\s*([\s\S]*?)```", raw, re.IGNORECASE)
    if match:
        optimized = match.group(1).strip()
    else:
        # fallback: look for any dockerfile block
        match = re.search(r"```dockerfile\s*([\s\S]*?)```", raw, re.IGNORECASE)
        if match:
            optimized = match.group(1).strip()
        elif "FROM" in raw:
            optimized = raw.strip()

    # Extract changes list
    changes = []
    match = re.search(r"CHANGES:([\s\S]*?)(?:SAVINGS:|$)", raw, re.IGNORECASE)
    if match:
        lines = match.group(1).strip().split("\n")
        for line in lines:
            line = line.strip().lstrip("-•*").strip()
            if line:
                changes.append(line)

    # Extract savings
    savings = ""
    match = re.search(r"SAVINGS:(.*?)(?:\n\n|$)", raw, re.IGNORECASE | re.DOTALL)
    if match:
        savings = match.group(1).strip()

    return {
        "optimized":  optimized,
        "changes":    changes,
        "savings":    savings,
        "raw":        raw,
        "success":    bool(optimized)
    }


def diff_dockerfiles(original: str, optimized: str) -> list:
    orig_lines = original.strip().splitlines()
    opt_lines  = optimized.strip().splitlines()

    result = []

    orig_set = set(l.strip() for l in orig_lines)
    opt_set  = set(l.strip() for l in opt_lines)

    for line in orig_lines:
        if line.strip() not in opt_set:
            result.append({"type": "removed", "line": line})
        else:
            result.append({"type": "kept", "line": line})

    for line in opt_lines:
        if line.strip() not in orig_set:
            result.append({"type": "added", "line": line})

    return result