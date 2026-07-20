# Release 1.0 checklist

Run from a clean checkout:

```bash
python -m pip install -r requirements.txt
python -m unittest discover -v
python scripts/bcw_yagzhev_certificate.py --write-artifact /tmp/certificate.json
cmp /tmp/certificate.json artifacts/bcw-yagzhev-dim79.json
python scripts/verify_bcw_yagzhev_artifact.py artifacts/bcw-yagzhev-dim79.json
python -m jsonschema -i artifacts/bcw-yagzhev-dim79.json artifacts/bcw-yagzhev-certificate.schema.json
sha256sum -c artifacts/SHA256SUMS
```

The committed PDF must have 43 pages and be compiled from the committed TeX
source. The DOI remains reserved until the external archive is published and
its files are compared with this release.

The canonical archive contains 43 files. `artifacts/SHA256SUMS` verifies the other 42 files and deliberately excludes itself.
