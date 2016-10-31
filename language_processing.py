# coding: utf8

import sys
from wit import Wit
import events
import datetime

# Перед запуском необходимо 'pip install wit'

class LanguageProcessing:

    # Приложение на сайте ещё не обучил
    # Поэтому пока что ничего работать не будет

    def __init__(self):

        access_token = '2XR2X3MEZI3RCQ4XGXZ43OVQ7GTYZL7W'

        actions = {
            'send': self.send,
        }

        client = Wit(access_token=access_token, actions=actions)
        client.interactive()

    def send(request, response):
        print(response['text'])
