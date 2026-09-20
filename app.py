from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "placeprep-secret-key"


# ---------------- DATABASE ----------------

def get_db():
    connection = sqlite3.connect("database.db")
    connection.row_factory = sqlite3.Row
    return connection


def create_database():

    connection = get_db()

    # Users table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Coding questions table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL
        )
    """)
        # Aptitude questions table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS aptitude_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            answer TEXT NOT NULL
        )
    """)
        # Interview questions table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS interview_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            question TEXT NOT NULL
        )
    """)
        # User progress table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            coding_solved INTEGER DEFAULT 0,
            aptitude_tests INTEGER DEFAULT 0,
            aptitude_score INTEGER DEFAULT 0,
            interview_answered INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    connection.commit()
    connection.close()


def add_sample_questions():
   
    connection = get_db()

    count = connection.execute(
        "SELECT COUNT(*) FROM questions"
    ).fetchone()[0]

    if count == 0:

        questions = [
            (
                "Two Sum",
                "Easy",
                "Arrays",
                "Given an array of integers and a target value, return the indices of two numbers that add up to the target."
            ),

            (
                "Valid Anagram",
                "Easy",
                "Strings",
                "Given two strings, determine whether one string is an anagram of the other."
            ),

            (
                "Contains Duplicate",
                "Easy",
                "Arrays",
                "Given an integer array, return True if any value appears at least twice."
            ),

            (
                "Best Time to Buy and Sell Stock",
                "Easy",
                "Arrays",
                "Find the maximum profit that can be achieved by buying and selling a stock."
            ),

            (
                "Majority Element",
                "Easy",
                "Arrays",
                "Find the element that appears more than half of the time in an array."
            )
        ]

        connection.executemany(
            """
            INSERT INTO questions
            (title, difficulty, category, description)
            VALUES (?, ?, ?, ?)
            """,
            questions
        )

        connection.commit()

    connection.close()
def add_aptitude_questions():

    connection = get_db()

    count = connection.execute(
        "SELECT COUNT(*) FROM aptitude_questions"
    ).fetchone()[0]

    if count == 0:

        questions = [
            (
                "A train travels 60 km in 1 hour. What is its speed?",
                "40 km/h",
                "50 km/h",
                "60 km/h",
                "70 km/h",
                "C"
            ),
            (
                "What is 20% of 250?",
                "40",
                "50",
                "60",
                "70",
                "B"
            ),
            (
                "If 5 workers complete a job in 10 days, how many worker-days are required?",
                "15",
                "25",
                "50",
                "100",
                "C"
            ),
            (
                "Find the next number: 2, 4, 8, 16, ?",
                "24",
                "30",
                "32",
                "36",
                "C"
            ),
            (
                "If the ratio of boys to girls is 2:3 and there are 20 boys, how many girls are there?",
                "20",
                "25",
                "30",
                "35",
                "C"
            )
        ]

        connection.executemany(
            """
            INSERT INTO aptitude_questions
            (question, option_a, option_b, option_c, option_d, answer)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            questions
        )

        connection.commit()

    connection.close() 
def add_interview_questions():

    connection = get_db()

    count = connection.execute(
        "SELECT COUNT(*) FROM interview_questions"
    ).fetchone()[0]

    if count == 0:

        questions = [
            (
                "HR",
                "Tell me about yourself."
            ),
            (
                "HR",
                "What are your strengths and weaknesses?"
            ),
            (
                "HR",
                "Why should we hire you?"
            ),
            (
                "Technical",
                "What is the difference between a list and a tuple in Python?"
            ),
            (
                "Technical",
                "What is a primary key in a database?"
            ),
            (
                "Technical",
                "Explain the concept of object-oriented programming."
            ),
            (
                "Project",
                "Explain one of your academic projects."
            ),
            (
                "Project",
                "What was your role in the project?"
            )
        ]

        connection.executemany(
            """
            INSERT INTO interview_questions
            (category, question)
            VALUES (?, ?)
            """,
            questions
        )

        connection.commit()

    connection.close()       


# ---------------- HOME ----------------

@app.route("/")
def home():

    return render_template("index.html")


# ---------------- REGISTER ----------------

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        connection = get_db()

        try:

            connection.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )

            connection.commit()
            user = connection.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
            ).fetchone()

            connection.execute(
            "INSERT INTO progress (user_id) VALUES (?)",
            (user["id"],)
            )

            connection.commit()
        except sqlite3.IntegrityError:

            connection.close()

            return "Email already registered."

        connection.close()

        return redirect(url_for("login"))

    return render_template("register.html")


# ---------------- LOGIN ----------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        connection = get_db()

        user = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["user_name"] = user["name"]

            # Check if progress record exists
            progress = connection.execute(
                "SELECT * FROM progress WHERE user_id = ?",
                (user["id"],)
            ).fetchone()

            # Create progress record for old users
            if progress is None:

                connection.execute(
                    "INSERT INTO progress (user_id) VALUES (?)",
                    (user["id"],)
                )

                connection.commit()

            connection.close()

            return redirect(url_for("dashboard"))

        connection.close()

        return "Invalid email or password."

    return render_template("login.html")

 
# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        name=session["user_name"]
    )



# ---------------- CODING ----------------

@app.route("/coding")
def coding():

    if "user_id" not in session:

        return redirect(url_for("login"))

    connection = get_db()

    questions = connection.execute(
        "SELECT * FROM questions"
    ).fetchall()

    connection.close()

    return render_template(
        "coding.html",
        questions=questions
    )


# ---------------- LOGOUT ----------------
@app.route("/aptitude", methods=["GET", "POST"])
def aptitude():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()

    questions = connection.execute(
        "SELECT * FROM aptitude_questions"
    ).fetchall()

    connection.close()

    score = None

    if request.method == "POST":

        score = 0

        for question in questions:

            selected_answer = request.form.get(
                "q" + str(question["id"])
            )

            if selected_answer == question["answer"]:
                score += 1

    return render_template(
        "aptitude.html",
        questions=questions,
        score=score
    )
@app.route("/interview")
def interview():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()

    questions = connection.execute(
        "SELECT * FROM interview_questions"
    ).fetchall()

    connection.close()

    return render_template(
        "interview.html",
        questions=questions
    )
@app.route("/skills", methods=["GET", "POST"])
def skills():

    if "user_id" not in session:
        return redirect(url_for("login"))

    coding = None
    aptitude = None
    interview = None
    overall = None

    if request.method == "POST":

        coding = int(request.form["coding"])
        aptitude = int(request.form["aptitude"])
        interview = int(request.form["interview"])

        overall = round(
            (coding + aptitude + interview) / 3
        )

    return render_template(
        "skills.html",
        coding=coding,
        aptitude=aptitude,
        interview=interview,
        overall=overall
    )
# =====================================================
# PROFILE
# =====================================================

@app.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]

        connection.execute(
            """
            UPDATE users
            SET name = ?, email = ?
            WHERE id = ?
            """,
            (name, email, session["user_id"])
        )

        connection.commit()

        session["user_name"] = name

    user = connection.execute(
        """
        SELECT name, email
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    connection.close()

    return render_template(
        "profile.html",
        name=user["name"],
        email=user["email"]
    )
# =====================================================
# SETTINGS
# =====================================================

@app.route("/settings")
def settings():

    if "user_id" not in session:
        return redirect(url_for("login"))

    return render_template(
        "settings.html",
        name=session["user_name"]
    )
# ---------------- PROGRESS ----------------

@app.route("/progress")
def progress():

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db()

    # Get user's progress
    progress_data = connection.execute(
        "SELECT * FROM progress WHERE user_id = ?",
        (session["user_id"],)
    ).fetchone()

    # Total coding questions
    total_coding = connection.execute(
        "SELECT COUNT(*) FROM questions"
    ).fetchone()[0]

    # Total interview questions
    total_interview = connection.execute(
        "SELECT COUNT(*) FROM interview_questions"
    ).fetchone()[0]

    connection.close()

    # If progress record doesn't exist
    if progress_data is None:

        coding_solved = 0
        aptitude_tests = 0
        aptitude_score = 0
        interview_answered = 0

    else:

        coding_solved = progress_data["coding_solved"]
        aptitude_tests = progress_data["aptitude_tests"]
        aptitude_score = progress_data["aptitude_score"]
        interview_answered = progress_data["interview_answered"]

    # Coding progress
    if total_coding > 0:
        coding_progress = round(
            (coding_solved / total_coding) * 100
        )
    else:
        coding_progress = 0

    # Aptitude progress
    aptitude_progress = aptitude_score

    # Interview progress
    if total_interview > 0:
        interview_progress = round(
            (interview_answered / total_interview) * 100
        )
    else:
        interview_progress = 0

    # Overall progress
    overall = round(
        (
            coding_progress
            + aptitude_progress
            + interview_progress
        ) / 3
    )

    return render_template(
        "progress.html",
        name=session["user_name"],
        overall=overall,
        coding_progress=coding_progress,
        aptitude_progress=aptitude_progress,
        interview_progress=interview_progress,
        coding_solved=coding_solved,
        aptitude_tests=aptitude_tests,
        interview_answered=interview_answered
    )

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ---------------- START APP ----------------

if __name__ == "__main__":

    create_database()

    add_sample_questions()
    add_aptitude_questions()
    add_interview_questions()

     port = int(os.environ.get("PORT", 5000))
     app.run(host="0.0.0.0", port=port)
