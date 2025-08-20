# Chess Tree Analyzer - Latest Version

## Current Build: ChessTreeAnalyzer_Latest.tar.gz

**Version Date:** August 20, 2025  
**File Size:** 394KB  
**Platform:** Windows x64 (.NET 8.0 required)

## What's Fixed in This Version

✅ **Knight Position Bug** - Black knight on b8 correctly preserved in PGN parsing  
✅ **Evaluation Accuracy** - Positions now evaluate correctly (~-60 to -70 cp for test position)  
✅ **Castling Notation** - Proper chess notation (O-O, O-O-O) instead of king moves (Kg1)  
✅ **Move Application** - UCI/SAN parameter ordering corrected  
✅ **Perspective Consistency** - All evaluations from White's perspective  
✅ **PGN Output Format** - Proper nested variations with evaluations as comments, matching Python version  
✅ **Multiple Analysis Support** - Can now run new analyses without restarting app, properly clears previous results  
✅ **File Loading Fix** - Improved FEN detection with case-insensitive matching and better regex pattern
✅ **UI Responsiveness** - Improved analysis startup with better logging
✅ **Chess Board Update** - Board display forces refresh when loading new positions  

## Quick Installation

1. Download `ChessTreeAnalyzer_Latest.tar.gz`
2. Extract to any folder on Windows
3. Ensure .NET 8.0 Runtime is installed
4. Configure Stockfish path when prompted
5. Run `ChessTreeAnalyzer.exe`

## Test Position Verification

The following FEN should evaluate to approximately -60 to -70 centipawns:
```
rnbqkb1r/ppp2ppp/8/4P3/8/2pP1N2/P1P3PP/R1BQKB1R w KQkq - 0 8
```

## Known Working Features

- PGN file import with correct position parsing
- Multi-variation tree generation to specified depth
- Accurate Stockfish evaluation integration
- Proper chess notation in output files
- Resource-aware engine configuration
- Interactive chess board display

## Output Formats

- PGN with variations and evaluations
- Diagnostic logs with detailed analysis
- Tree structure visualization

## Next Updates Planned

- Enhanced PGN output with more comprehensive variations
- Improved move filtering algorithms
- Database integration for opening book support

---

For full documentation, see `Archive/Documentation/`  
For source code, see `Windows_Version/ChessTreeAnalyzer/`