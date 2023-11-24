import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.middlewares import logging as mw_logging
from aiogram import executor
import sqlite3

API_TOKEN = '6402952763:AAFYTu9BlA4z-isaPIPEAC34mxsicy30ryc'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(mw_logging.LoggingMiddleware())

# Инициализация базы данных SQLite
conn = sqlite3.connect('profiles.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS profiles (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        photo TEXT,
        description TEXT,
        faculty TEXT,
        age INTEGER,
        interests TEXT,
        course INTEGER
    )
''')
conn.commit()

# Инициализация словаря профилей
profiles = {}

# Шаги создания профиля
STEPS = [
    "name",
    "photo",
    "description",
    "faculty",
    "age",
    "interests",
    "course"
]

class ProfileCreationStates:
    START = "start"
    COMPLETED = "completed"

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    profiles[user_id] = {}
    profiles[user_id]['state'] = ProfileCreationStates.START
    await message.answer("Привет! Давайте создадим ваш профиль. Напишите ваше имя:")

@dp.message_handler(lambda message: profiles.get(message.from_user.id, {}).get('state') == ProfileCreationStates.START)
async def process_name(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect('profiles.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE profiles SET name = ? WHERE user_id = ?', (message.text, user_id))
    conn.commit()

    profiles[user_id]['state'] = STEPS[1]
    await bot.send_message(user_id, "Теперь отправьте свою фотографию (это может быть фото профиля).")

@dp.message_handler(lambda message: profiles.get(message.from_user.id, {}).get('state') == STEPS[1])
async def process_photo(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect('profiles.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE profiles SET photo = ? WHERE user_id = ?', (message.text, user_id))
    conn.commit()

    profiles[user_id]['state'] = STEPS[2]
    await bot.send_message(user_id, "Отправьте описание о себе (короткое представление).")

@dp.message_handler(lambda message: profiles.get(message.from_user.id, {}).get('state') == STEPS[2])
async def process_description(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect('profiles.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE profiles SET description = ? WHERE user_id = ?', (message.text, user_id))
    conn.commit()

    profiles[user_id]['state'] = STEPS[3]
    await bot.send_message(user_id, "Выберите ваш факультет:")

@dp.callback_query_handler(lambda c: c.data.startswith('choose_faculty'))
async def choose_faculty_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    chosen_faculty = callback_query.data.split('_')[2]

    conn = sqlite3.connect('profiles.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE profiles SET faculty = ? WHERE user_id = ?', (chosen_faculty, user_id))
    conn.commit()

    profiles[user_id]['state'] = STEPS[4]
    await bot.send_message(user_id, f"Факультет успешно изменен на: {chosen_faculty}")
    await bot.send_message(user_id, "Укажите ваш возраст:")

@dp.message_handler(lambda message: profiles.get(message.from_user.id, {}).get('state') == STEPS[4])
async def process_age(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect('profiles.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE profiles SET age = ? WHERE user_id = ?', (int(message.text), user_id))
    conn.commit()

    profiles[user_id]['state'] = STEPS[5]
    await bot.send_message(user_id, "Расскажите о своих интересах:")

@dp.message_handler(lambda message: profiles.get(message.from_user.id, {}).get('state') == STEPS[5])
async def process_interests(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect('profiles.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE profiles SET interests = ? WHERE user_id = ?', (message.text, user_id))
    conn.commit()

    profiles[user_id]['state'] = STEPS[6]
    await bot.send_message(user_id, "Укажите ваш курс:")

@dp.message_handler(lambda message: profiles.get(message.from_user.id, {}).get('state') == STEPS[6])
async def process_course(message: types.Message):
    user_id = message.from_user.id
    conn = sqlite3.connect('profiles.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE profiles SET course = ? WHERE user_id = ?', (int(message.text), user_id))
    conn.commit()

    profiles[user_id]['state'] = ProfileCreationStates.COMPLETED
    await bot.send_message(user_id, "Профиль успешно создан!")

@dp.callback_query_handler(lambda c: c.data.startswith('view'))
async def view_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    view_type = callback_query.data.split('_')[1]

    if view_type == 'profile':
        profile = profiles.get(user_id, {})
        name = profile.get('name', 'Имя не указано')
        interests = profile.get('interests', 'Интересы не указаны')
        faculty = profile.get('faculty', 'Факультет не указан')
        age = profile.get('age', 'Возраст не указан')
        course = profile.get('course', 'Курс не указан')
        await bot.send_message(user_id, f"Ваш профиль:\nИмя: {name}\nФакультет: {faculty}\nВозраст: {age}\nИнтересы: {interests}\nКурс: {course}")
    elif view_type == 'profiles':
        # Здесь будет функционал для просмотра анкет в базе данных
        pass
    elif view_type == 'edit':
        profiles[user_id]['state'] = ProfileCreationStates.START
        await bot.send_message(user_id, "Изменение профиля. Напишите ваше имя:")

@dp.callback_query_handler(lambda c: c.data.startswith('edit_profile'))
async def edit_profile_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    profiles[user_id]['state'] = ProfileCreationStates.START
    await bot.send_message(user_id, "Изменение профиля. Напишите ваше имя:")

@dp.callback_query_handler(lambda c: c.data.startswith('view_profiles'))
async def view_profiles_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    # Здесь будет функционал для просмотра анкет в базе данных
    pass

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
