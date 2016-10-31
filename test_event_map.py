# coding: utf8

import unittest
import event_map
import events
import datetime


class EventMapTestCase(unittest.TestCase):
    def test_init(self):
        '''
        Проверка правильности инициализации
        :return:
        '''

        # Получаем текущее время
        now = datetime.datetime.now()

        # Заполнение фейкового листа событий
        event_list = []
        n = 5
        for i in range(n):
            time_next = datetime.datetime(day=now.day,
                                          month=now.month,
                                          year=now.year,
                                          hour=now.hour,
                                          minute=now.minute,
                                          second=now.second,
                                          microsecond=now.microsecond + n - i)
            event_list.append(events.Event(chat_id=0, date_real=time_next, date_notify=time_next, duration=0, description='test-event-{0}'.format(i)))

        # Загрузка событий в карту событий
        emap = event_map.EventMap(event_list)

        # Заполнение ожидаемого листа событий карты событий
        sorted_list = []
        for i in range(n - 1, -1, -1):
            sorted_list.append(event_list[i])

        # Результат = список событий карты событий
        result = emap.actual_events
        # Ожидается = отсортированный фейковый список событий
        expected = sorted_list

        self.assertEqual(result, expected, 'ERROR: Wrong __init__ result')

    def test_check(self):
        '''
        Проверка правильности работы фильтра событий текущего дня
        :return:
        '''

        # Текущее время
        now = datetime.datetime.now()

        # Инициализация переменных
        tomorrow_day = 1
        tomorrow_month = 1
        tomorrow_year = 1000

        # Условия для граничных значений
        if now.day < 31:
            tomorrow_day = now.day + 1
        else:
            tomorrow_day = 1
            if now.month < 12:
                tomorrow_month = now.month + 1
            else:
                tomorrow_day = 1
                tomorrow_month = 1
                tomorrow_year = now.year + 1

        # Дата следующего дня
        tomorrow = datetime.datetime(day=tomorrow_day,
                                     month=tomorrow_month,
                                     year=tomorrow_year,
                                     hour=now.hour,
                                     minute=now.minute,
                                     second=now.second,
                                     microsecond=now.microsecond)

        # Создание фейкового списка событий
        event_1 = events.Event(chat_id=0, date_real=now, date_notify=now, duration=0, description='test-event-1')
        event_2 = events.Event(chat_id=0, date_real=tomorrow, date_notify=tomorrow, duration=0, description='test-event-2')
        event_3 = events.Event(chat_id=0, date_real=tomorrow, date_notify=tomorrow, duration=0, description='test-event-3')
        event_4 = events.Event(chat_id=0, date_real=now, date_notify=now, duration=0, description='test-event-4')
        event_list = [event_1, event_2, event_3, event_4]

        # Результат = список событий, отфильтрованных как события текущего дня
        result = event_map.EventMap.check(event_list=event_list)
        # Ожидается = события 1 и 4 (происходящие сегодня)
        expected = [event_1, event_4]

        self.assertEqual(result, expected, 'ERROR: Wrong check result')

    def test_next_event(self):
        '''
        Проверка правильности работы функции поиска следующего события
        :return:
        '''

        # Текущее время
        now = datetime.datetime.now()

        # Фейковое время для следующего события
        time_next = datetime.datetime(day=now.day,
                                     month=now.month,
                                     year=now.year,
                                     hour=now.hour,
                                     minute=now.minute,
                                     second=now.second,
                                     microsecond=now.microsecond + 1)

        # Фейковое время для прошедшего события
        time_passed = datetime.datetime(day=now.day,
                                     month=now.month,
                                     year=now.year,
                                     hour=now.hour,
                                     minute=now.minute,
                                     second=now.second,
                                     microsecond=now.microsecond - 1)

        # Фейковое время для события в будущем, но не следующего
        time_far = datetime.datetime(day=now.day,
                                        month=now.month,
                                        year=now.year,
                                        hour=now.hour,
                                        minute=now.minute,
                                        second=now.second,
                                        microsecond=now.microsecond + 2)

        # Заполнение фейкового списка событий карты событий
        event_1 = events.Event(chat_id=0, date_real=time_passed, date_notify=time_passed, duration=0, description='event-1')
        event_2 = events.Event(chat_id=0, date_real=now, date_notify=now, duration=0, description='event-2')
        event_3 = events.Event(chat_id=0, date_real=time_next, date_notify=time_next, duration=0, description='event-3')
        event_4 = events.Event(chat_id=0, date_real=time_far, date_notify=time_far, duration=0, description='event-4')
        event_list = [event_1, event_2, event_3, event_4]
        emap = event_map.EventMap(event_list)

        # Результат = следующее событие из карты событий
        result = emap.next_event
        # Ожидается = событие 3 (ближайшее)
        expected = event_3

        self.assertEqual(result, expected, 'ERROR: Wrong next_event result')

if __name__ == '__main__':
    unittest.main()




