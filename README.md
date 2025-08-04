# AAS Creator v1.0

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

## Future Development

Planned features for upcoming releases:
- Batch processing for multiple BSP files
- Additional MBSPC parameter customization
- Integration with popular mapping tools
- Preset configurations for different game types

---

**Download AAS Creator today and streamline your Quake 3 mapping workflow!**

*For support, bug reports, or feature requests, please [contact information or repository link]*
