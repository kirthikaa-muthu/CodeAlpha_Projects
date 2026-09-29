from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
import os
import re
from flask_wtf.csrf import CSRFProtect

from database.database import get_connection, initialize_database

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

csrf = CSRFProtect(app)

def validate_student_input(name, email, course, year):
    errors = []

    # Name validation
    if not name or not name.strip():
        errors.append("Student name is required.")
    elif len(name.strip()) < 2 or len(name.strip()) > 100:
        errors.append("Student name must be between 2 and 100 characters.")

    # Email validation
    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    if not email or not email.strip():
        errors.append("Email address is required.")
    elif not re.match(email_pattern, email.strip()):
        errors.append("Please enter a valid email address.")

    # Course validation
    if not course or not course.strip():
        errors.append("Course/module is required.")

    # Year validation
    try:
        year_value = int(year)

        if year_value < 1 or year_value > 5:
            errors.append("Academic year must be between 1 and 5.")

    except (ValueError, TypeError):
        errors.append("Academic year must be a valid number.")

    return errors

def admin_required():

    if "username" not in session:
        return redirect(url_for("login"))

    if session.get("role") != "admin":
        return "Access denied", 403

    return None

initialize_database()

# =========================================================
# HOME / DASHBOARD
# =========================================================

@app.route("/")
def home():

    if "username" not in session:
        return redirect(url_for("login"))

    connection = get_connection()

    total_students = connection.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    total_modules = connection.execute(
        "SELECT COUNT(*) FROM modules"
    ).fetchone()[0]

    total_teachers = connection.execute(
        "SELECT COUNT(*) FROM teachers"
    ).fetchone()[0]

    recent_students = connection.execute(
        """
        SELECT
            students.*,
            modules.name AS module_name,
            teachers.name AS teacher_name
        FROM students
        LEFT JOIN modules
            ON students.course = modules.name
        LEFT JOIN teachers
            ON modules.teacher_id = teachers.id
        ORDER BY students.id DESC
        LIMIT 5
        """
    ).fetchall()

    connection.close()

    return render_template(
        "index.html",
        total_students=total_students,
        total_modules=total_modules,
        total_teachers=total_teachers,
        recent_students=recent_students
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = get_connection()

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        connection.close()

        if user and check_password_hash(
            user["password_hash"],
            password
        ):

            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect(url_for("home"))


        session.clear()
        return "Invalid username or password", 401

    return render_template("login.html")

# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

# =========================================================
# STUDENTS
# =========================================================

@app.route("/students")
def students():

    if "username" not in session:
        return redirect(url_for("login"))

    search = request.args.get("search", "").strip()

    connection = get_connection()

    if search:
        students = connection.execute(
            """
            SELECT
                students.*,
                teachers.name AS teacher_name
            FROM students
            LEFT JOIN modules
                ON students.course = modules.name
            LEFT JOIN teachers
                ON modules.teacher_id = teachers.id
            WHERE students.name LIKE ?
               OR students.email LIKE ?
               OR students.course LIKE ?
            """,
            (
                f"%{search}%",
                f"%{search}%",
                f"%{search}%"
            )
        ).fetchall()

    else:
        students = connection.execute(
            """
            SELECT
                students.*,
                teachers.name AS teacher_name
            FROM students
            LEFT JOIN modules
                ON students.course = modules.name
            LEFT JOIN teachers
                ON modules.teacher_id = teachers.id
            """
        ).fetchall()

    connection.close()


    return render_template(
        "students.html",
        students=students,
        search=search
    )

@app.route("/modules")
def modules():
    if "username" not in session:
        return redirect(url_for("login"))

    connection = get_connection()

    modules = connection.execute("""
        SELECT
            modules.id,
            modules.name,
            teachers.name AS teacher_name,
            COUNT(students.id) AS student_count
        FROM modules
        LEFT JOIN teachers
            ON modules.teacher_id = teachers.id
        LEFT JOIN students
            ON students.course = modules.name
        GROUP BY modules.id, modules.name, teachers.name
        ORDER BY modules.id
    """).fetchall()

    connection.close()

    return render_template(
        "modules.html",
        modules=modules
    )

# =========================================================
# TEACHERS
# =========================================================

@app.route("/teachers")
def teachers():

    if "username" not in session:
        return redirect(url_for("login"))

    connection = get_connection()

    teachers = connection.execute(
        """
        SELECT
            teachers.id,
            teachers.name,
            teachers.email,
            modules.name AS module_name
        FROM teachers
        LEFT JOIN modules
            ON teachers.id = modules.teacher_id
        ORDER BY teachers.name
        """
    ).fetchall()

    connection.close()

    return render_template(
        "teachers.html",
        teachers=teachers
    )

# =========================================================
# ADD STUDENT
# =========================================================

@app.route("/students/add", methods=["GET", "POST"])
def add_student():

    authorization_error = admin_required()

    if authorization_error:
        return authorization_error

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        course = request.form.get("course", "").strip()
        year = request.form.get("year", "").strip()

        errors = validate_student_input(
            name,
            email,
            course,
            year
        )

        if not errors:
            module_connection = get_connection()

            module = module_connection.execute(
                "SELECT id FROM modules WHERE name = ?",
                (course,)
            ).fetchone()

            module_connection.close()

            if module is None:
                errors.append("Selected module does not exist.")

        if errors:
            return "<br>".join(errors), 400

        connection = get_connection()

        connection.execute(
            """
            INSERT INTO students
            (name, email, course, year)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, course, int(year))
        )

        connection.commit()
        connection.close()

        return redirect(url_for("students"))

    connection = get_connection()

    modules = connection.execute(
        """
        SELECT id, name
        FROM modules
        ORDER BY name
        """
    ).fetchall()

    connection.close()

    return render_template(
        "add_student.html",
        modules=modules
    )

# =========================================================
# EDIT STUDENT
# =========================================================
@app.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):

    authorization_error = admin_required()

    if authorization_error:
        return authorization_error

    connection = get_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    if student is None:
        connection.close()
        return "Student not found", 404

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        course = request.form.get("course", "").strip()
        year = request.form.get("year", "").strip()

        errors = validate_student_input(
            name,
            email,
            course,
            year
    )
        if not errors:
            module_connection  = get_connection()

            module = module_connection.execute(
                "SELECT id FROM modules WHERE name = ?",
                (course,)
            ).fetchone()

            module_connection.close()

            if module is None:
                errors.append("Selected module does not exist.")

        if errors:
            return "<br>".join(errors), 400

        connection = get_connection()

        connection.execute(
            """
            UPDATE students
            SET name = ?, email = ?, course = ?, year = ?
            WHERE id = ?
            """,
            (name, email, course, int(year), student_id)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("manage_edit"))

    connection = get_connection()

    modules = connection.execute(
        """
        SELECT id, name
        FROM modules
        ORDER BY name
        """
    ).fetchall()

    connection.close()

    return render_template(
        "edit_student.html",
        student=student,
        modules=modules
    )

# =========================================================
# EDIT STUDENT PAGE
# =========================================================

@app.route("/manage/edit")
def manage_edit():

    authorization_error = admin_required()

    if authorization_error:
        return authorization_error

    connection = get_connection()

    students = connection.execute(
        """
        SELECT *
        FROM students
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    return render_template(
        "manage_edit.html",
        students=students
    )


# =========================================================
# DELETE STUDENT PAGE
# =========================================================

@app.route("/manage/delete")
def manage_delete():

    authorization_error = admin_required()

    if authorization_error:
        return authorization_error

    connection = get_connection()

    students = connection.execute(
        """
        SELECT *
        FROM students
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    return render_template(
        "manage_delete.html",
        students=students
    )

# =========================================================
# OLD DELETE ROUTE
# =========================================================

@app.route("/students/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):

    authorization_error = admin_required()

    if authorization_error:
        return authorization_error

    connection = get_connection()

    connection.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("manage_delete"))

# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode)
