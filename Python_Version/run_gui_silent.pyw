#!/usr/bin/env python3
"""
Silent launcher for Chess Tree Generator GUI (Python .pyw file - no console)
"""

import sys
import os

def main():
    try:
        # Add current directory to Python path to ensure imports work
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
        
        # Import and run the GUI
        from chess_gui import main as gui_main
        gui_main()
    except ImportError as e:
        # Show specific import error
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Chess Tree Generator - Import Error", 
                           f"Could not import required modules: {e}\n\n"
                           f"Make sure chess_gui.py is in the same folder as this file.\n"
                           f"Current directory: {os.getcwd()}")
        root.destroy()
        sys.exit(1)
    except Exception as e:
        # Show general error dialog
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Chess Tree Generator", 
                           f"Error starting GUI: {e}\n\n"
                           f"Make sure all dependencies are installed:\n"
                           f"- python-chess\n"
                           f"- psutil\n"
                           f"- tkinter (usually included with Python)")
        root.destroy()
        sys.exit(1)

if __name__ == "__main__":
    main()