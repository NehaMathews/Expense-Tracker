from flask import Flask, render_template, request, redirect, session
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

FILE = "expenses.json"
BUDGET = "budgets.json"

# ---------- Load / Save ----------
def load():
    if not os.path.exists(FILE):
        return []
    return json.load(open(FILE))

def save(data):
    json.dump(data, open(FILE, "w"), indent=4)

def load_budget():
    if not os.path.exists(BUDGET):
        return {"weekly": 0, "monthly": 0}
    return json.load(open(BUDGET))

def save_budget(data):
    json.dump(data, open(BUDGET, "w"), indent=4)

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    return json.load(open(USERS_FILE))

def save_users(data):
    json.dump(data, open(USERS_FILE, "w"), indent=4)

# ---------- Dashboard ----------
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")
    data = load()
    total = sum(e["amount"] for e in data)
    budget = load_budget()
    today = datetime.now()

    weekly_spent = sum(e["amount"] for e in data
        if 0 <= (today - datetime.strptime(e["date"], "%Y-%m-%d")).days < 7)

    monthly_spent = sum(e["amount"] for e in data
        if datetime.strptime(e["date"], "%Y-%m-%d").month == today.month)

    weekly_remaining = budget["weekly"] - weekly_spent
    monthly_remaining = budget["monthly"] - monthly_spent

    # status logic
    weekly_status = ""
    if budget["weekly"] > 0:
        percent = (weekly_spent / budget["weekly"]) * 100
        if percent >= 100:
            weekly_status = "exceeded"
        elif percent >= 80:
            weekly_status = "warning"

    monthly_status = ""
    if budget["monthly"] > 0:
        percent = (monthly_spent / budget["monthly"]) * 100
        if percent >= 100:
            monthly_status = "exceeded"
        elif percent >= 80:
            monthly_status = "warning"

    return render_template("index.html",
        expenses=data,
        total=total,
        budget=budget,
        weekly_remaining=weekly_remaining,
        monthly_remaining=monthly_remaining,
        weekly_status=weekly_status,
        monthly_status=monthly_status
    )


# ---------- Add ----------
@app.route("/add", methods=["POST"])
def add():
    if "user" not in session:
        return redirect("/login")
    data = load()
    data.append({
        "amount": float(request.form["amount"]),
        "category": request.form["category"],
        "desc": request.form["desc"],
        "date": datetime.now().strftime("%Y-%m-%d")
    })
    save(data)
    return redirect("/")

# ---------- Delete ----------
@app.route("/delete/<int:i>")
def delete(i):
    if "user" not in session:
        return redirect("/login")
    data = load()
    data.pop(i)
    save(data)
    return redirect("/")

# ---------- Edit ----------
@app.route("/edit/<int:i>", methods=["POST"])
def edit(i):
    if "user" not in session:
        return redirect("/login")
    data = load()
    data[i]["amount"] = float(request.form["amount"])
    data[i]["category"] = request.form["category"]
    data[i]["desc"] = request.form["desc"]
    save(data)
    return redirect("/")

# ---------- Search ----------
@app.route("/search", methods=["POST"])
def search():
    keyword = request.form["keyword"].lower()
    data = load()

    filtered = [e for e in data if keyword in e["category"].lower() or keyword in e["desc"].lower()]
    total = sum(e["amount"] for e in filtered)

    return render_template("index.html", expenses=filtered, total=total)

# ---------- Budget ----------
@app.route("/budget", methods=["GET", "POST"])
def budget():
    if "user" not in session:
        return redirect("/login")
    if request.method == "POST":
        save_budget({
            "weekly": float(request.form["weekly"]),
            "monthly": float(request.form["monthly"])
        })
        return redirect("/budget")

    b = load_budget()
    return render_template("budget.html", budget=b)

# ---------- Analytics ----------
@app.route("/analytics")
def analytics():
    if "user" not in session:
        return redirect("/login")
    data = load()
    today = datetime.now()

    # -------- Monthly Trend (last 12 months) --------
    monthly_totals = [0]*12

    for e in data:
        d = datetime.strptime(e["date"], "%Y-%m-%d")
        monthly_totals[d.month - 1] += e["amount"]

    # -------- Yearly Trend --------
    yearly_totals = {}

    for e in data:
        d = datetime.strptime(e["date"], "%Y-%m-%d")
        year = d.year
        yearly_totals[year] = yearly_totals.get(year, 0) + e["amount"]

    # -------- Category Annual --------
    category_totals = {}

    for e in data:
        d = datetime.strptime(e["date"], "%Y-%m-%d")

        if d.year == today.year:  # current year only
            cat = e["category"]
            category_totals[cat] = category_totals.get(cat, 0) + e["amount"]

    return render_template("analytics.html",
        monthly=monthly_totals,
        yearly=yearly_totals,
        categories=category_totals
    )

#---------- User Authentication ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        users = load_users()

        username = request.form["username"]
        password = request.form["password"]

        # Check if user exists
        for u in users:
            if u["username"] == username:
                return "User already exists!"

        users.append({
            "username": username,
            "password": password
        })

        save_users(users)
        return redirect("/login")

    return render_template("register.html")

#--------- Login ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        users = load_users()

        username = request.form["username"]
        password = request.form["password"]

        for u in users:
            if u["username"] == username and u["password"] == password:
                session["user"] = username
                return redirect("/")

        return "Invalid credentials!"

    return render_template("login.html")

#--------- Logout ----------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)