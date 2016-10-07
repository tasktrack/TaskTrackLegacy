import time
import logging
logging.basicConfig(filename='logs/base.log', format='<%(asctime)s> [%(name)s] [%(levelname)s]: %(message)s',
                    level=logging.INFO)
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
    while not response == 'stop':
        response = input('> ')
        if response.casefold() == 'say hi': print('Oh hi there')

    #Отключение бота
    logging.info('Stopping main updater polling')
    print('Stopping the main script...')
    updater.stop()
    logging.info('Script execution ended')
    print('Main script stopped')

if __name__ == "__main__":
    run()