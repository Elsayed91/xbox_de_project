SHELL=/bin/bash

# Include the environment variables from .env file
include .env

# List of all targets that are not files
.PHONY: 

# Load environment variables from .env file
VARS:=$(shell sed -ne 's/ *\#.*$$//; /./ s/=.*$$// p' .env )
$(foreach v,$(VARS),$(eval $(shell echo export $(v)="$($(v))")))


# Setup target to run the setup script
setup:
	@bash setup.sh