from api.repository.conversation_repository import ConversationRepository
from api.utils.firebase_manager import FirebaseManager

class FirebaseConversationRepository(ConversationRepository):
    def __init__(self):
        self.db = FirebaseManager.get_instance().db.collection('conversations')

    def store(
            self,
            user_id,
            type,
            current_status,
            created_at,
            updated_at
        ):

        self.db.add({
            'user_id': user_id,
            'type': type,
            'current_status': current_status,
            'created_at': created_at,
            'updated_at': updated_at
        })

    def update(self, user_id, update_data):
        docs = self.db.where('user_id', '==', user_id).stream()
        for doc in docs:
            doc.reference.update(update_data)

    def get_conversation_info_by_user_id(self, user_id):
        return [doc.to_dict() for doc in self.db.where('user_id', '==', user_id).stream()]
