# AAS Creator v1.1.2

**A simple and efficient tool for creating AAS files for Quake 3 based maps**

## Overview

AAS Creator is a user-friendly Python application that streamlines the process of generating AAS (Area Awareness System) files from BSP files for Quake 3 based games and mods. The tool provides a clean graphical interface that makes bot navigation file creation accessible to both beginners and experienced mappers.

## Features

### Core Functionality
- **BSP to AAS Conversion** - Convert your compiled BSP files to AAS bot navigation files
- **MBSPC Integration** - Seamless integration with the MBSPC compiler
- **Optimized Output** - Uses advanced parameters for optimal AAS file generation
- **Real-time Logging** - Monitor the compilation process with detailed output logs

### User Interface
- **Landscape Layout** - Optimized widescreen interface for better workflow
- **File Browser Integration** - Easy file selection with native dialog boxes
- **Progress Indication** - Visual feedback during AAS generation
- **Status Updates** - Clear status messages and success/error notifications

### Advanced Options
- **Automatic Compiler Detection** - Finds MBSPC automatically in common locations
- **Flexible Output Control** - Choose custom output directories or use BSP location
- **Comprehensive Logging** - Detailed process logs for troubleshooting
- **One-Click Operation** - Simple workflow from BSP selection to AAS creation

## Technical Specifications

### Compilation Parameters
The tool uses optimized MBSPC parameters for professional-quality AAS files:
```
mbspc.exe -bsp2aas -forcesidesvisible -optimize -reach [bsp-file]
```

### System Requirements
- **Python 3.6+** (Python 3.8+ recommended)
- **Windows 7/8/10/11** (primary platform)
- **MBSPC Compiler** (included with most Q3 mapping tools)
- **Tkinter** (included with standard Python installation)

### Cross-Platform Compatibility
- **Windows** - Full native support
- **Linux/macOS** - Python GUI compatible (requires MBSPC for Linux/macOS or Wine)

## Installation & Usage

### Quick Start
1. Ensure Python 3.6+ is installed on your system
2. Download and run the `aas_creator.py` file
3. Select your BSP file using the browse button
4. Specify the MBSPC compiler location (auto-detected if available)
5. Choose output directory (optional - defaults to BSP location)
6. Click "Create AAS File" to generate your bot navigation file

### No Dependencies Required
The tool uses only Python standard libraries - no additional packages needed!

## Why Choose AAS Creator?

### For Beginners
- **No Command Line Knowledge Required** - Simple point-and-click interface
- **Automatic Parameter Optimization** - Professional settings applied automatically
- **Clear Error Messages** - Helpful feedback when issues occur
- **Visual Progress Tracking** - Know exactly what's happening during compilation

### For Experienced Mappers
- **Streamlined Workflow** - Faster than manual command-line compilation
- **Batch Processing Ready** - Easy to integrate into mapping pipelines
- **Comprehensive Logging** - Detailed output for debugging complex maps
- **Reliable Results** - Uses proven MBSPC parameters for optimal AAS quality

## Target Audience

Perfect for:
- **Quake 3 Map Developers** - Creating bot navigation for custom maps
- **Game Modders** - Working with Q3-engine based games (Urban Terror, OpenArena, etc.)
- **Server Administrators** - Preparing maps with proper bot support
- **Mapping Communities** - Sharing an easy-to-use AAS creation tool

## Release Information

- **Version:** 1.0
- **Release Date:** August 2025
- **License:** MIT License
- **Platform:** Cross-platform (Windows primary)
- **Language:** Python 3.6+

## License

This project is licensed under the MIT License

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

---

**Download AAS Creator today and streamline your Quake 3 mapping workflow!**

*For support, bug reports, or feature requests, please [contact information or repository link]*
