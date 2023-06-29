SHELL=/bin/bash

# Include the environment variables from .env file
include .env

# List of all targets that are not files
.PHONY: git install_dependencies test style

# Load environment variables from .env file
VARS:=$(shell sed -ne 's/ *\#.*$$//; /./ s/=.*$$// p' .env )
$(foreach v,$(VARS),$(eval $(shell echo export $(v)="$($(v))")))


# Setup target to run the setup script
setup: #install_dependencies
	@bash setup.sh

install_dependencies:
	@pipenv install --dev

test:
	@pytest tests/ -s

style: 
	@black scrapers/
	@isort scrapers/
	@pylint --recursive=y -sn -rn scrapers/ --ignore-imports=yes  --errors-only --exit-zero

git: 
	@git add . && git commit -m "$$(openssl rand -hex 5)" && git push -u origin main

xd: 
	@cat manifests/airflow.yaml | envsubst | kubectl apply -f -
