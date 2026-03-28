import telebot
import sqlite3
import time
from datetime import datetime, timedelta
from telebot import types

bot = telebot.TeleBot('8460210534:AAH-4eVx_jp4951Z5y6KV7O8OnlM-r3BNXE')

def init_db():
    conn = sqlite3.connect('subs.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (user_id INTEGER PRIMARY KEY, expiry TEXT)''')
    conn.commit()
    conn.close()

def has_active_sub(user_id):
    conn = sqlite3.connect('subs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT expiry FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        expiry_date = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
        if expiry_date > datetime.now():
            return True
    return False

def add_subscription(user_id):
    expiry_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect('subs.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO users (user_id, expiry) VALUES (?, ?)", (user_id, expiry_date))
    conn.commit()
    conn.close()

@bot.message_handler(commands=['start'])
def start(message):
    if has_active_sub(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Стиралка", callback_data="stiralka"))
        bot.send_message(message.chat.id, "Не занимайте хуйней купи подписку в шторм снос\nhttps://stormsnos.fun/links", reply_markup=markup)
    else:
        bot.send_invoice(
            message.chat.id,
            title="Доступ к стиралкам на день",
            description="Активация доступа на 24 часа",
            provider_token="",
            currency="XTR",
            prices=[types.LabeledPrice(label="Доступ на день", amount=20)],
            payload="day_sub"
        )

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    add_subscription(message.from_user.id)
    bot.send_message(message.chat.id, "псë")

@bot.callback_query_handler(func=lambda call: call.data == "stiralka")
def handle_stiralka(call):
    if has_active_sub(call.from_user.id):
        msg = bot.send_message(call.message.chat.id, "Пиши юзернейм жертвы")
        bot.register_next_step_handler(msg, process_victim)
    else:
        bot.answer_callback_query(call.id, "Подписка закончилась")
        start(call.message)

def process_victim(message):
    if not has_active_sub(message.from_user.id):
        bot.send_message(message.chat.id, "Подписка закончилась")
        return
    
    status_msg = bot.send_message(message.chat.id, "Отправка жалоб")
    time.sleep(7)
    bot.edit_message_text("жалобы отправлены", message.chat.id, status_msg.message_id)

if __name__ == '__main__':
    init_db()
    bot.infinity_polling()
