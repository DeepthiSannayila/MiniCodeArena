from flask import Flask, render_template, request, jsonify
import sqlite3
import subprocess
import tempfile
import os
import sys
import io
from datetime import datetime
from flask import session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

init_db()
DB_PATH = "database.db"

# ================= HELPERS =================

def get_testcases(problem_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT input_data, expected_output FROM testcases WHERE problem_id = ?",
        (problem_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def run_with_custom_input(user_code, custom_input):
    full_code = f"""
import sys
import io

{user_code}

sys.stdin = io.StringIO(\"\"\"{custom_input}\"\"\")
try:
    solve()
except Exception as e:
    print(e)
"""

    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp:
        temp.write(full_code.encode())
        temp_filename = temp.name

    try:
        result = subprocess.run(
            [sys.executable, temp_filename],
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.stderr:
            return {"status": "runtime_error", "error": result.stderr}

        return {"status": "success", "output": result.stdout}

    except subprocess.TimeoutExpired:
        return {"status": "time_limit_exceeded", "error": "Time Limit Exceeded"}

    finally:
        os.remove(temp_filename)


def run_testcases(user_code, testcases):
    for index, (input_data, expected_output) in enumerate(testcases, start=1):

        full_code = f"""
import sys
import io

{user_code}

sys.stdin = io.StringIO(\"\"\"{input_data}\"\"\")
_buffer = io.StringIO()
sys.stdout = _buffer

try:
    solve()
except Exception as e:
    print(e)

sys.stdout = sys.__stdout__
print(_buffer.getvalue(), end="")
"""

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp:
            temp.write(full_code.encode())
            temp_filename = temp.name

        try:
            result = subprocess.run(
                [sys.executable, temp_filename],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.stderr:
                return {
                    "status": "runtime_error",
                    "testcase": index,
                    "error": result.stderr
                }

            actual = result.stdout.strip()
            expected = expected_output.strip()

            if actual != expected:
                return {
                    "status": "wrong_answer",
                    "testcase": index,
                    "expected": expected,
                    "got": actual
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "time_limit_exceeded",
                "testcase": index
            }

        finally:
            os.remove(temp_filename)

    return {"status": "accepted"}


# ================= CONTEST HELPERS =================

def get_active_contests():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, start_time, end_time FROM contests")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_contest(contest_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, start_time, end_time FROM contests WHERE id = ?",
        (contest_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return row


def get_contest_problems(contest_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.id, p.title, p.difficulty
        FROM contest_problems cp
        JOIN problems p ON cp.problem_id = p.id
        WHERE cp.contest_id = ?
    """, (contest_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def save_contest_submission(contest_id, problem_id, code, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO contest_submissions (contest_id, problem_id, user_code, status, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (contest_id, problem_id, code, status, datetime.now()))
    conn.commit()
    conn.close()


def save_contest_registration(contest_id, user_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO contest_registrations (contest_id, user_name, registered_at)
        VALUES (?, ?, ?)
    """, (contest_id, user_name, datetime.now()))
    conn.commit()
    conn.close()


def mark_problem_solved(contest_id, problem_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1 FROM contest_solved
        WHERE contest_id = ? AND problem_id = ?
    """, (contest_id, problem_id))

    exists = cursor.fetchone()

    if not exists:
        cursor.execute("""
            INSERT INTO contest_solved (contest_id, problem_id, status)
            VALUES (?, ?, 'accepted')
        """, (contest_id, problem_id))

    conn.commit()
    conn.close()


def get_solved_problems(contest_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT problem_id FROM contest_solved
        WHERE contest_id = ? AND status = 'accepted'
    """, (contest_id,))
    rows = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]

def judge(user_code, testcases):
    for index, (input_data, expected_output) in enumerate(testcases, start=1):

        full_code = f"""
import sys
import io

{user_code}

sys.stdin = io.StringIO(\"\"\"{input_data}\"\"\")
_buffer = io.StringIO()
sys.stdout = _buffer

try:
    solve()
except Exception as e:
    print(e)

sys.stdout = sys.__stdout__
print(_buffer.getvalue(), end="")
"""

        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp:
            temp.write(full_code.encode())
            temp_filename = temp.name

        try:
            result = subprocess.run(
                [sys.executable, temp_filename],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.stderr:
                return {
                    "status": "runtime_error",
                    "testcase": index,
                    "error": result.stderr
                }

            actual = result.stdout.strip()
            expected = expected_output.strip()

            if actual != expected:
                return {
                    "status": "wrong_answer",
                    "testcase": index,
                    "expected": expected,
                    "got": actual
                }

        except subprocess.TimeoutExpired:
            return {
                "status": "time_limit_exceeded",
                "testcase": index
            }

        finally:
            os.remove(temp_filename)

    return {"status": "accepted"}



# ================= FLASK APP =================

app = Flask(__name__)
app.secret_key = "super_secret_key_123"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )
            conn.commit()
        except:
            conn.close()
            return "User already exists!"

        conn.close()
        return redirect(url_for("login"))

    return render_template("register.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[2], password):
            session["user_id"] = user[0]
            session["user_name"] = user[1]
            return redirect(url_for("landing_page"))

        return "Invalid credentials!"

    return render_template("login.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing_page"))

@app.route("/")
def landing_page():
    return render_template("home.html")

@app.route("/problems")
def problems_page():
    return render_template("index.html")

@app.route("/about")
def about_page():
    return render_template("about.html")

@app.route("/contests")
def contests_page():
    return render_template("contests.html")

@app.route("/contest/<int:contest_id>")
def contest_detail_page(contest_id):
    return render_template("contest_detail.html", contest_id=contest_id)

@app.route("/contest/<int:contest_id>/problem/<int:problem_id>")
def contest_problem_page(contest_id, problem_id):
    return render_template(
        "contest_problem.html",
        contest_id=contest_id,
        problem_id=problem_id
    )


# ================= APIs =================

@app.route("/api/contests")
def api_contests():
    contests = get_active_contests()
    return jsonify([
        {"id": c[0], "title": c[1], "start_time": c[2], "end_time": c[3]}
        for c in contests
    ])

@app.route("/api/contest/<int:contest_id>")
def api_contest_detail(contest_id):
    c = get_contest(contest_id)
    if not c:
        return jsonify({"error": "Contest not found"}), 404

    return jsonify({
        "id": c[0],
        "title": c[1],
        "start_time": c[2],
        "end_time": c[3]
    })

@app.route("/api/contest/<int:contest_id>/problems")
def api_contest_problems(contest_id):
    problems = get_contest_problems(contest_id)
    return jsonify([
        {"id": p[0], "title": p[1], "difficulty": p[2]}
        for p in problems
    ])

@app.route("/api/contest/<int:contest_id>/solved")
def api_contest_solved(contest_id):
    solved = get_solved_problems(contest_id)
    return jsonify(solved)

@app.route("/api/problem/<int:problem_id>")
def api_problem(problem_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT title, description, sample_input, sample_output
        FROM problems WHERE id = ?
    """, (problem_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Problem not found"}), 404

    return jsonify({
        "title": row[0],
        "description": row[1],
        "sample_input": row[2],
        "sample_output": row[3]
    })


# ================= ACTION ROUTES =================

@app.route("/contest/register", methods=["POST"])
def contest_register():
    data = request.get_json()
    contest_id = data.get("contest_id")
    user_name = data.get("user_name")

    if not contest_id or not user_name:
        return jsonify({"status": "error", "message": "Missing contest ID or name"})

    save_contest_registration(contest_id, user_name)
    return jsonify({"status": "success"})


@app.route("/contest/submit", methods=["POST"])
def contest_submit():
    data = request.get_json()
    contest_id = data.get("contest_id")
    problem_id = data.get("problem_id")
    code = data.get("code")

    if not contest_id or not problem_id:
        return jsonify({"status": "error", "message": "Contest ID or Problem ID missing"})

    testcases = get_testcases(problem_id)
    if not testcases:
        return jsonify({"status": "error", "message": "No testcases found"})

    result = judge(code, testcases)

    save_contest_submission(contest_id, problem_id, code, result["status"])

    if result["status"] == "accepted":
        mark_problem_solved(contest_id, problem_id)

    return jsonify(result)



@app.route("/run", methods=["POST"])
def run_code():
    data = request.get_json()
    return jsonify(run_with_custom_input(
        data.get("code"),
        data.get("custom_input", "")
    ))

@app.route("/interview")
def interview_page():
    return render_template("interview.html")

# ================= MAIN =================

if __name__ == "__main__":
    app.run(debug=True)
