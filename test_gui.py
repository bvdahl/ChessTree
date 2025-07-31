#!/usr/bin/env python3
"""Simple GUI test to verify tkinter is working"""

import tkinter as tk
from tkinter import ttk

def test_gui():
    root = tk.Tk()
    root.title("GUI Test")
    root.geometry("400x300")
    
    label = ttk.Label(root, text="Chess Tree Generator GUI is working!")
    label.pack(pady=20)
    
    button = ttk.Button(root, text="Close", command=root.quit)
    button.pack(pady=10)
    
    print("GUI window created successfully")
    return root

if __name__ == "__main__":
    root = test_gui()
    root.after(5000, root.quit)  # Auto-close after 5 seconds
    root.mainloop()
    print("GUI test completed")