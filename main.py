import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

DATA_FILE = "books.json"


class BookTrackerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Book Tracker")
        self.root.geometry("900x600")

        self.books = []

        self._build_ui()
        self.load_data(show_message=False)

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        form = ttk.LabelFrame(main, text="Добавить книгу", padding=10)
        form.pack(fill="x")

        ttk.Label(form, text="Название:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.title_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.title_var, width=35).grid(row=0, column=1, padx=4, pady=4)

        ttk.Label(form, text="Автор:").grid(row=0, column=2, sticky="w", padx=4, pady=4)
        self.author_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.author_var, width=30).grid(row=0, column=3, padx=4, pady=4)

        ttk.Label(form, text="Жанр:").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.genre_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.genre_var, width=35).grid(row=1, column=1, padx=4, pady=4)

        ttk.Label(form, text="Страниц:").grid(row=1, column=2, sticky="w", padx=4, pady=4)
        self.pages_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.pages_var, width=30).grid(row=1, column=3, padx=4, pady=4)

        ttk.Button(form, text="Добавить книгу", command=self.add_book).grid(row=2, column=0, columnspan=4, pady=(8, 2))

        filter_frame = ttk.LabelFrame(main, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", pady=(10, 0))

        ttk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.filter_genre_var = tk.StringVar(value="Все")
        self.genre_combo = ttk.Combobox(filter_frame, textvariable=self.filter_genre_var, state="readonly", width=30)
        self.genre_combo.grid(row=0, column=1, padx=4, pady=4)
        self.genre_combo.bind("<<ComboboxSelected>>", lambda _: self.apply_filters())

        self.pages_filter_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            filter_frame,
            text="Только книги > 200 страниц",
            variable=self.pages_filter_var,
            command=self.apply_filters,
        ).grid(row=0, column=2, padx=8, pady=4, sticky="w")

        ttk.Button(filter_frame, text="Сброс фильтров", command=self.reset_filters).grid(row=0, column=3, padx=4, pady=4)

        table_frame = ttk.LabelFrame(main, text="Список книг", padding=10)
        table_frame.pack(fill="both", expand=True, pady=(10, 0))

        columns = ("title", "author", "genre", "pages")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=14)
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("pages", text="Страниц")

        self.tree.column("title", width=260)
        self.tree.column("author", width=220)
        self.tree.column("genre", width=170)
        self.tree.column("pages", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        controls = ttk.Frame(main)
        controls.pack(fill="x", pady=(10, 0))

        ttk.Button(controls, text="Сохранить в JSON", command=self.save_data).pack(side="left", padx=4)
        ttk.Button(controls, text="Загрузить из JSON", command=self.load_data).pack(side="left", padx=4)
        ttk.Button(controls, text="Удалить выбранную", command=self.remove_selected).pack(side="left", padx=4)

    def _validate_book(self, title: str, author: str, genre: str, pages_str: str):
        if not title or not author or not genre or not pages_str:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены.")
            return None

        try:
            pages = int(pages_str)
            if pages <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть положительным числом.")
            return None

        return {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages,
        }

    def add_book(self):
        book = self._validate_book(
            self.title_var.get().strip(),
            self.author_var.get().strip(),
            self.genre_var.get().strip(),
            self.pages_var.get().strip(),
        )
        if not book:
            return

        self.books.append(book)
        self.title_var.set("")
        self.author_var.set("")
        self.genre_var.set("")
        self.pages_var.set("")

        self._refresh_genres()
        self.apply_filters()

    def _refresh_genres(self):
        genres = sorted({b["genre"] for b in self.books})
        current = self.filter_genre_var.get()
        values = ["Все"] + genres
        self.genre_combo["values"] = values
        if current not in values:
            self.filter_genre_var.set("Все")

    def apply_filters(self):
        genre_filter = self.filter_genre_var.get()
        pages_filter = self.pages_filter_var.get()

        filtered = self.books

        if genre_filter and genre_filter != "Все":
            filtered = [b for b in filtered if b["genre"] == genre_filter]

        if pages_filter:
            filtered = [b for b in filtered if b["pages"] > 200]

        self._fill_table(filtered)

    def _fill_table(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for book in rows:
            self.tree.insert("", "end", values=(book["title"], book["author"], book["genre"], book["pages"]))

    def reset_filters(self):
        self.filter_genre_var.set("Все")
        self.pages_filter_var.set(False)
        self.apply_filters()

    def remove_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Сначала выберите книгу в таблице.")
            return

        values = self.tree.item(selected[0], "values")
        if not values:
            return

        target = {
            "title": values[0],
            "author": values[1],
            "genre": values[2],
            "pages": int(values[3]),
        }

        for idx, book in enumerate(self.books):
            if book == target:
                del self.books[idx]
                break

        self._refresh_genres()
        self.apply_filters()

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.books, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", f"Данные сохранены в {os.path.abspath(DATA_FILE)}")
        except OSError as err:
            messagebox.showerror("Ошибка", f"Не удалось сохранить файл: {err}")

    def load_data(self, show_message=True):
        if not os.path.exists(DATA_FILE):
            self.books = []
            self._refresh_genres()
            self.apply_filters()
            if show_message:
                messagebox.showwarning("Внимание", "Файл books.json не найден. Загружен пустой список.")
            return

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("Некорректный формат данных")

            validated = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                title = str(item.get("title", "")).strip()
                author = str(item.get("author", "")).strip()
                genre = str(item.get("genre", "")).strip()
                pages = item.get("pages")
                if title and author and genre and isinstance(pages, int) and pages > 0:
                    validated.append({"title": title, "author": author, "genre": genre, "pages": pages})

            self.books = validated
            self._refresh_genres()
            self.apply_filters()

            if show_message:
                messagebox.showinfo("Успех", "Данные успешно загружены.")
        except (OSError, json.JSONDecodeError, ValueError) as err:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {err}")


if __name__ == "__main__":
    root = tk.Tk()
    app = BookTrackerApp(root)
    root.mainloop()
