import sys
import logging


class AuditLog:

    def __init__(self):
        self.error_message = None
        self.info_message = None
        self.file = None

    def create_log_file(self):
        self.file = logging.basicConfig(filename="script.log", format='%(asctime)s: %(levelname)s: %(message)s', level=logging.INFO,
                                        filemode='w')

    def logging_info(self, info_message):
        self.info_message = info_message
        logging.info(self.info_message)

    def logging_warning(self, info_message):
        self.info_message = info_message
        logging.warning(self.info_message)

    def logging_error(self, error_message):
        self.error_message = error_message
        logging.error(self.error_message )
        sys.exit(self.error_message)
