import configparser
from configparser import ConfigParser
import os


class Configuration:
    def __init__(self, filepath):
        # Путь к файлу конфигурации
        self.config_path = filepath
        # Путь без названия и расширения файла
        dirpath = '/'.join(self.config_path.split('/')[:-1])
        # Если директорий не существует, они создаются, и в последнюю помещается пустой файл конфигурации
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
            with open(filepath, 'w') as f:
                f.write('[Main]\nTelegramToken = ')
        self.config = ConfigParser()
        self.config.read(self.config_path)

    def get_option(self, section, option, default=None):
        '''
        Возвращает значение параметра option из раздела section
        :param section:
        :param option:
        :param default:
        :return:
        '''
        try:
            return self.config.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default