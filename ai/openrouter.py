import asyncio
import datetime
import os
import json
import base64
from io import BytesIO

import httpx
from aiogram.client.session import aiohttp

from logger.logger import Logger
from settings import proxy

logger_manager = Logger()
logger_general= logger_manager.get_logger_general("ERROR")

'''response = requests.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": "Bearer <OPENROUTER_API_KEY>",
    "HTTP-Referer": "test", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "test", # Optional. Site title for rankings on openrouter.ai.
  },

  messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
  data=json.dumps({
    "model": "openrouter/auto", # Optional
    "messages": [
      {
        "role": "user",
        "content": "What is the meaning of life?"
      }
    ]
  })
)
'''


async def split_messages(data):
  split_messages_dict = {}
  len_current_data = 0
  # count_block = 1
  start_date = datetime.datetime.now().date()
  is_all_inclusive = True
  # print(data)
  for channel, messages in data.items():
    count_msg = 0
    for msg in messages:
      '''if count_msg >= 10:
          break'''
      len_str_msg = len(str(msg))
      count_msg += 1
      if len_str_msg + len_current_data >= 190000:
        # count_block += 1
        is_all_inclusive = False
        print(channel)
        # break # если убрать будет несколько блоков
      else:
        len_current_data += len_str_msg
        if not split_messages_dict.get(channel):
          split_messages_dict[channel] = {}
        split_messages_dict[channel][count_msg] = msg
        date = datetime.datetime.fromisoformat(msg.get('date')).date()
        # print(start_date,date, start_date > date)
        if start_date > date:
          start_date = date
          # print(start_date)
  print('is_all_inclusive', is_all_inclusive)
  return {'messages': split_messages_dict, "start_date": start_date, "is_all_inclusive": is_all_inclusive}

async def get_open_router_response(system_prompt: str, user_prompt: str, type_model) -> str:
  url = "https://openrouter.ai/api/v1/chat/completions"
  headers = {
          "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
          "Content-Type": "application/json",
            "HTTP-Referer": "test",  # Optional. Site URL for rankings on openrouter.ai.
            "X-Title": "test",  # Optional. Site title for rankings on openrouter.ai.
          }
  model = "qwen/qwen3-vl-8b-instruct" if type_model!='twitter' else "GPT-4o:online" #'x-ai/grok-4-fast'
  messages = [{"role": "system", "content": system_prompt},]
  if type_model != 'twitter':
    messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt}
    ]
  print(json.dumps(messages, indent=4))
  payload = {
  "model": model, #"qwen/qwen3-vl-235b-a22b-instruct", #"deepseek/deepseek-v3.2-exp", #"qwen/qwen3-vl-235b-a22b-instruct",#"google/gemini-2.5-pro", #"openrouter/auto",
  "temperature": 0.1,
  "messages": messages,
  "max_tokens": 20000,
  'provider': {
    'sort': 'latency',

  }
  }


  async with aiohttp.ClientSession() as session:
    try:
      async with session.post(
              url,
              headers=headers,
              json=payload,
              #proxy=proxy
              # timeout=aiohttp.ClientTimeout(total=60)  # Таймаут 60 сек
      ) as response:
        if response.status == 200:
          data = await response.json()
          return data["choices"][0]["message"]["content"]
        else:
          error_msg = await response.text()
          logger_general.error('ERROR LLM код %s ошибка %s', response.status, error_msg)
          return f"Ошибка API (код {response.status}): {error_msg}"
    except asyncio.TimeoutError:
      logger_general.error('ERROR LLM %s ', "TimeoutError")
      return "Превышено время ожидания ответа от DeepSeek."
    except Exception as e:
      logger_general.error('ERROR LLM %s ', e)
      return f"Произошла ошибка: {str(e)}"

async def get_open_router_image(user_prompt: str) -> str:
  url = "https://openrouter.ai/api/v1/chat/completions"
  headers = {
          "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
          "Content-Type": "application/json",
            "HTTP-Referer": "test",  # Optional. Site URL for rankings on openrouter.ai.
            "X-Title": "test",  # Optional. Site title for rankings on openrouter.ai.
          }

  messages = [
  {"role": "system", "content": f"Сгенерируй картинку. Пропорции картинки 16:9. Слова на картинке английские. В правый верхний угол изображения вставь название канала @GenAI_crypto_bot. На картинке должна быть отражена суть постов ниже:\n {user_prompt}"},
  # {"role": "user", "content": user_prompt}
  ]

  payload = {
  "model": "google/gemini-2.5-flash-image-preview", #"qwen/qwen3-vl-235b-a22b-instruct", #"deepseek/deepseek-v3.2-exp", #"qwen/qwen3-vl-235b-a22b-instruct",#"google/gemini-2.5-pro", #"openrouter/auto",
  "temperature": 0.1,
  "messages": messages,
  "max_tokens": 20000,
  'provider': {
    'sort': 'latency'
  }
  }


  async with aiohttp.ClientSession() as session:
    try:
      async with session.post(
              url,
              headers=headers,
              json=payload,
              proxy=proxy
              # timeout=aiohttp.ClientTimeout(total=60)  # Таймаут 60 сек
      ) as response:

        if response.status == 200:


            data = await response.json()  # Парсим JSON

            # Извлекаем base64 изображение из ответа:cite[1]
            image_data = data['choices'][0]['message']['images'][0]['image_url']['url']

            # Убираем префикс data URL чтобы получить чистый base64:cite[2]
            base64_string = image_data.split(',')[1]

            # Декодируем base64 в бинарные данные
            image_bytes = base64.b64decode(base64_string)
            #print(image_bytes)
            return image_bytes
        else:
          error_msg = await response.text()
          logger_general.error('ERROR LLM IMG код %s ошибка %s', response.status, error_msg)
          return f"Ошибка API (код {response.status}): {error_msg}"
    except asyncio.TimeoutError:
      logger_general.error('ERROR LLM IMG %s ', "TimeoutError")
      return "Превышено время ожидания ответа от DeepSeek."
    except Exception as e:
      logger_general.error('ERROR LLM IMG %s ', e)
      return f"Произошла ошибка: {str(e)}"


async def fetch_openrouter_response_prompt(data) -> dict:
  #image = None if not data['need_image'] else await get_open_image("Танцующий робот")
  model = data['model']
  prompt = data['prompt']
  addition_prompt = data['addition_prompt']
  split_messages_dict = await split_messages(data['posts'])
  #print(json.dumps(split_messages_dict['messages'], indent=4))
  json_data = json.dumps(split_messages_dict['messages'], ensure_ascii=False, indent=4)
  system_prompt = f"{prompt}{addition_prompt}"
  user_prompt = f"Данные для анализа (JSON): {json_data}"
  answer = await get_open_router_response(system_prompt, user_prompt, model)
  #print('for img', answer)
  image = None if not data.get('need_image') else await get_open_router_image(answer)
  return {
    'answer': answer,
    'start_date': split_messages_dict['start_date'],
    'is_all_inclusive': split_messages_dict['is_all_inclusive'],
    'image': image
  }