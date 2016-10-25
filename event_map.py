import datetime


class EventMap:
    def __init__(self, event_list):
        # Инициализация списка актуальных событий (этого дня)
        self.actual_events = []
        # Количество актуальных событий (пока не используется)
        self.event_count = 0
        # Загрузка актуальных событий из переданного списка
        self.check(event_list)
        # Сортировка списка по возрастанию даты
        self._sort_events()

    def __repr__(self):
        return '\n'.join(str(e) for e in self.actual_events)

    def _sort_events(self):
        '''
        Сортировка типа bubble для списка актуальных событий
        :return:
        '''
        n = 1
        while n < len(self.actual_events):
            for i in range(len(self.actual_events) - n):
                if self.actual_events[i].date_notify > self.actual_events[i + 1].date_notify:
                    self.actual_events[i], self.actual_events[i + 1] = self.actual_events[i + 1], self.actual_events[i]
            n += 1

    def add_event(self, event):
        self.actual_events.append(event)
        self.event_count += 1
        self._sort_events()

    @property
    def next_event(self):
        '''
        Недописанная функция, будет возвращать ближайшее событие
        :return:
        '''
        if len(self.actual_events):
            return self.actual_events[0]

    def check(self, event_list):
        '''
        Выделение из списка всех событий только актуальных
        :param event_list:
        :return:
        '''
        for event in event_list:
            if event.date_notify.day == datetime.datetime.now().day:
                self.actual_events.append(event)
                self.event_count += 1