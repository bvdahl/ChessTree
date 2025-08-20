# Chess Game Tree Generator

A Python command-line tool that generates chess game trees using Stockfish engine analysis with configurable depth and move filtering.

## Features

- **FEN Input**: Accept any chess position in FEN (Forsyth-Edwards Notation) format
- **Stockfish Integration**: Uses Stockfish chess engine for position analysis
- **Optimal Resource Usage**: Automatically detects system resources and configures engine with half available memory and all CPU threads
- **Deep Analysis**: Default 60-second analysis per position for thorough evaluation
- **Smart Move Filtering**: Includes top 3 moves, filtering out moves >30 centipawns worse than the best
- **Configurable Depth**: Set maximum tree depth in half-moves (default: 3)
- **Multiple Output Formats**: Human-readable tree view or JSON format
- **Complete Tree Generation**: Uses breadth-first algorithm to ensure complete coverage at each depth level

## Requirements

- Python 3.7+
- Stockfish chess engine executable (latest version recommended)
- Required Python packages:
  - python-chess
  - psutil

## Installation

1. **Download Stockfish**: Download the latest Stockfish chess engine from [https://stockfishchess.org/download/](https://stockfishchess.org/download/)

2. **Install Python dependencies**:
   ```bash
   pip install python-chess psutil
   ```

3. **Download the chess tree generator files**:
   - `chess_tree_generator.py` (main script)
   - `stockfish_analyzer.py` (engine interface)
   - `tree_node.py` (tree data structure)

## Usage

### Basic Usage (60 seconds analysis per position)

```bash
python chess_tree_generator.py --fen "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1" --stockfish-path /path/to/stockfish
