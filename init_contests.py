import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# ================= DROP OLD TABLES =================
cursor.execute("DROP TABLE IF EXISTS contests")
cursor.execute("DROP TABLE IF EXISTS contest_problems")
cursor.execute("DROP TABLE IF EXISTS contest_submissions")
cursor.execute("DROP TABLE IF EXISTS contest_registrations")

# ================= CREATE TABLES =================

cursor.execute("""
CREATE TABLE contests (
    id INTEGER PRIMARY KEY,
    title TEXT,
    start_time TEXT,
    end_time TEXT
)
""")

cursor.execute("""
CREATE TABLE contest_problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contest_id INTEGER,
    problem_id INTEGER
)
""")

cursor.execute("""
CREATE TABLE contest_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contest_id INTEGER,
    problem_id INTEGER,
    user_code TEXT,
    status TEXT,
    timestamp TEXT
)
""")

cursor.execute("""
CREATE TABLE contest_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contest_id INTEGER,
    user_name TEXT,
    registered_at TEXT
)
""")

# ================= INSERT CONTESTS =================

contests = [
    (101, "Weekly Contest #101", "2026-02-02 08:00", "2026-02-02 10:00"),
    (102, "Biweekly Contest #52", "2026-01-25 20:00", "2026-01-25 22:00"),
    (103, "Beginner Contest #12", "2026-01-22 18:00", "2026-01-22 20:00"),

    (105, "DSA Marathon #3", "2026-01-19 10:00", "2026-01-19 12:00"),
    (109, "System Design Round", "2026-01-19 12:00", "2026-01-19 15:00"),
]

cursor.executemany(
    "INSERT INTO contests VALUES (?, ?, ?, ?)", contests
)

# ================= LINK PROBLEMS =================

contest_problems = [
    # Contest 101
    (101, 1), (101, 2), (101, 3), (101, 4),

    # Contest 102
    (102, 5), (102, 6), (102, 7),

    # Contest 103
    (103, 1), (103, 2),

    # Contest 105
    (105, 8), (105, 9), (105, 10),

    # Contest 109
    (109, 4), (109, 6), (109, 7),
]

cursor.executemany(
    "INSERT INTO contest_problems (contest_id, problem_id) VALUES (?, ?)",
    contest_problems
)

conn.commit()
conn.close()

print("✅ Contests 101, 102, 103, 105, 109 initialized cleanly!")
def solve():
    arr = list(map(int, input().split()))
    result = 0
    for num in arr:
        result ^= num   # XOR cancels duplicates
    print(result)
import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS contest_solved (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contest_id INTEGER,
    problem_id INTEGER,
    status TEXT,
    UNIQUE(contest_id, problem_id)
)
""")
conn.commit()
conn.close()

print("✅ contest_solved table created")
