import os

from flask import Flask, request, abort
from dotenv import load_dotenv
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)

load_dotenv()

app = Flask(__name__)

app.config['CHANNEL_SECRET'] = os.getenv('CHANNEL_SECRET')
app.config['CHANNEL_ACCESS_TOKEN'] = os.getenv('CHANNEL_ACCESS_TOKEN')
app.config['GOOGLE_MAP_API_KEY'] = os.getenv('GOOGLE_MAP_API_KEY')

handler = WebhookHandler(app.config['CHANNEL_SECRET'])
line_bot_api = LineBotApi(app.config['CHANNEL_ACCESS_TOKEN'])

## LINE Bot API Webhook
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


## test page
@app.route("/")
def index():
    return "index page"
