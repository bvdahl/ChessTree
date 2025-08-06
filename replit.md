# Chess Tree Generator - Replit Configuration

## Overview

This project is a Python command-line tool that generates comprehensive chess game trees using the Stockfish chess engine. It analyzes chess positions from FEN notation or PGN files, creating game trees with configurable depth, move filtering, and analysis parameters. The goal is to provide a robust, resource-efficient tool for deep chess analysis, with ambitions to evolve into a professional Windows GUI application for serious chess analysis work.

## User Preferences

Preferred communication style: Simple, everyday language.
Analysis preference: Deep analysis with powerful local hardware rather than cloud limitations.
Output preference: PGN format for compatibility with ChessBase and other chess software.
Workflow preference: Analyze from existing PGN files rather than starting from FEN positions.
Resource management: Requires proper Stockfish engine cleanup after each run to prevent resource consumption.
Interface preference: Windows GUI application with intuitive controls, file pickers, persistent settings, and saved configurations rather than command-line interface.

## System Architecture

The application follows a modular, object-oriented architecture with clear separation of concerns, designed for both command-line and GUI interfaces.

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