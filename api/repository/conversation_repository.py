from abc import abstractclassmethod

class ConversationRepository:
    @abstractclassmethod
    def store(self, data):
        pass
