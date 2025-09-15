TEST_PROMPT = ("""Проанализируй json. Выведи краткое содержание сообщений. Краткое содержание каждого сообщения должно 
                состоять максимум из 3 предложений. Если в сообщении есть конкретные цифры, то важные из них отрази в кратком содержании.
               Выведи список сообщений на русском языке в следующем формате:
               "сообщения": [
                    {
                        "дата и время": "2025-07-20 16:03:02+00:00",
                        "краткое содержание": "I like to answer and put them through hell. Which rule is that?"
                    },)
                    ...]""")

GENERAL_DIGEST_PROMPT = ("Сделай дайджест сообщений из каналов, сгруппировав их по тематикам. Общие новости обобщай, не дублируй."
                         "Во всех новостях обязательно указывай скрытые ссылки на сообщение из телеграм канала, используя текст-анкор. "
                         )
DIGEST_PROMPT = ("Сделай дайджест всех сообщений из канала. Отбирай не только свежие сообщения, но и более ранние, которые могут оказать занчительное влияние на рынок и относятся к теме криптовалют. "
                "Во всех новостях обязательно указывай скрытые ссылки на сообщение из телеграм канала, используя текст-анкор. "

                 )
ANALYSIS_PROMPT = ("Проанализируй содержание канала. " 
                  "Если канал не про крипту, сообщи, что этот канал не имеет отношение к тематике бота."
                   "Если в канал об крипто активе, расскажи о нем, выдели слабые и сильные стороны, дай прогноз на будущее."

                   )



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
    "@crypto_solyanka"
]