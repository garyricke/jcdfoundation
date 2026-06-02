#!/usr/bin/env python3
"""Build print-ready bleed+crop-marks versions of the card sheets.

Page: 4.0 x 2.5 in.  Trim 3.5 x 2 (centered, 0.25in margin).  Bleed 0.125in.
Each card face is wrapped in a .bleed-sheet: a 3.75x2.25 colored bleed-fill
behind the 3.5x2 card (positioned at trim), an optional gold strip so the
left gold bar bleeds, and an SVG of 8 crop marks sitting in the outer margin.
"""
import re, pathlib

SRC = pathlib.Path(__file__).parent

# source -> output
FILES = {
    "card-bob.html": "card-bob-bleed.html",
    "card-jack.html": "card-jack-bleed.html",
    "card-jen.html": "card-jen-bleed.html",
    "card-generic.html": "card-generic-bleed.html",
    "pocket-card.html": "pocket-card-bleed.html",
}

BLEED_CSS = """
    /* ===== PRINT BLEED + CROP MARKS ===== */
    .bleed-sheet { position: relative; width: 4in; height: 2.5in; background: #FFFFFF; overflow: hidden; }
    .bleed-fill { position: absolute; left: 0.125in; top: 0.125in; width: 3.75in; height: 2.25in; }
    .bleed-sheet.bg-white .bleed-fill { background: #FFFFFF; }
    .bleed-sheet.bg-navy .bleed-fill { background: #0E2A58; }
    .bleed-sheet.bg-charcoal .bleed-fill { background: #111827; }
    .bleed-sheet .gold-bleed { position: absolute; left: 0.125in; top: 0.125in; width: 0.225in; height: 2.25in; background: #C5963A; }
    .bleed-sheet > .card { position: absolute; left: 0.25in; top: 0.25in; margin: 0; box-shadow: none; }
    .crop { position: absolute; left: 0; top: 0; width: 4in; height: 2.5in; pointer-events: none; }
    @media screen { .bleed-sheet { outline: 1px dashed rgba(197,150,58,0.4); outline-offset: 8px; margin: 0 auto; }
                    .bleed-sheet > .card { outline: none !important; } }
    @media print { .bleed-sheet { page-break-after: always; outline: none; }
                   .bleed-sheet:last-of-type { page-break-after: auto; }
                   .bleed-sheet > .card { outline: none !important; } }
"""

CROP_SVG = ('<svg class="crop" viewBox="0 0 4 2.5" xmlns="http://www.w3.org/2000/svg">'
            '<g stroke="#000000" stroke-width="0.006" fill="none">'
            '<line x1="0.25" y1="0" x2="0.25" y2="0.125"/><line x1="0" y1="0.25" x2="0.125" y2="0.25"/>'
            '<line x1="3.75" y1="0" x2="3.75" y2="0.125"/><line x1="3.875" y1="0.25" x2="4" y2="0.25"/>'
            '<line x1="0.25" y1="2.375" x2="0.25" y2="2.5"/><line x1="0" y1="2.25" x2="0.125" y2="2.25"/>'
            '<line x1="3.75" y1="2.375" x2="3.75" y2="2.5"/><line x1="3.875" y1="2.25" x2="4" y2="2.25"/>'
            '</g></svg>')

def face_style(cls):
    if "bob-front" in cls:  return ("bg-white", True)   # personal front (left gold bar)
    if "bob-back" in cls:   return ("bg-navy", False)   # personal back (full navy)
    if "gen-front" in cls:  return ("bg-white", False)  # generic front (white, no bar)
    if "gen-back" in cls:   return ("bg-navy", False)   # generic back (full navy)
    if cls.strip() == "card back": return ("bg-white", True)   # pocket back (left gold bar)
    if cls.strip() == "card":      return ("bg-charcoal", False) # pocket front (charcoal)
    return ("bg-white", False)

TAG = re.compile(r"<div\b[^>]*>|</div>")
FACE_OPEN = re.compile(r'<div class="(card(?:"| )[^"]*)"')

def match_close(html, open_start):
    """Return index just past the </div> that closes the div opened at open_start."""
    depth = 0
    for m in TAG.finditer(html, open_start):
        depth += 1 if m.group().startswith("<div") else -1
        if depth == 0:
            return m.end()
    raise RuntimeError("unbalanced divs")

def wrap(html):
    out, i = [], 0
    for m in FACE_OPEN.finditer(html):
        start = m.start()
        cls = m.group(1)
        end = match_close(html, start)
        bg, gold = face_style(cls)
        gold_div = '<div class="gold-bleed"></div>' if gold else ""
        out.append(html[i:start])
        out.append(f'<div class="bleed-sheet {bg}"><div class="bleed-fill"></div>{gold_div}')
        out.append(html[start:end])
        out.append(CROP_SVG + "</div>")
        i = end
    out.append(html[i:])
    return "".join(out)

for src, dst in FILES.items():
    html = (SRC / src).read_text()
    html = html.replace("@page { size: 3.5in 2in; margin: 0; }",
                        "@page { size: 4in 2.5in; margin: 0; }")
    html = html.replace("</style>", BLEED_CSS + "  </style>", 1)
    html = wrap(html)
    (SRC / dst).write_text(html)
    n = html.count('class="bleed-sheet')
    print(f"{src:20s} -> {dst:26s} ({n} faces wrapped)")
