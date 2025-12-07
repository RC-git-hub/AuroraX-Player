import os
from tkinter import ttk, messagebox
# Get the absolute path to the DLL folder
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
dll_dir = os.path.join(base_dir, "assets", "libs")

# Add it to PATH so Python can find libmpv-2.dll
os.environ["PATH"] = dll_dir + os.pathsep + os.environ["PATH"]

import mpv
import customtkinter as ctk

class MediaPlayer(ctk.CTkFrame):
    def __init__(self, parent, state):
        super().__init__(parent)
        self.state = state
        self.player = None
        self.after(100, self._init_players)

    def _init_players(self):
        # Create mpv player instance
        self.player = mpv.MPV(
            wid=str(self.winfo_id()),
            #background="#333333"
        )

    def play_next(self):
        self.stop()

        if self.state.shuffle or ((self.state.loop != 0) and (not self.state.is_stopped)):
            self.state.current_index = self.state.next_index()
            if self.state.current_index != -1:
                self.state.path = self.state.current_song_list[self.state.current_index]
                self.load_media()
                self.play()


    def load_media(self):
        path = self.state.path
        if not path:
            return

        try:
            ext = os.path.splitext(path)[1].lower()

            audio_exts = [".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".opus"]

            # 🎵 If audio → disable video output
            if ext in audio_exts:
                self.player["vid"] = "no"
            else:
                self.player["vid"] = "yes"  # video mode

            # Reset states
            self.player.stop()
            self.player.pause = False
            self.state.is_paused = False
            self.state.is_stopped = False

            # Play media
            self.player.play(path)

        except Exception as e:
            messagebox.showerror("Error loading media:", e)

    def play(self):
        self.player.pause = False

    def pause(self):
        self.player.pause = True

    def stop(self):
        if self.player and self.player.filename:
            self.player.stop()  # Properly stop the video playback
            self.state.is_stopped = True
            self.state.is_paused = True


    def seek(self, percent):
        if self.player.duration:
            target = percent * self.player.duration
            self.player.seek(target, reference="absolute")
        else:
            # Retry after 50 ms
            self.after(50, lambda: self.seek(percent))

    def get_position(self):
        if self.player and self.player.time_pos is not None and self.player.duration:
            return self.player.time_pos / self.player.duration
        return 0.0

    def get_time(self):
        if self.player and self.player.time_pos is not None and self.player.duration:
            return int(self.player.time_pos), int(self.player.duration)
        return 0, 0

    def forward(self, seconds=5):
        if self.player and self.player.duration and self.player.time_pos is not None:
            new_time = self.player.time_pos + seconds
            if new_time >= self.player.duration:
                # Clamp to the end
                self.player.seek(self.player.duration, reference="absolute", precision="exact")
                self.player.pause = True
                self.state.is_stopped = True
            else:
                self.player.seek(new_time, reference="absolute", precision="exact")
        else:
            messagebox.showerror("Error", "Unable to retrieve video duration or time position.")

    def backward(self, seconds=5):
        if self.player and self.player.duration and self.player.time_pos is not None:
            new_time = max(self.player.time_pos - seconds, 0)
            self.player.seek(new_time, reference="absolute", precision="exact")
        else:
            messagebox.showerror("Error", "Unable to retrieve video duration or time position.")

    def destroy(self):
        if self.player:
            self.player.terminate()
        super().destroy()

