#!/usr/bin/env bash
# ---------------------------------------------------------
# Lumo‑Viewer – automatischer Installations‑Helper
# ---------------------------------------------------------
# Dieser Installer erledigt:
#   • Prüfung von Python 3 und pip
#   • Anlegen eines virtuellen Environments (.venv)
#   • Installation der Python‑Abhängigkeiten (requirements.txt)
#   • Setzen der Ausführungsrechte für die Skripte
#   • Installation des Desktop‑Eintrags (mit dynamischen Home‑Pfaden)
# ---------------------------------------------------------

set -euo pipefail

# ---------- 1. Konstanten ----------
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_ROOT}/.venv"
REQ_FILE="${PROJECT_ROOT}/requirements.txt"
DESKTOP_SRC="${PROJECT_ROOT}/lumo-viewer.desktop"
DESKTOP_DST="${HOME}/.local/share/applications/lumo-viewer.desktop"

# ---------- 2. Hilfsfunktionen ----------
log()   { echo -e "\e[32m[+] $*\e[0m"; }
warn()  { echo -e "\e[33m[!] $*\e[0m"; }
error() { echo -e "\e[31m[-] $*\e[0m" >&2; exit 1; }

# ---------- 3. Prerequisites ----------
log "Prüfe Python3 ..."
if ! command -v python3 >/dev/null; then
    error "Python3 nicht gefunden – bitte installieren."
fi

PYVER=$(python3 -c 'import sys; print("%d.%d" % sys.version_info[:2])')
if (( $(echo "$PYVER < 3.8" | bc -l) )); then
    error "Python >= 3.8 benötigt (gefunden: $PYVER)."
fi

log "Prüfe pip ..."
if ! command -v pip3 >/dev/null; then
    error "pip3 nicht gefunden – bitte installieren."
fi

# ---------- 4. Virtuelles Environment ----------
if [[ -d "$VENV_DIR" ]]; then
    log "Virtuelles Environment existiert bereits → benutze es."
else
    log "Erstelle virtuelles Environment in .venv ..."
    python3 -m venv "$VENV_DIR"
fi

# Aktivieren
# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"

# Upgrade pip
log "Upgrade pip ..."
pip install --upgrade pip setuptools wheel

# ---------- 5. Abhängigkeiten ----------
if [[ -f "$REQ_FILE" ]]; then
    log "Installiere Python‑Abhängigkeiten ..."
    pip install -r "$REQ_FILE"
else
    warn "Keine requirements.txt gefunden – überspringe Pip‑Installation."
fi

# ---------- 6. Skripte ausführbar ----------
log "Setze Ausführungsrechte ..."
chmod +x "${PROJECT_ROOT}/run-lumo-viewer.sh"
chmod +x "${PROJECT_ROOT}/main.py"

# ---------- 7. Desktop‑Eintrag ----------
log "Installiere Desktop‑Eintrag ..."

# Zielverzeichnis sicherstellen
mkdir -p "$(dirname "$DESKTOP_DST")"

# Kopieren des Originals
cp "$DESKTOP_SRC" "$DESKTOP_DST"

# Absoluten Pfad für Exec und Icon eintragen (Home‑Pfad dynamisch)
# Wir ersetzen alles hinter "Exec=" bzw. "Icon=" durch die korrekten Pfade.
sed -i "s|^Exec=.*|Exec=${PROJECT_ROOT}/run-lumo-viewer.sh|g" "$DESKTOP_DST"
sed -i "s|^Icon=.*|Icon=${PROJECT_ROOT}/proton-lumo.svg|g" "$DESKTOP_DST"

# Desktop‑Cache aktualisieren (falls das Tool vorhanden ist)
if command -v update-desktop-database >/dev/null; then
    log "Aktualisiere Desktop‑Datenbank ..."
    update-desktop-database "$(dirname "$DESKTOP_DST")"
fi

log "✅  Installation abgeschlossen!"
log "Starten Sie Lumo‑Viewer über das Anwendungsmenü oder mit:"
echo "    ${PROJECT_ROOT}/run-lumo-viewer.sh"