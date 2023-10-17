import logging
import os
import unittest

from PIL import Image

from hv_bot.gui.gui_interface import get_info_from_fullscreen_image
from hv_bot.strategy import lowest_level_strategy_common
from hv_bot.util import logger


class MyTestCase(unittest.TestCase):
    def test_find_attack_max_hp_target_index(self):
        fullscreen_image = Image.open(r"res\screenshot_1012_021701.png")
        character, monster_list = get_info_from_fullscreen_image(fullscreen_image)
        index = lowest_level_strategy_common.find_attack_max_hp_target_index(monster_list)
        logging.info(f"index={index}")
        self.assertTrue(index == 0)

    def test_find_attack_max_deterrent_target_index(self):
        fullscreen_image = Image.open(r"res\screenshot_1010_123441.png")
        character, monster_list = get_info_from_fullscreen_image(fullscreen_image)
        index = lowest_level_strategy_common.find_attack_max_deterrent_target_index(monster_list)
        logging.info(f"index={index}")
        self.assertTrue(index == 3)

    def setUp(self) -> None:
        logger.init_logger()
        logging.getLogger().setLevel(logging.DEBUG)
        logging.error("------")

    def tearDown(self) -> None:
        DIR_PATH = os.path.dirname(os.path.realpath(__file__))
        os.chdir(DIR_PATH)


if __name__ == "__main__":
    unittest.main()
