import sqlite3

DB_NAME = "notes.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            chat_id INTEGER NOT NULL,
            title TEXT,
            subject TEXT,
            chapter TEXT,
            category TEXT,
            item_name TEXT,
            date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(chat_id, message_id)
        )
    """)

    conn.commit()
    conn.close()


def add_note(
    message_id,
    chat_id,
    title="",
    subject="",
    chapter="",
    category="",
    item_name="",
    date=""
):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO notes
        (
            message_id,
            chat_id,
            title,
            subject,
            chapter,
            category,
            item_name,
            date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        message_id,
        chat_id,
        title,
        subject,
        chapter,
        category,
        item_name,
        date
    ))

    conn.commit()
    conn.close()


def get_subjects():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT subject
        FROM notes
        WHERE subject != ''
        ORDER BY subject
    """)

    subjects = [row[0] for row in cursor.fetchall()]

    conn.close()
    return subjects


def get_chapters(subject):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT chapter
        FROM notes
        WHERE LOWER(subject) = LOWER(?)
        AND chapter != ''
        ORDER BY chapter
    """, (subject,))

    chapters = [row[0] for row in cursor.fetchall()]

    conn.close()
    return chapters


def get_categories(subject):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT category
        FROM notes
        WHERE LOWER(subject) = LOWER(?)
        AND category != ''
        ORDER BY category
    """, (subject,))

    categories = [row[0] for row in cursor.fetchall()]

    conn.close()
    return categories


def get_items(subject, category):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, chapter, item_name, message_id, chat_id
        FROM notes
        WHERE LOWER(subject) = LOWER(?)
        AND LOWER(category) = LOWER(?)
        ORDER BY chapter
    """, (subject, category))

    items = cursor.fetchall()

    conn.close()
    return items


def find_note(subject, chapter):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT message_id, chat_id
        FROM notes
        WHERE LOWER(subject) = LOWER(?)
        AND LOWER(chapter) = LOWER(?)
        LIMIT 1
    """, (subject, chapter))

    note = cursor.fetchone()

    conn.close()
    return note


def find_note_by_item(subject, category, item_name):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT message_id, chat_id
        FROM notes
        WHERE LOWER(subject) = LOWER(?)
        AND LOWER(category) = LOWER(?)
        AND LOWER(item_name) = LOWER(?)
        LIMIT 1
    """, (subject, category, item_name))

    note = cursor.fetchone()

    conn.close()
    return note
