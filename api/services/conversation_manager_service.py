import json
import os
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv
from firebase_admin import firestore
from linebot.v3.messaging import (
    FlexCarousel,
    FlexMessage,
    FlexBubble,
    FlexImage,
    FlexBox,
    FlexText,
    FlexIcon,
    FlexButton,
    FlexSeparator,
    MessageAction,
    ReplyMessageRequest,
    TextMessage,
    URIAction
)
from linebot.v3.messaging.models import (
    LocationAction,
    MessageAction,
    QuickReply,
    QuickReplyItem
)
from api.const.question_settings import QUESTION_SETTINGS, TEXT_TO_START_CONVERSATION
from api.utils.logger import Logger
from api.repository.firebase_conversation_repository import ConversationRepository

log = Logger().get()
load_dotenv()

class ConversationManagerService():
    def __init__(self, user_id: str, reply_token: str, conversation_repository: ConversationRepository):
        self.user_id = user_id
        self.reply_token = reply_token
        self.repository = conversation_repository


    def get_keys_from_value(self, d, val):
        return [k for k, v in d.items() if v == val][0]



    def handle_recive_text(self, recive_text):
        conversation_data = self.repository.get_conversation_info_by_user_id(self.user_id).to_dict()

        content = ''
        if conversation_data:
            content = self.handle_answer(recive_text, conversation_data)
        elif recive_text in list(TEXT_TO_START_CONVERSATION.values()):
            content = self.start_conversation(recive_text)
        else:
            return

        return content



    def start_conversation(self, recive_text):
        type = self.get_keys_from_value(TEXT_TO_START_CONVERSATION, recive_text)
        current_status = QUESTION_SETTINGS[type]['order'][0]
        store_data = {
            'user_id': self.user_id,
            'type': type,
            'current_status': current_status,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        self.repository.store(store_data)
        content = self._get_reply_content(type, current_status)
        return content



    def handle_answer(self, recive_text, conversation_data):
        current_status = conversation_data['current_status']
        type = conversation_data['type']
        questions_info = QUESTION_SETTINGS[type]

        if recive_text in questions_info['questions'][current_status]['options']:

            # 最後の質問に対する回答の場合は、回答を保存して現在地の質問を返却
            # 途中の質問に対する回答の場合は、回答を保存して次の質問内容を返却
            if current_status == questions_info['order'][-1]:
                update_data = {
                    'answer.' + questions_info['questions'][current_status]['property']: recive_text
                }
                self.repository.update(self.user_id, update_data)
                content = self._ask_location()
                return content
            else:
                index_of_current = questions_info['order'].index(current_status)
                next_status = questions_info['order'][index_of_current + 1]
                update_data = {
                    'current_status': next_status,
                    'answer.' + questions_info['questions'][current_status]['property']: recive_text
                }
                self.repository.update(self.user_id, update_data)
                content = self._get_reply_content(type, next_status)
                return content



    def get_result(self, latitude, longitude):
        # conversation_data = self.repository.get_conversation_info_by_user_id(self.user_id).to_dict()

        # base_url = os.environ.get('GOOGLE_MAP_API_URL')
        # query = {}
        # query['radius'] = 200
        # query['keyword'] = '海鮮'
        # query['location'] = str(latitude)+','+str(longitude)
        # query['key'] = os.environ.get('GOOGLE_MAP_API_KEY')
        # query['type'] = conversation_data['type']

        # endpoint = base_url + '?' + urlencode(query)
        # log.debug(endpoint)
        # response = requests.get(endpoint)
        # data = response.json()
        # result = data['results'][0]
        # log.debug(result)
        carousel = self._create_flex_message('a')

        return  ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[
                        FlexMessage(
                            alt_text="This is a Flex Carousel",
                            contents=carousel
                        )
                    ]
                )


    def _get_reply_content(self, type, current_status):
        question_info = QUESTION_SETTINGS[type]['questions'][current_status]
        reply_text = question_info['text']
        options = question_info['options']
        items = []
        for option in options:
            items.append(QuickReplyItem(action=MessageAction(label=option, text=option)))

        return  ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[
                        TextMessage(
                            text=reply_text,
                            quick_reply=QuickReply(items=items)
                        )
                    ]
                )

    def _ask_location(self):
        return  ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[
                        TextMessage(
                            text='現在地を選択してください',
                            quick_reply=QuickReply(
                                items=[QuickReplyItem(action=LocationAction(label="location", text="location"))]
                            )
                        )
                    ]
                )
    
    def _create_flex_message(self, data):
        bubble = FlexBubble(
            direction='ltr',
            hero=FlexImage(
                url='https://example.com/cafe.jpg',
                size='full',
                aspect_ratio='20:13',
                aspect_mode='cover',
                action=URIAction(uri='http://example.com', label='label')
            ),
            body=FlexBox(
                layout='vertical',
                contents=[
                    # title
                    FlexText(text='Brown Cafe', weight='bold', size='xl'),
                    # review
                    FlexBox(
                        layout='baseline',
                        margin='md',
                        contents=[
                            FlexIcon(size='sm', url='https://example.com/gold_star.png'),
                            FlexIcon(size='sm', url='https://example.com/grey_star.png'),
                            FlexIcon(size='sm', url='https://example.com/gold_star.png'),
                            FlexIcon(size='sm', url='https://example.com/gold_star.png'),
                            FlexIcon(size='sm', url='https://example.com/grey_star.png'),
                            FlexText(text='4.0', size='sm', color='#999999', margin='md', flex=0)
                        ]
                    ),
                    # info
                    FlexBox(
                        layout='vertical',
                        margin='lg',
                        spacing='sm',
                        contents=[
                            FlexBox(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    FlexText(
                                        text='Place',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    FlexText(
                                        text='Shinjuku, Tokyo',
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5
                                    )
                                ],
                            ),
                            FlexBox(
                                layout='baseline',
                                spacing='sm',
                                contents=[
                                    FlexText(
                                        text='Time',
                                        color='#aaaaaa',
                                        size='sm',
                                        flex=1
                                    ),
                                    FlexText(
                                        text="10:00 - 23:00",
                                        wrap=True,
                                        color='#666666',
                                        size='sm',
                                        flex=5,
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
            footer=FlexBox(
                layout='vertical',
                spacing='sm',
                contents=[
                    # callAction
                    FlexButton(
                        style='link',
                        height='sm',
                        action=URIAction(label='CALL', uri='tel:000000'),
                    ),
                    # separator
                    FlexSeparator(),
                    # websiteAction
                    FlexButton(
                        style='link',
                        height='sm',
                        action=URIAction(label='WEBSITE', uri="https://example.com")
                    )
                ]
            ),
        )
        # bubbles = [FlexMessage(alt_text="hello", contents=bubble), FlexMessage(alt_text="hello", contents=bubble)]
        bubbles = FlexCarousel(contents=[bubble, bubble])
        return bubbles

