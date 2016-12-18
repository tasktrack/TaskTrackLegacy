# coding: utf8

import datetime
import re
import events


class LanguageProcessing:
    def __init__(self):
        # Шаблон для проверки соответствия формального запроса
        self.pattern_add = '^(?P<day_real>\d{2})\.(?P<month_real>\d{2})\.(?P<year_real>\d{2}|\d{4})' \
                           '\s(?P<hour_real>\d{2}):(?P<minutes_real>\d{2})' \
                           '(\s(?P<day_notify>\d{2})\.(?P<month_notify>\d{2})\.(?P<year_notify>\d{2}|\d{4})' \
                           '\s(?P<hour_notify>\d{2}):(?P<minutes_notify>\d{2}))?' \
                           '(\s(?P<duration>\d+)\s?мин)?(\s#(?P<category>\w+))?' \
                           '\s(?P<description>.+)$'

    def analyse(self, chat_id, request):
        """
        Функция для определения типа запроса (формальный или неформальный) и вызова функции-обработчика
        :param chat_id:
        :param request:
        :return:
        """
        result = None
        if not re.match(self.pattern_add, request) is None:
            print('>> formal')
            result = [self.formal(chat_id, request)]
            print(result)
        else:
            print('>> informal')
            pass
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
