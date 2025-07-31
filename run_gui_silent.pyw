#!/usr/bin/env python3
"""
Silent launcher for Chess Tree Generator GUI (Python .pyw file - no console)
"""

import sys

def main():
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

if __name__ == "__main__":
    main()