from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import dotenv
import os
dotenv.load_dotenv()

# /start command handler
async def start(update: Update, context) -> None:
    await update.message.reply_text('Hello Aderonke(LOML), you are the best❤')

# /help command handler
async def help_command(update: Update, context) -> None:
    await update.message.reply_text(
    ''' 
    /start -> Welcome to this Bot 
    /help -> This particular message 
    /content -> This is just a random bot doing nothing much 
    /backend github roadmap -> Complete Backend road map you need to check out 
    /contact -> My Contact
    ''')

# Echo handler (replies with the same message sent by the user)
async def echo(update: Update, context) -> None:
    await update.message.reply_text(update.message.text)

async def content(update: Update, context) -> None:
    await update.message.reply_text('We have nothing much in this bot yet')

async def backend(update: Update, context) -> None:
    await update.message.reply_text('Backend roadmap link: https://github.com/PI-Space/Backend-Roadmap-2024')

async def contact(update: Update, context) -> None:
    await update.message.reply_text('contact me: wa.me/+2349019296990')    

def main() -> None:
    # Your bot token from BotFather
    TOKEN = os.environ.get('TOKEN')

    # Create the Application object and pass your bot's token
    app = Application.builder().token(TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("content", content))
    app.add_handler(CommandHandler("backend", backend))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("help", help_command))

    # Register a handler for non-command messages (echoes the user's mes
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start the bot
    app.run_polling()

if __name__ == '__main__':
    main()
