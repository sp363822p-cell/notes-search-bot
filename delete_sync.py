import os
from telethon import TelegramClient, events

from database import delete_note_by_message


API_ID = int(os.getenv("TG_API_ID"))
API_HASH = os.getenv("TG_API_HASH")
SESSION = os.getenv("TG_SESSION")

NOTES_VAULT_ID = int(os.getenv("NOTES_VAULT_ID"))


client = TelegramClient(
    "notes_vault_sync",
    API_ID,
    API_HASH
)


@client.on(events.MessageDeleted(chats=NOTES_VAULT_ID))
async def deleted_message_handler(event):

    for message_id in event.deleted_ids:

        deleted = delete_note_by_message(
            chat_id=NOTES_VAULT_ID,
            message_id=message_id
        )

        if deleted:
            print(
                f"Deleted message removed from database: {message_id}"
            )


async def start_delete_sync():

    await client.start(
        session=SESSION
    )

    print("Notes Vault deletion sync is running...")

    await client.run_until_disconnected()
