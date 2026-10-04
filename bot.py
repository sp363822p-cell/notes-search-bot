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
    get_categories,
    get_subjects,
    get_chapter_choices,
    get_chapter_by_note_id,
    get_notes_in_chapter,
    delete_note_by_id,
    find_note,
    find_note_by_chapter_number,
    find_grammar_note,
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
# START
# ─────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

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
# MANUAL REMOVE SYSTEM
# ─────────────────────────────────────

async def remove_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # Only private chat
    if update.effective_chat.type != "private":
        return

    # Admin ID
    admin_id = os.getenv("ADMIN_USER_ID")

    if not admin_id:
        await update.message.reply_text(
            "❌ Remove system is not configured."
        )
        return

    if str(update.effective_user.id) != str(admin_id):
        await update.message.reply_text(
            "❌ *Aᴄᴄᴇss Dᴇɴɪᴇᴅ*\n\n"
            "⚠️ Sirf bot administrator ye command use kar sakta hai.",
            parse_mode="Markdown"
        )
        return

    subjects = get_subjects()

    keyboard = []

    for subject in subjects:

        keyboard.append([
            InlineKeyboardButton(
                f"📚 {subject}",
                callback_data=f"remove_subject|{subject}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "❌ Cᴀɴᴄᴇʟ",
            callback_data="remove_cancel"
        )
    ])

    await update.message.reply_text(
        "╭━━━━━━━━━━━━━━━━━━━━╮\n"
        "🗑 *Rᴇᴍᴏᴠᴇ Nᴏᴛᴇ*\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
        "📚 *Sᴇʟᴇᴄᴛ Sᴜʙᴊᴇᴄᴛ*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def remove_subject_menu(query, subject):

    chapters = get_chapter_choices(subject)

    keyboard = []

    for note_id, chapter in chapters:

        keyboard.append([
            InlineKeyboardButton(
                f"📖 {chapter}",
                callback_data=f"remove_chapter|{note_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Bᴀᴄᴋ",
            callback_data="remove_back_subjects"
        )
    ])

    if not chapters:

        message = (
            "❌ *Nᴏ Cʜᴀᴘᴛᴇʀs Fᴏᴜɴᴅ*\n\n"
            "Is subject mein koi note nahi hai."
        )

    else:

        message = (
            "╭━━━━━━━━━━━━━━━━━━━━╮\n"
            "📖 *Rᴇᴍᴏᴠᴇ Cʜᴀᴘᴛᴇʀ Nᴏᴛᴇ*\n"
            "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
            f"📚 *Sᴜʙᴊᴇᴄᴛ:* {subject}\n\n"
            "👇 *Sᴇʟᴇᴄᴛ Cʜᴀᴘᴛᴇʀ*"
        )

    await query.edit_message_text(
        message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def remove_chapter_menu(query, note_id):

    chapter_data = get_chapter_by_note_id(note_id)

    if not chapter_data:

        await query.edit_message_text(
            "❌ *Cʜᴀᴘᴛᴇʀ Nᴏᴛ Fᴏᴜɴᴅ*",
            parse_mode="Markdown"
        )
        return

    (
        db_id,
        chat_id,
        message_id,
        title,
        subject,
        chapter,
        category,
        item_name,
        date
    ) = chapter_data

    notes = get_notes_in_chapter(
        subject,
        chapter
    )

    keyboard = []

    for note in notes:

        (
            note_id,
            note_chat_id,
            note_message_id,
            note_title,
            note_subject,
            note_chapter,
            note_category,
            note_item_name,
            note_date
        ) = note

        display_name = note_title or note_item_name

        if not display_name:
            display_name = f"Message {note_message_id}"

        # Keep button text short enough
        if len(display_name) > 45:
            display_name = display_name[:42] + "..."

        keyboard.append([
            InlineKeyboardButton(
                f"🗑 {display_name}",
                callback_data=f"remove_note|{note_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(
            "🔙 Bᴀᴄᴋ",
            callback_data=f"remove_subject|{subject}"
        )
    ])

    await query.edit_message_text(
        "╭━━━━━━━━━━━━━━━━━━━━╮\n"
        "🗑 *Sᴇʟᴇᴄᴛ Nᴏᴛᴇ Tᴏ Rᴇᴍᴏᴠᴇ*\n"
        "╰━━━━━━━━━━━━━━━━━━━━╯\n\n"
        f"📚 *Sᴜʙᴊᴇᴄᴛ:* {subject}\n"
        f"📖 *Cʜᴀᴘᴛᴇʀ:* {chapter}\n\n"
        "👇 *Select the exact PDF/part:*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def remove_note_confirm(query, note_id):

    note = get_chapter_by_note_id(note_id)

    if not note:

        await query.edit_message_text(
            "❌ *Nᴏᴛᴇ Aʟʀᴇᴀᴅʏ Rᴇᴍᴏᴠᴇᴅ*",
            parse_mode="Markdown"
        )
        return

    (
        db_id,
        chat_id,
        message_id,
        title,
        subject,
        chapter,
        category,
        item_name,
        date
    ) = note

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Yᴇs, Rᴇᴍᴏᴠᴇ",
                callback_data=f"remove_confirm|{note_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "❌ Cᴀɴᴄᴇʟ",
                callback_data=f"remove_chapter|{note_id}"
            )
        ]
    ]

    display_name = title or item_name or f"Message {message_id}"

    await query.edit_message_text(
        "⚠️ *Cᴏɴғɪʀᴍ Rᴇᴍᴏᴠᴀʟ*\n\n"
        f"📚 *Subject:* {subject}\n"
        f"📖 *Chapter:* {chapter}\n"
        f"📄 *Note:* {display_name}\n\n"
        "🗑 Is note ko bot database se remove karna hai?",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def remove_note_final(query, note_id):

    note = get_chapter_by_note_id(note_id)

    if not note:

        await query.edit_message_text(
            "❌ *Nᴏᴛᴇ Nᴏᴛ Fᴏᴜɴᴅ*",
            parse_mode="Markdown"
        )
        return

    (
        db_id,
        chat_id,
        message_id,
        title,
        subject,
        chapter,
        category,
        item_name,
        date
    ) = note

    deleted = delete_note_by_id(note_id)

    if deleted:

        # Check whether chapter still has notes
        remaining = get_notes_in_chapter(
            subject,
            chapter
        )

        if remaining:

            status = (
                "✅ *Nᴏᴛᴇ Rᴇᴍᴏᴠᴇᴅ*\n\n"
                "📖 Chapter mein abhi aur PDF/parts hain, "
                "isliye chapter button abhi rahega."
            )

        else:

            status = (
                "✅ *Nᴏᴛᴇ Rᴇᴍᴏᴠᴇᴅ*\n\n"
                "🗑 Is chapter ki last PDF/part thi.\n"
                "📖 Chapter button ab nahi dikhega."
            )

    else:

        status = (
            "❌ *Rᴇᴍᴏᴠᴀʟ Fᴀɪʟᴇᴅ*\n\n"
            "Note database mein nahi mila."
        )

    keyboard = [
        [
            InlineKeyboardButton(
                "🗑 Rᴇᴍᴏᴠᴇ Mᴏʀᴇ",
                callback_data="remove_back_subjects"
            )
        ],
        [
            InlineKeyboardButton(
                "🏠 Hᴏᴍᴇ",
                callback_data="back_home"
            )
        ]
    ]

    await query.edit_message_text(
        status,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
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

    for chapter in chapters:

        keyboard.append([
            InlineKeyboardButton(
                f"📖 {chapter}",
                callback_data=f"chapter|{subject}|{chapter}"
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
# GRAMMAR MENU
# ─────────────────────────────────────

async def grammar_menu(query, subject):

    categories = get_categories(subject)

    keyboard = []

    for category in categories:

        keyboard.append([
            InlineKeyboardButton(
                f"📖 {category}",
                callback_data=f"category|{subject}|{category}"
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
# FORWARD NOTE
# ─────────────────────────────────────

async def forward_note(query, context, note):

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

        print(f"Forward error: {error}")

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
    # MANUAL REMOVE SYSTEM
    # ─────────────────────────────

    if data == "remove_cancel":

        await query.edit_message_text(
            "❌ *Rᴇᴍᴏᴠᴇ Cᴀɴᴄᴇʟʟᴇᴅ*",
            parse_mode="Markdown"
        )

        return

    if data == "remove_back_subjects":

        subjects = get_subjects()

        keyboard = []

        for subject in subjects:

            keyboard.append([
                InlineKeyboardButton(
                    f"📚 {subject}",
                    callback_data=f"remove_subject|{subject}"
                )
            ])

        keyboard.append([
            InlineKeyboardButton(
                "❌ Cᴀɴᴄᴇʟ",
                callback_data="remove_cancel"
            )
        ])

        await query.edit_message_text(
            "🗑 *Rᴇᴍᴏᴠᴇ Nᴏᴛᴇ*\n\n"
            "📚 *Sᴇʟᴇᴄᴛ Sᴜʙᴊᴇᴄᴛ*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return

    if data.startswith("remove_subject|"):

        subject = data.split("|", 1)[1]

        await remove_subject_menu(
            query,
            subject
        )

        return

    if data.startswith("remove_chapter|"):

        note_id = int(
            data.split("|", 1)[1]
        )

        await remove_chapter_menu(
            query,
            note_id
        )

        return

    if data.startswith("remove_note|"):

        note_id = int(
            data.split("|", 1)[1]
        )

        await remove_note_confirm(
            query,
            note_id
        )

        return

    if data.startswith("remove_confirm|"):

        note_id = int(
            data.split("|", 1)[1]
        )

        await remove_note_final(
            query,
            note_id
        )

        return
        
    # GET NOTE
    if data == "get_note":

        await subject_menu(query)

        return

    # BACK HOME
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

    # SUBJECT
    if data.startswith("subject|"):

        subject = data.split("|", 1)[1]

        grammar_subjects = [
            "English Grammar",
            "Punjabi Grammar",
            "Hindi Grammar",
        ]

        if subject in grammar_subjects:

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

    # CHAPTER
    if data.startswith("chapter|"):

        parts = data.split("|", 2)

        subject = parts[1]
        chapter = parts[2]

        # First try exact chapter
        note = find_note(
            subject=subject,
            chapter=chapter
        )

        # If exact match fails, try chapter number
        if not note:

            match = re.search(
                r"(\d+)",
                chapter
            )

            if match:

                chapter_number = match.group(1)

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

    # GRAMMAR CATEGORY
    if data.startswith("category|"):

        parts = data.split("|", 2)

        subject = parts[1]
        category = parts[2]

        # Show category items
        # We use database directly
        from database import get_category_items

        items = get_category_items(
            subject,
            category
        )

        keyboard = []

        for item in items:

            keyboard.append([
                InlineKeyboardButton(
                    f"📖 {item}",
                    callback_data=f"item|{subject}|{category}|{item}"
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

        return

    # GRAMMAR ITEM
    if data.startswith("item|"):

        parts = data.split("|", 3)

        subject = parts[1]
        category = parts[2]
        item_name = parts[3]

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

    # Only documents/PDF
    if not post.document:
        return

    caption = post.caption or ""

    data = parse_caption(caption)

    # Subject required
    if not data["subject"]:
        print("Skipped note: Subject missing")
        return

    add_note(
        chat_id=post.chat.id,
        message_id=post.message_id,
        title=data["title"],
        subject=data["subject"],
        chapter=data["chapter"],
        category=data["category"],
        item_name=data["item_name"],
        date=data["date"],
    )

    print(
        "Note indexed: "
        f"{data['subject']} | "
        f"{data['chapter'] or data['category']}"
    )


# ─────────────────────────────────────
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

    print(f"Search received: {text}")

    # ─────────────────────────────
    # SUBJECT ONLY
    # Example: Science
    # ─────────────────────────────

    subjects = [
        "Science",
        "Math",
        "English R",
        "English Grammar",
        "S.S.T",
        "Computer",
        "Punjabi R",
        "Punjabi Grammar",
        "Hindi R",
        "Hindi Grammar",
    ]

    matched_subject = None

    for subject in subjects:

        if text.lower() == subject.lower():

            matched_subject = subject

            break

    if matched_subject:

        chapters = get_chapters(
            matched_subject
        )

        if chapters:

            keyboard = []

            for chapter in chapters:

                keyboard.append([
                    InlineKeyboardButton(
                        f"📖 {chapter}",
                        callback_data=(
                            f"chapter|{matched_subject}|{chapter}"
                        )
                    )
                ])

            await update.message.reply_text(
                "📖 *Sᴇʟᴇᴄᴛ Cʜᴀᴘᴛᴇʀ*\n\n"
                "👇 *Pʟᴇᴀsᴇ Sᴇʟᴇᴄᴛ Yᴏᴜʀ Cʜᴀᴘᴛᴇʀ*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        else:

            await update.message.reply_text(
                "❌ *Nᴏ Cʜᴀᴘᴛᴇʀs Fᴏᴜɴᴅ*",
                parse_mode="Markdown"
            )

        return

    # ─────────────────────────────
    # SUBJECT + CHAPTER
    # Example:
    # Science Ch - 1
    # ─────────────────────────────

    match = re.match(
        r"(?i)^(.+?)\s+ch\s*[-.]?\s*(\d+)\s*$",
        text
    )

    if match:

        subject = match.group(1).strip()
        chapter_number = match.group(2).strip()

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
    # Example:
    # Ch - 1
    # ─────────────────────────────

    match = re.match(
        r"(?i)^ch\s*[-.]?\s*(\d+)\s*$",
        text
    )

    if match:

        chapter_number = match.group(1)

        await update.message.reply_text(
            "📚 *Pʟᴇᴀsᴇ Sᴇʟᴇᴄᴛ Sᴜʙᴊᴇᴄᴛ Fɪʀsᴛ*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔬 Sᴄɪᴇɴᴄᴇ",
                        callback_data="subject|Science"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "➗ Mᴀᴛʜ",
                        callback_data="subject|Math"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📘 Eɴɢʟɪsʜ R",
                        callback_data="subject|English R"
                    )
                ],
            ])
        )

        return

    # ─────────────────────────────
    # GRAMMAR SEARCH
    # Example:
    # Hindi Gr Letter
    # ─────────────────────────────

    grammar_match = re.match(
        r"(?i)^(hindi|punjabi|english)\s+gr(?:ammar)?\s+(letter|story|essay|notice|e-mail|email|chapter)$",
        text
    )

    if grammar_match:

        language = grammar_match.group(1).lower()
        category = grammar_match.group(2)

        if language == "hindi":
            subject = "Hindi Grammar"

        elif language == "punjabi":
            subject = "Punjabi Grammar"

        else:
            subject = "English Grammar"

        if category.lower() == "email":
            category = "E-mail"

        categories = get_categories(
            subject
        )

        actual_category = None

        for item in categories:

            if item.lower() == category.lower():

                actual_category = item

                break

        if not actual_category:

            await update.message.reply_text(
                "❌ *Cᴀᴛᴇɢᴏʀʏ Nᴏᴛ Fᴏᴜɴᴅ*",
                parse_mode="Markdown"
            )

            return

        from database import get_category_items

        items = get_category_items(
            subject,
            actual_category
        )

        keyboard = []

        for item in items:

            keyboard.append([
                InlineKeyboardButton(
                    f"📖 {item}",
                    callback_data=(
                        f"item|{subject}|"
                        f"{actual_category}|{item}"
                    )
                )
            ])

        if items:

            await update.message.reply_text(
                f"📖 *Sᴇʟᴇᴄᴛ {actual_category}*\n\n"
                "👇 *Pʟᴇᴀsᴇ Sᴇʟᴇᴄᴛ Yᴏᴜʀ Nᴏᴛᴇ*",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        else:

            await update.message.reply_text(
                "❌ *Nᴏ Nᴏᴛᴇs Fᴏᴜɴᴅ*",
                parse_mode="Markdown"
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
# MAIN
# ─────────────────────────────────────

def main():

    token = os.getenv("BOT_TOKEN")

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

    # /start
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )
     # /remove
    app.add_handler(
        CommandHandler(
            "remove",
            remove_command
        )
    )
    # Buttons
    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    # Direct message search
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


if __name__ == "__main__":
    main()
