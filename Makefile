install:
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt

run:
	. venv/bin/activate && streamlit run app.py

cli:
	. venv/bin/activate && python main.py $(path)

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete

help:
	@echo "Commands:"
	@echo "  make install  - Setup virtual environment and install deps"
	@echo "  make run      - Launch the web UI"
	@echo "  make cli path=/your/project  - Run CLI on a project"
	@echo "  make clean    - Remove cache files"