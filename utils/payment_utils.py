import mysql.connector
import os
from mysql.connector import Error

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





import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

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

# Define the callback route correctly
@app.route('/callback', methods=['POST','GET'])
def handle_paystack_callback():
    """Handle Paystack callback to verify payment."""
    if(request.method=="POST"):
        try:
            data = request.get_json()
            if 'data' not in data or 'reference' not in data['data']:
                return jsonify({"status": "failure", "message": "Invalid callback data."}), 400
            reference = data['data']['reference']
            # Verify the payment with Paystack
            paystack = Paystack(secret_key=os.getenv('PAYSTACK_SECRET_KEY'))
            verification_response = paystack.verify_transaction(reference)
            if verification_response['status'] == True:
                # Payment was successful, proceed with your business logic here
                return jsonify({"status": "success", "message": "Payment successful!"}), 200
            else:
                return jsonify({"status": "failure", "message": "Payment failed."}), 400
        except Exception as e:
            return jsonify({"status": "failure", "message": str(e)}), 500
        
    else:
        trxid=request.args.get('trxref')
        return f"Payment {trxid} succesful"
if __name__ == '__main__':
    app.run(port=5000,debug=True)  # Make sure your server is accessible at this URL
