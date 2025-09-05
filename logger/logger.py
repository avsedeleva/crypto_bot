import logging
import sys
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


class Logger:
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
        return logger





if __name__ == "__main__":
    '''logger_general = Logger().get_logger_general('all')
    logger_audit = Logger().get_logger_audit('audit')
    logger_for_analytics = Logger().get_logger_for_analytics('db')
    logger_general.info('info_all')
    logger_audit.info('info_audit')
    a = ('contract', 'info')
    logger_for_analytics.info('info2_db %s', a)'''
