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
from logger.logger import Logger
from settings import DIGEST_PROMPT, GENERAL_DIGEST_PROMPT, ANALYSIS_PROMPT, CHANNEL_LIST


load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_ID = int(os.getenv("API_ID")) # Ваш API ID из my.telegram.org
API_HASH = os.getenv("API_HASH")  # Ваш API Hash
SESSION_NAME = f'session/session_name.session'



# Настройка логирования
#logging.basicConfig(level=logging.INFO)
#logger = logging.getLogger(__name__)
logger_manager = Logger()

logger_prompt = logger_manager.get_logger_prompt("PROMPT")
logger_answer = logger_manager.get_logger_answer("ANSWER")
logger_general = logger_manager.get_logger_general("GENERAL")

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
    waiting_for_command = State()
    posts = State()


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Общий криптодайджест"), KeyboardButton(text="Свой промпт по криптоновостям")],
        [KeyboardButton(text="Дайджест выбранного канала"), KeyboardButton(text="Анализ канала")],
        [KeyboardButton(text="Свой промпт по каналу")],

    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите опцию..."

)
# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    #await state.update_data(user_id=message.from_user.id, user_username=message.from_user.username)
    logger_general.info('USER %s %s %s START', message.from_user.id, message.from_user.first_name, message.from_user.username)
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    msg = await message.answer(

        "🖐️Привет! Я ИИ-бот. Помогу тебе с анализом <b>Telegram-каналов</b>.\n"
        #"🔥Никакого ручного копирования — просто кидай <b>ссылку</b>, а я сделаю всё остальное!\n"
        "Вот что я умею: \n"
        "📌 <b>Общий криптодайджест</b> – соберу самое важное по тематике криптовалют за день.\n"
        "📌 <b>Дайджест выбранного канала</b> – соберу самое важное по указанному каналу за выбранный период.\n"
        "📌 <b>Анализ канала</b> – проведу анализ указанного канала за выбранный период\n"
        "🔎 Хочешь попробовать?\n"
        "🖊️ Выбери опцию:",

        #"Введите username или ID группы/канала (например: @durov, -10012345678, https://t.me/...)

        reply_markup=main_keyboard

    )
    await state.update_data(
        period_message_id=msg.message_id,
        user_id=message.from_user.id,
        user_username=message.from_user.username
    )
    #await state.set_state(Data.waiting_for_prompt)

# Обработчик команды /menu
@dp.message(Command("menu"))
async def cmd_command(message: types.Message, state: FSMContext):
    # Удаляем старое сообщение
    try:
        await msg_delete(message, state)
    except:
        pass
    await state.clear()
    #await state.update_data(user_id=message.from_user.id, user_username=message.from_user.username)
    logger_general.info('USER %s %s %s MENU', message.from_user.id, message.from_user.first_name, message.from_user.username)
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    msg = await message.answer(
        "🖊️ Выбери опцию:",
        reply_markup=main_keyboard
    )
    await state.update_data(
        period_message_id=msg.message_id,
        user_id=message.from_user.id,
        user_username=message.from_user.username
    )

# --- Обработчик кнопок ---

@dp.message(F.text == "Общий криптодайджест")
async def general_digest(message: types.Message, state: FSMContext):
    logger_general.info('USER %s %s %s GENERAL_DIGEST', message.from_user.id, message.from_user.first_name, message.from_user.username)
    logger_prompt.info('USER %s %s %s GENERAL_DIGEST_PROMPT %s', message.from_user.id, message.from_user.first_name, message.from_user.username, GENERAL_DIGEST_PROMPT)
    await msg_delete(message, state)
    await state.update_data(prompt=GENERAL_DIGEST_PROMPT, type='general', period_message_id=message.message_id)
    await select_channel(message=message, state=state)

@dp.message(F.text == "Свой промпт по криптоновостям")
async def prompt_cryptonews(message: types.Message, state: FSMContext):
    logger_general.info('USER %s %s %s GENERAL_OTHER', message.from_user.id, message.from_user.first_name, message.from_user.username)
    await msg_delete(message, state)
    await state.update_data(prompt=None, type='general', period_message_id=message.message_id)
    await select_channel(message=message, state=state)


@dp.message(F.text == "Анализ канала")
async def analysis(message: types.Message, state: FSMContext):
    logger_general.info('USER %s %s %s ANALYSIS', message.from_user.id, message.from_user.first_name, message.from_user.username)
    logger_prompt.info('USER %s %s %s ANALYSIS_PROMPT %s', message.from_user.id, message.from_user.first_name, message.from_user.username, ANALYSIS_PROMPT)
    await msg_delete(message, state)
    await state.update_data(prompt=ANALYSIS_PROMPT, type="one_channel", period_message_id=message.message_id)
    await select_channel(message=message, state=state)


@dp.message(F.text == "Дайджест выбранного канала")
async def digest(message: types.Message, state: FSMContext):
    logger_general.info('USER %s %s %s DIGEST', message.from_user.id, message.from_user.first_name, message.from_user.username)
    logger_prompt.info('USER %s %s %s DIGEST_PROMPT %s', message.from_user.id, message.from_user.first_name, message.from_user.username, DIGEST_PROMPT)
    await msg_delete(message, state)
    await state.update_data(prompt=DIGEST_PROMPT, type="one_channel", period_message_id=message.message_id)
    await select_channel(message=message, state=state)

@dp.message(F.text == "Свой промпт по каналу")
async def prompt(message: types.Message, state: FSMContext):
    logger_general.info('USER %s %s %s OTHER', message.from_user.id, message.from_user.first_name, message.from_user.username)
    await msg_delete(message, state)
    await state.update_data(prompt=None, type='one_channel', period_message_id=message.message_id)
    await select_channel(message=message, state=state)


# --- Опросная часть ---

@dp.message(Data.waiting_for_command)
async def process_command(message: types.Message, state: FSMContext):
    # Удаляем старое сообщение
    await msg_delete(message, state)
    msg = await message.answer(
        "Нажми /menu, чтоб задать новый запрос.",
    )
    await state.update_data(period_message_id=msg.message_id)

@dp.message(Data.waiting_for_channel)
async def process_channel(message: types.Message, state: FSMContext):
    #Удаляем старое сообщение
    await msg_delete(message, state)
    logger_general.info('USER %s %s %s CHANNEL %s', message.from_user.id, message.from_user.first_name, message.from_user.username, message.text)
    channel = message.text.strip()

    if 'https://t.me/' in channel:
        channel = f"@{channel[13:]}"
    if '@' not in channel:
        msg = await message.answer(
            "Пожалуйста, введи username или ссылку канала корректно",
            input_field_placeholder="например: @durov, https://t.me/..."
        )
        #await asyncio.sleep(5)
        #msg = await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        await state.update_data(period_message_id=message.message_id)
        await msg_delete(message, state)
        await state.update_data(period_message_id=msg.message_id)
        logger_general.error('USER %s %s %s CHANNEL_ERROR', message.from_user.id, message.from_user.username, message.text)
        return
    await state.update_data(channel=channel, period_message_id=message.message_id)
    await select_limit(message, state)


@dp.message(Data.waiting_for_limit)
async def process_limit(message: types.Message, state: FSMContext):
    # Удаляем старое сообщение
    await msg_delete(message, state)
    data = await state.get_data()
    logger_general.info('USER %s %s %s LIMIT %s', message.from_user.id, message.from_user.first_name, message.from_user.username, message.text)
    if not message.text.isdigit():
        msg = await message.answer("Пожалуйста, введи число!")
        logger_general.error('USER %s %s %s LIMIT_ERROR %s', message.from_user.id, message.from_user.first_name, message.from_user.username, message.text)
        await state.update_data(period_message_id=message.message_id)
        await msg_delete(message, state)
        await state.update_data(period_message_id=msg.message_id)
        return

    limit = int(message.text)
    max_limit =  31 if data.get('type') == 'one_channel' else 5
    if limit < 1 or limit > max_limit:
        msg = await message.answer(f"Пожалуйста, введи число от 1 до {max_limit}!")
        await state.update_data(period_message_id=message.message_id)
        await msg_delete(message, state)
        await state.update_data(period_message_id=msg.message_id)
        logger_general.error('USER %s %s %s LIMIT_ERROR %s', message.from_user.id, message.from_user.first_name, message.from_user.username, message.text)
        return

    await state.update_data(limit=limit, period_message_id=message.message_id)
    await select_prompt(message, state)

@dp.message(Data.waiting_for_prompt)
async def process_prompt(message: types.Message, state: FSMContext):
    logger_prompt.info('USER %s %s %s OTHER_PROMPT %s', message.from_user.id, message.from_user.first_name, message.from_user.username, message.text)
    # Удаляем старое сообщение
    await msg_delete(message, state)
    await state.update_data(prompt=message.text, period_message_id=message.message_id)
    await process_save_posts(message, state)


# --- Utilits ---

async def select_channel(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data.get('type') == "one_channel":
        await msg_delete(message, state)
        msg = await message.answer(
            "🖊️ Введи username или ссылку канала(например: @durov, https://t.me/...)")

        await state.update_data(period_message_id=msg.message_id)
        await state.set_state(Data.waiting_for_channel)
    else:
        await select_limit(message, state)


async def select_limit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await msg_delete(message, state)
    max_limit = 31 if data.get('type') == 'one_channel' else 5
    msg = await message.answer(f"🗓️ За какой период нужно скачать посты (в днях). Максимум {max_limit} дней")
    await state.update_data(period_message_id=msg.message_id)
    await state.set_state(Data.waiting_for_limit)


async def select_prompt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    prompt = data.get("prompt")
    await msg_delete(message, state)
    if not prompt:
        msg = await message.answer(
            "🖊️Напиши ниже свой промпт.\n "
        )
        await state.update_data(period_message_id=msg.message_id)
        await state.set_state(Data.waiting_for_prompt)
    else:
        await process_save_posts(message, state)


async def process_save_posts(message: types.Message, state: FSMContext):
    await msg_delete(message, state)
    posts = {}
    data = await state.get_data()
    type_prompt = data.get('type')
    channel = data.get('channel')
    limit = data.get('limit')
    channel_list = CHANNEL_LIST if type_prompt == 'general' else [channel,]
    msg = await message.answer(f"🕔Начинаю скачивать посты...")
    for channel in channel_list:

        if not channel:
            continue

        try:
            # Скачиваем посты
            posts[channel] = await download_telegram_posts(channel, limit)


            # Сохраняем в файл
            filename = f"posts_{channel}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            #print(filename)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)


            if type_prompt == "one_channel" and len(posts[channel]) == 0:
                await message.answer(
                    f"❗Сообщения за выбранный период отсутствуют.\n"
                    "Выбери другой период в днях(максимум 30) или задай другой запрос через команду /start"
                )
                return
            '''if len(channel_list) < 2:
                # Отправляем файл пользователю
                with open(filename, 'rb') as f:
                    await message.answer_document(
                        document=types.BufferedInputFile(f.read(), filename=filename),
                        caption=f"✅ Вот {len(posts[channel])} постов из {channel}"
                    )'''

            # Удаляем временный файл
            os.remove(filename)

        except Exception as e:
            #logger_general.error(f"Ошибка при скачивании постов: {e}")
            await message.answer(f"❌Произошла ошибка: username или ссылка канала указаны неверно")
            logger_general.error('USER %s %s %s LOADING_MSG_ERROR %s', message.from_user.id, message.from_user.first_name, message.from_user.username, e)
            return await select_channel(message, state)
    await state.update_data(posts=posts)
    # Удаляем старое сообщение
    await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)

    return await send_to_ai(message, state)



async def download_telegram_posts(channel, limit):
    posts = []
    end = datetime.datetime.now(datetime.timezone.utc)
    end_date = end.date()+ datetime.timedelta(days=1)
    start = end_date - datetime.timedelta(days=limit)
    #print(end, end_date, start)
    async with client:
        async for message in client.iter_messages(channel, offset_date=end):
            if message.date.date() < start:
                break
            if start <= message.date.date() <= end_date and message.text != '':
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
    end_date = datetime.datetime.now().date()
    try:
        deepseek_response = await fetch_deepseek_response_prompt(data)
        logger_answer.info('USER %s %s %s DS_ANSWER %s', message.from_user.id, message.from_user.first_name, message.from_user.username, deepseek_response)
        #print(deepseek_response)
        start_date = deepseek_response['start_date']
        days_count = end_date - start_date + datetime.timedelta(days=1)
        deepseek_response = deepseek_response['answer']
        deepseek_response = await simple_html_to_text(deepseek_response)
        #print(deepseek_response)
        logger_answer.info('USER %s %s %s FORMAT_ANSWER %s', message.from_user.id, message.from_user.first_name, message.from_user.username, deepseek_response)

        # Удаляем старое сообщение
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        if data.get('limit') > days_count.days:
            await message.answer(
                f"🤖 *Внимание!*"
                f"\nВ связи с большим объемом информации, смог обработать только последние {days_count.days} дней."
                f"\n🛠️_Работаю над расширением возможностей!_",
                parse_mode='Markdown'
            )
        if len(deepseek_response) < 4000:
            await message.answer(f"\n{deepseek_response}", parse_mode='Markdown')
        else:
            answers = await split_by_paragraphs_answer(deepseek_response)
            for ans in answers:
                await message.answer(f"\n{ans}", parse_mode='Markdown')

    except Exception as e:
        await message.answer("❌ Произошла ошибка при обработке запроса.")
        logger_general.error('USER %s %s %s DS_ERROR %s', message.from_user.id, message.from_user.first_name, message.from_user.username, e)
    await state.set_state(Data.waiting_for_command)

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
        (r'<code>(.*?)</code>', r'\1'),
        (r'<pre>(.*?)</pre>', r'```\1```'),
        (r'<a\s+href=[\'"](.*?)[\'"]>(.*?)</a>', r'[\2](\1)'),
        (r'<ul>(.*?)</ul>', r'\1'),
        (r'<li>(.*?)</li>', r'• \1\n'),
        (r'<p>(.*?)</p>', r'\1\n\n'),
        (r'<br\s*/?>', r'\n'),
        #(r'\n\n', r'\n'),
        (r'<[^>]+>', r''),  # Удаляем все остальные теги
    ]

    text = html
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.DOTALL)

    # Очищаем множественные переносы строк
    text = re.sub(r'\n\s*\n', '\n\n', text)
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
    print('START_APP', me.first_name)
    await dp.start_polling(bot)


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
