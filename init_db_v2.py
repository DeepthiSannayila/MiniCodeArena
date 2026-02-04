import sqlite3
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS problems")
cursor.execute("DROP TABLE IF EXISTS testcases")
cursor.execute("DROP TABLE IF EXISTS submissions")
cursor.execute("""
CREATE TABLE problems (
    id INTEGER PRIMARY KEY,
    title TEXT,
    description TEXT,
    difficulty TEXT,
    sample_input TEXT,
    sample_output TEXT
)
""")

cursor.execute("""
CREATE TABLE testcases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER,
    input_data TEXT,
    expected_output TEXT
)
""")

cursor.execute("""
CREATE TABLE submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER,
    code TEXT,
    status TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

problems = [
    (1, "Two Sum", "Find indices of two numbers that add to target.", "Easy",
    "2 7 11 15\n9", "0 1"),

    (2, "Reverse String", "Write a function that reverses a string.", "Easy",
    "hello", "olleh"),

    (3, "Palindrome Number", "Check if a number is palindrome.", "Easy",
    "121", "true"),

    (4, "Valid Parentheses", "Check if parentheses are valid.", "Easy",
    "()[]{}", "true"),

    (5, "Merge Two Sorted Lists", "Merge two sorted lists.", "Easy",
    "1 2 4\n1 3 4", "1 1 2 3 4 4"),

    (6, "Remove Duplicates", "Remove duplicates from sorted array.", "Easy",
    "1 1 2", "1 2"),

    (7, "Best Time to Buy and Sell Stock", "Find max profit.", "Easy",
    "7 1 5 3 6 4", "5"),

    (8, "Single Number", "Find element appearing once.", "Easy",
    "4 1 2 1 2", "4"),

    (9, "Climbing Stairs", "Count distinct ways.", "Easy",
    "3", "3"),

    (10, "Maximum Subarray", "Find contiguous max sum.", "Easy",
    "-2 1 -3 4 -1 2 1", "6"),

    (17, "Linked List Cycle", "Detect cycle in linked list.", "Easy",
    "3 2 0 -4", "true"),
]

cursor.executemany("""
INSERT INTO problems (id, title, description, difficulty, sample_input, sample_output)
VALUES (?, ?, ?, ?, ?, ?)
""", problems)
testcases = [
    (1, "2 7 11 15\n9\n", "0 1"),
    (2, "hello\n", "olleh"),
    (2, "abc\n", "cba"),
    (3, "121\n", "true"),
    (3, "123\n", "false"),
    (4, "()[]{}\n", "true"),
    (4, "(]\n", "false"),
    (5, "1 2 4\n1 3 4\n", "1 1 2 3 4 4"),
    (6, "1 1 2\n", "1 2"),
    (7, "7 1 5 3 6 4\n", "5"),
    (8, "4 1 2 1 2\n", "4"),
    (9, "3\n", "3"),
    (10, "-2 1 -3 4 -1 2 1\n", "6"),
    (17, "3 2 0 -4\n", "true"),
]

cursor.executemany("""
INSERT INTO testcases (problem_id, input_data, expected_output)
VALUES (?, ?, ?)
""", testcases)
conn.commit()
conn.close()

print("✅ Phase 2 DB initialized successfully!")
