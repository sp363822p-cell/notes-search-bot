import os
import re

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from database import (
    setup_database,
    add_note,
    parse_caption,
    get_chapters,
    get_exercises,
    find_exercise_note,
    get_categories,
    get_category_items,
    find_note,
    find_note_by_chapter_number,
    find_grammar_note,
    get_subjects,
    get_notes_for_removal,
    count_notes_for_removal,
    delete_note_by_id,
)


# ─────────────────────────────────────
# WELCOME
# ─────────────────────────────────────

WELCOME_MESSAGE = (
    "╭━━━━━━━━━━━━━━━━━━━━╮\n"
    "📚 *Nᴏᴛᴇs Vᴀᴜʟᴛ*\n"
    "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
    "👋 *Wᴇʟᴄᴏᴍᴇ!*\n\n"
    "📖 Yahan aap apne *Class Notes, Q/A, M.C.Q, T/F, "
    "Blanks, Letters, Stories, Essays & more* easily search kar sakte hain.\n\n"
    "⚡ *Fast • Simple • Easy*\n\n"
    "💡 *Tip:* Aap Subject + Chapter likhkar bhi directly note search kar sakte hain.\n\n"
    "✨ *Nᴏᴛᴇs Sᴇᴀʀᴄʜ Bᴏᴛ*"
)


# ─────────────────────────────────────
# SUBJECT LIST
# ─────────────────────────────────────

SUBJECTS = [
    "Science",
    "Mathematics",
    "English R",
    "English Grammar",
    "S.S.T",
    "Computer",
    "Punjabi R",
    "Punjabi Grammar",
    "Hindi R",
    "Hindi Grammar",
]

GRAMMAR_SUBJECTS = [
    "English Grammar",
    "Punjabi Grammar",
    "Hindi Grammar",
]


# ─────────────────────────────────────
# START
# ─────────────────────────────────────

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    keyboard = [
        [
            InlineKeyboardButton(
                "📚 Gᴇᴛ Nᴏᴛᴇ",
                callback_data="get_note"
            )
        ]
    ]

    await update.message.reply_text(
        WELCOME_MESSAGE,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ─────────────────────────────────────
# SUBJECT MENU
# ─────────────────────────────────────

async def subject_menu(query):

    keyboard = [
        [
            InlineKeyboardButton(
                "🔬 Sᴄɪᴇɴᴄᴇ",
                callback_data="subject|Science"
            ),
            InlineKeyboardButton(
                "➗ Mᴀᴛʜ",
                callback_data="subject|Math"
            ),
        ],
        [
            InlineKeyboardButton(
                "📘 Eɴɢʟɪsʜ R",
                callback_data="subject|English R"
            ),
            InlineKeyboardButton(
                "📝 Eɴɢʟɪsʜ Gr",
                callback_data="subject|English Grammar"
            ),
        ],
        [
            InlineKeyboardButton(
                "🌍 S.Sᴛ",
                callback_data="subject|S.S.T"
            ),
            InlineKeyboardButton(
                "💻 Cᴏᴍᴘᴜᴛᴇʀ",
                callback_data="subject|Computer"
            ),
        ],
        [
            InlineKeyboardButton(
                "📗 Pᴜɴᴊᴀʙɪ R",
                callback_data="subject|Punjabi R"
            ),
            InlineKeyboardButton(
                "📝 Pᴜɴᴊᴀʙɪ Gr",
                callback_data="subject|Punjabi Grammar"
            ),
        ],
        [
            InlineKeyboardButton(
                "📕 Hɪɴᴅɪ R",
                callback_data="subject|Hindi R"
            ),
            InlineKeyboardButton(
                "📝 Hɪɴᴅɪ Gr",
                callback_data="subject|Hindi Grammar"
            ),
        ],
        [
            InlineKeyboardButton(
                "🔙 Bᴀᴄᴋ",
                callback_data="back_home"
            )
        ],
    ]

    message = (
        "╭━━━━━━━━━━━━━━━━━━━━╮\n"
        "📚 *Sᴇʟᴇᴄᴛ Sᴜʙᴊᴇᴄᴛ*\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "👇 *Pʟᴇᴀsᴇ Sᴇʟᴇᴄᴛ Yᴏᴜʀ Sᴜʙᴊᴇᴄᴛ*"
    )

    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ─────────────────────────────────────
# CHAPTER MENU
# ─────────────────────────────────────

async def chapter_menu(query, subject):

    chapters = get_chapters(subject)

    keyboard = []

    for index, chapter in enumerate(chapters):

        # Short callback data
        # Prevents Telegram Button_data_invalid
        callback = f"ch|{subject}|{index}"

        keyboard.append([
            InlineKeyboardButton(
                f"📖 {chapter}",
                callback_data=callback
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Bᴀᴄᴋ",
            callback_data="get_note"
        )
    ])

    if not chapters:

        message = (
            "╭━━━━━━━━━━━━━━━━━━━━╮\n"
            "📖 *Sᴇʟᴇᴄᴛ Cʜᴀᴘᴛᴇʀ*\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
            "❌ *Nᴏ Cʜᴀᴘᴛᴇʀs Fᴏᴜɴᴅ*\n\n"
            "📚 Notes database me abhi is subject ka note nahi hai."
        )

    else:

        message = (
            "╭━━━━━━━━━━━━━━━━━━━━╮\n"
            "📖 *Sᴇʟᴇᴄᴛ Cʜᴀᴘᴛᴇʀ*\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
            "👇 *Pʟᴇᴀsᴇ Sᴇʟᴇᴄᴛ Yᴏᴜʀ Cʜᴀᴘᴛᴇʀ*\n\n"
            "🔄 *Rᴏᴛᴀᴛᴇ Yᴏᴜʀ Pʜᴏɴᴇ Tᴏ Sᴇᴇ Fᴜʟʟ Nᴀᴍᴇ*"
        )

    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ─────────────────────────────────────
# MATHEMATICS EXERCISE MENU
# ─────────────────────────────────────

async def exercise_menu(query, subject, chapter, chapter_index=None):
    exercises = get_exercises(subject, chapter)
    keyboard = []

    for index, exercise in enumerate(exercises):
        # Keep callback data short and resolve names from the database.
        callback = f"ex|{chapter_index if chapter_index is not None else 0}|{index}"
        keyboard.append([
            InlineKeyboardButton(
                f"📝 Exercise - {exercise}",
                callback_data=callback
            )
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data=f"subject|{subject}")
    ])

    if not exercises:
        message = (
            "📘 *Mᴀᴛʜᴇᴍᴀᴛɪᴄs — Sᴇʟᴇᴄᴛ E x e r c i s e*\n\n"
            f"📖 Chapter: {chapter}\n\n"
            "❌ Is chapter ke liye abhi koi exercise PDF indexed nahi hai.\n\n"
            "PDF caption mein `Exercise - 1.1` jaisa field add karke upload karein."
        )
    else:
        message = (
            "╭━━━━━━━━━━━━━━━━━━━━╮\n"
            "📝 *Sᴇʟᴇᴄᴛ E x e r c i s e*\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
            f"📖 *Chapter:* {chapter}\n\n"
            "👇 *Pʟᴇᴀsᴇ Sᴇʟᴇᴄᴛ Yᴏᴜʀ E x e r c i s e*"
        )

    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ─────────────────────────────────────
# GRAMMAR MENU
# ─────────────────────────────────────

async def grammar_menu(query, subject):

    categories = get_categories(subject)

    keyboard = []

    for category in categories:

        # Category names are short enough
        callback = f"category|{subject}|{category}"

        keyboard.append([
            InlineKeyboardButton(
                f"📖 {category}",
                callback_data=callback
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Bᴀᴄᴋ",
            callback_data="get_note"
        )
    ])

    if not categories:

        message = (
            "╭━━━━━━━━━━━━━━━━━━━━╮\n"
            "📖 *Sᴇʟᴇᴄᴛ Cᴀᴛᴇɢᴏʀʏ*\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
            "❌ *Nᴏ Cᴀᴛᴇɢᴏʀɪᴇs Fᴏᴜɴᴅ*"
        )

    else:

        message = (
            "╭━━━━━━━━━━━━━━━━━━━━╮\n"
            "📖 *Sᴇʟᴇᴄᴛ Cᴀᴛᴇɢᴏʀʏ*\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
            "👇 *Pʟᴇᴀsᴇ Sᴇʟᴇᴄᴛ Yᴏᴜʀ Cᴀᴛᴇɢᴏʀʏ*\n\n"
            "🔄 *Rᴏᴛᴀᴛᴇ Yᴏᴜʀ Pʜᴏɴᴇ Tᴏ Sᴇᴇ Fᴜʟʟ Nᴀᴍᴇ*"
        )

    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ─────────────────────────────────────
# GRAMMAR ITEM MENU
# ─────────────────────────────────────

async def grammar_item_menu(
    query,
    subject,
    category
):

    items = get_category_items(
        subject,
        category
    )

    keyboard = []

    for index, item in enumerate(items):

        # VERY SHORT CALLBACK
        # Item name is NOT stored in callback
        callback = (
            f"gi|{subject}|{category}|{index}"
        )

        keyboard.append([
            InlineKeyboardButton(
                f"📖 {item}",
                callback_data=callback
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Bᴀᴄᴋ",
            callback_data=f"subject|{subject}"
        )
    ])

    if not items:

        await query.edit_message_text(
            "❌ *Nᴏ Iᴛᴇᴍs Fᴏᴜɴᴅ*",
            parse_mode="Markdown"
        )

        return

    message = (
        "╭━━━━━━━━━━━━━━━━━━━━╮\n"
        f"📖 *Sᴇʟᴇᴄᴛ {category.upper()}*\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "👇 *Pʟᴇᴀsᴇ Sᴇʟᴇᴄᴛ Yᴏᴜʀ Nᴏᴛᴇ*\n\n"
        "🔄 *Rᴏᴛᴀᴛᴇ Yᴏᴜʀ Pʜᴏɴᴇ Tᴏ Sᴇᴇ Fᴜʟʟ Nᴀᴍᴇ*"
    )

    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ─────────────────────────────────────
# FORWARD NOTE
# ─────────────────────────────────────

async def forward_note(
    query,
    context,
    note
):

    if not note:

        await query.edit_message_text(
            "❌ *Nᴏᴛᴇ Nᴏᴛ Fᴏᴜɴᴅ*\n\n"
            "📚 Is note ka PDF database mein nahi mila.",
            parse_mode="Markdown",
        )

        return

    (
        chat_id,
        message_id,
        title,
        subject,
        chapter,
        category,
        item_name,
        date
    ) = note

    try:

        await context.bot.forward_message(
            chat_id=query.message.chat.id,
            from_chat_id=chat_id,
            message_id=message_id,
        )

    except Exception as error:

        print(
            f"Forward error: {error}"
        )

        await query.edit_message_text(
            "❌ *Nᴏᴛᴇ Sᴇɴᴅ Nᴀʜɪ Hᴜᴀ*\n\n"
            "⚠️ Notes Vault message access mein problem aa rahi hai.",
            parse_mode="Markdown",
        )


# ─────────────────────────────────────
# BUTTON HANDLER
# ─────────────────────────────────────

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data


    # ─────────────────────────────
    # GET NOTE
    # ─────────────────────────────

    if data == "get_note":

        await subject_menu(query)

        return


    # ─────────────────────────────
    # BACK HOME
    # ─────────────────────────────

    if data == "back_home":

        keyboard = [
            [
                InlineKeyboardButton(
                    "📚 Gᴇᴛ Nᴏᴛᴇ",
                    callback_data="get_note"
                )
            ]
        ]

        await query.edit_message_text(
            WELCOME_MESSAGE,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

        return


    # ─────────────────────────────
    # SUBJECT
    # ─────────────────────────────

    if data.startswith("subject|"):

        subject = data.split(
            "|",
            1
        )[1]

        if subject.strip().lower() == "math":
            subject = "Mathematics"

        if subject in GRAMMAR_SUBJECTS:

            await grammar_menu(
                query,
                subject
            )

        else:

            await chapter_menu(
                query,
                subject
            )

        return


    # ─────────────────────────────
    # CHAPTER
    # Short callback:
    # ch|Science|0
    # ─────────────────────────────

    if data.startswith("ch|"):

        parts = data.split(
            "|",
            2
        )

        if len(parts) != 3:
            return

        subject = parts[1]

        try:
            index = int(parts[2])
        except ValueError:
            return

        chapters = get_chapters(
            subject
        )

        if index < 0 or index >= len(chapters):

            await query.edit_message_text(
                "❌ *Cʜᴀᴘᴛᴇʀ Nᴏᴛ Fᴏᴜɴᴅ*",
                parse_mode="Markdown"
            )

            return

        chapter = chapters[index]

        # Mathematics uses Chapter -> Exercise -> PDF. Other subjects keep the old flow.
        if subject.strip().lower() in ("math", "mathematics"):
            await exercise_menu(query, "Mathematics", chapter, index)
            return

        # Exact chapter search
        note = find_note(
            subject=subject,
            chapter=chapter
        )

        # Backup chapter number search
        if not note:

            match = re.search(
                r"(\d+)",
                chapter
            )

            if match:

                chapter_number = (
                    match.group(1)
                )

                note = find_note_by_chapter_number(
                    subject,
                    chapter_number
                )

        await forward_note(
            query,
            context,
            note
        )

        return


    # ─────────────────────────────
    # MATHEMATICS EXERCISE CALLBACK
    # ex|chapter_index|exercise_index
    # ─────────────────────────────

    if data.startswith("ex|"):
        parts = data.split("|", 2)
        if len(parts) != 3:
            return
        try:
            chapter_index = int(parts[1])
            exercise_index = int(parts[2])
        except ValueError:
            return

        chapters = get_chapters("Mathematics")
        if chapter_index < 0 or chapter_index >= len(chapters):
            await query.edit_message_text("❌ *Cʜᴀᴘᴛᴇʀ Nᴏᴛ Fᴏᴜɴᴅ*", parse_mode="Markdown")
            return

        chapter = chapters[chapter_index]
        exercises = get_exercises("Mathematics", chapter)
        if exercise_index < 0 or exercise_index >= len(exercises):
            await query.edit_message_text("❌ *E x e r c i s e Nᴏᴛ Fᴏᴜɴᴅ*", parse_mode="Markdown")
            return

        exercise = exercises[exercise_index]
        note = find_exercise_note("Mathematics", chapter, exercise)
        await forward_note(query, context, note)
        return


    # ─────────────────────────────
    # OLD CHAPTER CALLBACK
    # Kept for old messages/buttons
    # ─────────────────────────────

    if data.startswith("chapter|"):

        parts = data.split(
            "|",
            2
        )

        if len(parts) != 3:
            return

        subject = parts[1]
        chapter = parts[2]

        note = find_note(
            subject=subject,
            chapter=chapter
        )

        if not note:

            match = re.search(
                r"(\d+)",
                chapter
            )

            if match:

                chapter_number = (
                    match.group(1)
                )

                note = find_note_by_chapter_number(
                    subject,
                    chapter_number
                )

        await forward_note(
            query,
            context,
            note
        )

        return


    # ─────────────────────────────
    # GRAMMAR CATEGORY
    # ─────────────────────────────

    if data.startswith("category|"):

        parts = data.split(
            "|",
            2
        )

        if len(parts) != 3:
            return

        subject = parts[1]
        category = parts[2]

        await grammar_item_menu(
            query,
            subject,
            category
        )

        return


    # ─────────────────────────────
    # GRAMMAR ITEM
    #
    # Example:
    # gi|Hindi Grammar|Letter|0
    #
    # The actual long item name is
    # NOT stored in callback_data.
    # ─────────────────────────────

    if data.startswith("gi|"):

        parts = data.split(
            "|",
            3
        )

        if len(parts) != 4:
            return

        subject = parts[1]
        category = parts[2]

        try:
            index = int(parts[3])
        except ValueError:
            return

        items = get_category_items(
            subject,
            category
        )

        if index < 0 or index >= len(items):

            await query.edit_message_text(
                "❌ *Nᴏᴛᴇ Nᴏᴛ Fᴏᴜɴᴅ*",
                parse_mode="Markdown"
            )

            return

        item_name = items[index]

        note = find_grammar_note(
            subject,
            category,
            item_name
        )

        await forward_note(
            query,
            context,
            note
        )

        return


# ─────────────────────────────────────
# CHANNEL NOTE INDEXER
# ─────────────────────────────────────

async def channel_note_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    post = update.channel_post

    if not post:
        return

    # Only documents / PDFs
    if not post.document:
        return

    caption = post.caption or ""

    data = parse_caption(
        caption
    )

    # Subject required
    if not data["subject"]:

        print(
            "Skipped note: Subject missing"
        )

        return

    add_note(
        chat_id=post.chat.id,
        message_id=post.message_id,
        title=data["title"],
        subject=data["subject"],
        chapter=data["chapter"],
        exercise=data.get("exercise", ""),
        category=data["category"],
        item_name=data["item_name"],
        date=data["date"],
    )

    print(
        "Note indexed: "
        f"{data['subject']} | "
        f"{data['chapter'] or data['category']}"
        f" | Exercise: {data.get('exercise', '')}"
    )


# ─────────────────────────────────────
# SUBJECT CHAPTER MENU
# FOR DIRECT SEARCH
# ─────────────────────────────────────

async def send_subject_chapters(
    update,
    subject
):

    chapters = get_chapters(
        subject
    )

    if not chapters:

        await update.message.reply_text(
            "❌ *Nᴏ Cʜᴀᴘᴛᴇʀs Fᴏᴜɴᴅ*",
            parse_mode="Markdown"
        )

        return

    keyboard = []

    for index, chapter in enumerate(
        chapters
    ):

        keyboard.append([
            InlineKeyboardButton(
                f"📖 {chapter}",
                callback_data=(
                    f"ch|{subject}|{index}"
                )
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Bᴀᴄᴋ",
            callback_data="get_note"
        )
    ])

    await update.message.reply_text(
        "📖 *Sᴇʟᴇᴄᴛ Cʜᴀᴘᴛᴇʀ*\n\n"
        "👇 *Pʟᴇᴀsᴇ Sᴇʟᴇᴄᴛ Yᴏᴜʀ Cʜᴀᴘᴛᴇʀ*\n\n"
        "🔄 *Rᴏᴛᴀᴛᴇ Yᴏᴜʀ Pʜᴏɴᴇ Tᴏ Sᴇᴇ Fᴜʟʟ Nᴀᴍᴇ*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


# ─────────────────────────────────────
# DIRECT GRAMMAR SEARCH
# ─────────────────────────────────────

async def direct_grammar_search(
    update,
    subject,
    category
):

    categories = get_categories(
        subject
    )

    actual_category = None

    for db_category in categories:

        if db_category.lower() == category.lower():

            actual_category = db_category

            break

    if not actual_category:

        await update.message.reply_text(
            "❌ *Cᴀᴛᴇɢᴏʀʏ Nᴏᴛ Fᴏᴜɴᴅ*",
            parse_mode="Markdown"
        )

        return

    items = get_category_items(
        subject,
        actual_category
    )

    keyboard = []

    for index, item in enumerate(
        items
    ):

        keyboard.append([
            InlineKeyboardButton(
                f"📖 {item}",
                callback_data=(
                    f"gi|{subject}|"
                    f"{actual_category}|{index}"
                )
            )
        ])
    if not items:
        await update.message.reply_text(
            "❌ *Nᴏ Nᴏᴛᴇs Fᴏᴜɴᴅ*",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        f"📖 *Sᴇʟᴇᴄᴛ {actual_category}*\n\n"
        "👇 *Pʟᴇᴀsᴇ Sᴇʟᴇᴄᴛ Yᴏᴜʀ Nᴏᴛᴇ*\n\n"
        "🔄 *Rᴏᴛᴀᴛᴇ Yᴏᴜʀ Pʜᴏɴᴇ Tᴏ Sᴇᴇ Fᴜʟʟ Nᴀᴍᴇ*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )# ─────────────────────────────────────
# DIRECT MESSAGE SEARCH
# ─────────────────────────────────────

async def message_search(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    text = update.message.text.strip()

    if not text:
        return

    # Ignore commands
    if text.startswith("/"):
        return

    print(
        f"Search received: {text}"
    )


    # ─────────────────────────────
    # SUBJECT ONLY
    # Example:
    # Science
    # Hindi Grammar
    # ─────────────────────────────

    matched_subject = None

    # Accept the old direct-search alias "Math", but show the canonical subject name.
    if text.lower() in ("math", "mathematics"):
        matched_subject = "Mathematics"
    else:
        for subject in SUBJECTS:
            if text.lower() == subject.lower():
                matched_subject = subject
                break

    if matched_subject:

        # Grammar subject
        if matched_subject in GRAMMAR_SUBJECTS:

            categories = get_categories(
                matched_subject
            )

            keyboard = []

            for category in categories:

                keyboard.append([
                    InlineKeyboardButton(
                        f"📖 {category}",
                        callback_data=(
                            f"category|"
                            f"{matched_subject}|"
                            f"{category}"
                        )
                    )
                ])

            if not categories:

                await update.message.reply_text(
                    "❌ *Nᴏ Cᴀᴛᴇɢᴏʀɪᴇs Fᴏᴜɴᴅ*",
                    parse_mode="Markdown"
                )

                return

            await update.message.reply_text(
                "📖 *Sᴇʟᴇᴄᴛ Cᴀᴛᴇɢᴏʀʏ*\n\n"
                "👇 *Pʟᴇᴀsᴇ Sᴇʟᴇᴄᴛ Yᴏᴜʀ Cᴀᴛᴇɢᴏʀʏ*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(
                    keyboard
                )
            )

        else:

            await send_subject_chapters(
                update,
                matched_subject
            )

        return


    # ─────────────────────────────
    # SUBJECT + CHAPTER
    #
    # Example:
    # Science Ch - 1
    # Hindi R Ch - 3
    # ─────────────────────────────

    match = re.match(
        r"(?i)^(.+?)\s+ch\s*[-.]?\s*(\d+)\s*$",
        text
    )

    if match:

        subject = match.group(1).strip()
        chapter_number = match.group(2).strip()

        if subject.lower() in ("math", "mathematics"):
            subject = "Mathematics"
            chapters = get_chapters(subject)
            target_chapter = next(
                (ch for ch in chapters if re.search(r"\d+", ch) and re.search(r"\d+", ch).group(0) == chapter_number),
                None
            )
            if target_chapter:
                exercises = get_exercises(subject, target_chapter)
                keyboard = [
                    [InlineKeyboardButton(f"📝 Exercise - {exercise}", callback_data=f"ex|{chapters.index(target_chapter)}|{i}")]
                    for i, exercise in enumerate(exercises)
                ]
                keyboard.append([InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data=f"subject|{subject}")])
                await update.message.reply_text(
                    f"📝 *Sᴇʟᴇᴄᴛ E x e r c i s e*\n\n📖 Chapter: {target_chapter}",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                await update.message.reply_text("❌ *Cʜᴀᴘᴛᴇʀ Nᴏᴛ Fᴏᴜɴᴅ*", parse_mode="Markdown")
            return

        note = find_note_by_chapter_number(
            subject,
            chapter_number
        )

        if note:

            try:

                await context.bot.forward_message(
                    chat_id=update.message.chat.id,
                    from_chat_id=note[0],
                    message_id=note[1],
                )

            except Exception as error:

                print(
                    f"Search forward error: {error}"
                )

                await update.message.reply_text(
                    "❌ *Nᴏᴛᴇ Sᴇɴᴅ Nᴀʜɪ Hᴜᴀ*",
                    parse_mode="Markdown"
                )

        else:

            await update.message.reply_text(
                "❌ *Nᴏᴛᴇ Nᴏᴛ Fᴏᴜɴᴅ*\n\n"
                "📚 Is chapter ka note database mein nahi mila.",
                parse_mode="Markdown"
            )

        return


    # ─────────────────────────────
    # CH - NUMBER
    #
    # Example:
    # Ch - 1
    # ─────────────────────────────

    match = re.match(
        r"(?i)^ch\s*[-.]?\s*(\d+)\s*$",
        text
    )

    if match:

        keyboard = [
            [
                InlineKeyboardButton(
                    "🔬 Sᴄɪᴇɴᴄᴇ",
                    callback_data="subject|Science"
                )
            ],
            [
                InlineKeyboardButton(
                    "➗ Mᴀᴛʜᴇᴍᴀᴛɪᴄs",
                    callback_data="subject|Mathematics"
                )
            ],
            [
                InlineKeyboardButton(
                    "📘 Eɴɢʟɪsʜ R",
                    callback_data="subject|English R"
                )
            ],
            [
                InlineKeyboardButton(
                    "🌍 S.Sᴛ",
                    callback_data="subject|S.S.T"
                )
            ],
            [
                InlineKeyboardButton(
                    "💻 Cᴏᴍᴘᴜᴛᴇʀ",
                    callback_data="subject|Computer"
                )
            ],
            [
                InlineKeyboardButton(
                    "📗 Pᴜɴᴊᴀʙɪ R",
                    callback_data="subject|Punjabi R"
                )
            ],
            [
                InlineKeyboardButton(
                    "📕 Hɪɴᴅɪ R",
                    callback_data="subject|Hindi R"
                )
            ],
        ]

        await update.message.reply_text(
            "📚 *Pʟᴇᴀsᴇ Sᴇʟᴇᴄᴛ Sᴜʙᴊᴇᴄᴛ Fɪʀsᴛ*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return


    # ─────────────────────────────
    # GRAMMAR SEARCH
    #
    # Examples:
    # Hindi Gr Letter
    # Punjabi Gr Story
    # English Gr Essay
    # English Gr Notice
    # English Gr E-mail
    # ─────────────────────────────
    # GRAMMAR SUBJECT - SHOW CATEGORY BUTTONS

    grammar_subjects = {
        "punjabi gr": "Punjabi Grammar",
        "punjabi grammar": "Punjabi Grammar",
        "hindi gr": "Hindi Grammar",
        "hindi grammar": "Hindi Grammar",
        "english gr": "English Grammar",
        "english grammar": "English Grammar",
    }

    grammar_subject = grammar_subjects.get(text.lower())

    if grammar_subject:
        categories = get_categories(grammar_subject)
        keyboard = []

        for category in categories:
            keyboard.append([
                InlineKeyboardButton(
                    f"📚 {category}",
                    callback_data=f"category|{grammar_subject}|{category}"
                )
            ])

        if keyboard:
            keyboard.append([
                InlineKeyboardButton(
                    "🔙 Bᴀᴄᴋ",
                    callback_data="get_note"
                )
            ])

            await update.message.reply_text(
                "📚 *Sᴇʟᴇᴄᴛ Cᴀᴛᴇɢᴏʀʏ*\n\n"
                "👇 Choose Letter, Story, Essay or another category.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(
                "❌ *Nᴏ Cᴀᴛᴇɢᴏʀɪᴇs Fᴏᴜɴᴅ*",
                parse_mode="Markdown"
            )

        return
        
    grammar_match = re.match(
        r"(?i)^(hindi|punjabi|english)\s+gr(?:ammar)?\s+"
        r"(letter|story|essay|notice|e-mail|email|chapter)$",
        text
    )

    if grammar_match:

        language = (
            grammar_match.group(1).lower()
        )

        category = (
            grammar_match.group(2)
        )

        if language == "hindi":

            subject = "Hindi Grammar"

        elif language == "punjabi":

            subject = "Punjabi Grammar"

        else:

            subject = "English Grammar"

        if category.lower() == "email":

            category = "E-mail"

        await direct_grammar_search(
            update,
            subject,
            category
        )

        return


    # ─────────────────────────────
    # UNKNOWN SEARCH
    # ─────────────────────────────

    await update.message.reply_text(
        "🔎 *Nᴏᴛᴇ Fᴏᴜɴᴅ Nᴀʜɪ*\n\n"
        "💡 Example:\n"
        "`Science`\n"
        "`Science Ch - 1`\n"
        "`Hindi Gr Letter`",
        parse_mode="Markdown"
    )



# ─────────────────────────────────────
# ADMIN MANUAL REMOVE SYSTEM
# Set ADMIN_ID in FadeHost environment variables.
# This removes a record from notes.db (the bot's menu index);
# it does not delete the original PDF/channel post.
# ─────────────────────────────────────

REMOVE_PAGE_SIZE = 15


def is_admin_user(user_id):
    admin_value = os.getenv("ADMIN_ID", "").strip()
    if not admin_value:
        return False
    try:
        return int(admin_value) == int(user_id)
    except (TypeError, ValueError):
        return False


async def my_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user:
        await update.effective_message.reply_text(
            f"Your Telegram ID: {update.effective_user.id}\n\n"
            "Add this number as ADMIN_ID in FadeHost environment variables, "
            "then restart the bot."
        )


async def remove_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user or not is_admin_user(user.id):
        await update.effective_message.reply_text(
            "⛔ You are not authorized to use this command."
        )
        return

    subjects = get_subjects()
    if not subjects:
        await update.effective_message.reply_text("No notes are saved in the database.")
        return

    keyboard = [
        [InlineKeyboardButton(f"📚 {subject}", callback_data=f"rm_sub|{subject}|0")]
        for subject in subjects
    ]
    await update.effective_message.reply_text(
        "🗑️ MANUAL REMOVE\n\nSelect the subject whose menu entry you want to remove.",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def remove_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    if not user or not is_admin_user(user.id):
        await query.answer("Not authorized.", show_alert=True)
        return

    await query.answer()
    data = query.data or ""
    parts = data.split("|")

    if parts[0] == "rm_sub" and len(parts) == 3:
        subject = parts[1]
        try:
            page = max(0, int(parts[2]))
        except ValueError:
            page = 0
        await show_removal_notes(query, subject, page)
        return

    if parts[0] == "rm_note" and len(parts) == 2:
        try:
            note_id = int(parts[1])
        except ValueError:
            return
        from database import get_chapter_by_note_id
        note = get_chapter_by_note_id(note_id)
        if not note:
            await query.edit_message_text("This entry was not found. It may already be removed.")
            return
        # Row shape: id, chat_id, message_id, title, subject, chapter, category, item_name, date
        title = note[3] or note[5] or note[7] or "Untitled note"
        subject = note[4] or "Unknown subject"
        category = note[6] or ""
        item_name = note[7] or ""
        details = f"Title: {title}\nSubject: {subject}"
        if category:
            details += f"\nCategory: {category}"
        if item_name:
            details += f"\nItem: {item_name}"
        keyboard = [[
            InlineKeyboardButton("✅ YES, REMOVE ENTRY", callback_data=f"rm_yes|{note_id}"),
            InlineKeyboardButton("❌ CANCEL", callback_data=f"rm_cancel|{subject}|0"),
        ]]
        await query.edit_message_text(
            "⚠️ Confirm removal from the bot's menu database?\n\n"
            f"{details}\n\n"
            "The original PDF/channel post will NOT be deleted.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if parts[0] == "rm_yes" and len(parts) == 2:
        try:
            note_id = int(parts[1])
        except ValueError:
            return
        deleted = delete_note_by_id(note_id)
        if deleted:
            await query.edit_message_text(
                "✅ Entry removed from the bot's menu database.\n"
                "The original PDF/channel post remains in Notes Vault."
            )
        else:
            await query.edit_message_text("That entry was already removed or could not be found.")
        return

    if parts[0] == "rm_cancel" and len(parts) == 3:
        await show_removal_notes(query, parts[1], max(0, int(parts[2])))
        return


async def show_removal_notes(query, subject, page):
    total = count_notes_for_removal(subject)
    offset = page * REMOVE_PAGE_SIZE
    rows = get_notes_for_removal(subject, REMOVE_PAGE_SIZE, offset)

    if not rows:
        await query.edit_message_text(
            f"No entries found for {subject}.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Subjects", callback_data="rm_home")
            ]]),
        )
        return

    keyboard = []
    for row in rows:
        note_id, title, row_subject, chapter, category, item_name = row
        label = title or chapter or item_name or category or f"Note ID {note_id}"
        label = str(label).replace("\n", " ")
        if len(label) > 55:
            label = label[:52] + "..."
        keyboard.append([
            InlineKeyboardButton(f"🗑️ {label}", callback_data=f"rm_note|{note_id}")
        ])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"rm_sub|{subject}|{page-1}"))
    if offset + len(rows) < total:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"rm_sub|{subject}|{page+1}"))
    if nav:
        keyboard.append(nav)
    keyboard.append([InlineKeyboardButton("🔙 Subjects", callback_data="rm_home")])

    await query.edit_message_text(
        f"🗑️ MANUAL REMOVE\nSubject: {subject}\n"
        f"Entries: {offset + 1}–{offset + len(rows)} of {total}\n\n"
        "Select the exact entry to remove from the bot's menu:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def remove_home_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = update.effective_user
    if not user or not is_admin_user(user.id):
        await query.answer("Not authorized.", show_alert=True)
        return
    await query.answer()
    subjects = get_subjects()
    keyboard = [
        [InlineKeyboardButton(f"📚 {subject}", callback_data=f"rm_sub|{subject}|0")]
        for subject in subjects
    ]
    await query.edit_message_text(
        "🗑️ MANUAL REMOVE\n\nSelect a subject:",
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None,
    )


# ─────────────────────────────────────
# MAIN
# ─────────────────────────────────────

def main():

    token = os.getenv(
        "BOT_TOKEN"
    )

    if not token:

        raise ValueError(
            "BOT_TOKEN is not set"
        )

    setup_database()

    app = (
        Application
        .builder()
        .token(token)
        .build()
    )


    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", my_id))
    app.add_handler(CommandHandler("remove", remove_start))

    # Manual-remove callbacks must be registered before the general button handler.
    app.add_handler(CallbackQueryHandler(remove_home_callback, pattern=r"^rm_home$"))
    app.add_handler(CallbackQueryHandler(remove_callback, pattern=r"^rm_(?:sub|note|yes|cancel)\|"))

    # Normal inline buttons
    app.add_handler(CallbackQueryHandler(button_handler))


    # Direct search
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_search
        )
    )


    # Notes Vault channel
    app.add_handler(
        MessageHandler(
            filters.UpdateType.CHANNEL_POST,
            channel_note_handler
        )
    )


    print(
        "Nᴏᴛᴇs Sᴇᴀʀᴄʜ Bᴏᴛ is running..."
    )


    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


# ─────────────────────────────────────
# RUN
# ─────────────────────────────────────

if __name__ == "__main__":

    main()
