PYTHON ?= python

.PHONY: verify generate test schema hashes paper all

generate:
	$(PYTHON) scripts/bcw_yagzhev_certificate.py --write-artifact artifacts/bcw-yagzhev-dim79.json

verify:
	$(PYTHON) scripts/verify_bcw_yagzhev_artifact.py artifacts/bcw-yagzhev-dim79.json

test:
	$(PYTHON) -m unittest discover -v

schema:
	$(PYTHON) -m jsonschema -i artifacts/bcw-yagzhev-dim79.json artifacts/bcw-yagzhev-certificate.schema.json

hashes:
	sha256sum -c artifacts/SHA256SUMS

paper:
	pdflatex -interaction=nonstopmode -halt-on-error ahora-sabemos-v1.0.tex
	pdflatex -interaction=nonstopmode -halt-on-error ahora-sabemos-v1.0.tex
	pdflatex -interaction=nonstopmode -halt-on-error ahora-sabemos-v1.0.tex

all: test schema verify hashes
