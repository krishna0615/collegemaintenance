
from flask import Flask, render_template, request, redirect
import sqlite3
import re

app = Flask(__name__)

def create_database():
    with sqlite3.connect("complaints.db") as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room TEXT NOT NULL,
                problem TEXT NOT NULL,
                details TEXT NOT NULL,
                status TEXT DEFAULT 'Pending'
            )
        """)

def valid_room(room):
    match = re.fullmatch(r"([A-F])(\d{3})", room)
    if not match:
        return False

    block, code = match.groups()
    floor = int(code[0])
    number = int(code[1:])

    max_floor = 5 if block == "F" else 3
    return floor <= max_floor and 1 <= number <= 12

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    room = request.form.get("room", "").upper()
    problem = request.form.get("problem", "")
    details = request.form.get("details", "").strip()

    if not valid_room(room):
        return "Invalid room number!", 400

    if problem not in ["Fan", "Board", "Light", "Bench", "Other"] or not details:
        return "Please enter valid complaint details!", 400

    with sqlite3.connect("complaints.db") as con:
        con.execute(
            "INSERT INTO complaints (room, problem, details) VALUES (?, ?, ?)",
            (room, problem, details)
        )

    return "<h2>Complaint submitted successfully!</h2><a href='/'>Go back</a>"

@app.route("/admin")
def admin():
    with sqlite3.connect("complaints.db") as con:
        con.row_factory = sqlite3.Row
        complaints = con.execute(
            "SELECT * FROM complaints ORDER BY id DESC"
        ).fetchall()

    return render_template("admin.html", complaints=complaints)

@app.route("/update/<int:complaint_id>", methods=["POST"])
def update(complaint_id):
    status = request.form.get("status", "")

    if status not in ["Pending", "In Progress", "Resolved"]:
        return "Invalid status!", 400

    with sqlite3.connect("complaints.db") as con:
        con.execute(
            "UPDATE complaints SET status = ? WHERE id = ?",
            (status, complaint_id)
        )

    return redirect("/admin")

if __name__ == "__main__":
    create_database()
    app.run(debug=True)
