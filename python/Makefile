.PHONY: help
help: ## Prints help message.
	@ grep -h -E '^[a-zA-Z0-9_-].+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[1m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: localenv
localenv: ## Sets the local env.
	@ echo "Setup dependencies for the env with Python located in $$(which python)"
	@ python -m pip install -qq --upgrade pip pip-tools
	@ python -m pip install -qq -e '.[dev]'
	@ echo "Done"

.PHONY: tests
tests: ## Runs unittests.
	@ python -m pytest -vv


PY_VER := 3.10 3.11

.PHONY: .tests-docker
.tests-docker: localenv tests

.PHONY: tests-all
tests-all: ## Runs unittests for all supported Python versions.
	@ for ver in $(PY_VER); do \
   		echo Run tests for Python $$ver; \
   		docker run -v ${PWD}:/app -w /app -it python:$$ver-alpine /bin/sh -c "echo 'Setup OS dependencies' && apk add -q make && echo 'Done' && make .tests-docker"; \
   	  done

.PHONY: devtests
lint: ## Runs linters and type checks, and apply fixes.
	@ isort marketing_manager_api
	@ black marketing_manager_api
	@ mypy marketing_manager_api

.DEFAULT_GOAL := help
