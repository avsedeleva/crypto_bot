
import re


def clean_message_keep_links(text):
    """
    Очищает сообщение от специальных символов, сохраняя ссылки
    """
    # 1. Сначала извлекаем все ссылки
    links = re.findall(r'https?://[^\s\)]+', text)

    # 2. Удаляем эмодзи и surrogate pairs (\ud83c\uddf7\ud83c\uddfa)
    text = re.sub(r'\\ud[83cdef][0-9a-fA-F]{3}', '', text)

    # 3. Удаляем ** и другие символы форматирования
    text = re.sub(r'[*_~`]+', ' ', text)

    # 4. Декодируем Unicode escape последовательности (\u0410 и т.д.)
    def decode_unicode(match):
        try:
            return chr(int(match.group(1), 16))
        except:
            return ''

    text = re.sub(r'\\u([0-9a-fA-F]{4})', decode_unicode, text)

    # 5. Удаляем квадратные скобки но сохраняем текст внутри них
    text = re.sub(r'\[(.*?)\]', r'\1', text)

    # 6. Удаляем лишние пробелы и переносы строк
    text = re.sub(r'\s+', ' ', text)

    # 7. Удаляем оставшиеся специальные символы (оставляем только буквы, цифры, пробелы, пунктуацию и ссылки)
    # Сохраняем ссылки отдельно
    text_clean = re.sub(r'https?://[^\s\)]+', ' [ССЫЛКА] ', text)
    text_clean = re.sub(r'[^\w\s\.,!?;:()\-]', '', text_clean)
    text_clean = re.sub(r'\s+', ' ', text_clean).strip()

    return text_clean, links


def clean_message_with_links(text):
    """
    Очищает сообщение и возвращает текст со ссылками в конце
    """
    cleaned_text, links = clean_message_keep_links(text)

    result = cleaned_text
    if links:
        result += "\n\nСсылки из сообщения:\n" + "\n".join(f"- {link}" for link in links)

    return result


def clean_message_preserve_links(text):
    """
    Очищает сообщение, сохраняя ссылки на месте
    """
    # 1. Удаляем эмодзи и surrogate pairs
    text = re.sub(r'\\ud[83cdef][0-9a-fA-F]{3}', '', text)

    # 2. Удаляем ** и другие символы форматирования
    text = re.sub(r'[*_~`]+', ' ', text)

    # 3. Декодируем Unicode escape последовательности
    def decode_unicode(match):
        try:
            return chr(int(match.group(1), 16))
        except:
            return ''

    text = re.sub(r'\\u([0-9a-fA-F]{4})', decode_unicode, text)

    # 4. Удаляем квадратные скобки но сохраняем текст внутри них
    text = re.sub(r'\[(.*?)\]', r'\1', text)

    # 5. Удаляем лишние пробелы и переносы строк
    text = re.sub(r'\s+', ' ', text)

    # 6. Удаляем оставшиеся специальные символы, но сохраняем ссылки
    # Заменяем ссылки на временные маркеры
    link_markers = []

    def replace_link(match):
        link_markers.append(match.group(0))
        return f" [ССЫЛКА_{len(link_markers)}] "

    text_with_markers = re.sub(r'https?://[^\s\)]+', replace_link, text)

    # Очищаем текст от других специальных символов
    text_clean = re.sub(r'[^\w\s\.,!?;:()\-]', '', text_with_markers)
    text_clean = re.sub(r'\s+', ' ', text_clean).strip()

    # Восстанавливаем ссылки на место
    for i, link in enumerate(link_markers, 1):
        text_clean = text_clean.replace(f"[ССЫЛКА_{i}]", link)

    return text_clean


# Ваше сообщение
message = r"""\ud83c\uddf7\ud83c\uddfa **\u0427\u0442\u043e \u0434\u0435\u043b\u0430\u0442\u044c \u043f\u0440\u0438 \u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u043a\u0435 \u043a\u0430\u0440\u0442\u044b \u043f\u043e\u0441\u043b\u0435 \u043e\u0431\u043c\u0435\u043d\u0430 \u043a\u0440\u0438\u043f\u0442\u043e\u0432\u0430\u043b\u044e\u0442\u044b**\n\n\u0411\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u043a\u0438 \u0431\u0430\u043d\u043a\u043e\u0432\u0441\u043a\u0438\u0445 \u043a\u0430\u0440\u0442 \u043f\u043e\u0441\u043b\u0435 \u043e\u043f\u0435\u0440\u0430\u0446\u0438\u0439 \u0441 \u043a\u0440\u0438\u043f\u0442\u043e\u0432\u0430\u043b\u044e\u0442\u043e\u0439 \u0441\u0442\u0430\u043b\u0438 \u043c\u0430\u0441\u0441\u043e\u0432\u044b\u043c \u044f\u0432\u043b\u0435\u043d\u0438\u0435\u043c. \u0412 \u0446\u0435\u043b\u044f\u0445 \u0431\u043e\u0440\u044c\u0431\u044b \u0441 \u043e\u0442\u043c\u044b\u0432\u0430\u043d\u0438\u0435\u043c \u0441\u0440\u0435\u0434\u0441\u0442\u0432 \u0438 \u043c\u043e\u0448\u0435\u043d\u043d\u0438\u0447\u0435\u0441\u0442\u0432\u043e\u043c \u043c\u043e\u0433\u0443\u0442 \u0431\u044b\u0442\u044c \u0437\u0430\u043c\u043e\u0440\u043e\u0436\u0435\u043d\u044b \u0441\u0440\u0435\u0434\u0442\u0441\u0442\u0432\u0430 \u043a\u0430\u043a \u043f\u0440\u0435\u0441\u0442\u0443\u043f\u043d\u043e\u0433\u043e \u043f\u0440\u043e\u0438\u0441\u0445\u043e\u0436\u0434\u0435\u043d\u0438\u044f, \u0442\u0430\u043a \u0438 \u043f\u0440\u0438\u043d\u0430\u0434\u043b\u0435\u0436\u0430\u0449\u0438\u0435 \u0434\u043e\u0431\u0440\u043e\u0441\u043e\u0432\u0435\u0441\u0442\u043d\u044b\u043c \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f\u043c.\n\n\u041e\u0441\u043d\u043e\u0432\u0430\u043d\u0438\u044f \u0434\u043b\u044f \u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u043a\u0438 \u0447\u0430\u0449\u0435 \u0441\u0432\u044f\u0437\u0430\u043d\u044b \u043d\u0435 \u0441 \u043a\u0440\u0438\u043f\u0442\u043e\u0432\u0430\u043b\u044e\u0442\u043e\u0439 \u043a\u0430\u043a \u0442\u0430\u043a\u043e\u0432\u043e\u0439, \u0430 \u0441 \u043d\u0435\u0442\u0438\u043f\u0438\u0447\u043d\u043e\u0439 \u0444\u0438\u043d\u0430\u043d\u0441\u043e\u0432\u043e\u0439 \u0430\u043a\u0442\u0438\u0432\u043d\u043e\u0441\u0442\u044c\u044e, \u043d\u0435\u043f\u0440\u043e\u0437\u0440\u0430\u0447\u043d\u044b\u043c\u0438 \u0438\u0441\u0442\u043e\u0447\u043d\u0438\u043a\u0430\u043c\u0438 \u0441\u0440\u0435\u0434\u0441\u0442\u0432 \u0438\u043b\u0438 \u0443\u0447\u0430\u0441\u0442\u0438\u0435\u043c \u0432 \u043f\u043e\u0434\u043e\u0437\u0440\u0438\u0442\u0435\u043b\u044c\u043d\u044b\u0445 \u0446\u0435\u043f\u043e\u0447\u043a\u0430\u0445 \u043f\u0435\u0440\u0435\u0432\u043e\u0434\u043e\u0432, [\u043e\u0442\u043c\u0435\u0447\u0430\u044e\u0442](https://www.rbc.ru/crypto/news/68da88979a794752da917657?utm_source=telegram&utm_medium=post&utm_campaign=crypto) \u043e\u043f\u0440\u043e\u0448\u0435\u043d\u043d\u044b\u0435 \u0420\u0411\u041a \u041a\u0440\u0438\u043f\u0442\u043e \u044d\u043a\u0441\u043f\u0435\u0440\u0442\u044b.\n\n\u041f\u043e\u0447\u0435\u043c\u0443 \u0431\u0430\u043d\u043a\u0438 \u043c\u043e\u0433\u0443\u0442 \u0437\u0430\u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u0430\u0442\u044c \u0441\u0440\u0435\u0434\u0441\u0442\u0432\u0430, \u0438 \u043f\u043e\u0447\u0435\u043c\u0443 \u043e\u0431\u044b\u0447\u043d\u044b\u0435 \u043d\u0430 \u043f\u0435\u0440\u0432\u044b\u0439 \u0432\u0437\u0433\u043b\u044f\u0434 \u043f\u0435\u0440\u0435\u0432\u043e\u0434\u044b \u0432\u044b\u0437\u044b\u0432\u0430\u044e\u0442 \u043f\u043e\u0434\u043e\u0437\u0440\u0435\u043d\u0438\u044f, \u043a\u0430\u043a\u043e\u0432 \u043f\u043e\u0440\u044f\u0434\u043e\u043a \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0439 \u0432 \u0441\u043b\u0443\u0447\u0430\u0435 \u0431\u043b\u043e\u043a\u0438\u0440\u043e\u0432\u043a\u0438, \u043a\u0430\u043a\u043e\u0439 \u0437\u0430\u043f\u0440\u043e\u0441 \u0441\u0434\u0435\u043b\u0430\u0442\u044c \u0432 \u0431\u0430\u043d\u043a, \u043a\u0430\u043a\u0438\u0435 \u0434\u043e\u043a\u0443\u043c\u0435\u043d\u0442\u044b \u043f\u043e\u0434\u0433\u043e\u0442\u043e\u0432\u0438\u0442\u044c \u0438 \u0432 \u043a\u0430\u043a\u043e\u043c \u043f\u043e\u0440\u044f\u0434\u043a\u0435 \u043f\u043e\u0434\u0430\u0432\u0430\u0442\u044c \u043f\u0440\u0435\u0442\u0435\u043d\u0437\u0438\u0438 \u2014 \u0432 [**\u043c\u0430\u0442\u0435\u0440\u0438\u0430\u043b\u0435**](https://www.rbc.ru/crypto/news/68da88979a794752da917657?utm_source=telegram&utm_medium=post&utm_campaign=crypto) \u0420\u0411\u041a \u041a\u0440\u0438\u043f\u0442\u043e.\n\n[\u041f\u0440\u0438\u0441\u043e\u0435\u0434\u0438\u043d\u044f\u0439\u0442\u0435\u0441\u044c \u043a \u0444\u043e\u0440\u0443\u043c\u0443 \u0420\u0411\u041a \u041a\u0440\u0438\u043f\u0442\u043e](https://t.me/+UxXrhnVYWZ0yODUy) | [\u041f\u043e\u0434\u043f\u0438\u0441\u0430\u0442\u044c\u0441\u044f \u043d\u0430 \u043a\u0430\u043d\u0430\u043b](https://t.me/+1hFFPSrmzfE2NDMy)"""

print("=== СПОСОБ 1: Текст со ссылками в конце ===")
result1 = clean_message_with_links(message)
print(result1)

print("\n" + "=" * 50 + "\n")

print("=== СПОСОБ 2: Текст с ссылками на месте ===")
result2 = clean_message_preserve_links(message)
print(result2)

print("\n" + "=" * 50 + "\n")

print("=== СПОСОБ 3: Только очищенный текст и отдельно ссылки ===")
cleaned_text, links = clean_message_keep_links(message)
print("Очищенный текст:")
print(cleaned_text)
print("\nСсылки:")
for link in links:
    print(f"- {link}")

    "Используй разметку Markdown, оптимизированном для Telegram"
    "Критически важно: не поддерживаются:"
    "Заголовки # H1, ## H2,"
"Ненумерованные списки -, +,"
"Нумерованные списки 1. 2.,"
"Цитаты >,"
"Таблицы,"
"HTML теги"