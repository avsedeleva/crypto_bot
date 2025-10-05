import re


async def simple_html_to_text(html):
    # Заменяем HTML теги на Telegram форматирование
    replacements = [
        #(r'<h1>(.*?)</h1>', r'*\1*\n\n'),
        (r'\*\*(.*?)\*\*', r'<b>\1</b>'),
        (r'\*(.*?)\*', r'<u>\1</u>'),
        #(r'_', r'/_'),
        #(r'<h2>(.*?)</h2>', r'*\1*\n\n'),
        #(r'<h3>(.*?)</h3>', r'*\1*\n\n'),
        #(r'<b>(.*?)</b>', r'*\1*'),
        #(r'<strong>(.*?)</strong>', r'*\1*'),
        #(r'<i>(.*?)</i>', r'_\1_'),
        #(r'<em>(.*?)</em>', r'_\1_'),
        #(r'<code>(.*?)</code>', r'\1'),
        #(r'<pre>(.*?)</pre>', r'```\1```'),
        #(r'<a\s+href=[\'"](.*?)[\'"]>(.*?)</a>', r'[\2](\1)'),
        #(r'<ul>(.*?)</ul>', r'\1'),
        #(r'<li>(.*?)</li>', r'• \1\n'),
        #(r'<p>(.*?)</p>', r'\1\n\n'),
        #(r'<br\s*/?>', r'\n'),
        (r'####', r''),
        (r'###', r''),
        (r'##', r''),
        #(r'<[^>]+>', r''),  # Удаляем все остальные теги
    ]

    text = html
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.DOTALL)

    # Очищаем множественные переносы строк
    #text = re.sub(r'\n\s*\n', '\n\n', text)
    #text = re.sub(r'\n{3,}', '\n\n', text)  # Не больше двух переносов подряд

    return text.strip()


async def split_by_paragraphs_answer(text: str, max_length=3800) -> list[str]:
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 > max_length:  # +2 для '\n\n'
            chunks.append(current_chunk.strip())
            current_chunk = paragraph
        else:
            current_chunk += f"\n\n{paragraph}" if current_chunk else paragraph

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

async def split_by_paragraphs_answer_img(text: str, max_length=980) -> list[str]:
    paragraphs = text.split('\n')
    chunks = []
    current_chunk = ""


    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 > max_length:  # +2 для '\n\n'
            chunks.append(current_chunk.strip())
            max_length = 3800
            current_chunk = paragraph
        else:
            current_chunk += f"\n{paragraph}" if current_chunk else paragraph

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks