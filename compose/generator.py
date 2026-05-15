import yaml
from .templates import COMPOSE_TEMPLATES, DEFAULT_TEMPLATE
from pathlib import Path

def generate_compose(project_info: dict, options: dict) -> str:
    framework = project_info.get("framework", "").lower()
    language  = project_info.get("language",  "").lower()

    # pick best matching template
    template = COMPOSE_TEMPLATES.get(framework) or \
               COMPOSE_TEMPLATES.get(f"generic {language}") or \
               DEFAULT_TEMPLATE

    import copy
    compose = copy.deepcopy(template)

    # apply user options
    if not options.get("include_db") and "db" in compose["services"]:
        del compose["services"]["db"]
        if "postgres_data" in compose.get("volumes", {}):
            del compose["volumes"]["postgres_data"]
        if "mongo_data" in compose.get("volumes", {}):
            del compose["volumes"]["mongo_data"]
        for svc in compose["services"].values():
            if "depends_on" in svc:
                svc["depends_on"] = [
                    d for d in svc["depends_on"] if d != "db"
                ]

    if not options.get("include_redis") and "redis" in compose["services"]:
        del compose["services"]["redis"]
        for svc in compose["services"].values():
            if "depends_on" in svc:
                svc["depends_on"] = [
                    d for d in svc["depends_on"] if d != "redis"
                ]

    if not options.get("include_nginx") and "nginx" in compose["services"]:
        del compose["services"]["nginx"]

    # clean empty depends_on
    for svc in compose["services"].values():
        if "depends_on" in svc and not svc["depends_on"]:
            del svc["depends_on"]

    # clean empty volumes at top level
    compose["volumes"] = {
        k: v for k, v in compose.get("volumes", {}).items()
        if k in _used_volumes(compose["services"])
    }
    if not compose["volumes"]:
        del compose["volumes"]

    # build final structure
    output = {"version": "3.8", "services": compose["services"]}
    if "volumes" in compose:
        output["volumes"] = compose["volumes"]

    return yaml.dump(output, default_flow_style=False, sort_keys=False, allow_unicode=True)


def _used_volumes(services: dict) -> set:
    used = set()
    for svc in services.values():
        for v in svc.get("volumes", []):
            if ":" in v:
                name = v.split(":")[0]
                if "/" not in name and "." not in name:
                    used.add(name)
    return used


def save_compose(content: str, destination: str = ".") -> str:
    out = Path(destination) / "docker-compose.yml"
    out.write_text(content)
    return str(out.resolve())