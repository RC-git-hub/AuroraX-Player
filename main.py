from app.ui.main_app import MainApp

if __name__ == "__main__":
    app = MainApp()
    app.protocol("WM_DELETE_WINDOW", lambda: app.on_close())
    app.mainloop()