# Chess Tree Analyzer - Windows Setup Guide

## Overview

This guide covers setting up the Chess Tree Analyzer on Windows systems, with both the enhanced C# WPF application and the proven Python implementation.

## Option 1: C# WPF Application (Recommended)

### Prerequisites
1. **Windows 10 or later** (required for WPF)
2. **.NET 8 SDK** - Download from [Microsoft .NET](https://dotnet.microsoft.com/download)
3. **Stockfish Engine** - Download from [Stockfish website](https://stockfishchess.org/download/)

### Installation Steps

#### 1. Install .NET 8 SDK
- Download and install the .NET 8 SDK for Windows
- Verify installation: Open Command Prompt and run `dotnet --version`
- You should see version 8.0.x

#### 2. Set Up Stockfish
- Download Stockfish for Windows (stockfish-windows-x86-64-avx2.exe)
- Place it in a permanent location (e.g., `C:\Tools\Stockfish\`)
- Note the full path for later configuration

#### 3. Build the Application
```cmd
cd ChessTreeAnalyzer
dotnet restore
dotnet build --configuration Release
```

#### 4. Run the Application
```cmd
dotnet run --configuration Release
```

### First-Time Configuration
1. **Set Stockfish Path**: In the application, go to Analysis → Engine Settings
2. **Browse to Stockfish**: Select your stockfish.exe file
3. **Test Connection**: Click "Test Engine" to verify communication

## Option 2: Python Application (Fallback/Development)

### Prerequisites
1. **Python 3.8+** - Download from [python.org](https://python.org)
2. **Python Chess Library**: `pip install python-chess psutil`
3. **Stockfish Engine** (same as above)

### Quick Start
1. **Silent Launch** (no console window):
   ```cmd
   run_gui_silent.pyw
   ```
   Or double-click the file in Windows Explorer

2. **Debug Launch** (with console for troubleshooting):
   ```cmd
   python run_gui.py
   ```

### Configuration
- Use the Settings tab in the Python GUI
- Set Stockfish path: `C:\path\to\stockfish.exe`
- Configure analysis parameters as needed

## Recommended Workflow

### For Regular Chess Analysis
1. **Use C# WPF Application**:
   - Superior user interface
   - Interactive chess board
   - Native Windows integration
   - Better performance

### For Development/Debugging
1. **Use Python Application**:
   - Console output for debugging
   - Easier to modify and test
   - Proven stable implementation

## Advanced Setup

### Building Windows Installer
```cmd
cd ChessTreeAnalyzer
dotnet publish --configuration Release --self-contained true --runtime win-x64
```
This creates a standalone executable that doesn't require .NET to be installed separately.

### Professional Deployment
- The C# application can be packaged as an MSI installer
- Include Stockfish engine in the installer package
- Set up file associations for .pgn files
- Add desktop shortcuts and start menu entries

## Troubleshooting

### C# Application Issues

**"The application failed to start"**
- Ensure .NET 8 is installed
- Try running from command prompt to see error messages
- Check Windows Event Viewer for detailed errors

**"Engine not found"**
- Verify Stockfish path in settings
- Ensure you have the Windows version of Stockfish
- Test Stockfish manually: `stockfish.exe` should start UCI mode

**Performance Issues**
- Increase hash memory in engine settings
- Reduce analysis depth for faster results
- Close other applications to free up memory

### Python Application Issues

**"Module not found" errors**
- Install dependencies: `pip install python-chess psutil`
- Use virtual environment if you have Python conflicts
- Try Python 3.11 if you have compatibility issues

**Unicode display problems**
- Use `.pyw` launchers instead of `.py`
- Update Windows Console to support Unicode
- Switch to C# application for better Unicode support

**Slow analysis**
- Same Stockfish configuration applies
- Check system resources (CPU, memory)
- Reduce analysis time per position

## Performance Comparison

| Feature | C# WPF | Python GUI |
|---------|--------|------------|
| Startup Time | 2-3 seconds | 3-5 seconds |
| Memory Usage | 50-100 MB | 80-150 MB |
| UI Responsiveness | Excellent | Good |
| Chess Board Display | Interactive | Text-based |
| File Operations | Native dialogs | Basic dialogs |
| Error Handling | Professional | Functional |

## File Organization

After setup, your directory should look like:
```
Chess Tree Analyzer/
├── ChessTreeAnalyzer/           # C# WPF Application
│   ├── ChessTreeAnalyzer.sln
│   ├── ChessTreeAnalyzer/
│   ├── bin/Release/             # Built executable
│   └── README.md
├── Python GUI/                  # Python Application  
│   ├── chess_gui.py
│   ├── run_gui_silent.pyw
│   ├── start_gui.bat
│   └── analysis modules
├── Documentation/
│   ├── SETUP_GUIDE.md
│   ├── WINDOWS_SETUP_GUIDE.md
│   └── MIGRATION_SUMMARY.md
└── Stockfish/
    └── stockfish.exe            # Engine executable
```

## Support and Updates

- **C# Application**: Modern, actively developed, recommended for new users
- **Python Application**: Stable, proven, good for advanced users and debugging
- **Analysis Engine**: Both use identical Stockfish configuration and produce the same results

Choose the version that best fits your needs - both provide powerful chess analysis capabilities with the proven algorithms developed and refined through extensive testing.