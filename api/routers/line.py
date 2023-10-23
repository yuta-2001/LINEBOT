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
    LocationMessageContent,
    MessageEvent,
    TextMessageContent
)
from api.repository.firebase_conversation_repository import FirebaseConversationRepository
from api.services.conversation_manager_service import ConversationManagerService
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

line_bot_api = MessagingApi(ApiClient(configuration))
conversation_repository = FirebaseConversationRepository()

# 質問に対する回答
@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    conversation_manager = ConversationManagerService(event.source.user_id, event.reply_token, conversation_repository)
    reply_content = conversation_manager.handle_recive_text(event.message.text)
    line_bot_api.reply_message(reply_content)

# 位置情報取得後の結果送信
@handler.add(MessageEvent, message=LocationMessageContent)
def handle_location(event: MessageEvent):
    conversation_manager = ConversationManagerService(event.source.user_id, event.reply_token, conversation_repository)
    latitude = event.message.latitude
    longitude = event.message.longitude
    reply_result_content = conversation_manager.get_result(latitude, longitude)
    line_bot_api.reply_message(reply_result_content)
