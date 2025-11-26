#!/usr/bin/env bash
# ---------------------------------------------------------
# Wrapper für Lumo‑Viewer – aktiviert das venv und startet das Skript
# ---------------------------------------------------------

# Pfad zum Projekt (anpassen, falls anders)
PROJECT_DIR="/home/juli/projects/priv/Lumo-Viewer"

# in das Projektverzeichnis wechseln
cd "$PROJECT_DIR" || exit 1

# virtuelles Environment aktivieren
source ".venv/bin/activate"

# Python‑Skript ausführen (falls es nicht ausführbar ist, benutzen Sie python3)
exec ./main.py   # <-- "./main.py" muss ausführbar sein (chmod +x)
