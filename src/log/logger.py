# © 2024 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import inspect
import logging
import time

from log.color_handler import ColorHandler


class Logger:
    wrapped_logger = None

    def __init__(self, is_active=True):
        self._is_active = is_active
        self._start_time = 0
        if Logger.wrapped_logger is None:
            Logger.wrapped_logger = Logger._create_logger()

    @staticmethod
    def info(message):
        logger = Logger()
        func = inspect.currentframe().f_back.f_code
        logger.log_info(message, func)

    @staticmethod
    def warn(message):
        logger = Logger()
        func = inspect.currentframe().f_back.f_code
        logger.log_warn(str(message), func)

    @staticmethod
    def error(message):
        logger = Logger()
        func = inspect.currentframe().f_back.f_code
        logger.log_error(str(message), func)

    @staticmethod
    def _current_time_in_ms():
        return int(round(time.time() * 1000))

    @staticmethod
    def _create_logger():
        # If you do not see any logging output while running tests in PyCharm,
        # add the -s option as "Additional arguments" in the PyCharm run configuration or
        # in pyproject.toml under  [tool.pytest.ini_options] => addopts
        logger = logging.getLogger('micat')
        logger.propagate = 0
        logger.setLevel(logging.DEBUG)

        # log_handler = logging.StreamHandler(stream=sys.stdout)
        log_handler = ColorHandler()

        log_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', "%H:%M:%S")
        log_handler.setFormatter(formatter)
        logger.addHandler(log_handler)

        return logger

    def log_info(self, message='', func=None):
        if self._is_active:
            if func is None:
                func = inspect.currentframe().f_back.f_code
            link = 'File "' + func.co_filename + '", line ' + str(func.co_firstlineno)
            full_message = message + ' :\n' + func.co_name + ' in ' + link
            Logger.wrapped_logger.info(full_message)

    def log_warn(self, message='', func=None):
        if self._is_active:
            if func is None:
                func = inspect.currentframe().f_back.f_code
            link = 'File "' + func.co_filename + '", line ' + str(func.co_firstlineno)
            full_message = message + ' :\n' + func.co_name + ' in ' + link
            Logger.wrapped_logger.warning(full_message)

    def log_error(self, message='', func=None):
        if self._is_active:
            if func is None:
                func = inspect.currentframe().f_back.f_code
            link = 'File "' + func.co_filename + '", line ' + str(func.co_firstlineno)
            full_message = message + ' :\n' + func.co_name + ' in ' + link
            Logger.wrapped_logger.error(full_message)

    def start_timer(self):
        if self._is_active:
            self._start_time = self._current_time_in_ms()

    def info_elapsed_time(self, message=''):
        if self._is_active:
            current_time = self._current_time_in_ms()
            self.log_info(message + str(current_time - self._start_time) + ' ms')
