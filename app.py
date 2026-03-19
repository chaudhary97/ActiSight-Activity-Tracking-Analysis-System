from flask import Flask, render_template, request, redirect, session
import pandas as pd
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# Load CSV
df = pd.read_csv("data.csv")

# Convert time
df['Start_Time'] = pd.to_datetime(df['Start_Time'])
df['End_Time'] = pd.to_datetime(df['End_Time'])

# Duration in seconds
df['Duration'] = (df['End_Time'] - df['Start_Time']).dt.total_seconds()

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")

    return render_template("login.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")

    result = None

    # Search by name
    name = request.form.get("name")
    if name:
        result = df[df['Name'] == name]

    # Search by time range
    start = request.form.get("start")
    end = request.form.get("end")

    if start and end:
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)

        result = df[
            (df['Start_Time'] >= start) &
            (df['End_Time'] <= end)
        ]

    # Total time per person
    total_time = df.groupby('Name')['Duration'].sum().to_dict()

    return render_template(
        "dashboard.html",
        people=df['Name'].unique(),
        result=result,
        total_time=total_time
    )


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)