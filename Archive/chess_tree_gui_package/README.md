# Chess Tree Generator GUI - Local Installation

## Requirements
- Python 3.7 or higher
- Windows operating system

## Installation Steps

1. **Install Python** (if not already installed):
   - Download from https://python.org
   - Make sure to check "Add Python to PATH" during installation

2. **Install Dependencies**:
   - Double-click `install.bat`
   - OR run manually: `pip install -r requirements.txt`

3. **Run the GUI**:
   - Double-click `launch_gui.bat`
   - OR run manually: `python chess_gui.py`

## GUI Features

### Analysis Settings Tab
- **Input Options**: Choose between PGN file or FEN position
- **Engine Setup**: Browse and select your Stockfish engine executable
- **Analysis Parameters**: 
  - Depth (1-10 half-moves)
  - Time per position (0.1-60 seconds)
  - Hash memory (64-32768 MB)
- **Side-Specific Settings**:
  - White/Black move counts (1-10 moves each)
  - White/Black centipawn thresholds (10-500cp each)
- **Output Options**: Choose format (tree/json/pgn) and output file
- **Controls**: Start/Stop analysis, Save current settings

### Saved Settings Tab
- **Save Configurations**: Create named presets with all current settings
- **Load Configurations**: Quick-load previously saved settings
- **Delete Configurations**: Remove unwanted presets
- **Settings Details**: View complete configuration details

### Persistent Features
- **Automatic Path Memory**: Remembers Stockfish engine location
- **Directory Persistence**: Remembers last-used folders for files
- **Setting Persistence**: All configurations saved between sessions
- **Real-time Progress**: Live analysis output and progress tracking

## Stockfish Engine

You need to download Stockfish separately:
1. Visit: https://stockfishchess.org/download/
2. Download the Windows version
3. Extract the executable
4. In the GUI, browse to select the stockfish.exe file

## Usage Tips

1. **First Time Setup**:
   - Set your Stockfish engine path (only needed once)
   - Create and save a default configuration preset

2. **Analysis Workflow**:
   - Load a PGN file or enter FEN position
   - Adjust analysis parameters as needed
   - Click "Start Analysis" 
   - Monitor progress in real-time
   - Output saved to specified file

3. **Performance Optimization**:
   - Use fewer moves for Black if analyzing many positions
   - Increase hash memory for deeper analysis
   - Adjust time per position based on accuracy needs

## Troubleshooting

- **"No module named chess"**: Run install.bat or `pip install python-chess`
- **"Stockfish not found"**: Browse to correct engine executable path
- **Analysis fails**: Check engine path and input file validity
- **GUI doesn't start**: Ensure Python and tkinter are properly installed

## Support

For issues or questions, refer to the main project documentation.
