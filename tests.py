import unittest
import sqlite3

# Набор тестов, связанных с базой данных

class databasetests(unittest.TestCase):

    # Функция вводится, т.к. нельзя переопределить конструктор класса
    def basefortest(self, datapath):
        self.datapath = datapath

    # Проверка на существование таблицы
    def tabletest(self):
        temporaryconnection = sqlite3.connect(self.datapath)
        temporarycursor = temporaryconnection.cursor()
        # Выполнение запроса вернет значение 0, если таблицы не существует
        tempbool = temporarycursor.execute('SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'events' ')
        self.assertTrue(tempbool)
