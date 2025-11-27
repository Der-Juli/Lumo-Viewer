#!/usr/bin/env bash
# ---------------------------------------------------------
# Wrapper für Lumo‑Viewer – aktiviert das venv und startet das Skript
# ---------------------------------------------------------

# got to working dir
cd 

# virtuelles Environment aktivieren
source ".venv/bin/activate"
# Start Viewer
exec ./main.py
