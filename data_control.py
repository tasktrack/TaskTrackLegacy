# coding: utf8

import sqlite3
import events
import datetime


# import asyncio


class DataControl:
    def __init__(self, datapath):
        # Путь к базе данных
        self.datapath = datapath
        self.connect = None
        self.cursor = None

    def __repr__(self):
        return '> datacontrol > \'{0}\', \'{1}\', \'{2}\''.format(self.datapath, self.connect, self.cursor)

    def __enter__(self):
        """
        Подключение к базе данных
        :return:
        """
        self.connect = sqlite3.connect(self.datapath)
        self.cursor = self.connect.cursor()
        # Создание таблицы в базе данных, если таковая еще не существует.
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT , chat_id VARCHAR(50), date_real VARCHAR(50), date_notify VARCHAR(50), duration VARCHAR(50), category VARCHAR(50), description VARCHAR(200))')
        self.connect.commit()

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Отключение от базы данных
        :return:
        """
        self.cursor.close()
        self.cursor = None
        self.connect.close()
        self.connect = None
        return self

    def start(self):
        """
        Подключение к базе данных (эквивалент __enter__)
        :return:
        """
        self.connect = sqlite3.connect(self.datapath)
        self.cursor = self.connect.cursor()

        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT , chat_id VARCHAR(50), date_real VARCHAR(50), date_notify VARCHAR(50), duration VARCHAR(50), category VARCHAR(50), description VARCHAR(200))')
        self.connect.commit()

    def stop(self):
        '''
        Отключение от базы данных (эквивалент __exit__)
        :return:
        '''
        self.cursor.close()
        self.cursor = None
        self.connect.close()
        self.connect = None

    def date_convert(self, string_date):
        '''
        Конвертация строки в datetime (возможно, есть стандартная реализация)
        :param string_date:
        :return:
        '''
        date_complex = string_date.split(' ')
        date = date_complex[0].split('-')
        year = int(date[0])
        month = int(date[1])
        day = int(date[2])
        time = date_complex[1].split(':')
        hours = int(time[0])
        minutes = int(time[1])
        mseconds = 0

        if '.' in time[2]:
            tsecs = time[2].split('.')
            seconds = int(tsecs[0])
            mseconds = int(tsecs[1])
        else:
            seconds = int(time[2])

        return datetime.datetime(year, month, day, hours, minutes, seconds, mseconds)

    def print_events(self):
        '''
        Вывод загруженных событий
        :return:
        '''
        print('{chat_id:^9} | {date_real} | {date_notify} | {duration} | {cat:^10} | {desc}'.format(
            chat_id='ID Чата',
            date_real='Дата события',
            date_notify='Дата напоминания',
            duration='Длительность',
            cat='Категория',
            desc='Описание'))
        for event in self.get_events():
            print(event)

    def get_events_count(self):
        '''
        Вывод количества имеющихся в базе событий (для определения id следующего события
        Стоит усовершенствовать, очень черновое решение
        :return:
        '''
        return len(self.get_events())

    def get_events(self, output=False):
        '''
        Получение списка всех имеющихся в базе данных событий
        :param output:
        :return:
        '''
        if self.cursor is None: return None
        self.cursor.execute('SELECT * FROM events')
        row = self.cursor.fetchone()

        event_list = []
        if output:
            print('{0:3} {1:7} {2:12} {3:16} {4:12} {5:9} {6}'.format('ID', 'ID Чата', 'Дата события',
                                                                      'Дата напоминания', 'Длительность',
                                                                      'Категория', 'Описание'))
        while row is not None:
            if output:
                print('{0:3} {1:7} {2:12} {3:16} {4:12} {5:9} {6}'.format(str(row[0]), str(row[1]), str(row[2]),
                                                                          str(row[3]), str(row[4]), str(row[5]),
                                                                          str(row[6])))

            date_real = self.date_convert(str(row[2]))
            date_notify = self.date_convert(str(row[3]))

            new_event = events.Event(chat_id=row[1],
                                     date_real=date_real,
                                     date_notify=date_notify,
                                     duration=row[4],
                                     description=row[6],
                                     category=row[5])
            event_list.append(new_event)
            row = self.cursor.fetchone()
        return event_list

    def add_event(self, event):
        """
        Добавление в базу данных нового события
        :param event:
        :return:
        """
        if self.connect is None or self.cursor is None:
            return None
        self.cursor.execute("INSERT INTO events (chat_id,date_real,date_notify,"
                            "duration,category,description) VALUES ('{0}',"
                            "'{1}','{2}','{3}','{4}','{5}')".format(event.chat_id, event.date_real,
                                                                    event.date_notify, event.duration,
                                                                    event.category, event.description))
        self.connect.commit()

    def load_actual_events(self):
        if self.connect is None or self.cursor is None: return None

        actual_events = []

        for current_cell in self.cursor:
            if self.round_minutes(self.date_convert(current_cell[3])) == self.round_minutes(datetime.datetime.now()):
                actual_events.append(current_cell)

        return actual_events

    def get_info(self, chat):
        if self.cursor is None: return None
        self.cursor.execute('SELECT * FROM events WHERE chat_id = ?', (str(chat),))
        row = self.cursor.fetchone()
        counter = 0
        events_list = ''
        while row is not None:
            counter += 1
            events_list += 'Событие {}: '.format(counter) + str(row[6]) + '\n'

            real_full_date = str(row[2]).split()
            real_date = real_full_date[0].split('-')
            real_time = real_full_date[1].split(':')
            real_conv = '{day}.{month}.{year} в {hours}:{minutes}'.format(day=real_date[2], month=real_date[1], year=real_date[0], hours=real_time[0], minutes=real_time[1])

            events_list += 'Дата: {}'.format(real_conv)
            if row[3] != row[2]:
                events_list += '\nДата напоминания: ' + str(row[3]) + '\n'
            if row[4] != 'None':
                events_list += '\nДлительность: ' + str(row[4]) + '\n'
            if row[5] != 'None':
                events_list += '\nКатегория: ' + str(row[5]) + '\n'
            events_list += '\n'
            row = self.cursor.fetchone()
        return events_list

    def delete_event(self, event, chat):
        if self.cursor is None: return None
        self.cursor.execute('SELECT * FROM events WHERE (chat_id = ? AND description = ?)', (str(chat), event))
        row = self.cursor.fetchone()
        if row is None:
            return 'Не удалось найти такое событие'
        self.cursor.execute("DELETE FROM events WHERE (chat_id = ? AND description = ?)", (str(chat), event))
        self.cursor.execute('SELECT * FROM events WHERE (chat_id = ? AND description = ?)', (str(chat), event))
        row = self.cursor.fetchone()
        while row is not None:
            print('{0:3} {1:7} {2:12} {3:16} {4:12} {5:9} {6}'.format(str(row[0]), str(row[1]), str(row[2]),
                                                                            str(row[3]), str(row[4]), str(row[5]),
                                                                            str(row[6])))

            row = self.cursor.fetchone()
        self.connect.commit()
        if row is None:
            return 'Событие удалено. Совсем. Навсегда. Это грустно. Напомнить тебе о чем-нибудь другом?'
        else:
            return 'error'

    def round_minutes(self, t):  # t - объект datetime
        return t - datetime.timedelta(seconds=t.second, microseconds=t.microsecond)

    def get_last_id(self):
        if self.cursor is None: return None
        self.cursor.execute('SELECT * FROM events WHERE id = (SELECT max(id) FROM events) ')
        row = self.cursor.fetchone()
        result = str(row[0])
        print(result)
        return result

    def get_event_by_id(self, i):
        if self.cursor is None: return None
        self.cursor.execute('SELECT * FROM events WHERE id = ?', (str(i),))
        row = self.cursor.fetchone()
        return row

    def get_event(self, chat, date, desc):
        if self.cursor is None: return None
        self.cursor.execute('SELECT * FROM events WHERE (chat_id = ? AND date_real = ? AND description = ?)', (str(chat), str(date), str(desc)))
        row = self.cursor.fetchone()
        result = str(row[0])
        return result