#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Prüft ein MINT-CAD.app-Paket: Alle Bibliotheken müssen im Paket liegen, keine absoluten Pfade in den Entwicklungsordner."""
import os
import subprocess
import sys

resources = os.path.join(os.path.abspath(sys.argv[1]), "Contents", "Resources")
forbidden = sys.argv[2:]  # Pfadanfänge, die nicht vorkommen dürfen
names, files = set(), []
for base, _, fnames in os.walk(resources):
    for f in fnames:
        p = os.path.join(base, f)
        names.add(f)
        if os.path.islink(p):
            continue
        if f.endswith((".dylib", ".so")) or os.sep + "bin" + os.sep in p:
            files.append(p)

missing, leaks = {}, {}
for p in files:
    out = subprocess.run(["otool", "-L", p], capture_output=True, text=True).stdout
    if "is not an object file" in out or not out:
        continue
    for line in out.splitlines()[1:]:
        dep = line.strip().split(" (")[0]
        if any(dep.startswith(x) for x in forbidden):
            leaks.setdefault(dep, p)
        elif dep.startswith("@rpath/") and os.path.basename(dep) not in names and not os.path.basename(dep).endswith(os.path.basename(p)):
            missing.setdefault(os.path.basename(dep), p)
    rp = subprocess.run(["otool", "-l", p], capture_output=True, text=True).stdout
    for line in rp.splitlines():
        s = line.strip()
        if s.startswith("path ") and any(s[5:].startswith(x) for x in forbidden):
            leaks.setdefault("RPATH " + s[5:].split(" (")[0], p)

print("geprüfte Dateien:", len(files))
for k, v in sorted(missing.items()):
    print("FEHLT:", k, "<-", os.path.relpath(v, resources))
for k, v in sorted(leaks.items()):
    print("ABSOLUT:", k, "<-", os.path.relpath(v, resources))
print("fehlend: %d, absolute Pfade: %d" % (len(missing), len(leaks)))
sys.exit(1 if missing or leaks else 0)
