import os
import random
import requests
from typing import List, Union
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

from api.const import (
    ASK_LOCATION_QUESTION,
    CONVERSATION_RESET_TEXT,
    ERROR_TEXT,
    INFORM_TEXT,
    MAX_STARS,
    QUESTION_SETTINGS,
    STAR_NAMES,
    TEXT_TO_START_CONVERSATION,
)
from api.utils.helper import (
    get_keys_from_value,
    get_image_file_url
)
from api.utils.logger import Logger
from api.repository.firebase_conversation_repository import ConversationRepository

log = Logger().get()
load_dotenv()

class ConversationManagerService():
    """
    ユーザーとの会話全般の管理を行います

    主な役割
    - ユーザーのメッセージから適切な返答を生成
    - ユーザーの回答内容をDBに保存
    - 意図しないメッセージが来た場合にvalidationを実行

    Parameters
    ----------
    user_id : str
        メッセージ取得時に渡ってくるLINEユーザーのユニークID
    reply_token : str
        メッセージ取得時に、そのメッセージに返答を行うために必要なtoken
    conversation_repository : ConversationRepository
        会話のデータを保存・取得・削除するためのリポジトリ

    Attributes
    ---------
    user_id : str
        メッセージ取得時に渡ってくるLINEユーザーのユニークID
    reply_token : str
        メッセージ取得時に、そのメッセージに返答を行うために必要なtoken
    conversation_repository : ConversationRepository
        会話のデータを保存・取得・削除するためのリポジトリ
    """

    def __init__(self, user_id: str, reply_token: str, conversation_repository: ConversationRepository):
        self.user_id = user_id
        self.reply_token = reply_token
        self.repository = conversation_repository


    def handle_recive_text(self, receive_text: str) -> 'ReplyMessageRequest':
        """
        ユーザーの入力に対してて適切な回答を生成し返却

        ユーザーの入力に対しての次のアクションを、ユーザーの会話履歴等に基づいて振り分ける
        - 送信してきたユーザーに会話履歴があるかを確認
            - 会話リセットの場合 - 会話リセット用関数を呼び出す
            - ある場合
                - ユーザーの回答ということになるので、answerを処理する関数を呼び出す
            - ない場合
                - 会話スタートのテキストだった場合は会話スタート用のメソッドを呼び出す
                - 上記に当てはまらない場合は不正なリクエストなのでエラー文言を出すメソッドを呼び出す

        Parameters
        ----------
        receive_text : str
            ユーザーからのメッセージ

        Returns
        -------
        ReplyMessageRequest
            割り当てた関数内で生成されたcontentを返却
        """

        conversation_data = self.repository.get_conversation_info_by_user_id(self.user_id).to_dict()

        content = ''
        if receive_text == CONVERSATION_RESET_TEXT:
            content = self.reset_conversation()
        elif conversation_data:
            content = self.handle_answer(receive_text, conversation_data)
        elif receive_text in list(TEXT_TO_START_CONVERSATION.values()):
            content = self.start_conversation(receive_text)
        else:
            content = self._get_next_question_content(ERROR_TEXT['SELECT_FROM_RICH_MENU'])

        return content


    def reset_conversation(self) -> 'ReplyMessageRequest':
        """
        会話履歴のリセット関連処理を行う

        - 会話履歴の削除
        - 返答メッセージの生成

        Returns
        -------
        ReplyMessageRequest
            リセット後の返答メッセージコンテンツ
        """
        self.repository.delete(self.user_id)
        content = self._get_text_reply_content(INFORM_TEXT['RESET_CONVERSATION'])
        return content


    def start_conversation(self, receive_text: str) -> 'ReplyMessageRequest':
        """
        会話を開始する処理を行う

        - 受け取ったメッセージからなんのタイプの検索をするかを判定
        - それに基づいて、ユーザー用の会話履歴を保存
        - 最初の質問内容を返却する

        Paramenters
        -----------
        receive_text : str
            ユーザーからのメッセージ内容
        
        Returns
        -------
        ReplyMessageRequest
            次の質問に関する返答メッセージコンテンツ
        """
        type = get_keys_from_value(TEXT_TO_START_CONVERSATION, receive_text)
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


    def handle_answer(self, receive_text: str, conversation_data: dict) -> 'ReplyMessageRequest':
        """
        会話履歴のあるユーザー対して、回答メッセージに基づきデータの保存と次の質問メッセージコンテンツ等を返却

        - ユーザーのメッセージがクイックリプライの選択肢にあるものかを判定
            - ある場合
                - 最後の質問に対する回答
                    - 回答の保存と次の質問に関するコンテンツ(位置情報入力を求めるメッセージ)を返却
                - それ以外
                    回答の保存と次の質問に関するコンテンツを返却
            - ない場合 - エラーメッセージコンテンツを返却

        Parameters
        ----------
        receive_text : str
            ユーザーからのメッセージ内容
        conversation_data : dict
            ユーザーのこれまでの検索会話履歴

        Returns
        -------
        ReplyMessageRequest
            次の質問に関する返答メッセージコンテンツまたは位置情報コンテンツ
        """
        current_status = conversation_data['current_status']
        type = conversation_data['type']
        questions_info = QUESTION_SETTINGS[type]

        if receive_text in questions_info['questions'][current_status]['options']:

            # 最後の質問に対する回答の場合は、回答を保存して現在地の質問を返却
            # 途中の質問に対する回答の場合は、回答を保存して次の質問内容を返却
            if current_status == questions_info['order'][-1]:
                update_data = {
                    'answer.' + questions_info['questions'][current_status]['property']: receive_text
                }

                self.repository.update(self.user_id, update_data)
                content = self._get_location_content(ASK_LOCATION_QUESTION)
                return content
            else:
                index_of_current = questions_info['order'].index(current_status)
                next_status = questions_info['order'][index_of_current + 1]
                update_data = {
                    'current_status': next_status,
                    'answer.' + questions_info['questions'][current_status]['property']: receive_text
                }

                self.repository.update(self.user_id, update_data)
                content = self._get_next_question_content(type, next_status)
                return content
        else:
            content = self._get_text_reply_content(ERROR_TEXT['SELECT_FROM_QUICK_REPLY'])
            return content


    def get_result(self, latitude: str, longitude: str) -> 'ReplyMessageRequest':
        conversation_data = self.repository.get_conversation_info_by_user_id(self.user_id).to_dict()

        if conversation_data:
            if self._is_answerd_last_question(conversation_data):
                base_url = os.environ.get('GOOGLE_MAP_API_URL')
                query = conversation_data['answer']
                query['location'] = latitude+','+longitude
                query['key'] = os.environ.get('GOOGLE_MAP_API_KEY')
                query['type'] = conversation_data['type']

                endpoint = base_url + '?' + urlencode(query) + '&opennow'
                response = requests.get(endpoint)
                data = response.json()
                result = random.shuffle(data['results'])
                result = result[:3]
                self.repository.delete(self.user_id)
                carousel = self._get_flex_message(result)

                return  ReplyMessageRequest(
                            reply_token=self.reply_token,
                            messages=[
                                FlexMessage(
                                    alt_text="出力結果一覧",
                                    contents=carousel
                                )
                            ]
                        )
            else:
                content = self._get_text_reply_content('質問が最後まで終わっていません。')
                return content
        else:
            content = self._get_text_reply_content('会話記録がありません。')
            return content


    def _get_next_question_content(self, type: str, status: int) -> 'ReplyMessageRequest':
        """
        次の質問に関するコンテンツを作成

        検索のtypeとステータスナンバーから次の質問に関するコンテンツを作成
        - 質問の回答選択肢をクイックリプライで作成
        - 質問分をテキストで返却

        Paramenters
        -----------
        type : str
            検索のtype(restaurant)などの文字列
        status : int
            検索における何問目の質問かという情報

        Returns
        -------
        ReplyMessageRequest
            質問内容テキストと選択肢のクイックリプライコンテンツを生成し返却
        """

        question_info = QUESTION_SETTINGS[type]['questions'][status]
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


    def _get_text_reply_content(self, reply_text: str) -> 'ReplyMessageRequest':
        """
        引数で受けた文字列を元に返信コンテンツを生成して返却

        Parameters
        reply_text : str
            返信で使用するメッセージ内容

        Returns
        ReplyMessageRequest
            reply_textを元に生成した返信コンテンツ
        """
        return  ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[
                        TextMessage(
                            text=reply_text,
                        )
                    ]
                )


    def _get_location_content(self, reply_text: str) -> 'ReplyMessageRequest':
        """
        引数で受けたメッセージと位置情報を選択してもらうクイックリプライのコンテンツを生成して返却

        Parameters
        reply_text : str
            返信で使用するメッセージ内容

        Returns
        ReplyMessageRequest
            reply_textで受けた返信メッセージと、クイックリプライでlocationを入力するメッセージコンテンツ
        """
        return  ReplyMessageRequest(
                    reply_token=self.reply_token,
                    messages=[
                        TextMessage(
                            text=reply_text,
                            quick_reply=QuickReply(
                                items=[QuickReplyItem(action=LocationAction(label="location", text="location"))]
                            )
                        )
                    ]
                )


    def _get_flex_message(self, data: dict) -> 'FlexCarousel':
        """
        
        """
        items = []

        for item in data:
            image_url = self._get_photo_url(item["photos"][0]["photo_reference"])
            stars = self._create_stars(float(item['rating']))

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


    def _get_photo_url(self, photo_reference: str) -> str:
        """
        photo_reference(Places APIから取得できるお店の画像に関する文字列情報)を元に画像linkを作成

        Parameters
        ----------
        photo_reference : str
            Places APIから取得できるお店の画像に関する文字列情報

        Returns
        -------
        str
            生成した画像リンクが返却される
        """
        link = 'https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference='+photo_reference+'&key='+os.environ.get('GOOGLE_MAP_API_KEY')
        return link


    def _create_stars(self, rating: float) -> List[Union[FlexIcon, FlexText]]:
        """
        ratingの値から適切な星マークのコンテンツを取得

        Parameters
        ----------
        rating : float
            星マークを描画するための評価値。0-5のfloat値が渡ってくる

        Returns
        -------
        List[Union[FlexIcon, FlexText]]
            星マークのリスト。最後の要素には評価値がテキストとして追加される。
        """
        full_star_url = get_image_file_url(STAR_NAMES['FULL_STAR'])
        half_star_url = get_image_file_url(STAR_NAMES['HALF_STAR'])
        empty_star_url = get_image_file_url(STAR_NAMES['EMPTY_STAR'])

        # 整数部分と小数部分に分割
        int_part = int(rating)
        decimal_part = rating - int_part

        content = [FlexIcon(size='sm', url=full_star_url) for _ in range(int_part)]

        # 小数部分が0.5以上の場合、半分の星を追加
        if decimal_part >= 0.5:
            content.append(FlexIcon(size='sm', url=half_star_url))
            int_part += 1  # すでに半分の星を追加したので、残りの空の星の数を1つ減らす

        # 残りの星をempty_starで埋める
        content.extend([FlexIcon(size='sm', url=empty_star_url) for _ in range(MAX_STARS - int_part)])
        content.append(FlexText(text=str(rating), size='sm', color='#999999', margin='md', flex=0))

        return content


    def _is_answerd_last_question(self, conversation_data):
        last_question_index = QUESTION_SETTINGS[conversation_data['type']]['order'][-1]
        last_question_property = QUESTION_SETTINGS[conversation_data['type']][last_question_index]['property']
        return last_question_property in conversation_data['answer']

