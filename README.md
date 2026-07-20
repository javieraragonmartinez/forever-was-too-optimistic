# Ahora sabemos que “siempre” era demasiado optimista

**English title:** *Now We Know That “Always” Was Too Optimistic*

Versión 1.0 de un preprint extremadamente reciente, fechado el 20 de julio de
2026. No ha sido revisado por pares. El núcleo algebraico se acompaña de un
certificado exacto, un esquema JSON y un verificador independiente que usa
solo la biblioteca estándar de Python.

## El certificado elemental

El mapa polinómico estudiado es

\[
F(x,y,z)=\left(
\begin{aligned}
 &(1+xy)^3z+y^2(1+xy)(4+3xy),\\
 &y+3x(1+xy)^2z+3xy^2(4+3xy),\\
 &2x-3x^2y-x^3z
\end{aligned}
\right).
\]

La diferenciación exacta da

\[
\det JF=-2.
\]

Sin embargo, los tres puntos racionales distintos

\[
\left(0,0,-\frac14\right),\qquad
\left(1,-\frac32,\frac{13}{2}\right),\qquad
\left(-1,\frac32,\frac{13}{2}\right)
\]

tienen la imagen común

\[
F(p)=\left(-\frac14,0,0\right).
\]

Por tanto, `F` tiene determinante jacobiano constante y no nulo, pero no es
inyectivo; esto contradice la afirmación universal de la conjetura jacobiana
en dimensión tres. El manuscrito estudia además las fibras, la no propiedad,
la normalización de la superficie asintótica y una reducción constructiva de
Bass–Connell–Wright/Yagzhev a dimensión 79.

## Estado científico

- Preprint independiente; no revisado por pares.
- Resultado anunciado el 20 de julio de 2026 y todavía sujeto a verificación,
  revisión de prioridad y evaluación matemática externa.
- Las identidades polinómicas y las colisiones se comprueban con aritmética
  racional exacta por dos implementaciones separadas.
- No se afirma respaldo institucional por la existencia de una pull request,
  una publicación informal o un repositorio de terceros.
- El DOI `10.5281/zenodo.21460623` está **reservado y pendiente de
  publicación**. No debe citarse como depósito público resoluble hasta que el
  borrador de Zenodo sea publicado y auditado.

## Estructura

```text
ahora-sabemos-v1.0.tex              fuente canónica congelada
ahora-sabemos-v1.0.pdf              PDF compilado desde esa fuente
certificates/elementary-counterexample.tex
scripts/bcw_yagzhev_certificate.py  generador exacto (SymPy)
scripts/verify_bcw_yagzhev_artifact.py
scripts/generate_carousel.py        regenerador gráfico determinista
artifacts/bcw-yagzhev-dim79.json     certificado v2
artifacts/bcw-yagzhev-certificate.schema.json
artifacts/SHA256SUMS                 manifiesto de integridad
docs/REPRODUCIBILITY.md
docs/ARCHIVING.md
docs/ATTRIBUTION.md
docs/MATHEMATICAL_SCOPE.md
tests/                               pruebas automáticas
carousel/                            ocho láminas 1080×1350 y guía de uso
```

## Generación y verificación

Generar de nuevo el certificado:

```bash
python scripts/bcw_yagzhev_certificate.py \
  --write-artifact artifacts/bcw-yagzhev-dim79.json
```

Verificarlo sin SymPy y sin importar el generador:

```bash
python scripts/verify_bcw_yagzhev_artifact.py \
  artifacts/bcw-yagzhev-dim79.json
```

Validar la estructura v2 cuando `jsonschema` esté disponible:

```bash
python -m jsonschema \
  -i artifacts/bcw-yagzhev-dim79.json \
  artifacts/bcw-yagzhev-certificate.schema.json
```

Comprobar la integridad de la release:

```bash
sha256sum -c artifacts/SHA256SUMS
```

Ejecutar las pruebas:

```bash
python -m unittest discover -v
```

## Compilación

```bash
pdflatex -interaction=nonstopmode -halt-on-error ahora-sabemos-v1.0.tex
pdflatex -interaction=nonstopmode -halt-on-error ahora-sabemos-v1.0.tex
pdflatex -interaction=nonstopmode -halt-on-error ahora-sabemos-v1.0.tex
```

Los tres pases resuelven el índice, las referencias cruzadas y los enlaces de
retorno bibliográficos.

## Alcance del suplemento computacional

El certificado comprueba el mapa fuente, los determinantes tridimensionales,
las colisiones, las 18 identidades de reducción, la reconstrucción en
dimensión 39, los conteos `39/47/38`, la forma cúbica homogénea final y las
colisiones en dimensión 79. No sustituye la revisión por pares ni demuestra
de nuevo todos los teoremas generales citados por el artículo. Véase
[`docs/MATHEMATICAL_SCOPE.md`](docs/MATHEMATICAL_SCOPE.md).

## Atribución, cita y licencias

La cronología y la separación entre resultados importados, reproducidos y
desarrollados en el manuscrito se documentan en
[`docs/ATTRIBUTION.md`](docs/ATTRIBUTION.md). Los metadatos de cita están en
[`CITATION.cff`](CITATION.cff).

El artículo y la documentación narrativa se distribuyen bajo CC BY 4.0; el
código, el esquema y los artefactos de verificación, bajo MIT. La delimitación
exacta figura en [`LICENSE.md`](LICENSE.md).
