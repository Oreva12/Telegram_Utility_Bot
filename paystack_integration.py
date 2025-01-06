import os
import dotenv
import requests
from flask import Flask, request, jsonify

dotenv.load_dotenv()

app = Flask(__name__)

# Define Telegram Bot Token and API URL
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

class Paystack:
    def __init__(self, secret_key=os.getenv('PAYSTACK_SECRET_KEY')):
        self.secret_key = secret_key
        self.base_url = "https://api.paystack.co"

    def initialize_transaction(self, email, amount):
        url = f"{self.base_url}/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        data = {
            "email": email,
            "amount": amount * 100,  # Amount in kobo
            "callback_url": "https://08ab-105-113-22-40.ngrok-free.app/callback"
        }
        response = requests.post(url, json=data, headers=headers)
        return response.json()

    def verify_transaction(self, reference):
        url = f"{self.base_url}/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {self.secret_key}"
        }
        response = requests.get(url, headers=headers)
        return response.json()

# Function to send message via Telegram Bot API
def send_telegram_message(chat_id, message):
    url = TELEGRAM_API_URL
    data = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, data=data)
    return response.json()  # Return response to check for any issues

# Define the callback route correctly
@app.route('/callback', methods=['POST','GET'])
def handle_paystack_callback():
    """Handle Paystack callback to verify payment."""
    if(request.method == "POST"):
        try:
            # Get the callback data from Paystack
            data = request.get_json()

            if 'data' not in data or 'reference' not in data['data']:
                return jsonify({"status": "failure", "message": "Invalid callback data."}), 400

            reference = data['data']['reference']

            # Verify the payment with Paystack
            paystack = Paystack(secret_key=os.getenv('PAYSTACK_SECRET_KEY'))
            verification_response = paystack.verify_transaction(reference)

            # You must capture the user's chat_id when they interact with the bot initially
            # For this example, let's assume it's hardcoded or retrieved from your database
            chat_id = "USER_CHAT_ID"  # Replace this with actual logic to get chat_id

            # If the payment is successful, send success message to the user on Telegram
            if verification_response['status'] == 'success':
                message = "Payment successful! Thank you for your purchase."
                send_telegram_message(chat_id, message)
                return jsonify({"status": "success", "message": "Payment successful!"}), 200
            else:
                message = "Payment failed. Please try again."
                send_telegram_message(chat_id, message)
                return jsonify({"status": "failure", "message": "Payment failed."}), 400

        except Exception as e:
            return jsonify({"status": "failure", "message": str(e)}), 500

    else:
        trxid = request.args.get('trxref')
        return f"Payment {trxid} successful"

if __name__ == '__main__':
    app.run(port=5000, debug=True)  # Make sure your server is accessible at this URL
