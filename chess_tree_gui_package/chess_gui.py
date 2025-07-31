#!/usr/bin/env python3
"""
Chess Tree Generator GUI Application

A Windows GUI application for the chess tree generator with persistent settings
and intuitive controls for all analysis parameters.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import tkinter.simpledialog
import json
import os
import sys
import threading
from datetime import datetime
from pathlib import Path
import subprocess
from typing import Dict, Any

class ChessTreeGUI:
    """Main GUI application for Chess Tree Generator."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Tree Generator")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Settings file path
        self.settings_file = "chess_gui_settings.json"
        self.settings = self.load_settings()
        
        # Analysis process tracking
        self.analysis_process = None
        self.is_analyzing = False
        
        self.create_widgets()
        self.load_saved_settings()
        
    def create_widgets(self):
        """Create and layout all GUI widgets."""
        
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main Analysis Tab
        main_frame = ttk.Frame(notebook)
        notebook.add(main_frame, text="Analysis Settings")
        
        # Settings Management Tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Saved Settings")
        
        # Create main analysis interface
        self.create_main_interface(main_frame)
        
        # Create settings management interface
        self.create_settings_interface(settings_frame)
        
    def create_main_interface(self, parent):
        """Create the main analysis interface."""
        
        # Input Section
        input_frame = ttk.LabelFrame(parent, text="Input", padding=10)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Input type selection
        self.input_type = tk.StringVar(value="pgn")
        ttk.Radiobutton(input_frame, text="PGN File", variable=self.input_type, 
                       value="pgn", command=self.on_input_type_change).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(input_frame, text="FEN Position", variable=self.input_type, 
                       value="fen", command=self.on_input_type_change).grid(row=0, column=1, sticky=tk.W)
        
        # PGN file selection
        self.pgn_frame = ttk.Frame(input_frame)
        self.pgn_frame.grid(row=1, column=0, columnspan=3, sticky=tk.EW, pady=5)
        
        ttk.Label(self.pgn_frame, text="PGN File:").pack(side=tk.LEFT)
        self.pgn_file_var = tk.StringVar()
        self.pgn_entry = ttk.Entry(self.pgn_frame, textvariable=self.pgn_file_var, width=50)
        self.pgn_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(self.pgn_frame, text="Browse", command=self.browse_pgn_file).pack(side=tk.RIGHT)
        
        # FEN input
        self.fen_frame = ttk.Frame(input_frame)
        self.fen_frame.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=5)
        
        ttk.Label(self.fen_frame, text="FEN Position:").pack(side=tk.LEFT)
        self.fen_var = tk.StringVar()
        self.fen_entry = ttk.Entry(self.fen_frame, textvariable=self.fen_var, width=60)
        self.fen_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        input_frame.columnconfigure(2, weight=1)
        
        # Engine Section
        engine_frame = ttk.LabelFrame(parent, text="Stockfish Engine", padding=10)
        engine_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(engine_frame, text="Engine Path:").grid(row=0, column=0, sticky=tk.W)
        self.engine_path_var = tk.StringVar()
        self.engine_entry = ttk.Entry(engine_frame, textvariable=self.engine_path_var, width=50)
        self.engine_entry.grid(row=0, column=1, sticky=tk.EW, padx=5)
        ttk.Button(engine_frame, text="Browse", command=self.browse_engine_path).grid(row=0, column=2)
        
        engine_frame.columnconfigure(1, weight=1)
        
        # Analysis Parameters Section
        params_frame = ttk.LabelFrame(parent, text="Analysis Parameters", padding=10)
        params_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Basic parameters
        basic_frame = ttk.Frame(params_frame)
        basic_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(basic_frame, text="Depth:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.depth_var = tk.IntVar(value=3)
        depth_spin = ttk.Spinbox(basic_frame, from_=1, to=10, textvariable=self.depth_var, width=5)
        depth_spin.grid(row=0, column=1, padx=5)
        
        ttk.Label(basic_frame, text="Time per position (s):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.time_var = tk.DoubleVar(value=5.0)
        time_spin = ttk.Spinbox(basic_frame, from_=0.1, to=60.0, increment=0.5, textvariable=self.time_var, width=8)
        time_spin.grid(row=0, column=3, padx=5)
        
        ttk.Label(basic_frame, text="Hash Memory (MB):").grid(row=0, column=4, sticky=tk.W, padx=5)
        self.hash_var = tk.IntVar(value=8192)
        hash_spin = ttk.Spinbox(basic_frame, from_=64, to=32768, increment=1024, textvariable=self.hash_var, width=8)
        hash_spin.grid(row=0, column=5, padx=5)
        
        # Side-specific parameters
        side_frame = ttk.LabelFrame(params_frame, text="Side-Specific Settings", padding=5)
        side_frame.pack(fill=tk.X, pady=5)
        
        # White settings
        white_frame = ttk.Frame(side_frame)
        white_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(white_frame, text="White - Moves:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.white_moves_var = tk.IntVar(value=3)
        ttk.Spinbox(white_frame, from_=1, to=10, textvariable=self.white_moves_var, width=5).grid(row=0, column=1, padx=5)
        
        ttk.Label(white_frame, text="Threshold (cp):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.white_threshold_var = tk.IntVar(value=50)
        ttk.Spinbox(white_frame, from_=10, to=500, increment=10, textvariable=self.white_threshold_var, width=8).grid(row=0, column=3, padx=5)
        
        # Black settings
        black_frame = ttk.Frame(side_frame)
        black_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(black_frame, text="Black - Moves:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.black_moves_var = tk.IntVar(value=3)
        ttk.Spinbox(black_frame, from_=1, to=10, textvariable=self.black_moves_var, width=5).grid(row=0, column=1, padx=5)
        
        ttk.Label(black_frame, text="Threshold (cp):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.black_threshold_var = tk.IntVar(value=50)
        ttk.Spinbox(black_frame, from_=10, to=500, increment=10, textvariable=self.black_threshold_var, width=8).grid(row=0, column=3, padx=5)
        
        # Output Section
        output_frame = ttk.LabelFrame(parent, text="Output", padding=10)
        output_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Output format
        ttk.Label(output_frame, text="Format:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.output_format_var = tk.StringVar(value="pgn")
        format_combo = ttk.Combobox(output_frame, textvariable=self.output_format_var, 
                                   values=["tree", "json", "pgn"], state="readonly")
        format_combo.grid(row=0, column=1, padx=5)
        
        # Output file
        ttk.Label(output_frame, text="Output File:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.output_file_var = tk.StringVar()
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_file_var, width=50)
        self.output_entry.grid(row=1, column=1, columnspan=2, sticky=tk.EW, padx=5)
        ttk.Button(output_frame, text="Browse", command=self.browse_output_file).grid(row=1, column=3, padx=5)
        
        output_frame.columnconfigure(2, weight=1)
        
        # Control buttons
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=5, pady=10)
        
        self.analyze_button = ttk.Button(control_frame, text="Start Analysis", command=self.start_analysis)
        self.analyze_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Analysis", command=self.stop_analysis, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="Save Current Settings", command=self.save_current_settings).pack(side=tk.RIGHT, padx=5)
        
        # Progress and output
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding=10)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(progress_frame, textvariable=self.progress_var).pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Output text area
        self.output_text = scrolledtext.ScrolledText(progress_frame, height=8, wrap=tk.WORD)
        self.output_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Initialize input type visibility
        self.on_input_type_change()
        
    def create_settings_interface(self, parent):
        """Create the settings management interface."""
        
        settings_control_frame = ttk.Frame(parent)
        settings_control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(settings_control_frame, text="Saved Settings:").pack(side=tk.LEFT)
        
        self.settings_combo = ttk.Combobox(settings_control_frame, state="readonly", width=30)
        self.settings_combo.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        ttk.Button(settings_control_frame, text="Load", command=self.load_selected_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(settings_control_frame, text="Delete", command=self.delete_selected_settings).pack(side=tk.LEFT, padx=5)
        
        # Settings details
        details_frame = ttk.LabelFrame(parent, text="Settings Details", padding=10)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.settings_details = scrolledtext.ScrolledText(details_frame, height=20, wrap=tk.WORD)
        self.settings_details.pack(fill=tk.BOTH, expand=True)
        
        # Update settings list
        self.update_settings_list()
        
    def on_input_type_change(self):
        """Handle input type radio button changes."""
        input_type = self.input_type.get()
        
        if input_type == "pgn":
            self.pgn_frame.grid()
            self.fen_frame.grid_remove()
        else:
            self.pgn_frame.grid_remove() 
            self.fen_frame.grid()
    
    def browse_pgn_file(self):
        """Browse for PGN file."""
        initial_dir = self.settings.get("last_pgn_directory", os.path.expanduser("~"))
        filename = filedialog.askopenfilename(
            title="Select PGN File",
            initialdir=initial_dir,
            filetypes=[("PGN files", "*.pgn"), ("All files", "*.*")]
        )
        if filename:
            self.pgn_file_var.set(filename)
            self.settings["last_pgn_directory"] = os.path.dirname(filename)
            self.save_settings()
    
    def browse_engine_path(self):
        """Browse for Stockfish engine executable."""
        initial_dir = self.settings.get("last_engine_directory", os.path.expanduser("~"))
        filename = filedialog.askopenfilename(
            title="Select Stockfish Engine",
            initialdir=initial_dir,
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.engine_path_var.set(filename)
            self.settings["stockfish_path"] = filename
            self.settings["last_engine_directory"] = os.path.dirname(filename)
            self.save_settings()
    
    def browse_output_file(self):
        """Browse for output file location."""
        initial_dir = self.settings.get("last_output_directory", os.path.expanduser("~"))
        
        # Determine file extension based on format
        format_ext = {
            "pgn": ".pgn",
            "json": ".json", 
            "tree": ".txt"
        }
        ext = format_ext.get(self.output_format_var.get(), ".txt")
        
        filename = filedialog.asksaveasfilename(
            title="Save Output As",
            initialdir=initial_dir,
            defaultextension=ext,
            filetypes=[
                ("PGN files", "*.pgn"),
                ("JSON files", "*.json"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.output_file_var.set(filename)
            self.settings["last_output_directory"] = os.path.dirname(filename)
            self.save_settings()
    
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return {
            "stockfish_path": "",
            "last_pgn_directory": os.path.expanduser("~"),
            "last_engine_directory": os.path.expanduser("~"),
            "last_output_directory": os.path.expanduser("~"),
            "saved_configurations": {}
        }
    
    def save_settings(self):
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def load_saved_settings(self):
        """Load saved settings into GUI controls."""
        if "stockfish_path" in self.settings:
            self.engine_path_var.set(self.settings["stockfish_path"])
    
    def get_current_configuration(self) -> Dict[str, Any]:
        """Get current GUI configuration as dictionary."""
        return {
            "input_type": self.input_type.get(),
            "pgn_file": self.pgn_file_var.get(),
            "fen_position": self.fen_var.get(),
            "engine_path": self.engine_path_var.get(),
            "depth": self.depth_var.get(),
            "time": self.time_var.get(),
            "hash_memory": self.hash_var.get(),
            "white_moves": self.white_moves_var.get(),
            "white_threshold": self.white_threshold_var.get(),
            "black_moves": self.black_moves_var.get(),
            "black_threshold": self.black_threshold_var.get(),
            "output_format": self.output_format_var.get(),
            "output_file": self.output_file_var.get()
        }
    
    def set_configuration(self, config: Dict[str, Any]):
        """Set GUI configuration from dictionary."""
        self.input_type.set(config.get("input_type", "pgn"))
        self.pgn_file_var.set(config.get("pgn_file", ""))
        self.fen_var.set(config.get("fen_position", ""))
        self.engine_path_var.set(config.get("engine_path", ""))
        self.depth_var.set(config.get("depth", 3))
        self.time_var.set(config.get("time", 5.0))
        self.hash_var.set(config.get("hash_memory", 8192))
        self.white_moves_var.set(config.get("white_moves", 3))
        self.white_threshold_var.set(config.get("white_threshold", 50))
        self.black_moves_var.set(config.get("black_moves", 3))
        self.black_threshold_var.set(config.get("black_threshold", 50))
        self.output_format_var.set(config.get("output_format", "pgn"))
        self.output_file_var.set(config.get("output_file", ""))
        self.on_input_type_change()
    
    def save_current_settings(self):
        """Save current configuration with a name."""
        config = self.get_current_configuration()
        
        # Ask for name
        name = tkinter.simpledialog.askstring("Save Settings", "Enter a name for this configuration:")
        if name:
            config["saved_date"] = datetime.now().isoformat()
            self.settings["saved_configurations"][name] = config
            self.save_settings()
            self.update_settings_list()
            messagebox.showinfo("Settings Saved", f"Configuration '{name}' has been saved.")
    
    def update_settings_list(self):
        """Update the saved settings combo box."""
        configs = list(self.settings.get("saved_configurations", {}).keys())
        self.settings_combo['values'] = configs
        if configs:
            self.settings_combo.current(0)
            self.show_settings_details()
    
    def load_selected_settings(self):
        """Load the selected saved settings."""
        selected = self.settings_combo.get()
        if selected and selected in self.settings.get("saved_configurations", {}):
            config = self.settings["saved_configurations"][selected]
            self.set_configuration(config)
            messagebox.showinfo("Settings Loaded", f"Configuration '{selected}' has been loaded.")
    
    def delete_selected_settings(self):
        """Delete the selected saved settings."""
        selected = self.settings_combo.get()
        if selected and selected in self.settings.get("saved_configurations", {}):
            if messagebox.askyesno("Delete Settings", f"Delete configuration '{selected}'?"):
                del self.settings["saved_configurations"][selected]
                self.save_settings()
                self.update_settings_list()
                messagebox.showinfo("Settings Deleted", f"Configuration '{selected}' has been deleted.")
    
    def show_settings_details(self):
        """Show details of the selected settings."""
        selected = self.settings_combo.get()
        if selected and selected in self.settings.get("saved_configurations", {}):
            config = self.settings["saved_configurations"][selected]
            
            details = f"Configuration: {selected}\n"
            if "saved_date" in config:
                details += f"Saved: {config['saved_date']}\n"
            details += "\nSettings:\n"
            
            for key, value in config.items():
                if key != "saved_date":
                    details += f"  {key}: {value}\n"
            
            self.settings_details.delete(1.0, tk.END)
            self.settings_details.insert(1.0, details)
    
    def validate_inputs(self) -> bool:
        """Validate all inputs before starting analysis."""
        # Check engine path
        if not self.engine_path_var.get() or not os.path.exists(self.engine_path_var.get()):
            messagebox.showerror("Error", "Please select a valid Stockfish engine path.")
            return False
        
        # Check input
        if self.input_type.get() == "pgn":
            if not self.pgn_file_var.get() or not os.path.exists(self.pgn_file_var.get()):
                messagebox.showerror("Error", "Please select a valid PGN file.")
                return False
        else:
            if not self.fen_var.get().strip():
                messagebox.showerror("Error", "Please enter a FEN position.")
                return False
        
        # Check output file
        if not self.output_file_var.get():
            messagebox.showerror("Error", "Please specify an output file.")
            return False
        
        return True
    
    def start_analysis(self):
        """Start the chess analysis in a separate thread."""
        if not self.validate_inputs():
            return
        
        if self.is_analyzing:
            messagebox.showwarning("Warning", "Analysis is already running.")
            return
        
        self.is_analyzing = True
        self.analyze_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_var.set("Starting analysis...")
        self.progress_bar.start()
        self.output_text.delete(1.0, tk.END)
        
        # Start analysis in separate thread
        analysis_thread = threading.Thread(target=self.run_analysis, daemon=True)
        analysis_thread.start()
    
    def run_analysis(self):
        """Run the actual analysis process."""
        try:
            # Build command
            cmd = [
                sys.executable, "chess_tree_generator.py",
                "--stockfish-path", self.engine_path_var.get(),
                "--depth", str(self.depth_var.get()),
                "--time", str(self.time_var.get()),
                "--hash-memory", str(self.hash_var.get()),
                "--white-moves", str(self.white_moves_var.get()),
                "--white-threshold", str(self.white_threshold_var.get()),
                "--black-moves", str(self.black_moves_var.get()),
                "--black-threshold", str(self.black_threshold_var.get()),
                "--output", self.output_format_var.get(),
                "--output-file", self.output_file_var.get()
            ]
            
            # Add input
            if self.input_type.get() == "pgn":
                cmd.extend(["--pgn-file", self.pgn_file_var.get()])
            else:
                cmd.extend(["--fen", self.fen_var.get()])
            
            # Run process
            self.analysis_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Read output in real-time
            for line in iter(self.analysis_process.stdout.readline, ''):
                if not self.is_analyzing:  # Check if stopped
                    break
                self.root.after(0, self.update_output, line.strip())
            
            self.analysis_process.wait()
            
            if self.analysis_process.returncode == 0:
                self.root.after(0, self.analysis_complete, True)
            else:
                self.root.after(0, self.analysis_complete, False)
                
        except Exception as e:
            self.root.after(0, self.analysis_error, str(e))
    
    def update_output(self, line: str):
        """Update output text area with new line."""
        self.output_text.insert(tk.END, line + "\n")
        self.output_text.see(tk.END)
        
        # Update progress based on output patterns
        if "Analyzing depth" in line:
            self.progress_var.set(f"Running: {line}")
        elif "Analysis complete" in line:
            self.progress_var.set("Analysis completed successfully!")
    
    def analysis_complete(self, success: bool):
        """Handle analysis completion."""
        self.is_analyzing = False
        self.analyze_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_bar.stop()
        
        if success:
            self.progress_var.set("Analysis completed successfully!")
            messagebox.showinfo("Success", "Analysis completed successfully!")
        else:
            self.progress_var.set("Analysis failed!")
            messagebox.showerror("Error", "Analysis failed. Check the output for details.")
    
    def analysis_error(self, error_msg: str):
        """Handle analysis error."""
        self.is_analyzing = False
        self.analyze_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_var.set("Analysis error!")
        
        self.output_text.insert(tk.END, f"ERROR: {error_msg}\n")
        self.output_text.see(tk.END)
        messagebox.showerror("Error", f"Analysis error: {error_msg}")
    
    def stop_analysis(self):
        """Stop the running analysis."""
        if self.analysis_process and self.analysis_process.poll() is None:
            self.analysis_process.terminate()
        
        self.is_analyzing = False
        self.analyze_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_bar.stop()
        self.progress_var.set("Analysis stopped by user.")
        
        self.output_text.insert(tk.END, "Analysis stopped by user.\n")
        self.output_text.see(tk.END)


def main():
    """Main function to run the GUI application."""
    
    root = tk.Tk()
    app = ChessTreeGUI(root)
    
    # Handle window close
    def on_closing():
        if app.is_analyzing:
            if messagebox.askokcancel("Quit", "Analysis is running. Do you want to stop it and quit?"):
                app.stop_analysis()
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()