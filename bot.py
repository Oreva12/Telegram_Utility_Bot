from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import dotenv
import os
from flask import Flask, request, jsonify
import requests 
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

PAYSTACK_API_KEY = os.getenv("PAYSTACK_API_KEY")

def initiate_payment(amount, user_id):
    """
    Initiates a payment request with Paystack and returns the payment reference.
    """
    headers = {
        "Authorization": f"Bearer {PAYSTACK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "amount": int(amount) * 100,  # Paystack expects the amount in kobo (smallest unit)
        "email": f"user{user_id}@example.com",  # A placeholder email or actual user email
        "reference": f"user_{user_id}_{int(amount)}",  # A unique reference string
        "callback_url": "https://your-callback-url.com"  # Replace with your callback URL
    }

    try:
        response = requests.post("https://api.paystack.co/tran~saction/initialize", json=data, headers=headers)

        if response.status_code == 200:
            response_data = response.json()
            payment_reference = response_data['data']['reference']
            payment_url = response_data['data']['authorization_url']
            
            print(f"Payment initiated successfully. Reference: {payment_reference}")
            return payment_reference, payment_url
        else:
            print(f"Failed to initiate payment: {response.json()}")
            return None, None
    except Exception as e:
        print(f"An error occurred while initiating payment: {str(e)}")
        return None, None


app = Flask(__name__)

@app.route('/paystack/callback', methods=['POST'])
def paystack_callback():
    # Get the JSON data sent by Paystack
    data = request.json
    # Extract reference from the data
    reference = data.get('data', {}).get('reference')

    # Here, you would verify the payment
    if verify_payment(reference):
        # Handle successful payment (e.g., update user wallet)
        return jsonify({'status': 'success', 'message': 'Payment verified'}), 200
    else:
        # Handle payment failure
        return jsonify({'status': 'error', 'message': 'Payment verification failed'}), 400

def verify_payment(reference):
    # Your Paystack secret key from the environment variable
    PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')

    # Set up headers for the request
    headers = {
        'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json'
    }

    # Make a GET request to verify the transaction
    response = requests.get(f'https://api.paystack.co/transaction/verify/{reference}', headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        # Check if the transaction status is successful
        return response_data['data']['status'] == 'success'
    return False


async def fund_wallet(update: Update, context) -> None:
    user_id = update.message.from_user.id
    try:
        amount = float(context.args[0])  # Get the amount from the command arguments
        payment_reference, payment_url = initiate_payment(amount, user_id)

        if payment_reference and payment_url:
            await update.message.reply_text(
                f"Please complete your payment using the link below:\n{payment_url}\n"
                f"Payment Reference: {payment_reference}"
            )
        else:
            await update.message.reply_text("Failed to initiate payment. Please try again later.")
    except IndexError:
        await update.message.reply_text("Please specify the amount to fund your wallet like this: /fund_wallet 500")
    except ValueError:
        await update.message.reply_text("Invalid amount provided. Please enter a number.")
    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")

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

