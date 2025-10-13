TEST_PROMPT = ("""Проанализируй json. Выведи краткое содержание сообщений. Краткое содержание каждого сообщения должно 
                состоять максимум из 3 предложений. Если в сообщении есть конкретные цифры, то важные из них отрази в кратком содержании.
               Выведи список сообщений на русском языке в следующем формате:
               "сообщения": [
                    {
                        "дата и время": "2025-07-20 16:03:02+00:00",
                        "краткое содержание": "I like to answer and put them through hell. Which rule is that?"
                    },)
                    ...]""")

TEXT = (
    """
    Проанализируй содержание канала. 
        Если канал не про крипту, сообщи, что этот канал не имеет отношение к тематике бота. 
        Если в канал об крипто активе, расскажи о нем, выдели слабые и сильные стороны, дай прогноз на будущее.
    """
)

PROMPTS = {
    "general_digest":
        """
        Сделай дайджест сообщений из каналов, сгруппировав их по тематикам. Общие новости обобщай, не дублируй.
        Во всех новостях обязательно указывай скрытые ссылки на сообщение из телеграм канала, используя текст-анкор.
        """
    ,
    "general_forecast":
        """
        По данным новостей сделай прогноз на ближайшее будущее, касающийся тематики криптовалют. 
        Во что инвестировать, что продавать, на какой проект обратить внимание. 
        Оценивая влияние новостей, учитывай их хронологию. 
        Если возможно, указывай скрытые ссылки на сообщение из телеграм каналов, используя текст-анкор.
        """
    ,
    "digest":
        """
        Сделай дайджест всех сообщений из канала. Отбирай не только свежие сообщения, но и более ранние, которые могут 
        оказать значительное влияние на рынок финансовых активов, например, криптовалют, общество или технологии. 
        Расположи их от свежих к старым. 
        Во всех новостях обязательно указывай скрытые ссылки на сообщение из телеграм канала, используя текст-анкор.
        """
    ,
    "analysis":
        """
        Проанализируй сообщения и создай развернутый анализ. Для ключевых моментов
        указывай скрытые ссылки на сообщение с текстом-анкором.
        Расскажи о слабых и сильных сторонах канала. Если канал о продукте, сервисе или активе, расскажи о нем и дай прогноз на будущее.
        """
    ,
    "trending_tokens": """
        Какие новые токены и свежие проекты сейчас на хайпе. Отдельно обрати внимание на крипто Gems, молодые и 
        рискованные проекты с потенциалом вырасти во много раз. А так же расскажи о новых восходящих криптотрендах.
        Где возможно указывай скрытые ссылки на сообщение из телеграм канала, используй ссылки с текстом-анкором.
        """,
    "addition": (
        "Для форматирования текста твоего ответа используй только следующие HTML-теги: <b>, <i>, <a>, <u>,  •, <code>."
        #"Для форматирования текста твоего ответа используй Markdown, адаптированный под Telegram."
        "В тексте ответа можешь использовать эмоджи, где это уместно, но не перегружай текст."
        "Результат должен быть на {language} языке."
    )
}

MESSAGES = {
    "select_lang": "🌍Выбери язык/Choose a language",
    'select_img': "Нужна картинка (для админов)?",
    "lang": {
        "kbd": {
            "ru" : "RU",
            "en": "EN"
        },

    },
    "start": {
        "ru":
            (
            "🖐️Привет! Я ИИ-бот. Помогу тебе с анализом <b>Telegram-каналов</b>.\n"
            "Вот что я умею: \n"
            "📌 <b>Трендовые токены</b> – соберу информацию о быстрорастущих и обсуждаемых токенах.\n"
            "📌 <b>Дайджест криптоновостей</b> – соберу самое важное по тематике криптовалют за день.\n"
            "📌 <b>Прогноз рынка криптовалют</b> – дам прогноз рынка на основе новостей.\n"
            "📌 <b>Дайджест выбранного канала</b> – соберу самое важное по указанному каналу за выбранный период.\n"
            "📌 <b>Анализ канала</b> – проведу анализ указанного канала за выбранный период\n"
            "🔎 Хочешь попробовать?\n"
            "🖊️ Выбери опцию:"
            )
        ,
        "en":
            (
            "🖐️ Hi! I'm an AI bot. I'll help you analyze <b>Telegram channels</b>.\n"
            "Here's what I can do: \n"
            "📌 <b>Trending Tokens</b> – I'll gather information about hot tokens & fresh projects gaining momentum.\n"
            "📌 <b>Crypto News Digest</b> – I'll gather the most important cryptocurrency news of the day.\n"
            "📌 <b>Crypto Market Forecast</b> – I'll give a market prediction based on the news.\n"
            "📌 <b>Digest for a Selected Channel</b> – I'll gather the most important content from a channel "
            "for a selected period.\n"
            "📌 <b>Channel Analysis</b> – I'll analyze a channel for a selected period.\n"
            "🔎 Want to give it a try?\n"
            "🖊️ Choose an option:"
            )
    },
    "menu": {
        "ru": "🖊️ Выбери опцию:",
        "en": "🖊️ Choose an option:"
    },
    "kbd": {
        "general_digest": {
            "ru": "Дайджест криптоновостей",
            "en": "Crypto News Digest"
        },
        "general_forecast": {
            "ru": "Прогноз рынка криптовалют",
            "en": "Crypto Market Forecast"
        },
        "trending_tokens": {
            "ru": "Трендовые токены",
            "en": "Trending Tokens"
        },
        "general_other": {
            "ru": "Свой промпт по криптоновостям",
            "en": "Custom Crypto News Prompt"
        },
        "digest": {
            "ru": "Дайджест канала",
            "en": "Channel Digest"
        },
        "analysis": {
            "ru": "Анализ канала",
            "en": "Channel Analysis"
        },
        "other": {
            "ru": "Свой промпт по каналу",
            "en": "Custom Channel Prompt"
        },
        "twitter": {
            "ru": "Свой промпт по twitter",
            "en": "Custom Twitter Prompt"
        },
        "input_field":{
            "ru": "Выберите опцию...",
            "en": "Choose an option..."
        },
    },

    "new_command": {
        "ru": "Нажми /start, чтоб задать новый запрос.",
        "en": "Click /start to begin a new search."
    },
    "channel": {
        "select": {
            "ru": "🖊️ Введи username или ссылку канала({example})",
            "en": "🖊️ Enter channel username or link ({example})",
        },
        "error": {
            "ru": "❕ Пожалуйста, введи username или ссылку канала корректно",
            "en": "❕ Please enter a valid channel username or link",
        },
        "example": {
            "ru": "например: @durov, https://t.me/...",
            "en": "e.g., @durov, https://t.me/...",
        },
        "error_channel": {
            "ru": "❌Ошибка: username или ссылка канала указаны неверно",
            "en": "❌Error: invalid channel username or link",
        }

    },
    "limit": {
        "select": {
            "ru": "🗓️ За какой период нужно скачать посты (в днях). Максимум {max_limit} дней",
            "en": "🗓️ Enter the period for downloading posts (in days). Maximum: {max_limit} days",
        },
        "error": {
            "ru": "⚠️Пожалуйста, введи число от 1 до {max_limit}!",
            "en": "⚠️Please enter a number from 1 to {max_limit}!",
        },
    },
    "custom_prompt": {
        "ru": "🖊️Напиши ниже свой промпт:",
        "en": "🖊️ Write your prompt:"
    },
    "loading": {
        "download":{
            "ru": "🕔 Начинаю скачивать посты...",
            "en": "🕔 Downloading posts..."
        },
        "answer": {
            "ru": "🔄 Формирую ответ...",
            "en": "🔄 Generating response..."
        }
    },
    "attention": {
        "no_post": {
            "ru": (
                "⚠Сообщения за выбранный период отсутствуют.\n"
                "Выбери другой период или задай другой запрос, нажав /start"
            ),
            "en": (
                "⚠️No messages found for this period.\n"
                "Try different days or use /start"
            )
        },
        "period": {
            "ru": (
                "🤖 *Внимание!*\n"
                "В связи с большим объемом информации, смог обработать только последние {days} дней.\n"
                "🛠️_Работаю над расширением возможностей!_"
                ),
            "en": (
                "🤖 Attention!\n"
                "Due to the large volume of information, I was only able to process the last {days} days.\n"
                "🛠️_Working on expanding capabilities!_"
                )
        }
    },
    "error": {
        "ru": "❌ Произошла ошибка при обработке запроса. Попробуйте снова.",
        "en": "❌ An error occurred while processing your request. Please try again"
    },
    "title": {
        "ru": "<b><code>@GenAI_crypto_bot</code></b>\n────────────\n",
        "en": "<b><code>@GenAI_crypto_bot</code></b>\n────────────\n"
    }
}




"""CHANNEL_LIST = [
    "https://t.me/cointelegraph",
    "https://t.me/RBCCrypto",
    "https://t.me/Defiscamcheck",
    "https://t.me/DeCenter",
    "https://t.me/cryptodaily",
    "https://t.me/Coin_Post",
    "https://t.me/cryptopizza_news",
    "https://t.me/blockchaingerman",
    "https://t.me/Coins",
    "https://t.me/bfxannouncements",
    "https://t.me/crypto_sekta",
    "https://t.me/crypto_solyanka"
]"""
CHANNEL_LIST = [
        "@cointelegraph",
        "@RBCCrypto",
        "@Defiscamcheck",
        "@DeCenter",
        "@cryptodaily",
        "@Coin_Post",
        "@cryptopizza_news",
        "@blockchaingerman",
        "@Coins",
        "@bfxannouncements",
        "@crypto_sekta",
        "@crypto_solyanka",
        "@blockchainwhispersbaby",
        "@binance_announcements",
        "@CoinMarketCapAnnouncements",
        "@coinmarket",
        "@money"
        ]
'''"ru": [
        "@cointelegraph",
        "@RBCCrypto",
        "@Defiscamcheck",
        "@DeCenter",
        "@cryptodaily",
        "@Coin_Post",
        "@cryptopizza_news",
        "@blockchaingerman",
        "@Coins",
        "@bfxannouncements",
        "@crypto_sekta",
        "@crypto_solyanka"
    ],
    "en": [
        "@blockchainwhispersbaby",
        "@cointelegraph",
        "@binance_announcements",
        "@CoinMarketCapAnnouncements",
        "@coinmarket",
        "@money"
        ]'''

proxy = "http://L0WXPq:R9BYy0@196.19.122.145:8000"