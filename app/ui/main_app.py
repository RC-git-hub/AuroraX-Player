import os, ctypes, sys
import customtkinter as ctk
from PIL import Image, ImageTk
from customtkinter import CTkImage
from tkinter import messagebox
from app.state import AppState
from app.players.media_player import MediaPlayer
from app.ui.folder_panel import FolderPanel
from app.ui.control_panel import ControlPanel
from app.ui.playlist_panel import PlaylistPanel


# Initialize application state and controller
APP_NAME = "AuroraX"
APP_VERSION = "1.0.0"
APP_COMPANY = "©RC | ©RC_PROGRAMS"
APP_WEBSITE = ""
APP_SUPPORT_EMAIL = ""
APP_GITHUB = "https://github.com/RC-git-hub"

state = AppState()


class MainApp(ctk.CTk):
    def __init__(self,):
        super().__init__()
        self.setup_window()
        root = self.winfo_toplevel()

        
        self.icons = {}
        
        # Load icons
        base_dir = os.path.dirname(os.path.abspath(__file__))
        icons_dir = os.path.join(base_dir,'..', '..', 'assets', 'icons')

        icon_files = {
            "go_back": "go_back_icon.png",
            "play": "play_icon.png",
            "pause": "pause_icon.png",
            "forward": "forward_icon.png",
            "backward": "backward_icon.png",
            "settings": "setting_icon.png",
            "exit": "exit_icon.png",
            "stop": "stop_icon.png",
            "shuffle": "shuffle_icon.png",
            "loop_0": "loop[0]_icon.png",
            "loop_1": "loop[1]_icon.png",
            "loop_2": "loop[2]_icon.png",
        }

        for name, file in icon_files.items():
            self.load_icon(name, os.path.join(icons_dir, file))


        # Build UI components

        # Configure grid for dashboard layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)   # main video area expands
        self.grid_columnconfigure(1, weight=0)   # sidebar fixed

        # Main content area (video player always here)

        self.media_player = MediaPlayer(self, state)
        self.media_player.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.control_panel = ControlPanel(self, state, self.media_player, self.icons)
        self.control_panel.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        # Create Tabview as a vertical sidebar on the right
        self.tabview = ctk.CTkTabview(self, width=350, height=600, corner_radius=10)
        self.tabview.grid(row=0, column=1, sticky="ns", padx=10, pady=10)
        self.tabview.grid_propagate(False)   # prevents resizing to fit children
        
        # Add tabs (no video here, just controls/settings)
        self.tabview.add("Folder")
        self.tabview.add("Settings")
        self.tabview.add("C/O Playlist")

        # Access each tab like a frame
        folder_tab = self.tabview.tab("Folder")
        settings_tab = self.tabview.tab("Settings")
        playlist_tab = self.tabview.tab("C/O Playlist")
        
        
        self.folder_panel = FolderPanel(folder_tab, state, self.media_player, self.control_panel, self.icons)
        self.folder_panel.grid(row=0, column=0)

        playlist_panel = PlaylistPanel(playlist_tab, state, self.media_player, self.control_panel, self.icons)
        playlist_panel.grid(row=0, column=0, sticky="nsew")

        # Example content in Settings tab
        ctk.CTkLabel(settings_tab, text="⚙️ Settings", font=("Arial", 16)).grid(row=0, column=0, padx=20, pady=20)

        self.fullscreen_switch = ctk.CTkSwitch(settings_tab, text="Full Screen", command=self.toggle_fullscreen)
        self.fullscreen_switch.grid(row=1, column=0, padx=20, pady=10)
        
        root.bind("<Escape>", self.exit_fullscreen)
        root.bind("<f>", self.toggle_fullscreen)
        root.bind("<F>", self.toggle_fullscreen)
        self.bind("<Control-q>", lambda event: self.on_close())



    def exit_fullscreen(self, event=None):
        self.attributes("-fullscreen", False)
        self.fullscreen_switch.deselect()
        # Show panels back
        self.tabview.grid(row=0, column=1, sticky="ns", padx=10, pady=10)
        self.control_panel.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)



    def toggle_fullscreen(self, event=None):
    # Flip switch manually if user pressed F
        if event is not None:
            if self.fullscreen_switch.get():
                self.fullscreen_switch.deselect()
            else:
                self.fullscreen_switch.select()

        is_fullscreen = self.fullscreen_switch.get()
        self.attributes("-fullscreen", is_fullscreen)

        if is_fullscreen:
            self.tabview.grid_remove()
        else:
            self.tabview.grid(row=0, column=1, sticky="ns", padx=10, pady=10)
            self.control_panel.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=10)


    def load_icon(self, name, path, size=(20, 20)):
        img = Image.open(self.resource_path(path))
        icon = CTkImage(light_image=img, size=size)
        self.icons[name] = icon

    def setup_window(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if os.name == 'nt':  # For Windows
            myappid = u'aurorax-player.v1'  # Define a unique AppUserModelID
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            # Set the window icon for windows
            self.wm_iconbitmap(os.path.join(base_dir,'..', '..', 'assets', 'icons', 'icon_1.ico'))
            
        elif os.name == 'posix':  # For macOS
            icon_path = os.path.join(base_dir, '..', '..', 'assets', 'icons', 'icon_2.png')
            icon_img = ImageTk.PhotoImage(file=icon_path)
            self.iconphoto(False, icon_img)
        self.title(f"{APP_NAME}")
        


        # Center the window on the screen
        window_width = 1000
        window_height = 600

        # Get the screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate the x and y positions for the window to be centered
        x_position = (screen_width // 2) - (window_width // 2)
        y_position = (screen_height // 2) - (window_height // 2)

        # Set the window geometry with the center position
        self.geometry(f'{window_width}x{window_height}+{x_position}+{y_position}')
        self.minsize(950, 600)
        ctk.set_appearance_mode("dark")   # "dark" or "light", "system"
        ctk.set_default_color_theme("green")  # try "green", "dark-blue"

    def resource_path(self, relative_path):
        if hasattr(sys, "_MEIPASS"):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        
        return os.path.join(base_path, relative_path)



    def on_close(self):
        # Ask the user before closing
        if not messagebox.askokcancel("Quit", "Do you really want to exit?"):
            return  # user pressed Cancel → do nothing

        # Clean up resources
        self.media_player.destroy()
        self.destroy()