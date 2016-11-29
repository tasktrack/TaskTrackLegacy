import sqlite3


def test_table():
    datapath = 'database.db'
    temporary_connection = sqlite3.connect(datapath)
    temporary_cursor = temporary_connection.cursor()
    # Выполнение запроса вернет значение 0, если таблицы не существует
    temp_bool = temporary_cursor.execute('SELECT name FROM sqlite_master WHERE type = \'table\' AND name = \'events\' ')
    assert temp_bool
