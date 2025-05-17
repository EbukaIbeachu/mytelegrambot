from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)

TOKEN = "7728527408:AAE7oJY2Q_6N1mslOoXG0E43TFRywTmukw0"

# --- command callbacks -------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I’m alive. Type /help to see what I do.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start – restart the conversation\n"
        "/stats – get today’s stats")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # do something useful here
    await update.message.reply_text("📊 No stats yet!")

# --- main --------------------------------------------------------------
if __name__ == "__main__":
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start",  start))
    app.add_handler(CommandHandler("help",   help_cmd))
    app.add_handler(CommandHandler("stats",  stats))

    app.run_polling()
