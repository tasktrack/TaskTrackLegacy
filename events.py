# coding: utf8


class Event:
    def __init__(self, chat_id, date_real, date_notify, duration, description, category='basic'):
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

    def __repr__(self):
        result = '< {id} | {date_real} | {date_notify} ' \
                 '| {duration} | {category} | {description} >'.format(id=self.chat_id,
                                                                      date_real=self.date_real,
                                                                      date_notify=self.date_notify,
                                                                      duration=self.duration,
                                                                      category=self.category,
                                                                      description=self.description)
        return result
