import sqlite3
import telebot
from telebot import types

# Замените 'YOUR_BOT_TOKEN' на токен, который вы получили от BotFather
TOKEN = '6855146133:AAEk0TXm1iV7Fntv7k0m61dMhPIR1MwSjNI'
YOUR_ADMIN_USER_ID = 1611801020  # Замените на ваш реальный идентификатор пользователя с правами администратора

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Обработчики команд
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Добро пожаловать! Пожалуйста, введите ваш город:')
    bot.register_next_step_handler(message, collect_city)

def collect_city(message):
    user_state = {'step': 2, 'city': message.text}
    bot.send_message(message.chat.id, 'Пожалуйста, введите вашу школу:')
    bot.register_next_step_handler(message, collect_school, user_state)

def collect_school(message, user_state):
    user_state['school'] = message.text
    user_state['step'] = 3
    bot.send_message(message.chat.id, 'Пожалуйста, введите описание:')
    bot.register_next_step_handler(message, collect_description, user_state)

def collect_description(message, user_state):
    city = user_state['city']
    school = user_state['school']
    description = message.text

    # Сохранение данных в базу данных SQLite
    with sqlite3.connect('user_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO user_data (city, school, description)
            VALUES (?, ?, ?)
        ''', (city, school, description))
        conn.commit()

    bot.send_message(message.chat.id, 'Спасибо! Ваши данные сохранены.')

# Админская команда для просмотра и удаления записей
@bot.message_handler(commands=['admin'])
def admin_menu(message):
    if message.from_user.id == YOUR_ADMIN_USER_ID:
        markup = types.InlineKeyboardMarkup()
        view_button = types.InlineKeyboardButton('Просмотреть записи', callback_data='view_entries')
        delete_button = types.InlineKeyboardButton('Удалить запись', callback_data='delete_entry')
        markup.add(view_button, delete_button)

        bot.send_message(message.chat.id, 'Меню администратора:', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'У вас нет прав доступа к администраторскому меню.')

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    if call.data == 'view_entries':
        view_entries(call.message)
    elif call.data == 'delete_entry':
        delete_entry(call.message)
    elif call.data.startswith('confirm_delete_'):
        entry_id = call.data.split('_')[-1]
        with sqlite3.connect('user_data.db') as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM user_data WHERE id = ?', (entry_id,))
            conn.commit()

        bot.send_message(call.message.chat.id, f'Запись с ID {entry_id} удалена.')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Удаление подтверждено.')
    elif call.data == 'cancel_delete':
        bot.send_message(call.message.chat.id, 'Удаление отменено.')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Удаление отменено.')
    elif call.data.startswith('view_entry_'):
        entry_id = call.data.split('_')[-1]
        view_entry(call.message, entry_id)

# Добавить функцию просмотра записи
def view_entry(message, entry_id):
    with sqlite3.connect('user_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_data WHERE id = ?', (entry_id,))
        entry = cursor.fetchone()

        if entry:
            entry_text = f'ID записи: {entry[0]}\nГород: {entry[1]}\nШкола: {entry[2]}\nОписание: {entry[3]}'
            bot.send_message(message.chat.id, entry_text)
        else:
            bot.send_message(message.chat.id, f'Запись с ID {entry_id} не найдена.')

# Добавить функцию просмотра всех записей
def view_entries(message):
    with sqlite3.connect('user_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_data')
        entries = cursor.fetchall()

        if entries:
            for entry in entries:
                entry_text = f'ID записи: {entry[0]}\nГород: {entry[1]}\nШкола: {entry[2]}\nОписание: {entry[3]}'
                bot.send_message(message.chat.id, entry_text)
        else:
            bot.send_message(message.chat.id, 'Записи не найдены.')

# Добавить функцию удаления записи
def delete_entry(message):
    bot.send_message(message.chat.id, 'Пожалуйста, введите ID записи, которую вы хотите удалить:')
    bot.register_next_step_handler(message, confirm_delete)

# Добавить функцию подтверждения удаления
def confirm_delete(message):
    entry_id = message.text
    with sqlite3.connect('user_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM user_data WHERE id = ?', (entry_id,))
        entry = cursor.fetchone()

        if entry:
            entry_text = f'Вы уверены, что хотите удалить следующую запись?\n' \
                          f'ID записи: {entry[0]}\nГород: {entry[1]}\nШкола: {entry[2]}\nОписание: {entry[3]}'
            entry_markup = confirm_deletion_markup(entry_id)
            bot.send_message(message.chat.id, entry_text, reply_markup=entry_markup)
        else:
            bot.send_message(message.chat.id, f'Запись с ID {entry_id} не найдена.')

# Добавить функцию формирования клавиатуры подтверждения удаления
def confirm_deletion_markup(entry_id):
    markup = types.InlineKeyboardMarkup()
    yes_button = types.InlineKeyboardButton('Да', callback_data=f'confirm_delete_{entry_id}')
    no_button = types.InlineKeyboardButton('Нет', callback_data='cancel_delete')
    markup.add(yes_button, no_button)
    return markup

# Обработка других сообщений
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    bot.send_message(message.chat.id, "Я простой бот. Пожалуйста, используйте /start, чтобы предоставить свои данные.")

# Запуск бота
bot.polling(none_stop=True, interval=0)
