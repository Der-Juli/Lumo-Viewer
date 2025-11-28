#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
venv_path = "/home/juli/projects/priv/Lumo-Viewer/.venv"
site_packages = os.path.join(
    venv_path,
    "lib",
    f"python{sys.version_info.major}.{sys.version_info.minor}",
    "site-packages"
)

if site_packages not in sys.path:
    sys.path.insert(0, site_packages)   # vorn einfügen, hat Vorrang

# Optional: VIRTUAL_ENV setzen – manche Pakete prüfen das
os.environ["VIRTUAL_ENV"] = venv_path


from PyQt5.QtCore import QUrl, Qt, QMimeData
from PyQt5.QtGui import QKeySequence, QClipboard, QPalette, QColor
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QAction,
    QShortcut,
    QMessageBox,
)
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView,
    QWebEnginePage,
    QWebEngineSettings,
    QWebEngineProfile,
)


# ----------------------------------------------------------------------
# 1️⃣  Dark‑Palette & Stylesheet (inkl. Menü‑Leiste)
# ----------------------------------------------------------------------
def apply_lumo_dark_palette(app: QApplication) -> None:
    """Setzt ein dunkles Farbschema für das gesamte Qt‑Interface."""
    dark_palette = QPalette()

    # Grundfarben
    dark_palette.setColor(QPalette.Window, QColor("#0d0d0d"))
    dark_palette.setColor(QPalette.WindowText, QColor("#e6e6e6"))
    dark_palette.setColor(QPalette.Base, QColor("#1e1e1e"))
    dark_palette.setColor(QPalette.AlternateBase, QColor("#2c2c2c"))
    dark_palette.setColor(QPalette.ToolTipBase, QColor("#e6e6e6"))
    dark_palette.setColor(QPalette.ToolTipText, QColor("#e6e6e6"))

    # Text‑ und Button‑Farben
    dark_palette.setColor(QPalette.Text, QColor("#e6e6e6"))
    dark_palette.setColor(QPalette.Button, QColor("#333333"))
    dark_palette.setColor(QPalette.ButtonText, QColor("#e6e6e6"))
    dark_palette.setColor(QPalette.BrightText, QColor("#ff5555"))

    # Links / Highlight
    dark_palette.setColor(QPalette.Link, QColor("#80cbc4"))
    dark_palette.setColor(QPalette.Highlight, QColor("#80cbc4"))
    dark_palette.setColor(QPalette.HighlightedText, QColor("#0d0d0d"))

    # Menü‑Leiste und Tool‑Bars explizit dunkel färben
    dark_palette.setColor(QPalette.Light, QColor("#2c2c2c"))
    dark_palette.setColor(QPalette.Midlight, QColor("#1e1e1e"))
    dark_palette.setColor(QPalette.Dark, QColor("#0d0d0d"))

    app.setPalette(dark_palette)


# Optionales Stylesheet für Rahmen, Menüs usw.
DARK_FRAME_STYLESHEET = """
QWidget {
    background-color: #0d0d0d;
    color: #e6e6e6;
    border: 1px solid #333333;
    border-radius: 4px;
}

/* Menü‑Leiste */
QMenuBar {
    background-color: #0d0d0d;
    spacing: 3px;
}
QMenuBar::item {
    background: transparent;
    padding: 4px 10px;
}
QMenuBar::item:selected {
    background: #333333;
}

/* Kontext‑Menüs */
QMenu {
    background-color: #1e1e1e;
    border: 1px solid #333333;
}
QMenu::item:selected {
    background-color: #333333;
}
"""


# ----------------------------------------------------------------------
# 2️⃣  Navigation‑Lock (nur erlaubte Domains zulassen)
# ----------------------------------------------------------------------
class LockedPage(QWebEnginePage):
    allowed_base = QUrl("https://lumo.proton.me/")

    def acceptNavigationRequest(self, url: QUrl, _type, isMainFrame: bool):
        # Alles unterhalb der Basis‑Domain und alle *.proton.me‑Subdomains zulassen
        if url.toString().startswith(self.allowed_base.toString()):
            return True
        if url.host().endswith("proton.me"):
            return True
        print(f"[BLOCKED] {url.toString()}")
        return False


# ----------------------------------------------------------------------
# 3️⃣  Hauptfenster (QMainWindow) inkl. Menü‑Bar, Aktionen & Shortcuts
# ----------------------------------------------------------------------
class SinglePageWindow(QMainWindow):
    TARGET_URL = "https://lumo.proton.me/u/18/"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lumo Viewer")          # Gewünschter Titel
        self.resize(1024, 768)

        # ----- Zentrales Widget & Layout ---------------------------------
        central = QWidget(self)
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # ----- Web‑View ---------------------------------------------------
        self.web_view = QWebEngineView(self)
        self.web_view.setPage(LockedPage(self.web_view))

        # ---- Aktivieren von Cookies (über das Profil) -------------------
        profile: QWebEngineProfile = self.web_view.page().profile()
        profile.setPersistentCookiesPolicy(
            QWebEngineProfile.ForcePersistentCookies
        )  # <-- jetzt aktiv

        # Optional: Lokalen Speicher aktivieren (für z. B. IndexedDB)
        settings = self.web_view.settings()
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)

        layout.addWidget(self.web_view)

        # ----- Aktionen & Shortcuts erstellen -----------------------------
        self._create_actions()
        self._install_shortcuts()

        # ----- Ziel‑URL laden --------------------------------------------
        self.web_view.load(QUrl(self.TARGET_URL))

    # ------------------------------------------------------------------
    # Aktionen (QAction) – werden später in den Menüs verwendet
    # ------------------------------------------------------------------
    def _create_actions(self):
        # Neu laden
        self.act_reload = QAction("Neu laden", self, shortcut=QKeySequence("Ctrl+R"))
        self.act_reload.triggered.connect(self.reload_page)

        # Beenden
        self.act_quit = QAction("Beenden", self, shortcut=QKeySequence("Ctrl+Q"))
        self.act_quit.triggered.connect(QApplication.instance().quit)

        # Vollbild
        self.act_fullscreen = QAction("Vollbild", self, shortcut=QKeySequence("F11"))
        self.act_fullscreen.triggered.connect(self.toggle_fullscreen)

        # Entwickler‑Tools
        self.act_devtools = QAction(
            "Entwickler‑Tools", self, shortcut=QKeySequence("Ctrl+Shift+I")
        )
        self.act_devtools.triggered.connect(self.open_devtools)

        # URL kopieren
        self.act_copy_url = QAction(
            "URL kopieren", self, shortcut=QKeySequence("Ctrl+L")
        )
        self.act_copy_url.triggered.connect(self.copy_current_url)

        # ----- Menü‑Bar zusammenbauen ------------------------------------
        menubar = self.menuBar()

        # Datei‑Menü
        file_menu = menubar.addMenu("Datei")
        file_menu.addAction(self.act_reload)
        file_menu.addSeparator()
        file_menu.addAction(self.act_quit)

        # Ansicht‑Menü
        view_menu = menubar.addMenu("Ansicht")
        view_menu.addAction(self.act_fullscreen)
        view_menu.addAction(self.act_devtools)
        view_menu.addAction(self.act_copy_url)

    # ------------------------------------------------------------------
    # Shortcuts (direkt am Fenster) – ergänzen die Aktionen
    # ------------------------------------------------------------------
    def _install_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Q"), self, QApplication.instance().quit)
        QShortcut(QKeySequence("Ctrl+R"), self, self.reload_page)
        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen)
        QShortcut(QKeySequence("Ctrl+Shift+I"), self, self.open_devtools)
        QShortcut(QKeySequence("Ctrl+L"), self, self.copy_current_url)

        # Zoom‑Steuerung
        QShortcut(QKeySequence("Ctrl++"), self,
                  lambda: self.web_view.setZoomFactor(self.web_view.zoomFactor() + 0.1))
        QShortcut(QKeySequence("Ctrl+-"), self,
                  lambda: self.web_view.setZoomFactor(max(0.1, self.web_view.zoomFactor() - 0.1)))
        QShortcut(QKeySequence("Ctrl+0"), self,
                  lambda: self.web_view.setZoomFactor(1.0))

    # ------------------------------------------------------------------
    # Aktions‑Methoden
    # ------------------------------------------------------------------
    def reload_page(self):
        """Seite neu laden – nützlich, wenn das Login‑Formular nicht erscheint."""
        self.web_view.reload()

    def toggle_fullscreen(self):
        """Vollbild‑Modus ein‑/ausschalten."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def open_devtools(self):
        """Qt‑WebEngine‑Inspector öffnen (nur für Debugging)."""
        profile: QWebEngineProfile = self.web_view.page().profile()
        dev_tools = QWebEngineView()
        dev_tools_page = QWebEnginePage(profile, dev_tools)
        dev_tools.setPage(dev_tools_page)
        dev_tools_page.setInspectedPage(self.web_view.page())
        dev_tools.resize(1200, 800)
        dev_tools.show()

    def copy_current_url(self):
        """Aktuelle URL in die Zwischenablage kopieren."""
        url = self.web_view.url().toString()
        clipboard: QClipboard = QApplication.clipboard()
        clipboard.setText(url, mode=clipboard.Clipboard)
        QMessageBox.information(self, "URL kopiert", f"URL:\n{url}")


# ----------------------------------------------------------------------
# 4️⃣  Anwendung starten
# ----------------------------------------------------------------------
def main() -> None:
    app = QApplication(sys.argv)

    # Dark‑Theme aktivieren (Palette + Stylesheet)
    apply_lumo_dark_palette(app)
    app.setStyleSheet(DARK_FRAME_STYLESHEET)

    # Optimierung für native Widgets (wie im Original‑Script)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings, True)

    win = SinglePageWindow()
    win.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()