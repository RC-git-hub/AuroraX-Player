import os
from tkinter import filedialog

class FileLoader:
    def load(self, allowed_exts):
        folder = filedialog.askdirectory(title="Select Video Folder", initialdir=os.getcwd())
        if not folder:
            return [], None
        files = [f for f in os.listdir(folder) if f.lower().endswith(tuple(allowed_exts))]
        return files, folder