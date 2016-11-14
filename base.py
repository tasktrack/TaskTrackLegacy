# coding: utf8

import logging
import datetime
import events
import data_control
import event_map
import language_processing
from random import randint

logging.basicConfig(filename='logs/base.log', format='<%(asctime)s> [%(name)s] [%(levelname)s]: %(message)s',
                    level=logging.INFO)

from configuration import Configuration
import telegram

def telegram_command_handle(updater, db_control):
    '''
    Обработка команд из чата Telegram
    :param updater:
    :param db_control:
    :return:
    '''

    dispatcher = updater.dispatcher

    from telegram.ext import CommandHandler

    def start(bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text="Hello world.")
        logging.info('Command \'start\' invoked by chat id [{0}]'.format(update.message.chat_id))

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    def help_me(bot, update):
        response = 'Список доступных команд:\n' \
                   '/start - Проверка работоспособности бота\n' \
                   '/help - Справка по использованию бота\n\n' \
                   'Формат ввода:\n' \
                   'dd.mm.yy hh:mm Описание события\n' \
                   '< или >\n' \
                   'dd.mm.yyyy hh:mm Описание события\n\n' \
                   'Например:\n' \
                   '01.01.2001 00:00 Поздравить друзей с Новым Годом!\n' \
                   '< или >\n' \
                   '01.01.01 00:00 Поздравть друзей с Новым Годом!\n\n' \
                   'Бот умеет говорить умные фразы! Пообщайтесь с ним!'
        bot.sendMessage(chat_id=update.message.chat_id, text=response)
        logging.info('Command \'help\' invoked by chat id [{0}]'.format(update.message.chat_id))

    help_me_handler = CommandHandler('help', help_me)
    dispatcher.add_handler(help_me_handler)

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

    test_handler = CommandHandler('test', test)
    dispatcher.add_handler(test_handler)

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

    caps_handler = CommandHandler('caps', caps, pass_args=True)
    dispatcher.add_handler(caps_handler)

    # Обработка текста
    def echo(bot, update):
        '''
        Общая обработка текста
        :param bot:
        :param update:
        :return:
        '''
        # Текст, поступивший боту
        utext = update.message.text
        # Текст без учета заглавных букв
        utext_cf = utext.casefold()
        # Уникальный ID пользователя
        uchat = update.message.chat_id
        # Несколько тестовых проверок на совпадения
        if 'привет'.casefold() in utext_cf:
            bot.sendMessage(chat_id=uchat, text='Привет, друг!')
        elif 'напомни'.casefold() in utext_cf:
            bot.sendMessage(chat_id=uchat, text='Разве мы уже на \"ты\"? ;)')
            days = ['понедельник', 'вторник', 'сред', 'четверг', 'пятниц', 'суббот', 'воскресенье']
            days_match = []

            for day in days:
                if day in utext_cf:
                    if day == 'сред':
                        day = 'cреду'
                    elif day == 'пятниц':
                        day = 'пятницу'
                    elif day == 'суббот':
                        day = 'субботу'
                    days_match.append(day)
            if len(days_match):
                dayformat = ', '.join(days_match[:-1]) + ' и %s' % days_match[-1]
                bot.sendMessage(chat_id=uchat, text='Хорошо, я напомню тебе об этом в %s' % dayformat)
        else:
            lang = language_processing.LanguageProcessing()
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
                db_control.add_event(db_control.get_events_count(), result)
                db_control.stop()
                # Уведомление об успешной записи, требуется доработка формата вывода
                bot.sendMessage(chat_id=uchat, text='Хорошо, я напомню тебе об этом {date}'.format(date=result.date_notify))

    from telegram.ext import MessageHandler, Filters
    echo_handler = MessageHandler([Filters.text], echo)
    dispatcher.add_handler(echo_handler)


def terminal_command_handle(db_control, ev_map):
    while True:
        # Приём команд на выполнение
        response = input('> ').casefold()
        if response == 'stop': break
        elif response == 'say hi': print('Oh hi there')
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
        elif response == 'emap':
            e = events.Event(0, datetime.datetime.now(), datetime.datetime.now(), 0, 'eventmap test')
            db_control.start()
            ev_map = event_map.EventMap(db_control.get_events())
            db_control.stop()
            print(ev_map)
            print('Next event is:\n{event}'.format(event=ev_map.next_event))
        elif response == 'lreq':
            request = input('Enter a message to analyse: ')
            lang = language_processing.LanguageProcessing()
            print(lang.analyse(0, request))
        else:
            print('Unknown command')

if __name__ == "__main__":
    # Настойка конфигурирования
    bot_conf = Configuration('conf/access.ini')
    # Настройка логирования
    logging.basicConfig(filename='logs/base.log', format='<%(asctime)s> [%(name)s] [%(levelname)s]: %(message)s',
                        level=logging.INFO)

    # Сообщение в лог о старте работы скрипта
    logging.info('Script execution started')
    print('Script started')

    from telegram.ext import Updater

    try:
        updater = Updater(token=bot_conf.get_option('Main', 'TelegramToken'))
    except telegram.error.InvalidToken:
        print('Critical Error > Telegram Access Token is invalid. Terminal halted.\nCheck the configuration file')
        exit()

    # Создание экземпляра контролирующего обработку речи
    # lg_processing = language_processing.LanguageProcessing()
    # lg_processing.send("Напомни мне купить батон")

    # Создание экземпляра контролирующего работу с базой данных класса
    db_control = data_control.DataControl('database.db')

    # Подключение к базе данных и создание первичной карты дня
    db_control.start()
    ev_map = event_map.EventMap(db_control.get_events())
    db_control.stop()

    # Обработка команд из чата Telegram
    telegram_command_handle(updater, db_control)

    # Начало обработки запросов
    updater.start_polling()
    logging.info('Started main updater polling')
    print('Running the main script normally')

    # Режим терминала
    terminal_command_handle(db_control, ev_map)

    # Отключение бота
    logging.info('Stopping main updater polling')
    print('Stopping the main script...')
    updater.stop()
    logging.info('Script execution ended')
    print('Main script stopped')
