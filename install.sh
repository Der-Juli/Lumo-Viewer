#!/usr/bin/env bash
# ---------------------------------------------------------
# Lumo‑Viewer – automatischer Installations‑Helper
# ---------------------------------------------------------
# Dieses Skript erledigt:
#   • Prüfung von Python 3 (mind. 3.8) und pip
#   • Anlegen eines virtuellen Environments (.venv)
#   • Installation der Python‑Abhängigkeiten (requirements.txt)
#   • Setzen der Ausführungsrechte für die Skripte
#   • Installation des Desktop‑Eintrags (mit dynamischen Pfaden)
# ---------------------------------------------------------

set -euo pipefail

# ---------- 1. Konstanten ----------
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_ROOT}/.venv"
REQ_FILE="${PROJECT_ROOT}/requirements.txt"
DESKTOP_SRC="${PROJECT_ROOT}/lumo-viewer.desktop"
DESKTOP_DST="${HOME}/.local/share/applications/lumo-viewer.desktop"
START_SCRIPT="${PROJECT_ROOT}/run-lumo-viewer.sh"

# ---------- 2. Hilfsfunktionen ----------
log()   { echo -e "\e[32m[+] $*\e[0m"; }
warn()  { echo -e "\e[33m[!] $*\e[0m"; }
error() { echo -e "\e[31m[-] $*\e[0m" >&2; exit 1; }

# ---------- 3. Python‑Version prüfen ----------
log "Prüfe Python3 (>= 3.8)…"
if ! command -v python3 >/dev/null; then
    error "Python3 nicht gefunden – bitte installieren."
fi

# Der Check läuft komplett in Python, daher unabhängig von bc, awk, … 
PY_OK=$(python3 - <<'PY'
import sys
if sys.version_info >= (3, 8):
    sys.exit(0)
else:
    sys.exit(1)
PY
)

if [[ "$PY_OK" -ne 0 ]]; then
    # Wenn wir hier landen, ist die Version zu alt
    FOUND_VER=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
    error "Python >= 3.8 benötigt (gefunden: $FOUND_VER)."
fi
log "Python‑Version OK."

# ---------- 4. pip prüfen ----------
log "Prüfe pip3 …"
if ! command -v pip3 >/dev/null; then
    error "pip3 nicht gefunden – bitte installieren."
fi

# ---------- 5. Virtuelles Environment ----------
if [[ -d "$VENV_DIR" ]]; then
    log "Virtuelles Environment existiert bereits → benutze es."
else
    log "Erstelle virtuelles Environment in .venv …"
    python3 -m venv "$VENV_DIR"
fi

# Aktivieren
# shellcheck source=/dev/null
source "${VENV_DIR}/bin/activate"

# Upgrade pip, setuptools, wheel
log "Upgrade pip, setuptools, wheel …"
pip install --quiet --upgrade pip setuptools wheel

# ---------- 6. Abhängigkeiten ----------
if [[ -f "$REQ_FILE" ]]; then
    log "Installiere Python‑Abhängigkeiten aus requirements.txt …"
    pip install --quiet -r "$REQ_FILE"
else
    warn "Keine requirements.txt gefunden – überspringe Pip‑Installation."
fi

# ---------- 7. Skripte ausführbar ----------
log "Setze Ausführungsrechte für run‑lumo‑viewer.sh und main.py …"
chmod +x "${PROJECT_ROOT}/run-lumo-viewer.sh"
chmod +x "${PROJECT_ROOT}/main.py"

# ---------- 8. Desktop‑Eintrag ----------
log "Installiere Desktop‑Eintrag …"
mkdir -p "$(dirname "$DESKTOP_DST")"
cp "$DESKTOP_SRC" "$DESKTOP_DST"

# Pfade dynamisch eintragen (absolute Pfade zum Projekt)
sed -i "s|^Exec=.*|Exec=${PROJECT_ROOT}/run-lumo-viewer.sh|g" "$DESKTOP_DST"
sed -i "s|^Icon=.*|Icon=${PROJECT_ROOT}/proton-lumo.png|g" "$DESKTOP_DST"
sed -i "s|^cd.*|cd ${PROJECT_ROOT}/|g" "$START_SCRIPT"

# Desktop‑Cache aktualisieren (wenn das Tool vorhanden ist)
if command -v update-desktop-database >/dev/null; then
    log "Aktualisiere Desktop‑Datenbank …"
    update-desktop-database "$(dirname "$DESKTOP_DST")"
fi

log "✅  Installation erfolgreich abgeschlossen!"
log "Sie können Lumo‑Viewer jetzt über das Anwendungsmenü starten oder mit:"
echo "    ${PROJECT_ROOT}/run-lumo-viewer.sh"
