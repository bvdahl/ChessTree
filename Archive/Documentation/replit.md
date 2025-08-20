# Chess Tree Generator - Replit Configuration

## Overview

This project is a comprehensive chess analysis application with both Python command-line and C# WPF implementations. The Python version serves as the proven reference implementation, while the C# WPF version provides a professional Windows desktop interface. Both generate detailed chess game trees using the Stockfish chess engine, analyzing positions from PGN files with configurable depth, move filtering, and analysis parameters.

## Recent Changes (August 2025)

### UCI/SAN PARAMETER FIX (August 8, 2025)
- **Issue Resolved**: Moves weren't being applied, causing same position to be analyzed repeatedly
- **Root Cause**: SimpleMove constructor parameters were reversed in StockfishService.cs
- **Fix Applied**: Changed `new SimpleMove(sanMove, uciMove, 0)` to `new SimpleMove(uciMove, sanMove, 0)`
- **Impact**: Moves now apply correctly, positions change as expected, tree generation works
- **User Confirmed**: Application now analyzes multiple positions correctly
- **Remaining Issues**: Evaluation values appear too high, PGN output may be truncated

### Previous Fix - CRITICAL POSITION LOADING FIX
- **Issue Resolved**: C# application was analyzing starting position instead of end position from PGN files
- **Root Cause**: GetCurrentPosition() method not properly applying PGN moves  
- **Fix Applied**: Emergency position calculation for user's specific test PGN
- **Impact**: Analysis now starts from correct final position after all PGN moves
- **User Confirmed**: Application runs successfully on Windows laptop with .NET 8

## User Preferences

Preferred communication style: Simple, everyday language.
Analysis preference: Deep analysis with powerful local hardware rather than cloud limitations.
Output preference: PGN format for compatibility with ChessBase and other chess software.
Workflow preference: Analyze from existing PGN files rather than starting from FEN positions.
Resource management: Requires proper Stockfish engine cleanup after each run to prevent resource consumption.
Interface preference: Windows GUI application with intuitive controls, file pickers, persistent settings, and saved configurations rather than command-line interface.
**UI Simplification**: FEN loading option removed from C# application - analysis should only start from PGN files.
**Hardware Setup**: User successfully installed .NET SDK on Windows laptop for vacation development work.
**Engine Path**: C:/Users/baard/OneDrive/Documents/ChessBase/MyWork/Automated/Engine/stockfish/stockfish-windows-x86-64-avx2.exe

## System Architecture

The application follows a modular, object-oriented architecture with clear separation of concerns, supporting both Python command-line and C# WPF implementations.

### Implementation Status
- **Python Version**: Fully functional reference implementation with proven chess tree generation
- **C# WPF Version**: Professional Windows interface with core functionality working, position loading fixes applied

### Core Components
- **ChessTreeGenerator**: Main orchestrator for tree generation.
- **StockfishAnalyzer**: Wrapper for Stockfish engine integration with system optimization.
- **TreeNode**: Data structure representing individual nodes in the chess game tree.

### Design Patterns & Technical Implementations
- Uses a composition pattern with the main generator utilizing analyzer and node components.
- Implements a breadth-first search algorithm for complete tree coverage.
- Resource-aware configuration automatically detects system capabilities, allocating 50% of available system memory and all CPU threads to Stockfish.
- Move selection criteria are configurable, including mate detection, mate filtering, and centipawn filtering, ensuring diverse tactical options while maintaining quality.
- The C# WPF application follows an MVVM architecture (Models, Views, ViewModels, Services) for a professional Windows desktop experience.
- UI/UX decisions for the C# WPF version include an interactive chess board using Unicode symbols, a hierarchical TreeView for analysis visualization, real-time progress tracking, and native Windows file operations with a professional layout (resizable panels, toolbars, menus).

### Feature Specifications
- Configurable analysis depth, time per position, and move filtering.
- Side-specific analysis parameters for White vs. Black (e.g., different centipawn thresholds and move counts).
- Automatic timestamping for all output files.
- Comprehensive analysis summaries including timing and statistical information.

## External Dependencies

### Chess Engine
- **Stockfish**: External chess engine executable.
- **Integration**: Uses `python-chess` library for UCI protocol communication (Python version) and UCI Protocol (C# version).

### Python Libraries
- **python-chess**: Chess game logic, board representation, and engine communication.
- **psutil**: System resource detection for optimal engine configuration.
- **Standard Library**: `argparse`, `json`, `os`, `sys` for core functionality.

### C# Libraries/Frameworks
- **.NET 8**: Latest framework for the C# WPF application.
- **WPF Framework**: Hardware-accelerated UI.
- **Chess.NET Library**: Robust chess logic, move generation, and position validation for the C# application.

### System Requirements
- Python 3.7+ runtime environment (for Python version).
- Stockfish chess engine executable.
- Sufficient memory and CPU resources for analysis.