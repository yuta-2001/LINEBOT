from firebase_admin import firestore
from api.const.question_settings import QUESTION_SETTINGS
from api.const.types import TYPES
from api.utils.firebase_manager import FirebaseManager
from api.utils.logger import Logger

log = Logger().get()

class LineSearchRestaurantService:

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.db = FirebaseManager.get_instance().db.collection('conversations')
        self.search_type = 'restaurant'

    def startConversation(self):
        self.db.add({
            'user_id': self.user_id,
            'type': TYPES[self.search_type],
            'current_status': QUESTION_SETTINGS[self.search_type]['order'][0],
            'answers': '',
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        })

        text = QUESTION_SETTINGS[self.search_type]['questions'][QUESTION_SETTINGS[self.search_type]['order'][0]]['text']
        options = list(QUESTION_SETTINGS[self.search_type]['questions'][QUESTION_SETTINGS[self.search_type]['order'][0]]['options'].keys())

        return text, options



