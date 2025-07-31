# Chess Tree Generator GUI - Windows Setup Guide

## Problem: "pip is not recognized"

This error means Python is either not installed or not properly configured. Here's how to fix it:

## Option 1: Install Python Properly (Recommended)

1. **Download Python**:
   - Go to https://python.org/downloads/
   - Download the latest Python 3.x version

2. **Install Python with PATH**:
   - Run the installer
   - **IMPORTANT**: Check "Add Python to PATH" at the bottom
   - Click "Install Now"
   - Wait for installation to complete

3. **Verify Installation**:
   - Open a new Command Prompt (search "cmd")
   - Type: `python --version`
   - Should show Python version
   - Type: `pip --version`
   - Should show pip version

4. **Install Dependencies**:
   - Run the improved_install.bat file
   - OR manually: `pip install python-chess psutil`

## Option 2: Use Standalone Version

If you continue having Python issues, use the standalone version:

1. **Try Standalone GUI**:
   - Run: `python standalone_gui.py`
   - This version handles missing dependencies better

## Option 3: Manual Installation

If automatic installation fails:

1. **Open Command Prompt as Administrator**
2. **Navigate to the folder** containing the GUI files
3. **Install dependencies manually**:
   ```
   python -m pip install python-chess
   python -m pip install psutil
   ```

## Running the GUI

Once dependencies are installed, you can run:
- Double-click `launch_gui.bat`
- OR: `python chess_gui.py`
- OR: `python standalone_gui.py`

## Still Having Issues?

### Check if Python is installed:
```
python --version
```

### Check if pip works:
```
python -m pip --version
```

### Install packages with full path:
```
python -m pip install python-chess psutil
```

### Alternative package manager:
If pip doesn't work, try:
```
python -m ensurepip --upgrade
python -m pip install python-chess psutil
```

## GUI Features Once Running

- **File Pickers**: Browse for PGN files and Stockfish engine
- **Parameter Controls**: Spinboxes for all analysis settings
- **Side-Specific Settings**: Different moves/thresholds for White/Black
- **Saved Configurations**: Create and load named presets
- **Real-time Progress**: Live analysis output and progress
- **Persistent Settings**: Remembers paths and settings between sessions

## Stockfish Engine

Don't forget to download Stockfish:
1. Visit: https://stockfishchess.org/download/
2. Download Windows version
3. Extract stockfish.exe
4. In GUI, browse to select the engine file

The GUI will remember the engine path once set.