# Chess Tree Generator - Replit Configuration

## Overview

This is a Python command-line tool that generates chess game trees using the Stockfish chess engine. The application analyzes chess positions from FEN notation and creates comprehensive game trees with configurable depth, move filtering, and analysis parameters. It uses a modular architecture with separate components for Stockfish analysis, tree node representation, and main tree generation logic.

## User Preferences

Preferred communication style: Simple, everyday language.
Analysis preference: Deep analysis with powerful local hardware rather than cloud limitations.
Output preference: PGN format for compatibility with ChessBase and other chess software.
Workflow preference: Analyze from existing PGN files rather than starting from FEN positions.
Resource management: Requires proper Stockfish engine cleanup after each run to prevent resource consumption.

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
- Includes top 3 moves from engine analysis
- Filters out moves more than 30 centipawns worse than best move
- Ensures diverse tactical options while maintaining quality

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

## Recent Changes

**January 30, 2025 - Major Feature Updates:**
- **Fixed PGN depth truncation**: Replaced hardcoded 3-level PGN generation with full recursive depth matching analysis depth
- **Added timestamp functionality**: All output files now automatically include YYYYMMDDHHMM timestamp (e.g., analyzed_game_202507300944.pgn)
- **Added comprehensive analysis summary**: End-of-run statistics showing start time, end time, duration, positions analyzed, total moves considered, and averages
- **Removed truncation fallbacks**: System now fails with clear error instead of producing incomplete PGN output when tree is too complex
- **Verified timing behavior**: Stockfish respects time limits and reaches deep analysis (depth 25+ in 5-10 seconds with large hash tables)

**Previous Improvements:**
- Fixed critical efficiency issue: system now analyzes exactly the requested number of moves instead of analyzing 3 and filtering down
- Added configurable hash memory parameter (--hash-memory) with user-requested default of 8192MB and removed all artificial memory limits
- Created comprehensive command-line documentation with usage examples and parameter interactions
- Successfully tested deep analysis capabilities: completed depth 6 analysis with 190 positions analyzed across all depth levels