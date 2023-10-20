from linebot.v3.messaging.models import (
    MessageAction,
    QuickReply,
    QuickReplyItem
)

class LineService:
    def _make_quick_reply(self, options):
        items = []
        for option in options:
            items.append(QuickReplyItem(action=MessageAction(label=option, text=option)))

        return QuickReply(items=items)
