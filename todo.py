import customtkinter as ctk
import tkinter as tk
from tkinter import Toplevel
import sqlite3

# Theme of app
BG_COLOR = "#2a1045"
HEADER_COLOR = "#3c1e5d"
TEXT_COLOR = "white"
TASK_COLOR = "#3c1e5d"
BUTTON_COLOR = "#5b2872"
BUTTON_HOVER = "#a064c9"
BORDER = "#a855f7"
DIM_TEXT = "#7d7c7c"
PLACEHOLDER="#bbbbbb"

# Adding database
conn = sqlite3.connect("tasks.db")
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        completed INTEGER NOT NULL DEFAULT 0
    )
""")
conn.commit()

# app window
ctk.set_appearance_mode("System")
app = ctk.CTk()
app.title("To-Do List")
app.geometry("320x400")
app.configure(fg_color=BG_COLOR)

tasks = []

# updates if the task is complete or not
def update_progress():
    total = len(tasks)
    completed = sum(1 for _, var, _ in tasks if var.get())
    progress_label.configure(text=f"{completed}/{total}")
    update_placeholder()

#placeholder function
def update_placeholder():
    if not tasks:
        placeholder_label.pack(pady=10)
    else:
        placeholder_label.pack_forget()

#updates checkboxes
def toggle_task(var, checkbox, task_id):
    if var.get():
        checkbox.configure(text_color=DIM_TEXT, font=("Segoe UI", 20))
        c.execute("UPDATE tasks SET completed=1 WHERE id=?", (task_id,))
    else:
        checkbox.configure(text_color=TEXT_COLOR, font=("Segoe UI", 20))
        c.execute("UPDATE tasks SET completed=0 WHERE id=?", (task_id,))
    conn.commit()
    update_progress()

#adding tasks 
def add_task():
    task_text = entry.get().strip()
    if task_text:
        c.execute("INSERT INTO tasks (text, completed) VALUES (?, 0)", (task_text,))
        task_id = c.lastrowid
        conn.commit()
        entry.delete(0, 'end')
        create_task_widget(task_text, False, task_id)
        update_progress()

#add the tasks and checkbox
def create_task_widget(text, completed, task_id):
    var = ctk.BooleanVar(value=completed)
    checkbox = ctk.CTkCheckBox(
        task_frame,
        text=text,
        variable=var,
        command=lambda: toggle_task(var, checkbox, task_id),
        fg_color=BUTTON_COLOR,
        hover_color=BUTTON_HOVER,
        text_color=DIM_TEXT if completed else TEXT_COLOR,
        font=("Segoe UI", 20, "overstrike" if completed else "normal")
    )
    checkbox.pack(anchor="w", padx=10, pady=2)
    tasks.append((checkbox, var, task_id))
    update_placeholder()

#deleting the completed tasks
def delete_completed_tasks():
    for checkbox, var, task_id in tasks[:]:
        if var.get():
            checkbox.destroy()
            tasks.remove((checkbox, var, task_id))
            c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    update_progress()

#deleting all the tasks
def delete_all_tasks():
    for checkbox, _, _ in tasks:
        checkbox.destroy()
    tasks.clear()
    c.execute("DELETE FROM tasks")
    conn.commit()
    update_progress()

#Popup menu using Toplevel
menu_popup = None

#popup menu window setup
def show_menu_popup():
    global menu_popup
    if menu_popup and menu_popup.winfo_exists():
        menu_popup.destroy()
        menu_popup = None
        return
    
    menu_popup = tk.Toplevel(app)
    menu_popup.wm_overrideredirect(True)
    menu_popup.configure(bg=BG_COLOR)

    x = menu_button.winfo_rootx()
    y = menu_button.winfo_rooty() + menu_button.winfo_height()
    menu_popup.geometry(f"+{x}+{y}")
    
    #closing popup menu
    def close():
        global menu_popup
        if menu_popup:
            menu_popup.destroy()
            menu_popup = None
    
    #buttons in menu popup
    ctk.CTkButton(menu_popup, text="Delete completed tasks", command=lambda: [delete_completed_tasks(), close()], fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER, text_color="white", font=("Segoe UI", 14), width=180).pack(padx=5, pady=5)

    ctk.CTkButton(menu_popup, text="Delete all tasks", command=lambda: [delete_all_tasks(), close()], fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER, text_color="white", font=("Segoe UI", 14), width=180).pack(padx=5, pady=(0, 5))

#Top frame
top_frame = ctk.CTkFrame(app, fg_color=HEADER_COLOR)
top_frame.pack(pady=10, fill="x", padx=10)

#menu button
menu_button = ctk.CTkButton(top_frame, text="⋯", width=20, fg_color=BUTTON_COLOR, hover_color=BUTTON_HOVER, text_color="white", font=("Segoe UI", 22, "bold"), command=show_menu_popup)
menu_button.pack(side="left", padx=7, pady=7)

# shows title "My tasks" hehe
title_label = ctk.CTkLabel(top_frame, text="My Tasks", font=("Segoe UI", 18), text_color=TEXT_COLOR)
title_label.pack(side="left", padx=5, pady=10)

#shows tasks progress
progress_label = ctk.CTkLabel(top_frame, text="0/0", font=("Segoe UI", 14), text_color="white")
progress_label.pack(side="right", padx=7, pady=7)

# task frame
task_frame = ctk.CTkScrollableFrame(app, fg_color=TASK_COLOR)
task_frame.pack(expand=True, fill="both", padx=10, pady=1)

#placeholder in task frame
placeholder_label = ctk.CTkLabel(task_frame, text="No tasks yet", font=("Segoe UI", 18), text_color=PLACEHOLDER)

#bottom frame
bottom_frame = ctk.CTkFrame(app, fg_color=BG_COLOR)
bottom_frame.pack(fill="x", padx=10, pady=(0, 10))

#Adding task entry
entry = ctk.CTkEntry(bottom_frame, placeholder_text="+ Add new task",placeholder_text_color=PLACEHOLDER, height=35, border_color=BORDER, border_width=2, fg_color=TASK_COLOR, text_color=TEXT_COLOR)
entry.pack(fill="x")
entry.bind("<Return>", lambda event: add_task())

# Load tasks from database
c.execute("SELECT id, text, completed FROM tasks")
for task_id, text, completed in c.fetchall():
    create_task_widget(text, bool(completed), task_id)
update_progress()

# Run
app.mainloop()
conn.close()
