import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
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
# BUTTON HANDLER
# ─────────────────────────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "get_note":
        await subject_menu(query)
        return

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

    if data.startswith("subject|"):

        subject = data.split("|", 1)[1]

        grammar_subjects = [
            "English Grammar",
            "Punjabi Grammar",
            "Hindi Grammar",
        ]

        if subject in grammar_subjects:
            await grammar_menu(query, subject)
        else:
            await chapter_menu(query, subject)

        return

    if data.startswith("chapter|"):

        parts = data.split("|", 2)

        subject = parts[1]
        chapter = parts[2]

        await query.edit_message_text(
            f"📖 *{subject}*\n\n"
            f"📚 *Chapter:* {chapter}\n\n"
            "🔎 Note forwarding next step me connect hoga...",
            parse_mode="Markdown",
        )

        return

    if data.startswith("category|"):

        parts = data.split("|", 2)

        subject = parts[1]
        category = parts[2]

        await query.edit_message_text(
            f"📖 *{subject}*\n\n"
            f"📚 *Category:* {category}\n\n"
            "🔎 Note forwarding next step me connect hoga...",
            parse_mode="Markdown",
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

    caption = post.caption or ""

    # Sirf PDF/document posts ko process karenge
    if not post.document:
        return

    # Caption se information read karo
    data = parse_caption(caption)

    # Subject missing ho to note save nahi karna
    if not data["subject"]:
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
        f"Note indexed: "
        f"{data['subject']} | "
        f"{data['chapter'] or data['category']}"
    )


# ─────────────────────────────────────
# MAIN
# ─────────────────────────────────────

def main():

    token = os.getenv("BOT_TOKEN")

    if not token:
        raise ValueError("BOT_TOKEN is not set")

    setup_database()

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(
        CallbackQueryHandler(button_handler)
    )

    # Notes Vault channel ke naye PDFs
    app.add_handler(
        MessageHandler(
            filters.UpdateType.CHANNEL_POST,
            channel_note_handler
        )
    )

    print("Nᴏᴛᴇs Sᴇᴀʀᴄʜ Bᴏᴛ is running...")

    app.run_polling(
        allowed_updates=Update.ALL_TYPES
    )


if __name__ == "__main__":
    main()
