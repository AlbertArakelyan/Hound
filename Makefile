SHELL := /bin/bash
VENV := .venv

.DEFAULT_GOAL := run
.PHONY: run

run:
	@if [ ! -f "$(VENV)/bin/activate" ]; then \
		echo "error: no venv at $(VENV). Create one first:"; \
		echo "  python3 -m venv $(VENV) && $(VENV)/bin/pip install -r requirements.txt"; \
		exit 1; \
	fi
	@if [ -n "$$VIRTUAL_ENV" ]; then \
		python3 main.py; \
	else \
		echo "activating $(VENV)"; \
		source $(VENV)/bin/activate && python3 main.py; \
	fi
