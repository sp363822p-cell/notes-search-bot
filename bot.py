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
    get_category_items,
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
# SUBJECT LIST
# ─────────────────────────────────────

SUBJECTS = [
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


    # /start
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    # Inline buttons
    app.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )


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
