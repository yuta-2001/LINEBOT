from api.repository.conversation_repository import ConversationRepository
from api.utils.firebase_manager import FirebaseManager
from api.utils.logger import Logger

log = Logger().get()

class FirebaseConversationRepository(ConversationRepository):
    def __init__(self):
        self.db = FirebaseManager.get_instance().db.collection('conversations')

    def store(self, data):
        self.db.add(data)

    def update(self, user_id, update_data):
        docs = self.db.where('user_id', '==', user_id).stream()
        for doc in docs:
            doc.reference.update(update_data)

    def get_conversation_info_by_user_id(self, user_id):
        result = [doc.to_dict() for doc in self.db.where('user_id', '==', user_id).stream()]
        if not result:
            return None
        return result[0]
