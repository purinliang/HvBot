import logging
import os
import unittest
from multiprocessing import Queue
from unittest.mock import MagicMock, patch

from PIL import Image

import hv_bot.gui.gui_captcha
from hv_bot import external_communication_controller
from hv_bot.util import logger

captcha_image_path = r"res\captcha_test_1.png"
no_captcha_image_path = r"res\screenshot_1012_011343.png"

mock_time_sleep = MagicMock()
mock_winsound_beep = MagicMock()

mock_save_fullscreen_image = MagicMock(return_value=captcha_image_path)
mock_get_fullscreen_image_has_captcha = MagicMock(return_value=Image.open(captcha_image_path))
mock_get_fullscreen_image_has_not_captcha = MagicMock(return_value=Image.open(no_captcha_image_path))

mock_clear_sub_from_queue = MagicMock()
mock_wrap_handle_answer_from_sub_from_queue = MagicMock(wraps=hv_bot.gui.gui_captcha._handle_answer_from_sub_from_queue)
mock_wrap_submit_captcha = MagicMock(wraps=hv_bot.gui.gui_captcha._submit_captcha)
mock_wrap_report_captcha_submitted = MagicMock(wrapss=hv_bot.gui.gui_captcha._report_captcha_submitted)
mock_wrap_report_captcha_timeout = MagicMock(wraps=hv_bot.gui.gui_captcha._report_captcha_timeout)
mock_captcha_time_limitation = 2
mock_captcha_time_submit_limitation = 0.5


class MyTestCase(unittest.TestCase):

    # the functions in the same module can be mocked and used directly
    # however, the functions in other modules should be used in module_name.function_name
    # otherwise, the mocked functions will not work
    #
    # maybe coding in Google Code Style can avoid this problem

    @patch("time.sleep", mock_time_sleep)
    @patch("winsound.Beep", mock_winsound_beep)
    @patch("hv_bot.gui.gui_execute.get_fullscreen_image", mock_get_fullscreen_image_has_captcha)
    @patch("hv_bot.gui.gui_execute.save_fullscreen_image", mock_save_fullscreen_image)
    @patch("hv_bot.gui.gui_captcha._submit_captcha", mock_wrap_submit_captcha)
    @patch("hv_bot.gui.gui_captcha._handle_answer_from_sub_from_queue", mock_wrap_handle_answer_from_sub_from_queue)
    @patch("hv_bot.gui.gui_captcha._report_captcha_submitted", mock_wrap_report_captcha_submitted)
    @patch("hv_bot.gui.gui_captcha._report_captcha_timeout", mock_wrap_report_captcha_timeout)
    @patch("hv_bot.gui.gui_captcha.CAPTCHA_TIME_LIMITATION", mock_captcha_time_limitation)
    @patch("hv_bot.gui.gui_captcha.CAPTCHA_TIME_SUBMIT_LIMITATION", mock_captcha_time_submit_limitation)
    def test_handle_captcha_clear_sub_from_queue(self):
        sub_from_queue = Queue()
        external_communication_controller.set_sub_from_queue(sub_from_queue)
        sub_from_queue.put({"op": "receive_poll_result", "poll_result": ["Twilight Sparkle", "Pinkie Pie"]})

        fullscreen_image = Image.open(captcha_image_path)
        hv_bot.gui.gui_captcha.handle_captcha(fullscreen_image)

        self.assertGreater(mock_wrap_handle_answer_from_sub_from_queue.call_count, 5)
        self.assertEqual(mock_wrap_report_captcha_submitted.call_count, 0)
        self.assertEqual(mock_wrap_report_captcha_timeout.call_count, 1)

    @patch("time.sleep", mock_time_sleep)
    @patch("winsound.Beep", mock_winsound_beep)
    @patch("hv_bot.gui.gui_execute.get_fullscreen_image", mock_get_fullscreen_image_has_not_captcha)
    @patch("hv_bot.gui.gui_execute.save_fullscreen_image", mock_save_fullscreen_image)
    @patch("hv_bot.gui.gui_captcha._submit_captcha", mock_wrap_submit_captcha)
    @patch("hv_bot.gui.gui_captcha._clear_sub_from_queue", mock_clear_sub_from_queue)
    @patch("hv_bot.gui.gui_captcha._handle_answer_from_sub_from_queue", mock_wrap_handle_answer_from_sub_from_queue)
    @patch("hv_bot.gui.gui_captcha._report_captcha_submitted", mock_wrap_report_captcha_submitted)
    @patch("hv_bot.gui.gui_captcha._report_captcha_timeout", mock_wrap_report_captcha_timeout)
    @patch("hv_bot.gui.gui_captcha.CAPTCHA_TIME_LIMITATION", mock_captcha_time_limitation)
    @patch("hv_bot.gui.gui_captcha.CAPTCHA_TIME_SUBMIT_LIMITATION", mock_captcha_time_submit_limitation)
    def test_handle_captcha_submitted_by_command(self):
        sub_from_queue = Queue()
        external_communication_controller.set_sub_from_queue(sub_from_queue)
        sub_from_queue.put({"op": "receive_poll_result", "poll_result": ["Twilight Sparkle", "Pinkie Pie"]})

        fullscreen_image = Image.open(captcha_image_path)
        hv_bot.gui.gui_captcha.handle_captcha(fullscreen_image)

        self.assertEqual(mock_wrap_handle_answer_from_sub_from_queue.call_count, 1)
        self.assertEqual(mock_wrap_report_captcha_submitted.call_count, 1)
        self.assertEqual(mock_wrap_report_captcha_timeout.call_count, 0)
        self.assertEqual(mock_wrap_submit_captcha.call_count, 1)
        mock_wrap_submit_captcha.assert_called_with([0, 4])

    @patch("time.sleep", mock_time_sleep)
    @patch("winsound.Beep", mock_winsound_beep)
    @patch("hv_bot.gui.gui_execute.save_fullscreen_image", mock_save_fullscreen_image)
    @patch("hv_bot.gui.gui_execute.get_fullscreen_image", mock_get_fullscreen_image_has_captcha)
    @patch("hv_bot.gui.gui_captcha._submit_captcha", mock_wrap_submit_captcha)
    @patch("hv_bot.gui.gui_captcha._clear_sub_from_queue", mock_clear_sub_from_queue)
    @patch("hv_bot.gui.gui_captcha._handle_answer_from_sub_from_queue", mock_wrap_handle_answer_from_sub_from_queue)
    @patch("hv_bot.gui.gui_captcha._report_captcha_submitted", mock_wrap_report_captcha_submitted)
    @patch("hv_bot.gui.gui_captcha._report_captcha_timeout", mock_wrap_report_captcha_timeout)
    @patch("hv_bot.gui.gui_captcha.CAPTCHA_TIME_LIMITATION", mock_captcha_time_limitation)
    @patch("hv_bot.gui.gui_captcha.CAPTCHA_TIME_SUBMIT_LIMITATION", mock_captcha_time_submit_limitation)
    def test_handle_captcha_auto_submitted(self):
        sub_from_queue = Queue()
        external_communication_controller.set_sub_from_queue(sub_from_queue)

        fullscreen_image = Image.open(captcha_image_path)
        hv_bot.gui.gui_captcha.handle_captcha(fullscreen_image)

        self.assertGreater(mock_wrap_handle_answer_from_sub_from_queue.call_count, 5)
        self.assertEqual(mock_wrap_report_captcha_submitted.call_count, 0)
        self.assertEqual(mock_wrap_report_captcha_timeout.call_count, 1)

    def setUp(self) -> None:
        logger.init_logger()
        logging.getLogger().setLevel(logging.DEBUG)
        logging.error("------")

    def tearDown(self) -> None:
        DIR_PATH = os.path.dirname(os.path.realpath(__file__))
        os.chdir(DIR_PATH)
        mock_wrap_handle_answer_from_sub_from_queue.reset_mock()
        mock_wrap_report_captcha_submitted.reset_mock()
        mock_wrap_report_captcha_timeout.reset_mock()
        mock_wrap_submit_captcha.reset_mock()


if __name__ == "__main__":
    unittest.main()
