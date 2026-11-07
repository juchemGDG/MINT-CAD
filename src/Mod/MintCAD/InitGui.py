# SPDX-License-Identifier: LGPL-2.1-or-later
"""MINT-CAD: Schulanpassungen. Wird beim Start der Oberfläche geladen."""

import MintCADSetup

MintCADSetup.apply_defaults()

import MintCADSimplify

MintCADSimplify.install()

import MintCADHelp

MintCADHelp.register()
