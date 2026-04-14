import json
import os
from datetime import datetime

FILE_NAME = "expenses.json"

def load_expenses():
    if not os.path.exists(FILE_NAME):
        return []
    with open(FILE_NAME, "r") as file:
        return json.load(file)

def save_expenses(expenses):
    with open(FILE_NAME, "w") as file:
        json.dump(expenses, file, indent=4)

BUDGET_FILE = "budgets.json"

def load_budgets():
    if not os.path.exists(BUDGET_FILE):
        return {"weekly": 0, "monthly": 0}
    with open(BUDGET_FILE, "r") as file:
        return json.load(file)

def save_budgets(budgets):
    with open(BUDGET_FILE, "w") as file:
        json.dump(budgets, file, indent=4)

def set_budget():
    budgets = load_budgets()

    weekly = float(input("Enter weekly budget: "))
    monthly = float(input("Enter monthly budget: "))

    budgets["weekly"] = weekly
    budgets["monthly"] = monthly

    save_budgets(budgets)
    print("✅ Budgets updated!")

def add_expense():
    amount = float(input("Enter amount: "))
    category = input("Enter category (food, travel, etc): ").lower()
    description = input("Enter description: ")
    date = datetime.now().strftime("%Y-%m-%d")

    expense = {
        "amount": amount,
        "category": category,
        "description": description,
        "date": date
    }

    expenses = load_expenses()
    expenses.append(expense)
    save_expenses(expenses)
    print("✅ Expense added!")
    check_budget()

def view_expenses(expenses=None):
    if expenses is None:
        expenses = load_expenses()

    if not expenses:
        print("No expenses found.")
        return

    total = 0
    for i, exp in enumerate(expenses, start=1):
        print(f"{i}. ₹{exp['amount']} | {exp['category']} | {exp['description']} | {exp['date']}")
        total += exp["amount"]

    print(f"\nTotal Spent: ₹{total}")

def delete_expense():
    expenses = load_expenses()
    if not expenses:
        print("No expenses to delete.")
        return

    view_expenses(expenses)

    try:
        index = int(input("Enter expense number to delete: ")) - 1
        if 0 <= index < len(expenses):
            removed = expenses.pop(index)
            save_expenses(expenses)
            print(f"🗑️ Deleted: ₹{removed['amount']} ({removed['description']})")
        else:
            print("Invalid number.")
    except ValueError:
        print("Enter a valid number.")

# 🔎 Search
def search_expenses():
    keyword = input("Enter keyword to search: ").lower()
    expenses = load_expenses()

    results = [
        exp for exp in expenses
        if keyword in exp["category"].lower() or keyword in exp["description"].lower()
    ]

    print("\n🔎 Search Results:")
    view_expenses(results)

# 🏷️ Filter
def filter_by_category():
    category = input("Enter category to filter: ").lower()
    expenses = load_expenses()

    filtered = [exp for exp in expenses if exp["category"] == category]

    print(f"\n📂 Expenses in '{category}':")
    view_expenses(filtered)

#  Edit
def edit_expense():
    expenses = load_expenses()
    if not expenses:
        print("No expenses to edit.")
        return

    view_expenses(expenses)

    try:
        index = int(input("Enter expense number to edit: ")) - 1

        if 0 <= index < len(expenses):
            exp = expenses[index]

            print("\nLeave blank to keep old value.")

            new_amount = input(f"Amount ({exp['amount']}): ")
            new_category = input(f"Category ({exp['category']}): ")
            new_description = input(f"Description ({exp['description']}): ")

            if new_amount:
                exp["amount"] = float(new_amount)
            if new_category:
                exp["category"] = new_category.lower()
            if new_description:
                exp["description"] = new_description

            save_expenses(expenses)
            print("✏️ Expense updated!")

        else:
            print("Invalid number.")
    except ValueError:
        print("Enter a valid number.")

#Daily Summary
def daily_summary():
    expenses = load_expenses()
    today = datetime.now().strftime("%Y-%m-%d")

    total = sum(exp["amount"] for exp in expenses if exp["date"] == today)

    print(f"\n📅 Today's Spending: ₹{total}")

def weekly_summary():
    expenses = load_expenses()
    today = datetime.now()

    total = 0
    for exp in expenses:
        exp_date = datetime.strptime(exp["date"], "%Y-%m-%d")
        diff = (today - exp_date).days

        if 0 <= diff < 7:
            total += exp["amount"]

    print(f"\n📆 Last 7 Days Spending: ₹{total}")

def monthly_summary():
    expenses = load_expenses()
    today = datetime.now()

    total = 0
    for exp in expenses:
        exp_date = datetime.strptime(exp["date"], "%Y-%m-%d")

        if exp_date.month == today.month and exp_date.year == today.year:
            total += exp["amount"]

    print(f"\n🗓️ This Month's Spending: ₹{total}")

#Category-wise Summary 
def category_summary():
    expenses = load_expenses()

    choice = input("View by (1) Month or (2) Year: ")

    totals = {}

    if choice == "1":
        month = int(input("Enter month (1-12): "))
        year = int(input("Enter year (e.g., 2026): "))

        for exp in expenses:
            exp_date = datetime.strptime(exp["date"], "%Y-%m-%d")

            if exp_date.month == month and exp_date.year == year:
                cat = exp["category"]
                totals[cat] = totals.get(cat, 0) + exp["amount"]

    elif choice == "2":
        year = int(input("Enter year: "))

        for exp in expenses:
            exp_date = datetime.strptime(exp["date"], "%Y-%m-%d")

            if exp_date.year == year:
                cat = exp["category"]
                totals[cat] = totals.get(cat, 0) + exp["amount"]

    else:
        print("Invalid choice.")
        return

    print("\n Category-wise Spending:")
    for cat, amt in totals.items():
        print(f"{cat}: ₹{amt}")

def get_weekly_spending():
    expenses = load_expenses()
    today = datetime.now()

    total = 0
    for exp in expenses:
        exp_date = datetime.strptime(exp["date"], "%Y-%m-%d")
        if 0 <= (today - exp_date).days < 7:
            total += exp["amount"]
    return total

def get_monthly_spending():
    expenses = load_expenses()
    today = datetime.now()

    total = 0
    for exp in expenses:
        exp_date = datetime.strptime(exp["date"], "%Y-%m-%d")
        if exp_date.month == today.month and exp_date.year == today.year:
            total += exp["amount"]
    return total

def check_budget():
    budgets = load_budgets()

    weekly_spent = get_weekly_spending()
    monthly_spent = get_monthly_spending()

    weekly_budget = budgets["weekly"]
    monthly_budget = budgets["monthly"]

    print("\n💰 Budget Status:")

    # Weekly
    if weekly_budget > 0:
        percent = (weekly_spent / weekly_budget) * 100

        if percent >= 100:
            print(f"🚨 Weekly budget exceeded! (₹{weekly_spent}/{weekly_budget})")
        elif percent >= 80:
            print(f"⚠️ Near weekly budget limit ({percent:.1f}%)")

    # Monthly
    if monthly_budget > 0:
        percent = (monthly_spent / monthly_budget) * 100

        if percent >= 100:
            print(f"🚨 Monthly budget exceeded! (₹{monthly_spent}/{monthly_budget})")
        elif percent >= 80:
            print(f"⚠️ Near monthly budget limit ({percent:.1f}%)")

def view_remaining_budget():
    budgets = load_budgets()

    weekly_budget = budgets["weekly"]
    monthly_budget = budgets["monthly"]

    weekly_spent = get_weekly_spending()
    monthly_spent = get_monthly_spending()

    print("\n💰 Remaining Budget Status:\n")

    # Weekly
    if weekly_budget > 0:
        remaining_weekly = weekly_budget - weekly_spent
        percent_weekly = (weekly_spent / weekly_budget) * 100
        print(f"Weekly Budget: ₹{weekly_budget}")
        print(f"Spent: ₹{weekly_spent}")
        print(f"Remaining: ₹{remaining_weekly}")
        print(f"Used: {percent_weekly:.1f}%")

        if percent_weekly >= 80:
            print("⚠️ Approaching weekly limit!")

        if remaining_weekly < 0:
            print("🚨 You have exceeded your weekly budget!")

    else:
        print("Weekly budget not set.")

    print()

    # Monthly
    if monthly_budget > 0:
        remaining_monthly = monthly_budget - monthly_spent
        percent_monthly = (monthly_spent / monthly_budget) * 100
        print(f"Monthly Budget: ₹{monthly_budget}")
        print(f"Spent: ₹{monthly_spent}")
        print(f"Remaining: ₹{remaining_monthly}")
        print(f"Used: {percent_monthly:.1f}%")
        
        if percent_monthly >= 80:
            print("⚠️ Approaching monthly limit!")

        if remaining_monthly < 0:
            print("🚨 You have exceeded your monthly budget!")

    else:
        print("Monthly budget not set.")

def main():
    while True:
        print("\n--- Expense Tracker ---")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Delete Expense")
        print("4. Search Expenses")
        print("5. Filter by Category")
        print("6. Edit Expense")
        print("7. Daily Summary")
        print("8. Weekly Summary")
        print("9. Monthly Summary")
        print("10. Category Summary")
        print("11. Set Budget")
        print("12. Check Budget Status")
        print("13. View Remaining Budget")
        print("14. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            delete_expense()
        elif choice == "4":
            search_expenses()
        elif choice == "5":
            filter_by_category()
        elif choice == "6":
            edit_expense()
        elif choice == "7":
            daily_summary()
        elif choice == "8":
            weekly_summary()
        elif choice == "9":
            monthly_summary()
        elif choice == "10":
            category_summary()
        elif choice == "11":
            set_budget()
        elif choice == "12":
            check_budget()
        elif choice == "13":
            view_remaining_budget()
        elif choice == "14":
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()