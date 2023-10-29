from abc import ABC, abstractclassmethod

class ConversationRepository(ABC):
    @abstractclassmethod
    def store(self, data: dict) -> None:
        raise NotImplementedError()

    @abstractclassmethod
    def update(self, user_id: str, data: dict) -> None:
        raise NotImplementedError()

    @abstractclassmethod
    def delete(self, user_id: str, data: dict) -> None:
        raise NotImplementedError()

    @abstractclassmethod
    def get_conversation_info_by_user_id(self, user_id: str) -> None:
        raise NotImplementedError()
