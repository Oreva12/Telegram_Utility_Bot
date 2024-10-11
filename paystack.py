import requests
import dotenv
import flask
import os

dotenv.load_dotenv()
base_url="https://api.paystack.co"

class Paystack:
    def __init__(self,url=base_url,key=os.environ.get('PAYSTACK_API_KEY')) -> None:
        self.base_url=base_url
        self.key=key

    def initialize_transaction(self,email:str, amount:int)->dict:
        req=requests.post(f"{self.base_url}/transaction/initialize",
       json={
                "email":email,
                "amount":int(amount)*100
                                                    },
                                      headers={
            "authorization":f"Bearer {self.key}",
            "Content-Type": "application/json",
            },
            )
        return req.json()

    def confirm_transaction(self,reference:str)->tuple:
        req=requests.get(f"{base_url}/transaction/verify/{reference}",
        headers={
            "authorization":f"Bearer {self.key}"
            })
        return req.json().get("status"),req.json()
    @staticmethod
    def handle_callback(data):
        if(data['event']=='charge.success'):
            return data['data']['status']
app=flask.Flask(__name__)

@app.route('/callback',methods=['POST'])
def handle_callback():
    #you should implement a service to verify the origin
    data=flask.request.get_json()
    return Paystack.handle_callback(data)

if __name__=='__main__':
    app.run('0.0.0.0',os.environ.get('CALLBACK_PORT',8080))