# Chess Tree Analyzer - Windows Launch Options

## Quick Start Options

### Option 1: C# WPF Application (Recommended for Windows)
```bash
cd ChessTreeAnalyzer
dotnet run
```
**Benefits**: Native Windows performance, professional interface, interactive chess board

### Option 2: Python GUI (Fallback)
**No Console Window:**
- Double-click `run_gui_silent.pyw`
- Or run `start_gui.bat`

**With Console (for debugging):**
- Double-click `run_gui.py`
- Or run `python run_gui.py`

## Detailed Launch Methods

### C# WPF Application
1. **Prerequisites**: .NET 8 SDK installed
2. **First Time Setup**: Run `./build_csharp.sh` to build
3. **Launch**: `cd ChessTreeAnalyzer && dotnet run`
4. **Features**: 
   - Interactive chess board visualization
   - Professional Windows interface
   - Native file dialogs
   - Real-time analysis progress

### Python Application
1. **Silent Launch** (No console popup):
   - `run_gui_silent.pyw` - Python launcher without console
   - `run_gui_windowless.py` - Alternative windowless launcher
   - `start_gui.bat` - Windows batch file
   - `start_gui_simple.bat` - Minimal batch launcher

2. **Debug Launch** (With console for troubleshooting):
   - `run_gui.py` - Standard Python launcher
   - `python chess_gui.py` - Direct module execution

## Troubleshooting

### C# Application Issues
- **"dotnet not found"**: Install .NET 8 SDK from Microsoft
- **Build errors**: Run `dotnet restore` in ChessTreeAnalyzer folder
- **Runtime errors**: Check Stockfish path in settings

### Python Application Issues
- **Import errors**: Ensure dependencies installed (`pip install python-chess psutil`)
- **Unicode errors**: Use `.pyw` launchers for clean startup
- **Stockfish not found**: Set correct path: `C:/path/to/stockfish.exe`

## Performance Comparison

| Feature | C# WPF | Python GUI |
|---------|--------|------------|
| Startup Speed | Fast | Medium |
| UI Responsiveness | Excellent | Good |
| Memory Usage | Low | Medium |
| Chess Board | Interactive | Text-based |
| Windows Integration | Native | Basic |
| Analysis Speed | Same (uses Stockfish) | Same |

## Recommended Workflow

1. **For regular use**: Use C# WPF application for best experience
2. **For debugging**: Use Python GUI with console for detailed logging
3. **For automation**: Use command-line Python script directly

## File Organization

```
Chess Tree Analyzer/
├── C# Application
│   ├── ChessTreeAnalyzer.sln
│   ├── ChessTreeAnalyzer/
│   └── build_csharp.sh
├── Python Application  
│   ├── chess_gui.py
│   ├── run_gui_silent.pyw
│   ├── start_gui.bat
│   └── core analysis modules
└── Documentation
    ├── README.md
    ├── SETUP_GUIDE.md
    └── this file
```

Both applications use the same Stockfish engine and produce identical analysis results, with the C# version providing enhanced user experience for Windows users.