#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: erzeugt aus den FreeCAD-Icons einen einheitlichen, flachen Icon-Satz für dunkle Oberflächen.

Vorgehen je SVG: Verläufe -> Flächenfarbe, Schatten/Filter entfernen, Neutraltöne invertieren
(dunkle Konturen werden hell), Buntfarben auf die PAP-Editor-Palette abbilden, Linien abrunden.

Aufruf:  python3 -I tools/mintcad/make_icons.py <Ausgabeordner> [Icon.svg ...]
Ohne Dateiliste werden alle Icons der behaltenen Module verarbeitet.
"""
import colorsys
import os
import re
import sys
from lxml import etree

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIRS = [
    "src/Gui/Icons",
    "src/Mod/Part/Gui/Resources/icons",
    "src/Mod/PartDesign/Gui/Resources/icons",
    "src/Mod/Sketcher/Gui/Resources/icons",
    "src/Mod/TechDraw/Gui/Resources/icons",
    "src/Mod/Draft/Resources/icons",
    "src/Mod/Assembly/Gui/Resources/icons",
    "src/Mod/Fem/Gui/Resources/icons",
    "src/Mod/Spreadsheet/Gui/Resources/icons",
    "src/Mod/Mesh/Gui/Resources/icons",
    "src/Mod/Measure/Gui/Resources/icons",
    "src/Mod/Import/Gui/Resources/icons",
    "src/Mod/Start/Gui/Resources/icons",
]

NS = {"svg": "http://www.w3.org/2000/svg", "xlink": "http://www.w3.org/1999/xlink"}
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"

# Palette (angelehnt an PAP Editor / Tailwind)
OUTLINE = (226, 232, 240)   # #e2e8f0  helle Kontur
MIDGRAY = (148, 163, 184)   # #94a3b8
DARKFILL = (51, 65, 85)     # #334155
PAPER = (30, 41, 59)        # #1e293b
HUES = [  # (Obergrenze Hue in Grad, Farbe)
    (20, (251, 113, 133)),   # rot  -> rose
    (70, (251, 191, 36)),    # orange/gelb -> amber
    (170, (74, 222, 128)),   # grün
    (250, (96, 165, 250)),   # blau
    (345, (167, 139, 250)),  # violett
    (361, (251, 113, 133)),  # zurück zu rot
]

NAMED = {"white": "#ffffff", "black": "#000000", "red": "#ff0000", "blue": "#0000ff",
         "green": "#008000", "yellow": "#ffff00", "gray": "#808080", "grey": "#808080",
         "orange": "#ffa500", "lime": "#00ff00", "cyan": "#00ffff", "magenta": "#ff00ff"}


def parse_color(value):
    value = value.strip().lower()
    value = NAMED.get(value, value)
    m = re.fullmatch(r"#([0-9a-f]{3})", value)
    if m:
        h = m.group(1)
        return tuple(int(c * 2, 16) for c in h)
    m = re.fullmatch(r"#([0-9a-f]{6})", value)
    if m:
        h = m.group(1)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = re.fullmatch(r"rgb\(([^)]*)\)", value)
    if m:
        parts = [p.strip() for p in m.group(1).split(",")]
        out = []
        for p in parts[:3]:
            out.append(round(float(p[:-1]) * 2.55) if p.endswith("%") else int(float(p)))
        return tuple(out)
    return None


def to_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def restyle(rgb, kind, opacity):
    """Bildet eine Originalfarbe auf die MINT-CAD-Palette ab."""
    r, g, b = (c / 255 for c in rgb)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if l < 0.22 or s < 0.15:                      # dunkel oder neutral -> invertiert
        if l >= 0.9:                              # fast weiß
            if kind == "fill" and opacity < 0.95:  # Glanzlicht bleibt Glanzlicht
                return (255, 255, 255)
            return PAPER if kind == "fill" else OUTLINE
        if l < 0.3:
            return OUTLINE
        if l < 0.6:
            return MIDGRAY
        return DARKFILL
    deg = h * 360
    for limit, col in HUES:
        if deg < limit:
            base = col
            break
    br, bg_, bb = (c / 255 for c in base)
    bh, bl, bs = colorsys.rgb_to_hls(br, bg_, bb)
    nl = 0.42 + 0.30 * l                          # Helligkeitsunterschiede bleiben erhalten
    if kind == "stroke":
        nl = max(0.45, nl - 0.05)
    nr, ng, nb = colorsys.hls_to_rgb(bh, nl, min(1.0, 0.55 + 0.4 * s))
    return (nr * 255, ng * 255, nb * 255)


def style_dict(el):
    d = {}
    style = el.get("style")
    if style:
        for part in style.split(";"):
            if ":" in part:
                k, v = part.split(":", 1)
                d[k.strip()] = v.strip()
    return d


def gradient_colors(root):
    """id -> Farbe (Mittelwert der Stops), Verweise (xlink:href) werden aufgelöst."""
    grads = {}
    for g in root.iter("{%s}linearGradient" % NS["svg"], "{%s}radialGradient" % NS["svg"]):
        grads[g.get("id")] = g

    def stops(g, seen=()):
        found = g.findall("svg:stop", NS)
        if found:
            return found
        href = g.get(XLINK_HREF)
        if href and href.startswith("#") and href[1:] in grads and href[1:] not in seen:
            return stops(grads[href[1:]], seen + (href[1:],))
        return []

    result = {}
    for gid, g in grads.items():
        cols = []
        for st in stops(g):
            sd = style_dict(st)
            c = parse_color(sd.get("stop-color", st.get("stop-color", "#808080")))
            if c:
                cols.append(c)
        if cols:
            result[gid] = tuple(sum(c[i] for c in cols) / len(cols) for i in range(3))
    return result


def convert(path, out_path):
    tree = etree.parse(path)
    root = tree.getroot()
    gcol = gradient_colors(root)

    # Filter und Metadaten entfernen
    for tag in ("filter", "metadata", "{http://www.w3.org/2000/svg}metadata"):
        for el in list(root.iter("{%s}%s" % (NS["svg"], tag.split("}")[-1]))):
            el.getparent().remove(el)

    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        sd = style_dict(el)
        changed = False

        def get(name):
            return sd.get(name, el.get(name))

        try:
            op = float(get("opacity") or 1) * float(get("fill-opacity") or 1)
        except ValueError:
            op = 1.0
        for prop, kind in (("fill", "fill"), ("stroke", "stroke")):
            val = get(prop)
            if not val or val in ("none", "inherit", "currentColor"):
                continue
            rgb = None
            m = re.fullmatch(r"url\(#([^)]+)\)", val)
            if m:
                rgb = gcol.get(m.group(1))
            else:
                rgb = parse_color(val)
            if rgb is None:
                continue
            sd[prop] = to_hex(restyle(rgb, kind, op))
            if prop in el.attrib:
                del el.attrib[prop]
            changed = True
        for prop in ("stop-color", "flood-color", "lighting-color"):
            val = get(prop)
            if val:
                rgb = parse_color(val)
                if rgb:
                    sd[prop] = to_hex(restyle(rgb, "fill", 1.0))
                    el.attrib.pop(prop, None)
                    changed = True
        if "filter" in sd or el.get("filter"):
            sd.pop("filter", None)
            el.attrib.pop("filter", None)
            changed = True
        if sd.get("stroke") not in (None, "none"):
            sd["stroke-linejoin"] = "round"
            sd["stroke-linecap"] = "round"
            changed = True
        if changed:
            el.set("style", ";".join("%s:%s" % kv for kv in sd.items()))

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    tree.write(out_path, xml_declaration=True, encoding="UTF-8")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    out = sys.argv[1]
    files = sys.argv[2:]
    if not files:
        for d in SRC_DIRS:
            full = os.path.join(ROOT, d)
            if os.path.isdir(full):
                files += [os.path.join(full, f) for f in sorted(os.listdir(full)) if f.endswith(".svg")]
    seen = set()
    done = 0
    for f in files:
        name = os.path.basename(f)
        if name in seen:
            continue
        seen.add(name)
        try:
            convert(f, os.path.join(out, name))
            done += 1
        except Exception as exc:  # defektes SVG überspringen
            print("übersprungen:", name, exc)
    print("%d Icons erzeugt" % done)
    return 0


if __name__ == "__main__":
    sys.exit(main())
