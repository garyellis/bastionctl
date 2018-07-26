.PHONY: help
	.DEFAULT_GOAL := help

help: ## show this message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

activate_venv = source venv/bin/activate

install: ## install the virtualenv environment
	python -m virtualenv --python python2.7 venv
	$(activate_venv); \
	pip install -r requirements.txt && \
	python setup.py develop

lint: ## run flake8 style checks
	$(activate_venv); flake8 ./ec2_patching

test: ## run unit tests
	$(activate_venv); pytest --capture=no -vvvv tests

test-integration: ## run integration tests
	$(activate_venv); pytest --capture=no -vvvv integration-tests

clean: ## remove temporary files and virtualenv environment
	rm -rf .tox .Python bin .cache include lib man iam_reporter.egg-info pip-selfcheck.json venv
