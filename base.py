import sqlite3
import logging
logging.basicConfig(filename='logs/base.log', format='<%(asctime)s> [%(name)s] [%(levelname)s]: %(message)s',
                    level=logging.INFO)
#Работа с базой данных

def add_event(datapath, date_real, date_notify, duration, description, category = 'basic', rating = 1):
    print('Procedure add_event have started its job')
    connect = sqlite3.connect(datapath)
    cursor = connect.cursor()

    cursor.execute('SELECT * FROM events')
    row = cursor.fetchone()
    # выводим список пользователей в цикле
    count = 0
    while row is not None:
        print("ID: " + str(row[0]) + "\nДата события: " + row[1] + "\nДата напоминания: " + row[2])
        count += 1
        row = cursor.fetchone()

    #cursor.execute("INSERT INTO events (id,date_real,date_notify,duration,category,rating,description) VALUES ('%d','%s','%s','%d','%s','%d','%s')" % (count, date_real, date_notify, duration, description, category, rating))

    connect.commit()
    cursor.close()
    connect.close()
    print('oh hai')

def run():
    logging.info('Script execution started')
    print('Script started')
    from telegram.ext import Updater
    updater = Updater(token='289680799:AAHDpjJLcqBF0Flcybl3GyE8wTpdfiZjM4Y')
    dispatcher = updater.dispatcher

    #Обработка команд
    from telegram.ext import CommandHandler

    def start(bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text="Hello world.")
        logging.info('Command \'start\' invoked by chat id [{0}]'.format(update.message.chat_id))
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    def test(bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text="Test executed")

        from events import Event
        new_event = Event(datetime.datetime.now(), datetime.datetime.now(), 0, 'Пример', 'basic', 1)
        bot.sendMessage(chat_id=update.message.chat_id, text=new_event)
        bot.sendMessage(chat_id=update.message.chat_id, text='123')

        import data_control
        db_control = data_control.DataControl('database.db')
        db_control.start()
        print(db_control.get_events())
        new_id = db_control.get_events_count()
        db_control.add_event(update.message.chat_id,
                            new_id,
                            datetime.datetime.now(),
                            datetime.datetime.now(),
                            0, 'Пример', 'basic', 1)
        db_control.stop()

        logging.info('Command \'test\' invoked by chat id [{0}]'.format(update.message.chat_id))
    start_handler = CommandHandler('test', test)
    dispatcher.add_handler(start_handler)

    def caps(bot, update, args):
        text_caps = '%s' % ' '.join(args).upper()
        bot.sendMessage(chat_id=update.message.chat_id, text=text_caps)
        logging.info('Command \'caps\' invoked by char id [{0}]'.format(update.message.chat_id))
    caps_handler = CommandHandler('caps', caps, pass_args=True)
    dispatcher.add_handler(caps_handler)

    #Обработка текста
    def echo(bot, update):
        utext = update.message.text
        utext_cf = utext.casefold()
        uchat = update.message.chat_id
        if 'привет'.casefold() in utext_cf:
            bot.sendMessage(chat_id=uchat, text='Привет, друг!')
        elif 'напомни'.casefold() in utext_cf:
            bot.sendMessage(chat_id=uchat, text='Разве мы уже на \"ты\"? ;)')
            days = ['понедельник', 'вторник', 'сред', 'четверг', 'пятниц', 'суббот', 'воскресенье']
            days_match = []

            for day in days:
                if day in utext_cf:
                    if day == 'сред': day = 'cреду'
                    elif day == 'пятниц': day = 'пятницу'
                    elif day == 'суббот': day = 'субботу'
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

    #Начало обработки запросов
    updater.start_polling()
    logging.info('Started main updater polling')
    print('Running the main script normally')

    #Режим терминала
    response = ''
    while True:
        response = input('> ').casefold()
        if response == 'stop': break
        elif response == 'say hi': print('Oh hi there')
        elif response == 'add':
            import datetime
            date_real = datetime.datetime(2016, 10, 10, 23, 55, 0)
            date_notify = datetime.datetime(2016, 10, 10, 23, 50, 0)
            add_event('database.db', date_real, date_notify, 0, 'Пример')
        elif response == 'controlinit':
            pass
        else:
            print('Unknown command')

    #Отключение бота
    logging.info('Stopping main updater polling')
    print('Stopping the main script...')
    updater.stop()
    logging.info('Script execution ended')
    print('Main script stopped')

if __name__ == "__main__":
    run()