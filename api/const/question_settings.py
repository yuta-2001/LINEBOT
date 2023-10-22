# それぞれの質問内容を格納
QUESTION_SETTINGS = {
    "restaurant": {
        'order': [1, 2],
        'questions': {
            1: {
                'id': 1,
                'text': 'お好みのジャンルを選択してください',
                'property': 'keyword',
                'options': {
                    '海鮮': 1,
                    'ラーメン': 2,
                    'うどん・そば': 3,
                    '定食': 4,
                    '中華': 5,
                    '韓国料理': 6,
                    'こだわりなし': 7,
                },
                'error_message': '選択肢から選んでください'
            },
            2: {
                'id': 2,
                'text': '現在地からの距離を入力してください',
                'property': 'radius',
                'options': {
                    '徒歩5分圏内': 400,
                    '徒歩10分圏内': 800,
                    '徒歩15分圏内': 1200,
                    '徒歩20分圏内': 1600,
                },
                'error_message': '選択肢から選んでください',
            },
        }
    }
}

TEXT_TO_START_CONVERSATION = {
    'restaurant': '近くの飲食店を検索する'
}
