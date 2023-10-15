from linebot.v3.messaging.models import (
    MessageAction,
    QuickReply,
    QuickReplyItem
)

class LineService:
    @staticmethod
    def makeQuickReply(options: list):
        items = []
        for option in options:
            items.append(QuickReplyItem(action=MessageAction(label=option, text=option)))

        return QuickReply(items=items)
