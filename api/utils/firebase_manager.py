import firebase_admin
from firebase_admin import (
    credentials,
    firestore
)

class FirebaseManager:
    _instance = None

    @staticmethod
    def get_instance():
        if FirebaseManager._instance is None:
            FirebaseManager()
        return FirebaseManager._instance

    def __init__(self, json_path='api/line-bot-project-db-firebase-adminsdk-zwk0l-6333ab5473.json'):
        if FirebaseManager._instance is not None:
            raise Exception("This class is a singleton")
        else:
            FirebaseManager._instance = self
            self._initialize_firebase(json_path)

    def _initialize_firebase(self, json_path):
        cred = credentials.Certificate(json_path)
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()
