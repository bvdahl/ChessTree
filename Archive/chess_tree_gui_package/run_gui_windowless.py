#!/usr/bin/env python3
"""
Windowless launcher for the Chess Tree Generator GUI (no console window)
"""

import sys

if __name__ == "__main__":
    # Hide console window completely on Windows
    if sys.platform == "win32":
        import ctypes
        import ctypes.wintypes
        
        # Get console window handle
        kernel32 = ctypes.windll.kernel32
        user32 = ctypes.windll.user32
        console_window = kernel32.GetConsoleWindow()
        
        if console_window:
            # Hide the console window
            user32.ShowWindow(console_window, 0)
    
    # Import and run the GUI
    try:
        from chess_gui import main as gui_main
        gui_main()
    except Exception as e:
        # Show error dialog if GUI fails
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Chess Tree Generator", 
                           f"Error starting GUI: {e}\n\nMake sure all dependencies are installed.")
        root.destroy()
        sys.exit(1)