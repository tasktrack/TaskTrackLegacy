def run():
    print('Script started')
    from telegram.ext import Updater
    updater = Updater(token='289680799:AAHDpjJLcqBF0Flcybl3GyE8wTpdfiZjM4Y')
    dispatcher = updater.dispatcher

    import logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    #Обработка команд
    from telegram.ext import CommandHandler

    def start(bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text="Hello world.")
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    def caps(bot, update, args):
        text_caps = ''.join(args).upper()
        bot.sendMessage(chat_id=update.message.chat_id, text=text_caps)
    caps_handler = CommandHandler('caps', caps, pass_args=True)
    dispatcher.add_handler(caps_handler)

    #Обработка текста
    def echo(bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text=update.message.text)

    from telegram.ext import MessageHandler, Filters
    echo_handler = MessageHandler([Filters.text], echo)
    dispatcher.add_handler(echo_handler)

    #Начало обработки запросов
    updater.start_polling()
    print('Running the main script normally')

if __name__ == "__main__":
    run()