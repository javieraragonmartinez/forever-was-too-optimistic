# Carrusel visual

Ocho láminas verticales de 1080 × 1350 píxeles para presentar el preprint de
forma rigurosa y accesible.

## Orden

1. `01-portada.png` — título y tesis visual.
2. `02-el-mapa.png` — las tres componentes del mapa.
3. `03-local-vs-global.png` — diferencia entre invertibilidad local y global.
4. `04-colision-racional.png` — los tres puntos y su imagen común.
5. `05-que-cae.png` — consecuencias y límites del resultado.
6. `06-geometria-fibras.png` — cúbica, grado genérico y superficie asintótica.
7. `07-reduccion-79.png` — reducción constructiva 3 → 39 → 79.
8. `08-como-comprobarlo.png` — paquete de verificación y estado científico.

## Texto sugerido para la publicación

Un mapa polinómico explícito de dimensión tres tiene determinante jacobiano
constante `−2`, pero tres puntos racionales distintos comparten exactamente
la misma imagen. Este carrusel resume el certificado elemental, su geometría
y la infraestructura reproducible que acompaña al preprint.

Preprint independiente, versión 1.0, 20 de julio de 2026. No revisado por
pares. DOI `10.5281/zenodo.21460623` reservado y pendiente de publicación.

## Regeneración

```bash
python scripts/generate_carousel.py
```

La paleta reproduce la identidad visual del artículo y todo el texto se
renderiza determinísticamente con Pillow y las fuentes DejaVu de TeX Live.