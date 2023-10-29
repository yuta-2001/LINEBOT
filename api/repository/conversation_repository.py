from abc import ABC, abstractclassmethod

class ConversationRepository(ABC):
    """
    会話記録のDB操作を行う実装クラスのインターフェース

    CURDの基本的なDB操作を定義
    abstractclassmethodとして定義し、継承したクラスはこれらのメソッドを作成する
    """
    @abstractclassmethod
    def store(self, data: dict) -> None:
        """
        会話データを新規で保存

        Parameters
        ----------
        data - dict
            保存するデータの内容
        """
        raise NotImplementedError()

    @abstractclassmethod
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
        raise NotImplementedError()

    @abstractclassmethod
    def delete(self, user_id: str) -> None:
        """
        会話データを削除

        Parameters
        ----------
        user_id - str
            LINEユーザーのユニークID
        """
        raise NotImplementedError()

    @abstractclassmethod
    def get_conversation_info_by_user_id(self, user_id: str) -> None:
        """
        特定ユーザーの会話記録を取得

        Parameters
        ----------
        user_id - str
            LINEユーザーのユニークID
        """
        raise NotImplementedError()
