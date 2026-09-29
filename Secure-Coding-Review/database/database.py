import sqlite3

DATABASE = "database/students.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()

    # Students table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            course TEXT NOT NULL,
            year INTEGER NOT NULL
        )
    """)
    # Users table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    # Teachers table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            email TEXT
        )
    """)

    # Modules table
    connection.execute("""
        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            teacher_id INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id)
        )
    """)

    # Add example teachers
    connection.execute("""
        INSERT OR IGNORE INTO teachers (name, email)
        VALUES (?, ?)
    """, ("Ms Vinisha", "vinisha@example.com"))

    connection.execute("""
        INSERT OR IGNORE INTO teachers (name, email)
        VALUES (?, ?)
    """, ("Mr Daniel", "daniel@example.com"))

    connection.execute("""
        INSERT OR IGNORE INTO teachers (name, email)
        VALUES (?, ?)
    """, ("Mr Arun", "arun@example.com"))

    connection.execute("""
        INSERT OR IGNORE INTO teachers (name, email)
        VALUES (?, ?)
    """, ("Dr Sarah", "sarah@example.com"))

    # Get teacher IDs
    vinisha = connection.execute(
        "SELECT id FROM teachers WHERE name = ?",
        ("Ms Vinisha",)
    ).fetchone()

    daniel = connection.execute(
        "SELECT id FROM teachers WHERE name = ?",
        ("Mr Daniel",)
    ).fetchone()

    arun = connection.execute(
        "SELECT id FROM teachers WHERE name = ?",
        ("Mr Arun",)
    ).fetchone()

    sarah = connection.execute(
        "SELECT id FROM teachers WHERE name = ?",
        ("Dr Sarah",)
    ).fetchone()

    # Add example modules and allocate teachers
    connection.execute("""
        INSERT OR IGNORE INTO modules (name, teacher_id)
        VALUES (?, ?)
    """, ("Cybersecurity", vinisha["id"]))

    connection.execute("""
        INSERT OR IGNORE INTO modules (name, teacher_id)
        VALUES (?, ?)
    """, ("Computer Science", daniel["id"]))

    connection.execute("""
        INSERT OR IGNORE INTO modules (name, teacher_id)
        VALUES (?, ?)
    """, ("Networking", arun["id"]))

    connection.execute("""
        INSERT OR IGNORE INTO modules (name, teacher_id)
        VALUES (?, ?)
    """, ("AI", sarah["id"]))

    connection.commit()
    connection.close()


if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")