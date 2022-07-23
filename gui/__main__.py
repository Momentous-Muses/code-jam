import tkinter as tk


class MainApplication(tk.Frame):
    """The main application."""

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.server_process = None


def run_gui():
    """Setup TK root and add the main frame."""
    root = tk.Tk()
    app = MainApplication(root)
    app.pack(side="top", fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    run_gui()
