import sqlite3
import events


class DataControl:
    def __init__(self, datapath):
        self.datapath = datapath
        self.connect = None
        self.cursor = None

    def start(self):
        self.connect = sqlite3.connect(self.datapath)
        self.cursor = self.connect.cursor()

    def stop(self):
        self.cursor.close()
        self.connect.close()

    def get_events_count(self):
        return len(self.get_events())

    def get_events(self, output = False):
        if self.cursor is None: return None
        self.cursor.execute('SELECT * FROM events')
        row = self.cursor.fetchone()

        event_list = []
        if output:
            print('{0:3} {1:15} {2:12} {3:16} {4:12} {5:9} {6:8} {7}'.format('ID', 'ID Чата', 'Дата события', 'Дата напоминания', 'Длительность', 'Категория', 'Важность', 'Описание'))
        while row is not None:
            if output:
                print('{0:3} {1:15} {2:12} {3:16} {4:12} {5:9} {6:8} {7}'.format(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
            # print("ID: " + str(row[0]) + " | Дата события: " + row[1] + " | Дата напоминания: " + row[2])
            row = self.cursor.fetchone()
            new_event = events(row[0], row[1], row[2], row[3], row[4], row[5])
            event_list.append(new_event)
        return event_list

    def add_event(self, chat_id, id, date_real, date_notify, duration, description, category = 'basic', rating = 1):
        if self.connect is None or self.cursor is None: return None
        self.cursor.execute(
            "INSERT INTO events (chat_id,id,date_real,date_notify,duration,category,rating,description) "
            "VALUES ('%d','%s','%s','%d','%s','%d','%s')" % (chat_id, id, date_real, date_notify, duration, description, category, rating))
        self.connect.commit()

    def add_event(self, chat_id, id, event):
        if self.connect is None or self.cursor is None: return None
        self.cursor.execute(
            "INSERT INTO events (chat_id,id,date_real,date_notify,duration,category,rating,description) "
            "VALUES ('%d','%s','%s','%d','%s','%d','%s')" % (chat_id, id, event.date_real, event.date_notify, event.duration, event.description, event.category, event.rating))
        self.connect.commit()