<p align="center"><img src="assets/repository-cover.png" alt="Portada académica: tres puntos racionales convergen en una imagen" width="100%"></p>

# Ahora sabemos que “siempre” era demasiado optimista

[English](README.en.md) · **Español**

[![Build and verify](https://github.com/javieraragonmartinez/forever-was-too-optimistic/actions/workflows/build-and-verify.yml/badge.svg)](https://github.com/javieraragonmartinez/forever-was-too-optimistic/actions/workflows/build-and-verify.yml)
![Preprint](https://img.shields.io/badge/status-preprint-B88430)
![Peer review](https://img.shields.io/badge/peer_review-pending-24598F)
![License](https://img.shields.io/badge/license-CC_BY_4.0_%2B_MIT-1A6B6B)

**English title:** *Now We Know That “Always” Was Too Optimistic*

Versión 1.0 de un preprint extremadamente reciente, fechado el 20 de julio de 2026. No ha sido revisado por pares. El núcleo algebraico se acompaña de un certificado exacto, un esquema JSON y un verificador independiente que usa solo la biblioteca estándar de Python.

## El certificado elemental

\[
F(x,y,z)=\left(
\begin{aligned}
 &(1+xy)^3z+y^2(1+xy)(4+3xy),\\
 &y+3x(1+xy)^2z+3xy^2(4+3xy),\\
 &2x-3x^2y-x^3z
\end{aligned}
\right), \qquad \det JF=-2.
\]

Sin embargo, los tres puntos racionales distintos

\[
\left(0,0,-\frac14\right),\quad
\left(1,-\frac32,\frac{13}{2}\right),\quad
\left(-1,\frac32,\frac{13}{2}\right)
\]

tienen la imagen común \(F(p)=(-1/4,0,0)\). Por tanto, `F` tiene determinante jacobiano constante y no nulo, pero no es inyectivo. El manuscrito estudia además las fibras, la no propiedad, la normalización de la superficie asintótica y una reducción constructiva de Bass–Connell–Wright/Yagzhev a dimensión 79.

## Estado científico

- Preprint independiente; no revisado por pares.
- Resultado todavía sujeto a verificación, revisión de prioridad y evaluación matemática externa.
- Las identidades y colisiones se comprueban con aritmética racional exacta por dos implementaciones separadas.
- No se afirma respaldo institucional por discusiones, publicaciones informales o repositorios de terceros.
- El DOI `10.5281/zenodo.21460623` está **reservado y pendiente de publicación**.

## Generación y verificación

```bash
python -m pip install -r requirements.txt
python scripts/bcw_yagzhev_certificate.py --write-artifact artifacts/bcw-yagzhev-dim79.json
python scripts/verify_bcw_yagzhev_artifact.py artifacts/bcw-yagzhev-dim79.json
python -m jsonschema -i artifacts/bcw-yagzhev-dim79.json artifacts/bcw-yagzhev-certificate.schema.json
python -m unittest discover -v
sha256sum -c artifacts/SHA256SUMS
```

El artículo se compila con tres pases de `pdflatex`. La automatización del repositorio regenera el PDF, el certificado, los gráficos y el manifiesto SHA-256.

## Alcance, atribución y licencias

- [`docs/MATHEMATICAL_SCOPE.md`](docs/MATHEMATICAL_SCOPE.md)
- [`docs/ATTRIBUTION.md`](docs/ATTRIBUTION.md)
- [`docs/REPRODUCIBILITY.md`](docs/REPRODUCIBILITY.md)
- [`LICENSE.md`](LICENSE.md)
- [`CITATION.cff`](CITATION.cff)

## Sistema visual

- [Portada académica](assets/repository-cover.png)
- [Vista previa social](assets/social-preview.png)
- [Visual abstract SVG](assets/visual-abstract.svg)
- [Carrusel académico revisado](carousel-v2/)
- [Fuente editable en Figma](https://www.figma.com/design/Zz8DXi2BvnEV0f4rWOaI1F)

La identidad visual utiliza únicamente relaciones demostrables del ejemplo: tres puntos racionales distintos, una imagen común y el determinante jacobiano constante.
