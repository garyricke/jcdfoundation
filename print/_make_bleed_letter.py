#!/usr/bin/env python3
"""Bleed+crop version of the letterhead (8.5x11 with a full-bleed navy header).

Page 9x11.5.  Trim 8.5x11 centered (0.25in margin).  The whole sheet is
scaled just enough (8.75/8.5 x, 11.25/11 y) so its edge artwork — the navy
header — reaches the 0.125in bleed, then 8 crop marks sit in the outer margin.
"""
import re, sys, pathlib
SRC = pathlib.Path(__file__).parent
TAG = re.compile(r"<div\b[^>]*>|</div>")

# Same bleed treatment works for any letter-format sheet (letterhead, outreach
# letter, …). Pass a stem to pick the source: `_make_bleed_letter.py outreach-letter`
STEM = sys.argv[1] if len(sys.argv) > 1 else "letterhead"

def match_close(html, start):
    depth = 0
    for m in TAG.finditer(html, start):
        depth += 1 if m.group().startswith("<div") else -1
        if depth == 0:
            return m.end()
    raise RuntimeError("unbalanced divs")

CROP = ('<svg class="crop" viewBox="0 0 9 11.5" xmlns="http://www.w3.org/2000/svg">'
        '<g stroke="#000000" stroke-width="0.01" fill="none">'
        '<line x1="0.25" y1="0" x2="0.25" y2="0.125"/><line x1="0" y1="0.25" x2="0.125" y2="0.25"/>'
        '<line x1="8.75" y1="0" x2="8.75" y2="0.125"/><line x1="8.875" y1="0.25" x2="9" y2="0.25"/>'
        '<line x1="0.25" y1="11.375" x2="0.25" y2="11.5"/><line x1="0" y1="11.25" x2="0.125" y2="11.25"/>'
        '<line x1="8.75" y1="11.375" x2="8.75" y2="11.5"/><line x1="8.875" y1="11.25" x2="9" y2="11.25"/>'
        '</g></svg>')

BLEED_CSS = """
    /* ===== PRINT BLEED + CROP MARKS (letterhead) ===== */
    .bleed-page { position: relative; width: 9in; height: 11.5in; background: #FFFFFF; overflow: hidden; margin: 0 auto; }
    .bleed-page > .sheet { position: absolute; left: 0.25in; top: 0.25in; margin: 0; box-shadow: none;
                           transform: scale(1.029412, 1.022727); transform-origin: center center; }
    .crop { position: absolute; left: 0; top: 0; width: 9in; height: 11.5in; pointer-events: none; }
    @media screen { .bleed-page { outline: 1px dashed rgba(197,150,58,0.35); outline-offset: 10px; } }
"""

html = (SRC / f"{STEM}.html").read_text()
html = html.replace("size: 8.5in 11in", "size: 9in 11.5in")
html = html.replace("</style>", BLEED_CSS + "  </style>", 1)
m = re.search(r'<div class="sheet"[^>]*>', html)
start, end = m.start(), match_close(html, m.start())
html = html[:start] + '<div class="bleed-page">' + html[start:end] + CROP + "</div>" + html[end:]
(SRC / f"{STEM}-bleed.html").write_text(html)
print(f"wrote {STEM}-bleed.html")
