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
