import sqlite3

DATABASE_NAME = "data/jobs.db"


def create_connection():
    return sqlite3.connect(DATABASE_NAME)


def create_table():
    connection = create_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            job_role TEXT NOT NULL,
            location TEXT,
            application_date DATE,
            status TEXT,
            interview_date DATE,
            follow_up_date DATE,
            notes TEXT
        )
    """)

    connection.commit()
    connection.close()


if __name__ == "__main__":
    create_table()
    print("Database and table created successfully!")