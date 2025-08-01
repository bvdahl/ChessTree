# Chess Tree Generator - Replit Configuration

## Overview

This is a Python command-line tool that generates chess game trees using the Stockfish chess engine. The application analyzes chess positions from FEN notation and creates comprehensive game trees with configurable depth, move filtering, and analysis parameters. It uses a modular architecture with separate components for Stockfish analysis, tree node representation, and main tree generation logic.

## User Preferences

Preferred communication style: Simple, everyday language.
Analysis preference: Deep analysis with powerful local hardware rather than cloud limitations.
Output preference: PGN format for compatibility with ChessBase and other chess software.
Workflow preference: Analyze from existing PGN files rather than starting from FEN positions.
Resource management: Requires proper Stockfish engine cleanup after each run to prevent resource consumption.
Interface preference: Windows GUI application with intuitive controls, file pickers, persistent settings, and saved configurations rather than command-line interface.

## System Architecture

The application follows a modular, object-oriented architecture with clear separation of concerns:

### Core Components
- **ChessTreeGenerator**: Main orchestrator class that coordinates tree generation
- **StockfishAnalyzer**: Wrapper for Stockfish engine integration with system optimization
- **TreeNode**: Data structure representing individual nodes in the chess game tree

### Design Pattern
- Uses composition pattern with the main generator class utilizing analyzer and node components
- Implements breadth-first search algorithm for complete tree coverage
- Resource-aware configuration automatically detecting system capabilities

## Key Components

### 1. Chess Tree Generator (`chess_tree_generator.py`)
- **Purpose**: Main entry point and orchestration logic
- **Responsibilities**: 
  - Command-line interface handling
  - Tree generation coordination
  - Output formatting (human-readable and JSON)
- **Key Features**: Configurable depth, analysis time, and move filtering

### 2. Stockfish Analyzer (`stockfish_analyzer.py`)
- **Purpose**: Interface to Stockfish chess engine
- **Responsibilities**:
  - Engine initialization with optimal system resource allocation
  - Position analysis and move evaluation
  - Memory and CPU thread management
- **Optimization**: Automatically uses half available system memory and all CPU threads

### 3. Tree Node (`tree_node.py`)
- **Purpose**: Data structure for game tree representation
- **Responsibilities**:
  - Store board positions, moves, and evaluations
  - Maintain parent-child relationships
  - Provide tree traversal utilities
- **Structure**: Contains board state, move history, evaluation scores, and depth tracking

## Data Flow

1. **Input Processing**: FEN string parsed into chess board position
2. **Engine Configuration**: Stockfish initialized with system-optimized settings
3. **Tree Generation**: Breadth-first expansion of game tree up to specified depth
4. **Move Analysis**: Each position analyzed by Stockfish with time limit
5. **Move Filtering**: Top moves selected based on evaluation thresholds
6. **Output Generation**: Tree formatted as human-readable text or JSON

### Move Selection Criteria
- Configurable number of moves per side with intelligent mate handling
- **Side-specific parameters**: Support for different thresholds and move counts for White vs Black
- **Mate detection**: When current player has forced mate (#N for White, -#N for Black), shows only that move and ends variation
- **Mate filtering**: Automatically filters moves giving opponent mate regardless of threshold
- **Centipawn filtering**: For non-mate positions, filters moves more than configurable centipawns worse than best
- Ensures diverse tactical options while maintaining quality and chess logic

## External Dependencies

### Chess Engine
- **Stockfish**: External chess engine executable required
- **Integration**: Uses python-chess library for UCI protocol communication
- **Configuration**: Engine path must be provided as command-line argument

### Python Libraries
- **python-chess**: Chess game logic, board representation, and engine communication
- **psutil**: System resource detection for optimal engine configuration
- **Standard Library**: argparse, json, os, sys for core functionality

### System Requirements
- Python 3.7+ runtime environment
- Stockfish chess engine executable
- Sufficient memory and CPU resources for analysis

## Deployment Strategy

### Local Execution
- **Primary Use**: Command-line tool for local chess analysis
- **Installation**: Simple pip install of dependencies plus Stockfish binary
- **Configuration**: Engine path and analysis parameters configurable via CLI

### Resource Management
- **Memory**: Automatically allocates 50% of available system memory to engine
- **CPU**: Utilizes all available CPU threads for analysis
- **Time**: Configurable analysis time per position (default 1 second)

### Scalability Considerations
- **Analysis Depth**: Exponential complexity requires careful depth limits
- **Memory Usage**: Large trees may require significant memory for storage
- **Processing Time**: Deep analysis can take considerable time for complex positions

The architecture prioritizes modularity, resource efficiency, and ease of use while maintaining the flexibility to handle various chess analysis scenarios.

## C# WPF Application Architecture

### Modern Windows Implementation
The C# WPF rewrite provides a professional Windows desktop application with enhanced user experience:

**Core Components:**
- **ChessTreeAnalyzer.sln**: Complete Visual Studio solution with .NET 8 framework
- **MVVM Architecture**: Models, Views, ViewModels, and Services with clear separation of concerns  
- **Interactive UI**: Professional WPF interface with native Windows controls and styling

**Key Features:**
- **Interactive Chess Board**: Visual piece representation using Unicode chess symbols
- **Analysis Tree Visualization**: Hierarchical TreeView showing analyzed variations
- **Real-time Progress Tracking**: Progress bars and status updates during analysis
- **Native File Operations**: Windows file dialogs for PGN/FEN import and analysis export
- **Professional Layout**: Resizable panels, toolbars, menus, and status bars

**Technical Stack:**
- **.NET 8**: Latest framework with performance optimizations and Windows integration
- **Chess.NET Library**: Robust chess logic, move generation, and position validation
- **WPF Framework**: Hardware-accelerated UI with modern Windows theming
- **UCI Protocol**: Standard Stockfish engine communication preserved from Python version

The C# implementation maintains full compatibility with the Python analysis engine while providing superior Windows user experience, performance, and professional appearance suitable for serious chess analysis work.

## Recent Changes

**August 1, 2025 - C# WPF APPLICATION WITH FULL FUNCTIONALITY:**
- **✅ COMPLETED: Professional Windows application**: C# WPF rewrite fully functional with native Windows experience and complete analysis functionality
- **✅ VERIFIED: Modern MVVM architecture**: Clean separation with Models, Views, ViewModels, and Services working correctly
- **✅ FUNCTIONAL: Complete chess analysis integration**: Real Stockfish engine integration, analysis settings dialogs, progress tracking, and result visualization
- **✅ BUILDS SUCCESSFULLY: All compilation errors resolved**: SimpleChessBoard implementation replaces external dependencies
- **✅ READY FOR DEPLOYMENT: Windows executable**: Can be packaged as standalone application with dotnet publish
- **✅ PRESERVED: Python codebase maintained**: All existing Python work preserved as proven analysis reference
- **✅ REAL FUNCTIONALITY: All menu items connected**: Analysis settings dialog, file operations, engine integration, and tree visualization working

**January 31, 2025 - CONSOLE & OUTPUT IMPROVEMENTS:**
- **✅ NEW: Console window elimination**: Three launcher options for silent GUI startup (run_gui.py, run_gui_windowless.py, run_gui_silent.pyw)
- **✅ NEW: Filtered output display**: Analysis shows only analysis moves, not original PGN game moves (except initial position context)
- **✅ IMPROVED: Clean analysis feedback**: Progress shows relevant moves (e.g., "8.d4 Qd5 9.Rb1") without full game history repetition
- **✅ ENHANCED: Diagnostics organization**: Automatic Diagnostics/ folder creation with timestamped detailed analysis files

**January 31, 2025 - CRITICAL FIXES APPLIED:**
- **✅ RESOLVED: Unicode encoding error**: Removed emoji characters (🔍, 📊, ⚙️) that caused Windows 'charmap' codec errors
- **✅ IMPROVED: File selection UX**: Changed from single file picker to folder + base name approach with automatic timestamping
- **✅ NEW: Output workflow**: Users select output directory once, enter base names (e.g., "Vienna"), program automatically adds timestamp (e.g., "Vienna_202507311045.pgn")
- **✅ NEW: Success feedback**: Analysis completion shows exact output file path created
- **✅ VERIFIED: Windows compatibility**: No more encoding issues, improved user workflow matching command-line behavior

**January 31, 2025 - GUI APPLICATION COMPLETE:**
- **✅ NEW: Windows GUI Application**: Complete tkinter-based GUI with intuitive interface replacing command-line usage
- **✅ NEW: Persistent Settings**: Automatic saving of Stockfish path, file directories, and custom configuration presets
- **✅ NEW: Advanced Interface**: File pickers, dropdown boxes, spinboxes, tabbed interface, and real-time analysis output
- **✅ NEW: Configuration Management**: Save/load/delete named setting presets for different analysis scenarios
- **✅ NEW: Real-time Monitoring**: Live progress updates, output streaming, and process control with start/stop functionality

**January 31, 2025 - PERFORMANCE OPTIMIZATION COMPLETE:**
- **✅ CRITICAL FIX: True side-specific move analysis**: System now analyzes only the requested number of moves per side from the start, eliminating wasted computation time
- **✅ VERIFIED: Time savings achieved**: Black positions with fewer requested moves now analyze exactly that count (e.g., 2 moves instead of analyzing 3 and filtering to 2)
- **✅ PERFORMANCE: Optimal resource usage**: No more analyzing excess moves and discarding them - direct analysis efficiency improvement

**January 30, 2025 - COMPLETE SOLUTION WITH MATE HANDLING:**
- **✅ FULLY RESOLVED: Variation depth truncation**: All variations now continue to their complete analyzed depth instead of ending as single moves
- **✅ FULLY RESOLVED: Missing diagnostics summaries**: Complete timing and statistical information now properly captured in all diagnostics files  
- **✅ FULLY RESOLVED: Infinite recursion in PGN generation**: Implemented stack-based tree building with controlled recursion depth limits
- **✅ VERIFIED: Complete tree structure**: Every analyzed position (all 169 in user's example) now properly represented in PGN with full variation continuations
- **✅ PERFORMANCE: Stable operation**: System handles depth 4+ analysis without timeouts or crashes, completing 15+ positions in 30 seconds
- **✅ NEW: Advanced mate evaluation handling**: System now properly detects and handles forced mate positions with intelligent filtering and variation termination
- **✅ NEW: Side-specific analysis parameters**: Support for different centipawn thresholds and move counts for White vs Black positions (--white-threshold, --black-threshold, --white-moves, --black-moves)

**Previous Updates:**
- **Fixed centipawn filtering for Black moves**: Algorithm now correctly filters from Black's perspective (lower values are better for Black, higher for White)
- **Added filtered move reporting**: Console output now shows exactly which moves were filtered out with evaluation scores and threshold information
- **Implemented diagnostics file capture**: All console output during analysis is automatically saved to timestamped diagnostics files (diagnostics_YYYYMMDDHHMM.txt)
- **Fixed summary statistics**: Now tracks moves AFTER filtering instead of before, providing accurate branching factor data
- **Verified filtering logic**: System correctly identifies best moves for both White (higher = better) and Black (lower = better) positions

**Previous Major Updates:**
- **Fixed PGN depth truncation**: Replaced hardcoded 3-level PGN generation with full recursive depth matching analysis depth  
- **Added timestamp functionality**: All output files now automatically include YYYYMMDDHHMM timestamp
- **Added comprehensive analysis summary**: End-of-run statistics showing start time, end time, duration, positions analyzed, and moves used after filtering
- **Removed truncation fallbacks**: System now fails with clear error instead of producing incomplete PGN output when tree is too complex
- **Verified timing behavior**: Stockfish respects time limits and reaches deep analysis (depth 25+ in 5-10 seconds with large hash tables)

**Previous Improvements:**
- Fixed critical efficiency issue: system now analyzes exactly the requested number of moves instead of analyzing 3 and filtering down
- Added configurable hash memory parameter (--hash-memory) with user-requested default of 8192MB and removed all artificial memory limits
- Created comprehensive command-line documentation with usage examples and parameter interactions
- Successfully tested deep analysis capabilities: completed depth 6 analysis with 190 positions analyzed across all depth levels