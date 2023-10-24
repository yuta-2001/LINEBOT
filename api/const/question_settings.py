# それぞれの質問内容を格納
QUESTION_SETTINGS = {
    "restaurant": {
        'order': [1, 2],
        'questions': {
            1: {
                'id': 1,
                'text': 'お好みのジャンルを選択してください',
                'property': 'keyword',
                'in_query': True,
                'options': [
                    '海鮮',
                    'ラーメン',
                    '定食',
                    '中華',
                    '韓国料理',
                    'インド料理',
                    'ベトナム料理'
                ],
                'error_message': '選択肢から選んでください'
            },
            2: {
                'id': 2,
                'text': '現在地からの距離(m)を選択してください',
                'property': 'radius',
                'in_query': True,
                'options': [
                    '500',
                    '1000',
                    '1500',
                    '2000',
                    '2500'
                ],
                'error_message': '選択肢から選んでください',
            },
        }
    }
}

TEXT_TO_START_CONVERSATION = {
    'restaurant': '近くの飲食店を検索する'
}
