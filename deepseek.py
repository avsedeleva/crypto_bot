import asyncio
import datetime
import json

import aiohttp
from openai import OpenAI


client = OpenAI(
    api_key="sk-c9fdde628e7845bb9da4dfc9614a5b82",
    base_url="https://api.deepseek.com",
)
async def split_messages(data):
    split_messages_dict = {}
    len_current_data = 0
    #count_block = 1
    start_date = datetime.datetime.now().date()
    print(data)
    for channel, messages in data.items():
        count_msg = 0
        for msg in messages:
            '''if count_msg >= 10:
                break'''
            len_str_msg = len(str(msg))
            count_msg += 1
            if len_str_msg + len_current_data >= 100000:
                #count_block += 1
                break # если убрать будет несколько блоков
            len_current_data += len_str_msg
            if not split_messages_dict.get(channel):
                split_messages_dict[channel] = {}
            split_messages_dict[channel][count_msg] = msg
            date = datetime.datetime.fromisoformat(msg.get('date')).date()
            if start_date > date:
                start_date = date
    return {'messages': split_messages_dict, "start_date": start_date}

async def get_deepseek_response(system_prompt: str, user_prompt: str, json_data: str) -> str:
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer sk-c9fdde628e7845bb9da4dfc9614a5b82",  # Замените на ваш API-ключ
        "Content-Type": "application/json"
    }

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    payload = {
        "model": "deepseek-chat",
        "temperature": 0.1,
        "messages": messages,
        "max_tokens": 8192
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                    url,
                    headers=headers,
                    json=payload,
                    #timeout=aiohttp.ClientTimeout(total=60)  # Таймаут 60 сек
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    error_msg = await response.text()
                    return f"Ошибка API (код {response.status}): {error_msg}"
        except asyncio.TimeoutError:
            return "Превышено время ожидания ответа от DeepSeek."
        except Exception as e:
            return f"Произошла ошибка: {str(e)}"


async def fetch_deepseek_response_prompt(data) -> dict:
    prompt = data['prompt']
    #print(data['posts'])
    split_messages_dict = await split_messages(data['posts'])
    json_data = json.dumps(split_messages_dict['messages'], ensure_ascii=False, indent=4)
    system_prompt = (
        f"{prompt}"

        #f"Для форматирования заголовков и подзаголовко используй HTML."
        "В тексте используй HTML-теги для форматирования сообщения для телеграм бота."
        #"Используй эмодзи для выделения заголовков." (<b>, <i>, <a>, <br>, <ul>, <li>, <u>, <s>, <ol>)
        f"Результат должен быть на русском языке."
    )
    user_prompt = f"Данные для анализа (JSON): {json_data}"
    print('Отправляемый промпт:', user_prompt)  # Для отладки

    answer = await get_deepseek_response(system_prompt, user_prompt, json_data)
    return {'answer': answer, 'start_date': split_messages_dict['start_date']}
