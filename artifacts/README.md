# BCW/Yagzhev certificate format

`bcw-yagzhev-dim79.json` uses schema `bcw-yagzhev-certificate-v2`. Its authoritative representation consists entirely of exact rational numbers and sparse polynomials.

## Top-level sections

- `schema`, `schema_file`: format version and local JSON Schema.
- `release`: titles, author/contact, version/date and reserved DOI status.
- `format`: coefficient field and polynomial encodings.
- `provenance`: generation command, software versions and SHA-256 hashes.
- `dimensions`: dimensions 3, 39 and 79.
- `source_map`: original map, determinant `-2` and rational collision.
- `normalization`: exact transformation `K=(F3/2,F2,F1)` and determinant `1`.
- `degree_reduction`: 18 elementary operations and exact size profile.
- `intermediate_map`: dimension-39 map and `I+A2+A3` decomposition.
- `final_map`: dimension-79 homogeneous-cubic map and collision data.
- `claims`: machine-readable summary of the certified conclusions.

Each polynomial includes a reader-facing `expression` and a canonical `terms` array. Coefficients are reduced rational strings, exponent vectors have full length, zero terms are forbidden and an empty list represents zero.

Generate and verify with:

```bash
python scripts/bcw_yagzhev_certificate.py --write-artifact artifacts/bcw-yagzhev-dim79.json
python scripts/verify_bcw_yagzhev_artifact.py artifacts/bcw-yagzhev-dim79.json
```

The second command is independent of SymPy and of the generator source. A successful run ends with `Certificate verification: PASS`.
