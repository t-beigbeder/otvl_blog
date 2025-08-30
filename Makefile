all:
	@echo "nothing is done when 'all' is done, try make help"
help:	## show this help
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

VENV := $(shell if [ -z "${VENV}" ] ; then echo /tools/venvs/otvl_blog ; else echo ${VENV} ; fi)

.PHONY: venv
venv: ## create a virtualenv and install dependencies
venv:
	virtualenv $(VENV)
	$(VENV)/bin/pip install pip-tools
	$(VENV)/bin/pip-compile requirements-dev.in
	$(VENV)/bin/pip-compile requirements.in
	$(VENV)/bin/pip install -r requirements.txt -r requirements-dev.txt

.PHONY: qa
qa:	## launch QA tests
	$(VENV)/bin/flake8 src
