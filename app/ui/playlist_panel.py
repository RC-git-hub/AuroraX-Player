import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os

class PlaylistPanel(ctk.CTkFrame):
    def __init__(self, master, state, video_player, control_panel, icons):
        super().__init__(master)
        self.state = state
        self.video_player = video_player
        self.control_panel = control_panel
        self.icons = icons

        self.playlist_path = None
        self.entries = []  # list of absolute file paths from the m3u

        self.build_ui()
        self.tree_list.bind("<Return>", lambda event: self.selected_video())

    # -------------------------------------------------------------
    # Load an .m3u or .m3u8 file
    # -------------------------------------------------------------
    def load_playlist(self):
        path = filedialog.askopenfilename(
            title="Select M3U Playlist",
            filetypes=[("M3U Playlist", "*.m3u *.m3u8")]
        )

        if not path:
            return

        self.playlist_path = path
        self.entries = self.parse_m3u(path)
        self.refresh_media()

    # -------------------------------------------------------------
    # Parse M3U playlist
    # -------------------------------------------------------------
    def parse_m3u(self, path):
        entries = []

        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read playlist:\n{e}")
            return entries

        base_dir = os.path.dirname(path)

        for line in lines:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            # Absolute path or URL?
            if "://" in line:
                entries.append(line)
                continue

            # Otherwise treat as local file (relative)
            abs_path = os.path.abspath(os.path.join(base_dir, line))

            if os.path.isfile(abs_path):
                entries.append(abs_path)

        return entries

    # -------------------------------------------------------------
    # Refresh tree
    # -------------------------------------------------------------
    def refresh_media(self):
        for item in self.tree_list.get_children():
            self.tree_list.delete(item)

        if not self.entries:
            messagebox.showwarning("Playlist Empty", "The selected M3U playlist contains no playable files!")
            return

        for i, full_path in enumerate(self.entries):
            fname = os.path.basename(full_path)

            row_tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.tree_list.insert("", tk.END, values=(fname,), tags=(row_tag,))

    # -------------------------------------------------------------
    # UI
    # -------------------------------------------------------------
    def build_ui(self):
        # ---------- Style ----------
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
                        font=("Segoe UI", 12, "bold"))
        style.map("Custom.Treeview.Heading",
                  background=[("active", "#333333"),
                              ("pressed", "#333333")],
                  foreground=[("active", "#ffffff"),
                              ("pressed", "#ffffff")])

        # ---------- Treeview ----------
        self.tree_list = ttk.Treeview(
            self,
            columns=("Media",),
            show="headings",
            style="Custom.Treeview",
            selectmode="browse",
            height=10
        )
        self.tree_list.heading("Media", text="Playlist Media")
        self.tree_list.column("Media", anchor="center", width=300)
        self.tree_list.tag_configure("oddrow", background="#2b2b2b")
        self.tree_list.tag_configure("evenrow", background="#383838")

        # ---------- Scrollbar ----------
        self.v_scroll = ctk.CTkScrollbar(self, orientation="vertical", command=self.tree_list.yview)
        self.tree_list.configure(yscrollcommand=self.v_scroll.set)

        # ---------- Layout ----------
        self.tree_list.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=(10,0), pady=10)
        self.v_scroll.grid(row=0, column=2, sticky="ns", padx=(0,10), pady=10)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # -------------------------------------------------------------
        # BUTTON BAR (BOTTOM) — ALWAYS SHOWS
        # -------------------------------------------------------------
        button_bar = ctk.CTkFrame(self)
        button_bar.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,10))

        # Expand button bar horizontally
        button_bar.grid_columnconfigure((0,1), weight=1)

        self.btn_load = ctk.CTkButton(button_bar, text="Load M3U", command=self.load_playlist)
        self.btn_load.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.btn_play = ctk.CTkButton(button_bar, text="Play", command=self.selected_video)
        self.btn_play.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.btn_create = ctk.CTkButton(button_bar, text="Create Playlist", command=self.create_playlist)
        self.btn_create.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.btn_add = ctk.CTkButton(button_bar, text="Add Files", command=self.append_file)
        self.btn_add.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

    # -------------------------------------------------------------
    # Append a file to a playlist
    # -------------------------------------------------------------

    def append_file(self):
        if not self.entries:
            messagebox.showwarning("No Playlist Loaded", "Load a playlist first or create a new one.")
            return

        # Allowed media types (video + audio)
        file_types = [
            ("Media", "*.mp4 *.mkv *.avi *.mov *.mp3 *.wav *.ogg *.flac *.m4a *.aac *.opus"),
            ("All Files", "*.*")
        ]

        # Select files to add
        new_files = filedialog.askopenfilenames(
            title="Add Files to Playlist",
            filetypes=file_types
        )

        if not new_files:
            return

        # Convert to list and extend existing entries
        new_files = list(new_files)

        # Append to internal playlist
        self.entries.extend(new_files)

        # Refresh UI
        self.refresh_media()

        # If playlist came from an M3U file → append automatically
        if self.playlist_path:
            try:
                with open(self.playlist_path, "a", encoding="utf-8") as f:
                    for item in new_files:
                        f.write(item.replace("\\", "/") + "\n")

            except Exception as e:
                messagebox.showerror("Error", f"Could not update playlist file:\n{e}")
                return

        messagebox.showinfo("Playlist Updated", f"Added {len(new_files)} file(s) to playlist.")

    # -------------------------------------------------------------
    # Play selected entry
    # -------------------------------------------------------------
    def selected_video(self):
        selected = self.tree_list.focus()
        if selected:
            index = self.tree_list.index(selected)

            if index < len(self.entries):
                self.state.path = self.entries[index]
                self.state.current_song_list = self.entries.copy()
                self.state.current_index = index
                self.video_player.load_media()
                self.control_panel.btn_play_pause.configure(image=self.icons["pause"])
                return

        messagebox.showwarning("Playlist", "Please select a file!")
        self.state.path = None

    # -------------------------------------------------------------
    # Create M3U playlist
    # -------------------------------------------------------------
    def create_playlist(self):
        paths = filedialog.askopenfilenames(
            title="Select Videos/Music for Playlist",
            filetypes=[
                ("Media", "*.mp4 *.mkv *.avi *.mov *.mp3 *.wav *.ogg *.flac *.m4a *.aac *.opus"),
                ("All Files", "*.*")
            ]
        )
        if not paths:
            return
        self.playlist = list(paths)
        self.save_playlist()

    def save_playlist(self):
        if not self.playlist:
            messagebox.showerror("Error", "No playlist to save.")
            return
        path = filedialog.asksaveasfilename(
            title="Save Playlist",
            defaultextension=".m3u",
            filetypes=[("M3U Playlist", "*.m3u"), ("All Files", "*.*")]
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                for video in self.playlist:
                    f.write(video.replace("\\", "/") + "\n")
            messagebox.showinfo("Playlist Saved", "Playlist saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save playlist:\n{e}")
