# coding: utf8

from wit import Wit
import datetime
import re
import events


class LanguageProcessing:
    def __init__(self, access_token):
        # Шаблон для проверки соответствия формального запроса
        self.pattern_add = '^(?P<mode>\+)' \
                           '\s(?P<day_real>\d{2})\.(?P<month_real>\d{2})\.(?P<year_real>\d{2}|\d{4})' \
                           '\s(?P<hour_real>\d{2}):(?P<minutes_real>\d{2})' \
                           '(\s(?P<day_notify>\d{2})\.(?P<month_notify>\d{2})\.(?P<year_notify>\d{2}|\d{4})' \
                           '\s(?P<hour_notify>\d{2}):(?P<minutes_notify>\d{2}))?' \
                           '(\s(?P<duration>\d+)\s?мин)?(\s(?P<rating>\d+)!)?(\s#(?P<category>\w+))?' \
                           '\s(?P<description>.+)$'

        self.pattern_delete = '^(?P<mode>\-)' \
                              '\s(?P<description>.+)$'

        self.actions = {
            'send': self.send,
            'add_task': self.add_task,
            'remove_task': self.remove_task
        }

        # self.client = Wit(access_token=access_token, actions=actions)
        # self.client.interactive()

    def analyse(self, chat_id, request):
        '''
        Функция для определения типа запроса (формальный или неформальный) и вызова функции-обработчика
        :param chat_id:
        :param request:
        :return:
        '''
        result = None
        if not re.match(self.pattern_add, request) is None:
            print('>> formal')
            mode = re.match(self.pattern_add, request).group('mode')
            # Строки для отладки
            # for group in re.match(self.pattern, request).groups():
            #     print('>', group)
            result = [mode, self.formal(chat_id, request)]
            print(result)
        elif not re.match(self.pattern_delete, request) is None:
            print('>> formal')
            mode = re.match(self.pattern_delete, request).group('mode')
            result = [mode, re.match(self.pattern_delete, request).group('description'), chat_id]
            print(result)

        else:
            # Вызов функции распознавания человеческой речи
            print('>> informal')
            pass

        return result

    def formal(self, chat_id, request):
        '''
        Функция для преобразования формального запроса в ответ типа event
        :param chat_id:
        :param request:
        :return:
        '''
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
        rating = exp.group('rating')

        return events.Event(chat_id, date_real, date_notify, duration, description, category, rating)

    def first_entity_value(entities, entity):
        if entity not in entities:
            return None
            val = entities[entity][0]['value']
            if not val:
                return None
        return val['value'] if isinstance(val, dict) else val

    '''Actions'''

    def send(request, response):
        print(response['text'])

    def add_task(request, response):
        context = request['context']
        entities = request['entities']

        task = first_entity_value(entities, 'task')

        # Добавление задачи в бд

        return context

    def remove_task(request):
        context = request['context']
        entities = request['entities']

        task = first_entity_value(entities, 'task')

        # Удаление задачи из бд

        return context
