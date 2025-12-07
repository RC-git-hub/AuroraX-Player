import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk

class ControlPanel(ctk.CTkFrame):
    def __init__(self, parent, state, media_player, icons):
        super().__init__(parent)
        self.media_player = media_player
        self.state = state
        self.icons = icons
        self.root = self.winfo_toplevel()

        # Bind keys to methods
        self.root.bind("<s>", lambda event: self.stop())
        self.root.bind("<space>", lambda event: self.toggle_play_pause())
        self.root.bind("<l>", lambda event: self.media_player.forward(10))
        self.root.bind("<j>", lambda event: self.media_player.backward(10))
        self.root.bind("<k>", lambda event: self.toggle_play_pause())

        # Build the Control Panel UI
        self.build_ui()

    def build_ui(self):

        # Play/Pause Button
        self.btn_play_pause = ctk.CTkButton(
            master=self,
            image=self.icons["pause"],  # Initial icon
            text="",
            corner_radius=10,
            width=40,
            height=40,
            fg_color=("gray90", "gray20"),
            hover_color="gray",
            command=self.toggle_play_pause
        )
        self.btn_play_pause.grid(row=0, column=1, padx=10, pady=5)

        # Backward Button
        self.btn_backward = ctk.CTkButton(
            master=self,
            image=self.icons["backward"],
            text="",
            width=40,
            height=40,
            fg_color=("gray90", "gray20"),
            hover_color="gray",
            command=lambda: self.media_player.backward(5)
        )
        self.btn_backward.grid(row=0, column=0, padx=10, pady=5)

        # Forward Button
        self.btn_forward = ctk.CTkButton(
            master=self,
            image=self.icons["forward"],
            text="",
            width=40,
            height=40,
            fg_color=("gray90", "gray20"),
            hover_color="gray",
            command=lambda: self.media_player.forward(5)
        )
        self.btn_forward.grid(row=0, column=2, padx=10, pady=5)

        # Stop Button
        self.btn_stop = ctk.CTkButton(
            master=self,
            image=self.icons["stop"],
            text="",
            width=40,
            height=40,
            corner_radius=10,
            fg_color=("gray90", "gray20"),
            hover_color="gray",
            command=self.stop
        )
        self.btn_stop.grid(row=0, column=3, padx=10, pady=5)

        # Shuffle Button
        self.btn_shuffle = ctk.CTkButton(
            master=self,
            image=self.icons["shuffle"],
            text="",
            width=40,
            height=40,
            fg_color=("gray90", "gray20"),
            hover_color="gray",
            command=self.toggle_shuffle  # You will implement this
        )
        self.btn_shuffle.grid(row=0, column=7, padx=10, pady=5)

        # Loop Button
        self.btn_loop = ctk.CTkButton(
            master=self,
            image=self.icons["loop_0"],
            text="",
            width=40,
            height=40,
            fg_color=("gray90", "gray20"),
            hover_color="gray",
            command=self.toggle_loop  # You will implement this
        )
        self.btn_loop.grid(row=0, column=6, padx=10, pady=5)

        # Seek Slider
        self.seek_slider = ctk.CTkSlider(
            self,
            from_=0,
            to=1,
            number_of_steps=1000,
            command=self.on_seek,
            progress_color="deepskyblue",
            fg_color=("gray90", "gray20")
        )
        self.seek_slider.grid(row=0, column=4, sticky="ew", padx=20, pady=10)
        self.columnconfigure(4, weight=1)

        # Time Label
        self.lbl_time = ctk.CTkLabel(
            self,
            text="00:00 / 00:00",
            font=("Arial", 12, "bold"),
        )
        self.lbl_time.grid(row=0, column=5, padx=15, pady=5)

        # Start UI updates
        self.update_loop()

    def toggle_shuffle(self):
        self.state.shuffle = not self.state.shuffle 
        self.btn_shuffle.configure(
            fg_color="deepskyblue" if self.state.shuffle else ("gray90", "gray20"),
            hover_color="deepskyblue" if self.state.shuffle else "gray"
        )


    def toggle_loop(self):
        if self.state.loop == 0:
            self.state.loop = 1
            self.btn_loop.configure(image=self.icons["loop_1"])
        elif self.state.loop == 1:
            self.state.loop = 2
            self.btn_loop.configure(image=self.icons["loop_2"])
        else:
            self.state.loop = 0
            self.btn_loop.configure(image=self.icons["loop_0"])


    def toggle_play_pause(self):
        if self.state.is_paused == True:
            self.media_player.play()
            self.state.is_paused = False
            self.btn_play_pause.configure(image=self.icons["pause"])
        else:
            self.media_player.pause()
            self.state.is_paused = True
            self.btn_play_pause.configure(image=self.icons["play"])

    def stop(self):
        # Reset playback state
        self.media_player.stop()
        self.state.reset_all()
        self.state.is_stopped = True
        self.state.is_paused = True

        # Reset UI elements
        self.btn_play_pause.configure(image=self.icons["play"])
        self.seek_slider.set(0)
        self.lbl_time.configure(text="00:00 / 00:00")
        

    def on_seek(self, value):
        self.media_player.seek(value)

    def update_loop(self):
        try:
            # --- Get playback position safely ---
            pos = self.media_player.get_position()
            if pos is not None:
                try:
                    self.seek_slider.set(pos)
                except tk.TclError:
                    # Widget temporarily unavailable (playlist reload, dialogs, etc.)
                    return self.after(150, self.update_loop)

            # --- Get times safely ---
            current, total = self.media_player.get_time()
            if (
                current is not None 
                and total is not None 
                and total > 0
            ):
                try:
                    self.lbl_time.configure(
                        text=f"{current//60:02d}:{current%60:02d} / {total//60:02d}:{total%60:02d}"
                    )
                except tk.TclError:
                    return self.after(150, self.update_loop)
            elif (
                current is not None 
                and total is not None
                and (self.state.loop != 0 or self.state.shuffle)
            ): 
                if  total > 0 and (total - current) < 0.1:
                    try:
                        self.media_player.play_next()
                    except tk.TclError:
                        return self.after(150, self.update_loop)
        except Exception as e:
            # Show error to the user instead of printing
            messagebox.showerror("Media Player Error", f"An error occurred:\n{e}")

        finally:
            # Smooth update ~6× per second (safe for Tk)
            self.after(150, self.update_loop)
