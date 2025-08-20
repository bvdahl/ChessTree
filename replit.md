# Overview

Chess Tree Generator is a desktop application that performs deep chess position analysis using the Stockfish engine. The application generates comprehensive game trees from chess positions, exploring multiple variations at configurable depths. It supports both command-line operation and a GUI interface, with the ability to import PGN files or analyze specific FEN positions. The tool is designed for chess players and analysts who need to explore positions in depth and export results in standard formats compatible with ChessBase and other chess software.

## Version Management
- Latest stable build always in root: `ChessTreeAnalyzer_Latest.tar.gz`
- Previous versions archived in `Archive/Builds/`
- Version details documented in `LATEST_VERSION.md`
- After each iteration: old files → Archive, new build → root

## Recent Achievements (August 20, 2025)
- ✅ PGN output format completely fixed - proper nested variations with evaluations
- ✅ All core functionality working: position analysis, evaluations, move notation
- ✅ Output matches Python version's format exactly
- ✅ Compatible with ChessBase and standard chess software

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Project Organization

The project is now organized into two separate implementations:

**Windows_Version/**: Complete C# WPF desktop application
- ChessTreeAnalyzer project with full GUI
- .NET 8.0 based implementation
- Professional Windows desktop interface

**Python_Version/**: Python implementation with command-line and GUI options
- chess_tree_generator.py - Main analysis engine
- stockfish_analyzer.py - Stockfish interface
- chess_gui.py - Tkinter GUI
- Cross-platform compatibility

## Core Components

**Chess Analysis Engine**: The main analysis system orchestrates position analysis using Stockfish. Both implementations use a tree-based data structure to represent chess variations hierarchically, with each node containing a chess position, the move that led to it, and engine evaluation.

**Stockfish Integration**: Manages UCI protocol communication with the Stockfish engine. Handles engine configuration including hash memory allocation, thread count optimization based on system resources, and multi-PV analysis for generating multiple move candidates per position.

**GUI Applications**: 
- C# WPF: Professional Windows desktop interface with interactive chess board
- Python Tkinter: Cross-platform GUI with analysis parameter configuration

## Data Processing Pipeline

**Input Processing**: The system accepts either PGN files (extracting positions from games) or direct FEN notation for single position analysis. The chess library handles move validation and board state management throughout the analysis process.

**Analysis Configuration**: Configurable parameters include analysis depth (half-moves), time per position, move count per side, and centipawn thresholds for move filtering. Different thresholds can be set for White and Black positions to accommodate playing style differences.

**Tree Generation**: The analysis proceeds depth-first, analyzing the best moves from each position and recursively building the game tree. Move filtering is applied based on centipawn thresholds to focus on the most relevant variations.

## Performance Optimization

**System Resource Management**: The application automatically detects CPU core count and available RAM to optimize Stockfish configuration. Hash table memory is allocated based on system capacity, and thread count is set to match available CPU cores.

**Memory Management**: The tree structure is built incrementally to manage memory usage during deep analysis. The system includes progress tracking and the ability to stop analysis mid-process without losing partial results.

## Output Generation

**Multiple Export Formats**: Results can be exported as formatted text trees (showing move sequences with evaluations), JSON data (for programmatic processing), or PGN format (compatible with chess databases). The PGN output includes all analyzed variations as alternative lines.

**Diagnostic Logging**: Comprehensive logging captures analysis progress, engine communication, and timing information for debugging and performance analysis.

# External Dependencies

**Stockfish Chess Engine**: Requires separate Stockfish executable for position analysis. The application communicates with Stockfish via UCI protocol, supporting various Stockfish versions and configurations.

**Python Chess Library**: Uses python-chess for chess position representation, move validation, PGN parsing, and UCI engine communication. This library handles all chess-specific logic and notation conversions.

**System Libraries**: Depends on psutil for system resource detection (CPU cores, memory) to optimize engine configuration. Tkinter is used for the GUI interface and comes with Python standard library.

**File System Integration**: Reads PGN files for position import and writes various output formats. Settings persistence uses JSON format for configuration storage between sessions.