import logging
import os
from dotenv import load_dotenv

load_dotenv()

class Logger:
    def __init__(self, name=__name__):
        self.logger = logging.getLogger(name)

        env = os.getenv("ENV", "production")
        if env == "local":
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

        # ログをコンソールに表示するハンドラ
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

        # ログをファイルに出力するハンドラ
        fh = logging.FileHandler('api/app.log')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def get(self):
        return self.logger
