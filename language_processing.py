# coding: utf8

import datetime
import re
import events

from wit import Wit

class LanguageProcessing:
    def __init__(self, access_token, bot):
        # Шаблон для проверки соответствия формального запроса
        self.pattern_add = '^(?P<day_real>\d{2})\.(?P<month_real>\d{2})\.(?P<year_real>\d{2}|\d{4})' \
                           '\s(?P<hour_real>\d{2}):(?P<minutes_real>\d{2})' \
                           '(\s(?P<day_notify>\d{2})\.(?P<month_notify>\d{2})\.(?P<year_notify>\d{2}|\d{4})' \
                           '\s(?P<hour_notify>\d{2}):(?P<minutes_notify>\d{2}))?' \
                           '(\s(?P<duration>\d+)\s?мин)?(\s#(?P<category>\w+))?' \
                           '\s(?P<description>.+)$'

        # Передача объекта бота, чтобы wit.ai мог отправлять сообщения
        self.bot = bot

        # Настройка лиента для работы с wit.ai
        self.actions = {
            'send': self.send,
        }
        self.access_token = access_token
        self.client = Wit(access_token=access_token, actions=self.actions)

    def analyse(self, chat_id, request):
        """
        Функция для определения типа запроса (формальный или неформальный) и вызова функции-обработчика
        :param chat_id:
        :param request:
        :return:
        """
        self.chat_id = chat_id

        result = None
        if not re.match(self.pattern_add, request) is None:
            print('>> formal')
            result = [self.formal(chat_id, request)]
            print(result)
        else:
            print('>> informal')
            resp = self.client.converse(chat_id, request, {})
            result = [self.informal(chat_id, resp)]
            print(result)

        return result

    def formal(self, chat_id, request):
        """
        Функция для преобразования формального запроса в ответ типа event
        :param chat_id:
        :param request:
        :return:
        """
        exp = re.match(self.pattern_add, request)

        year_real = exp.group('year_real')
        if len(year_real) == 2:
            year_real = '20' + year_real
        year_real = int(year_real)

        date_real = datetime.datetime(year_real,
                                      int(exp.group('month_real')),
                                      int(exp.group('day_real')),
                                      int(exp.group('hour_real')),
                                      int(exp.group('minutes_real')))
        if exp.group('year_notify') is None or exp.group('month_notify') is None or exp.group('day_notify') is None:
            date_notify = date_real
        else:
            year_notify = exp.group('year_notify')
            if len(year_notify) == 2:
                year_notify = int('20' + year_notify)
            date_notify = datetime.datetime(year_notify,
                                            int(exp.group('month_notify')),
                                            int(exp.group('day_notify')),
                                            int(exp.group('hour_notify')),
                                            int(exp.group('minutes_notify')))
        duration = exp.group('duration')
        description = exp.group('description')
        category = exp.group('category')
        if category is not None:
            category = category.title()

        return events.Event(chat_id, date_real, date_notify, duration, description, category)

    def informal(self, chat_id, wit_response):
        """
        Функция для преобразования неформального запроса в ответ типа event
        :param chat_id:
        :param wit_response:
        :return:
        """
        entities = wit_response['entities']

        if entities is not None:
            message = self.first_entity_value(entities, 'message')
            date_string = self.first_entity_value(entities, 'date')
            print(message)
            date = ""
            if date_string is not None:
                now = datetime.datetime.now()
                if date_string.lower() == "сегодня":
                    # date = datetime.datetime(now.year, now.month, now.day, now.hour + 1, 00)
                    date = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute + 1)
                elif date_string.lower() == "завтра":
                    date = datetime.datetime(now.year, now.month, now.day + 1, 12, 00)
                elif date_string.lower() == "послезавтра":
                    date = datetime.datetime(now.year, now.month, now.day + 2, 12, 00)
                else:
                    date_string = None
            if message is None:
                self.bot.sendMessage(chat_id=self.chat_id, text="Так-так, я не понял, что напомнить. \nПовторите всё сначала, пожалуйста. Или введите /help для получения справки.")
                return None
            elif date_string is None:
                self.bot.sendMessage(chat_id=self.chat_id, text="Так-так, я не понял, когда напомнить. \nПовторите всё сначала, пожалуйста. Или введите /help для получения справки.")
                return None
            else:
                lst = message.split()
                lst[0] = lst[0].title()
                description = " ".join(lst)
                print(description)
                return events.Event(chat_id, date, date, None, description, None)

        return None

    def first_entity_value(self, entities, entity):
        """
        Функция для поиска определённой сущности wit.ai
        :param entities:
        :param entity:
        :return:
        """
        if entity not in entities:
            return None
        val = entities[entity][0]['value']
        if not val:
            return None
        return val['value'] if isinstance(val, dict) else val

    def send(self, request, response):
        """
        Функция wit.ai для отправки сообщения в telegram
        :param request:
        :param response:
        :return:
        """
        text = response["text"].decode("utf-8")
        self.bot.sendMessage(chat_id=self.chat_id, text=text)
