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
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)
from api.services.line_service import LineService
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

    if recive_text == '近くの飲食店を探す':
        reply_text, options = LineSearchRestaurantService(event.source.user_id).startConversation()
        quick_reply_messages = LineService().makeQuickReply(options)

        with ApiClient(configuration) as api_client:
            line_bot_api = MessagingApi(api_client)
            line_bot_api.reply_message(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        TextMessage(
                            text=reply_text,
                            quick_reply=quick_reply_messages
                        )
                    ]
                )
            )

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=event.message.text)]
            )
        )