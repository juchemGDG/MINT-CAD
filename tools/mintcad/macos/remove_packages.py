# SPDX-License-Identifier: LGPL-2.1-or-later
# MINT-CAD: entfernt alle Dateien der genannten conda-Pakete aus dem Programmpaket.
# Aufruf: remove_packages.py <Umgebung> <Resources> <Paket>...
import json,glob,os,sys
env,res=sys.argv[1:3]; names=set(sys.argv[3:])
n=0
for f in glob.glob(env+"/conda-meta/*.json"):
    d=json.load(open(f))
    if d["name"] in names:
        for x in d.get("files",[]):
            p=os.path.join(res,x)
            if os.path.lexists(p) and not os.path.isdir(p):
                os.remove(p); n+=1
print("entfernt:",n,"Dateien")
