SHELL := /bin/bash
VENV := .venv
PY := python3

.DEFAULT_GOAL := run
.PHONY: run install

# Fail if there is no venv, then activate it unless one is already active.
# Every line ends with a backslash so the whole block stays one shell command,
# which is what lets the activation survive into the rest of the recipe.
define require_venv
if [ ! -f "$(VENV)/bin/activate" ]; then \
	echo "error: no venv at $(VENV). Create one first:"; \
	echo "  $(PY) -m venv $(VENV) && make install"; \
	exit 1; \
fi; \
if [ -z "$$VIRTUAL_ENV" ]; then \
	echo "activating $(VENV)"; \
	source $(VENV)/bin/activate; \
fi
endef

run:
	@$(require_venv); \
	$(PY) main.py

install:
	@$(require_venv); \
	$(PY) -m pip install -r requirements.txt
