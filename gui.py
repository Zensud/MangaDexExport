import json
import tkinter as tk
from tkinter import ttk, messagebox


class MangaLibraryGUI(tk.Tk):
    """Simple GUI for browsing a MangaDex library export."""

    def __init__(self, library_path: str = "library.json") -> None:
        super().__init__()
        self.title("Manga Library")
        self.geometry("600x400")
        self.library_path = library_path
        self.library = self._load_library()
        self._build_ui()

    def _load_library(self) -> list:
        """Load the exported library JSON file."""
        try:
            with open(self.library_path, "r", encoding="utf-8") as handle:
                return json.load(handle)
        except FileNotFoundError:
            messagebox.showerror("Missing file", f"Could not find '{self.library_path}'.")
        except json.JSONDecodeError:
            messagebox.showerror("Invalid JSON", f"Failed to parse '{self.library_path}'.")
        return []

    def _build_ui(self) -> None:
        """Construct the main interface."""
        columns = ("title", "author")
        tree = ttk.Treeview(self, columns=columns, show="headings")
        tree.heading("title", text="Title")
        tree.heading("author", text="Author(s)")
        tree.pack(fill=tk.BOTH, expand=True)

        for entry in self.library:
            title = entry.get("title", "Unknown")
            author = ", ".join(entry.get("authors", []))
            tree.insert("", tk.END, values=(title, author))

        tree.bind("<<TreeviewSelect>>", lambda e: self._show_details(tree))

    def _show_details(self, tree: ttk.Treeview) -> None:
        """Display details for the selected manga."""
        selected = tree.selection()
        if not selected:
            return
        index = tree.index(selected[0])
        manga = self.library[index]
        title = manga.get("title", "Manga")
        description = manga.get("description", "No description available.")
        messagebox.showinfo(title, description)


def main() -> None:
    gui = MangaLibraryGUI()
    gui.mainloop()


if __name__ == "__main__":
    main()
