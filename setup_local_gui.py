#!/usr/bin/env python3
"""
Setup script to create a local Windows installation of the Chess Tree Generator GUI
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_local_package():
    """Create a local package with all necessary files."""
    
    print("Creating Chess Tree Generator GUI package for local installation...")
    
    # Create package directory
    package_dir = Path("chess_tree_gui_package")
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    
    # Files to include
    files_to_copy = [
        "chess_gui.py",
        "chess_tree_generator.py", 
        "stockfish_analyzer.py",
        "tree_node.py",
        "run_gui.py"
    ]
    
    # Copy core files
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, package_dir / file_name)
            print(f"✓ Copied {file_name}")
    
    # Create requirements.txt
    requirements_content = """python-chess>=1.999
psutil>=5.0.0
"""
    
    with open(package_dir / "requirements.txt", "w") as f:
        f.write(requirements_content)
    print("✓ Created requirements.txt")
    
    # Create installation script for Windows
    install_script = """@echo off
echo ================================================
echo Chess Tree Generator GUI - Windows Installation
echo ================================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

echo.
echo Installation complete!
echo.
echo To run the GUI:
echo   python chess_gui.py
echo.
echo Or use the launcher:
echo   python run_gui.py
echo.
pause
"""
    
    with open(package_dir / "install.bat", "w") as f:
        f.write(install_script)
    print("✓ Created install.bat")
    
    # Create launcher script for Windows
    launcher_script = """@echo off
echo Starting Chess Tree Generator GUI...
python chess_gui.py
pause
"""
    
    with open(package_dir / "launch_gui.bat", "w") as f:
        f.write(launcher_script)
    print("✓ Created launch_gui.bat")
    
    # Create README for local installation
    readme_content = """# Chess Tree Generator GUI - Local Installation

## Requirements
- Python 3.7 or higher
- Windows operating system

## Installation Steps

1. **Install Python** (if not already installed):
   - Download from https://python.org
   - Make sure to check "Add Python to PATH" during installation

2. **Install Dependencies**:
   - Double-click `install.bat`
   - OR run manually: `pip install -r requirements.txt`

3. **Run the GUI**:
   - Double-click `launch_gui.bat`
   - OR run manually: `python chess_gui.py`

## GUI Features

### Analysis Settings Tab
- **Input Options**: Choose between PGN file or FEN position
- **Engine Setup**: Browse and select your Stockfish engine executable
- **Analysis Parameters**: 
  - Depth (1-10 half-moves)
  - Time per position (0.1-60 seconds)
  - Hash memory (64-32768 MB)
- **Side-Specific Settings**:
  - White/Black move counts (1-10 moves each)
  - White/Black centipawn thresholds (10-500cp each)
- **Output Options**: Choose format (tree/json/pgn) and output file
- **Controls**: Start/Stop analysis, Save current settings

### Saved Settings Tab
- **Save Configurations**: Create named presets with all current settings
- **Load Configurations**: Quick-load previously saved settings
- **Delete Configurations**: Remove unwanted presets
- **Settings Details**: View complete configuration details

### Persistent Features
- **Automatic Path Memory**: Remembers Stockfish engine location
- **Directory Persistence**: Remembers last-used folders for files
- **Setting Persistence**: All configurations saved between sessions
- **Real-time Progress**: Live analysis output and progress tracking

## Stockfish Engine

You need to download Stockfish separately:
1. Visit: https://stockfishchess.org/download/
2. Download the Windows version
3. Extract the executable
4. In the GUI, browse to select the stockfish.exe file

## Usage Tips

1. **First Time Setup**:
   - Set your Stockfish engine path (only needed once)
   - Create and save a default configuration preset

2. **Analysis Workflow**:
   - Load a PGN file or enter FEN position
   - Adjust analysis parameters as needed
   - Click "Start Analysis" 
   - Monitor progress in real-time
   - Output saved to specified file

3. **Performance Optimization**:
   - Use fewer moves for Black if analyzing many positions
   - Increase hash memory for deeper analysis
   - Adjust time per position based on accuracy needs

## Troubleshooting

- **"No module named chess"**: Run install.bat or `pip install python-chess`
- **"Stockfish not found"**: Browse to correct engine executable path
- **Analysis fails**: Check engine path and input file validity
- **GUI doesn't start**: Ensure Python and tkinter are properly installed

## Support

For issues or questions, refer to the main project documentation.
"""
    
    with open(package_dir / "README.md", "w") as f:
        f.write(readme_content)
    print("✓ Created README.md")
    
    # Create zip file for easy distribution
    zip_path = "chess_tree_gui_windows.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(package_dir.parent)
                zipf.write(file_path, arcname)
    
    print(f"✓ Created {zip_path}")
    print()
    print("=" * 60)
    print("LOCAL INSTALLATION PACKAGE READY!")
    print("=" * 60)
    print(f"📦 Package location: {package_dir.absolute()}")
    print(f"📦 Zip file: {Path(zip_path).absolute()}")
    print()
    print("To install on your Windows machine:")
    print("1. Download the zip file")
    print("2. Extract to a folder")
    print("3. Run install.bat")
    print("4. Run launch_gui.bat")
    print()
    print("The GUI will have all the features:")
    print("- File pickers for easy file selection")
    print("- Dropdown boxes and spinboxes for parameters")
    print("- Save/load configuration presets")
    print("- Persistent settings between sessions")
    print("- Real-time analysis progress")

if __name__ == "__main__":
    create_local_package()