import telebot
from telebot import types
import config as cfg
import mesh.mesh as mesh
from time import time

bot = telebot.TeleBot(cfg.token)

answers = {}
times = {}

@bot.message_handler(commands=['start', 'cdz'])
def start(message):
    try:
        if message.text == '/start':
            msg = bot.send_message(message.chat.id,
                                   'Тут должен быть какой-то приветственный текст, но тут его нет, увы.')
            bot.register_next_step_handler(msg, start)
        elif message.text == '/cdz':
            msg = bot.send_message(message.chat.id, 'Введите ссылку на тест')
            bot.register_next_step_handler(msg, answer)
        else:
            msg = bot.send_message(message.chat.id,
                                   "Я вас не понимаю. Воспользуйтесь дуступными командами.",
                                   parse_mode="HTML")
            bot.register_next_step_handler(msg, start)
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка, {}'.format(e))


@bot.message_handler(
    content_types=['animation', 'audio', 'contact', 'dice', 'document', 'location', 'photo', 'poll', 'sticker', 'text',
                   'venue', 'video', 'video_note', 'voice'])
def answer(message: types.Message):
    try:
        kb_answers = types.InlineKeyboardMarkup(row_width=3)
        kb_answers_goto = types.InlineKeyboardButton(text="Показать ответы в боте", callback_data="check " + str(message.from_user.id) + " cdz_answers")
        kb_answers.add(kb_answers_goto)

        answers[message.from_user.id] = []
        print(answers.get(message.from_user.id))
        times[message.from_user.id] = int(time())

        for i in mesh.get_answers(message.text):
            mess = '<b>📄Задание</b>\n<code>└' + str(i[0]) + '</code>\n<b>✏️Ответ</b>\n<code>└' + str(i[1] + '</code>')
            answers[message.from_user.id] += [mess]
            # msg = bot.send_message(message.chat.id, mess, parse_mode="HTML")

        msg = bot.send_message(message.chat.id, 'Ответы сгенерированы за ' + str(round(time() - times.get(message.from_user.id), 2)) + ' секунды', reply_markup=kb_answers)
        bot.register_next_step_handler(msg, start)
    except IndexError:
        bot.send_message(message.chat.id, 'Ошибка, введена некорректная ссылка')
    except Exception as e:
        bot.send_message(message.chat.id, 'Ошибка, {}'.format(e))

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    try:
        if call.message:
            if "cdz_answers" in call.data:
                for i in answers[call.from_user.id]:
                    msg = bot.send_message(chat_id=call.message.chat.id, text=i, parse_mode="HTML")
                bot.register_next_step_handler(msg, start)
    except Exception as e:
        print(repr(e))


bot.polling()
