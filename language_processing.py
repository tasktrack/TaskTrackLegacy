# coding: utf8

from wit import Wit
import datetime
import re
import events
from configuration import Configuration

# Перед запуском необходимо 'pip install wit'


class LanguageProcessing:

    def __init__(self, access_token):
        self.pattern_date = r'\b\d{2}\.\d{2}\.\d{2,4}\b'
        self.pattern_time = r'\b\d{2}:\d{2}\b'

        actions = {
            'send': self.send,
            'add_task': self.add_task,
            'remove_task': self.remove_task
        }

        client = Wit(access_token=access_token, actions=actions)
        client.interactive()

    def analyse(self, chat_id, request):
        '''
        Функция для определения типа запроса: формальный или неформальный
        :param request:
        :return:
        '''
        result = None
        # Строки для отладки
        # sample = '12.11.2016 16:00 Напоминание'
        # request = sample
        pattern = re.compile('{date} {time}'.format(date=self.pattern_date, time=self.pattern_time))

        if pattern.match(request):
            result = self.formal(chat_id, request)
        else:
            # Вызов функции распознавания человеческой речи
            pass

        return result

    def formal(self, chat_id, request):
        '''
        Функция для преобразования формального запроса в ответ типа event
        :param chat_id:
        :param request:
        :return:
        '''
        # Поиск дат и указания времени в запросе
        date_list = re.findall(self.pattern_date, request)
        time_list = re.findall(self.pattern_time, request)

        # Обработка даты и разбиение на день, месяц и год
        date_real_list = date_list[0].split('.')
        # Дополнение неполного значения года (к примеру, 01.01.17 будет преобразовано в 01.01.2017)
        if len(date_real_list[2]) == 2:
            date_real_list[2] = '20' + date_real_list[2]
        elif len(date_real_list[2]) == 3:
            date_real_list[2] = '2' + date_real_list[2]
        # Обработка времени и разбиение на часы и минуты
        time_real_list = time_list[0].split(':')
        # Создание объекта datetime для реальной даты события
        date_real = datetime.datetime(int(date_real_list[2]), int(date_real_list[1]), int(date_real_list[0]),
                                      int(time_real_list[0]), int(time_real_list[1]))
        # Для даты напоминания нужно придумать формат, временное решение
        date_notify = date_real
        # Блок для обработки даты напоминания
        # if len(date_list) > 1 and len(time_list) > 1:
        #    date_notify_list = date_list[1].split('.')
        #    time_notify_list = time_list[1].split(':')
        #    date_notify = datetime.datetime(date_notify_list[0], date_notify_list[1], date_notify_list[2],
        #                                    time_notify_list[0], time_notify_list[1])

        # Для продолжитальности нужно придумать формат, временное решение
        duration = 0

        # Удаления из запроса технической информации для записи пользовательского описания события
        disassembled_request = request.split()
        for word in disassembled_request:
            for date in date_list:
                if word == date:
                    disassembled_request.remove(date)
        for word in disassembled_request:
            for time in time_list:
                if word == time:
                    disassembled_request.remove(time)
        description = ' '.join(disassembled_request)

        return events.Event(chat_id, date_real, date_notify, duration, description)

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

    def add_task(request):
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
