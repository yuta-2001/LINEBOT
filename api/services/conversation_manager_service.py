from firebase_admin import firestore
from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.messaging.models import (
    MessageAction,
    QuickReply,
    QuickReplyItem
)
from api.const.question_settings import QUESTION_SETTINGS, TEXT_TO_START_CONVERSATION
from api.utils.logger import Logger
from api.repository.firebase_conversation_repository import ConversationRepository

log = Logger().get()

class ConversationManagerService():
    def __init__(self, user_id: str, reply_token: str, conversation_repository: ConversationRepository):
        self.user_id = user_id
        self.reply_token = reply_token
        self.repository = conversation_repository

    def get_keys_from_value(self, d, val):
        return [k for k, v in d.items() if v == val][0]



    def handle_recive_text(self, recive_text):
        conversation_data = self.repository.get_conversation_info_by_user_id(self.user_id)

        content = ''
        if conversation_data:
            content = self.handle_answer(recive_text, conversation_data)
        elif recive_text in list(TEXT_TO_START_CONVERSATION.values()):
            content = self.start_conversation(recive_text)
        else:
            return

        return content



    def start_conversation(self, recive_text):
        type = self.get_keys_from_value(TEXT_TO_START_CONVERSATION, recive_text)
        current_status = QUESTION_SETTINGS[type]['order'][0]
        store_data = {
            'user_id': self.user_id,
            'type': 1,
            'current_status': current_status,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        self.repository.store(store_data)
        content = self._get_reply_content(type, current_status)
        return content



    def handle_answer(self, recive_text, conversation_data):
        current_status = conversation_data['current_status']
        type = conversation_data['type']
        question_info = QUESTION_SETTINGS[type]
        index_of_current = QUESTION_SETTINGS["restaurant"]['order'].index(current_status)
        next_status = QUESTION_SETTINGS["restaurant"]['order'][index_of_current + 1]

        if recive_text in question_info['questions'][current_status]['optioins']:
            content = self._get_reply_content(self, type, next_status)
            return content



    def _get_reply_content(self, type, current_status):
        question_info = QUESTION_SETTINGS[type]['questions'][current_status]
        reply_text = question_info['text']
        options = question_info['options']
        items = []
        for option in options:
            items.append(QuickReplyItem(action=MessageAction(label=option, text=option)))

        return  ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[
                        TextMessage(
                            text=reply_text,
                            quick_reply=QuickReply(items=items)
                        )
                    ]
                )

