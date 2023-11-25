import aiogram
from aiogram import types, Bot
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3
import random
import base64
import io

TOKEN = '6402952763:AAFYTu9BlA4z-isaPIPEAC34mxsicy30ryc'
API_URL = 'https://api.telegram.org/bot' + TOKEN
storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)

# Подключение к базе данных SQLite
conn = sqlite3.connect('profiles.db')
cursor = conn.cursor()

# Создание таблицы профилей, если её нет
cursor.execute('''
    CREATE TABLE IF NOT EXISTS profiles (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    faculty TEXT,
    age TEXT,
    interests TEXT,
    course TEXT,
    photo_path TEXT
)
''')
conn.commit()

# Определение состояний
class ProfileStates(StatesGroup):
    START = State()
    GENDER = State()
    NAME = State()
    FACULTY = State()
    AGE = State()
    INTERESTS = State()
    COURSE = State()
    PHOTO = State()

# Класс профиля
class Profile:
    def __init__(self, user_id, gender=None, name=None, faculty=None, age=None, interests=None, course=None, photo_path=None):
        self.user_id = user_id
        self.gender = gender
        self.name = name
        self.faculty = faculty
        self.age = age
        self.interests = interests
        self.course = course
        self.photo_path = photo_path

# Функция создания клавиатуры
def create_profile_keyboard(existing_profile):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton("Изменить профиль", callback_data="edit_profile"),
                 InlineKeyboardButton("Просмотр анкет", callback_data="view_profiles"))
    # Если профиль существует, добавляем кнопку для просмотра своего профиля
    if existing_profile:
        keyboard.add(InlineKeyboardButton("Просмотр своего профиля", callback_data="view_own_profile"))
    return keyboard

# Функция выполнения SQL-запроса
def execute_query(query, values=None, fetchone=False, fetchall=False):
    cursor.execute(query, values)
    conn.commit()
    if fetchone:
        return cursor.fetchone()
    elif fetchall:
        return cursor.fetchall()

# Функция получения случайного профиля, соответствующего фильтрам
def get_random_profile_with_filters(filters):
    query = 'SELECT * FROM profiles WHERE '
    conditions = []
    values = []
    for key, value in filters.items():
        conditions.append(f'{key} = ?')
        values.append(value)
    query += ' AND '.join(conditions)
    cursor.execute(query, tuple(values))
    profiles = cursor.fetchall()
    if profiles:
        return random.choice(profiles)
    else:
        return None

@dp.message_handler(commands=['start'])
async def start_command_handler(message: types.Message):
    await ProfileStates.GENDER.set()
    user_id = message.from_user.id
    print(f"User {user_id} initiated the /start command.")

    # Проверяем, есть ли профиль пользователя в базе данных
    cursor.execute('SELECT * FROM profiles WHERE user_id = ?', (user_id,))
    existing_profile = cursor.fetchone()
    print(f"Existing profile for user {user_id}: {existing_profile}")

    if existing_profile:
        # Если профиль уже существует, выводим три кнопки
        keyboard = create_profile_keyboard(bool(existing_profile))
        print("Existing profile. Sending keyboard.")
        await message.reply("Выберите действие:", reply_markup=keyboard)
    else:
        # Если профиля нет, предлагаем создать анкету
        await ProfileStates.GENDER.set()
        print("No existing profile. Setting state to GENDER.")
        await message.reply("Создание профиля. Выберите ваш пол:",
                            reply_markup=InlineKeyboardMarkup(
                                inline_keyboard=[
                                    [InlineKeyboardButton("Мужской", callback_data="gender:Male")],
                                    [InlineKeyboardButton("Женский", callback_data="gender:Female")],
                                ]
                            ))

@dp.callback_query_handler(lambda c: c.data.startswith('gender:'), state=ProfileStates.GENDER)
async def process_gender_callback(query: types.CallbackQuery, state: FSMContext):
    # Извлекаем выбранный пол из callback_data
    selected_gender = query.data.split(':')[-1]
    # Сохраняем выбранный пол в состояние
    await state.update_data(gender=selected_gender)
    # Переходим к следующему состоянию
    await ProfileStates.NAME.set()
    # Отправляем сообщение с запросом имени
    await bot.send_message(query.from_user.id, "Напишите ваше имя:")

# Главный обработчик текстовых сообщений
@dp.message_handler(state=ProfileStates.NAME)
async def process_name(message: types.Message, state: FSMContext):
    # Сохраняем имя в состояние
    await state.update_data(name=message.text)
    # Создаем инлайн-клавиатуру с кнопками для каждого факультета
    keyboard = InlineKeyboardMarkup()
    faculties = ["ФАДЭТ", "ФБФВИЖ", "ФПИК", "ИГСН", "ИИМРТ", "ИИГУ", "ИП", "ИПЧ", "ИТМ", "ИХЗЧС", "ИНЭБ", "ИЭТИ", "ФТИ"]
    for faculty in faculties:
        keyboard.add(InlineKeyboardButton(faculty, callback_data=f"faculty:{faculty}"))
    # Отправляем клавиатуру пользователю
    await message.reply("Выберите ваш факультет:", reply_markup=keyboard)
    # Сохраняем список факультетов в состоянии
    await state.update_data(faculties=faculties)
    # Переходим к следующему состоянию
    await ProfileStates.FACULTY.set()

# Обработчик для ввода факультета
@dp.message_handler(state=ProfileStates.FACULTY)
async def process_faculty(message: types.Message, state: FSMContext):
    # Переходим к следующему состоянию
    await ProfileStates.AGE.set()

@dp.callback_query_handler(lambda c: c.data.startswith('faculty:'), state=ProfileStates.FACULTY)
async def process_faculty_callback(query: types.CallbackQuery, state: FSMContext):
    # Извлекаем выбранный факультет из callback_data
    selected_faculty = query.data.split(':')[-1]
    # Сохраняем выбранный факультет в состояние
    await state.update_data(faculty=selected_faculty)
    # Переходим к следующему состоянию
    await ProfileStates.AGE.set()
    # Отправляем сообщение с запросом возраста
    await bot.send_message(query.from_user.id, "Напишите ваш возраст:")

# Обработчик для ввода возраста
@dp.message_handler(state=ProfileStates.AGE)
async def process_age(message: types.Message, state: FSMContext):
    # Сохраняем возраст в состояние
    await state.update_data(age=message.text)
    # Переходим к следующему состоянию
    await ProfileStates.INTERESTS.set()
    # Запрашиваем интересы
    await message.reply("Напишите ваши интересы:")
    print("Age processed successfully.")

# Обработчик для ввода интересов
@dp.message_handler(state=ProfileStates.INTERESTS)
async def process_interests(message: types.Message, state: FSMContext):
    # Сохраняем интересы в состояние
    await state.update_data(interests=message.text)
    # Переходим к следующему состоянию
    await ProfileStates.PHOTO.set()  # Исправляем переход к состоянию PHOTO
    # Запрашиваем фотографию
    await message.reply("Пришлите вашу фотографию или укажите путь к файлу:")
    print("Interests processed successfully.")

@dp.message_handler(content_types=['photo'], state=ProfileStates.PHOTO)
async def process_photo(message: types.Message, state: FSMContext):
    await state.update_data(photo=message.photo[0].file_id)
    await ProfileStates.COURSE.set()
    await message.reply("Напишите ваш курс:")

# Обработчик для ввода курса
@dp.message_handler(state=ProfileStates.COURSE)
async def process_course(message: types.Message, state: FSMContext):
    # Сохраняем курс в состояние
    await state.update_data(course=message.text)

    # Создаем профиль
    user_id = message.from_user.id
    data = await state.get_data()
    print(data)
    photo_file_id = data['photo']
    profile = Profile(user_id, gender=data['gender'], name=data['name'], faculty=data['faculty'],
                      age=data['age'], interests=data['interests'], course=data['course'],
                      photo_path=photo_file_id)

    print("Profile created successfully.")

    # Проверка, существует ли пользователь уже в базе данных
    existing_profile = execute_query('SELECT * FROM profiles WHERE user_id = ?', (user_id,), fetchone=True)
    print(f"Existing profile: {existing_profile}")

    try:
        if existing_profile:
            # Если пользователь уже существует, обновляем профиль
            execute_query('UPDATE profiles SET name=?, faculty=?, age=?, interests=?, course=?, photo_path=? WHERE user_id=?',
                          (profile.name, profile.faculty, profile.age, profile.interests, profile.course, profile.photo_path, user_id))
        else:
            # Если пользователь не существует, вставляем новый профиль
            execute_query('INSERT INTO profiles VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                          (user_id, profile.name, profile.faculty, profile.age, profile.interests, profile.course,
                           profile.photo_path, profile.gender))

        print("Profile updated/inserted successfully.")

        # Завершаем состояние ProfileStates.START
        await ProfileStates.START.finish()

        # Завершаем состояние ProfileStates.COURSE
        await state.finish()

        # Отправляем сообщение о успешном создании профиля
        keyboard = create_profile_keyboard(existing_profile=bool(existing_profile))
        await message.reply("Профиль успешно создан. Теперь вы можете просмотреть его.",
                            reply_markup=keyboard)

    except Exception as e:
        print(f"An error occurred: {e}")
        await message.reply("Произошла ошибка при обработке профиля. Пожалуйста, попробуйте еще раз.")
# Обработчик для просмотра профиля
@dp.callback_query_handler(lambda c: c.data == 'view_own_profile', state='*')
async def view_own_profile_callback(query: types.CallbackQuery, state: FSMContext):
    # Ваша логика обработки запроса на просмотр своего профиля
    user_id = query.from_user.id
    print(f"User {user_id} initiated the view_own_profile callback.")

    # Получаем профиль из базы данных
    profile = execute_query('SELECT * FROM profiles WHERE user_id = ?', (user_id,), fetchone=True)

    if profile:
        print("Profile found.")
        # Формируем сообщение с параметрами профиля
        profile_message = (
            f"Имя: {profile[1]}\n"
            f"Гендер: {profile[6]}\n"
            f"Возраст: {profile[3]}\n"
            f"Факультет: {profile[2]}\n"
            f"Курс: {profile[5]}\n"
            f"Интересы: {profile[4]}\n"
        )

        # Декодируем base64 в байты
        photo_bytes = base64.b64decode(profile[7])

        # Отправляем фотографию профиля
        await bot.send_photo(chat_id=query.from_user.id, photo=types.InputFile(io.BytesIO(photo_bytes)), caption=profile_message)

        print("Profile photo sent.")

        # Отправляем клавиатуру с кнопками "Изменить профиль" и "Просмотр анкет"
        keyboard = create_profile_keyboard(existing_profile=True)
        await bot.send_message(query.from_user.id, "Выберите действие:", reply_markup=keyboard)
        print("Keyboard sent.")
    else:
        # Если профиль не найден, отправляем сообщение об ошибке
        await bot.send_message(query.from_user.id, "Профиль не найден.")
        print("Profile not found.")

# Обработчик для просмотра анкет
@dp.callback_query_handler(lambda c: c.data == 'view_profiles', state='*')
async def view_profiles_callback(query: types.CallbackQuery, state: FSMContext):
    user_id = query.from_user.id
    print(f"User {user_id} initiated the view_profiles callback.")

    # Получаем все профили из базы данных
    profiles = execute_query('SELECT * FROM profiles', fetchall=True)

    if profiles:
        # Отправляем каждый профиль пользователю
        for profile in profiles:
            # Формируем сообщение с параметрами профиля
            profile_message = (
                f"Имя: {profile[1]}\n"
                f"Гендер: {profile[6]}\n"
                f"Возраст: {profile[3]}\n"
                f"Факультет: {profile[2]}\n"
                f"Курс: {profile[5]}\n"
                f"Интересы: {profile[4]}\n"
            )

            # Отправляем сообщение с параметрами профиля и фотографией
            await bot.send_photo(query.from_user.id, profile[7], caption=profile_message)

        # Отправляем клавиатуру с кнопками "Изменить профиль" и "Просмотр анкет"
        keyboard = create_profile_keyboard(existing_profile=True)
        await bot.send_message(query.from_user.id, "Выберите действие:", reply_markup=keyboard)
    else:
        # Если профили не найдены, отправляем сообщение об ошибке
        await bot.send_message(query.from_user.id, "Профили не найдены.")
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
