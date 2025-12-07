import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import os
from app.services.file_loader import FileLoader

class FolderPanel(ctk.CTkFrame):
    def __init__(self, master, state, media_player, control_panel, icons):
        super().__init__(master)

        self.folder_path = None
        self.state = state
        self.media_player = media_player
        self.files = []    
        self.control_panel = control_panel
        self.icons = icons

        self.build_ui()
        self.tree_list.bind("<Return>", lambda event: self.selected_video())

    
    def load_folder(self):
        self.files, self.folder_path = FileLoader().load(
            allowed_exts=[".mp4", ".avi", ".mov", ".mkv", 
                ".mp3", ".wav", ".flac", ".aac", ".m4a", 
                ".ogg", ".opus"])
        if self.folder_path:
            self.refresh_media()

    def refresh_media(self):
        for item in self.tree_list.get_children():
            self.tree_list.delete(item)

        if not self.folder_path or not self.files:
            messagebox.showwarning("Folder Empty", "Please select a folder that contains at least a video/music!")
            return
            
        for i, fname in enumerate(self.files):
            path = os.path.join(self.folder_path, fname)
            if os.path.isfile(path):
                row_tag = "evenrow" if i % 2 == 0 else "oddrow"
                self.tree_list.insert("", tk.END, values=(fname,), tags=(row_tag,))

    def build_ui(self):
        # ---------- Style the Treeview ----------
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview",
                        background="#2b2b2b",
                        foreground="#ffffff",
                        rowheight=30,
                        fieldbackground="#2b2b2b",
                        font=("Segoe UI", 12))
        style.map("Custom.Treeview",
                  background=[("selected", "#2fa572")],
                  foreground=[("selected", "#ffffff")])
        style.configure("Custom.Treeview.Heading",
                        background="#333333",
                        foreground="#ffffff",
                        font=("Segoe UI", 12, "bold"),
                        relief="raised")
        # Prevent hover or active changes
        style.map("Custom.Treeview.Heading",
                background=[("active", "#333333"),    # header on hover
                            ("pressed", "#333333")],  # header on click
                foreground=[("active", "#ffffff"), 
                            ("pressed", "#ffffff")])

        # ---------- Treeview ----------
        self.tree_list = ttk.Treeview(
            self, 
            columns=("Media",), 
            show="headings",  # Changed from "tree" to "headings"
            style="Custom.Treeview", 
            selectmode="browse",
            height=10
        )
        self.tree_list.heading("Media", text="Media Folder")  # Add heading
        self.tree_list.column("Media", anchor="center", width=300)
        self.tree_list.tag_configure("oddrow", background="#2b2b2b")
        self.tree_list.tag_configure("evenrow", background="#383838")

        # ---------- Scrollbar ----------
        self.v_scroll = ctk.CTkScrollbar(self, orientation="vertical", command=self.tree_list.yview)
        self.tree_list.configure(yscrollcommand=self.v_scroll.set)

        # ---------- Grid Layout ----------
        self.tree_list.grid(row=0, column=0, padx=(10,0), pady=10, columnspan=2, sticky="nsew")
        self.v_scroll.grid(row=0, column=2, padx=(0,10), pady=10, sticky="ns")

        # Make the tree expand with the frame
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # -------------------------------------------------------------
        # BUTTON BAR (BOTTOM) — ALWAYS SHOWS
        # -------------------------------------------------------------
        button_bar = ctk.CTkFrame(self)
        button_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,10))

        # Expand button bar horizontally
        button_bar.grid_columnconfigure((0,1), weight=1)

        self.btn_load = ctk.CTkButton(button_bar, text="Load Folder", command=self.load_folder)
        self.btn_load.grid(row=1, column=0, padx=10, pady=10)

        self.btn_play = ctk.CTkButton(button_bar, text="Play", command=self.selected_video)
        self.btn_play.grid(row=1, column=1, padx=10, pady=10)

    def selected_video(self):
        selected = self.tree_list.focus()
        if selected:
            values = self.tree_list.item(selected, "values")
            if values:
                fname = values[0]
                self.state.path = os.path.join(self.folder_path, fname)
                self.state.current_song_list = [
                    os.path.join(self.folder_path, f) for f in self.files  # full paths
                ]
                self.state.current_index = (self.files.index(fname))    # current index
                self.media_player.load_media()
                self.control_panel.btn_play_pause.configure(image=self.icons["pause"])
                return

        messagebox.showwarning("Folder", "Please select a file!")
        self.state.path = None
