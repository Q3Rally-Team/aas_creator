import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import subprocess
import threading
from pathlib import Path

class AASCreator:
    def __init__(self, root):
        self.root = root
        self.root.title("AAS Creator")
        self.root.geometry("800x500")
        self.root.resizable(True, True)
        
        # Variables
        self.bsp_file_path = tk.StringVar()
        self.mbspc_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        
        # Try to find mbspc.exe automatically
        self.find_mbspc()
        
        self.setup_ui()
        
    def find_mbspc(self):
        """Try to find mbspc.exe automatically"""
        common_paths = [
            "mbspc.exe",
            "./mbspc.exe",
            "../mbspc.exe",
            "C:/Program Files/id Software/Quake III Arena/mbspc.exe",
            "C:/Games/Quake3/mbspc.exe"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                self.mbspc_path.set(path)
                break
                
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="AAS Creator", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # BSP file selection
        ttk.Label(main_frame, text="BSP File (.bsp):").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.bsp_file_path, width=50).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_bsp_file).grid(row=1, column=2, pady=5)
        
        # MBSPC compiler path
        ttk.Label(main_frame, text="MBSPC Compiler:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.mbspc_path, width=50).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_mbspc).grid(row=2, column=2, pady=5)
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.output_dir, width=50).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_output_dir).grid(row=3, column=2, pady=5)
        
        # Separator
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=20)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        # Create AAS button
        self.create_button = ttk.Button(buttons_frame, text="Create AAS File", command=self.create_aas)
        self.create_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        ttk.Button(buttons_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=(0, 10))
        
        # Exit button
        ttk.Button(buttons_frame, text="Exit", command=self.exit_app).pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Output log
        ttk.Label(main_frame, text="Output Log:").grid(row=7, column=0, sticky=tk.W, pady=(20, 5))
        
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
    def browse_bsp_file(self):
        """Browse for .bsp file"""
        filename = filedialog.askopenfilename(
            title="Select BSP File",
            filetypes=[("BSP files", "*.bsp"), ("All files", "*.*")]
        )
        if filename:
            self.bsp_file_path.set(filename)
            # Set output directory to same as bsp file if not set
            if not self.output_dir.get():
                self.output_dir.set(os.path.dirname(filename))
                
    def browse_mbspc(self):
        """Browse for mbspc.exe"""
        filename = filedialog.askopenfilename(
            title="Select MBSPC Compiler",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.mbspc_path.set(filename)
            
    def browse_output_dir(self):
        """Browse for output directory"""
        dirname = filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self.output_dir.set(dirname)
            
    def clear_all(self):
        """Clear all input fields and log"""
        self.bsp_file_path.set("")
        self.output_dir.set("")
        self.log_text.delete(1.0, tk.END)
        self.status_var.set("Ready")
        
    def exit_app(self):
        """Exit the application"""
        self.root.quit()
        self.root.destroy()
        
    def log_message(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def validate_inputs(self):
        """Validate all inputs before processing"""
        if not self.bsp_file_path.get():
            messagebox.showerror("Error", "Please select a .bsp file")
            return False
            
        if not os.path.exists(self.bsp_file_path.get()):
            messagebox.showerror("Error", "BSP file does not exist")
            return False
            
        if not self.mbspc_path.get():
            messagebox.showerror("Error", "Please specify the MBSPC compiler path")
            return False
            
        if not os.path.exists(self.mbspc_path.get()):
            messagebox.showerror("Error", "MBSPC compiler not found")
            return False
            
        return True
        
    def create_aas_thread(self):
        """Create AAS file in separate thread"""
        try:
            self.status_var.set("Processing...")
            self.progress.start()
            
            bsp_file = self.bsp_file_path.get()
            mbspc_exe = self.mbspc_path.get()
            output_dir = self.output_dir.get()
            
            self.log_message(f"Starting AAS creation for: {os.path.basename(bsp_file)}")
            self.log_message(f"Using compiler: {mbspc_exe}")
            if output_dir:
                self.log_message(f"Output directory: {output_dir}")
            self.log_message("-" * 50)
            
            # Prepare command
            # MBSPC parameters for AAS creation from BSP
            cmd = [
                mbspc_exe,
                "-bsp2aas",
                "-forcesidesvisible",
                "-optimize",
                "-reach",
                bsp_file
            ]
            
            self.log_message(f"Command: {' '.join(cmd)}")
            self.log_message("-" * 50)
            
            # Set working directory
            work_dir = output_dir if output_dir else os.path.dirname(bsp_file)
            
            # Execute command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=work_dir
            )
            
            # Read output in real-time
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_message(output.strip())
                    
            rc = process.poll()
            
            if rc == 0:
                # Check if AAS file was created
                bsp_name = Path(bsp_file).stem
                
                # Look for AAS file in output directory or same directory as BSP
                search_dirs = []
                if output_dir:
                    search_dirs.append(output_dir)
                search_dirs.append(os.path.dirname(bsp_file))
                
                aas_file = None
                for search_dir in search_dirs:
                    potential_aas = os.path.join(search_dir, f"{bsp_name}.aas")
                    if os.path.exists(potential_aas):
                        aas_file = potential_aas
                        break
                
                if aas_file:
                    self.log_message("-" * 50)
                    self.log_message(f"SUCCESS: AAS file created: {aas_file}")
                    self.status_var.set("AAS file created successfully!")
                    messagebox.showinfo("Success", f"AAS file created successfully!\n\nOutput: {aas_file}")
                else:
                    self.log_message("-" * 50)
                    self.log_message("WARNING: Process completed but AAS file not found")
                    self.status_var.set("Process completed - check log")
            else:
                self.log_message("-" * 50)
                self.log_message(f"ERROR: Process failed with return code {rc}")
                self.status_var.set("Process failed - check log")
                messagebox.showerror("Error", f"AAS creation failed with return code {rc}\nCheck the log for details.")
                
        except Exception as e:
            self.log_message(f"ERROR: {str(e)}")
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
        finally:
            self.progress.stop()
            self.create_button.config(state=tk.NORMAL)
            
    def create_aas(self):
        """Create AAS file"""
        if not self.validate_inputs():
            return
            
        # Disable button during processing
        self.create_button.config(state=tk.DISABLED)
        
        # Clear previous log
        self.log_text.delete(1.0, tk.END)
        
        # Start processing in separate thread
        thread = threading.Thread(target=self.create_aas_thread)
        thread.daemon = True
        thread.start()

def main():
    root = tk.Tk()
    app = AASCreator(root)
    root.mainloop()

if __name__ == "__main__":
    main()