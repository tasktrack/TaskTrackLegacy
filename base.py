# coding: utf8

import logging
import datetime
import os
from random import randint

import events
import data_control
import language_processing
from configuration import Configuration

import telegram
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater


def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='Привет! Меня зовут TaskTrack, и я предназначен, '
                                                         'чтобы помочь людям не забыть о важных делах. '
                                                         'Попросите меня напомнить о чем-нибудь!')
    logging.info('Command \'start\' invoked by chat id [{0}]'.format(update.message.chat_id))


def help_me(bot, update):
    response = 'Список доступных команд:\n' \
               '/start - Проверка работоспособности бота\n' \
               '/help - Справка по использованию бота\n\n' \
               'Формат ввода:\n' \
               '< или >\n' \
               'Например:\n' \
               '< или >\n' \
               'Также, поддерживается расширенный формат ввода\n' \
               'После указания даты и времени, можно указать дату и время напоминания по такому же формату ' \
               'важность события по формату < {важность}! > и категорию вида < #{категория} >\n' \
               'Например:\n' \
               'Бот умеет говорить умные фразы! Пообщайтесь с ним!'
    bot.sendMessage(chat_id=update.message.chat_id, text=response)
    logging.info('Command \'help\' invoked by chat id [{0}]'.format(update.message.chat_id))


def test(bot, update):
    '''
    Тестовая команда
    В данный момент создает новую запись в базу данных с параметрами по-умолчанию, chat_id вызвавшего и текстом 'telegram cmd test'
    :param bot:
    :param update:
    :return:
    '''
    # Уникальный id пользователя
    u_chat = int(update.message.chat_id)

    bot.sendMessage(chat_id=u_chat, text="Test executed")
    # Создаем событие для последующей записи в базу данных
    e = events.Event(u_chat, datetime.datetime.now(), datetime.datetime.now(), 0, 'telegram cmd test')
    # Подключаемся к базе данных
    db_control.start()
    # Добавляем запись в базу данных
    db_control.add_event(db_control.get_events_count(), e)
    # Отключаемся от базы данныз
    db_control.stop()
    logging.info('Command \'test\' invoked by chat id [{0}]'.format(update.message.chat_id))


def caps(bot, update, args):
    '''
    Тестовая команда
    В данный момент возвращает UPPERCASE версию присланного боту сообщения
    :param bot:
    :param update:
    :param args:
    :return:
    '''
    text_caps = '%s' % ' '.join(args).upper()
    bot.sendMessage(chat_id=update.message.chat_id, text=text_caps)
    logging.info('Command \'caps\' invoked by char id [{0}]'.format(update.message.chat_id))


# Обработка текста
def echo(bot, update):
    '''
    Общая обработка текста
    :param bot:
    :param update:
    :return:
    '''
    utext = update.message.text
    utext_cf = utext.casefold()
    uchat = update.message.chat_id

    # Несколько тестовых проверок на совпадения
    if 'привет'.casefold() in utext_cf:
        bot.sendMessage(chat_id=uchat, text='Привет, друг!')
    else:
        lang = language_processing.LanguageProcessing(0)
        result = lang.analyse(uchat, utext)
        if result is None:
            # Несколько случайных фраз на случай, если боту нечего ответить
            replies = ['Открытый разум подобен крепости, врата которой распахнуты, а стража погрязла в беспутстве',
                       'Ничто не истинно, всё дозволено',
                       'Всё проходит, пройдёт и это. Ничто не проходит',
                       'Ну, возможно',
                       'Я в себя, если что-то, но я иду к победе']
            bot.sendMessage(chat_id=uchat, text=replies[randint(0, len(replies) - 1)])
            bot.sendMessage(chat_id=uchat, text='Введите /help, чтобы получить справку о формате ввода')
        else:
            # Запись события в базу данных
            db_control.start()
            db_control.add_event(db_control.get_events_count(), result[1])
            db_control.stop()
            # Уведомление об успешной записи, требуется доработка формата вывода
            bot.sendMessage(chat_id=uchat, text='Хорошо, я напомню тебе об этом {date}'.format(date=result[1].date_notify))


def telegram_command_handle(updater, db_control):
    '''
    Обработка команд из чата Telegram
    :param updater:
    :param db_control:
    :return:
    '''

    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    help_me_handler = CommandHandler('help', help_me)
    dispatcher.add_handler(help_me_handler)

    test_handler = CommandHandler('test', test)
    dispatcher.add_handler(test_handler)

    caps_handler = CommandHandler('caps', caps, pass_args=True)
    dispatcher.add_handler(caps_handler)

    echo_handler = MessageHandler(Filters.text, echo)
    dispatcher.add_handler(echo_handler)


def terminal_command_handle(db_control):
    while True:
        # Приём команд на выполнение
        response = input('> ').casefold()
        if response == 'stop': break
        elif response == 'ping': print('pong')
        elif response == 'eadd':
            # Добавляет тестовое событие в базу данных
            e = events.Event(0, datetime.datetime.now(), datetime.datetime.now(), 0, 'datacontrol add')
            db_control.start()
            # Добавляем событие и присваиваем ему id количества имеющихся элементов в базе
            db_control.add_event(db_control.get_events_count(), e)
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
            lang = language_processing.LanguageProcessing(0)
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

    lg_processing = language_processing.LanguageProcessing(bot_conf.get_option('Main', 'WitToken'))
    db_control = data_control.DataControl('database.db')

    # Обработка команд из чата Telegram
    telegram_command_handle(updater, db_control)
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
