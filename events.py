class Event:
    def __init__(self, chat_id, date_real, date_notify, duration, description, category = 'basic', rating = 1):
        # Уникальный id пользователя
        self.chat_id = chat_id
        # Реальная дата события
        self.date_real = date_real
        # Дата напоминания
        self.date_notify = date_notify
        # Продолжительность (int), требуется доработка структуры
        self.duration = duration
        # Текстовое описание
        self.description = description
        # Категория события для сортировок и выборочного вывода (в будущем)
        self.category = category
        # Важность события по категориям
        self.rating = rating

    def __repr__(self):
        return '{0:9} | {1} | {2} | {3:3} | {5:10} | {6:3} | \'{4}\''.format(self.chat_id, self.date_real, self.date_notify, self.duration, self.description, self.category, self.rating)