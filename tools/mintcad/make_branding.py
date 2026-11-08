#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: erzeugt Logo, Startbild (Splash), Info-Bild und das macOS-Programmsymbol.

Aufruf (aus dem Quellordner):  pixi run python -I tools/mintcad/make_branding.py
Das Logo ist ein Skizzen-Linienzug in M-Form mit Punkten, in den Farben des PAP Editors.
"""
import os
import subprocess
import sys
import tempfile

os.environ["QT_QPA_PLATFORM"] = "offscreen"
from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ICONS = os.path.join(ROOT, "src", "Gui", "Icons")
NAVY, CARD, BLUE, TEXT, MUTED = "#0f172a", "#1e293b", "#2563eb", "#f8fafc", "#94a3b8"
ACCENT = "#60a5fa"


def logo_svg(background=True):
    bg = '<rect x="4" y="4" width="120" height="120" rx="27" fill="%s"/>' % NAVY if background else ""
    pts = [(32, 92), (32, 36), (64, 74), (96, 36), (96, 92)]
    line = " ".join("%d,%d" % p for p in pts)
    dots = "".join('<circle cx="%d" cy="%d" r="9.5" fill="%s" stroke="%s" stroke-width="4"/>' % (x, y, ACCENT, NAVY) for x, y in pts)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">%s'
        '<polyline points="%s" fill="none" stroke="%s" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>%s</svg>'
        % (bg, line, TEXT, dots)
    )


def draw_logo(painter, rect):
    QSvgRenderer(QByteArray(logo_svg().encode())).render(painter, rect)


def canvas(w, h, color=NAVY):
    img = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
    img.fill(QColor(color))
    p = QPainter(img)
    p.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing | QPainter.SmoothPixmapTransform)
    return img, p


def text(p, x, y, w, h, s, size, color, bold=False):
    f = QFont("Helvetica")
    f.setPixelSize(int(size))
    f.setBold(bold)
    p.setFont(f)
    p.setPen(QColor(color))
    p.drawText(QRectF(x, y, w, h), Qt.AlignLeft | Qt.AlignVCenter, s)


def splash(k):
    img, p = canvas(568 * k, 368 * k)
    p.scale(k, k)
    p.fillRect(QRectF(0, 0, 568, 5), QColor(BLUE))
    draw_logo(p, QRectF(40, 72, 112, 112))
    text(p, 172, 78, 380, 60, "MINT-CAD", 50, TEXT, True)
    text(p, 174, 138, 380, 30, "Skizzieren, Konstruieren, Zeichnen", 18, MUTED)
    text(p, 40, 318, 490, 22, "Basiert auf FreeCAD (LGPL)", 13, MUTED)
    p.end()
    return img


def about():
    img, p = canvas(552 * 2, 189 * 2)
    p.scale(2, 2)
    draw_logo(p, QRectF(28, 40, 108, 108))
    text(p, 156, 48, 380, 56, "MINT-CAD", 44, TEXT, True)
    text(p, 158, 102, 380, 26, "Skizzieren, Konstruieren, Zeichnen", 16, MUTED)
    text(p, 158, 128, 380, 22, "Basiert auf FreeCAD (LGPL)", 13, MUTED)
    p.end()
    return img.scaled(552, 189, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)


def app_icon_set(iconset):
    os.makedirs(iconset)
    for size in (16, 32, 128, 256, 512):
        for scale in (1, 2):
            px = size * scale
            img = QImage(px, px, QImage.Format_ARGB32_Premultiplied)
            img.fill(Qt.transparent)
            p = QPainter(img)
            p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
            draw_logo(p, QRectF(0, 0, px, px))
            p.end()
            img.save(os.path.join(iconset, "icon_%dx%d%s.png" % (size, size, "@2x" if scale == 2 else "")))


def main():
    QGuiApplication(sys.argv[:1])
    with open(os.path.join(ICONS, "mintcad.svg"), "w", encoding="utf-8") as fh:
        fh.write(logo_svg())
    splash(1).save(os.path.join(ICONS, "mintcadsplash.png"))
    splash(2).save(os.path.join(ICONS, "mintcadsplash_2x.png"))
    about().save(os.path.join(ICONS, "mintcadabout.png"))
    with tempfile.TemporaryDirectory() as tmp:
        iconset = os.path.join(tmp, "mintcad.iconset")
        app_icon_set(iconset)
        target = os.path.join(ROOT, "tools", "mintcad", "macos", "mintcad.icns")
        subprocess.run(["iconutil", "-c", "icns", iconset, "-o", target], check=True)
    print("Branding erzeugt")


if __name__ == "__main__":
    main()
