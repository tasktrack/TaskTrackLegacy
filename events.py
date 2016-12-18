# coding: utf8


class Event:
    def __init__(self, chat_id, date_real, date_notify, duration, description, category='basic'):
        # Уникальный id пользователя
        self.chat_id = chat_id
        # Реальная дата события
        self.date_real = date_real
        # Дата напоминания
        self.date_notify = date_notify
        # Конвертация дат для текстового представления
        self.convert_dates()
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

    def convert_dates(self):
        day = str(self.date_real.day)
        if len(day) == 1:
            day = '0' + day
        month = str(self.date_real.month)
        if len(month) == 1:
            month = '0' + month
        year = str(self.date_real.year)
        if len(year) == 4:
            year = year
        hours = str(self.date_real.hour)
        if len(hours) == 1:
            hours = '0' + hours
        minutes = str(self.date_real.minute)
        if len(minutes) == 1:
            minutes = '0' + minutes
        self.date_real_conv = '{day}.{month}.{year} в {hours}:{minutes}'.format(day=day,
                                                                                month=month,
                                                                                year=year,
                                                                                hours=hours,
                                                                                minutes=minutes)
        day = str(self.date_notify.day)
        if len(day) == 1:
            day = '0' + day
        month = str(self.date_notify.month)
        if len(month) == 1:
            month = '0' + month
        year = str(self.date_notify.year)
        if len(year) == 4:
            year = year
        hours = str(self.date_notify.hour)
        if len(hours) == 1:
            hours = '0' + hours
        minutes = str(self.date_notify.minute)
        if len(minutes) == 1:
            minutes = '0' + minutes
        self.date_notify_conv = '{day}.{month}.{year} в {hours}:{minutes}'.format(day=day,
                                                                                  month=month,
                                                                                  year=year,
                                                                                  hours=hours,
                                                                                  minutes=minutes)
