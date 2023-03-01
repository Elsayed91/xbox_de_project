SHELL=/bin/bash

# Include the environment variables from .env file
include .env

# List of all targets that are not files
.PHONY: git

# Load environment variables from .env file
VARS:=$(shell sed -ne 's/ *\#.*$$//; /./ s/=.*$$// p' .env )
$(foreach v,$(VARS),$(eval $(shell echo export $(v)="$($(v))")))


# Setup target to run the setup script
setup:
	@bash setup.sh

r:
	@kubectl delete -f ${arg} && cat ${arg} | envsubst | kubectl apply -f -

rr: 
	@cat ${arg} | envsubst | kubectl apply -f -

git: 
	@git add . && git commit -m "$$(openssl rand -hex 5)" && git push -u origin main