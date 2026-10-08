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

    # ─────────────────────────────────────
    # NORMALIZE LINE
    # Removes emojis / decorative symbols
    # from the beginning of each line
    # ─────────────────────────────────────

    def clean_line(line):
        line = line.strip()

        # Remove common decorative characters/emojis
        while line and not (
            line[0].isalnum()
            or line[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            or "\u0900" <= line[0] <= "\u097F"
            or "\u0A00" <= line[0] <= "\u0A7F"
        ):
            line = line[1:].strip()

        return line

    # ─────────────────────────────────────
    # STYLISH FIELD NORMALIZER
    # ─────────────────────────────────────

    def normalize_label(label):

        label = label.strip()

        # Unicode stylish letters → normal letters
        replacements = {
            "ᴛ": "t",
            "ᴛ": "t",
            "ɪ": "i",
            "ʟ": "l",
            "ᴇ": "e",
            "s": "s",
            "S": "s",
            "ᴜ": "u",
            "ʙ": "b",
            "ᴊ": "j",
            "ᴏ": "o",
            "ᴜ": "u",
            "ᴅ": "d",
            "ᴀ": "a",
            "ɴ": "n",
            "ᴄ": "c",
            "ʜ": "h",
            "ᴘ": "p",
            "ʀ": "r",
            "ᴛ": "t",
            "ᴇ": "e",
            "ᴍ": "m",
            "ғ": "f",
            "ᴄ": "c",
            "ᴀ": "a",
            "ᴛ": "t",
            "ɢ": "g",
            "ᴏ": "o",
            "ʀ": "r",
            "ʏ": "y",
        }

        for old, new in replacements.items():
            label = label.replace(old, new)

        return label.lower().strip()

    # ─────────────────────────────────────
    # READ EACH LINE
    # ─────────────────────────────────────

    for raw_line in caption.splitlines():

        line = clean_line(raw_line)

        if not line:
            continue

        # Split label and value
        match = re.match(
            r"^(.+?)\s*[-:]\s*(.+)$",
            line
        )

        if not match:
            continue

        raw_label = match.group(1).strip()
        value = match.group(2).strip()

        label = normalize_label(raw_label)

        # ─────────────────────────────
        # ENGLISH / STYLISH ENGLISH
        # ─────────────────────────────

        if label == "title":
            data["title"] = value
            continue

        if label == "subject":
            data["subject"] = value
            continue

        if label == "chapter":
            data["chapter"] = value
            continue

       if label == "category":
    category_value = value.strip()

    category_map = {
        "ਲੇਖ": "Essay",
        "ਪੱਤਰ": "Letter",
        "ਕਹਾਣੀ": "Story",
        "लेख": "Essay",
        "पत्र": "Letter",
        "कहानी": "Story",
    }

    data["category"] = category_map.get(
        category_value,
        category_value
    )

    continue

        if label in [
            "item",
            "letter",
            "story",
            "essay",
            "notice",
            "e-mail",
            "email",
        ]:

            data["item_name"] = value

            if label == "letter":
                data["category"] = "Letter"

            elif label == "story":
                data["category"] = "Story"

            elif label == "essay":
                data["category"] = "Essay"

            elif label == "notice":
                data["category"] = "Notice"

            elif label in ["email", "e-mail"]:
                data["category"] = "E-mail"

            continue

        if label == "date":
            data["date"] = value
            continue

        # ─────────────────────────────
        # HINDI
        # ─────────────────────────────

        if raw_label == "शीर्षक":
            data["title"] = value
            continue

        if raw_label == "विषय":
            data["subject"] = value
            continue

        if raw_label == "अध्याय":
            data["chapter"] = value
            continue

        if raw_label == "पत्र":
            data["item_name"] = value
            data["category"] = "Letter"
            continue

        if raw_label == "कहानी":
            data["item_name"] = value
            data["category"] = "Story"
            continue

        if raw_label == "लेख":
            data["item_name"] = value
            data["category"] = "Essay"
            continue

        if raw_label == "दिनांक":
            data["date"] = value
            continue

        # ─────────────────────────────
        # PUNJABI
        # ─────────────────────────────

        if raw_label == "ਸਿਰਲੇਖ":
            data["title"] = value
            continue

        if raw_label == "ਵਿਸ਼ਾ":
            data["subject"] = value
            continue

        if raw_label == "ਪਾਠ":
            data["chapter"] = value
            continue

        if raw_label == "ਪੱਤਰ":
            data["item_name"] = value
            data["category"] = "Letter"
            continue

        if raw_label == "ਕਹਾਣੀ":
            data["item_name"] = value
            data["category"] = "Story"
            continue

        if raw_label == "ਲੇਖ":
            data["item_name"] = value
            data["category"] = "Essay"
            continue

        if raw_label == "ਮਿਤੀ":
            data["date"] = value
            continue

    # ─────────────────────────────────────
    # AUTO CATEGORY FROM TITLE
    # ─────────────────────────────────────

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
# ─────────────────────────────────────
# GET ALL SUBJECTS
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
