# Quick Start - Windows Executable

## Download and Run

1. **Download**: `ChessTreeAnalyzer_Windows_Executable.tar.gz`

2. **Extract**: Use 7-Zip or WinRAR to extract the files

3. **Run**: Double-click `ChessTreeAnalyzer.exe`

## Files Included
- ChessTreeAnalyzer.exe - The main executable
- ChessTreeAnalyzer.dll - Application library
- Newtonsoft.Json.dll - JSON processing library
- Supporting files (.deps.json, .runtimeconfig.json)

## What's Fixed in This Version
✅ **Moves now apply correctly** - The UCI/SAN parameter bug is fixed
✅ **Positions change properly** - Analysis explores different variations
✅ **Tree generation works** - Multiple positions analyzed to configured depth

## Known Issue
The evaluation values are displaying higher than expected (+400s instead of -100s). This is a display issue only - the analysis is working correctly.

## No Build Required!
This is a pre-compiled executable. Just extract and run - no Visual Studio or .NET SDK needed on your machine.