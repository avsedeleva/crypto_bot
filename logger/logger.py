import csv
import logging
import os
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler


'''class Logger:
    def __init__(self):
        self.FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(level)s — %(message)s")
        self.LOG_FILE = "discovery_all.log"
        logging.basicConfig(filename='discovery.log',
                            filemode='a',
                            format='%(asctime)s, %(name)s %(levelname)s %(message)s',
                            datefmt='%H:%M:%S',
                            level=logging.INFO)

    def get_console_handler(self):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.FORMATTER)
        return console_handler

    def get_file_handler(self):
        file_handler = TimedRotatingFileHandler(self.LOG_FILE, when='midnight')
        file_handler.setFormatter(self.FORMATTER)

        return file_handler

    def get_logger(self, logger_name, log_file):
        self.LOG_FILE = log_file
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)  # лучше иметь больше логов, чем их нехватку
        #logger.addHandler(self.get_console_handler())
        logger.addHandler(self.get_file_handler())
        logger.propagate = False
        return logger'''


'''class Logger:
    def __init__(self):
        self.handler = None
        self.FORMATTER = logging.Formatter('%(asctime)s %(name)-s %(levelname)-6s %(message)s', "%Y-%m-%d %H:%M:%S")

    def get_logger_general(self, name_log):
        logger = logging.getLogger(name_log)
        logger.setLevel(logging.INFO)
        if self.handler is not None:
            logger.removeHandler(self.handler)
        self.handler = TimedRotatingFileHandler('logs/general/general.log', when='midnight')
        self.handler.setLevel(logging.INFO)
        self.handler.setFormatter(self.FORMATTER)
        logger.addHandler(self.handler)
        return logger'''


class Logger:
    def __init__(self):
        self.handler = None
        self.FORMATTER = logging.Formatter(
            '%(asctime)s %(name)-s %(levelname)-6s %(message)s',
            "%Y-%m-%d %H:%M:%S"
        )
        # Создаем директории для логов
        os.makedirs('logs', exist_ok=True)
        os.makedirs('logs/general', exist_ok=True)
        os.makedirs('logs/answer', exist_ok=True)
        os.makedirs('logs/prompt', exist_ok=True)

    def _add_console_handler(self, logger):
        """Добавить вывод логов в консоль"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(self.FORMATTER)
        logger.addHandler(console_handler)

    def get_logger_general(self, name_log, log_dir='logs/general'):
        """Логгер для общих сообщений"""
        return self._get_daily_logger(f"{name_log}", log_dir, "general")

    def get_logger_answer(self, name_log, log_dir='logs/answer'):
        """Логгер для ответов"""
        return self._get_daily_logger(f"{name_log}", log_dir, "answer")

    def get_logger_prompt(self, name_log, log_dir='logs/prompt'):
        """Логгер для промптов"""
        return self._get_daily_logger(f"{name_log}", log_dir, "prompt")

    def _get_daily_logger(self, logger_name, log_dir, file_prefix):
        """
        Внутренний метод для создания логгеров с разными именами
        """
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

        # Очищаем существующие обработчики
        if logger.handlers:
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

        # Создаем файл с текущей датой в имени
        current_date = datetime.now().strftime("%Y-%m-%d")
        file_handler = logging.FileHandler(
            filename=os.path.join(log_dir, f"{current_date}_{file_prefix}.log"),
            encoding='utf-8'
        )

        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(self.FORMATTER)

        logger.addHandler(file_handler)
        self._add_console_handler(logger)

        return logger


'''class Logger:
    def __init__(self):
        # CSV формат с разделителем табуляции (легко импортировать в Excel)
        self.FORMATTER = logging.Formatter(
            '%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s',
            "%Y-%m-%d %H:%M:%S"
        )

        # Альтернативный CSV формат с запятыми
        self.CSV_FORMATTER = logging.Formatter(
            '"%(asctime)s","%(name)s","%(levelname)s","%(message)s"',
            "%Y-%m-%d %H:%M:%S"
        )

        # Создаем директории для логов
        os.makedirs('logs', exist_ok=True)
        os.makedirs('logs/general', exist_ok=True)
        os.makedirs('logs/answer', exist_ok=True)
        os.makedirs('logs/prompt', exist_ok=True)

    def get_logger_general(self, name_log):
        """Логгер с ротацией файлов в TSV формате"""
        logger = logging.getLogger(f"{name_log}_general")
        logger.setLevel(logging.INFO)

        if logger.handlers:
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

        handler = TimedRotatingFileHandler(
            filename='logs/general.log',
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )

        handler.setLevel(logging.INFO)
        handler.setFormatter(self.FORMATTER)  # TSV формат
        handler.suffix = "%Y-%m-%d"

        logger.addHandler(handler)
        self._add_console_handler(logger)

        return logger

    def _add_console_handler(self, logger):
        """Вывод в консоль с человеко-читаемым форматом"""
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            "%Y-%m-%d %H:%M:%S"
        )
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

    def get_csv_logger(self, name_log, log_dir='logs/genaral'):
        """Логгер в чистом CSV формате с заголовками"""
        os.makedirs(log_dir, exist_ok=True)

        logger = logging.getLogger(f"{name_log}_csv")
        logger.setLevel(logging.INFO)

        if logger.handlers:
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

        current_date = datetime.now().strftime("%Y-%m-%d")
        csv_file = os.path.join(log_dir, f"{current_date}.csv")

        # Создаем файл с заголовком, если он не существует
        if not os.path.exists(csv_file):
            with open(csv_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'logger_name', 'level', 'message'])

        handler = logging.FileHandler(csv_file, encoding='utf-8')
        handler.setLevel(logging.INFO)
        handler.setFormatter(self.CSV_FORMATTER)

        logger.addHandler(handler)
        self._add_console_handler(logger)
        return logger

    def get_structured_logger(self, name_log, log_dir='logs'):
        """
        Логгер со структурированными данными для анализа
        log_type: 'prompt', 'answer', 'general', 'error'
        """
        os.makedirs(log_dir, exist_ok=True)

        logger = logging.getLogger(f"{name_log}")
        logger.setLevel(logging.INFO)

        if logger.handlers:
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)

        current_date = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(log_dir, f"{current_date}.tsv")

        # Формат для структурированного логирования
        structured_formatter = logging.Formatter(
            '%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s',
            "%Y-%m-%d %H:%M:%S"
        )

        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setLevel(logging.INFO)
        handler.setFormatter(structured_formatter)

        logger.addHandler(handler)
        return logger

    # Методы для разных типов логов с структурированным форматом
    def get_prompt_logger(self, name_log):
        return self.get_structured_logger(name_log, 'logs/prompt')

    def get_answer_logger(self, name_log):
        return self.get_structured_logger(name_log,  'logs/answer')

    def get_general_logger(self, name_log):
        return self.get_structured_logger(name_log, 'logs/general')'''


if __name__ == "__main__":
    '''logger_general = Logger().get_logger_general('all')
    logger_audit = Logger().get_logger_audit('audit')
    logger_for_analytics = Logger().get_logger_for_analytics('db')
    logger_general.info('info_all')
    logger_audit.info('info_audit')
    a = ('contract', 'info')
    logger_for_analytics.info('info2_db %s', a)'''
