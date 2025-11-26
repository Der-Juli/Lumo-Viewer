#!/usr/bin/env bash
# ---------------------------------------------------------
# Wrapper für Lumo‑Viewer – aktiviert das venv und startet das Skript
# ---------------------------------------------------------

# virtuelles Environment aktivieren
source ".venv/bin/activate"
# Start Viewer
exec ./main.py
