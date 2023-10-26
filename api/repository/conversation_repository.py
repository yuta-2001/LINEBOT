from abc import abstractclassmethod

class ConversationRepository:
    @abstractclassmethod
    def store(self, data):
        pass

    @abstractclassmethod
    def update(self, user_id, data):
        pass

    @abstractclassmethod
    def delete(self, user_id, data):
        pass
