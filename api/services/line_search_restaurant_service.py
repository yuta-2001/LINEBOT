from firebase_admin import firestore
from linebot.v3.messaging import (
    ReplyMessageRequest,
    TextMessage
)
from api.const.question_settings import QUESTION_SETTINGS
from api.const.types import TYPES
from api.services.line_service import LineService
from api.utils.logger import Logger
from api.repository.firebase_conversation_repository import ConversationRepository

log = Logger().get()

class LineSearchRestaurantService(LineService):
    def __init__(self, user_id: str, reply_token: str, conversation_repository: ConversationRepository):
        self.user_id = user_id
        self.search_type = 'restaurant'
        self.reply_token = reply_token
        self.repository = conversation_repository

    def ask_genre(self):
        current_status = QUESTION_SETTINGS[self.search_type]['order'][0]
        self._create_new_conversation(current_status)

        reply_text = QUESTION_SETTINGS[self.search_type]['questions'][current_status]['text']
        options = list(QUESTION_SETTINGS[self.search_type]['questions'][current_status]['options'].keys())
        quick_reply_messages = self._make_quick_reply(options)

        return  ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[
                        TextMessage(
                            text=reply_text,
                            quick_reply=quick_reply_messages
                        )
                    ]
                )

    def ask_distance(self, answer):
        current_status = QUESTION_SETTINGS[self.search_type]['order'][1]
        self._update_conversation(answer, current_status)
        reply_text = QUESTION_SETTINGS[self.search_type]['questions'][current_status]['text']
        options = list(QUESTION_SETTINGS[self.search_type]['questions'][current_status]['options'].keys())
        quick_reply_messages = self._make_quick_reply(options)

        return  ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[
                        TextMessage(
                            text=reply_text,
                            quick_reply=quick_reply_messages
                        )
                    ]
                )

    def get_conversation_info(self):
        return self.repository.get_conversation_info_by_user_id(self.user_id)

    def _create_new_conversation(self, current_status):
        store_data = {
            'user_id': self.user_id,
            'type': TYPES[self.search_type],
            'current_status': current_status,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        self.repository.store(store_data)

    def _update_conversation(self, answer, current_status):
        update_data = {
            'answer': answer,
            'current_status': current_status,
            'update_at': firestore.SERVER_TIMESTAMP
        }
        self.repository.update(self.user_id, update_data)
