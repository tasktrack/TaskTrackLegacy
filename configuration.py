import os
import configparser
from configparser import ConfigParser


class Configuration:
    def __init__(self, filepath):
        # Путь к файлу конфигурации
        self.config_path = filepath
        # Путь без названия и расширения файла
        dirpath = os.path.dirname(self.config_path)
        # Если директорий не существует, они создаются, и в последнюю помещается пустой файл конфигурации
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)
        if not os.path.exists(filepath):
            with open(filepath, 'w') as f:
                f.write('[Main]\n')
                f.write('TelegramToken = \n')
                f.write('WitToken = \n')
        self.config = ConfigParser()
        self.config.read(self.config_path)

    def get_option(self, section, option, default=None):
        """
        Возвращает значение параметра option из раздела section
        :param section:
        :param option:
        :param default:
        :return:
        """
        try:
            return self.config.get(section, option)
        except (configparser.NoSectionError, configparser.NoOptionError):
            return default
