import logging
import os

from PIL import Image

import hv_bot.gui.gui_execute
from hv_bot.util import ocr
from hv_bot.util import logger
from hv_bot.util import path
from hv_bot.gui import gui_finish


def parse_material_prices():
    fullscreen_image = hv_bot.gui.gui_execute.get_fullscreen_image()
    # fullscreen_image.show()
    # hv_bot.gui.gui_execute.save_fullscreen_image("material")
    LEFT = 360
    TOP = 106


def open_finish_images():
    saves_dir_path = path.get_saves_dir_path()
    listdir = os.listdir(saves_dir_path)
    logging.warning(listdir)
    dict_drops_sum_up = {}
    for file_name in listdir:
        if not file_name.startswith("finish"):
            continue
        logging.error("------")
        full_path = os.path.join(saves_dir_path, file_name)
        finish_image = Image.open(full_path)
        dict_drops = parse_drops(finish_image)

        for name in dict_drops:
            num_int = dict_drops[name]
            if name not in dict_drops_sum_up:
                dict_drops_sum_up[name] = 0
            dict_drops_sum_up[name] += num_int

    logging.error("------")
    logging.warning(dict_drops_sum_up)


def parse_drops(fullscreen_image: Image):
    # fullscreen_image: Image = hv_bot.gui.gui_execute.get_fullscreen_image()
    # fullscreen_image.show()
    # hv_bot.gui.gui_execute.save_fullscreen_image("material")
    finish_button_location = gui_finish.locate_finish_button(fullscreen_image)
    LEFT = 740
    TOP = 39 + finish_button_location.top
    WIDTH = 280
    HEIGHT = 12
    drop_dict = {}
    for i in range(30):
        BOX = [
            LEFT,
            TOP + i * HEIGHT,
            LEFT + WIDTH,
            TOP + (i + 1) * HEIGHT
        ]
        single_line: Image = fullscreen_image.crop(BOX)
        # single_line.show()
        text = ocr.ocr_single_line_text(single_line)

        for _ in range(3):
            text = text.removeprefix("(")
            text = text.removeprefix("‘")
            text = text.removesuffix(".")
            text = text.removesuffix("\"")
            text = text.removesuffix("”")
            text = text.removesuffix("_")
            text = text.removesuffix("|")
            text = text.removesuffix(" ")

        if text.startswith("Ix"):
            text = text.replace("Ix", "1x", 1)
        if text.startswith("§"):
            text = text.replace("§", "5", 1)

        logging.info(text)

        num_text, name = text.split(" ", maxsplit=1)
        num_text: str = num_text.removesuffix("x")
        num_text = num_text.replace(",", "")
        num_text = num_text.replace(".", "")
        num_int = int(num_text)
        drop_dict[name] = num_int

        if text.endswith("EXP"):
            break

    logging.warning(drop_dict)
    return drop_dict


if __name__ == "__main__":
    logger.init_logger()
    open_finish_images()
