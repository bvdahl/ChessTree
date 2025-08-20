# Chess Tree Analyzer Project

## Project Structure

The project is now organized into clean, separate directories for each version:

### 📁 Windows_Version/
Contains the complete C# WPF application (ChessTreeAnalyzer)
- Full Windows desktop application with GUI
- .NET 8.0 based implementation
- Uses Stockfish engine for analysis
- Generates comprehensive chess analysis trees

### 📁 Python_Version/
Contains the Python implementation and related tools
- `chess_tree_generator.py` - Main analysis script
- `stockfish_analyzer.py` - Stockfish engine interface
- `tree_node.py` - Tree data structure
- `chess_gui.py` - Python GUI version
- `run_gui.py` - GUI launcher
- `stockfish/` - Stockfish engine directory
- `stockfish_engine` - Linux Stockfish executable

### 📁 Archive/
Historical files and documentation
- `Builds/` - Previous executable builds
- `Documentation/` - All documentation files
- `Scripts/` - Build and utility scripts
- `chess_tree_gui_package/` - Earlier GUI package

### 📁 attached_assets/
User-provided files and analysis outputs
- PGN files for testing
- Analysis results
- Diagnostic logs

## Quick Start

### For Windows Users:
1. Navigate to `Windows_Version/ChessTreeAnalyzer/`
2. Open the solution in Visual Studio or build with .NET CLI
3. Download the latest build from `Archive/Builds/ChessTreeAnalyzer_Castling_Fix.tar.gz`
4. Extract and run `ChessTreeAnalyzer.exe`

### For Python Users:
1. Navigate to `Python_Version/`
2. Install dependencies: `pip install python-chess psutil`
3. Run the GUI: `python run_gui.py`
4. Or use command line: `python chess_tree_generator.py --help`

## Latest Features

### Windows Version (C# WPF)
✅ Full PGN import/export support
✅ Interactive chess board UI
✅ Multi-variation tree analysis
✅ Correct position evaluation (fixed knight bug)
✅ Proper castling notation (O-O, O-O-O)
✅ Resource-aware Stockfish configuration
✅ Real-time analysis progress tracking

### Python Version
✅ Command-line and GUI interfaces
✅ Flexible analysis parameters
✅ JSON and text output formats
✅ Cross-platform compatibility
✅ Batch position analysis

## Requirements

### Windows Version
- Windows 10/11 (64-bit)
- .NET 8.0 Runtime
- Stockfish chess engine

### Python Version
- Python 3.7+
- python-chess library
- psutil library
- Stockfish chess engine

## Documentation

See `Archive/Documentation/` for:
- `CHESS_TREE_ANALYZER_SPECIFICATION.md` - Full technical specification
- `WINDOWS_SETUP_GUIDE.md` - Windows installation guide
- `SETUP_GUIDE.md` - Python setup instructions

## Latest Build

The most recent stable Windows build is always in the root folder:
**`ChessTreeAnalyzer_Latest.tar.gz`**

This includes:
- Fixed knight position parsing (Black knight on b8)
- Correct evaluation perspective (~-60 to -70 cp for test position)
- Proper castling notation (O-O, O-O-O)
- All previous bug fixes

See `LATEST_VERSION.md` for detailed version information.

## Version Management

- **Root Folder**: Always contains the latest stable build
- **Archive/Builds/**: Historical builds from previous iterations
- After each update, the new version replaces the root package
- Previous versions are automatically archived with timestamps