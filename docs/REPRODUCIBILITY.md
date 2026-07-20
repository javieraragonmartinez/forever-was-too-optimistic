# Reproducibility

All algebraic checks are exact. The generator uses SymPy over the rational numbers; the independent verifier uses only the Python standard library and a separate sparse-polynomial implementation.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/bcw_yagzhev_certificate.py --write-artifact /tmp/bcw-yagzhev-dim79.json
cmp /tmp/bcw-yagzhev-dim79.json artifacts/bcw-yagzhev-dim79.json
python scripts/verify_bcw_yagzhev_artifact.py artifacts/bcw-yagzhev-dim79.json
python -m jsonschema -i artifacts/bcw-yagzhev-dim79.json artifacts/bcw-yagzhev-certificate.schema.json
python -m unittest discover -v
sha256sum -c artifacts/SHA256SUMS
```

Compile the paper with three `pdflatex` passes.
