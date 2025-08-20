#!/usr/bin/env python3
"""
Standalone Chess Tree Generator GUI - No external dependencies required
This version includes error handling for missing dependencies
"""

import sys
import os

def check_dependencies():
    """Check if all required dependencies are available."""
    missing = []
    
    try:
        import tkinter
    except ImportError:
        missing.append("tkinter (usually comes with Python)")
    
    try:
        import chess
    except ImportError:
        missing.append("python-chess")
    
    try:
        import psutil
    except ImportError:
        missing.append("psutil")
    
    return missing

def install_dependencies():
    """Try to install missing dependencies."""
    print("Attempting to install missing dependencies...")
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-chess", "psutil"])
        return True
    except Exception as e:
        print(f"Failed to install dependencies: {e}")
        return False

def main():
    print("Chess Tree Generator GUI")
    print("=" * 40)
    
    # Check dependencies
    missing = check_dependencies()
    
    if missing:
        print("Missing dependencies:")
        for dep in missing:
            print(f"  - {dep}")
        print()
        
        if "tkinter" in str(missing):
            print("ERROR: tkinter is required but not found.")
            print("This usually means Python was installed without tkinter.")
            print("Please reinstall Python with tkinter support.")
            input("Press Enter to exit...")
            return
        
        print("Attempting to install missing packages...")
        if install_dependencies():
            print("Dependencies installed! Please restart the application.")
            input("Press Enter to exit...")
            return
        else:
            print("Failed to install dependencies automatically.")
            print("Please install manually:")
            print("  pip install python-chess psutil")
            input("Press Enter to exit...")
            return
    
    # Try to import and run the GUI
    try:
        from chess_gui import ChessTreeGUI
        import tkinter as tk
        
        root = tk.Tk()
        app = ChessTreeGUI(root)
        
        def on_closing():
            if hasattr(app, 'is_analyzing') and app.is_analyzing:
                import tkinter.messagebox as messagebox
                if messagebox.askokcancel("Quit", "Analysis is running. Do you want to stop it and quit?"):
                    app.stop_analysis()
                    root.destroy()
            else:
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        print("Starting GUI...")
        root.mainloop()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Some dependencies may still be missing.")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"Error starting GUI: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()