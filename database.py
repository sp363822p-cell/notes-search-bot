import sqlite3
import re


DATABASE = "notes.db"


def connect_db():
    return sqlite3.connect(DATABASE)


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
        INSERT OR IGNORE INTO notes
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


def parse_caption(caption):
    """
    Notes Vault caption ko read karke
    subject, chapter, category etc. nikalta hai.
    """

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

        # English fields
        match = re.match(r"(?i)title\s*[-:]\s*(.+)", line)
        if match:
            data["title"] = match.group(1).strip()
            continue

        match = re.match(r"(?i)subject\s*[-:]\s*(.+)", line)
        if match:
            data["subject"] = match.group(1).strip()
            continue

        match = re.match(r"(?i)chapter\s*[-:]\s*(.+)", line)
        if match:
            data["chapter"] = match.group(1).strip()
            continue

        match = re.match(r"(?i)category\s*[-:]\s*(.+)", line)
        if match:
            data["category"] = match.group(1).strip()
            continue

        match = re.match(r"(?i)(letter|story|essay|notice|e-mail|email)\s*[-:]\s*(.+)", line)
        if match:
            data["item_name"] = match.group(2).strip()

            if not data["category"]:
                data["category"] = match.group(1).strip().title()

            continue

        match = re.match(r"(?i)date\s*[-:]\s*(.+)", line)
        if match:
            data["date"] = match.group(1).strip()
            continue

        # Hindi fields
        match = re.match(r"शीर्षक\s*[-:]\s*(.+)", line)
        if match:
            data["title"] = match.group(1).strip()
            continue

        match = re.match(r"विषय\s*[-:]\s*(.+)", line)
        if match:
            data["subject"] = match.group(1).strip()
            continue

        match = re.match(r"अध्याय\s*[-:]\s*(.+)", line)
        if match:
            data["chapter"] = match.group(1).strip()
            continue

        match = re.match(r"पत्र\s*[-:]\s*(.+)", line)
        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Letter"
            continue

        match = re.match(r"कहानी\s*[-:]\s*(.+)", line)
        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Story"
            continue

        match = re.match(r"लेख\s*[-:]\s*(.+)", line)
        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Essay"
            continue

        match = re.match(r"दिनांक\s*[-:]\s*(.+)", line)
        if match:
            data["date"] = match.group(1).strip()
            continue

        # Punjabi fields
        match = re.match(r"ਸਿਰਲੇਖ\s*[-:]\s*(.+)", line)
        if match:
            data["title"] = match.group(1).strip()
            continue

        match = re.match(r"ਵਿਸ਼ਾ\s*[-:]\s*(.+)", line)
        if match:
            data["subject"] = match.group(1).strip()
            continue

        match = re.match(r"ਪਾਠ\s*[-:]\s*(.+)", line)
        if match:
            data["chapter"] = match.group(1).strip()
            continue

        match = re.match(r"ਪੱਤਰ\s*[-:]\s*(.+)", line)
        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Letter"
            continue

        match = re.match(r"ਕਹਾਣੀ\s*[-:]\s*(.+)", line)
        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Story"
            continue

        match = re.match(r"ਲੇਖ\s*[-:]\s*(.+)", line)
        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Essay"
            continue

        match = re.match(r"ਮਿਤੀ\s*[-:]\s*(.+)", line)
        if match:
            data["date"] = match.group(1).strip()
            continue

    # Grammar category title se automatically identify
    title_lower = data["title"].lower()

    if not data["category"]:
        for category in [
            "Chapter",
            "Letter",
            "Notice",
            "E-mail",
            "Story",
            "Essay",
        ]:
            if category.lower() in title_lower:
                data["category"] = category
                break

    return data


def get_subjects():
    conn = connect_db()
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
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT chapter
        FROM notes
        WHERE subject = ?
        AND chapter != ''
        ORDER BY chapter
    """, (subject,))

    chapters = [row[0] for row in cursor.fetchall()]

    conn.close()
    return chapters


def get_categories(subject):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT category
        FROM notes
        WHERE subject = ?
        AND category != ''
        ORDER BY category
    """, (subject,))

    categories = [row[0] for row in cursor.fetchall()]

    conn.close()
    return categories


def find_note(subject=None, chapter=None, category=None, item_name=None):
    conn = connect_db()
    cursor = conn.cursor()

    query = """
        SELECT chat_id, message_id, title, subject, chapter,
               category, item_name, date
        FROM notes
        WHERE 1=1
    """

    values = []

    if subject:
        query += " AND LOWER(subject) = LOWER(?)"
        values.append(subject)

    if chapter:
        query += " AND LOWER(chapter) = LOWER(?)"
        values.append(chapter)

    if category:
        query += " AND LOWER(category) = LOWER(?)"
        values.append(category)

    if item_name:
        query += " AND LOWER(item_name) = LOWER(?)"
        values.append(item_name)

    query += " LIMIT 1"

    cursor.execute(query, values)
    result = cursor.fetchone()

    conn.close()

    return result


def get_notes_by_subject(subject):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT chat_id, message_id, title, chapter,
               category, item_name, date
        FROM notes
        WHERE LOWER(subject) = LOWER(?)
        ORDER BY id
    """, (subject,))

    results = cursor.fetchall()

    conn.close()
    return results
