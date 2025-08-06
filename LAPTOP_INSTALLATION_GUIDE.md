# Chess Tree Analyzer - Laptop Installation Guide

## Prerequisites ✅
- .NET SDK (already installed on your laptop)
- Windows operating system

## Installation Steps

### 1. Download the Application
Download `ChessTreeAnalyzer-WPF-Functional.tar.gz` from your Replit workspace to your laptop.

### 2. Extract the Application
```cmd
# Create a working directory
mkdir C:\ChessAnalysis
cd C:\ChessAnalysis

# Extract the package (Windows 10/11 has built-in tar support)
tar -xzf ChessTreeAnalyzer-WPF-Functional.tar.gz
```

### 3. Install Stockfish Engine
Download Stockfish from: https://stockfishchess.org/download/
- Choose "Windows" version
- Extract to a folder like `C:\Stockfish\`
- Note the path to `stockfish.exe` (e.g., `C:\Stockfish\stockfish.exe`)

### 4. Run the Application
```cmd
cd ChessTreeAnalyzer
dotnet run --configuration Release
```

### 5. Configure Engine Path
1. Launch the application
2. Go to **Analysis → Settings**
3. Click **Browse** for Stockfish Path
4. Select your `stockfish.exe` file
5. Adjust settings for laptop performance:
   - **Hash Size**: 512 MB (instead of 8192 MB for desktop)
   - **Thread Count**: 4 (or number of CPU cores on laptop)
   - **Time per Position**: 0.5 seconds (faster for laptop)

### 6. Test Analysis
1. **File → Load FEN** and paste: `rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1`
2. **Analysis → Settings** to verify Stockfish path
3. Click **Start Analysis** (F5)
4. Should see real-time analysis output

## Laptop-Optimized Settings

For vacation laptop performance:
- **Max Depth**: 2-3 (instead of 4-6 for desktop)
- **Hash Size**: 256-512 MB (conserve RAM)
- **Thread Count**: 2-4 (match laptop CPU cores)
- **Time per Position**: 0.5-1.0 seconds (faster analysis)
- **Moves to Analyze**: 2-3 per side (reduce computation)

## Troubleshooting

**If application won't start:**
```cmd
# Verify .NET installation
dotnet --version

# Should show version 8.0 or higher
```

**If Stockfish not found:**
- Ensure path in settings points to actual `stockfish.exe`
- Try placing stockfish.exe in same folder as application

**If analysis is slow:**
- Reduce hash size to 256 MB
- Set time per position to 0.5 seconds
- Use depth 2 for quick testing

## File Locations
- **Application**: `C:\ChessAnalysis\ChessTreeAnalyzer\`
- **Stockfish**: `C:\Stockfish\stockfish.exe` (or your chosen location)
- **Analysis Results**: Saved wherever you choose via File → Save Analysis

You now have a complete professional chess analysis application running on your laptop!