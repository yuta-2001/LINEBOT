from fastapi import (
    APIRouter,
    Header, 
    Request
)
import os
from dotenv import load_dotenv
from starlette.exceptions import HTTPException
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from api.const.question_settings import QUESTION_SETTINGS
from api.repository.firebase_conversation_repository import FirebaseConversationRepository
from api.services.line_search_restaurant_service import LineSearchRestaurantService
from api.utils.logger import Logger

load_dotenv()
log = Logger().get()
router = APIRouter()

handler = WebhookHandler(os.environ.get('CHANNEL_SECRET'))
configuration = Configuration(access_token=os.environ.get('CHANNEL_ACCESS_TOKEN'))

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
        log.error('webhookエラー発生')
        raise HTTPException(status_code=400, detail="InvalidSignatureError")

    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    recive_text = event.message.text
    user_id = event.source.user_id
    line_bot_api = MessagingApi(ApiClient(configuration))
    conversation_repository = FirebaseConversationRepository()
    conversation_manager = LineSearchRestaurantService(user_id, event.reply_token, conversation_repository)
    user_conversation_info = conversation_manager.get_conversation_info()[0]


    if user_conversation_info:
        if user_conversation_info['type'] == 1:
            if user_conversation_info['current_status'] == 1:
                if recive_text in QUESTION_SETTINGS['restaurant']['questions'][1]['options']:
                    reply_content = conversation_manager.ask_distance(recive_text)
                    line_bot_api.reply_message(reply_content)


    if recive_text == '近くの飲食店を探す':
        reply_content = conversation_manager.ask_genre()
        line_bot_api.reply_message(reply_content)
