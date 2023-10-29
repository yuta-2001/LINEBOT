from api.repository.conversation_repository import ConversationRepository
from api.utils.firebase_manager import FirebaseManager


class FirebaseConversationRepository(ConversationRepository):
    def __init__(self):
        self.db = FirebaseManager.get_instance().db.collection('conversations')

    def store(self, data: dict) -> None:
        self.db.document(data['user_id']).set(data)

    def update(self, user_id: str, data: dict) -> None:
        self.db.document(user_id).update(data)

    def delete(self, user_id: str) -> None:
        self.db.document(user_id).delete()

    def get_conversation_info_by_user_id(self, user_id: str) -> None:
        result = self.db.document(user_id).get()
        if not result:
            return None
        return result
