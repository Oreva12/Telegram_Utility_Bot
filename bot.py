from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import dotenv
import os
import mysql.connector
from mysql.connector import Error

dotenv.load_dotenv()

# Connect to the MySQL database
def create_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        if connection.is_connected():
            print("Connected to the database")
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# Insert a new user or fetch existing user
def get_or_create_user(telegram_id, username):
    connection = create_db_connection()
    cursor = connection.cursor()
    try:
        # Check if user already exists
        cursor.execute("SELECT user_id FROM users WHERE telegram_id = %s", (telegram_id,))
        result = cursor.fetchone()

        if result:
            return result[0]  # user_id
        else:
            # Insert new user
            cursor.execute(
                "INSERT INTO users (telegram_id, username) VALUES (%s, %s)",
                (telegram_id, username)
            )
            connection.commit()
            return cursor.lastrowid  # return newly created user_id
    finally:
        cursor.close()
        connection.close()

# /help command handler
async def help_command(update: Update, context) -> None:
    await update.message.reply_text(
    ''' 
    /start -> Welcome to this Bot 
    /help -> This particular message 
    /content -> This is just a random bot doing nothing much 
    /backend github roadmap -> Complete Backend road map you need to check out 
    /contact -> My Contact
    '''
    )

# Generate greeting for user
async def generate_greeting(update: Update, context) -> str:
    user_name = update.message.from_user.first_name
    telegram_id = update.message.from_user.id

    # Store user in database
    user_id = get_or_create_user(telegram_id, user_name)

    greeting = f"Hello {user_name}, welcome to Orevaoghene's Utility bot! Your User ID is {user_id}."
    return greeting


async def start(update: Update, context) -> None:
    greeting_message = await generate_greeting(update, context)  # Fetch the message
    await update.message.reply_text(greeting_message)

async def echo(update: Update, context) -> None:
    await update.message.reply_text(update.message.text)

async def content(update: Update, context) -> None:
    await update.message.reply_text('We have nothing much in this bot yet')

async def backend(update: Update, context) -> None:
    await update.message.reply_text('Backend roadmap link: https://github.com/PI-Space/Backend-Roadmap-2024')

async def contact(update: Update, context) -> None:
    await update.message.reply_text('contact me: wa.me/+2349019296990')

# Main function
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

    # Register a handler for non-command messages (echoes the user's messages)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start the bot
    app.run_polling()

if __name__ == '__main__':
    main()
    app.run(port=5000)

