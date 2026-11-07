# Design-Tokens (aus dem PAP Editor, pap.mint-checker.de)

Quelle: `pap-reference.css`. Diese Werte werden später in das Qt-Stylesheet übernommen.

| Token | Wert | Verwendung |
|---|---|---|
| bg-sidebar | #0f172a | Seitenleiste / Docks (dunkel) |
| surface | #1e293b | Karten, Buttons in dunklen Bereichen |
| surface-hover | #2d3f55 | Hover/Active auf surface |
| border | #334155 | Rahmen dunkel |
| border-hover | #475569 | Rahmen Hover |
| text | #f8fafc | Text auf dunkel |
| text-muted | #94a3b8 | Nebentext, Labels |
| bg-main | #f8fafc | Arbeitsfläche (hell) |
| topbar | #e2e8f0 | Werkzeugleiste (hell) |
| topbar-border | #cbd5e1 | Trennlinien hell |
| text-dark | #0f172a | Text auf hell |
| text-dark-muted | #475569 | Statuszeile |
| accent | #2563eb | Primäre Aktion |
| accent-hover | #4f46e5 | Hover primär |
| accent-active | #1d4ed8 | Pressed primär |
| danger | #dc2626 | Löschen |
| radius-card | 10px | Karten, Menüs |
| radius-btn | 6px | Buttons |
| radius-modal | 14px | Dialoge |
| font | Helvetica, Arial, sans-serif | Schrift |

Layout-Prinzip: dunkle Seitenleiste (252px) links mit Karten-Bausteinen,
helle Arbeitsfläche rechts, zweizeilige Kopfleiste (Titel + Status / Aktionen),
einzelne blaue Primär-Schaltfläche, runde Ecken, dezente Schatten.

Abbildung auf FreeCAD: Seitenleiste = Kombi-Ansicht/Baumansicht, Karten = Befehls-Buttons
der Schul-Workbench, Arbeitsfläche = 3D-Ansicht/Skizze, Kopfleiste = Werkzeugleiste.
