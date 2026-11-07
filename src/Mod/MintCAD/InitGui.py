# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: Schulanpassungen. Wird beim Start der Oberfläche geladen."""

import MintCADSetup

MintCADSetup.apply_workbench_selection()

import MintCADSimplify

MintCADSimplify.install()
