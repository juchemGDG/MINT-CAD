# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: Vereinfachung der Werkzeugleisten und Menüs (WorkbenchManipulator).

Die Listen unten enthalten, was für den Unterricht ausgeblendet wird. Die Befehle bleiben
in FreeCAD vorhanden (Einstellungen > Anpassen), sie erscheinen nur nicht mehr standardmäßig.
Pro Aufruf entfernt der Manipulator das erste Vorkommen, daher wird jeder Befehl einmal gelistet.
"""

import FreeCADGui as Gui

# Ganze Werkzeugleisten (interne Namen)
HIDE_TOOLBARS = [
]

# Einzelne Befehle (aus Werkzeugleisten und Menüs)
HIDE_COMMANDS = [
]


class _Simplifier:
    def modifyToolBars(self):
        return [{"remove": name} for name in HIDE_TOOLBARS + HIDE_COMMANDS]

    def modifyMenuBar(self):
        return [{"remove": name} for name in HIDE_COMMANDS]


_manipulator = None


def install():
    global _manipulator
    if _manipulator is None:
        _manipulator = _Simplifier()
        Gui.addWorkbenchManipulator(_manipulator)
