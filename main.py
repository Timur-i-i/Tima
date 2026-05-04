import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class MovieLibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 Movie Library")
        self.root.geometry("700x500")
        self.movies = []
        self.load_movies()

        # --- Основной фрейм для формы ---
        form_frame = tk.LabelFrame(root, text="Добавить новый фильм", padx=10, pady=10)
        form_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # --- Поля ввода ---
        tk.Label(form_frame, text="Название:").grid(row=0, column=0, sticky="e")
        self.title_entry = tk.Entry(form_frame, width=40)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Жанр:").grid(row=1, column=0, sticky="e")
        self.genre_entry = tk.Entry(form_frame, width=40)
        self.genre_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Год выпуска:").grid(row=2, column=0, sticky="e")
        self.year_entry = tk.Entry(form_frame, width=15)
        self.year_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        tk.Label(form_frame, text="Рейтинг (0-10):").grid(row=3, column=0, sticky="e")
        self.rating_entry = tk.Entry(form_frame, width=15)
        self.rating_entry.grid(row=3, column=1, sticky="w", padx=5, pady=5)

        # --- Кнопка ---
        self.add_btn = tk.Button(
            form_frame,
            text="➕ Добавить фильм",
            command=self.add_movie,
            bg="#4CAF50",
            fg="white"
        )
        self.add_btn.grid(row=4, column=0, columnspan=2, pady=20)

        # --- Таблица ---
        columns = ("title", "genre", "year", "rating")
        self.tree = ttk.Treeview(root, columns=columns, show='headings')
        self.tree.heading("title", text="Название")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("year", text="Год")
        self.tree.heading("rating", text="Рейтинг")

         # Добавляем скроллбар
         yscroll = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
         self.tree.configure(yscroll=yscroll.set)

         self.tree.grid(row=1, column=0, sticky="nsew", padx=10)
         yscroll.grid(row=1, column=1, sticky="ns")

         # Настройка весов для растягивания окна
         root.grid_rowconfigure(1, weight=1)
         root.grid_columnconfigure(0, weight=1)

         # --- Фильтры ---
         filter_frame = tk.LabelFrame(root, text="Фильтрация", padx=10, pady=5)
         filter_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

         tk.Label(filter_frame, text="Жанр:").grid(row=0, column=0, sticky="e")
         self.filter_genre = tk.Entry(filter_frame)
         self.filter_genre.grid(row=0, column=1, padx=5, pady=5)

         tk.Label(filter_frame, text="Год:").grid(row=1, column=0, sticky="e")
         self.filter_year = tk.Entry(filter_frame)
         self.filter_year.grid(row=1, column=1, padx=5, pady=5)

         self.filter_btn = tk.Button(
             filter_frame,
             text="🔍 Применить фильтр",
             command=self.apply_filter,
             bg="#2196F3",
             fg="white"
         )
         self.filter_btn.grid(row=2, column=0, columnspan=2, pady=10)

         # Заполнение таблицы при запуске
         self.update_table()

    def validate_input(self):
        """Проверяет корректность введенных данных."""
        title = self.title_entry.get().strip()
        genre = self.genre_entry.get().strip()
        year = self.year_entry.get().strip()
        rating = self.rating_entry.get().strip()

        if not title or not genre or not year or not rating:
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения!")
            return False

        if not year.isdigit():
            messagebox.showerror("Ошибка", "Год должен быть числом!")
            return False

        try:
            rating_val = float(rating)
            if not (0 <= rating_val <= 10):
                raise ValueError("Рейтинг вне диапазона 0-10.")
            year_val = int(year)
            return {"title": title, "genre": genre, "year": year_val, "rating": rating_val}
        
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Рейтинг должен быть числом от 0 до 10!\n{str(e)}")
            return False

    def add_movie(self):
        """Добавляет фильм в библиотеку."""
        movie_data = self.validate_input()
        
        if movie_data:
            self.movies.append(movie_data)
            self.clear_entries()
            self.update_table()
            self.save_movies()
            messagebox.showinfo("Успех", "Фильм добавлен в библиотеку!")

    def clear_entries(self):
        """Очищает поля ввода."""
         self.title_entry.delete(0, tk.END)
         self.genre_entry.delete(0, tk.END)
         self.year_entry.delete(0, tk.END)
         self.rating_entry.delete(0, tk.END)
         self.title_entry.focus()

    def update_table(self):
        """Обновляет данные в таблице."""
         for i in self.tree.get_children():
             self.tree.delete(i)
         for movie in self.movies:
             self.tree.insert("", tk.END, values=(movie["title"], movie["genre"], movie["year"], movie["rating"]))

    def apply_filter(self):
         """Применяет фильтр по жанру и/или году."""
         genre_filter = self.filter_genre.get().lower()
         year_filter = self.filter_year.get()
         
         filtered_movies = self.movies

         if genre_filter:
             filtered_movies = [m for m in filtered_movies if genre_filter in m["genre"].lower()]
         
         if year_filter.isdigit():
             filtered_movies = [m for m in filtered_movies if m["year"] == int(year_filter)]
         
         # Очистка таблицы перед вставкой отфильтрованных данных
         for i in self.tree.get_children():
             self.tree.delete(i)
         
         for movie in filtered_movies:
             self.tree.insert("", tk.END, values=(movie["title"], movie["genre"], movie["year"], movie["rating"]))

    def save_movies(self):
         """Сохраняет данные в JSON файл."""
         with open("movies.json", "w", encoding="utf-8") as f:
             json.dump(self.movies, f, ensure_ascii=False, indent=4)

    def load_movies(self):
         """Загружает данные из JSON файла при старте."""
         if os.path.exists("movies.json"):
             try:
                 with open("movies.json", "r", encoding="utf-8") as f:
                     data = json.load(f)
                     if isinstance(data, list):
                         self.movies = data
             except (json.JSONDecodeError, FileNotFoundError):
                 messagebox.showwarning("Загрузка", "Файл данных поврежден или отсутствует. Будет создан новый.")
                 self.movies = []


if __name__ == "__main__":
    root = tk.Tk()
    app = MovieLibraryApp(root)
    root.mainloop()
