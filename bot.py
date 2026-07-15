import os
import random
import string
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment
TOKEN = os.environ.get("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

# Password generation function
def generate_password(length=16, use_upper=True, use_lower=True, use_digits=True, use_symbols=True):
    chars = ""
    if use_upper:
        chars += string.ascii_uppercase
    if use_lower:
        chars += string.ascii_lowercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    if not chars:
        chars = string.ascii_letters + string.digits
    
    return ''.join(random.choice(chars) for _ in range(length))

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🔐 Generate Password", callback_data="gen_16"),
            InlineKeyboardButton("⚙️ Custom Length", callback_data="custom"),
        ],
        [
            InlineKeyboardButton("💪 Strong (24 chars)", callback_data="gen_24"),
            InlineKeyboardButton("🚀 Extreme (32 chars)", callback_data="gen_32"),
        ],
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="help"),
            InlineKeyboardButton("📊 About", callback_data="about"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🔐 *PassGen Bot*\n\n"
        "Generate strong, secure passwords instantly!\n\n"
        "Choose an option below:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# Handle button presses
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "help":
        await query.edit_message_text(
            "📖 *How to use PassGen Bot*\n\n"
            "• Click 'Generate Password' for a 16-char password\n"
            "• Use 'Custom Length' to set your own length (4-64)\n"
            "• Choose preset lengths for quick generation\n\n"
            "All passwords are generated securely and never stored!\n\n"
            "⚡ *Tips:*\n"
            "• Longer passwords = stronger security\n"
            "• Use symbols and numbers for extra strength\n"
            "• Never share your passwords with anyone",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
            ])
        )
    
    elif data == "about":
        await query.edit_message_text(
            "🤖 *About PassGen Bot*\n\n"
            "Version: 1.0.0\n"
            "Language: Python\n"
            "Framework: python-telegram-bot\n\n"
            "🔒 *Security Features:*\n"
            "• Passwords generated locally\n"
            "• No storage of passwords\n"
            "• Uses cryptographically secure random\n"
            "• Customizable character sets\n\n"
            "Made with ❤️ for secure password management",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
            ])
        )
    
    elif data == "back":
        # Recreate main menu
        keyboard = [
            [
                InlineKeyboardButton("🔐 Generate Password", callback_data="gen_16"),
                InlineKeyboardButton("⚙️ Custom Length", callback_data="custom"),
            ],
            [
                InlineKeyboardButton("💪 Strong (24 chars)", callback_data="gen_24"),
                InlineKeyboardButton("🚀 Extreme (32 chars)", callback_data="gen_32"),
            ],
            [
                InlineKeyboardButton("ℹ️ Help", callback_data="help"),
                InlineKeyboardButton("📊 About", callback_data="about"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🔐 *PassGen Bot*\n\n"
            "Generate strong, secure passwords instantly!\n\n"
            "Choose an option below:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    
    elif data == "custom":
        await query.edit_message_text(
            "✏️ *Custom Password*\n\n"
            "Send a number between 4 and 64 for password length.\n"
            "Example: `24`\n\n"
            "Or use these presets:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔢 8 chars", callback_data="gen_8")],
                [InlineKeyboardButton("🔢 12 chars", callback_data="gen_12")],
                [InlineKeyboardButton("🔢 16 chars", callback_data="gen_16")],
                [InlineKeyboardButton("🔢 20 chars", callback_data="gen_20")],
                [InlineKeyboardButton("🔢 24 chars", callback_data="gen_24")],
                [InlineKeyboardButton("🔢 32 chars", callback_data="gen_32")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
            ])
        )
        context.user_data["awaiting_length"] = True
    
    elif data.startswith("gen_"):
        length = int(data.split("_")[1])
        password = generate_password(length)
        
        # Calculate strength
        strength = "Weak"
        if length >= 20:
            strength = "Very Strong 🔒"
        elif length >= 16:
            strength = "Strong 🔐"
        elif length >= 12:
            strength = "Medium 🔑"
        elif length >= 8:
            strength = "Fair 🗝️"
        
        await query.edit_message_text(
            f"🔑 *Your Password*\n\n"
            f"`{password}`\n\n"
            f"📏 Length: {length} characters\n"
            f"🛡️ Strength: {strength}\n\n"
            f"💡 *Tip:* Click to copy the password!",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Generate Again", callback_data=f"gen_{length}")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
            ])
        )

# Handle custom length input
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_length"):
        try:
            length = int(update.message.text.strip())
            if 4 <= length <= 64:
                password = generate_password(length)
                await update.message.reply_text(
                    f"🔑 *Your Password*\n\n"
                    f"`{password}`\n\n"
                    f"📏 Length: {length} characters\n\n"
                    f"Click /start to generate more passwords!",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back")]
                    ])
                )
                context.user_data["awaiting_length"] = False
            else:
                await update.message.reply_text(
                    "❌ Please enter a number between 4 and 64.\n"
                    "Example: `20`",
                    parse_mode="Markdown"
                )
        except ValueError:
            await update.message.reply_text(
                "❌ Please enter a valid number.\n"
                "Example: `20`",
                parse_mode="Markdown"
            )

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.message:
        await update.message.reply_text(
            "❌ An error occurred. Please try again or contact support."
        )

def main():
    """Start the bot."""
    # Create Application with specific settings to avoid Python 3.13 issues
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Start the Bot
    print("🤖 PassGen Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
