# coding: utf8

import sqlite3
import events
import datetime


class DataControl:
    def __init__(self, datapath):
        # Путь к базе данных
        self.datapath = datapath
        self.connect = None
        self.cursor = None

    def __repr__(self):
        return '> datacontrol > \'{0}\', \'{1}\', \'{2}\''.format(self.datapath, self.connect, self.cursor)

    def __enter__(self):
        '''
        Подключение к базе данных
        :return:
        '''
        # (Для Михаила): функция connect создает базу, если ее нет и подключается, если она существует.
        self.connect = sqlite3.connect(self.datapath)
        self.cursor = self.connect.cursor()
        # Создание таблицы в базе данных, если таковая еще не существует.
        self.cursor.execute('CREATE TABLE if not exists events (id INTEGER PRIMARY KEY, chat_id VARCHAR(50), date_real VARCHAR(50), date_notify VARCHAR(50), duration VARCHAR(50), category VARCHAR(50), rating VARCHAR(50), description VARCHAR(200))')

    def __exit__(self, exc_type, exc_value, traceback):
        '''
        Отключение от базы данных
        :return:
        '''
        self.cursor.close()
        self.cursor = None
        self.connect.close()
        self.connect = None
        return self

    def start(self):
        '''
        Подключение к базе данных (эквивалент __enter__)
        :return:
        '''
        self.connect = sqlite3.connect(self.datapath)
        self.cursor = self.connect.cursor()

        # !!!!!! Здесь также разместить создание таблицы, в случае ее отсутствия

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
        print('{chat_id:^9} | {date_real} | {date_notify} | {duration} | {cat:^10} | {rating:^3} | {desc}'.format(chat_id='ID Чата',
                                                                                                 date_real='Дата события',
                                                                                                 date_notify='Дата напоминания',
                                                                                                 duration='Длительность',
                                                                                                 cat='Категория',
                                                                                                 rating='Рейтинг',
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

    def get_events(self, output = False):
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
            print('{0:3} {1:7} {2:12} {3:16} {4:12} {5:9} {6:8} {7}'.format('ID', 'ID Чата', 'Дата события', 'Дата напоминания', 'Длительность', 'Категория', 'Важность', 'Описание'))
        while row is not None:
            if output:
                print('{0:3} {1:7} {2:12} {3:16} {4:12} {5:9} {6:8} {7}'.format(str(row[0]), str(row[1]), str(row[2]), str(row[3]), str(row[4]), str(row[5]), str(row[6]), str(row[7])))

            date_real = self.date_convert(str(row[2]))
            date_notify = self.date_convert(str(row[3]))

            new_event = events.Event(chat_id=row[1],
                                     date_real=date_real,
                                     date_notify=date_notify,
                                     duration=row[4],
                                     description=row[7],
                                     category=row[5],
                                     rating=row[6])
            event_list.append(new_event)
            row = self.cursor.fetchone()
        return event_list

    def add_event(self, id, event):
        '''
        Добавление в базу данных нового события
        :param id:
        :param event:
        :return:
        '''
        if self.connect is None or self.cursor is None: return None
        self.cursor.execute("INSERT INTO events (id, chat_id,date_real,date_notify,"
                            "duration,category,rating,description) VALUES ('{0}',"
                            "'{1}','{2}','{3}','{4}','{5}','{6}','{7}')".format(id, event.chat_id, event.date_real, event.date_notify, event.duration, event.category, event.rating, event.description))
        self.connect.commit()