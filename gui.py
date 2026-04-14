import tkinter as tk
from tkinter import messagebox
import json, os
from datetime import datetime

FILE_NAME = "expenses.json"
BUDGET_FILE = "budgets.json"

# ---------- Data ----------
def load_expenses():
    if not os.path.exists(FILE_NAME):
        return []
    with open(FILE_NAME, "r") as f:
        return json.load(f)

def save_expenses(data):
    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=4)

def load_budgets():
    if not os.path.exists(BUDGET_FILE):
        return {"weekly": 0, "monthly": 0}
    with open(BUDGET_FILE, "r") as f:
        return json.load(f)

def save_budgets(data):
    with open(BUDGET_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------- Calculations ----------
def get_weekly():
    today = datetime.now()
    return sum(e["amount"] for e in load_expenses()
               if 0 <= (today - datetime.strptime(e["date"], "%Y-%m-%d")).days < 7)

def get_monthly():
    today = datetime.now()
    return sum(e["amount"] for e in load_expenses()
               if datetime.strptime(e["date"], "%Y-%m-%d").month == today.month)

# ---------- Theme ----------
dark = True

def theme():
    bg = "#121212" if dark else "#f4f4f4"
    fg = "white" if dark else "black"

    root.configure(bg=bg)
    main.configure(bg=bg)
    for f in frames:
        f.configure(bg=bg)

# ---------- Rounded Button ----------
def rounded_button(parent, text, color, command):
    btn = tk.Label(parent, text=text, bg=color, fg="white",
                   padx=15, pady=8, cursor="hand2",
                   font=("Segoe UI", 10, "bold"))
    btn.bind("<Button-1>", lambda e: command())
    btn.bind("<Enter>", lambda e: btn.config(bg="#666"))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn

# ---------- Functions ----------
def show_frame(frame):
    for f in frames:
        f.pack_forget()
    frame.pack(fill="both", expand=True)

def refresh():
    listbox.delete(0, tk.END)
    for i, e in enumerate(load_expenses()):
        listbox.insert(tk.END, f"{i+1}. ₹{e['amount']} | {e['category']}")

    b = load_budgets()
    weekly_lbl.config(text=f"₹{b['weekly'] - get_weekly()}")
    monthly_lbl.config(text=f"₹{b['monthly'] - get_monthly()}")

def add():
    try:
        data = load_expenses()
        data.append({
            "amount": float(amount.get()),
            "category": category.get(),
            "description": desc.get(),
            "date": datetime.now().strftime("%Y-%m-%d")
        })
        save_expenses(data)
        refresh()
    except:
        messagebox.showerror("Error", "Invalid input")

def delete():
    try:
        i = listbox.curselection()[0]
        data = load_expenses()
        data.pop(i)
        save_expenses(data)
        refresh()
    except:
        messagebox.showerror("Error", "Select item")

def save_budget():
    save_budgets({
        "weekly": float(week_entry.get()),
        "monthly": float(month_entry.get())
    })
    messagebox.showinfo("Saved", "Budget updated")
    refresh()

def toggle():
    global dark
    dark = not dark
    theme()

# ---------- UI ----------
root = tk.Tk()
root.title("Expense Tracker Pro")
root.geometry("1000x600")

# Sidebar
sidebar = tk.Frame(root, bg="#1e1e2f", width=200)
sidebar.pack(side="left", fill="y")

main = tk.Frame(root)
main.pack(fill="both", expand=True)

# Frames
dashboard = tk.Frame(main)
analytics = tk.Frame(main)
budget = tk.Frame(main)

frames = [dashboard, analytics, budget]

# Sidebar buttons (icons included)
rounded_button(sidebar, "🏠 Dashboard", "#3498db",
               lambda: show_frame(dashboard)).pack(pady=15)

rounded_button(sidebar, "📊 Analytics", "#9b59b6",
               lambda: show_frame(analytics)).pack(pady=15)

rounded_button(sidebar, "💰 Budget", "#2ecc71",
               lambda: show_frame(budget)).pack(pady=15)

rounded_button(sidebar, "🌗 Toggle Theme", "#e67e22",
               toggle).pack(pady=15)

# ---------- Dashboard ----------
weekly_lbl = tk.Label(dashboard, text="₹0", font=("Segoe UI", 16))
monthly_lbl = tk.Label(dashboard, text="₹0", font=("Segoe UI", 16))

weekly_lbl.pack()
monthly_lbl.pack()

listbox = tk.Listbox(dashboard, width=60, height=15)
listbox.pack(pady=10)

amount = tk.Entry(dashboard)
category = tk.Entry(dashboard)
desc = tk.Entry(dashboard)

amount.pack()
category.pack()
desc.pack()

rounded_button(dashboard, "➕ Add Expense", "#2ecc71", add).pack(pady=5)
rounded_button(dashboard, "🗑 Delete", "#e74c3c", delete).pack(pady=5)

# ---------- Analytics ----------
tk.Label(analytics, text="📊 Analytics Coming Soon",
         font=("Segoe UI", 16)).pack(pady=100)

# ---------- Budget ----------
week_entry = tk.Entry(budget)
month_entry = tk.Entry(budget)

week_entry.pack(pady=10)
month_entry.pack(pady=10)

rounded_button(budget, "💾 Save Budget", "#3498db",
               save_budget).pack(pady=10)

# Start
show_frame(dashboard)
theme()
refresh()

root.mainloop()
