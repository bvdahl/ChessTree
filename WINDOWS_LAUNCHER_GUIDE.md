# Windows Launcher Guide - Chess Tree Generator

## Problem: .pyw File Won't Run

If you get an error like "Python Launcher is sorry to say... Unable to create process", this means Windows can't find the correct Python installation to run the .pyw file.

## Solutions (in order of preference):

### Option 1: Use Batch File (Recommended)
Double-click one of these batch files:
- **`start_gui_simple.bat`** - Simple launcher (try this first)
- **`start_gui.bat`** - Advanced launcher with Python detection

These will automatically find Python and start the GUI without a console window.

### Option 2: Fix Python File Association
1. Right-click on `run_gui_silent.pyw`
2. Select "Open with" → "Choose another app"
3. Browse to your Python installation folder (usually `C:\Program Files\Python3X\`)
4. Select `pythonw.exe` (NOT `python.exe`)
5. Check "Always use this app to open .pyw files"

### Option 3: Command Line Method
1. Open Command Prompt in the Chess Tree Generator folder
2. Run: `python run_gui_silent.pyw`

### Option 4: Regular Python File
Double-click `run_gui.py` instead (may show a brief console window)

## Troubleshooting

**If batch files don't work:**
1. Make sure Python is installed and in your PATH
2. Try running from Command Prompt: `python --version`
3. If that fails, reinstall Python with "Add to PATH" option checked

**If you get import errors:**
Make sure all these files are in the same folder:
- `chess_gui.py`
- `chess_tree_generator.py` 
- `stockfish_analyzer.py`
- `tree_node.py`
- All launcher files

**If you get dependency errors:**
Install required packages:
```
pip install python-chess psutil
```

## File Descriptions

- `run_gui_silent.pyw` - Python GUI file (no console)
- `start_gui_simple.bat` - Simple batch launcher
- `start_gui.bat` - Advanced batch launcher with Python detection
- `run_gui.py` - Regular Python launcher (may show console briefly)
- `run_gui_windowless.py` - Python launcher with hidden console