import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import configparser
import os
import struct
import subprocess
import threading
from pathlib import Path

# Optional Drag & Drop support via tkinterdnd2.
# Install with:  pip install tkinterdnd2
try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    _DND_AVAILABLE = True
except ImportError:
    _DND_AVAILABLE = False

VERSION     = "1.1.2"
CONFIG_FILE = "aas_creator.cfg"

# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def load_config() -> dict:
    """Load persisted paths from config file.
    Returns dict with keys: bsp_file, mbspc_path, output_dir, aas_val_path."""
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_FILE)
    defaults = {"bsp_file": "", "mbspc_path": "", "output_dir": "", "aas_val_path": ""}
    if cfg.has_section("paths"):
        for key in defaults:
            defaults[key] = cfg.get("paths", key, fallback="")
    return defaults


def save_config(bsp_file: str, mbspc_path: str, output_dir: str, aas_val_path: str) -> None:
    """Persist current paths to config file (aas_creator.cfg)."""
    cfg = configparser.ConfigParser()
    cfg["paths"] = {
        "bsp_file":     bsp_file,
        "mbspc_path":   mbspc_path,
        "output_dir":   output_dir,
        "aas_val_path": aas_val_path,
    }
    try:
        with open(CONFIG_FILE, "w") as f:
            cfg.write(f)
    except OSError:
        pass  # Non-critical – silently ignore write errors


# ---------------------------------------------------------------------------
# BSP parsing helpers (Quake III BSP format)
# ---------------------------------------------------------------------------

BSP_MAGIC   = b"IBSP"
BSP_VERSION = 46  # Q3 / Q3Rally

LUMP_ENTITIES    = 0
LUMP_TEXTURES    = 1
LUMP_PLANES      = 2
LUMP_NODES       = 3
LUMP_LEAFS       = 4
LUMP_LEAFFACES   = 5
LUMP_LEAFBRUSHES = 6
LUMP_MODELS      = 7
LUMP_BRUSHES     = 8
LUMP_BRUSHSIDES  = 9
LUMP_VERTICES    = 10
LUMP_MESHVERTS   = 11
LUMP_EFFECTS     = 12
LUMP_FACES       = 13
LUMP_LIGHTMAPS   = 14
LUMP_LIGHTVOLS   = 15
LUMP_VISDATA     = 16
NUM_LUMPS        = 17

TEXTURE_ENTRY_SIZE   = 72
BRUSH_ENTRY_SIZE     = 12
BRUSHSIDE_ENTRY_SIZE = 8
FACE_ENTRY_SIZE      = 104


def parse_bsp(filepath: str) -> dict | None:
    """Parse a Quake III BSP file and return an info dict, or None on error."""
    try:
        with open(filepath, "rb") as f:
            data = f.read()
    except OSError:
        return None

    if len(data) < 8:
        return None

    magic   = data[0:4]
    version = struct.unpack_from("<I", data, 4)[0]

    if magic != BSP_MAGIC or version != BSP_VERSION:
        return None

    lumps = []
    for i in range(NUM_LUMPS):
        off = 8 + i * 8
        lump_offset, lump_length = struct.unpack_from("<II", data, off)
        lumps.append((lump_offset, lump_length))

    info = {}
    info["file_size"] = len(data)

    ent_off, ent_len = lumps[LUMP_ENTITIES]
    raw_entities = data[ent_off: ent_off + ent_len].decode("latin-1", errors="replace").strip("\x00")
    info["entity_string"] = raw_entities
    info["entities"]      = _parse_entities(raw_entities)

    map_name = ""
    for ent in info["entities"]:
        if ent.get("classname") == "worldspawn":
            map_name = ent.get("message", "")
            break
    info["map_name"] = map_name or Path(filepath).stem

    tex_off, tex_len = lumps[LUMP_TEXTURES]
    tex_count = tex_len // TEXTURE_ENTRY_SIZE
    textures  = []
    for i in range(tex_count):
        start      = tex_off + i * TEXTURE_ENTRY_SIZE
        name_bytes = data[start: start + 64]
        name       = name_bytes.split(b"\x00")[0].decode("latin-1", errors="replace")
        flags, contents = struct.unpack_from("<II", data, start + 64)
        textures.append({"name": name, "flags": flags, "contents": contents})
    info["textures"] = textures

    brush_off, brush_len = lumps[LUMP_BRUSHES]
    info["brush_count"] = brush_len // BRUSH_ENTRY_SIZE

    face_off, face_len = lumps[LUMP_FACES]
    info["face_count"] = face_len // FACE_ENTRY_SIZE

    vert_off, vert_len = lumps[LUMP_VERTICES]
    info["vertex_count"] = vert_len // 44

    return info


def _parse_entities(entity_string: str) -> list[dict]:
    """Parse Q3 entity string into a list of dicts."""
    entities = []
    current  = {}
    in_ent   = False
    for line in entity_string.splitlines():
        line = line.strip()
        if line == "{":
            in_ent = True
            current = {}
        elif line == "}":
            if current:
                entities.append(current)
            in_ent = False
        elif in_ent and line.startswith('"'):
            parts = line.split('"')
            if len(parts) >= 5:
                current[parts[1]] = parts[3]
    return entities


# ---------------------------------------------------------------------------
# AAS validation
# ---------------------------------------------------------------------------

AAS_MAGIC       = 1396789061  # 'EAAS' as little-endian int
AAS_MAGIC_BYTES = b"EAAS"


def validate_aas(filepath: str) -> dict:
    """Check if an AAS file exists and has valid content."""
    result = {
        "path": filepath, "exists": False, "size": 0,
        "size_ok": False, "magic_ok": False, "errors": []
    }

    if not os.path.exists(filepath):
        result["errors"].append("File does not exist")
        return result

    result["exists"] = True
    size = os.path.getsize(filepath)
    result["size"] = size

    if size == 0:
        result["errors"].append("File is empty (0 bytes)")
        return result

    result["size_ok"] = True

    try:
        with open(filepath, "rb") as f:
            header = f.read(4)
        if header == AAS_MAGIC_BYTES:
            result["magic_ok"] = True
        else:
            result["errors"].append(
                f"Unexpected magic bytes: {header!r} (expected b'EAAS')")
    except OSError as e:
        result["errors"].append(f"Could not read file: {e}")

    return result


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

class AASCreator:
    def __init__(self, root):
        self.root = root
        self.root.title(f"AAS Creator – Q3Rally  v{VERSION}")
        self.root.geometry("860x620")
        self.root.resizable(True, True)

        self.bsp_file_path = tk.StringVar()
        self.mbspc_path    = tk.StringVar()
        self.output_dir    = tk.StringVar()

        self.bsp_file_path.trace_add("write", self._on_bsp_changed)

        self._load_saved_paths()
        self.find_mbspc()
        self.setup_ui()

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------

    def _load_saved_paths(self) -> None:
        """Restore paths from last session."""
        cfg = load_config()
        if cfg["bsp_file"] and os.path.exists(cfg["bsp_file"]):
            self.bsp_file_path.set(cfg["bsp_file"])
        if cfg["mbspc_path"] and os.path.exists(cfg["mbspc_path"]):
            self.mbspc_path.set(cfg["mbspc_path"])
        if cfg["output_dir"] and os.path.isdir(cfg["output_dir"]):
            self.output_dir.set(cfg["output_dir"])
        self._saved_aas_val = cfg["aas_val_path"]

    def _save_paths(self) -> None:
        """Persist current paths."""
        save_config(
            bsp_file     = self.bsp_file_path.get(),
            mbspc_path   = self.mbspc_path.get(),
            output_dir   = self.output_dir.get(),
            aas_val_path = self.aas_val_path.get() if hasattr(self, "aas_val_path") else "",
        )

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def find_mbspc(self) -> None:
        """Auto-detect mbspc.exe only when no path is already set."""
        if self.mbspc_path.get():
            return
        for path in [
            "mbspc.exe", "./mbspc.exe", "../mbspc.exe",
            "C:/Program Files/id Software/Quake III Arena/mbspc.exe",
            "C:/Games/Quake3/mbspc.exe",
        ]:
            if os.path.exists(path):
                self.mbspc_path.set(path)
                break

    def setup_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        notebook = ttk.Notebook(self.root)
        notebook.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)

        tab_create = ttk.Frame(notebook, padding=10)
        notebook.add(tab_create, text="  Create AAS  ")
        self._build_create_tab(tab_create)

        tab_info = ttk.Frame(notebook, padding=10)
        notebook.add(tab_info, text="  BSP Info  ")
        self._build_bsp_info_tab(tab_info)

        tab_val = ttk.Frame(notebook, padding=10)
        notebook.add(tab_val, text="  AAS Validation  ")
        self._build_validation_tab(tab_val)

        if self._saved_aas_val and os.path.exists(self._saved_aas_val):
            self.aas_val_path.set(self._saved_aas_val)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W).grid(
            row=1, column=0, sticky="ew", padx=8, pady=(0, 4))

        self.root.protocol("WM_DELETE_WINDOW", self.exit_app)

    # ------------------------------------------------------------------
    # Tab 1 – Create AAS
    # ------------------------------------------------------------------

    def _build_create_tab(self, parent) -> None:
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(8, weight=1)

        title_frame = ttk.Frame(parent)
        title_frame.grid(row=0, column=0, columnspan=3, pady=(0, 16))
        ttk.Label(title_frame, text="AAS Creator", font=("Arial", 15, "bold")).pack(side=tk.LEFT)
        ttk.Label(title_frame, text=f"v{VERSION}", font=("Arial", 9),
                  foreground="gray").pack(side=tk.LEFT, padx=(8, 0), anchor="s", pady=(0, 2))

        def file_row(row, label, var, browse_cmd):
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4)
            e = ttk.Entry(parent, textvariable=var, width=52)
            e.grid(row=row, column=1, sticky="ew", padx=5, pady=4)
            ttk.Button(parent, text="Browse", command=browse_cmd).grid(row=row, column=2, pady=4)
            return e

        self._bsp_entry = file_row(1, "BSP File (.bsp):",  self.bsp_file_path, self.browse_bsp_file)
        file_row(2, "MBSPC Compiler:",   self.mbspc_path,    self.browse_mbspc)
        file_row(3, "Output Directory:", self.output_dir,     self.browse_output_dir)

        self._setup_dnd()

        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(
            row=4, column=0, columnspan=3, sticky="ew", pady=16)

        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=6)
        self.create_button = ttk.Button(btn_frame, text="Create AAS File", command=self.create_aas)
        self.create_button.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="Exit",      command=self.exit_app).pack(side=tk.LEFT)

        self.progress = ttk.Progressbar(parent, mode="indeterminate")
        self.progress.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(8, 0))

        ttk.Label(parent, text="Output Log:").grid(row=7, column=0, sticky="w", pady=(16, 4))
        log_frame = ttk.Frame(parent)
        log_frame.grid(row=8, column=0, columnspan=3, sticky="nsew", pady=(0, 6))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.grid(row=0, column=0, sticky="nsew")

    # ------------------------------------------------------------------
    # Drag & Drop
    # ------------------------------------------------------------------

    def _setup_dnd(self) -> None:
        """Register Drag & Drop on the BSP entry if tkinterdnd2 is available."""
        if _DND_AVAILABLE:
            self._bsp_entry.drop_target_register(DND_FILES)
            self._bsp_entry.dnd_bind("<<Drop>>", self._on_drop)
            # Small hint label inside the entry row
            ttk.Label(self._bsp_entry.master,
                      text="(or drag & drop a .bsp here)",
                      foreground="gray", font=("Arial", 8)).grid(
                row=1, column=1, sticky="e", padx=(0, 80))
        else:
            ttk.Label(self._bsp_entry.master,
                      text="Tip: pip install tkinterdnd2 for drag & drop support",
                      foreground="#999999", font=("Arial", 8)).grid(
                row=9, column=0, columnspan=3, sticky="w", pady=(4, 0))

    def _on_drop(self, event) -> None:
        """Handle a .bsp file dropped onto the BSP entry."""
        raw  = event.data.strip()
        path = raw.strip("{}").strip('"')
        if path.lower().endswith(".bsp") and os.path.exists(path):
            self.bsp_file_path.set(path)
            if not self.output_dir.get():
                self.output_dir.set(os.path.dirname(path))
        else:
            messagebox.showwarning("Drag & Drop",
                                   f"Only .bsp files are accepted.\nDropped: {path}")

    # ------------------------------------------------------------------
    # Tab 2 – BSP Info
    # ------------------------------------------------------------------

    def _build_bsp_info_tab(self, parent) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        top = ttk.Frame(parent)
        top.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        top.columnconfigure(0, weight=1)
        ttk.Label(top, text="BSP Info", font=("Arial", 13, "bold")).grid(row=0, column=0, sticky="w")
        ttk.Label(top, text="Select a BSP file on the 'Create AAS' tab to populate this panel.",
                  foreground="gray").grid(row=1, column=0, sticky="w")
        ttk.Button(top, text="Refresh", command=self.refresh_bsp_info).grid(
            row=0, column=1, rowspan=2, padx=(8, 0))

        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.grid(row=1, column=0, sticky="nsew")

        left = ttk.Frame(paned, padding=4)
        paned.add(left, weight=2)
        left.columnconfigure(0, weight=1)
        left.rowconfigure(2, weight=1)

        summary = ttk.LabelFrame(left, text="Summary", padding=8)
        summary.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        summary.columnconfigure(1, weight=1)

        self.info_labels = {}
        for i, (key, label) in enumerate([
            ("map_name",     "Map Name"),
            ("file_size",    "File Size"),
            ("brush_count",  "Brushes"),
            ("face_count",   "Faces"),
            ("vertex_count", "Vertices"),
            ("tex_count",    "Textures"),
            ("entity_count", "Entities"),
        ]):
            ttk.Label(summary, text=label + ":").grid(row=i, column=0, sticky="w", padx=(0, 12), pady=2)
            var = tk.StringVar(value="—")
            self.info_labels[key] = var
            ttk.Label(summary, textvariable=var, foreground="#0055cc").grid(
                row=i, column=1, sticky="w", pady=2)

        ttk.Label(left, text="Entities:").grid(row=1, column=0, sticky="w", pady=(0, 2))
        ent_frame = ttk.Frame(left)
        ent_frame.grid(row=2, column=0, sticky="nsew")
        ent_frame.columnconfigure(0, weight=1)
        ent_frame.rowconfigure(0, weight=1)

        cols = ("classname", "targetname", "origin")
        self.entity_tree = ttk.Treeview(ent_frame, columns=cols, show="headings", height=10)
        for col in cols:
            self.entity_tree.heading(col, text=col.capitalize())
            self.entity_tree.column(col, width=120, anchor="w")
        vsb = ttk.Scrollbar(ent_frame, orient="vertical", command=self.entity_tree.yview)
        self.entity_tree.configure(yscrollcommand=vsb.set)
        self.entity_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        right = ttk.Frame(paned, padding=4)
        paned.add(right, weight=1)
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        ttk.Label(right, text="Textures:").grid(row=0, column=0, sticky="w", pady=(0, 2))
        tex_frame = ttk.Frame(right)
        tex_frame.grid(row=1, column=0, sticky="nsew")
        tex_frame.columnconfigure(0, weight=1)
        tex_frame.rowconfigure(0, weight=1)

        self.tex_list = tk.Listbox(tex_frame, font=("Courier New", 9))
        tex_vsb = ttk.Scrollbar(tex_frame, orient="vertical",   command=self.tex_list.yview)
        tex_hsb = ttk.Scrollbar(tex_frame, orient="horizontal", command=self.tex_list.xview)
        self.tex_list.configure(yscrollcommand=tex_vsb.set, xscrollcommand=tex_hsb.set)
        self.tex_list.grid(row=0, column=0, sticky="nsew")
        tex_vsb.grid(row=0, column=1, sticky="ns")
        tex_hsb.grid(row=1, column=0, sticky="ew")

    # ------------------------------------------------------------------
    # Tab 3 – AAS Validation
    # ------------------------------------------------------------------

    def _build_validation_tab(self, parent) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(3, weight=1)

        ttk.Label(parent, text="AAS Validation", font=("Arial", 13, "bold")).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 12))

        ttk.Label(parent, text="AAS File:").grid(row=1, column=0, sticky="w", pady=4)
        self.aas_val_path = tk.StringVar()
        ttk.Entry(parent, textvariable=self.aas_val_path, width=55).grid(
            row=1, column=1, sticky="ew", padx=5, pady=4)
        ttk.Button(parent, text="Browse", command=self.browse_aas_file).grid(row=1, column=2, pady=4)
        parent.columnconfigure(1, weight=1)

        ttk.Button(parent, text="Validate", command=self.run_validation).grid(
            row=2, column=0, columnspan=3, pady=(6, 12))

        result_frame = ttk.LabelFrame(parent, text="Validation Result", padding=10)
        result_frame.grid(row=3, column=0, columnspan=3, sticky="nsew")
        result_frame.columnconfigure(1, weight=1)

        checks = [
            ("exists",   "File exists"),
            ("size_ok",  "File size > 0"),
            ("magic_ok", "AAS magic bytes valid"),
        ]
        self.val_indicators = {}
        for i, (key, label) in enumerate(checks):
            ttk.Label(result_frame, text=label + ":").grid(
                row=i, column=0, sticky="w", padx=(0, 12), pady=4)
            var = tk.StringVar(value="—")
            lbl = ttk.Label(result_frame, textvariable=var, width=10)
            lbl.grid(row=i, column=1, sticky="w", pady=4)
            self.val_indicators[key] = (var, lbl)

        n = len(checks)
        ttk.Label(result_frame, text="File Size:").grid(row=n, column=0, sticky="w", padx=(0, 12), pady=4)
        self.val_size_var = tk.StringVar(value="—")
        ttk.Label(result_frame, textvariable=self.val_size_var).grid(row=n, column=1, sticky="w", pady=4)

        ttk.Label(result_frame, text="Errors / Notes:").grid(
            row=n + 1, column=0, sticky="nw", padx=(0, 12), pady=4)
        self.val_errors_text = scrolledtext.ScrolledText(result_frame, height=6, state="disabled")
        self.val_errors_text.grid(row=n + 1, column=1, sticky="ew", pady=4)
        result_frame.rowconfigure(n + 1, weight=1)

    # ------------------------------------------------------------------
    # BSP Info logic
    # ------------------------------------------------------------------

    def _on_bsp_changed(self, *_) -> None:
        self.refresh_bsp_info()

    def refresh_bsp_info(self) -> None:
        path = self.bsp_file_path.get()
        if not path or not os.path.exists(path):
            return

        info = parse_bsp(path)
        if info is None:
            messagebox.showwarning(
                "BSP Info",
                "Could not parse BSP file.\n"
                "Make sure it is a valid Quake III BSP (version 46).")
            return

        self.info_labels["map_name"].set(info["map_name"])
        self.info_labels["file_size"].set(
            f"{info['file_size']:,} bytes ({info['file_size'] / 1024:.1f} KB)")
        self.info_labels["brush_count"].set(str(info["brush_count"]))
        self.info_labels["face_count"].set(str(info["face_count"]))
        self.info_labels["vertex_count"].set(str(info["vertex_count"]))
        self.info_labels["tex_count"].set(str(len(info["textures"])))
        self.info_labels["entity_count"].set(str(len(info["entities"])))

        for item in self.entity_tree.get_children():
            self.entity_tree.delete(item)
        for ent in info["entities"]:
            self.entity_tree.insert("", "end", values=(
                ent.get("classname", ""),
                ent.get("targetname", ""),
                ent.get("origin", ""),
            ))

        self.tex_list.delete(0, tk.END)
        for tex in info["textures"]:
            self.tex_list.insert(tk.END, tex["name"])

        if hasattr(self, "aas_val_path") and not self.aas_val_path.get():
            self.aas_val_path.set(
                os.path.join(os.path.dirname(path), Path(path).stem + ".aas"))

    # ------------------------------------------------------------------
    # AAS Validation logic
    # ------------------------------------------------------------------

    def browse_aas_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Select AAS File",
            filetypes=[("AAS files", "*.aas"), ("All files", "*.*")])
        if path:
            self.aas_val_path.set(path)

    def run_validation(self) -> None:
        path = self.aas_val_path.get().strip()
        if not path:
            messagebox.showwarning("Validation", "Please specify an AAS file path.")
            return

        result = validate_aas(path)
        tick, cross, dash = "✔  OK", "✘  FAIL", "—"
        green, red, gray  = "#1a7a1a", "#cc0000", "gray"

        for key in ("exists", "size_ok", "magic_ok"):
            var, lbl = self.val_indicators[key]
            val = result.get(key, False)
            if not result["exists"] and key != "exists":
                var.set(dash);  lbl.configure(foreground=gray)
            elif val:
                var.set(tick);  lbl.configure(foreground=green)
            else:
                var.set(cross); lbl.configure(foreground=red)

        size = result["size"]
        self.val_size_var.set(
            f"{size:,} bytes ({size / 1024:.1f} KB)" if size else "0 bytes")

        self.val_errors_text.configure(state="normal")
        self.val_errors_text.delete(1.0, tk.END)
        self.val_errors_text.insert(
            tk.END,
            "\n".join(result["errors"]) if result["errors"] else "No errors detected.")
        self.val_errors_text.configure(state="disabled")

    # ------------------------------------------------------------------
    # Browse helpers
    # ------------------------------------------------------------------

    def browse_bsp_file(self) -> None:
        filename = filedialog.askopenfilename(
            title="Select BSP File",
            filetypes=[("BSP files", "*.bsp"), ("All files", "*.*")])
        if filename:
            self.bsp_file_path.set(filename)
            if not self.output_dir.get():
                self.output_dir.set(os.path.dirname(filename))

    def browse_mbspc(self) -> None:
        filename = filedialog.askopenfilename(
            title="Select MBSPC Compiler",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")])
        if filename:
            self.mbspc_path.set(filename)

    def browse_output_dir(self) -> None:
        dirname = filedialog.askdirectory(title="Select Output Directory")
        if dirname:
            self.output_dir.set(dirname)

    # ------------------------------------------------------------------
    # Create AAS
    # ------------------------------------------------------------------

    def clear_all(self) -> None:
        self.bsp_file_path.set("")
        self.output_dir.set("")
        self.log_text.delete(1.0, tk.END)
        self.status_var.set("Ready")

    def exit_app(self) -> None:
        self._save_paths()
        self.root.quit()
        self.root.destroy()

    def log_message(self, message: str) -> None:
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def validate_inputs(self) -> bool:
        if not self.bsp_file_path.get():
            messagebox.showerror("Error", "Please select a .bsp file"); return False
        if not os.path.exists(self.bsp_file_path.get()):
            messagebox.showerror("Error", "BSP file does not exist");   return False
        if not self.mbspc_path.get():
            messagebox.showerror("Error", "Please specify the MBSPC compiler path"); return False
        if not os.path.exists(self.mbspc_path.get()):
            messagebox.showerror("Error", "MBSPC compiler not found"); return False
        return True

    def create_aas_thread(self) -> None:
        try:
            self.status_var.set("Processing...")
            self.progress.start()

            bsp_file   = self.bsp_file_path.get()
            mbspc_exe  = self.mbspc_path.get()
            output_dir = self.output_dir.get()

            self.log_message(f"Starting AAS creation for: {os.path.basename(bsp_file)}")
            self.log_message(f"Using compiler: {mbspc_exe}")
            if output_dir:
                self.log_message(f"Output directory: {output_dir}")
            self.log_message("-" * 50)

            cmd = [mbspc_exe, "-bsp2aas", "-forcesidesvisible", "-optimize", "-reach", bsp_file]
            self.log_message(f"Command: {' '.join(cmd)}")
            self.log_message("-" * 50)

            work_dir = output_dir if output_dir else os.path.dirname(bsp_file)
            process  = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                universal_newlines=True, cwd=work_dir)

            while True:
                line = process.stdout.readline()
                if line == "" and process.poll() is not None:
                    break
                if line:
                    self.log_message(line.strip())

            rc = process.poll()
            if rc == 0:
                bsp_name    = Path(bsp_file).stem
                search_dirs = ([output_dir] if output_dir else []) + [os.path.dirname(bsp_file)]
                aas_file    = next(
                    (os.path.join(d, f"{bsp_name}.aas") for d in search_dirs
                     if os.path.exists(os.path.join(d, f"{bsp_name}.aas"))), None)

                if aas_file:
                    self.log_message("-" * 50)
                    self.log_message(f"SUCCESS: AAS file created: {aas_file}")
                    self.status_var.set("AAS file created successfully!")
                    self.aas_val_path.set(aas_file)
                    self._save_paths()
                    messagebox.showinfo("Success", f"AAS file created!\n\nOutput: {aas_file}")
                else:
                    self.log_message("-" * 50)
                    self.log_message("WARNING: Process completed but AAS file not found")
                    self.status_var.set("Process completed - check log")
            else:
                self.log_message("-" * 50)
                self.log_message(f"ERROR: Process failed with return code {rc}")
                self.status_var.set("Process failed - check log")
                messagebox.showerror("Error",
                    f"AAS creation failed (return code {rc})\nSee log for details.")

        except Exception as e:
            self.log_message(f"ERROR: {e}")
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            self.progress.stop()
            self.create_button.config(state=tk.NORMAL)

    def create_aas(self) -> None:
        if not self.validate_inputs():
            return
        self.create_button.config(state=tk.DISABLED)
        self.log_text.delete(1.0, tk.END)
        threading.Thread(target=self.create_aas_thread, daemon=True).start()


# ---------------------------------------------------------------------------

def main():
    if _DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    AASCreator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
