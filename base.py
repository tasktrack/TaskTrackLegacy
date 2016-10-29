# coding: utf8

import logging
import datetime
import events
import data_control
import event_map


logging.basicConfig(filename='logs/base.log', format='<%(asctime)s> [%(name)s] [%(levelname)s]: %(message)s',
                    level=logging.INFO)


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

    start_handler = CommandHandler('test', test)
    dispatcher.add_handler(start_handler)

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
            bot.sendMessage(chat_id=uchat, text='Не знаю, что сказать, поэтому просто предразню :Р')
            bot.sendMessage(chat_id=uchat, text=utext)

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
        else:
            print('Unknown command')

if __name__ == "__main__":
    # Сообщение в лог о старте работы скрипта
    logging.info('Script execution started')
    print('Script started')

    from telegram.ext import Updater

    updater = Updater(token='289680799:AAHDpjJLcqBF0Flcybl3GyE8wTpdfiZjM4Y')

    # Создание экземпляра контролирующего работу с базой данных класса
    db_control = data_control.DataControl('database.db')

    # Комментарий для теста

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
