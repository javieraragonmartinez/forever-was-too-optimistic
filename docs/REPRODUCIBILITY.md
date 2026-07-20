# Reproducibility

All algebraic checks are exact. The generator uses SymPy over the rational
numbers; the independent verifier uses only the Python standard library and
a separate sparse-polynomial implementation.

## Environment

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

## Regenerate the certificate

```bash
python scripts/bcw_yagzhev_certificate.py \
  --write-artifact /tmp/bcw-yagzhev-dim79.json
cmp /tmp/bcw-yagzhev-dim79.json artifacts/bcw-yagzhev-dim79.json
```

## Independent verification

```bash
python scripts/verify_bcw_yagzhev_artifact.py \
  artifacts/bcw-yagzhev-dim79.json
```

The verifier does not import the generator or SymPy. It reconstructs the
source map, normalization, 18 degree-lowering steps, the dimension-39 map,
the final dimension-79 block map and all three collision certificates.

## JSON Schema

```bash
python -m jsonschema \
  -i artifacts/bcw-yagzhev-dim79.json \
  artifacts/bcw-yagzhev-certificate.schema.json
```

## Tests and integrity

```bash
python -m unittest discover -v
sha256sum -c artifacts/SHA256SUMS
```

## Paper

Compile in three passes:

```bash
pdflatex -interaction=nonstopmode -halt-on-error ahora-sabemos-v1.0.tex
pdflatex -interaction=nonstopmode -halt-on-error ahora-sabemos-v1.0.tex
pdflatex -interaction=nonstopmode -halt-on-error ahora-sabemos-v1.0.tex
```
