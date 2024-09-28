import telebot
from telebot import types
import random
import json
import os

# Проверка на наличие конфигурационного файла
config_file_path = 'config.json'
if not os.path.exists(config_file_path):
    raise FileNotFoundError(f"Конфигурационный файл '{config_file_path}' не найден.")

# Загрузка конфигурации из файла
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

# Получение токена из конфигурационного файла
TOKEN = config.get('Telegram', {}).get('Token')
if not TOKEN:
    raise ValueError("Токен не найден в конфигурационном файле.")

bot = telebot.TeleBot(TOKEN)

# Словарь для хранения статистики пользователей
user_stats = {}

def initialize_user_stats(user_id):
    if user_id not in user_stats:
        user_stats[user_id] = {
            'wins': 0,
            'losses': 0,
            'draws': 0,
            'choices': {'🪨 Камень': 0, '✂️ Ножницы': 0, '📄 Бумага': 0}
        }

# Функция для обработки команды /start
@bot.message_handler(commands=['start'])

# Обработчик команды /start. Отправляет приветственное сообщение и отображает кнопки для игры
def send_welcome(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton('Начать играть'),
        types.KeyboardButton('📊 Профиль'),
        types.KeyboardButton('ℹ️ Информация'),
        types.KeyboardButton('💬 Поддержка')
    )
    bot.send_message(
        message.chat.id,
        "Добро пожаловать! Выберите одну из опций ниже:",
        reply_markup=keyboard
    )

# Функция для обработки команды /profile
@bot.message_handler(commands=['profile'])

# Обработчик команды /profile. Отправляет профиль пользователя
def send_profile_command(message):
    send_profile(message.chat.id)

# Отправляет профиль пользователя
def send_profile(user_id):
    initialize_user_stats(user_id)
    stats = user_stats[user_id]
    profile_message = (
        f"📊 Ваш профиль:\n"
        f"Победы: {stats['wins']}\n"
        f"Поражения: {stats['losses']}\n"
        f"Ничьи: {stats['draws']}\n"
        f"Выборы: Камень - {stats['choices']['🪨 Камень']}, Ножницы - {stats['choices']['✂️ Ножницы']}, Бумага - {stats['choices']['📄 Бумага']}"
    )
    bot.send_message(user_id, profile_message)

# Обработчик инлайн-кнопок
@bot.callback_query_handler(func=lambda call: call.data in ['🪨 Камень', '✂️ Ножницы', '📄 Бумага'])

# Обрабатывает выбор пользователя и отвечает в соответствии с результатом игры
def handle_game_choice(call):
    user_id = call.message.chat.id
    user_choice = call.data
    bot_choice = random.choice(['🪨 Камень', '✂️ Ножницы', '📄 Бумага'])

    initialize_user_stats(user_id)
    user_stats[user_id]['choices'][user_choice] += 1

    # Определяем результат игры
    if user_choice == bot_choice:
        user_stats[user_id]['draws'] += 1
        response = f"Вы выбрали {user_choice}, а я выбрал {bot_choice}. Ничья!"
    elif (user_choice == '🪨 Камень' and bot_choice == '✂️ Ножницы') or \
         (user_choice == '✂️ Ножницы' and bot_choice == '📄 Бумага') or \
         (user_choice == '📄 Бумага' and bot_choice == '🪨 Камень'):
        user_stats[user_id]['wins'] += 1
        response = f"Вы выбрали {user_choice}, а я выбрал {bot_choice}. Вы победили! 🎉"
    else:
        user_stats[user_id]['losses'] += 1
        response = f"Вы выбрали {user_choice}, а я выбрал {bot_choice}. Я победил! 😄"

    # Создаем инлайн-кнопки для нового выбора
    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(
        types.InlineKeyboardButton('🪨 Камень', callback_data='🪨 Камень'),
        types.InlineKeyboardButton('✂️ Ножницы', callback_data='✂️ Ножницы'),
        types.InlineKeyboardButton('📄 Бумага', callback_data='📄 Бумага')
    )

    # Редактируем предыдущее сообщение, чтобы отобразить результат и новые инлайн-кнопки
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=response,
        reply_markup=inline_keyboard
    )

# Функция для обработки всех текстовых сообщений
@bot.message_handler(func=lambda msg: True)

# Обработчик всех текстовых сообщений. Определяет выбор пользователя и отвечает в соответствии с результатом игры
def handle_text(message):
    user_id = message.chat.id
    initialize_user_stats(user_id)
    user_choice = message.text

    if user_choice == '📊 Профиль':
        send_profile(user_id)
        return
    elif user_choice == 'ℹ️ Информация':
        send_info(user_id)
        return
    elif user_choice == '💬 Поддержка':
        send_support(user_id)
        return
    elif user_choice == 'Начать играть':
        start_game(user_id)
        return

    bot.send_message(
        message.chat.id,
        "Пожалуйста, используйте меню для выбора опции."
    )

# Начинает игру, отправляя сообщение с инлайн-кнопками для выбора
def start_game(user_id):
    inline_keyboard = types.InlineKeyboardMarkup()
    inline_keyboard.add(
        types.InlineKeyboardButton('🪨 Камень', callback_data='🪨 Камень'),
        types.InlineKeyboardButton('✂️ Ножницы', callback_data='✂️ Ножницы'),
        types.InlineKeyboardButton('📄 Бумага', callback_data='📄 Бумага')
    )
    bot.send_message(
        user_id,
        "Выберите один из вариантов:",
        reply_markup=inline_keyboard
    )

# Отправляет информацию о том, как играть
def send_info(user_id):
    info_message = (
        "Информация о игре:\n"
        "Камень, Ножницы, Бумага - классическая игра.\n"
        "Правила:\n"
        "1. Камень побеждает Ножницы\n"
        "2. Ножницы побеждают Бумагу\n"
        "3. Бумага побеждает Камень\n"
        "Выберите один из вариантов, чтобы сыграть."
    )
    bot.send_message(user_id, info_message)

# Отправляет информацию о поддержке
def send_support(user_id):
    support_message = "Для поддержки посетите мой профиль GitHub: https://github.com/geniuszly"
    bot.send_message(user_id, support_message, disable_web_page_preview=True)

# Запуск бота
bot.polling(none_stop=True)
