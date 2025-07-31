#!/usr/bin/env python3
"""
Simple launcher for the Chess Tree Generator GUI
"""

import os
import sys

def main():
    # Hide console window on Windows
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    # Import and run the GUI silently
    try:
        from chess_gui import main as gui_main
        gui_main()
    except Exception as e:
        # Only show error if GUI fails to start
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Chess Tree Generator", f"Error starting GUI: {e}\nMake sure all dependencies are installed.")
        root.destroy()

if __name__ == "__main__":
    main()