import os
import random
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
from api.const.const import QUESTION_SETTINGS, TEXT_TO_START_CONVERSATION, CONVERSATION_RESET_TEXT
from api.utils.helper import get_keys_from_value
from api.utils.logger import Logger
from api.repository.firebase_conversation_repository import ConversationRepository

log = Logger().get()
load_dotenv()

class ConversationManagerService():
    def __init__(self, user_id: str, reply_token: str, conversation_repository: ConversationRepository):
        self.user_id = user_id
        self.reply_token = reply_token
        self.repository = conversation_repository

    def handle_recive_text(self, recive_text):
        conversation_data = self.repository.get_conversation_info_by_user_id(self.user_id).to_dict()

        content = ''
        if recive_text == CONVERSATION_RESET_TEXT:
            content = self.reset_conversation()
        elif conversation_data:
            content = self.handle_answer(recive_text, conversation_data)
        elif recive_text in list(TEXT_TO_START_CONVERSATION.values()):
            content = self.start_conversation(recive_text)
        else:
            content = self.caution_to_select_from_rich_menu()

        return content

    def reset_conversation(self):
        self.repository.delete(self.user_id)
        reply_str = '検索内容をリセットしました。'
        content = self._get_text_reply_content(reply_str)
        return content

    def caution_to_select_from_rich_menu(self):
        caution = 'リッチメニューから選択してください'
        content = self._get_next_question_content(caution)
        return content

    def start_conversation(self, recive_text):
        type = get_keys_from_value(TEXT_TO_START_CONVERSATION, recive_text)
        current_status = QUESTION_SETTINGS[type]['order'][0]
        store_data = {
            'user_id': self.user_id,
            'type': type,
            'current_status': current_status,
            'created_at': firestore.SERVER_TIMESTAMP,
            'updated_at': firestore.SERVER_TIMESTAMP
        }
        self.repository.store(store_data)
        content = self._get_next_question_content(type, current_status)
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
                content = self._get_next_question_content(type, next_status)
                return content

    def get_result(self, latitude, longitude):
        conversation_data = self.repository.get_conversation_info_by_user_id(self.user_id).to_dict()

        base_url = os.environ.get('GOOGLE_MAP_API_URL')
        query = conversation_data['answer']
        query['location'] = str(latitude)+','+str(longitude)
        query['key'] = os.environ.get('GOOGLE_MAP_API_KEY')
        query['type'] = conversation_data['type']

        endpoint = base_url + '?' + urlencode(query) + '&opennow'
        response = requests.get(endpoint)
        data = response.json()
        result = random.shuffle(data['results'])
        result = result[:3]
        self.repository.delete(self.user_id)
        carousel = self._create_flex_message(result)

        return  ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[
                        FlexMessage(
                            alt_text="出力結果一覧",
                            contents=carousel
                        )
                    ]
                )

    def _get_next_question_content(self, type, current_status):
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

    def _get_text_reply_content(self, reply_text):
        return  ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[
                        TextMessage(
                            text=reply_text,
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
        items = []

        for item in data:
            image_url = self._get_photo_url(item["photos"][0]["photo_reference"])
            stars = self._create_stars(int(item['rating']))

            place_id = item['place_id']
            google_maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"

            bubble = FlexBubble(
                direction='ltr',
                hero=FlexImage(
                    url=image_url,
                    size='full',
                    aspect_ratio='3:2',
                    aspect_mode='cover',
                ),
                body=FlexBox(
                    layout='vertical',
                    contents=[
                        # title
                        FlexText(text=item['name'], weight='bold', size='xl'),
                        # review
                        FlexBox(
                            layout='baseline',
                            margin='md',
                            contents=stars
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
                                            text='レビュー数',
                                            color='#aaaaaa',
                                            size='sm',
                                            flex=2
                                        ),
                                        FlexText(
                                            text=str(item['user_ratings_total']),
                                            wrap=True,
                                            color='#666666',
                                            size='sm',
                                            flex=5
                                        )
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
                        FlexButton(
                            style='link',
                            height='sm',
                            action=URIAction(label='Google Map', uri=google_maps_url)
                        )
                    ]
                ),
            )
            items.append(bubble)

        bubbles = FlexCarousel(contents=items)
        return bubbles

    def _get_photo_url(self, photo_reference):
        link = 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference='+photo_reference+'&key='+os.environ.get('GOOGLE_MAP_API_KEY')
        return link

    def _create_stars(self, rating):
        gold_star_url = 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gold_star_28.png'
        gray_star_url = 'https://scdn.line-apps.com/n/channel_devcenter/img/fx/review_gray_star_28.png'
        MAX_STARS = 5

        content = [
            FlexIcon(size='sm', url=gold_star_url) if i < rating else FlexIcon(size='sm', url=gray_star_url)
            for i in range(MAX_STARS)
        ] + [FlexText(text=str(rating), size='sm', color='#999999', margin='md', flex=0)]

        return content
