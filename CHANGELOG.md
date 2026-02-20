# AAS Creator – Changelog

All notable changes to this project are documented here.  
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.1.2] – 2026-02-20

### Added
- **Config-Persistenz** – alle Pfade (BSP, mbspc, Output-Dir, AAS-Validation) werden beim Schließen automatisch in `aas_creator.cfg` gespeichert und beim nächsten Start wiederhergestellt
  - Format: INI-Datei (`configparser`), Sektion `[paths]`
  - Pfade werden nur wiederhergestellt wenn sie noch existieren (kein Fehler bei verschobenen Dateien)
  - Config wird auch nach erfolgreichem Compile gespeichert, nicht nur beim Beenden
- **Drag & Drop** – BSP-Dateien können direkt auf das BSP-Eingabefeld gezogen werden
  - Erfordert `tkinterdnd2` (`pip install tkinterdnd2`)
  - Wenn `tkinterdnd2` nicht installiert ist: graceful fallback mit Hinweistext, keine Fehler
  - Validierung beim Drop: nur `.bsp`-Dateien akzeptiert, Warnung bei anderem Dateityp
  - Output-Directory wird automatisch gefüllt wenn noch leer

### Changed
- `find_mbspc()` überschreibt jetzt keinen bereits aus der Config geladenen Pfad mehr
- `WM_DELETE_WINDOW`-Handler gesetzt: Fenster schließen löst nun `_save_paths()` aus
- `main()` verwendet `TkinterDnD.Tk()` wenn verfügbar, sonst Standard `tk.Tk()`

---

## [1.1.1] – 2026-02-20

### Fixed
- AAS magic bytes korrigiert: `AASF` → `EAAS` (Q3Rally-spezifisches Format)
- Fehlermeldung im Validator aktualisiert, zeigt jetzt `expected b'EAAS'`

---

## [1.1.0] – 2026-02-20

### Added
- **BSP Info Tab** – automatic parsing of Quake III BSP files (version 46) directly from binary, no external tool required
  - Summary panel: Map Name, File Size, Brush/Face/Vertex counts, Texture count, Entity count
  - Entity table: classname, targetname, origin – scrollable Treeview
  - Texture list: full texture path list, scrollable with horizontal scroll support
  - Auto-refresh on BSP file selection
- **AAS Validation Tab** – post-compile validation of generated AAS files
  - Checks: file exists, size > 0, AAS magic bytes (`AASF`)
  - Color-coded indicators (✔ OK / ✘ FAIL)
  - Error/notes log
  - Auto-filled with output path after successful compile
- **Version display** – version string shown in window title and as label in UI
- **Version constant** `VERSION` at top of source file for easy updates

### Changed
- Window title updated to `AAS Creator – Q3Rally  v1.1.0`
- After successful AAS compile: AAS Validation tab is now auto-filled with the output path
- UI restructured into a `ttk.Notebook` with three tabs (Create AAS / BSP Info / AAS Validation)

---

## [1.0.0] – initial release

### Added
- Basic GUI (tkinter) for running `mbspc.exe` to convert BSP → AAS
- BSP file, MBSPC compiler, and output directory selection
- Real-time log output from mbspc process (separate thread)
- Indeterminate progress bar during compile
- Auto-detection of mbspc.exe at common install paths
- Auto-fill of output directory from BSP file location
- Status bar
