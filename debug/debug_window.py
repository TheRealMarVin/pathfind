import tkinter as tk
from threading import Thread
from queue import Queue, Empty

import config

debug_queue = Queue()
debug_thread = None
debug_ui = None
debug_enabled = False

class DebugWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Debug Info")
        self.labels = {}

        self.keys = config.CONFIG["display_debug_values"]
        for key in self.keys:
            label = tk.Label(self.root, text=f"{key}: ...")
            label.pack(anchor="w")
            self.labels[key] = label

        self.running = True
        self.visible = True
        self.root.protocol("WM_DELETE_WINDOW", self._hide_only)
        self.root.after(100, self.update_labels)

    def update_labels(self):
        try:
            while True:
                data = debug_queue.get_nowait()
                for key, value in data.items():
                    if key in self.labels:
                        self.labels[key].config(text=f"{key}: {value}")
        except Empty:
            pass

        if self.running:
            self.root.after(100, self.update_labels)

    def _hide_only(self):
        self.root.withdraw()
        self.visible = False

    def _show_only(self):
        self.root.deiconify()
        self.visible = True

    def toggle_visibility(self):
        if self.visible:
            self.root.after(0, self._hide_only)
        else:
            self.root.after(0, self._show_only)

    def run(self):
        self.root.mainloop()

def toggle_debug_window():
    global debug_enabled, debug_thread, debug_ui

    if debug_ui:
        debug_ui.toggle_visibility()
        debug_enabled = debug_ui.visible
    else:
        def thread_func():
            global debug_ui
            debug_ui = DebugWindow()
            debug_ui.run()

        debug_thread = Thread(target=thread_func, daemon=True)
        debug_thread.start()
        debug_enabled = True
