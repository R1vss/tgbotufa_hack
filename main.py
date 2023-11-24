import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import executor

API_TOKEN = 'secret'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

profiles = {}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_user.id
    if user_id not in profiles:
        profiles[user_id] = {}
        await message.answer("Привет! Давайте создадим ваш профиль. Используйте кнопки ниже:")
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Изменить фото", callback_data='edit_photo'))
        keyboard.add(InlineKeyboardButton("Изменить описание", callback_data='edit_description'))
        keyboard.add(InlineKeyboardButton("Выбрать факультет", callback_data='choose_faculty'))
        keyboard.add(InlineKeyboardButton("Выбрать возраст", callback_data='choose_age'))
        keyboard.add(InlineKeyboardButton("Выбрать интересы", callback_data='choose_interests'))
        keyboard.add(InlineKeyboardButton("Выбрать курс", callback_data='choose_course'))
        await message.answer("Выберите действие:", reply_markup=keyboard)
    else:
        await message.answer("Ваш профиль уже создан. Используйте кнопки ниже:")
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Просмотреть свой профиль", callback_data='view_profile'))
        keyboard.add(InlineKeyboardButton("Изменить фото", callback_data='edit_photo'))
        keyboard.add(InlineKeyboardButton("Изменить описание", callback_data='edit_description'))
        keyboard.add(InlineKeyboardButton("Выбрать факультет", callback_data='choose_faculty'))
        keyboard.add(InlineKeyboardButton("Выбрать возраст", callback_data='choose_age'))
        keyboard.add(InlineKeyboardButton("Выбрать интересы", callback_data='choose_interests'))
        keyboard.add(InlineKeyboardButton("Выбрать курс", callback_data='choose_course'))
        await message.answer("Выберите действие:", reply_markup=keyboard)

# Добавим обработчики для каждой кнопки
@dp.callback_query_handler(lambda c: c.data.startswith('edit'))
async def edit_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    edit_type = callback_query.data.split('_')[1]

    if edit_type == 'photo':
        await bot.send_message(user_id, "Здесь будет функционал для изменения фото.")
    elif edit_type == 'description':
        await bot.send_message(user_id, "Здесь будет функционал для изменения описания.")
    elif edit_type == 'faculty':
        await bot.send_message(user_id, "Здесь будет функционал для выбора факультета.")
    elif edit_type == 'age':
        await bot.send_message(user_id, "Здесь будет функционал для выбора возраста.")
    elif edit_type == 'interests':
        await bot.send_message(user_id, "Здесь будет функционал для выбора интересов.")
    elif edit_type == 'course':
        await bot.send_message(user_id, "Здесь будет функционал для выбора курса.")

@dp.callback_query_handler(lambda c: c.data.startswith('view'))
async def view_callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    view_type = callback_query.data.split('_')[1]

    if view_type == 'profile':
        profile = profiles[user_id]
        name = profile.get('name', 'Имя не указано')
        interests = profile.get('interests', 'Интересы не указаны')
        faculty = profile.get('faculty', 'Факультет не указан')
        age = profile.get('age', 'Возраст не указан')
        course = profile.get('course', 'Курс не указан')
        await bot.send_message(user_id, f"Ваш профиль:\nИмя: {name}\nФакультет: {faculty}\nВозраст: {age}\nИнтересы: {interests}\nКурс: {course}")
    elif view_type == 'all_profiles':
        await bot.send_message(user_id, "Здесь будет функционал для просмотра анкет в базе данных.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)