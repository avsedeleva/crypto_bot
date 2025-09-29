import codecs
import re
# -*- coding: utf-8 -*-
a = ("<br>• BTC торгуется около $116 000, доминация — 58,24%. Альткоины показывают смешанную динамику. "
"<br>👉 <a href='https://t.me/cryptopizza_news/18733'>Обзор рынка</a>")
b = ("""<code>
📊 <b>Прогноз на основе анализа криптоновостей (16-17 сентября 2025)</b>

🔹 <b>Рыночные тенденции:</b>
• <i>Bitcoin</i> сохраняет стабильность в диапазоне $115–117k на фоне подготовки к решению ФРС. 
• <i>Altcoins</i> демонстрируют смешанную динамику: SOL (+15% за неделю благодаря институциональным покупкам), ETH (-2% коррекция), XMR волатилен из-за атак на сеть.
• Индекс альтсезона достиг 70–80, что указывает на потенциал роста альтов в среднесрочной перспективе.

🔹 <b>Ключевые события:</b>
• <b>17 сентября:</b> Заседание ФРС — ожидается снижение ставки на 0.25%. Это может усилить приток в рисковые активы (крипто, акции).
• <b>18 сентября:</b> Запуск XRP ETF ($XRPR) в США — позитивный сигнал для альткоинов.
• Активные покупки институционалов: Strategy ($60M в BTC), Galaxy Digital ($1.55 млрд в SOL), BitMine (2.15M ETH).

🔹 <b>Прогноз на 1-2 недели:</b>
• <b>BTC:</b> Коррекция до $112k возможна при негативе от ФРС, но рост к $120k вероятен при одобрении BITCOIN Act и продолжении инвестпритока.
• <b>ETH:</b> Цель — тест ATH ($4.8k+) на фоне новостей о стейкинге и ИИ-инициативах Ethereum Foundation.
• <b>SOL:</b> Дальнейший рост к $260–280 при поддержке корпоративных казначейств (Forward Industries, Pantera).
• <b>Риски:</b> Волатильность из-за разблокировок токенов ($353M на неделе), атаки на сети (Monero, YU stablecoin).

🔹 <b>Рекомендации:</b>
• <b>Краткосрочно:</b> Фиксировать прибыль в альтах перед FOMC. Мониторить BTC на пробой $117k.
• <b>Среднесрочно:</b> Накопление ETH, SOL и качественных альтов (децентрализованные инфраструктурные проекты).
• <b>Стоп-лоссы:</b> Для BTC — $112k, для ETH — $4.3k.

📌 <b>Итог:</b> Общий тренд бычий, но краткосрочная коррекция возможна. Фокус на события ФРС и институциональные потоки.
</code>""")

c = ('<!DOCTYPE html>\n<html>\n<body>\n\n<h1>📊 Криптодайджест за 22-24 сентября 2025 года</h1>\n\n' 
    '<h2>🏦 Крупные корпоративные покупки криптовалют</h2>\n<ul>\n<li><strong>Strategy (ex-MicroStrategy)</strong> ' 
    'приобрела 850 BTC на $99.7 млн по средней цене $117,344 за биткоин. Теперь компания владеет 639,835 BTC на сумму '
     'около $47.33 млрд <a href="https://t.me/cointelegraph/64105">(источник)</a></li>\n<li><strong>Metaplanet</strong> '
     'купила 5,419 BTC на $632.5 млн, увеличив общий резерв до 25,555 BTC <a href="https://t.me/cointelegraph/64073">'
     '(источник)</a></li>\n<li><strong>BitMine</strong> накопила более 2.4 млн ETH (свыше 2% от общего предложения), а '
     'общая стоимость активов компании достигла $11.4 млрд <a href="https://t.me/RBCCrypto/20417">(источник)</a></li>\n'
     '<li><strong>ETHZilla</strong> привлекла $350 млн через конвертируемые облигации для дальнейших покупок Ethereum '
     '<a href="https://t.me/cointelegraph/64109">(источник)</a></li>\n</ul>\n\n<h2>💼 Регуляторные новости и '
     'институциональное внедрение</h2>\n<ul>\n<li><strong>SEC</strong> планирует ввести "innovation exemption" до '
     'конца года, упрощающий запуск криптопродуктов <a href="https://t.me/RBCCrypto/20431">(источник)</a></li>\n'
     '<li><strong>CFTC</strong> разрешит использование стейблкоинов в качестве токенизированного обеспечения для деривативов '
     '<a href="https://t.me/DeCenter/22059">(источник)</a></li>\n<li><strong>Morgan Stanley</strong> запустит торговлю '
     'BTC, ETH и SOL на платформе E*Trade в первой половине 2026 года <a href="https://t.me/RBCCrypto/20433">(источник)'
     '</a></li>\n<li><strong>США и Великобритания</strong> создали совместную рабочую группу для гармонизации '
     'регулирования цифровых активов <a href="https://t.me/RBCCrypto/20423">(источник)</a></li>\n</ul>\n\n<h2>🌎 '
     'Международные проекты и CBDC</h2>\n<ul>\n<li><strong>Казахстан</strong> запустил пилотный проект национального '
     'стейблкоина KZTE на базе Solana в партнерстве с Mastercard <a href="https://t.me/RBCCrypto/20430">(источник)</a>'
     '</li>\n<li><strong>ЕС</strong> согласовал дорожную карту по цифровому евро, но запуск может занять до 2029 года '
     '<a href="https://t.me/RBCCrypto/20410">(источник)</a></li>\n<li><strong>Китай</strong> рекомендовал приостановить '
     'RWA-токенизацию в Гонконге <a href="https://t.me/RBCCrypto/20415">(источник)</a></li>\n<li><strong>ОАЭ</strong> '
     'присоединились к международному соглашению об автоматическом обмене налоговой информацией по криптоактивам '
     '<a href="https://t.me/RBCCrypto/20414">(источник)</a></li>\n</ul>\n\n<h2>💸 Ключевые проекты и финансирование</h2>'
     '\n<ul>\n<li><strong>Tether</strong> ведет переговоры о привлечении $15-20 млрд при оценке в $500 млрд '
     '<a href="https://t.me/RBCCrypto/20438">(источник)</a></li>\n<li><strong>Plasma</strong> анонсировала запуск '
     'глобального необанка Plasma One с поддержкой стейблкоинов <a href="https://t.me/Defiscamcheck/4555">(источник)'
     '</a></li>\n<li><strong>Ripple</strong> интегрировала стейблкоин RLUSD в токенизированные фонды BlackRock и '
     'VanEck <a href="https://t.me/DeCenter/22068">(источник)</a></li>\n<li><strong>Nvidia</strong> инвестирует до '
     '$100 млрд в OpenAI для развертывания дата-центров <a href="https://t.me/DeCenter/22038">(источник)</a></li>\n'
     '</ul>\n\n<h2>⚡️ Технические обновления и безопасность</h2>\n<ul>\n<li><strong>BNB Chain</strong> предлагает '
     'снизить комиссии на 50% и ускорить генерацию блоков <a href="https://t.me/cointelegraph/64142">(источник)</a></li>'
     '\n<li><strong>Виталик Бутерин</strong> защитил безопасность L2-решений, выделив Base как пример правильной '
     'реализации <a href="https://t.me/RBCCrypto/20426">(источник)</a></li>\n<li><strong>Взлом UXLINK</strong> на $45 '
     'млн обернулся для хакера потерей $48 млн из-за фишинга <a href="https://t.me/DeCenter/22045">(источник)</a></li>'
     '\n</ul>\n\n<h2>📈 Аналитика рынка</h2>\n<ul>\n<li>За 24 сентября <strong>ликвидации составили $1.7 млрд</strong>, '
     'преимущественно по лонг-позициям <a href="https://t.me/crypto_sekta/3803">(источник)</a></li>\n<li><strong>Биткоин '
     'тестирует ключевой уровень поддержки $112,000</strong>, потеря которого может открыть дорогу к $95,000-100,000 '
     '<a href="https://t.me/crypto_sekta/3804">(источник)</a></li>\n<li><strong>Индекс альтсезона опустился ниже 75</strong>, что указывает на доминирование биткоина <a href="https://t.me/RBCCrypto/20411">(источник)</a></li>\n<li>Число <strong>криптомиллионеров выросло на 40%</strong> до 241,700 человек за год <a href="https://t.me/RBCCrypto/20432">(источник)</a></li>\n</ul>\n\n<h2>🎯 Прогнозы и значимые заявления</h2>\n<ul>\n<li><strong>Брайан Армстронг (Coinbase)</strong>: "Биткоин может достичь $1 млн к 2030 году" <a href="https://t.me/cointelegraph/64133">(источник)</a></li>\n<li><strong>Энтони Скарамуччи</strong> сохраняет целевой уровень BTC в $150,000 на 2025 год <a href="https://t.me/Coins/4177">(источник)</a></li>\n<li><strong>Джейми Даймон (JPMorgan)</strong> подтвердил разработку банковских стейблкоинов <a href="https://t.me/DeCenter/22063">(источник)</a></li>\n</ul>\n\n</body>\n</html>'
     )
'''def simple_html_to_text(html):
    # Заменяем HTML теги на Markdown форматирование
    replacements = [
        (r'<h1>(.*?)</h1>', r'# \1\n\n'),
        (r'<h2>(.*?)</h2>', r'## \1\n\n'),
        (r'<h3>(.*?)</h3>', r'### \1\n\n'),
        (r'<b>(.*?)</b>', r'**\1**'),
        (r'<strong>(.*?)</strong>', r'**\1**'),
        (r'<i>(.*?)</i>', r'*\1*'),
        (r'<em>(.*?)</em>', r'*\1*'),
        (r'<code>(.*?)</code>', r'\1'),
        (r'<pre>(.*?)</pre>', r'```\n\1\n```'),
        (r'<a\s+href=[\'"](.*?)[\'"]>(.*?)</a>', r'[\2](\1)'),
        (r'<ul>(.*?)</ul>', r'\1'),
        (r'<li>(.*?)</li>', r'• \1\n'),
        (r'<p>(.*?)</p>', r'\1\n\n'),
        (r'<br\s*/?>', r'\n'),
        (r'\n\n+', r'\n\n'),  # Убираем лишние переносы
        (r'<[^>]+>', r''),  # Удаляем все остальные теги
    ]

    text = html
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.DOTALL)

    # Очищаем множественные переносы строк
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)  # Не больше двух переносов подряд

    return text.strip()'''

def simple_html_to_text(html):
    # Заменяем HTML теги на Telegram форматирование
    replacements = [
        (r'<h1>(.*?)</h1>', r'*\1*\n\n'),
        #(r'_', r'/_'),
        (r'<h2>(.*?)</h2>', r'*\1*\n\n'),
        (r'<h3>(.*?)</h3>', r'*\1*\n\n'),
        (r'<b>(.*?)</b>', r'*\1*'),
        (r'<strong>(.*?)</strong>', r'*\1*'),
        (r'<i>(.*?)</i>', r'_\1_'),
        (r'<em>(.*?)</em>', r'_\1_'),
        (r'<code>(.*?)</code>', r'\1'),
        (r'<pre>(.*?)</pre>', r'```\1```'),
        (r'<a\s+href=[\'"](.*?)[\'"]>(.*?)</a>', r'[\2](\1)'),
        (r'<ul>(.*?)</ul>', r'\1'),
        (r'<li>(.*?)</li>', r'• \1\n'),
        (r'<p>(.*?)</p>', r'\1\n\n'),
        (r'<br\s*/?>', r'\n'),
        (r'###', r''),
        (r'<[^>]+>', r''),  # Удаляем все остальные теги
    ]

    text = html
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.DOTALL)

    # Очищаем множественные переносы строк
    text = re.sub(r'\n\s*\n', '\n\n', text)
    #text = re.sub(r'\n{3,}', '\n\n', text)  # Не больше двух переносов подряд

    return text.strip()

#print(simple_html_to_text(c))
def correct_text_decoding(text):
    """Правильное декодирование текста с UTF-8 байтами"""


    final_text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)

    return final_text


def clean_text_completely(text):
    """
    Полная очистка текста - УДАЛЯЕТ все мешающие символы
    """
    # 1. Удаляем эмодзи (\ud83c\uddf7\ud83c\uddfa)
    text = re.sub(r'\\ud[83cdef][0-9a-fA-F]{3}', '', text)

    # 2. Удаляем ** и другое форматирование
    text = re.sub(r'[*_~`]+', ' ', text)

    # 3. Заменяем кириллические Unicode символы
    def decode_cyrillic(match):
        hex_code = match.group(1)
        try:
            # Диапазон кириллических символов
            code_point = int(hex_code, 16)
            if 0x0400 <= code_point <= 0x04FF:
                return chr(code_point)
            else:
                return ''  # Удаляем не-кириллические
        except:
            return ''

    text = re.sub(r'\\u([0-9a-fA-F]{4})', decode_cyrillic, text)

    # 4. Удаляем оставшиеся специальные символы
    text = re.sub(r'[^\w\s\.,!?;:()\-]', ' ', text)

    # 5. Нормализуем пробелы
    text = re.sub(r'\s+', ' ', text).strip()

    return text
abc =  "\u00e2\u009a\u00a1\u00ef\u00b8\u008f LATEST: Binance launched a \u00e2\u0080\u009ccrypto-as-a-service\u00e2\u0080\u009d solution for banks, brokerages, and exchanges, with first adopters starting Sept 30.\n\nRead more: [ct.com\n](https://cointelegraph.com/)\n[News |](https://cointelegraph.com/) [Markets |](https://cointelegraph.com/markets) [YouTube](https://youtube.com/@cointelegraph?si=4ge6Mqs-_0fvJCM2)"
print(clean_text_completely(abc))