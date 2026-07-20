#!/usr/bin/env python3
"""Render the Spanish social carousel for the Jacobian preprint.

The output is deterministic: eight 1080x1350 PNG files using only Pillow and
the DejaVu fonts distributed with TeX Live.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1080, 1350
SCALE = 2
OUT = Path("carousel")

INK = "#182230"
DEEP = "#173B57"
TEAL = "#177E89"
GOLD = "#C7922E"
PAPER = "#F8F6F0"
WHITE = "#FFFFFF"
SOFT_BLUE = "#EAF3F6"
SOFT_TEAL = "#DDEFF0"
SOFT_GOLD = "#F7EBCF"
MUTED = "#65717D"
RED = "#A34A3E"

FONT_ROOT = Path(
    "/usr/local/texlive/2025/texmf-dist/fonts/truetype/public/dejavu"
)
SANS = FONT_ROOT / "DejaVuSans.ttf"
SANS_BOLD = FONT_ROOT / "DejaVuSans-Bold.ttf"
SERIF_BOLD = FONT_ROOT / "DejaVuSerif-Bold.ttf"
MONO = FONT_ROOT / "DejaVuSansMono.ttf"


def px(value: float) -> int:
    return round(value * SCALE)


def rect(box):
    return tuple(px(value) for value in box)


def font(size: int, family: Path = SANS):
    return ImageFont.truetype(str(family), px(size))


def measure(draw, text, text_font):
    box = draw.textbbox((0, 0), text, font=text_font)
    return box[2] - box[0], box[3] - box[1]


def wrap(draw, text, text_font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if measure(draw, candidate, text_font)[0] <= px(max_width):
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_text(draw, xy, text, size, fill=INK, family=SANS, anchor="la",
              spacing=1.18, max_width=None, align="left"):
    text_font = font(size, family)
    x, y = xy
    if max_width is None:
        draw.text((px(x), px(y)), text, font=text_font, fill=fill, anchor=anchor)
        return y + size * spacing
    lines = wrap(draw, text, text_font, max_width)
    line_height = size * spacing
    for index, line in enumerate(lines):
        line_x = x
        if align == "center":
            line_x = x + max_width / 2
            line_anchor = "ma"
        elif align == "right":
            line_x = x + max_width
            line_anchor = "ra"
        else:
            line_anchor = "la"
        draw.text((px(line_x), px(y + index * line_height)), line,
                  font=text_font, fill=fill, anchor=line_anchor)
    return y + len(lines) * line_height


def rounded(draw, box, fill, outline=None, radius=24, width=2):
    draw.rounded_rectangle(rect(box), radius=px(radius), fill=fill,
                           outline=outline, width=px(width))


def line(draw, points, fill, width=3):
    draw.line([(px(x), px(y)) for x, y in points], fill=fill,
              width=px(width), joint="curve")


def circle(draw, center, radius, fill, outline=None, width=2):
    x, y = center
    draw.ellipse(rect((x-radius, y-radius, x+radius, y+radius)), fill=fill,
                 outline=outline, width=px(width))


def arrow(draw, start, end, fill=TEAL, width=4, head=13):
    x1, y1 = start
    x2, y2 = end
    line(draw, [start, end], fill, width)
    angle = math.atan2(y2-y1, x2-x1)
    left = (x2-head*math.cos(angle-math.pi/6),
            y2-head*math.sin(angle-math.pi/6))
    right = (x2-head*math.cos(angle+math.pi/6),
             y2-head*math.sin(angle+math.pi/6))
    draw.polygon([(px(x2), px(y2)), (px(left[0]), px(left[1])),
                  (px(right[0]), px(right[1]))], fill=fill)


def curve(draw, start, control, end, fill=TEAL, width=4):
    points = []
    for step in range(41):
        t = step / 40
        x = ((1-t)**2 * start[0] + 2*(1-t)*t*control[0] + t**2*end[0])
        y = ((1-t)**2 * start[1] + 2*(1-t)*t*control[1] + t**2*end[1])
        points.append((x, y))
    line(draw, points, fill, width)


def base(number, section):
    image = Image.new("RGB", (px(WIDTH), px(HEIGHT)), PAPER)
    draw = ImageDraw.Draw(image)
    draw.rectangle(rect((0, 0, WIDTH, 18)), fill=DEEP)
    circle(draw, (1002, 92), 88, SOFT_TEAL)
    circle(draw, (1025, 65), 37, GOLD)
    draw_text(draw, (72, 53), section.upper(), 18, TEAL, SANS_BOLD)
    circle(draw, (967, 1217), 31, DEEP)
    draw_text(draw, (967, 1217), str(number), 18, WHITE, SANS_BOLD, anchor="mm")
    line(draw, [(72, 1258), (930, 1258)], DEEP, 1)
    draw_text(draw, (72, 1280), "Javier Aragón · Preprint v1.0 · 20 JUL 2026",
              16, MUTED, SANS)
    return image, draw


def title(draw, text, subtitle=None):
    y = draw_text(draw, (72, 112), text, 53, DEEP, SERIF_BOLD,
                  max_width=880, spacing=1.08)
    if subtitle:
        y += 12
        y = draw_text(draw, (74, y), subtitle, 23, MUTED, SANS,
                      max_width=850, spacing=1.28)
    return y


def pill(draw, box, text, fill=DEEP, text_fill=WHITE, size=22):
    rounded(draw, box, fill, radius=28)
    x1, y1, x2, y2 = box
    draw_text(draw, ((x1+x2)/2, (y1+y2)/2), text, size, text_fill,
              SANS_BOLD, anchor="mm")


def card(draw, box, heading, body=None, accent=TEAL, body_size=22,
         fill=WHITE, heading_size=25):
    rounded(draw, box, fill, outline="#D4DCE0", radius=25, width=2)
    x1, y1, x2, _ = box
    draw.rectangle(rect((x1, y1, x1+10, box[3])), fill=accent)
    draw_text(draw, (x1+34, y1+27), heading, heading_size, DEEP, SANS_BOLD,
              max_width=x2-x1-64, spacing=1.15)
    if body:
        draw_text(draw, (x1+34, y1+76), body, body_size, INK, SANS,
                  max_width=x2-x1-64, spacing=1.28)


def save(image, name):
    OUT.mkdir(exist_ok=True)
    image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).save(
        OUT / name, optimize=True
    )


def slide_1():
    image, draw = base(1, "Conjetura jacobiana · carrusel 1/8")
    title(draw, "Ahora sabemos que “siempre” era demasiado optimista",
          "Anatomía de un contraejemplo explícito en dimensión tres")
    pill(draw, (72, 410, 420, 476), "det JF = −2", GOLD, INK, 27)
    pill(draw, (438, 410, 870, 476), "F NO ES INYECTIVA", DEEP, WHITE, 23)
    rounded(draw, (72, 535, 935, 1050), SOFT_BLUE, radius=34)
    draw_text(draw, (505, 600), "Tres ramas. Una misma imagen.", 28,
              DEEP, SANS_BOLD, anchor="ma")
    sources = [(220, 760), (505, 705), (790, 760)]
    colors = [TEAL, DEEP, GOLD]
    for index, (point, color) in enumerate(zip(sources, colors), 1):
        circle(draw, point, 43, WHITE, color, 5)
        draw_text(draw, point, f"p{index}", 22, color, SANS_BOLD, anchor="mm")
        curve(draw, (point[0], point[1]+48),
              ((point[0]+505)/2, 920), (505, 954), color, 5)
    circle(draw, (505, 954), 55, GOLD)
    draw_text(draw, (505, 954), "F(p)", 22, INK, SANS_BOLD, anchor="mm")
    pill(draw, (72, 1105, 535, 1163), "PREPRINT · NO REVISADO POR PARES",
         RED, WHITE, 18)
    save(image, "01-portada.png")


def slide_2():
    image, draw = base(2, "El objeto matemático · carrusel 2/8")
    title(draw, "El mapa", "Un endomorfismo polinómico F: ℂ³ → ℂ³")
    formulas = [
        ("F₁", "(1+xy)³z + y²(1+xy)(4+3xy)"),
        ("F₂", "y + 3x(1+xy)²z + 3xy²(4+3xy)"),
        ("F₃", "2x − 3x²y − x³z"),
    ]
    y = 350
    for label, formula in formulas:
        rounded(draw, (72, y, 935, y+172), WHITE, "#D4DCE0", 25, 2)
        pill(draw, (98, y+49, 190, y+119), label, DEEP, WHITE, 27)
        draw_text(draw, (220, y+61), formula, 25, INK, MONO,
                  max_width=675, spacing=1.2)
        y += 198
    rounded(draw, (72, 974, 935, 1140), SOFT_GOLD, radius=25)
    draw_text(draw, (104, 1010), "Datos exactos", 23, GOLD, SANS_BOLD)
    draw_text(draw, (104, 1054),
              "Coeficientes enteros · grado total 7 · definido sobre cualquier cuerpo de característica cero",
              21, INK, SANS, max_width=790, spacing=1.25)
    save(image, "02-el-mapa.png")


def slide_3():
    image, draw = base(3, "Local frente a global · carrusel 3/8")
    title(draw, "Localmente perfecto. Globalmente no.")
    card(draw, (72, 310, 500, 610), "det JF = −2",
         "La diferencial es invertible en cada punto. Existen inversas locales alrededor de todo punto.",
         TEAL, 22, SOFT_TEAL)
    card(draw, (525, 310, 935, 610), "F no es inyectiva",
         "La información infinitesimal no impide que varias hojas se conecten a través del infinito.",
         GOLD, 22, SOFT_GOLD)
    rounded(draw, (72, 680, 935, 1088), WHITE, "#D4DCE0", 30, 2)
    for x in (230, 505, 780):
        circle(draw, (x, 810), 70, SOFT_BLUE, TEAL, 4)
        circle(draw, (x, 810), 14, DEEP)
    curve(draw, (230, 890), (340, 1030), (505, 1010), TEAL, 5)
    curve(draw, (505, 890), (505, 980), (505, 1010), DEEP, 5)
    curve(draw, (780, 890), (670, 1030), (505, 1010), GOLD, 5)
    circle(draw, (505, 1010), 36, GOLD)
    draw_text(draw, (505, 729), "Invertibilidad local ≠ invertibilidad global",
              25, DEEP, SANS_BOLD, anchor="ma")
    save(image, "03-local-vs-global.png")


def slide_4():
    image, draw = base(4, "Certificado racional · carrusel 4/8")
    title(draw, "La colisión racional",
          "Tres puntos distintos producen exactamente el mismo valor")
    points = [
        ("p₁", "(0, 0, −1/4)", TEAL),
        ("p₂", "(1, −3/2, 13/2)", DEEP),
        ("p₃", "(−1, 3/2, 13/2)", GOLD),
    ]
    x_values = [72, 369, 666]
    for (label, value, color), x in zip(points, x_values):
        rounded(draw, (x, 370, x+270, 555), WHITE, color, 24, 3)
        draw_text(draw, (x+135, 414), label, 27, color, SANS_BOLD, anchor="ma")
        draw_text(draw, (x+135, 475), value, 19, INK, MONO, anchor="ma")
        curve(draw, (x+135, 560), (x+135, 700), (505, 786), color, 5)
    rounded(draw, (257, 780, 753, 940), SOFT_GOLD, GOLD, 34, 3)
    draw_text(draw, (505, 818), "F(p₁) = F(p₂) = F(p₃)", 25,
              DEEP, SANS_BOLD, anchor="ma")
    draw_text(draw, (505, 878), "(−1/4, 0, 0)", 32, INK, MONO, anchor="ma")
    rounded(draw, (72, 1005, 935, 1146), SOFT_BLUE, radius=24)
    draw_text(draw, (104, 1041),
              "Una sola colisión basta: la conjetura era una afirmación universal sobre todos los mapas de Keller.",
              22, DEEP, SANS_BOLD, max_width=790, spacing=1.22)
    save(image, "04-colision-racional.png")


def slide_5():
    image, draw = base(5, "Consecuencias · carrusel 5/8")
    title(draw, "Qué cae — y qué no")
    card(draw, (72, 300, 935, 510), "Cae",
         "JC₃ es falsa. Al añadir coordenadas identidad, también falla JCₙ para todo n ≥ 3.",
         RED, 24, "#F4E5E2")
    card(draw, (72, 545, 935, 755), "Permanece abierto",
         "El caso complejo de dimensión 2 no queda decidido por este ejemplo.",
         GOLD, 24, SOFT_GOLD)
    card(draw, (72, 790, 935, 1085), "Sigue vigente",
         "El teorema de la función inversa, los criterios bajo hipótesis adicionales y toda la geometría local. Lo que falla es el salto automático de lo local a lo global.",
         TEAL, 22, SOFT_TEAL)
    save(image, "05-que-cae.png")


def slide_6():
    image, draw = base(6, "Geometría de las fibras · carrusel 6/8")
    title(draw, "No es una colisión aislada")
    rounded(draw, (72, 285, 935, 455), DEEP, radius=28)
    draw_text(draw, (505, 335), "D(a,b,c)x³ + (4−3bc)x − 2c = 0",
              29, WHITE, MONO, anchor="ma")
    draw_text(draw, (505, 397), "La cúbica controla la fibra genérica",
              20, "#CFE3EA", SANS_BOLD, anchor="ma")
    cards = [
        ((72, 520, 490, 715), "Grado genérico", "3", TEAL),
        ((517, 520, 935, 715), "Cierre normal", "S₃", GOLD),
        ((72, 750, 490, 978), "No propiedad", "S = {D=0}", DEEP),
        ((517, 750, 935, 978), "Sección transversal", "X² + Y³ = 0", TEAL),
    ]
    for box, heading, value, accent in cards:
        rounded(draw, box, WHITE, "#D4DCE0", 25, 2)
        draw_text(draw, (box[0]+30, box[1]+30), heading, 21, MUTED, SANS_BOLD)
        draw_text(draw, ((box[0]+box[2])/2, box[1]+108), value, 37,
                  accent, SERIF_BOLD, anchor="mm")
    draw_text(draw, (72, 1040),
              "Fuera de S: 3 puntos · sobre S menos Γ: 1 punto · sobre Γ: 0 puntos",
              21, DEEP, SANS_BOLD, max_width=850, spacing=1.2, align="center")
    save(image, "06-geometria-fibras.png")


def slide_7():
    image, draw = base(7, "Reducción constructiva · carrusel 7/8")
    title(draw, "De 3 a 79 dimensiones",
          "Una cadena exacta de Bass–Connell–Wright/Yagzhev")
    stages = [
        (180, "3", "mapa fuente", "grado 7"),
        (505, "39", "mapa intermedio", "grado ≤ 3"),
        (830, "79", "forma final", "I + cúbica homogénea"),
    ]
    for x, dimension, heading, detail in stages:
        circle(draw, (x, 545), 92, SOFT_BLUE, DEEP, 5)
        draw_text(draw, (x, 528), dimension, 42, DEEP, SERIF_BOLD, anchor="mm")
        draw_text(draw, (x, 585), "dim.", 17, MUTED, SANS_BOLD, anchor="mm")
        draw_text(draw, (x, 680), heading, 21, DEEP, SANS_BOLD,
                  anchor="ma")
        draw_text(draw, (x, 722), detail, 18, MUTED, SANS, anchor="ma")
    arrow(draw, (282, 545), (392, 545), TEAL, 5, 16)
    arrow(draw, (607, 545), (717, 545), GOLD, 5, 16)
    pill(draw, (315, 445, 580, 495), "18 PASOS EXACTOS", TEAL, WHITE, 16)
    pill(draw, (636, 445, 910, 495), "HOMOGENEIZACIÓN", GOLD, INK, 16)
    rounded(draw, (72, 830, 935, 1090), WHITE, "#D4DCE0", 28, 2)
    draw_text(draw, (104, 870), "Certificado final", 24, DEEP, SANS_BOLD)
    draw_text(draw, (104, 925),
              "det J = 1 · parte no lineal homogénea de grado 3 · tres colisiones racionales preservadas",
              23, INK, SANS, max_width=790, spacing=1.28)
    pill(draw, (104, 1015, 630, 1065), "39 lineales · 47 cuadráticos · 38 cúbicos",
         SOFT_GOLD, GOLD, 17)
    save(image, "07-reduccion-79.png")


def slide_8():
    image, draw = base(8, "Reproducibilidad · carrusel 8/8")
    title(draw, "No tienes que creerlo. Puedes comprobarlo.")
    items = [
        ("01", "Generador exacto", "SymPy y aritmética racional"),
        ("02", "Certificado JSON v2", "polinomios dispersos canónicos"),
        ("03", "Verificador independiente", "solo biblioteca estándar"),
        ("04", "Manifiesto SHA-256", "integridad de toda la release"),
    ]
    y = 315
    for index, heading, body in items:
        rounded(draw, (72, y, 935, y+145), WHITE, "#D4DCE0", 23, 2)
        circle(draw, (132, y+72), 35, DEEP)
        draw_text(draw, (132, y+72), index, 17, WHITE, SANS_BOLD, anchor="mm")
        draw_text(draw, (194, y+31), heading, 23, DEEP, SANS_BOLD)
        draw_text(draw, (194, y+78), body, 20, MUTED, SANS)
        y += 166
    rounded(draw, (72, 1015, 935, 1155), SOFT_GOLD, GOLD, 25, 2)
    draw_text(draw, (104, 1044), "Lee · ejecuta · revisa", 25,
              GOLD, SANS_BOLD)
    draw_text(draw, (104, 1090),
              "DOI reservado 10.5281/zenodo.21460623 · pendiente de publicación",
              18, INK, SANS, max_width=785)
    pill(draw, (610, 1175, 935, 1228), "EXACTO ≠ REVISADO POR PARES",
         RED, WHITE, 14)
    save(image, "08-como-comprobarlo.png")


def main():
    OUT.mkdir(exist_ok=True)
    for path in OUT.glob("*.png"):
        path.unlink()
    slide_1()
    slide_2()
    slide_3()
    slide_4()
    slide_5()
    slide_6()
    slide_7()
    slide_8()
    print(f"Rendered 8 carousel slides in {OUT}/")


if __name__ == "__main__":
    main()