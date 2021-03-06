#
#	 Makefile, ver 1.7.1
#
# --- declarations  --------------------------------------------------------------------------------


PROJECT := ec2tools
CUR_DIR = $(shell pwd)
PYTHON_VERSION := python3
PYTHON3_PATH := $(shell which $(PYTHON_VERSION))
GIT := $(shell which git)
VENV_DIR := $(CUR_DIR)/p3_venv
PIP_CALL := $(VENV_DIR)/bin/pip
ACTIVATE = $(shell . $(VENV_DIR)/bin/activate)
MAKE = $(shell which make)
MODULE_PATH := $(CUR_DIR)/$(PROJECT)
SCRIPTS := $(CUR_DIR)/scripts
S3UPLOAD_SCRIPT = s3upload.sh
DOC_PATH := $(CUR_DIR)/docs
CONFIG_PATH = $(HOME)/.config/$(PROJECT)
REQUIREMENT = $(CUR_DIR)/requirements.txt
VERSION_FILE = $(CUR_DIR)/$(PROJECT)/_version.py

# formatting
org := \033[38;5;95;38;5;214m
bold := \u001b[1m
bbl := \033[38;5;51m
byg := \033[38;5;95;38;5;155m
bwt := \033[38;5;15m
rst := \u001b[0m


# --- rollup targets  ------------------------------------------------------------------------------


.PHONY: fresh-install fresh-test-install deploy-test deploy-prod

zero-source-install: clean source-install build-sizes  ## Install (source: local). Zero prebuild artifacts

zero-test-install: clean setup-venv test-install  ## Install (source: testpypi). Zero prebuild artifacts

deploy-test: clean testpypi  ## Deploy (testpypi), generate all prebuild artifacts

deploy-prod: clean pypi   ## Deploy (pypi), generate all prebuild artifacts


# --- targets -------------------------------------------------------------------------------------


.PHONY: pre-build
pre-build:    ## Remove residual build artifacts
	rm -rf $(CUR_DIR)/dist
	mkdir $(CUR_DIR)/dist


.PHONY: setup-venv
setup-venv:  pre-build   ## Create and activiate python venv
	$(PYTHON3_PATH) -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate && $(PIP_CALL) install -U setuptools pip && \
	$(PIP_CALL) install -r $(REQUIREMENT)


.PHONY: test
test:     ## Run pytest unittests
	if [ $(PDB) ]; then PDB = "true"; \
	bash $(CUR_DIR)/scripts/make-test.sh $(CUR_DIR) $(VENV_DIR) $(MODULE_PATH) $(PDB); \
	elif [ $(MODULE) ]; then PDB = "false"; \
	bash $(CUR_DIR)/scripts/make-test.sh $(CUR_DIR) $(VENV_DIR) $(MODULE_PATH) $(PDB) $(MODULE); \
	elif [ $(COMPLEXITY) ]; then COMPLEXITY = "run"; \
	bash $(CUR_DIR)/scripts/make-test.sh $(CUR_DIR) $(VENV_DIR) $(MODULE_PATH) $(COMPLEXITY) $(MODULE); \
	else bash $(CUR_DIR)/scripts/make-test.sh $(CUR_DIR) $(VENV_DIR) $(MODULE_PATH); fi


docs:  setup-venv    ## Generate sphinx documentation
	. $(VENV_DIR)/bin/activate && \
	$(PIP_CALL) install sphinx sphinx_rtd_theme autodoc
	cd $(CUR_DIR) && $(MAKE) clean-docs
	cd $(DOC_PATH) && . $(VENV_DIR)/bin/activate && $(MAKE) html


.PHONY: build
build: pre-build setup-venv    ## Build dist, increment version || force version (VERSION=X.Y)
	if [ $(VERSION) ]; then bash $(SCRIPTS)/version_update.sh $(VERSION); \
	else bash $(SCRIPTS)/version_update.sh; fi && . $(VENV_DIR)/bin/activate && \
	cd $(CUR_DIR) && $(PYTHON3_PATH) setup.py sdist


.PHONY: build-sizes
build-sizes:	##  Create ec2 sizes.txt if 10 days age. FORCE=true trigger refresh
	cp $(MODULE_PATH)/_version.py $(SCRIPTS)/
	if [ -d $(VENV_DIR) ]; then . $(VENV_DIR)/bin/activate && \
	$(PYTHON3_PATH) $(SCRIPTS)/ec2sizes.py $(FORCE); else \
	$(MAKE) setup-venv && . $(VENV_DIR)/bin/activate && \
	$(PYTHON3_PATH) $(SCRIPTS)/ec2sizes.py $(FORCE); fi
	rm -f $(SCRIPTS)/_version.py


.PHONY: testpypi
testpypi: build-sizes build ## Deploy to testpypi without regenerating prebuild artifacts
	@echo "Deploy $(PROJECT) to test.pypi.org"
	. $(VENV_DIR)/bin/activate && twine upload --repository testpypi dist/*


.PHONY: pypi
pypi: clean build-sizes build ## Deploy to pypi without regenerating prebuild artifacts
	@echo "Deploy $(bd)$(bbl)$(PROJECT)$(rst) to pypi.org"
	. $(VENV_DIR)/bin/activate && twine upload --repository pypi dist/*


.PHONY: install
install:  setup-venv  ## Install (source: pypi). Build artifacts exist
	cd $(CUR_DIR) && . $(VENV_DIR)/bin/activate && \
	$(PIP_CALL) install -U $(PROJECT)


.PHONY: test-install
test-install:  setup-venv ## Install (source: testpypi). Build artifacts exist
	cd $(CUR_DIR) && . $(VENV_DIR)/bin/activate && \
	$(PIP_CALL) install -U $(PROJECT) --extra-index-url https://test.pypi.org/simple/


.PHONY: source-install
source-install: clean setup-venv  ## Install (source: local source). Build artifacts exist
	cd $(CUR_DIR) && . $(VENV_DIR)/bin/activate && $(PIP_CALL) install . ; \
	if [[ ! -d $(CONFIG_PATH)/userdata ]]; then mkdir -p $(CONFIG_PATH)/userdata; fi; \
	cp $(CUR_DIR)/userdata/*.sh $(CONFIG_PATH)/userdata/ ; \
	bash $(SCRIPTS)/$(S3UPLOAD_SCRIPT);


.PHONY: update-src-install
update-src-install:     ## Update Install (source: local source).
	if [ -e $(VENV_DIR) ]; then \
	cp -rv $(MODULE_PATH) $(VENV_DIR)/lib/python3.*/site-packages/; else \
 	printf -- '\n  %s\n\n' "No virtualenv built - nothing to update"; fi; \
	if [[ ! -d $(CONFIG_PATH)/userdata ]]; then mkdir -p $(CONFIG_PATH)/userdata; fi;  \
	cp $(CUR_DIR)/userdata/* $(CONFIG_PATH)/userdata/


.PHONY: upload-artifacts
upload-artifacts:    ## Upload ec2 configuration mgmt files to Amazon S3
	if [ ! -e $(VENV_DIR) ]; then $(MAKE) setup-venv && . $(VENV_DIR)/bin/activate && \
	bash $(SCRIPTS)/$(S3UPLOAD_SCRIPT); else \
	. $(VENV_DIR)/bin/activate && bash $(SCRIPTS)/$(S3UPLOAD_SCRIPT); fi


.PHONY: help
help:   ## Print help index
	@printf "\n\033[0m %-15s\033[0m %-13s\u001b[37;1m%-15s\u001b[0m\n\n" " " "make targets: " $(PROJECT)
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf "\033[0m%-2s\033[36m%-20s\033[33m %-8s\033[0m%-5s\n\n"," ", $$1, "-->", $$2}' $(MAKEFILE_LIST)
	@printf "\u001b[37;0m%-2s\u001b[37;0m%-2s\n\n" " " "___________________________________________________________________"
	@printf "\u001b[37;1m%-3s\u001b[37;1m%-3s\033[0m %-6s\u001b[44;1m%-9s\u001b[37;0m%-15s\n\n" " " "  make" "deploy-[test|prod] " "VERSION=X" " to deploy specific version"


.PHONY: clean-docs
clean-docs:    ## Remove build artifacts for documentation only
	@echo "Clean docs build"
	if [ -e $(VENV_DIR) ]; then . $(VENV_DIR)/bin/activate && \
	cd $(DOC_PATH) && $(MAKE) clean || true; fi


.PHONY: clean
clean:  clean-docs  ## Remove all build artifacts generated by make
	@echo "Cleanup"
	rm -rf $(VENV_DIR) || true
	rm -rf $(CUR_DIR)/dist || true
	rm -rf $(CUR_DIR)/*.egg-info || true
	rm -f $(CUR_DIR)/README.rst || true
	rm -rf $(CUR_DIR)/$(PROJECT)/__pycache__ || true
	rm -rf $(CUR_DIR)/tests/__pycache__ || true
	rm -rf $(CUR_DIR)/.pytest_cache || true
