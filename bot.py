
from flask import app, jsonify, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from paystack_integration import Paystack
import os
import dotenv
import mysql.connector
from mysql.connector import Error


dotenv.load_dotenv()

def create_db_connection():
    """Create and return a database connection."""
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

def get_or_create_user(telegram_id, username):
    """Fetch or create a user in the database."""
    connection = create_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT user_id FROM users WHERE telegram_id = %s", (telegram_id,))
        result = cursor.fetchone()

        if result:
            return result[0]  # Return existing user_id
        else:
            cursor.execute(
                "INSERT INTO users (telegram_id, username) VALUES (%s, %s)",
                (telegram_id, username)
            )
            connection.commit()
            return cursor.lastrowid  # Return newly created user_id
    finally:
        cursor.close()
        connection.close()

async def start(update: Update, context) -> None:
    """Handle the /start command."""
    user_name = update.message.from_user.first_name
    greeting_message = f"Hi {user_name}, welcome to the Data Buying Bot!\n\n"
    greeting_message += "Use the /buy <amount> command to buy data."
    await update.message.reply_text(greeting_message)


async def buy_data(update: Update, context) -> None:
    """Handle the /buy <amount> command."""
    # Get the amount from the user's command (e.g., /buy 100)
    if len(context.args) == 0:
        await update.message.reply_text("Please provide an amount. Usage: /buy <amount>")
        return
    
    try:
        amount = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Please provide a valid amount in numbers.")
        return
    
    # Create a Paystack instance and initialize a transaction
    paystack = Paystack(secret_key=os.getenv("PAYSTACK_SECRET_KEY"))
    email = "ovedheo@gmail.com"
    transaction_data = paystack.initialize_transaction(email=email, amount=amount)

    if transaction_data['status']:
        payment_url = transaction_data['data']['authorization_url']
        await update.message.reply_text(f"Click here to complete your payment: {payment_url}")
    else:
        await update.message.reply_text(f"Error initializing payment: {transaction_data['message']}")



def main():
    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    app = Application.builder().token(TOKEN).build()

    # Register handlers
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("buy", buy_data))
    

    # Start the bot
    app.run_polling()

if __name__ == '__main__':
    main()
