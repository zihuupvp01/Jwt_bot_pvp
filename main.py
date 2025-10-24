import asyncio
import json
import random
import string
import os
from datetime import datetime
from aiohttp import ClientSession
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from keep_alive import keep_alive

BOT_TOKEN = os.getenv("8448327784:AAE8TVqnooGN7ZNI4-vpLZfau3Gt-pNiNl4")

API_URLS = [
    "https://senpai-jwt-v1.vercel.app/token?uid={uid}&password={password}",
    "https://senpai-jwt-v2.vercel.app/token?uid={uid}&password={password}",
    "https://senpai-jwt-v3.vercel.app/token?uid={uid}&password={password}",
"https://senpai-jwt-v4.vercel.app/token?uid={uid}&password={password}",
    "https://senpai-jwt-v5.vercel.app/token?uid={uid}&password={password}",
    "https://senpai-jwt-v6.vercel.app/token?uid={uid}&password={password}",
    "https://senpai-jwt-v7.vercel.app/token?uid={uid}&password={password}",
    "https://senpai-jwt-v8.vercel.app/token?uid={uid}&password={password}",
    "https://senpai-jwt-v9.vercel.app/token?uid={uid}&password={password}",
]

ANIME_NAMES = [
    "Naruto", "Sasuke", "Itachi", "Hinata", "Sakura", "Kakashi", "Goku", "Vegeta", "Luffy", "Zoro",
    "Nami", "Eren", "Levi", "Mikasa", "Tanjiro", "Nezuko", "Gojo", "Yuji", "Asta", "Ichigo"
]

def chunk_accounts(accounts, num_chunks):
    chunks = [[] for _ in range(num_chunks)]
    for i, account in enumerate(accounts):
        chunks[i % num_chunks].append(account)
    return chunks

async def fetch_tokens(session, chunk, api_template):
    tokens = []
    invalid_accounts = []
    for acc in chunk:
        try:
            url = api_template.format(uid=acc['uid'], password=acc['password'])
            async with session.get(url) as resp:
                data = await resp.json()
                if "token" in data:
                    tokens.append({"token": data["token"]})
                else:
                    invalid_accounts.append(acc)
        except Exception:
            invalid_accounts.append(acc)
    return tokens, invalid_accounts

async def process_json(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_path = await file.download_to_drive()
    
    with open(file_path, 'r') as f:
        accounts = json.load(f)

    total_accounts = len(accounts)
    await update.message.reply_text(f"⏳ Processing your accounts...\nTotal accounts received: {total_accounts}")

    tokens = []
    invalid_accounts = []

    async with ClientSession() as session:
        chunks = chunk_accounts(accounts, len(API_URLS))
        tasks = [
            fetch_tokens(session, chunks[i], API_URLS[i])
            for i in range(len(chunks)) if chunks[i]
        ]
        results = await asyncio.gather(*tasks)
        for result in results:
            tokens.extend(result[0])
            invalid_accounts.extend(result[1])

    name = random.choice(ANIME_NAMES)
    filename = f"account.txt"
    with open(filename, "w") as f:
        json.dump(tokens, f, indent=2)

    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=open(filename, "rb"),
        caption=f"✅ Tokens generated for {len(tokens)} accounts"
    )

    if invalid_accounts:
        with open("invalid_accounts.txt", "w") as f:
            json.dump(invalid_accounts, f, indent=2)
        await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=open("invalid_accounts.txt", "rb"),
            caption=f"⚠️ Failed to generate tokens for {len(invalid_accounts)} accounts"
        )
        os.remove("invalid_accounts.txt")

    os.remove(file_path)
    os.remove(filename)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 **Welcome to Senpai JWT Bot!**\n\n"
        "🔐 This bot generates JWT tokens from your uploaded `.json` file containing UID and Password pairs.\n\n"
        "📤 Just upload your `.json` file and relax — I’ll generate working tokens and send them back to you.\n\n"
        "ℹ️ To know the correct format for the file, send the command /help\n\n"
        "__~ Developed by your Senpai 🧠__"
    )
    await update.message.reply_markdown(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    format_text = (
        "📄 **Your JSON file should look like this:**\n"
        "```json\n"
        "[\n"
        "  {\"uid\": \"your_uid1\", \"password\": \"your_password1\"},\n"
        "  {\"uid\": \"your_uid2\", \"password\": \"your_password2\"}\n"
        "]\n"
        "```"
    )
    await update.message.reply_markdown(format_text)

def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.Document.FileExtension("json"), process_json))
    print("🤖 BOT IS RUNNING ✅")
    app.run_polling()

if __name__ == "__main__":
    main()