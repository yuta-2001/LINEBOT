from api.repository.conversation_repository import ConversationRepository
from api.utils.firebase_manager import FirebaseManager


class FirebaseConversationRepository(ConversationRepository):
    """
    Firebaseでの会話記録のDB管理をするクラス

    ConversationRepository(interface)を継承しCRUDの基本的なDB操作について定義

    Attributes
        db - CollectionReference
            Firebaseのconversationsコレクションとの接続を司る
    """

    def __init__(self):
        self.db = FirebaseManager.get_instance().db.collection('conversations')

    def store(self, data: dict) -> None:
        """
        会話データを新規で保存

        Parameters
        ----------
        data - dict
            保存するデータの内容
        """
        self.db.document(data['user_id']).set(data)

    def update(self, user_id: str, data: dict) -> None:
        """
        会話データの更新

        Parameters
        ----------
        user_id - str
            LINEユーザーのユニークID
        data - dict
            更新したい内容
        """
        self.db.document(user_id).update(data)

    def delete(self, user_id: str) -> None:
        """
        会話データを削除

        Parameters
        ----------
        user_id - str
            LINEユーザーのユニークID
        """
        self.db.document(user_id).delete()

    def get_conversation_info_by_user_id(self, user_id: str) -> None:
        """
        特定ユーザーの会話記録を取得

        Parameters
        ----------
        user_id - str
            LINEユーザーのユニークID
        """
        result = self.db.document(user_id).get()
        if not result:
            return None
        return result
