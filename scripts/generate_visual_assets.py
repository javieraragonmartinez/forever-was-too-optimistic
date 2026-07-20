#!/usr/bin/env python3
"""Generate the academic repository covers and revised ten-slide carousel.

The output is deterministic when run with Pillow 12.2.0 and DejaVu fonts.
It deliberately uses only visual relationships that correspond to the exact
counterexample: three distinct rational points, one common image, and a
constant non-zero Jacobian determinant.
"""

from __future__ import annotations

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CAROUSEL = ROOT / "carousel-v2"
ASSETS.mkdir(exist_ok=True)
CAROUSEL.mkdir(exist_ok=True)

FONT_CANDIDATES = [
    Path("/usr/local/texlive/2025/texmf-dist/fonts/truetype/public/dejavu"),
    Path("/usr/share/fonts/truetype/dejavu"),
]
FONT_ROOT = next((p for p in FONT_CANDIDATES if p.exists()), FONT_CANDIDATES[-1])
FONTS = {
    "serif": FONT_ROOT / "DejaVuSerif.ttf",
    "serif_bold": FONT_ROOT / "DejaVuSerif-Bold.ttf",
    "sans": FONT_ROOT / "DejaVuSans.ttf",
    "sans_bold": FONT_ROOT / "DejaVuSans-Bold.ttf",
}

INK = "#09101C"
PAPER = "#F6F2E8"
GOLD = "#B88430"
BLUE = "#24598F"
TEAL = "#1A6B6B"
MUTED = "#9CA2AA"
LINE = "#D2CBBE"
REPOSITORY_URL = "github.com/javieraragonmartinez/forever-was-too-optimistic"


def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS[kind]), size)


def wrap(draw: ImageDraw.ImageDraw, text: str, text_font, max_width: int) -> str:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for word in paragraph.split():
            candidate = f"{current} {word}".strip()
            if draw.textbbox((0, 0), candidate, font=text_font)[2] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return "\n".join(lines)


def rounded(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def abstract(draw: ImageDraw.ImageDraw, box, dark: bool = True) -> None:
    x0, y0, x1, y1 = box
    width, height = x1 - x0, y1 - y0
    points = [
        (x0 + width * 0.12, y0 + height * 0.12, BLUE, "p₁"),
        (x0 + width * 0.50, y0 + height * 0.06, PAPER if dark else INK, "p₂"),
        (x0 + width * 0.88, y0 + height * 0.12, GOLD, "p₃"),
    ]
    target_x, target_y = x0 + width * 0.50, y0 + height * 0.82
    for x, y, colour, label in points:
        draw.line((x, y, target_x, target_y), fill=colour, width=max(3, int(width / 280)))
        radius = max(12, int(width / 55))
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=INK if dark else PAPER,
            outline=colour,
            width=4,
        )
        draw.text(
            (x, y), label, font=font("serif", max(18, int(width / 45))),
            fill=PAPER if dark else INK, anchor="mm",
        )
    radius = max(18, int(width / 38))
    draw.ellipse(
        (target_x - radius, target_y - radius, target_x + radius, target_y + radius),
        fill=GOLD,
    )
    draw.text(
        (target_x, target_y), "F(p)", font=font("sans_bold", max(14, int(width / 60))),
        fill=INK, anchor="mm",
    )


def make_cover(path: Path, size: tuple[int, int], paper: bool = False) -> None:
    width, height = size
    background = PAPER if paper else INK
    foreground = INK if paper else PAPER
    image = Image.new("RGB", size, background)
    draw = ImageDraw.Draw(image)
    margin = int(width * 0.055)
    draw.text(
        (margin, margin),
        "JACOBIAN CONJECTURE · EXPLICIT COUNTEREXAMPLE · PREPRINT",
        font=font("sans_bold", max(14, int(width * 0.012))),
        fill=BLUE if paper else GOLD,
    )
    draw.multiline_text(
        (margin, margin + int(height * 0.10)),
        "Now We Know That\n“Always” Was Too Optimistic",
        font=font("serif_bold", max(38, int(width * 0.046))),
        fill=foreground,
        spacing=8,
    )
    subtitle = "Algebraic and geometric anatomy of an explicit polynomial map in dimension three."
    body_font = font("sans", max(16, int(width * 0.017)))
    draw.multiline_text(
        (margin, margin + int(height * 0.31)),
        wrap(draw, subtitle, body_font, int(width * 0.66)),
        font=body_font,
        fill=MUTED if paper else "#D8D8D3",
        spacing=8,
    )
    abstract(draw, (margin, int(height * 0.45), width - margin, int(height * 0.78)), not paper)
    x, y = margin, int(height * 0.82)
    pill_font = font("sans_bold", max(13, int(width * 0.012)))
    for text in ["det JF = −2", "3 rational points · 1 image", "exact certificate"]:
        text_width = draw.textbbox((0, 0), text, font=pill_font)[2]
        rounded(draw, (x, y, x + text_width + 28, y + 36), 18, outline=GOLD, width=2)
        draw.text((x + 14, y + 18), text, font=pill_font, fill=foreground, anchor="lm")
        x += text_width + 42
    draw.line((margin, height - margin * 0.75, width - margin, height - margin * 0.75), fill=LINE if paper else "#59616B")
    footer_font = font("sans_bold", max(11, int(width * 0.009)))
    draw.text((margin, height - margin * 0.52), "Javier Aragón · v1.0 · 20 July 2026", font=footer_font, fill=foreground)
    draw.text((width - margin, height - margin * 0.52), "PREPRINT · NOT PEER REVIEWED", font=footer_font, fill=BLUE if paper else GOLD, anchor="ra")
    image.save(path, optimize=False)


def make_visual_abstract() -> None:
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 500" role="img" aria-labelledby="title description">
<title id="title">Three distinct rational points map to one image</title>
<desc id="description">Visual abstract for the explicit Jacobian counterexample.</desc>
<rect width="1200" height="500" fill="{PAPER}"/>
<g fill="none" stroke-width="6">
<path d="M150 100 C350 130 460 320 600 400" stroke="{BLUE}"/>
<path d="M600 70 C600 180 600 290 600 400" stroke="{INK}"/>
<path d="M1050 100 C850 130 740 320 600 400" stroke="{GOLD}"/>
</g>
<g font-family="Georgia,serif" font-size="34" text-anchor="middle">
<circle cx="150" cy="100" r="32" fill="{PAPER}" stroke="{BLUE}" stroke-width="6"/><text x="150" y="112" fill="{INK}">p₁</text>
<circle cx="600" cy="70" r="32" fill="{PAPER}" stroke="{INK}" stroke-width="6"/><text x="600" y="82" fill="{INK}">p₂</text>
<circle cx="1050" cy="100" r="32" fill="{PAPER}" stroke="{GOLD}" stroke-width="6"/><text x="1050" y="112" fill="{INK}">p₃</text>
<circle cx="600" cy="400" r="46" fill="{GOLD}"/><text x="600" y="412" fill="{INK}">F(p)</text>
</g>
<text x="600" y="475" fill="{INK}" font-family="Arial,sans-serif" font-size="26" text-anchor="middle">det JF = −2 · three distinct rational points · one image</text>
</svg>'''
    (ASSETS / "visual-abstract.svg").write_text(svg, encoding="utf-8")


SLIDES = [
    ("Now We Know That “Always” Was Too Optimistic", "EXPLICIT COUNTEREXAMPLE", "Algebraic and geometric anatomy of an explicit polynomial map in dimension three.", "abstract"),
    ("Three rational points. One image.", "THE DECISIVE COLLISION", "p₁ = (0, 0, −1/4)\np₂ = (1, −3/2, 13/2)\np₃ = (−1, 3/2, 13/2)\n\nF(p₁) = F(p₂) = F(p₃) = (−1/4, 0, 0)", "abstract"),
    ("Local invertibility is not global injectivity.", "THE LOGICAL GAP", "LOCAL\n det JF = −2 everywhere.\n No differential collapse.\n\nGLOBAL\n Three distinct points share one image.\n The map is not one-to-one.", "split"),
    ("The explicit polynomial map.", "EXACT SOURCE OBJECT", "F₁ = (1+xy)³z + y²(1+xy)(4+3xy)\n\nF₂ = y + 3x(1+xy)²z + 3xy²(4+3xy)\n\nF₃ = 2x − 3x²y − x³z", "text"),
    ("What falls — and what does not.", "SCIENTIFIC SCOPE", "FALLS · The universal real Jacobian claim in dimension 3 — therefore for n ≥ 3.\n\nREMAINS OPEN · The two-dimensional case.\n\nREMAINS TRUE · Local invertibility and the inverse function theorem.\n\nREQUIRES CARE · Broader consequences depend on precise hypotheses.", "text"),
    ("A generic fiber has degree three.", "GEOMETRY OF THE MAP", "One output can admit up to three preimages.\n\nThe cubic fiber equation matches the explicit triple collision.\n\nThe manuscript separately studies the discriminant and generic monodromy S₃.", "diagram"),
    ("Non-properness and the asymptotic surface.", "GLOBAL GEOMETRY", "Inputs escape → images converge → asymptotic surface S → cusp Γ.\n\nThe failure is global, not singular: local invertibility survives.", "chain"),
    ("From dimension 3 to a cubic map in dimension 79.", "BCW–YAGZHEV REDUCTION", "3  →  39  →  79\nsource map · degree-reduced · homogeneous cubic\n\n18 explicit Jacobian-preserving operations.\nAfter linear normalization, det J = 1.", "flow"),
    ("Every claim should be machine-checkable.", "REPRODUCIBILITY", "✓ deterministic certificate generation\n✓ JSON Schema 2020-12 validation\n✓ independent verifier without SymPy\n✓ byte-for-byte regeneration\n✓ complete SHA-256 manifest", "text"),
    ("The mathematics is exact. The verification is open.", "OPEN REVIEW", "The repository publishes the preprint, source, exact certificate, independent verifier, tests, licenses, attribution and integrity manifest.\n\nDo not trust the claim. Check it.\n\nPREPRINT · NOT PEER REVIEWED · DOI RESERVED", "abstract"),
]
NAMES = ["portada", "colision", "local-global", "mapa", "alcance", "fibras", "no-propiedad", "reduccion", "reproducibilidad", "revision"]


def make_slide(index: int, title: str, kicker: str, body: str, kind: str) -> Path:
    width, height, margin = 1080, 1350, 72
    image = Image.new("RGB", (width, height), INK)
    draw = ImageDraw.Draw(image)
    draw.text((margin, 55), f"{index}/10", font=font("sans_bold", 20), fill=GOLD)
    draw.text((width - margin, 55), kicker, font=font("sans_bold", 18), fill=PAPER, anchor="ra")
    title_text = wrap(draw, title, font("serif_bold", 56), width - 2 * margin)
    draw.multiline_text((margin, 130), title_text, font=font("serif_bold", 56), fill=PAPER, spacing=8)
    y = 130 + len(title_text.splitlines()) * 68 + 35
    if kind == "abstract":
        abstract(draw, (margin, y, width - margin, y + 310), True)
        y += 350
    elif kind == "split":
        box_width = (width - 2 * margin - 24) // 2
        for position, (heading, text, colour) in enumerate([
            ("LOCAL", "det JF = −2 everywhere.\nNo differential collapse.", BLUE),
            ("GLOBAL", "Three distinct points share one image.\nNot one-to-one.", GOLD),
        ]):
            x = margin + position * (box_width + 24)
            rounded(draw, (x, y, x + box_width, y + 350), 16, fill="#101B2A", outline=colour, width=3)
            draw.text((x + 24, y + 26), heading, font=font("serif_bold", 38), fill=PAPER)
            draw.multiline_text((x + 24, y + 100), text, font=font("sans", 23), fill=PAPER, spacing=12)
        y += 390
    elif kind == "diagram":
        for position, colour in enumerate((BLUE, GOLD, TEAL)):
            center_x = margin + 160 + position * 300
            draw.ellipse((center_x - 70, y + 20, center_x + 70, y + 160), outline=colour, width=4, fill="#101B2A")
            draw.text((center_x, y + 90), f"sheet {position + 1}", font=font("sans_bold", 20), fill=PAPER, anchor="mm")
        y += 230
    elif kind == "chain":
        for position, label in enumerate(["Escape", "Limit", "Surface S", "Cusp Γ"]):
            x = margin + position * 235
            rounded(draw, (x, y, x + 190, y + 120), 14, fill="#101B2A", outline=GOLD, width=2)
            draw.text((x + 95, y + 60), label, font=font("serif_bold", 26), fill=PAPER, anchor="mm")
            if position < 3:
                draw.text((x + 212, y + 60), "→", font=font("serif_bold", 30), fill=GOLD, anchor="mm")
        y += 170
    elif kind == "flow":
        draw.text((width / 2, y + 60), "3   →   39   →   79", font=font("serif_bold", 70), fill=PAPER, anchor="ma")
        draw.text((width / 2, y + 160), "source map · degree-reduced · homogeneous cubic", font=font("sans", 22), fill=MUTED, anchor="ma")
        y += 240
    draw.multiline_text((margin, y), body, font=font("sans", 25), fill=PAPER, spacing=14)
    draw.line((margin, height - 95, width - margin, height - 95), fill="#566171")
    draw.text((margin, height - 70), REPOSITORY_URL, font=font("sans", 14), fill=MUTED)
    path = CAROUSEL / f"{index:02d}-{NAMES[index - 1]}.png"
    image.save(path, optimize=False)
    return path


def make_contact_sheet(paths: list[Path]) -> None:
    sheet = Image.new("RGB", (1350, 676), "white")
    for index, path in enumerate(paths):
        image = Image.open(path)
        image.thumbnail((270, 338))
        sheet.paste(image, ((index % 5) * 270, (index // 5) * 338))
    sheet.save(CAROUSEL / "contact-sheet.jpg", quality=92, optimize=False)


def main() -> None:
    make_cover(ASSETS / "repository-cover.png", (1600, 900))
    make_cover(ASSETS / "social-preview.png", (1280, 640))
    make_cover(ASSETS / "academic-cover.png", (840, 1188), paper=True)
    make_visual_abstract()
    slide_paths = [make_slide(index, *slide) for index, slide in enumerate(SLIDES, 1)]
    make_contact_sheet(slide_paths)
    print("Academic visual assets generated: PASS")


if __name__ == "__main__":
    main()
