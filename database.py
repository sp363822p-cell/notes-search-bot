import sqlite3
import re

DATABASE = "notes.db"


def connect_db():
    return sqlite3.connect(DATABASE)


# ─────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────

def setup_database():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            title TEXT,
            subject TEXT,
            chapter TEXT,
            category TEXT,
            item_name TEXT,
            date TEXT,
            UNIQUE(chat_id, message_id)
        )
    """)

    conn.commit()
    conn.close()


# ─────────────────────────────────────
# ADD NOTE
# ─────────────────────────────────────

def add_note(
    chat_id,
    message_id,
    title="",
    subject="",
    chapter="",
    category="",
    item_name="",
    date=""
):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO notes
        (chat_id, message_id, title, subject, chapter, category, item_name, date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        chat_id,
        message_id,
        title,
        subject,
        chapter,
        category,
        item_name,
        date
    ))

    conn.commit()
    conn.close()


# ─────────────────────────────────────
# CAPTION PARSER
# ─────────────────────────────────────

def parse_caption(caption):

    data = {
        "title": "",
        "subject": "",
        "chapter": "",
        "category": "",
        "item_name": "",
        "date": "",
    }

    if not caption:
        return data

    lines = caption.splitlines()

    for line in lines:

        line = line.strip()

        if not line:
            continue

        # English Title
        match = re.match(r"(?i)^title\s*[-:]\s*(.+)", line)

        if match:
            data["title"] = match.group(1).strip()
            continue

        # English Subject
        match = re.match(r"(?i)^subject\s*[-:]\s*(.+)", line)

        if match:
            data["subject"] = match.group(1).strip()
            continue

        # English Chapter
        match = re.match(r"(?i)^chapter\s*[-:]\s*(.+)", line)

        if match:
            data["chapter"] = match.group(1).strip()
            continue

        # Category
        match = re.match(r"(?i)^category\s*[-:]\s*(.+)", line)

        if match:
            data["category"] = match.group(1).strip()
            continue

        # Letter / Story / Essay / Notice / E-mail
        match = re.match(
            r"(?i)^(letter|story|essay|notice|e-mail|email)\s*[-:]\s*(.+)",
            line
        )

        if match:

            data["item_name"] = match.group(2).strip()

            if not data["category"]:
                data["category"] = match.group(1).strip().title()

            continue

        # Date
        match = re.match(r"(?i)^date\s*[-:]\s*(.+)", line)

        if match:
            data["date"] = match.group(1).strip()
            continue

        # ─────────────────────────────
        # HINDI
        # ─────────────────────────────

        match = re.match(r"^शीर्षक\s*[-:]\s*(.+)", line)

        if match:
            data["title"] = match.group(1).strip()
            continue

        match = re.match(r"^विषय\s*[-:]\s*(.+)", line)

        if match:
            data["subject"] = match.group(1).strip()
            continue

        match = re.match(r"^अध्याय\s*[-:]\s*(.+)", line)

        if match:
            data["chapter"] = match.group(1).strip()
            continue

        match = re.match(r"^पत्र\s*[-:]\s*(.+)", line)

        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Letter"
            continue

        match = re.match(r"^कहानी\s*[-:]\s*(.+)", line)

        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Story"
            continue

        match = re.match(r"^लेख\s*[-:]\s*(.+)", line)

        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Essay"
            continue

        match = re.match(r"^दिनांक\s*[-:]\s*(.+)", line)

        if match:
            data["date"] = match.group(1).strip()
            continue

        # ─────────────────────────────
        # PUNJABI
        # ─────────────────────────────

        match = re.match(r"^ਸਿਰਲੇਖ\s*[-:]\s*(.+)", line)

        if match:
            data["title"] = match.group(1).strip()
            continue

        match = re.match(r"^ਵਿਸ਼ਾ\s*[-:]\s*(.+)", line)

        if match:
            data["subject"] = match.group(1).strip()
            continue

        match = re.match(r"^ਪਾਠ\s*[-:]\s*(.+)", line)

        if match:
            data["chapter"] = match.group(1).strip()
            continue

        match = re.match(r"^ਪੱਤਰ\s*[-:]\s*(.+)", line)

        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Letter"
            continue

        match = re.match(r"^ਕਹਾਣੀ\s*[-:]\s*(.+)", line)

        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Story"
            continue

        match = re.match(r"^ਲੇਖ\s*[-:]\s*(.+)", line)

        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Essay"
            continue

        match = re.match(r"^ਮਿਤੀ\s*[-:]\s*(.+)", line)

        if match:
            data["date"] = match.group(1).strip()
            continue

    # ─────────────────────────────
    # AUTO CATEGORY FROM TITLE
    # ─────────────────────────────

    title_lower = data["title"].lower()

    if not data["category"]:

        categories = [
            "Chapter",
            "Letter",
            "Notice",
            "E-mail",
            "Email",
            "Story",
            "Essay",
        ]

        for category in categories:

            if category.lower() in title_lower:

                data["category"] = category

                if category.lower() == "email":
                    data["category"] = "E-mail"

                break

    return data


# ─────────────────────────────────────
# SUBJECTS
# ─────────────────────────────────────

def get_subjects():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT subject
        FROM notes
        WHERE subject != ''
        ORDER BY subject
    """)

    subjects = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return subjects


# ─────────────────────────────────────
# CHAPTERS
# ─────────────────────────────────────

def get_chapters(subject):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT chapter
        FROM notes
        WHERE LOWER(subject) = LOWER(?)
        AND chapter != ''
        ORDER BY id
    """, (subject,))

    chapters = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return chapters


# ─────────────────────────────────────
# CATEGORIES
# ─────────────────────────────────────

def get_categories(subject):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT category
        FROM notes
        WHERE LOWER(subject) = LOWER(?)
        AND category != ''
        ORDER BY id
    """, (subject,))

    categories = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return categories


# ─────────────────────────────────────
# FIND EXACT NOTE
# ─────────────────────────────────────

def find_note(
    subject=None,
    chapter=None,
    category=None,
    item_name=None
):

    conn = connect_db()
    cursor = conn.cursor()

    query = """
        SELECT
            chat_id,
            message_id,
            title,
            subject,
            chapter,
            category,
            item_name,
            date
        FROM notes
        WHERE 1=1
    """

    values = []

    if subject:

        query += """
            AND LOWER(subject) = LOWER(?)
        """

        values.append(subject)

    if chapter:

        query += """
            AND LOWER(chapter) = LOWER(?)
        """

        values.append(chapter)

    if category:

        query += """
            AND LOWER(category) = LOWER(?)
        """

        values.append(category)

    if item_name:

        query += """
            AND LOWER(item_name) = LOWER(?)
        """

        values.append(item_name)

    query += """
        ORDER BY id DESC
        LIMIT 1
    """

    cursor.execute(query, values)

    result = cursor.fetchone()

    conn.close()

    return result


# ─────────────────────────────────────
# FIND NOTE BY CHAPTER NUMBER
# ─────────────────────────────────────

def find_note_by_chapter_number(subject, chapter_number):

    conn = connect_db()
    cursor = conn.cursor()

    pattern = f"{chapter_number} (%"

    cursor.execute("""
        SELECT
            chat_id,
            message_id,
            title,
            subject,
            chapter,
            category,
            item_name,
            date
        FROM notes
        WHERE LOWER(subject) = LOWER(?)
        AND (
            LOWER(chapter) = LOWER(?)
            OR LOWER(chapter) LIKE LOWER(?)
        )
        ORDER BY id DESC
        LIMIT 1
    """, (
        subject,
        str(chapter_number),
        pattern
    ))

    result = cursor.fetchone()

    conn.close()

    return result


# ─────────────────────────────────────
# FIND GRAMMAR NOTE
# ─────────────────────────────────────

def find_grammar_note(subject, category, item_name):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            chat_id,
            message_id,
            title,
            subject,
            chapter,
            category,
            item_name,
            date
        FROM notes
        WHERE LOWER(subject) = LOWER(?)
        AND LOWER(category) = LOWER(?)
        AND LOWER(item_name) = LOWER(?)
        ORDER BY id DESC
        LIMIT 1
    """, (
        subject,
        category,
        item_name
    ))

    result = cursor.fetchone()

    conn.close()

    return result
