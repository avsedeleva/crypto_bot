from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from telethon.sync import TelegramClient
import os
import json
import datetime
import asyncio
import re
# Загружаем переменные окружения (.env)
from deepseek import fetch_deepseek_response_prompt
from settings import DIGEST_PROMPT, GENERAL_DIGEST_PROMPT, ANALYSIS_PROMPT, CHANNEL_LIST

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_ID = int(os.getenv("API_ID")) # Ваш API ID из my.telegram.org
API_HASH = os.getenv("API_HASH")  # Ваш API Hash
SESSION_NAME = f'session/session_name.session'



# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)  # Теперь правильно
)
dp = Dispatcher()

# Инициализация Telethon клиента
client = TelegramClient(SESSION_NAME, API_ID, API_HASH, system_version="4.16.30-vxCUSTOM")


# Определение состояний
class Data(StatesGroup):
    waiting_for_prompt = State()
    waiting_for_channel = State()
    waiting_for_limit = State()
    posts = State()


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Общий криптодайджест"), KeyboardButton(text="Дайджест выбранного канала")],
        [KeyboardButton(text="Анализ канала"), KeyboardButton(text="Свой промпт")],

    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите промпт..."

)
# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    msg = await message.answer(

        "🖐️Привет! Я ИИ-бот. Помогу тебе с анализом <b>Telegram-каналов</b>.\n"
        "🔥Никакого ручного копирования — просто кидай <b>ссылку</b>, а я сделаю всё остальное!\n"
        "Вот что я умею: \n"
        "📌 <b>Краткий дайджест новостей</b> – соберу самое важное за выбранный период.\n"
        "📌 <b>Суммаризация информации</b> – сделаю краткое содержание длинных постов.\n"
        "📌 <b>Сравнение каналов</b> – покажу, о чем пишут разные источники и в чем их различия.\n"
        "🔎 Хочешь попробовать?\n"
        "🖊️ Выбери опцию:",

        #"Введите username или ID группы/канала (например: @durov, -10012345678, https://t.me/...)

        reply_markup=main_keyboard

    )
    await state.update_data(period_message_id=msg.message_id)
    #await state.set_state(Data.waiting_for_prompt)

# --- Обработчик кнопок ---

@dp.message(F.text == "Общий криптодайджест")
async def digest(message: types.Message, state: FSMContext):
    await state.update_data(prompt=GENERAL_DIGEST_PROMPT)
    await state.update_data(limit=1)
    await msg_delete(message, state)
    await process_save_posts(message, state)


@dp.message(F.text == "Анализ канала")
async def analysis(message: types.Message, state: FSMContext):
    await state.update_data(prompt=ANALYSIS_PROMPT)
    await msg_delete(message, state)
    await select_channel(message=message, state=state)


@dp.message(F.text == "Дайджест выбранного канала")
async def forecast(message: types.Message, state: FSMContext):
    await state.update_data(prompt=DIGEST_PROMPT)
    await msg_delete(message, state)
    await select_channel(message=message, state=state)

@dp.message(F.text == "Свой промпт")
async def forecast(message: types.Message, state: FSMContext):
    await state.update_data(prompt=DIGEST_PROMPT)
    await msg_delete(message, state)
    msg = await message.answer(
        "🖊️Напиши ниже свой промпт.\n "
        "На следующем шаге нужно будет указать группу и период анализа сообщений."
    )
    await state.update_data(period_message_id=msg.message_id)
    await state.set_state(Data.waiting_for_prompt)


# --- Опросная часть ---

@dp.message(Data.waiting_for_prompt)
async def process_prompt(message: types.Message, state: FSMContext):
    await state.update_data(prompt=message.text)
    # Удаляем старое сообщение
    await msg_delete(message, state)
    await select_channel(message=message, state=state)

@dp.message(Data.waiting_for_channel)
async def process_channel(message: types.Message, state: FSMContext):
    #Удаляем старое сообщение
    await msg_delete(message, state)

    channel = message.text.strip()
    if 'https://t.me/' in channel:
        channel = f"@{channel[13:]}"
        #print(channel)
    await state.update_data(channel=channel)
    msg = await message.answer("🗓️ За какой период нужно скачать посты (в днях). Максимум 30 дней")
    await state.update_data(period_message_id=msg.message_id)
    await state.set_state(Data.waiting_for_limit)


@dp.message(Data.waiting_for_limit)
async def process_limit(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        msg = await message.answer("Пожалуйста, введите число!")
        await asyncio.sleep(5)
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        return

    limit = int(message.text)
    if limit < 1 or limit > 31:
        msg = await message.answer("Пожалуйста, введите число от 1 до 31!")
        await asyncio.sleep(5)
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        return
    await state.update_data(limit=limit)

    # Удаляем старое сообщение
    await msg_delete(message, state)

    await process_save_posts(message, state)


# --- Utilits ---

async def select_channel(message: types.Message, state: FSMContext):
    msg = await message.answer(
        "🖊️ Введи username, ID группы/канала или ссылку (например: @durov, -10012345678, https://t.me/...)"
    )
    await state.update_data(period_message_id=msg.message_id)
    await state.set_state(Data.waiting_for_channel)


async def process_save_posts(message: types.Message, state: FSMContext):
    posts = {}
    data = await state.get_data()
    channel = data.get('channel')
    limit = data.get('limit')
    channel_list = CHANNEL_LIST if not channel else [channel,]
    for channel in channel_list:

        if not channel:
            continue

        if len(channel_list) < 2:
            msg = await message.answer(f"🕔Начинаю скачивать посты за последние {limit} дней из {channel}...")
        try:
            # Скачиваем посты
            posts[channel] = await download_telegram_posts(channel, limit)

            # Удаляем старое сообщение
            if len(channel_list) < 2:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)

            # Сохраняем в файл
            filename = f"posts_{channel}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            print(filename)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)

            if len(channel_list) < 2:
                # Отправляем файл пользователю
                with open(filename, 'rb') as f:
                    await message.answer_document(
                        document=types.BufferedInputFile(f.read(), filename=filename),
                        caption=f"✅ Вот {len(posts[channel])} постов из {channel}"
                    )
            # Удаляем временный файл
            os.remove(filename)

        except Exception as e:
            logger.error(f"Ошибка при скачивании постов: {e}")
            await message.answer(f"Произошла ошибка: {e}")
    await state.update_data(posts=posts)
    await send_to_ai(message, state)



async def download_telegram_posts(channel, limit):
    posts = []
    END_DATE = datetime.datetime.now(datetime.timezone.utc)
    START_DATE = END_DATE - datetime.timedelta(days=limit)
    async with client:
        async for message in client.iter_messages(channel, offset_date=END_DATE.date()+ datetime.timedelta(days=1)):
            if message.date < START_DATE:
                break
            if START_DATE <= message.date <= END_DATE and message.text != '':
                posts.append({
                    'date': message.date.isoformat(),
                    'text': message.text,
                    'link': f'https://t.me/{channel[1:]}/{message.id}'
                    #'views': message.views if hasattr(message, 'views') else None,
                    #'media': bool(message.media),
                })

    return posts


async def send_to_ai(message: types.Message, state: FSMContext):
    data = await state.get_data()
    msg = await message.answer("🔄 Формирую ответ...", reply_markup=ReplyKeyboardRemove())

    try:
        deepseek_response = await fetch_deepseek_response_prompt(data)
        print(deepseek_response)
        deepseek_response = await simple_html_to_text(deepseek_response)
        print(deepseek_response)

        # Удаляем старое сообщение
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        if len(deepseek_response) < 4000:
            await message.answer(f"\n{deepseek_response}", parse_mode='Markdown')
        else:
            answers = await split_by_paragraphs_answer(deepseek_response)
            for ans in answers:
                await message.answer(f"\n{ans}", parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("❌ Произошла ошибка при обработке запроса.")

async def simple_html_to_text(html):
    # Заменяем HTML теги на Telegram форматирование
    replacements = [
        (r'<h1>(.*?)</h1>', r'*\1*\n\n'),
        (r'<h2>(.*?)</h2>', r'*\1*\n\n'),
        (r'<h3>(.*?)</h3>', r'*\1*\n\n'),
        (r'<b>(.*?)</b>', r'*\1*'),
        (r'<strong>(.*?)</strong>', r'*\1*'),
        (r'<i>(.*?)</i>', r'_\1_'),
        (r'<em>(.*?)</em>', r'_\1_'),
        (r'<code>(.*?)</code>', r'`\1`'),
        (r'<pre>(.*?)</pre>', r'```\1```'),
        (r'<a href="(.*?)">(.*?)</a>', r'[\2](\1)'),
        (r'<ul>(.*?)</ul>', r'\1'),
        (r'<li>(.*?)</li>', r'• \1\n'),
        (r'<p>(.*?)</p>', r'\1\n\n'),
        (r'<br\s*/?>', r'\n'),
        (r'<[^>]+>', r''),  # Удаляем все остальные теги
    ]

    text = html
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.DOTALL)

    # Очищаем множественные переносы строк
    text = re.sub(r'\n\s*\n', '\n\n', text)

    return text.strip()


async def split_by_paragraphs_answer(text: str, max_length=4000) -> list[str]:
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


async def msg_delete(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # Удаляем старое сообщение
    period_message_id = data.get('period_message_id')
    if period_message_id:
        try:
            await message.bot.delete_message(chat_id=message.chat.id, message_id=period_message_id)
        except Exception as e:
            print(f"Не удалось удалить сообщение: {e}")


# Запуск бота
async def main():
    await client.connect()
    me = await client.get_me()
    print(me.first_name)
    await dp.start_polling(bot)


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
