import logging
import os
import threading
import unittest
from multiprocessing import Queue
from unittest.mock import patch, MagicMock

import hv_bot.main_controller
import hv_bot.util.path
from hv_bot import main_controller, external_communication_controller
from hv_bot.util import logger

mock_time_sleep = MagicMock()


class MyTestCase(unittest.TestCase):
    def test_send_text(self):
        to_queue = Queue()
        external_communication_controller.set_to_queue(to_queue)
        external_communication_controller.send_text("test_text")
        to_queue_data = {"op": "send_text", "text": "test_text"}
        self.assertDictEqual(to_queue_data, external_communication_controller.get_to_queue().get_nowait())

    def test_send_image(self):
        to_queue = Queue()
        external_communication_controller.set_to_queue(to_queue)
        external_communication_controller.send_image("test_image_path")
        to_queue_data = {"op": "send_image", "image_path": "test_image_path"}
        self.assertDictEqual(to_queue_data, external_communication_controller.get_to_queue().get_nowait())

    @staticmethod
    @patch("time.sleep", mock_time_sleep)
    def test_main():
        event = threading.Event()
        from_queue = Queue()
        to_queue = Queue()
        # from_queue.put({"cmd": "start arena"})
        from_queue.put({"cmd": "unknown"})
        from_queue.put({"cmd": "close"})
        main_controller.main(event, from_queue, to_queue)

    def setUp(self) -> None:
        logger.init_logger()
        logging.getLogger().setLevel(logging.DEBUG)
        logging.error("------")
        os.chdir(hv_bot.util.path.ROOT_PATH)


if __name__ == "__main__":
    unittest.main()
