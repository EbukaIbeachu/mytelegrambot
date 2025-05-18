from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ChatAction
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler,
    MessageHandler, filters, ConversationHandler
)
import os

# === CONFIGURATION ===
TOKEN = "8108165211:AAEhiP5fm0JlowYk_oLzkiq7E9HHEOGpiPs"
ADMIN_CHAT_ID = 6612187231  # Replace with your Telegram user ID

# === STATES ===
CHOOSE_SERVICE, SCHEDULE_SESSION, AWAIT_PAYMENT_DETAILS = range(3)

# === SERVICES ===
services = [
    ["💄 Makeup Session - ₦20,000", "📸 Studio Photography - ₦40,000"],
    ["💃 Both (Makeup + Photo) - ₦60,000"]
]
deposit_percent = 0.25

# === TEMP DATA STORE ===
user_bookings = {}

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(ChatAction.TYPING)
    await update.message.reply_text(
        "✨ Welcome to *Precys_Glow* — where beauty meets perfection! ✨\n\n"
        "Please choose a service to get started:",
        reply_markup=ReplyKeyboardMarkup(services, resize_keyboard=True),
        parse_mode="Markdown"
    )
    return CHOOSE_SERVICE

# === CHOOSE SERVICE ===
async def choose_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.chat.send_action(ChatAction.TYPING)
    selected = update.message.text

    if "₦" not in selected:
        await update.message.reply_text("❗ Please select a valid service from the options.")
        return CHOOSE_SERVICE

    try:
        price_text = selected.split(" - ₦")[-1].replace(',', '')
        price = int(price_text)
    except ValueError:
        await update.message.reply_text("❗ Could not extract price. Please choose a valid service.")
        return CHOOSE_SERVICE

    deposit = int(price * deposit_percent)

    context.user_data.update({
        "service": selected,
        "price": price,
        "deposit": deposit
    })

    await update.message.reply_text(
        f"Great choice! 🥰 You've selected: {selected}\n\n"
        f"The full price is ₦{price:,}.\n"
        f"To confirm your booking, please pay a 25% deposit of ₦{deposit:,}.\n\n"
        "Now, please tell us your preferred *date and time* for the session.\n"
        "_Example: 25th July, 2 PM_",
        parse_mode="Markdown"
    )
    return SCHEDULE_SESSION

# === SCHEDULE SESSION ===
async def schedule_session(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["schedule"] = update.message.text

    account_details = (
        "💳 *Payment Details:*\n"
        "`Account Name:` PRECYS GLOW BEAUTY HUB\n"
        "`Account Number:` 1234567890\n"
        "`Bank:` XYZ Bank\n\n"
        "Please transfer the deposit and then reply with the *Account Name used* and *Amount Paid*.\n\n"
        "_Example: Jane Doe, ₦5,000_"
    )

    await update.message.reply_text(account_details, parse_mode="Markdown")
    return AWAIT_PAYMENT_DETAILS

# === AWAIT PAYMENT DETAILS ===
async def receive_payment_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    context.user_data["payment_details"] = update.message.text

    user_bookings[user.id] = context.user_data.copy()

    await update.message.reply_text("⏳ *Give us a moment...*", parse_mode="Markdown")

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=(
            f"📩 *New Booking Pending Confirmation*\n\n"
            f"👤 Name: {user.full_name}\n"
            f"🆔 User ID: `{user.id}`\n"
            f"💼 Service: {context.user_data['service']}\n"
            f"📅 Schedule: {context.user_data['schedule']}\n"
            f"💵 Deposit Expected: ₦{context.user_data['deposit']:,}\n"
            f"📥 Payment Info Provided: {context.user_data['payment_details']}\n\n"
            f"✅ *To confirm, reply with:* `/confirm {user.id}`"
        ),
        parse_mode="Markdown"
    )

    await update.message.reply_text(
        "✅ Thank you! Your booking request has been received.\n"
        "We'll confirm once your payment is verified. 💕"
    )
    return ConversationHandler.END

# === ADMIN CONFIRMATION ===
async def confirm_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("❌ You are not authorized to confirm bookings.")
        return

    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("⚠️ Usage: /confirm <user_id>")
        return

    user_id = int(context.args[0])
    booking = user_bookings.get(user_id)

    if not booking:
        await update.message.reply_text("❌ Booking not found for that user ID.")
        return

    await context.bot.send_message(
        chat_id=user_id,
        text=(
            "🎉 *Your booking has been successfully confirmed!*\n\n"
            "We look forward to serving you at *Precys_Glow Beauty Hub*.\n"
            "Please be punctual for your scheduled session. 💄📸",
        ),
        parse_mode="Markdown"
    )

    await update.message.reply_text(f"✅ Booking confirmed for user ID: {user_id}")

# === HANDLERS SETUP ===
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSE_SERVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_service)],
            SCHEDULE_SESSION: [MessageHandler(filters.TEXT & ~filters.COMMAND, schedule_session)],
            AWAIT_PAYMENT_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_payment_details)],
        },
        fallbacks=[]
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("confirm", confirm_booking))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
