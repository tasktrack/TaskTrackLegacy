# coding: utf8

import logging
import datetime
import os
# from random import randint

import events
import data_control
import language_processing
from configuration import Configuration

import telegram
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, Job

b1 = KeyboardButton('Добавить событие')
b2 = KeyboardButton('Удалить событие')
b3 = KeyboardButton('Список активных задач')
b4 = KeyboardButton('Справка')

keyboard = ReplyKeyboardMarkup([[b1], [b2], [b3], [b4]], one_time_keyboard=1)

mode = ''


def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text='Привет! Меня зовут TaskTrack, и я предназначен, '
                         'чтобы помочь людям не забыть о важных делах. '
                         'Я сразу перейду на "ты", чтобы создать непринужденную атмосферу, ладно? '
                         'Попроси меня напомнить о чем-нибудь!',
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
               'После указания даты и времени можно указать дату и время ' \
               'напоминания по такому же формату и категорию вида < #{категория} >\n' \
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
    if 'привет' in utext_cf:
        bot.sendMessage(chat_id=uchat, text='Привет, друг! Хочешь кофейку, или секретное задание?',
                        reply_markup=keyboard)
    elif utext_cf == 'справка':
        response = 'Список доступных команд:\n' \
                   '/start - Проверка работоспособности бота\n' \
                   '/help - Справка по использованию бота\n\n' \
                   'Для добавления нового события нажмите на кнопку "Добавить событие", а затем введите информацию о нем в формате:\n' \
                   '{Дата события} {Время события} {Описание события}\n' \
                   'Например:\n' \
                   '01.01.2017 00:00 Поздравить друзей с Новым Годом\n' \
                   '< или >\n' \
                   '01.01.17 00:00 Поздравить друзей с Новым Годом\n\n' \
                   'Также, поддерживается расширенный формат ввода\n' \
                   'После указания даты и времени можно указать дату и время ' \
                   'напоминания по такому же формату и категорию вида < #{категория} >\n' \
                   'Например:\n' \
                   '08.02.2017 09:00 01.02.2017 20:00 #работа День Рождения начальника\n\n' \
                   'Для удаления события нажмите на кнопку "Удалить событие", а затем введите его описание\n' \
                   'Все прошедшие события удаляются автоматически\n' \
                   'Бот умеет говорить умные фразы! Пообщайтесь с ним!'
        bot.sendMessage(chat_id=update.message.chat_id, text=response, reply_markup=keyboard)
    elif utext.casefold() == 'добавить событие':
        mode = '+'
        response = 'Введите данные о событии в формате:\n[Дата события] [Время события] [Описание события]\n\n' \
                   'Например:\n' \
                   '01.01.2345 00:00 Отпраздновать Галактический Новый Год!\n' \
                   '20.12.16 18:00 Экзамен в Технопарке\n\n' \
                   'Для отмены ввода напишите "Отмена"'
        bot.sendMessage(chat_id=uchat, text=response)
    elif utext_cf == 'удалить событие':
        response = 'О каком событии мне не напоминать тебе? Введи название события, пожалуйста.\n\n' \
                   'Для отмены ввода напишите "Отмена"'
        bot.sendMessage(chat_id=uchat, text=response)
        mode = '-'
    elif utext_cf == 'список активных задач':
        db_control.start()
        chat_id = update.message.chat_id
        event_list = db_control.get_info(chat_id)
        if event_list == '':
            response = 'Хмм... Кажется, активных событий сейчас нет. Может, настало время исправить это?'
        else:
            response = 'Список текущих активных задач:\n\n'
            response += event_list
        bot.sendMessage(chat_id=update.message.chat_id, text=response, reply_markup=keyboard)
    elif utext_cf == 'отмена':
        mode = ''
        bot.sendMessage(chat_id=uchat, text='Выберите действие', reply_markup=keyboard)
    elif mode == '+':
        wit_token = bot_conf.get_option('Main', 'WitToken')
        lang = language_processing.LanguageProcessing(wit_token, bot)
        result = lang.analyse(uchat, utext)
        if result:
            delay = round((result[0].date_notify - datetime.datetime.now()).total_seconds())

            if delay < 0:
                bot.sendMessage(chat_id=uchat,
                                text='Пожалуй, я не смогу напомнить о событии, '
                                     'если время напоминания уже прошло ¯\_(ツ)_/¯\n'
                                     'Возможно, время указано неправильно?',
                                reply_markup=keyboard)
            else:
                # Запись события в базу данных
                # Исправить
                db_control.start()
                db_control.add_event(result[0])
                queue.put(Job(callback, delay, repeat=False,
                              context=db_control.get_last_id()))

                db_control.stop()
                mode = ''
                # Уведомление об успешной записи
                if delay > 0:
                    bot.sendMessage(chat_id=uchat,
                                    text='Хорошо, я напомню тебе об этом {date}.'.format(date=result[0].date_notify_conv))
        else:
            bot.sendMessage(chat_id=uchat,
                            text='Что-то пошло не так, не могу понять что. '
                                 'Может, погода испортилась и мои шестеренки теперь хуже крутятся. '
                                 'Попробуй еще раз, пожалуйста!',
                            reply_markup=keyboard)
    elif mode == '-':
        db_control.start()
        msg = db_control.delete_event(utext, uchat)
        db_control.stop()
        mode = ''
        bot.sendMessage(chat_id=uchat,
                        text=msg, reply_markup=keyboard)
    else:
        #response = 'Что-то пошло не так, не могу понять что. ' \
        #           'Вернее, понять могу, но говорить не буду. ' \
        #           'Попробуй ещё раз, пожалуйста!\n' \
        #           'Введите /help для получения справки.'
        #bot.sendMessage(chat_id=uchat, text=response, reply_markup=keyboard)
        wit_token = bot_conf.get_option('Main', 'WitToken')
        lg_processing = language_processing.LanguageProcessing(wit_token, bot)

        result = lg_processing.analyse(uchat, utext)
        if result:
            delay = round((result[0].date_notify - datetime.datetime.now()).total_seconds())

            if delay < 0:
                bot.sendMessage(chat_id = uchat,
                                text='Пожалуй, я не смогу напомнить о событии, '
                                     'если время напоминания уже прошло ¯\_(ツ)_/¯\n'
                                     'Возможно, время указано неправильно?',
                                reply_markup=keyboard)
            else:
                # Запись события в базу данных
                # Исправить
                db_control.start()
                db_control.add_event(result[0])
                queue.put(Job(callback, delay, repeat=False,
                              context=dict(chat_id=update.message.chat_id,
                                           title='{}'.format(result[0].description),
                                           text='{date}:\n{desc}'.format(date=result[0].date_notify_conv, desc=result[0].description))))

                db_control.stop()
                mode = ''
                # Уведомление об успешной записи
                if delay > 0:
                    bot.sendMessage(chat_id=uchat,
                                    text='Хорошо, я напомню \"{description}\" {date}.'.format(description=result[0].description, date=result[0].date_notify_conv),
                                    reply_markup=keyboard)


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
            #wit_token = bot_conf.get_option('Main', 'WitToken')
            #lang = language_processing.LanguageProcessing(wit_token, db_control)
            #print(lang.analyse(0, request))
        else:
            print('Unknown command')


def callback(bot, job):
    db_control.start()
    elem = db_control.get_event_by_id(job.context)
    if elem is not None:
        print('1')
        bot.sendMessage(chat_id=elem[1],
                        text='Напоминание о событии {0} {1}.{2}.{3} в {4}\n\n'
                             'Попроси меня напомнить еще о чем-нибудь!'.format(elem[6], elem[2][8:10], elem[2][5:7],
                                                                               elem[2][:4], elem[2][11:16]),
                        reply_markup=keyboard)
        print('Callback > [{chat_id}] was notified at {date}'.format(chat_id=elem[1],
                                                                     date=datetime.datetime.now()))
        db_control.delete_event(elem[6], elem[1])
    print('2')
    db_control.stop()

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

    queue = updater.job_queue
    db_control = data_control.DataControl('database.db')

    db_control.start()
    current_events = db_control.get_events()

    counter = 0
    for event in current_events:
        delay = round((event.date_notify - datetime.datetime.now()).total_seconds())
        queue.put(Job(callback, delay, repeat=False,
                      context=db_control.get_event(event.chat_id, event.date_real, event.description)))
        counter += 1
    db_control.stop()
    print('Added {} events to queue'.format(counter))

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
