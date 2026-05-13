RULES = [
    {
        "id": "R001",
        "severity": "error",
        "check": lambda lines: not any(l.strip().startswith("FROM") for l in lines),
        "message": "Missing FROM instruction — every Dockerfile must start with FROM."
    },
    {
        "id": "R002",
        "severity": "error",
        "check": lambda lines: not any(l.strip().startswith("CMD") or l.strip().startswith("ENTRYPOINT") for l in lines),
        "message": "Missing CMD or ENTRYPOINT — container won't know how to start."
    },
    {
        "id": "R003",
        "severity": "warning",
        "check": lambda lines: not any(l.strip().startswith("WORKDIR") for l in lines),
        "message": "Missing WORKDIR — files will be placed in root directory."
    },
    {
        "id": "R004",
        "severity": "warning",
        "check": lambda lines: any("latest" in l and l.strip().startswith("FROM") for l in lines),
        "message": "Using 'latest' tag in FROM — pin a specific version for reproducible builds."
    },
    {
        "id": "R005",
        "severity": "warning",
        "check": lambda lines: any(
            l.strip().startswith("RUN") and "apt-get install" in l and "apt-get update" not in l
            for l in lines
        ),
        "message": "Running apt-get install without apt-get update — may install outdated packages."
    },
    {
        "id": "R006",
        "severity": "warning",
        "check": lambda lines: any(
            l.strip().startswith("RUN") and "apt-get" in l and "--no-install-recommends" not in l
            for l in lines
        ),
        "message": "apt-get install without --no-install-recommends — image will be unnecessarily large."
    },
    {
        "id": "R007",
        "severity": "info",
        "check": lambda lines: not any(l.strip().startswith("EXPOSE") for l in lines),
        "message": "No EXPOSE instruction — consider documenting which port the app listens on."
    },
    {
        "id": "R008",
        "severity": "warning",
        "check": lambda lines: any(
            "root" in l.lower() and l.strip().startswith("USER")
            for l in lines
        ),
        "message": "Running as root user — add a non-root USER for security."
    },
    {
        "id": "R009",
        "severity": "info",
        "check": lambda lines: not any(l.strip().startswith("USER") for l in lines),
        "message": "No USER instruction — consider adding a non-root user for better security."
    },
    {
        "id": "R010",
        "severity": "warning",
        "check": lambda lines: any(
            l.strip().startswith("RUN") and "&&" not in l and
            sum(1 for x in lines if x.strip().startswith("RUN")) > 3
            for l in lines
        ),
        "message": "Multiple separate RUN instructions — combine with && to reduce image layers."
    },
]