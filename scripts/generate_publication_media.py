#!/usr/bin/env python3
"""Generate deterministic publication media for the Jacobian preprint."""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CAROUSEL = ROOT / "carousel-v2"
SOCIAL = ROOT / "social"
for directory in (ASSETS, CAROUSEL, SOCIAL):
    directory.mkdir(parents=True, exist_ok=True)

C = {
    "ink": "#08111f", "paper": "#f5f0e6", "gold": "#c9912b",
    "blue": "#2f69a2", "teal": "#1a6b6b", "muted": "#d6dbe2",
    "soft": "#aab2bd", "panel": "#101d2d", "line": "#5b6470",
}

FONT_CANDIDATES = [
    Path("/usr/share/fonts/truetype/dejavu"),
    Path("/usr/local/texlive/2025/texmf-dist/fonts/truetype/public/dejavu"),
]
FONT_ROOT = next((p for p in FONT_CANDIDATES if p.exists()), FONT_CANDIDATES[0])
FONTS = {
    "serif": FONT_ROOT / "DejaVuSerif.ttf",
    "serif_bold": FONT_ROOT / "DejaVuSerif-Bold.ttf",
    "sans": FONT_ROOT / "DejaVuSans.ttf",
    "sans_bold": FONT_ROOT / "DejaVuSans-Bold.ttf",
}

def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS[kind]), size)

def wrap(draw: ImageDraw.ImageDraw, text: str, face, width: int) -> str:
    output: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            output.append("")
            continue
        current = ""
        for word in paragraph.split():
            candidate = f"{current} {word}".strip()
            if draw.textbbox((0, 0), candidate, font=face)[2] <= width:
                current = candidate
            else:
                if current:
                    output.append(current)
                current = word
        if current:
            output.append(current)
    return "\n".join(output)

def convergence(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], dark: bool = True) -> None:
    x0, y0, x1, y1 = box
    width, height = x1 - x0, y1 - y0
    points = [
        (x0 + width * .12, y0 + height * .12, C["blue"], "p₁"),
        (x0 + width * .50, y0 + height * .06, C["paper"] if dark else C["ink"], "p₂"),
        (x0 + width * .88, y0 + height * .12, C["gold"], "p₃"),
    ]
    target = (x0 + width * .50, y0 + height * .82)
    for x, y, color, label in points:
        draw.line((x, y, *target), fill=color, width=max(3, width // 280))
        radius = max(12, width // 55)
        draw.ellipse((x-radius, y-radius, x+radius, y+radius),
                     fill=C["ink"] if dark else C["paper"], outline=color, width=4)
        draw.text((x, y), label, font=font("serif", max(18, width // 45)),
                  fill=C["paper"] if dark else C["ink"], anchor="mm")
    radius = max(18, width // 38)
    draw.ellipse((target[0]-radius, target[1]-radius, target[0]+radius, target[1]+radius),
                 fill=C["gold"])
    draw.text(target, "F(p)", font=font("sans_bold", max(14, width // 60)),
              fill=C["ink"], anchor="mm")

def cover(path: Path, size: tuple[int, int], paper: bool = False) -> None:
    width, height = size
    background = C["paper"] if paper else C["ink"]
    foreground = C["ink"] if paper else C["paper"]
    image = Image.new("RGB", size, background)
    draw = ImageDraw.Draw(image)
    margin = int(width * .055)
    draw.text((margin, margin), "JACOBIAN CONJECTURE · EXPLICIT COUNTEREXAMPLE · PREPRINT",
              font=font("sans_bold", max(14, int(width*.012))),
              fill=C["blue"] if paper else C["gold"])
    draw.multiline_text((margin, margin+int(height*.10)),
                        "Now We Know That\n“Always” Was Too Optimistic",
                        font=font("serif_bold", max(38, int(width*.046))),
                        fill=foreground, spacing=8)
    subtitle = "Algebraic and geometric anatomy of an explicit polynomial map in dimension three."
    face = font("sans", max(16, int(width*.017)))
    draw.multiline_text((margin, margin+int(height*.31)), wrap(draw, subtitle, face, int(width*.68)),
                        font=face, fill=C["soft"] if paper else C["muted"], spacing=8)
    convergence(draw, (margin, int(height*.45), width-margin, int(height*.78)), not paper)
    labels = ["det JF = −2", "3 rational points · 1 image", "exact certificate"]
    x, y = margin, int(height*.82)
    face = font("sans_bold", max(13, int(width*.012)))
    for label in labels:
        tw = draw.textbbox((0, 0), label, font=face)[2]
        draw.rounded_rectangle((x, y, x+tw+28, y+36), radius=18, outline=C["gold"], width=2)
        draw.text((x+14, y+18), label, font=face, fill=foreground, anchor="lm")
        x += tw + 42
    draw.line((margin, height-margin*.75, width-margin, height-margin*.75),
              fill=C["line"], width=1)
    footer = font("sans_bold", max(11, int(width*.009)))
    draw.text((margin, height-margin*.52), "Javier Aragón · v1.0 · 20 July 2026",
              font=footer, fill=foreground)
    draw.text((width-margin, height-margin*.52), "PREPRINT · NOT PEER REVIEWED",
              font=footer, fill=C["blue"] if paper else C["gold"], anchor="ra")
    image.save(path, optimize=True)

def slide(index: int, title: str, kicker: str, body: str, kind: str, name: str) -> Path:
    width, height, margin = 1080, 1350, 72
    image = Image.new("RGB", (width, height), C["ink"])
    draw = ImageDraw.Draw(image)
    draw.text((margin, 55), f"{index}/10", font=font("sans_bold", 20), fill=C["gold"])
    draw.text((width-margin, 55), kicker, font=font("sans_bold", 18),
              fill=C["paper"], anchor="ra")
    wrapped = wrap(draw, title, font("serif_bold", 56), width-2*margin)
    draw.multiline_text((margin, 130), wrapped, font=font("serif_bold", 56),
                        fill=C["paper"], spacing=8)
    y = 130 + len(wrapped.splitlines()) * 68 + 35
    if kind == "abstract":
        convergence(draw, (margin, y, width-margin, y+310), True)
        y += 350
    elif kind == "split":
        box_width = (width-2*margin-24)//2
        for position, (heading, copy, color) in enumerate([
            ("LOCAL", "det JF = −2 everywhere.\nNo differential collapse.", C["blue"]),
            ("GLOBAL", "Three distinct points share one image.\nNot one-to-one.", C["gold"]),
        ]):
            x = margin + position*(box_width+24)
            draw.rounded_rectangle((x, y, x+box_width, y+350), radius=16,
                                   fill=C["panel"], outline=color, width=3)
            draw.text((x+24, y+26), heading, font=font("serif_bold", 38), fill=C["paper"])
            draw.multiline_text((x+24, y+100), copy, font=font("sans", 23),
                                fill=C["paper"], spacing=12)
        y += 390
    elif kind == "flow":
        draw.text((width/2, y+60), "3   →   39   →   79",
                  font=font("serif_bold", 70), fill=C["paper"], anchor="ma")
        draw.text((width/2, y+160), "source map · degree-reduced · homogeneous cubic",
                  font=font("sans", 22), fill=C["soft"], anchor="ma")
        y += 240
    elif kind == "diagram":
        for offset, color in enumerate((C["blue"], C["gold"], C["teal"])):
            cx = margin + 160 + offset*300
            draw.ellipse((cx-70, y+20, cx+70, y+160), outline=color,
                         width=4, fill=C["panel"])
            draw.text((cx, y+90), f"sheet {offset+1}", font=font("sans_bold", 20),
                      fill=C["paper"], anchor="mm")
        y += 230
    elif kind == "chain":
        for offset, label in enumerate(["Escape", "Limit", "Surface S", "Cusp Γ"]):
            x = margin + offset*235
            draw.rounded_rectangle((x, y, x+190, y+120), radius=14,
                                   fill=C["panel"], outline=C["gold"], width=2)
            draw.text((x+95, y+60), label, font=font("serif_bold", 26),
                      fill=C["paper"], anchor="mm")
            if offset < 3:
                draw.text((x+212, y+60), "→", font=font("serif_bold", 30),
                          fill=C["gold"], anchor="mm")
        y += 170
    draw.multiline_text((margin, y), body, font=font("sans", 25),
                        fill=C["paper"], spacing=14)
    draw.line((margin, height-95, width-margin, height-95), fill=C["line"], width=1)
    draw.text((margin, height-70),
              "github.com/javieraragonmartinez/forever-was-too-optimistic",
              font=font("sans", 14), fill=C["soft"])
    output = CAROUSEL / f"{index:02d}-{name}.png"
    image.save(output, optimize=True)
    return output

def social_card(path: Path, title: tuple[str, str], kicker: str, mode: str) -> None:
    image = Image.new("RGB", (1080, 1350), C["ink"])
    draw = ImageDraw.Draw(image)
    draw.text((72, 86), kicker, font=font("sans_bold", 20), fill=C["gold"])
    draw.text((72, 210), title[0], font=font("serif_bold", 62), fill=C["paper"])
    draw.text((72, 286), title[1], font=font("serif_bold", 62), fill=C["paper"])
    if mode == "announcement":
        convergence(draw, (72, 430, 1008, 800), True)
        draw.text((72, 900), "det JF = −2", font=font("serif_bold", 48), fill=C["paper"])
        draw.text((72, 956), "Tres puntos racionales distintos.", font=font("sans", 27), fill=C["muted"])
        draw.text((72, 996), "Una imagen común.", font=font("sans", 27), fill=C["muted"])
    elif mode == "collision":
        lines = ["p₁ = (0, 0, −1/4)", "p₂ = (1, −3/2, 13/2)", "p₃ = (−1, 3/2, 13/2)"]
        for offset, line in enumerate(lines):
            draw.text((98, 430+offset*80), line, font=font("serif", 32), fill=C["paper"])
        convergence(draw, (72, 650, 1008, 940), True)
        draw.text((72, 1030), "F(p₁) = F(p₂) = F(p₃) = (−1/4, 0, 0)",
                  font=font("serif_bold", 30), fill=C["paper"])
    elif mode == "split":
        for position, (heading, formula, copy, color) in enumerate([
            ("LOCAL", "det JF = −2", "No differential collapse.", C["blue"]),
            ("GLOBAL", "p₁, p₂, p₃", "One common image.", C["gold"]),
        ]):
            x = 72 + position*496
            draw.rounded_rectangle((x, 390, x+440, 890), radius=20,
                                   fill=C["panel"], outline=color, width=3)
            draw.text((x+40, 470), heading, font=font("serif_bold", 42), fill=C["paper"])
            draw.text((x+40, 555), formula, font=font("serif_bold", 38), fill=C["gold"])
            draw.text((x+40, 640), copy, font=font("sans", 27), fill=C["muted"])
        draw.text((72, 1015), "El fallo descrito es global, no singular.",
                  font=font("serif_bold", 38), fill=C["paper"])
    else:
        items = [
            "Generación determinista del certificado",
            "Regeneración idéntica byte a byte",
            "Verificador independiente",
            "JSON Schema 2020-12 y tests",
            "Manifiesto de integridad SHA-256",
        ]
        for offset, item in enumerate(items):
            y = 430 + offset*110
            draw.ellipse((78, y-18, 114, y+18), fill=C["gold"])
            draw.text((96, y), "✓", font=font("sans_bold", 22), fill=C["ink"], anchor="mm")
            draw.text((138, y), item, font=font("sans", 28), fill=C["paper"], anchor="lm")
    draw.line((72, 1215, 1008, 1215), fill=C["line"], width=1)
    draw.text((72, 1260), "Javier Aragón · v1.0", font=font("sans", 18),
              fill=C["soft"], anchor="lm")
    draw.text((1008, 1260), "PREPRINT · NO REVISADO POR PARES",
              font=font("sans_bold", 18), fill=C["gold"], anchor="rm")
    image.save(path, optimize=True)

def contact_sheet(paths: list[Path], output: Path, columns: int, thumb: tuple[int, int]) -> None:
    loaded = []
    for path in paths:
        image = Image.open(path).convert("RGB")
        image.thumbnail(thumb)
        loaded.append(image.copy())
    rows = (len(loaded)+columns-1)//columns
    sheet = Image.new("RGB", (thumb[0]*columns, thumb[1]*rows), C["paper"])
    for index, image in enumerate(loaded):
        sheet.paste(image, ((index % columns)*thumb[0], (index // columns)*thumb[1]))
    sheet.save(output, optimize=True)

def main() -> None:
    cover(ASSETS / "repository-cover.png", (1600, 900))
    cover(ASSETS / "social-preview.png", (1280, 640))
    cover(ASSETS / "academic-cover.png", (840, 1188), paper=True)
    (ASSETS / "visual-abstract.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 500">'
        f'<rect width="1200" height="500" fill="{C["paper"]}"/>'
        f'<path d="M150 100C350 130 460 320 600 400M600 70V400M1050 100C850 130 740 320 600 400" fill="none" stroke="{C["gold"]}" stroke-width="6"/>'
        f'<circle cx="600" cy="400" r="46" fill="{C["gold"]}"/>'
        f'<text x="600" y="412" text-anchor="middle" font-family="Arial" font-size="28" fill="{C["ink"]}">F(p)</text>'
        '</svg>', encoding="utf-8"
    )

    specifications = [
        ("Now We Know That “Always” Was Too Optimistic", "EXPLICIT COUNTEREXAMPLE",
         "Algebraic and geometric anatomy of an explicit polynomial map in dimension three.", "abstract", "portada"),
        ("Three rational points. One image.", "THE DECISIVE COLLISION",
         "p₁ = (0, 0, −1/4)\np₂ = (1, −3/2, 13/2)\np₃ = (−1, 3/2, 13/2)\n\nF(p₁) = F(p₂) = F(p₃) = (−1/4, 0, 0)", "abstract", "colision"),
        ("Local invertibility is not global injectivity.", "THE LOGICAL GAP",
         "LOCAL\n det JF = −2 everywhere.\n No differential collapse.\n\nGLOBAL\n Three distinct points share one image.\n The map is not one-to-one.", "split", "local-global"),
        ("The explicit polynomial map.", "EXACT SOURCE OBJECT",
         "F₁ = (1+xy)³z + y²(1+xy)(4+3xy)\n\nF₂ = y + 3x(1+xy)²z + 3xy²(4+3xy)\n\nF₃ = 2x − 3x²y − x³z", "text", "mapa"),
        ("What falls — and what does not.", "SCIENTIFIC SCOPE",
         "FALLS · The universal real Jacobian claim in dimension 3 — therefore for n ≥ 3.\n\nREMAINS OPEN · The two-dimensional case.\n\nREMAINS TRUE · Local invertibility and the inverse function theorem.", "text", "alcance"),
        ("A generic fiber has degree three.", "GEOMETRY OF THE MAP",
         "One output can admit up to three preimages.\n\nThe manuscript studies the discriminant and generic monodromy S₃.", "diagram", "fibras"),
        ("Non-properness and the asymptotic surface.", "GLOBAL GEOMETRY",
         "Inputs escape → images converge → asymptotic surface S → cusp Γ.\n\nThe failure is global, not singular.", "chain", "no-propiedad"),
        ("From dimension 3 to a cubic map in dimension 79.", "BCW–YAGZHEV REDUCTION",
         "18 explicit Jacobian-preserving operations.\nAfter linear normalization, det J = 1.", "flow", "reduccion"),
        ("Every claim should be machine-checkable.", "REPRODUCIBILITY",
         "✓ deterministic certificate generation\n✓ JSON Schema 2020-12 validation\n✓ independent verifier\n✓ byte-for-byte regeneration\n✓ complete SHA-256 manifest", "text", "reproducibilidad"),
        ("The mathematics is exact. The verification is open.", "OPEN REVIEW",
         "Do not trust the claim. Check it.\n\nPREPRINT · NOT PEER REVIEWED · DOI RESERVED", "abstract", "revision"),
    ]
    carousel_paths = [slide(index, *spec) for index, spec in enumerate(specifications, 1)]
    contact_sheet(carousel_paths, CAROUSEL / "contact-sheet.jpg", 5, (270, 338))

    social_specs = [
        (("“Siempre” era", "demasiado optimista"), "PREPRINT INDEPENDIENTE · 20 JUL 2026", "announcement", "01-preprint.png"),
        (("Tres puntos.", "Una imagen."), "EL CERTIFICADO ELEMENTAL", "collision", "02-colision.png"),
        (("Invertibilidad local", "no es inyectividad global"), "LA DISTINCIÓN CENTRAL", "split", "03-local-global.png"),
        (("No confíes en la afirmación.", "Compruébala."), "REPRODUCIBILIDAD", "checks", "04-reproducibilidad.png"),
    ]
    social_paths = []
    for title, kicker, mode, filename in social_specs:
        output = SOCIAL / filename
        social_card(output, title, kicker, mode)
        social_paths.append(output)
    contact_sheet(social_paths, SOCIAL / "contact-sheet.jpg", 2, (324, 405))

if __name__ == "__main__":
    main()
