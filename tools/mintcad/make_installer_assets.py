#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: erzeugt Programmsymbol und Installer-Grafiken für Windows und Linux.

Aufruf (aus dem Quellordner):  pixi run python -I tools/mintcad/make_installer_assets.py
Ausgabe:  tools/mintcad/windows/{mintcad.ico,header.bmp,banner.bmp}
          tools/mintcad/linux/{de.mint-checker.MINT-CAD.svg,.png}
Verwendet das Logo aus make_branding.py (Windows-Icon enthält PNG-Größen 16 bis 256).
"""
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QRectF, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter

import make_branding as mb

HERE = os.path.dirname(os.path.abspath(__file__))
WIN = os.path.join(HERE, "windows")
LIN = os.path.join(HERE, "linux")


def icon_png(px):
    img = QImage(px, px, QImage.Format_ARGB32_Premultiplied)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
    mb.draw_logo(p, QRectF(0, 0, px, px))
    p.end()
    return img


def png_bytes(img):
    ba = QByteArray()
    buf = QBuffer(ba)
    buf.open(QIODevice.WriteOnly)
    img.save(buf, "PNG")
    return bytes(ba)


def write_ico(path, sizes=(16, 24, 32, 48, 64, 128, 256)):
    images = [(s, png_bytes(icon_png(s))) for s in sizes]
    out = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    for s, data in images:
        out += struct.pack("<BBBBHHII", s % 256, s % 256, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    with open(path, "wb") as fh:
        fh.write(out + b"".join(d for _, d in images))


def header_bmp():  # NSIS: 150 x 57
    img, p = mb.canvas(150, 57, "#ffffff")
    mb.draw_logo(p, QRectF(8, 6, 45, 45))
    mb.text(p, 60, 8, 90, 24, "MINT-CAD", 17, mb.NAVY, True)
    mb.text(p, 61, 30, 90, 18, "Konstruieren", 11, "#475569")
    p.end()
    return img.convertToFormat(QImage.Format_RGB888)


def banner_bmp():  # NSIS: 164 x 314 (Willkommensseite)
    img, p = mb.canvas(164, 314, mb.NAVY)
    p.fillRect(QRectF(0, 0, 164, 5), mb.QColor(mb.BLUE))
    mb.draw_logo(p, QRectF(26, 50, 112, 112))
    mb.text(p, 14, 178, 140, 34, "MINT-CAD", 25, mb.TEXT, True)
    mb.text(p, 15, 212, 140, 50, "Skizzieren,\nKonstruieren,\nZeichnen", 13, mb.MUTED)
    mb.text(p, 15, 280, 140, 20, "Basiert auf FreeCAD", 11, mb.MUTED)
    p.end()
    return img.convertToFormat(QImage.Format_RGB888)


def main():
    QGuiApplication(sys.argv[:1])
    os.makedirs(WIN, exist_ok=True)
    os.makedirs(LIN, exist_ok=True)
    write_ico(os.path.join(WIN, "mintcad.ico"))
    header_bmp().save(os.path.join(WIN, "header.bmp"), "BMP")
    banner_bmp().save(os.path.join(WIN, "banner.bmp"), "BMP")
    with open(os.path.join(LIN, "de.mint-checker.MINT-CAD.svg"), "w", encoding="utf-8") as fh:
        fh.write(mb.logo_svg())
    icon_png(256).save(os.path.join(LIN, "de.mint-checker.MINT-CAD.png"), "PNG")
    print("Fertig:", WIN, LIN)


if __name__ == "__main__":
    main()
