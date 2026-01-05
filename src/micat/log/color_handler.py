# © 2024-2026 Fraunhofer-Gesellschaft e.V., München
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import logging
import sys


class ColorHandler(logging.StreamHandler):
    def __init__(self, stream=sys.stdout):
        super().__init__(stream)
        self._msg_colors = {
            logging.DEBUG: 32,  # "green",
            logging.INFO: 0,  # white "white",
            logging.WARNING: 33,  # "yellow",
            logging.ERROR: 31,  # "red"
        }

    def emit(self, record):
        color = self._msg_colors.get(record.levelno, 0)
        text = record.msg
        message = f'\x1b[{color};1m{text}\x1b[0m\n'
        try:
            self.stream.write(message)
        except BrokenPipeError:
            print(message)
