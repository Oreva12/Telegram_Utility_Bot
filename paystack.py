import requests
import dotenv
import flask
import os

dotenv.load_dotenv()
base_url=""

class Paystack:
    def __init__(self,url=base_url,key=os.environ.get('PAYSTACK_API_KEY')) -> None:
        self.base_url=base_url
        self.key=key

    def initialize_transaction(self,)->str:
        pass

    def confirm_transaction(self,)->bool:
        pass

    @staticmethod
    def handle_callback(data):
        pass
app=flask.Flask()

@app.route('/callback',methods=['POST'])
def handle_callback():
    data=flask.request.get_json()
    return Paystack.handle_callback(data)

if __name__=='__main__':
    app.run('0.0.0.0',os.environ.get('CALLBACK_PORT',8080))