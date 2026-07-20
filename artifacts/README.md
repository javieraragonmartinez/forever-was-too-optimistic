# BCW/Yagzhev certificate format

`bcw-yagzhev-dim79.json` uses schema `bcw-yagzhev-certificate-v2`.  Its
authoritative algebraic representation consists entirely of exact rational
numbers and sparse polynomials.

## Top-level sections

| Field | Meaning |
|---|---|
| `schema`, `schema_file` | Format version and local JSON Schema. |
| `release` | Titles, author/contact, version/date and reserved DOI status. |
| `format` | Coefficient field and polynomial encodings. |
| `provenance` | Generator command, software versions and SHA-256 hashes. |
| `dimensions` | Dimensions 3, 39 and 79 in the constructive chain. |
| `source_map` | Original map, determinant `-2` and rational collision. |
| `normalization` | Exact transformation `K=(F3/2,F2,F1)` and determinant `1`. |
| `degree_reduction` | The 18 elementary operations and the exact size profile. |
| `intermediate_map` | The 39-dimensional map and its `I+A2+A3` decomposition. |
| `final_map` | The 79-dimensional cubic homogeneous map and collision data. |
| `claims` | Machine-readable summary of the certified conclusions. |

## Polynomial objects

Each polynomial has two fields:

```json
{
  "expression": "x**2 - 3*y/2",
  "terms": [
    {"coefficient": "1", "exponents": [2, 0]},
    {"coefficient": "-3/2", "exponents": [0, 1]}
  ]
}
```

The enclosing section declares the variable order.  Exponent vectors always
have that full length.  Coefficients are reduced rational strings; the
denominator is positive.  Terms with zero coefficient are forbidden, and an
empty list represents the zero polynomial.

`expression` is included for readers.  `terms` is canonical and is the input
used by the independent verifier.

## Degree-reduction steps

For step `j`, `variables_before` fixes the current coordinate order,
`new_variables` is `[uj,vj]`, and `component` is one-based.  If `P` and `Q`
are the recorded polynomials, the transformation is

```text
K_component <- K_component - (uj + P)(vj + Q)
K_uj        <- uj + P
K_vj        <- vj + Q.
```

The Jacobian row certificate is

```text
row(component) + (vj+Q) row(uj) + (uj+P) row(vj)
    = old row(component),
```

with the old row padded by two zeros.  Together with the two final identity
columns, this proves determinant preservation without expanding a growing
determinant.

## Final block construction

Writing the intermediate map as `K(X)=X+A2(X)+A3(X)`, the final variables are
ordered as `(X,Y,T)` and the final map is

```text
(X + Y T^2 + A2(X) T,  Y - A3(X),  T).
```

Every nonlinear monomial has degree three.  The verified block-Jacobian
identity reduces its determinant to the determinant-one identity for `K`.

## Verification

Generate and verify with:

```text
python scripts/bcw_yagzhev_certificate.py \
  --write-artifact artifacts/bcw-yagzhev-dim79.json
python scripts/verify_bcw_yagzhev_artifact.py \
  artifacts/bcw-yagzhev-dim79.json
```

The second command is independent of SymPy and of the generator source. A
successful run ends with `Certificate verification: PASS`.