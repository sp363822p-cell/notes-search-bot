import sqlite3
import re

DATABASE = "notes.db"


# ─────────────────────────────────────
# DATABASE CONNECTION
# ─────────────────────────────────────

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
# ADD / UPDATE NOTE
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
        (
            chat_id,
            message_id,
            title,
            subject,
            chapter,
            category,
            item_name,
            date
        )
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
# PARSE CAPTION
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

        # ─────────────────────────────
        # ENGLISH
        # ─────────────────────────────

        match = re.match(
            r"(?i)^title\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["title"] = match.group(1).strip()
            continue

        match = re.match(
            r"(?i)^subject\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["subject"] = match.group(1).strip()
            continue

        match = re.match(
            r"(?i)^chapter\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["chapter"] = match.group(1).strip()
            continue

        match = re.match(
            r"(?i)^category\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["category"] = match.group(1).strip()
            continue

        match = re.match(
            r"(?i)^(letter|story|essay|notice|e-mail|email)\s*[-:]\s*(.+)",
            line
        )

        if match:

            data["item_name"] = match.group(2).strip()

            if not data["category"]:
                data["category"] = (
                    match.group(1)
                    .strip()
                    .title()
                )

            if data["category"].lower() == "email":
                data["category"] = "E-mail"

            continue

        match = re.match(
            r"(?i)^date\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["date"] = match.group(1).strip()
            continue

        # ─────────────────────────────
        # HINDI
        # ─────────────────────────────

        match = re.match(
            r"^शीर्षक\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["title"] = match.group(1).strip()
            continue

        match = re.match(
            r"^विषय\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["subject"] = match.group(1).strip()
            continue

        match = re.match(
            r"^अध्याय\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["chapter"] = match.group(1).strip()
            continue

        match = re.match(
            r"^पत्र\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Letter"
            continue

        match = re.match(
            r"^कहानी\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Story"
            continue

        match = re.match(
            r"^लेख\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Essay"
            continue

        match = re.match(
            r"^दिनांक\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["date"] = match.group(1).strip()
            continue

        # ─────────────────────────────
        # PUNJABI
        # ─────────────────────────────

        match = re.match(
            r"^ਸਿਰਲੇਖ\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["title"] = match.group(1).strip()
            continue

        match = re.match(
            r"^ਵਿਸ਼ਾ\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["subject"] = match.group(1).strip()
            continue

        match = re.match(
            r"^ਪਾਠ\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["chapter"] = match.group(1).strip()
            continue

        match = re.match(
            r"^ਪੱਤਰ\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Letter"
            continue

        match = re.match(
            r"^ਕਹਾਣੀ\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Story"
            continue

        match = re.match(
            r"^ਲੇਖ\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["item_name"] = match.group(1).strip()
            data["category"] = "Essay"
            continue

        match = re.match(
            r"^ਮਿਤੀ\s*[-:]\s*(.+)",
            line
        )

        if match:
            data["date"] = match.group(1).strip()
            continue

    # ─────────────────────────────────
    # AUTO CATEGORY FROM TITLE
    # ─────────────────────────────────

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
# GET ALL SUBJECTS
# ─────────────────────────────────────

def get_chapters(subject):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT chapter
        FROM notes
        WHERE LOWER(subject) = LOWER(?)
        AND chapter != ''
    """, (subject,))

    chapters = [row[0] for row in cursor.fetchall()]
    conn.close()

    def chapter_sort_key(chapter):
        match = re.search(r'\d+', chapter)

        if match:
            return (0, int(match.group()), chapter.lower())

        return (1, 999999, chapter.lower())

    chapters.sort(key=chapter_sort_key)

    return chapters

# ─────────────────────────────────────
# GET CHAPTERS
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
# GET GRAMMAR CATEGORIES
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
# GET CATEGORY ITEMS
# ─────────────────────────────────────

def get_category_items(subject, category):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT item_name
        FROM notes
        WHERE LOWER(subject) = LOWER(?)
        AND LOWER(category) = LOWER(?)
        AND item_name != ''
        ORDER BY id
    """, (
        subject,
        category
    ))

    items = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return items


# ─────────────────────────────────────
# FIND NOTE
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

    cursor.execute(
        query,
        values
    )

    result = cursor.fetchone()

    conn.close()

    return result


# ─────────────────────────────────────
# FIND NOTE BY CHAPTER NUMBER
# ─────────────────────────────────────

def find_note_by_chapter_number(
    subject,
    chapter_number
):

    conn = connect_db()
    cursor = conn.cursor()

    number = str(chapter_number).strip()

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
            OR LOWER(chapter) LIKE LOWER(?)
        )
        ORDER BY id DESC
        LIMIT 1
    """, (
        subject,
        number,
        f"{number} %",
        f"{number} (%"
    ))

    result = cursor.fetchone()

    conn.close()

    return result


# ─────────────────────────────────────
# FIND GRAMMAR NOTE
# ─────────────────────────────────────

def find_grammar_note(
    subject,
    category,
    item_name
):

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
    
def delete_note_by_message(chat_id, message_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM notes
        WHERE chat_id = ?
        AND message_id = ?
    """, (chat_id, message_id))

    deleted = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted
# ─────────────────────────────────────
# DELETE NOTE BY MESSAGE ID
# ─────────────────────────────────────

def delete_note_by_message_id(chat_id, message_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM notes
        WHERE chat_id = ? AND message_id = ?
    """, (chat_id, message_id))
    conn.commit()
    conn.close()
    
# ─────────────────────────────────────
# MANUAL REMOVE SYSTEM
# ─────────────────────────────────────

def get_chapter_choices(subject):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT MIN(id), chapter
        FROM notes
        WHERE LOWER(subject) = LOWER(?)
        AND chapter != ''
        GROUP BY LOWER(chapter)
        ORDER BY MIN(id)
    """, (subject,))

    chapters = cursor.fetchall()

    conn.close()

    return chapters


def get_chapter_by_note_id(note_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            chat_id,
            message_id,
            title,
            subject,
            chapter,
            category,
            item_name,
            date
        FROM notes
        WHERE id = ?
        LIMIT 1
    """, (note_id,))

    result = cursor.fetchone()

    conn.close()

    return result


def get_notes_in_chapter(subject, chapter):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
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
        AND LOWER(chapter) = LOWER(?)
        ORDER BY id
    """, (
        subject,
        chapter
    ))

    notes = cursor.fetchall()

    conn.close()

    return notes


def delete_note_by_id(note_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM notes
        WHERE id = ?
    """, (note_id,))

    deleted = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted
