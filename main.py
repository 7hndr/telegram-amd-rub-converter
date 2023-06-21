import os
from dotenv import load_dotenv
import telebot
from telebot import types
import requests

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CURRENCY_TOKEN = os.environ.get("CURRENCY_API_KEY")
URL = 'https://openexchangerates.org/api/latest.json'

bot = telebot.TeleBot(BOT_TOKEN)


def convert_currency(amount, source_currency, target_currency):
    params = {
        'app_id': CURRENCY_TOKEN
    }

    response = requests.get(URL, params=params)

    if response.status_code == 200:
        rates = response.json()['rates']
        target = float(rates[f'{target_currency}'])
        source = float(rates[f'{source_currency}'])

        return round(target / source, 2)
    else:
        return None


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.InlineKeyboardMarkup()
    item_get = types.InlineKeyboardButton(text='🏦 Get rate', callback_data='get')
    item_calc = types.InlineKeyboardButton(text='↔️ Convert currency', callback_data='convert')

    markup.add(item_get,
               item_calc)
    bot.send_message(message.chat.id, '👉 Please choose an action', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'get':
        rate = convert_currency(1000, 'RUB', 'AMD')
        bot.send_message(call.message.chat.id, f"AMD/RUB rate: {rate}")
        welcome(call.message)
        pass
    elif call.data == 'convert':
        markup = types.InlineKeyboardMarkup()
        amd_to_rub = types.InlineKeyboardButton(text='RUB → AMD', callback_data='to_amd')
        rub_to_amd = types.InlineKeyboardButton(text='AMD → RUB', callback_data='to_rub')

        markup.add(amd_to_rub,
                   rub_to_amd)

        bot.send_message(call.message.chat.id, 'Choose a flow 👇', reply_markup=markup)
        pass
    elif call.data == 'to_rub':
        bot.send_message(call.message.chat.id, 'Please enter amount in AMD')
        bot.register_next_step_handler(call.message, convert_specific, call.data)
    if call.data == 'to_amd':
        bot.send_message(call.message.chat.id, 'Please enter amount in RUB')
        bot.register_next_step_handler(call.message, convert_specific, call.data)


def convert_specific(message, arg):
    amount = message.text
    if amount.isdigit():
        amount = int(amount)
        rate = convert_currency(1000, 'RUB', 'AMD')

        if arg == 'to_rub':
            res = round(amount / rate, 2)
            bot.send_message(message.chat.id, f'💵 Converted sum: {res} RUB')
            welcome(message)
        elif arg == 'to_amd':
            res = round(amount * rate, 2)
            bot.send_message(message.chat.id, f'💵 Converted sum: {res} AMD')
            welcome(message)

    else:
        bot.send_message(message.chat.id, "😬 Please enter a number")
        bot.register_next_step_handler(message, convert_specific, arg)



@bot.message_handler(content_types=['text'])
def convert(message):
    welcome(message)


print('bot started')
bot.enable_save_next_step_handlers(delay=1)
bot.load_next_step_handlers()
bot.polling(none_stop=True)
