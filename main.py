import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
from datetime import datetime

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Expense Tracker")
        self.root.geometry("800x600")
        self.expenses = []
        self.load_expenses()

        # --- Основной фрейм для формы ---
        form_frame = tk.LabelFrame(root, text="Добавить расход", padx=10, pady=10)
        form_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        # --- Поля ввода ---
        tk.Label(form_frame, text="Сумма:").grid(row=0, column=0, sticky="e")
        self.amount_entry = tk.Entry(form_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Категория:").grid(row=1, column=0, sticky="e")
        self.category_entry = tk.Entry(form_frame, width=25)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Дата:").grid(row=2, column=0, sticky="e")
        self.date_picker = DateEntry(form_frame, width=15, background='darkblue',
                                    foreground='white', borderwidth=2)
        self.date_picker.grid(row=2, column=1, padx=5, pady=5)

        # --- Кнопка ---
        self.add_btn = tk.Button(
            form_frame,
            text="➕ Добавить расход",
            command=self.add_expense,
            bg="#4CAF50",
            fg="white"
        )
        self.add_btn.grid(row=3, column=0, columnspan=2, pady=20)

        # --- Таблица ---
        columns = ("amount", "category", "date")
        self.tree = ttk.Treeview(root, columns=columns, show='headings')
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")

         # Добавляем скроллбар
        yscroll = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=yscroll.set)

        self.tree.grid(row=1, column=0, sticky="nsew", padx=10)
        yscroll.grid(row=1, column=1, sticky="ns")

         # Настройка весов для растягивания окна
        root.grid_rowconfigure(1, weight=1)
        root.grid_columnconfigure(0, weight=1)

         # --- Фильтры и Сумма ---
        filter_frame = tk.LabelFrame(root, text="Фильтрация и Статистика", padx=10, pady=5)
        filter_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew")

        tk.Label(filter_frame, text="Категория:").grid(row=0, column=0, sticky="e")
        self.filter_category = tk.Entry(filter_frame)
        self.filter_category.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(filter_frame, text="Дата начала:").grid(row=1, column=0, sticky="e")
        self.start_date_picker = DateEntry(filter_frame, width=12,
                                          background='darkblue', foreground='white')
        self.start_date_picker.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        tk.Label(filter_frame, text="Дата окончания:").grid(row=2, column=0, sticky="e")
        self.end_date_picker = DateEntry(filter_frame, width=12,
                                        background='darkblue', foreground='white')
        self.end_date_picker.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        self.filter_btn = tk.Button(
             filter_frame,
             text="🔍 Применить фильтр",
             command=self.apply_filter,
             bg="#2196F3",
             fg="white"
         )
        self.filter_btn.grid(row=3, column=0, columnspan=2, pady=5)

        self.sum_label = tk.Label(filter_frame, text="Сумма расходов: 0 ₽", font=('Arial', 12))
        self.sum_label.grid(row=4, column=0, columnspan=2)

         # Заполнение таблицы при запуске и обновление суммы
        self.update_table()

    def validate_input(self):
        """Проверяет корректность введенных данных."""
        amount_str = self.amount_entry.get().strip()
        
        # Валидация: Сумма должна быть положительным числом
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Сумма должна быть больше нуля.")
            if len(str(amount).split('.')[1]) > 2: # Проверка на копейки (не более 2 знаков)
                raise ValueError("Слишком много знаков после запятой.")
            amount = round(amount, 2) # Округляем до 2 знаков
            
            category = self.category_entry.get().strip()
            if not category:
                raise ValueError("Категория обязательна.")
                
            date = self.date_picker.get_date().strftime('%Y-%m-%d')
            
            return {"amount": amount, "category": category, "date": date}
        
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            return False

    def add_expense(self):
        """Добавляет расход в базу данных."""
        expense_data = self.validate_input()
        
        if expense_data:
            self.expenses.append(expense_data)
            self.clear_entries()
            self.update_table()
            self.save_expenses()
            messagebox.showinfo("Успех", "Расход добавлен!")

    def clear_entries(self):
        """Очищает поля ввода."""
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
         # Дата сбрасывается на текущую автоматически в виджете DateEntry

    def update_table(self):
        """Обновляет данные в таблице и пересчитывает сумму."""
        for i in self.tree.get_children():
             self.tree.delete(i)
         
        for expense in self.expenses:
             # Форматируем сумму с пробелом как разделителем тысяч и запятой как десятичным разделителем (русский стиль)
             formatted_amount = "{:,.2f}".format(expense["amount"]).replace(",", " ").replace(".", ",")
             self.tree.insert("", tk.END, values=(f"{formatted_amount} ₽", expense["category"], expense["date"]))
         
         # Пересчет общей суммы всех расходов (без учета фильтров на этом этапе)
        total_sum = sum(item['amount'] for item in self.expenses)
        total_str = "{:,.2f}".format(total_sum).replace(",", " ").replace(".", ",")
        self.sum_label.config(text=f"Сумма расходов: {total_str} ₽")

    def apply_filter(self):
        """Применяет фильтр по категории и/или дате."""
        filtered_expenses = self.expenses

          # Фильтр по категории (без учета регистра)
        category_filter = self.filter_category.get().strip().lower()
        if category_filter:
            filtered_expenses = [e for e in filtered_expenses if category_filter in e["category"].lower()]
          
          # Фильтр по дате (включительно)
        try:
            start_date = self.start_date_picker.get_date()
            end_date = self.end_date_picker.get_date()
              
            if start_date and end_date and start_date > end_date:
                raise ValueError("Дата начала не может быть позже даты окончания.")
              
            if start_date:
                start_str = start_date.strftime('%Y-%m-%d')
                filtered_expenses = [e for e in filtered_expenses if e["date"] >= start_str]
              
            if end_date:
                end_str = end_date.strftime('%Y-%m-%d')
                filtered_expenses = [e for e in filtered_expenses if e["date"] <= end_str]
              
        except ValueError as e:
            messagebox.showerror("Ошибка даты", str(e))
            return

          # Очистка таблицы перед вставкой отфильтрованных данных
        for i in self.tree.get_children():
            self.tree.delete(i)
          
          # Вставка отфильтрованных данных в таблицу
        for expense in filtered_expenses:
            formatted_amount = "{:,.2f}".format(expense["amount"]).replace(",", " ").replace(".", ",")
            self.tree.insert("", tk.END, values=(f"{formatted_amount} ₽", expense["category"], expense["date"]))
          
          # Пересчет суммы для отфильтрованных данных
        total_sum = sum(item['amount'] for item in filtered_expenses)
        total_str = "{:,.2f}".format(total_sum).replace(",", " ").replace(".", ",")
        self.sum_label.config(text=f"Сумма расходов: {total_str} ₽")

    def save_expenses(self):
        """Сохраняет данные в JSON файл."""
        with open("expenses.json", "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=4)

    def load_expenses(self):
        """Загружает данные из JSON файла при старте."""
        if os.path.exists("expenses.json"):
            try:
                with open("expenses.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                          self.expenses = data
            except (json.JSONDecodeError, FileNotFoundError):
                messagebox.showwarning("Загрузка", "Файл данных поврежден или отсутствует. Будет создан новый.")
                self.expenses = []


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
