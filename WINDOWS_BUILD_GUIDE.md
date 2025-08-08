# Windows Build Guide for Chess Tree Analyzer

## Quick Start (If you have .NET 8 SDK installed)

1. **Extract the tar.gz file**
   - Use 7-Zip or WinRAR to extract `ChessTreeAnalyzer_Evaluation_Fix.tar.gz`
   - You'll get a folder called `ChessTreeAnalyzer`

2. **Build the application**
   - Option A: Double-click the `BUILD_AND_RUN.bat` file
   - Option B: Manual build:
     ```
     cd ChessTreeAnalyzer
     dotnet build -c Release
     ```

3. **Run the application**
   - The executable will be in: `ChessTreeAnalyzer\bin\Release\net8.0-windows\ChessTreeAnalyzer.exe`

## What Changed in This Version

### Fixed ✅
- Move application bug - moves now apply correctly
- Positions change as expected during analysis
- Tree generation works properly

### In Progress 🔧
- Evaluation values adjustment (currently showing higher than expected)
- Added logging to help diagnose the issue

## Testing the Fix

1. Load your PGN file
2. Run an analysis
3. Check the diagnostics file for:
   - Moves being applied (should show different FEN positions)
   - Raw evaluation values (will help identify the scaling issue)

## Manual Fix (If you have the previous version)

If you already have a version of the app and just want to apply the fix manually:

In `StockfishService.cs` around line 160, change:
```csharp
// OLD (wrong):
analyzedMove.Evaluation = cp;

// NEW (correct):
analyzedMove.Evaluation = position.WhiteToMove ? cp : -cp;
```

And around line 182, ensure the SimpleMove constructor has UCI first:
```csharp
// Correct order: UCI, then SAN
analyzedMove.Move = new SimpleMove(uciMove, sanMove, 0);
```

## Troubleshooting

If build fails:
- Ensure .NET 8.0 SDK is installed
- Check that all files extracted properly
- Run from an elevated command prompt if needed

The application is working correctly for move generation and tree analysis. The remaining evaluation display issue is being investigated.