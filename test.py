import re

a = ("<br>• BTC торгуется около $116 000, доминация — 58,24%. Альткоины показывают смешанную динамику. "
"<br>👉 <a href='https://t.me/cryptopizza_news/18733'>Обзор рынка</a>")

def simple_html_to_text(html):
    # Заменяем HTML теги на Markdown форматирование
    replacements = [
        (r'<h1>(.*?)</h1>', r'# \1\n\n'),
        (r'<h2>(.*?)</h2>', r'## \1\n\n'),
        (r'<h3>(.*?)</h3>', r'### \1\n\n'),
        (r'<b>(.*?)</b>', r'**\1**'),
        (r'<strong>(.*?)</strong>', r'**\1**'),
        (r'<i>(.*?)</i>', r'*\1*'),
        (r'<em>(.*?)</em>', r'*\1*'),
        (r'<code>(.*?)</code>', r'`\1`'),
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

    return text.strip()

print(simple_html_to_text(a))