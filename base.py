# coding: utf8

import logging
import datetime
import os
#from random import randint

import events
import data_control
import language_processing
from configuration import Configuration

import telegram
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater
from telegram import ReplyKeyboardMarkup, KeyboardButton

b1 = KeyboardButton('Добавить событие')
b2 = KeyboardButton('Удалить событие')
b3 = KeyboardButton('Список активных задач')
keyboard = ReplyKeyboardMarkup([[b1, b2], [b3]], one_time_keyboard=1)

mode = ''


def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='Привет! Меня зовут TaskTrack, и я предназначен, '
                                                         'чтобы помочь людям не забыть о важных делах. '
                                                         'Попросите меня напомнить о чем-нибудь!',
                    reply_markup=keyboard)
    logging.info('Command \'start\' invoked by chat id [{0}]'.format(update.message.chat_id))


def help_me(bot, update):
    response = 'Список доступных команд:\n' \
               '/start - Проверка работоспособности бота\n' \
               '/help - Справка по использованию бота\n\n' \
               'Для добавления нового события нажмите на кнопку "Добавить событие", а затем введите:\n' \
               '{Дата события} {Время события} {Описание события}\n' \
               'Например:\n' \
               '01.01.2017 00:00 Поздравить друзей с Новым Годом\n' \
               '< или >\n' \
               '01.01.17 00:00 Поздравить друзей с Новым Годом\n\n' \
               'Также, поддерживается расширенный формат ввода\n' \
               'После указания даты и времени можно указать дату и время напоминания по такому же формату и категорию вида < #{категория} >\n' \
               'Например:\n' \
               '08.02.2017 09:00 01.02.2017 20:00 #работа День Рождения начальника\n\n' \
               'Для удаления события нажмите на кнопку "Удалить событие", а затем введите его описание\n' \
               'Все прошедшие события удаляются автоматически\n' \
               'Бот умеет говорить умные фразы! Пообщайтесь с ним!'
    bot.sendMessage(chat_id=update.message.chat_id, text=response, reply_markup=keyboard)
    logging.info('Command \'help\' invoked by chat id [{0}]'.format(update.message.chat_id))


# Обработка текста
def echo(bot, update):
    """
    Общая обработка текста
    :param bot:
    :param update:
    :return:
    """
    global mode
    utext = update.message.text
    utext_cf = utext.casefold()
    uchat = update.message.chat_id

    # Несколько тестовых проверок на совпадения
    if 'привет'.casefold() in utext_cf:
        bot.sendMessage(chat_id=uchat, text='Привет, друг!')
    elif utext == 'Добавить событие':
        mode = '+'
        response = 'Введите данные о событии в формате: {Дата события} {Время события} {Описание события}\n' \
                   'Для отмены ввода напишите "отмена"'
        bot.sendMessage(chat_id=uchat, text=response)
    elif utext == 'Удалить событие':
        response = 'Введите название события\n' \
                   'Для отмены ввода напишите "отмена"'
        bot.sendMessage(chat_id=uchat, text=response)
        mode = '-'
    elif utext == 'Список активных задач':
        db_control.start()
        chat_id = update.message.chat_id
        event_list = db_control.get_info(chat_id)
        response = 'Список ваших задач:\n'
        response += event_list
        bot.sendMessage(chat_id=update.message.chat_id, text=response, reply_markup=keyboard)
    elif utext == 'отмена':
        mode = ''
        bot.sendMessage(chat_id=uchat, text='Выберете действие', reply_markup=keyboard)
    elif mode == '+':
        lang = language_processing.LanguageProcessing()
        result = lang.analyse(uchat, utext)
        if result:
            # Запись события в базу данных
            db_control.start()
            db_control.add_event(result[0])
            db_control.stop()
            mode = ''
            # Уведомление об успешной записи, требуется доработка формата вывода
            bot.sendMessage(chat_id=uchat,
                            text='Хорошо, я напомню тебе об этом {date}'.format(date=result[0].date_notify),
                            reply_markup=keyboard)
        else:
            mode = ''
            bot.sendMessage(chat_id=uchat, text='Что-то пошло не так, попробуйте еще раз', reply_markup=keyboard)
    elif mode == '-':
        db_control.start()
        msg = db_control.delete_event(utext, uchat)
        db_control.stop()
        mode = ''
        bot.sendMessage(chat_id=uchat,
                        text=msg, reply_markup=keyboard)
    else:
        mode = ''
        response = 'Что-то пошло не так, попробуйте еще раз\n' \
                   'Введите /help для получения справки'
        bot.sendMessage(chat_id=uchat,
                        text=response, reply_markup=keyboard)

        # else:
        # Несколько случайных фраз на случай, если боту нечего ответить
        #     replies = ['Открытый разум подобен крепости, врата которой распахнуты, а стража погрязла в беспутстве',
        #                 'Ничто не истинно, всё дозволено',
        #                'Всё проходит, пройдёт и это. Ничто не проходит',
        #                'Ну, возможно',
        #                'Я в себя, если что-то, но я иду к победе']
        #     bot.sendMessage(chat_id=uchat, text=replies[randint(0, len(replies) - 1)])
        #     bot.sendMessage(chat_id=uchat, text='Введите /help, чтобы получить справку о формате ввода')


def telegram_command_handle(updater):
    """
    Обработка команд из чата Telegram
    :param updater:
    :return:
    """

    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    help_me_handler = CommandHandler('help', help_me)
    dispatcher.add_handler(help_me_handler)

    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)


def terminal_command_handle(db_control):
    while True:
        # Приём команд на выполнение
        response = input('> ').casefold()
        if response == 'stop':
            break
        elif response == 'ping':
            print('pong')
        elif response == 'eadd':
            # Добавляет тестовое событие в базу данных
            e = events.Event(0, datetime.datetime.now(), datetime.datetime.now(), 0, 'datacontrol add')
            db_control.start()
            # Добавляем событие и присваиваем ему id количества имеющихся элементов в базе
            db_control.add_event(e)
            db_control.stop()
        elif response == 'eshow':
            # Выводит события из базы данных на экран
            db_control.start()
            for event in db_control.get_events(False):
                print(event)
            db_control.stop()
        elif response == 'lreq':
            request = input('Enter a message to analyse: ')
            # В тестовом режиме передается wit-токен равный нулю
            lang = language_processing.LanguageProcessing()
            print(lang.analyse(0, request))
        else:
            print('Unknown command')


if __name__ == "__main__":
    # Настройка логирования
    if not os.path.exists('logs/base.log'):
        if not os.path.exists('logs/'):
            os.mkdir('logs/')
        with open('logs/base.log', 'w') as f:
            f.write('[[[ LOGFILE BOUND TO < {} >  MODULE ]]]\n\n'.format(os.path.split(__file__)[1]))

    logging.basicConfig(filename='logs/base.log', format='<%(asctime)s> [%(name)s] [%(levelname)s]: %(message)s',
                        level=logging.INFO)

    # Настройка конфигурирования
    bot_conf = Configuration('conf/access.ini')

    logging.info('Script execution started')
    print('Script started')

    try:
        telegram_token = bot_conf.get_option('Main', 'TelegramToken')
        updater = Updater(token=telegram_token)
    except (telegram.error.InvalidToken, ValueError):
        print('Critical Error > Telegram Access Token is invalid. Terminal halted.\nCheck the configuration file.')
        exit()

    db_control = data_control.DataControl('database.db')

    # Обработка команд из чата Telegram
    telegram_command_handle(updater)
    updater.start_polling()

    logging.info('Started main updater polling')
    print('Running the main script normally')

    # Режим терминала
    terminal_command_handle(db_control)

    # Отключение бота
    logging.info('Stopping main updater polling')
    print('Stopping the main script...')
    updater.stop()
    logging.info('Script execution ended')
    print('Main script stopped')
