import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)


# ─────────────────────────────────────
# START / WELCOME
# ─────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📚 Gᴇᴛ Nᴏᴛᴇ", callback_data="get_note")]
    ]

    message = (
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

    await update.message.reply_text(
        message,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ─────────────────────────────────────
# SUBJECT MENU
# ─────────────────────────────────────

async def subject_menu(query):
    keyboard = [
        [
            InlineKeyboardButton("🔬 Sᴄɪᴇɴᴄᴇ", callback_data="subject_science"),
            InlineKeyboardButton("➗ Mᴀᴛʜ", callback_data="subject_math"),
        ],
        [
            InlineKeyboardButton("📘 Eɴɢʟɪsʜ R", callback_data="subject_english_r"),
            InlineKeyboardButton("📝 Eɴɢʟɪsʜ Gr", callback_data="subject_english_gr"),
        ],
        [
            InlineKeyboardButton("🌍 S.Sᴛ", callback_data="subject_sst"),
            InlineKeyboardButton("💻 Cᴏᴍᴘᴜᴛᴇʀ", callback_data="subject_computer"),
        ],
        [
            InlineKeyboardButton("📗 Pᴜɴᴊᴀʙɪ R", callback_data="subject_punjabi_r"),
            InlineKeyboardButton("📝 Pᴜɴᴊᴀʙɪ Gr", callback_data="subject_punjabi_gr"),
        ],
        [
            InlineKeyboardButton("📕 Hɪɴᴅɪ R", callback_data="subject_hindi_r"),
            InlineKeyboardButton("📝 Hɪɴᴅɪ Gr", callback_data="subject_hindi_gr"),
        ],
        [
            InlineKeyboardButton("🔙 Bᴀᴄᴋ", callback_data="back_home")
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
# BUTTON HANDLER
# ─────────────────────────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "get_note":
        await subject_menu(query)

    elif query.data == "back_home":
        keyboard = [
            [InlineKeyboardButton("📚 Gᴇᴛ Nᴏᴛᴇ", callback_data="get_note")]
        ]

        message = (
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

        await query.edit_message_text(
            message,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


# ─────────────────────────────────────
# MAIN
# ─────────────────────────────────────

def main():
    token = os.getenv("BOT_TOKEN")

    if not token:
        raise ValueError("BOT_TOKEN is not set")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Nᴏᴛᴇs Sᴇᴀʀᴄʜ Bᴏᴛ is running...")

    app.run_polling()


if __name__ == "__main__":
    main()
