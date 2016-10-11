import datetime


class Event:
    def __init__(self, date_real, date_notify, duration, description, category = 'basic', rating = 1):
        self.date_real = datetime.datetime(date_real)
        self.date_notify = datetime.datetime(date_notify)
        self.duration = duration
        self.description = description
        self.category = category
        self.rating = rating

    def __repr__(self):
        return '{0} | {1} | {2} | {3} | {4} | {5}'.format(self.date_real, self.date_notify, self.duration, self.description, self.category, self.rating)

    def print(self):
        return '{0} | {1} | {2} | {3} | {4} | {5}'.format(self.date_real, self.date_notify, self.duration, self.description, self.category, self.rating)
