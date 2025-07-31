#!/usr/bin/env python3
"""
Simple launcher for the Chess Tree Generator GUI
"""

import os
import sys

def main():
    print("=" * 60)
    print("Chess Tree Generator GUI")
    print("=" * 60)
    print()
    print("Starting the GUI application...")
    print("The GUI window should appear shortly.")
    print()
    print("Features:")
    print("- File pickers for PGN files and Stockfish engine")
    print("- All analysis parameters with intuitive controls")
    print("- Save/load configuration presets")
    print("- Real-time analysis progress")
    print("- Persistent settings between sessions")
    print()
    
    # Import and run the GUI
    try:
        from chess_gui import main as gui_main
        gui_main()
    except Exception as e:
        print(f"Error starting GUI: {e}")
        print("Make sure all dependencies are installed.")

if __name__ == "__main__":
    main()