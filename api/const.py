# それぞれの質問内容を格納
QUESTION_SETTINGS = {
    "restaurant": {
        'order': [1, 2],
        'questions': {
            1: {
                'id': 1,
                'text': 'お好みのジャンルを選択してください',
                'property': 'keyword',
                'options': [
                    '日本食',
                    'イタリアン',
                    '中華料理',
                    '韓国料理',
                    'インド料理',
                ],
            },
            2: {
                'id': 2,
                'text': '現在地からの距離(m)を選択してください',
                'property': 'radius',
                'options': [
                    '100',
                    '2000',
                    '3000',
                    '4000',
                    '5000'
                ],
            },
        }
    },
    'cafe': {
        'order': [1],
        'questions': {
            1: {
                'id': 1,
                'text': '現在地からの距離(m)を選択してください',
                'property': 'radius',
                'options': [
                    '500',
                    '1000',
                    '1500',
                    '2000',
                    '2500'
                ],
            },
        }
    }
}

TEXT_TO_START_CONVERSATION = {
    'restaurant': '近くの飲食店を検索',
    'cafe': '近くのカフェを検索'
}

CONVERSATION_RESET_TEXT = '会話をリセットする'

ERROR_TEXT = {
    'EXCEPTION_ERROR_MESSAGE': '予期せぬエラーが発生しました。リッチメニューから会話をリセットしてください。',
    'SELECT_FROM_RICH_MENU': 'リッチメニューから選択してください。',
    'SELECT_FROM_QUICK_REPLY': '選択肢の中から選んでください。',
    'NO_CONVERSATION_DATA': '会話記録がありません。',
}

MAX_STARS = 5
STAR_NAMES = {
    'FULL_STAR': 'star-solid.svg',
    'HARF_STAR': 'star-half-stroke-solid.svg',
    'EMPTY_STAR': 'star-regular.svg'
}


