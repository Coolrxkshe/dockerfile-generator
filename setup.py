from setuptools import setup, find_packages

setup(
    name="dockerfile-generator",
    version="1.0.0",
    description="Generate production-ready Dockerfiles using local LLMs",
    author="Your Name",
    packages=find_packages(),
    install_requires=[
        "ollama>=0.1.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "streamlit>=1.28.0",
    ],
    entry_points={
        "console_scripts": [
            "dockergen=main:app",
        ],
    },
    python_requires=">=3.9",
)