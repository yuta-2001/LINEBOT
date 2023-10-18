from abc import abstractclassmethod

class ConversationRepository:
    @abstractclassmethod
    def store(
        self,
        user_id,
        type,
        current_status,
        created_at,
        updated_at
    ):
        pass

    @abstractclassmethod
    def get_conversation_info_by_user_id(self, user_id):
        pass
