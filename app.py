import server
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r'/approve_join': {"origins": "*"}})


@app.route('/', methods=["GET", "POST"])
def hello_world():
    return 'Hello, World!'


@app.route('/approve_join', methods=["GET", "POST"])
async def approve_join():
    print("approve_join")
    chat_id = request.form['chat_id']
    user_address = request.form['user_address']
    signature = request.form['signature']

    await server.approve_join_deeplink(chat_id, user_address, signature)

    echo = f"received data:\nchat id: {chat_id}\nuser_address: {user_address}\nsignature: {signature}"
    return echo

if __name__ == "__main__":
    app.run(ssl_context='adhoc')