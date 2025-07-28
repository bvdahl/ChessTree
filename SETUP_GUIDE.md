# Chess Tree Generator - Setup Guide for Your PC

## Quick Start

This chess tree generator creates comprehensive game trees using Stockfish analysis. It's designed to use your full system capabilities for deep chess analysis.

## What You Need

1. **Python 3.7+** - Most modern systems have this
2. **Latest Stockfish** - Download from [stockfishchess.org](https://stockfishchess.org/download/)
3. **The three Python files** from this project:
   - `chess_tree_generator.py` (main program)
   - `stockfish_analyzer.py` (engine interface) 
   - `tree_node.py` (tree structure)

## Installation Steps

### 1. Install Python Dependencies
```bash
pip install python-chess psutil
```

### 2. Download Stockfish
- Go to [https://stockfishchess.org/download/](https://stockfishchess.org/download/)
- Download the version for your operating system
- Extract it to a folder (remember the path)

### 3. Test the Setup
```bash
# Basic test with starting position after 1.e4
python chess_tree_generator.py --fen "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1" --stockfish-path /path/to/your/stockfish
```

## Usage Examples

### Quick Analysis (5 seconds per position)
```bash
python chess_tree_generator.py --fen "your_position_here" --stockfish-path /path/to/stockfish --time 5
```

### Deep Analysis (full 60 seconds per position) 
```bash
python chess_tree_generator.py --fen "your_position_here" --stockfish-path /path/to/stockfish
```

### Save Results to File
```bash
python chess_tree_generator.py --fen "your_position_here" --stockfish-path /path/to/stockfish --output json --output-file results.json
```

### Deeper Tree (5 half-moves)
```bash
python chess_tree_generator.py --fen "your_position_here" --stockfish-path /path/to/stockfish --depth 5
```

## What the Tool Does

1. **Detects your system**: Automatically finds your CPU cores and RAM
2. **Optimizes Stockfish**: Uses all your CPU cores and up to half your RAM
3. **Deep analysis**: Spends 60 seconds analyzing each position (configurable)
4. **Smart filtering**: Only includes the best 3 moves, filtering out clearly bad ones
5. **Complete trees**: Uses breadth-first search to build complete game trees

## Expected Performance

With your powerful PC setup:
- **Analysis quality**: Much better than online tools due to longer analysis time
- **Speed**: Faster than cloud environments due to local processing
- **Memory**: Can handle deeper analysis with more RAM
- **CPU**: All cores working simultaneously for maximum strength

## Command Options

- `--fen`: Chess position in FEN format (required)
- `--stockfish-path`: Path to your Stockfish executable (required)
- `--depth`: How many half-moves deep (default: 3)
- `--time`: Seconds to analyze each position (default: 60)
- `--threshold`: How close moves must be to the best (default: 30 centipawns)
- `--output`: Format - 'tree' (readable) or 'json' (data)
- `--output-file`: Save to file instead of displaying

## Troubleshooting

**"Stockfish not found"**: Check the path to your Stockfish executable
**Very slow**: Deep analysis takes time - this is normal for thorough evaluation
**Memory warnings**: The tool manages memory automatically
**Permission errors**: Make sure Stockfish executable has run permissions

## Example Output

```
Detected 16 CPU threads
Detected 32768MB total RAM, allocating 1024MB for hash table
Generating game tree from FEN: rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1
Max depth: 3 half-moves
Analysis time: 60.0 seconds per position
Centipawn threshold: 30
==================================================
Starting position (FEN: rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1)
  e7e5 (eval: 25)
    g1f3 (eval: 15)
      b8c6 (eval: 20)
    b1c3 (eval: 20)
    d2d4 (eval: 30)
  c7c5 (eval: 15)
    g1f3 (eval: 10)
    b1c3 (eval: 12)
```

Your PC will deliver much more detailed and accurate analysis than what's possible in cloud environments!