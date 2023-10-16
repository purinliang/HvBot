import logging
import unittest

import coloredlogs
from hv_bot.util import logger


class MyTestCase(unittest.TestCase):

    @staticmethod
    def test_init_logger():
        logger.init_logger()
        # To observer the style of DEBUG level
        coloredlogs.set_level("DEBUG")

        logging.debug("test_logger debug")
        logging.info("test_logger info")
        logging.warning("test_logger warning")
        logging.error("test_logger error")
        logging.critical("test_logger critical")


if __name__ == "__main__":
    unittest.main()
