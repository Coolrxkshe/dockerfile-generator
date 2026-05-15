COMPOSE_TEMPLATES = {

    "fastapi": {
        "services": {
            "app": {
                "build": ".",
                "ports": ["8000:8000"],
                "environment": ["DATABASE_URL=postgresql://user:password@db:5432/appdb"],
                "depends_on": ["db"],
                "volumes": [".:/app"],
                "restart": "unless-stopped"
            },
            "db": {
                "image": "postgres:15-alpine",
                "environment": [
                    "POSTGRES_USER=user",
                    "POSTGRES_PASSWORD=password",
                    "POSTGRES_DB=appdb"
                ],
                "volumes": ["postgres_data:/var/lib/postgresql/data"],
                "ports": ["5432:5432"],
                "restart": "unless-stopped"
            }
        },
        "volumes": {"postgres_data": None}
    },

    "flask": {
        "services": {
            "app": {
                "build": ".",
                "ports": ["5000:5000"],
                "environment": [
                    "FLASK_ENV=production",
                    "DATABASE_URL=postgresql://user:password@db:5432/appdb"
                ],
                "depends_on": ["db", "redis"],
                "volumes": [".:/app"],
                "restart": "unless-stopped"
            },
            "db": {
                "image": "postgres:15-alpine",
                "environment": [
                    "POSTGRES_USER=user",
                    "POSTGRES_PASSWORD=password",
                    "POSTGRES_DB=appdb"
                ],
                "volumes": ["postgres_data:/var/lib/postgresql/data"],
                "restart": "unless-stopped"
            },
            "redis": {
                "image": "redis:7-alpine",
                "ports": ["6379:6379"],
                "restart": "unless-stopped"
            }
        },
        "volumes": {"postgres_data": None}
    },

    "django": {
        "services": {
            "app": {
                "build": ".",
                "ports": ["8000:8000"],
                "command": "gunicorn config.wsgi:application --bind 0.0.0.0:8000",
                "environment": [
                    "DEBUG=0",
                    "DATABASE_URL=postgresql://user:password@db:5432/appdb",
                    "REDIS_URL=redis://redis:6379/0"
                ],
                "depends_on": ["db", "redis"],
                "volumes": [".:/app", "static_volume:/app/staticfiles"],
                "restart": "unless-stopped"
            },
            "db": {
                "image": "postgres:15-alpine",
                "environment": [
                    "POSTGRES_USER=user",
                    "POSTGRES_PASSWORD=password",
                    "POSTGRES_DB=appdb"
                ],
                "volumes": ["postgres_data:/var/lib/postgresql/data"],
                "restart": "unless-stopped"
            },
            "redis": {
                "image": "redis:7-alpine",
                "restart": "unless-stopped"
            },
            "nginx": {
                "image": "nginx:alpine",
                "ports": ["80:80"],
                "volumes": [
                    "./nginx.conf:/etc/nginx/conf.d/default.conf",
                    "static_volume:/app/staticfiles"
                ],
                "depends_on": ["app"],
                "restart": "unless-stopped"
            }
        },
        "volumes": {
            "postgres_data": None,
            "static_volume": None
        }
    },

    "express": {
        "services": {
            "app": {
                "build": ".",
                "ports": ["3000:3000"],
                "environment": [
                    "NODE_ENV=production",
                    "MONGO_URL=mongodb://mongo:27017/appdb"
                ],
                "depends_on": ["mongo"],
                "volumes": [".:/app", "/app/node_modules"],
                "restart": "unless-stopped"
            },
            "mongo": {
                "image": "mongo:7",
                "ports": ["27017:27017"],
                "volumes": ["mongo_data:/data/db"],
                "restart": "unless-stopped"
            }
        },
        "volumes": {"mongo_data": None}
    },

    "nextjs": {
        "services": {
            "app": {
                "build": ".",
                "ports": ["3000:3000"],
                "environment": ["NODE_ENV=production"],
                "restart": "unless-stopped"
            }
        },
        "volumes": {}
    },

    "go module": {
        "services": {
            "app": {
                "build": ".",
                "ports": ["8080:8080"],
                "environment": [
                    "DATABASE_URL=postgresql://user:password@db:5432/appdb"
                ],
                "depends_on": ["db"],
                "restart": "unless-stopped"
            },
            "db": {
                "image": "postgres:15-alpine",
                "environment": [
                    "POSTGRES_USER=user",
                    "POSTGRES_PASSWORD=password",
                    "POSTGRES_DB=appdb"
                ],
                "volumes": ["postgres_data:/var/lib/postgresql/data"],
                "restart": "unless-stopped"
            }
        },
        "volumes": {"postgres_data": None}
    },

    "generic python": {
        "services": {
            "app": {
                "build": ".",
                "ports": ["8000:8000"],
                "volumes": [".:/app"],
                "restart": "unless-stopped"
            }
        },
        "volumes": {}
    },

    "generic node": {
        "services": {
            "app": {
                "build": ".",
                "ports": ["3000:3000"],
                "volumes": [".:/app", "/app/node_modules"],
                "restart": "unless-stopped"
            }
        },
        "volumes": {}
    },
}

DEFAULT_TEMPLATE = {
    "services": {
        "app": {
            "build": ".",
            "ports": ["8080:8080"],
            "restart": "unless-stopped"
        }
    },
    "volumes": {}
}