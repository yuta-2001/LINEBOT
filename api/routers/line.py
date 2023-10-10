from fastapi import APIRouter, Header, Request
# from modules.line import getHandler
import os
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from starlette.exceptions import HTTPException

load_dotenv()
router = APIRouter()

handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))
line_bot_api = LineBotApi(os.environ.get('CHANNEL_ACCESS_TOKEN'))

@router.post(
    '/api/callback',
    summary='LINE Message APIからのコールバック',
    description='ユーザーからメッセージを受信した際、LINE Message APIからこちらにリクエストが送られます。',
)
async def callback(request: Request, x_line_signature=Header(None)):
    body = await request.body()

    try:
        handler.handle(body.decode("utf-8"), x_line_signature)

    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="InvalidSignatureError")

    return "OK"
