import codecs
import re
from io import BytesIO

from dotenv import load_dotenv
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Message, BufferedInputFile
from aiogram import Dispatcher, types, F
from aiogram.filters import Command, BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import os
import json
import datetime

from ai.deepseek import fetch_deepseek_response_prompt
from ai.openrouter import fetch_openrouter_response_prompt
from logger.logger import Logger
from settings import CHANNEL_LIST, MESSAGES, PROMPTS
from utilits import split_by_paragraphs_answer, simple_html_to_text, split_by_paragraphs_answer_img

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")


# Настройка логирования
logger_manager = Logger()
logger_prompt = logger_manager.get_logger_prompt("PROMPT")
logger_answer = logger_manager.get_logger_answer("ANSWER")
logger_general = logger_manager.get_logger_general("GENERAL")


dp = Dispatcher()

# Определение состояний
class Data(StatesGroup):
    waiting_for_prompt = State()
    waiting_for_channel = State()
    waiting_for_limit = State()
    waiting_for_command = State()
    posts = State()


class LanguageFilter(BaseFilter):
    def __init__(self, button_key: str):
        self.button_key = button_key

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        data = await state.get_data()
        lang = data.get('lang', 'en')

        # Проверяем условие с учетом языка
        return message.text == MESSAGES["kbd"][self.button_key].get(lang, "")


def get_main_keyboard(lang):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MESSAGES["kbd"]["trending_tokens"][lang]),],
            [KeyboardButton(text=MESSAGES["kbd"]["general_digest"][lang]), KeyboardButton(text=MESSAGES["kbd"]["general_forecast"][lang]), ],
            [KeyboardButton(text=MESSAGES["kbd"]["digest"][lang]), KeyboardButton(text=MESSAGES["kbd"]["analysis"][lang])],
            [KeyboardButton(text=MESSAGES["kbd"]["general_other"][lang]), KeyboardButton(text=MESSAGES["kbd"]["other"][lang])],
            #[KeyboardButton(text=MESSAGES["kbd"]["twitter"][lang]),]

             ],
        resize_keyboard=True,
        input_field_placeholder=MESSAGES["kbd"]["input_field"][lang]

)

def get_lang_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MESSAGES["lang"]["kbd"]["ru"]), KeyboardButton(text=MESSAGES["lang"]["kbd"]["en"])],

        ],
        resize_keyboard=True,

)

def get_img_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='ДА'), KeyboardButton(text='НЕТ')],

        ],
        resize_keyboard=True,

)


# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    # Удаляем старое сообщение
    await msg_delete(message, state)
    await state.clear()
    await state.update_data(model='no_twitter', need_image=False)
    logger_general.info('USER %s %s %s START', message.from_user.id, message.from_user.first_name, message.from_user.username)
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await select_lang(message, state)
    '''msg = await message.answer(
        MESSAGES['start'][lang],
        reply_markup=get_main_keyboard(lang)
    )
    await state.update_data(
        period_message_id=msg.message_id,
        user_id=message.from_user.id,
        user_username=message.from_user.username
    )'''

# Обработчик команды /menu
@dp.message(Command("menu"))
async def cmd_command(message: types.Message, state: FSMContext):
    # Удаляем старое сообщение
    await msg_delete(message, state)
    await state.clear()
    await state.update_data(model='no_twitter', need_image=False)
    logger_general.info('USER %s %s %s MENU', message.from_user.id, message.from_user.first_name, message.from_user.username)
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await select_lang(message, state)
    '''msg = await message.answer(
        MESSAGES['menu'][lang],
        reply_markup=get_main_keyboard(lang)
    )
    await state.update_data(
        period_message_id=msg.message_id,
        user_id=message.from_user.id,
        user_username=message.from_user.username
    )'''

# --- Обработчик кнопок ---
@dp.message(F.text == MESSAGES["lang"]["kbd"]["ru"])
async def ru(message: types.Message, state: FSMContext):
    lang = "ru"
    logger_general.info('USER %s %s %s RU', message.from_user.id, message.from_user.first_name, message.from_user.username)
    #logger_prompt.info('USER %s %s %s GENERAL_DIGEST_PROMPT %s', message.from_user.id, message.from_user.first_name, message.from_user.username, PROMPTS["general_digest"])

    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await msg_delete(message, state)
    await state.update_data(lang=lang)
    if message.from_user.id in [8320319465, 97592799]:
        return await select_img(message=message, state=state)
    await select_option(message=message, state=state)


@dp.message(F.text == MESSAGES["lang"]["kbd"]["en"])
async def en(message: types.Message, state: FSMContext):
    lang = "en"
    logger_general.info('USER %s %s %s EN', message.from_user.id, message.from_user.first_name, message.from_user.username)
    #logger_prompt.info('USER %s %s %s GENERAL_DIGEST_PROMPT %s', message.from_user.id, message.from_user.first_name, message.from_user.username, PROMPTS["general_digest"])
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await msg_delete(message, state)
    await state.update_data(lang=lang)
    if message.from_user.id in [8320319465, 97592799]:
        return await select_img(message=message, state=state)
    await select_option(message=message, state=state)

@dp.message(F.text == 'ДА')
async def yes_img(message: types.Message, state: FSMContext):
    #logger_prompt.info('USER %s %s %s GENERAL_DIGEST_PROMPT %s', message.from_user.id, message.from_user.first_name, message.from_user.username, PROMPTS["general_digest"])
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await msg_delete(message, state)
    await state.update_data(need_image=True)
    await select_option(message=message, state=state)

@dp.message(F.text == 'НЕТ')
async def no_img(message: types.Message, state: FSMContext):
    #logger_prompt.info('USER %s %s %s GENERAL_DIGEST_PROMPT %s', message.from_user.id, message.from_user.first_name, message.from_user.username, PROMPTS["general_digest"])
    await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await msg_delete(message, state)
    await select_option(message=message, state=state)


#@dp.message(F.text == MESSAGES["kbd"]["general_digest"][lang])
#@dp.message(F.text == MESSAGES["kbd"]["general_digest"][data["lang"]])
@dp.message(LanguageFilter("general_digest"))
async def general_digest(message: types.Message, state: FSMContext):
    logger_general.info('USER %s %s %s GENERAL_DIGEST', message.from_user.id, message.from_user.first_name, message.from_user.username)
    logger_prompt.info('USER %s %s %s GENERAL_DIGEST_PROMPT %s', message.from_user.id, message.from_user.first_name, message.from_user.username, PROMPTS["general_digest"])
    await msg_delete(message, state)
    await state.update_data(prompt=PROMPTS["general_digest"], type='general', period_message_id=message.message_id)
    await select_channel(message=message, state=state)

#@dp.message(F.text == MESSAGES['general_forecast'][lang])
#@dp.message(lambda message: message.text == MESSAGES["kbd"]["general_forecast"][lang] if lang else False)
@dp.message(LanguageFilter("general_forecast"))
async def general_forecast(message: types.Message, state: FSMContext):
    logger_general.info('USER %s %s %s GENERAL_FORECAST', message.from_user.id, message.from_user.first_name, message.from_user.username)
    logger_prompt.info('USER %s %s %s GENERAL_FORECAST_PROMPT %s', message.from_user.id, message.from_user.first_name, message.from_user.username, PROMPTS["general_forecast"])
    await msg_delete(message, state)
    await state.update_data(prompt=PROMPTS["general_forecast"], type='general', period_message_id=message.message_id)
    await select_channel(message=message, state=state)

@dp.message(LanguageFilter("trending_tokens"))
async def trend_tokens(message: types.Message, state: FSMContext):
    logger_general.info('USER %s %s %s TRENDING_TOKENS', message.from_user.id, message.from_user.first_name, message.from_user.username)
    logger_prompt.info('USER %s %s %s TRENDING_TOKENS_PROMPT %s', message.from_user.id, message.from_user.first_name, message.from_user.username, PROMPTS["trending_tokens"])
    await msg_delete(message, state)
    await state.update_data(prompt=PROMPTS["trending_tokens"], type='general', period_message_id=message.message_id)
    await select_channel(message=message, state=state)

#@dp.message(F.text == MESSAGES['general_other'][lang])
#@dp.message(lambda message: message.text == MESSAGES["kbd"]["general_other"][lang] if lang else False)
@dp.message(LanguageFilter("general_other"))
async def prompt_cryptonews(message: types.Message, state: FSMContext):
    logger_general.info('USER %s %s %s GENERAL_OTHER', message.from_user.id, message.from_user.first_name, message.from_user.username)
    await msg_delete(message, state)
    await state.update_data(prompt=None, type='general', period_message_id=message.message_id)
    await select_channel(message=message, state=state)

#@dp.message(F.text == MESSAGES['digest'][lang])
@dp.message(LanguageFilter("digest"))
#@dp.message(lambda message: message.text == MESSAGES["kbd"]["digest"][lang] if lang else False)
async def digest(message: types.Message, state: FSMContext):
    logger_general.info('USER %s %s %s DIGEST', message.from_user.id, message.from_user.first_name, message.from_user.username)
    logger_prompt.info('USER %s %s %s DIGEST_PROMPT %s', message.from_user.id, message.from_user.first_name, message.from_user.username, PROMPTS["digest"])
    await msg_delete(message, state)
    await state.update_data(prompt=PROMPTS["digest"], type="one_channel", period_message_id=message.message_id)
    await select_channel(message=message, state=state)

#@dp.message(F.text == MESSAGES['analysis'][lang])
#@dp.message(lambda message: message.text == MESSAGES["kbd"]["analysis"][lang] if lang else False)
@dp.message(LanguageFilter("analysis"))
async def analysis(message: types.Message, state: FSMContext):
    logger_general.info('USER %s %s %s ANALYSIS', message.from_user.id, message.from_user.first_name, message.from_user.username)
    logger_prompt.info('USER %s %s %s ANALYSIS_PROMPT %s', message.from_user.id, message.from_user.first_name, message.from_user.username, PROMPTS["analysis"])
    await msg_delete(message, state)
    await state.update_data(prompt=PROMPTS["analysis"], type="one_channel", period_message_id=message.message_id)
    await select_channel(message=message, state=state)

#@dp.message(F.text == MESSAGES['other'][lang])
#@dp.message(lambda message: message.text == MESSAGES["kbd"]["other"][lang] if lang else False)
@dp.message(LanguageFilter("other"))
async def prompt(message: types.Message, state: FSMContext):
    logger_general.info('USER %s %s %s OTHER', message.from_user.id, message.from_user.first_name, message.from_user.username)
    await msg_delete(message, state)
    await state.update_data(prompt=None, type='one_channel', period_message_id=message.message_id)
    await select_channel(message=message, state=state)

@dp.message(LanguageFilter("twitter"))
async def twitter(message: types.Message, state: FSMContext):
    logger_general.info('USER %s %s %s TWITTER', message.from_user.id, message.from_user.first_name, message.from_user.username)
    await msg_delete(message, state)
    await state.update_data(prompt=None, type='twitter', period_message_id=message.message_id, model='twitter')
    await select_prompt(message, state)


# --- Опросная часть ---

@dp.message(Data.waiting_for_command)
async def process_command(message: types.Message, state: FSMContext):
    # Удаляем старое сообщение
    await msg_delete(message, state)
    data = await state.get_data()
    lang = data.get("lang")
    msg = await message.answer(MESSAGES["new_command"][lang])
    await state.update_data(period_message_id=msg.message_id)

@dp.message(Data.waiting_for_channel)
async def process_channel(message: types.Message, state: FSMContext):
    #Удаляем старое сообщение
    await msg_delete(message, state)
    data = await state.get_data()
    lang = data.get("lang")
    logger_general.info('USER %s %s %s CHANNEL %s', message.from_user.id, message.from_user.first_name, message.from_user.username, message.text)
    channel = message.text.strip()

    if 'https://t.me/' in channel:
        channel = f"@{channel[13:]}"
    if '@' not in channel:
        msg = await message.answer(
            MESSAGES["channel"]["error"][lang].format(example=MESSAGES["channel"]["example"][lang]),
            input_field_placeholder=MESSAGES["channel"]["example"][lang]
        )
        await state.update_data(period_message_id=message.message_id)
        await msg_delete(message, state)
        await state.update_data(period_message_id=msg.message_id, channel_error=True)
        logger_general.error('USER %s %s %s CHANNEL_ERROR', message.from_user.id, message.from_user.username, message.text)
        return
    await state.update_data(channel=channel, period_message_id=message.message_id)
    await select_limit(message, state)


@dp.message(Data.waiting_for_limit)
async def process_limit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")
    # Удаляем старое сообщение
    await msg_delete(message, state)
    data = await state.get_data()
    logger_general.info('USER %s %s %s LIMIT %s', message.from_user.id, message.from_user.first_name, message.from_user.username, message.text)
    max_limit = 31 if data.get('type') == 'one_channel' else 3
    if not message.text.isdigit():
        msg = await message.answer(MESSAGES["limit"]["error"][lang].format(max_limit=max_limit))
        logger_general.error('USER %s %s %s LIMIT_ERROR %s', message.from_user.id, message.from_user.first_name, message.from_user.username, message.text)
        await state.update_data(period_message_id=message.message_id)
        await msg_delete(message, state)
        await state.update_data(period_message_id=msg.message_id)
        return

    limit = int(message.text)

    if limit < 1 or limit > max_limit:
        msg = await message.answer(MESSAGES["limit"]["error"][lang].format(max_limit=max_limit))
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
async def select_lang(message: types.Message, state: FSMContext):
    msg = await message.answer(
        MESSAGES["select_lang"],
        reply_markup=get_lang_keyboard()
    )
    await state.update_data(period_message_id=msg.message_id, channel_error=False)

async def select_img(message: types.Message, state: FSMContext):
    msg = await message.answer(
        MESSAGES["select_img"],
        reply_markup=get_img_keyboard()
    )
    await state.update_data(period_message_id=msg.message_id)

async def select_option(message: types.Message, state: FSMContext):
    await msg_delete(message, state)
    data = await state.get_data()
    lang= data.get("lang")
    msg = await message.answer(
            MESSAGES['start'][lang],
            reply_markup=get_main_keyboard(lang)
        )
    await state.update_data(period_message_id=msg.message_id)


async def select_channel(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")
    if not data.get("prompt"):  #Удаляем выбор своего промпта
        await msg_delete(message, state)
    if data.get('type') == "one_channel":
        msg = await message.answer(MESSAGES["channel"]["select"][lang].format(example=MESSAGES["channel"]["example"][lang]))
        await state.update_data(period_message_id=msg.message_id, channel_error=False)
        await state.set_state(Data.waiting_for_channel)
    else:
        await select_limit(message, state)


async def select_limit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")
    if data.get("channel_error"):
        # Удаляем старое сообщение
        await msg_delete(message, state)
    max_limit = 31 if data.get('type') == 'one_channel' else 3
    msg = await message.answer(MESSAGES["limit"]["select"][lang].format(max_limit=max_limit))
    await state.update_data(period_message_id=msg.message_id)
    await state.set_state(Data.waiting_for_limit)


async def select_prompt(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")
    prompt = data.get("prompt")
    await msg_delete(message, state)
    if not prompt:
        msg = await message.answer(MESSAGES["custom_prompt"][lang])
        await state.update_data(period_message_id=msg.message_id)
        await state.set_state(Data.waiting_for_prompt)
    else:
        await process_save_posts(message, state)


async def process_save_posts(message: types.Message, state: FSMContext):

    posts = {}
    data = await state.get_data()
    lang = data.get("lang")
    type_prompt = data.get('type')
    channel = data.get('channel')
    limit = data.get('limit')
    channel_list = CHANNEL_LIST if type_prompt == 'general' else [channel,]
    msg = await message.answer(MESSAGES["loading"]["download"][lang])
    await state.update_data(period_message_id=msg.message_id)
    for channel in channel_list:
        if not channel:
            continue
        try:
            # Скачиваем посты
            #print(channel)
            posts[channel] = await download_telegram_posts(channel, limit)

            # Сохраняем в файл
            filename = f"posts_{channel}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(posts, f, ensure_ascii=False, indent=2)

            if type_prompt == "one_channel" and len(posts[channel]) == 0:
                await msg_delete(msg, state)
                msg = await message.answer(MESSAGES["attention"]["no_post"][lang])
                await state.update_data(period_message_id=msg.message_id)
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
            await msg_delete(msg, state)
            msg = await message.answer(MESSAGES["channel"]["error_channel"][lang])
            await state.update_data(period_message_id=msg.message_id, channel_error=True)
            logger_general.error('USER %s %s %s LOADING_MSG_ERROR %s', message.from_user.id, message.from_user.first_name, message.from_user.username, e)
            return await select_channel(message, state)
    await state.update_data(posts=posts)
    # Удаляем старое сообщение
    await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)

    return await send_to_ai(message, state)



async def decode_msg(text):
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


async def download_telegram_posts(channel, limit):
    posts = []
    end = datetime.datetime.now(datetime.timezone.utc)
    end_date = end.date()+ datetime.timedelta(days=1)
    start = end_date - datetime.timedelta(days=limit)
    async with client:
        channel_entity = await client.get_entity(channel)
        async for message in client.iter_messages(channel_entity, offset_date=end):

            if message.date.date() < start:
                break
            if start <= message.date.date() <= end_date and message.text != '':

                msg = await decode_msg(message.text) if message.text else ''

                posts.append({
                    'date': message.date.isoformat(),
                    'text': msg,
                    'link': f'https://t.me/{channel[1:]}/{message.id}'
                    #'views': message.views if hasattr(message, 'views') else None,
                    #'media': bool(message.media),
                })

    return posts


async def send_to_ai(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")
    msg = await message.answer(MESSAGES["loading"]["answer"][lang], reply_markup=ReplyKeyboardRemove())
    await state.update_data(period_message_id=msg.message_id)
    end_date = datetime.datetime.now().date()
    language = "русском" if lang == "ru" else "английском"
    await state.update_data(addition_prompt=PROMPTS["addition"].format(language=language))
    data = await state.get_data()
    try:
        deepseek_response = await fetch_openrouter_response_prompt(data)
        logger_answer.info('USER %s %s %s IMG %s DS_ANSWER %s', message.from_user.id, message.from_user.first_name, message.from_user.username, data.get('need_image'), deepseek_response['answer'])
        start_date = deepseek_response['start_date']
        image = deepseek_response['image']
        image_file = BufferedInputFile(
            file=image,
            filename="generated_image.png"
        )
        days_count = end_date - start_date + datetime.timedelta(days=1)
        is_all_inclusive = deepseek_response['is_all_inclusive']
        print('is_all_inclusive', is_all_inclusive)
        deepseek_response = await simple_html_to_text(deepseek_response['answer'])
        #deepseek_response = deepseek_response['answer']
        #print(deepseek_response)
        logger_answer.info('USER %s %s %s FORMAT_ANSWER %s', message.from_user.id, message.from_user.first_name, message.from_user.username, deepseek_response)

        # Удаляем старое сообщение
        await message.bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
        if not is_all_inclusive and data.get('limit') > days_count.days:
            logger_answer.info('USER %s %s %s LIMIT %s COUNT_DAYS %s', message.from_user.id, message.from_user.first_name,
                               message.from_user.username, data.get('limit'), days_count.days)
            await message.answer(
                MESSAGES["attention"]["period"][lang].format(days=days_count.days),
                parse_mode='Markdown'
            )
        deepseek_response =MESSAGES["title"][lang] + deepseek_response
        if len(deepseek_response) < 980:
            # Создаем BytesIO объект
            if image:
                print('с картинкой')

                #image_buffer = BytesIO(image)
                #image_buffer.name = 'image.png'  # Указываем имя файла

                # Отправляем изображение
                await message.answer_photo(
                    photo=image_file,
                    caption=f"\n{deepseek_response}",
                    parse_mode='HTML',
                    disable_web_page_preview=True,
            )
            else:
                await message.answer(f"\n{deepseek_response}", parse_mode='HTML', disable_web_page_preview=True, )
        else:
            if image:
                answers = await split_by_paragraphs_answer_img(deepseek_response)

                has_image = False
                for ans in answers:
                    if image and not has_image:
                        print('с картинкой')

                        # Отправляем изображение
                        await message.answer_photo(
                            photo=image_file,
                            caption=f"\n{ans}",
                            parse_mode='HTML',
                            disable_web_page_preview=True,
                        )
                        print(ans)
                        has_image = True
                    else:
                        await message.answer(f"\n{ans}", parse_mode='HTML', disable_web_page_preview=True)
            else:
                answers = await split_by_paragraphs_answer(deepseek_response)
                for ans in answers:
                    await message.answer(f"\n{ans}", parse_mode='HTML', disable_web_page_preview= True)

    except Exception as e:
        await msg_delete(msg, state)
        msg = await message.answer(MESSAGES["error"][lang])
        await state.update_data(period_message_id=msg.message_id)
        logger_general.error('USER %s %s %s DS_ERROR %s', message.from_user.id, message.from_user.first_name, message.from_user.username, e)
    await state.set_state(Data.waiting_for_command)





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
async def main(client_bot, bot):
    global client
    client = client_bot
    await client.connect()
    me = await client.get_me()
    print('START_APP', me.first_name)
    await dp.start_polling(bot)


