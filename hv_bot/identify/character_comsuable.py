import os
from typing import List

from PIL import Image

import hv_bot.util.path
from hv_bot.gui.gui_execute import have_image

CONSUMABLE_WIDTH = 36
CONSUMABLE_HEIGHT = 36
CONSUMABLE_INTERVAL = 1

FIRST_CONSUMABLE_LEFT_CORNER_X = 40
FIRST_CONSUMABLE_LEFT_CORNER_Y = 193

FIRST_CONSUMABLE_CENTER_X = 56
FIRST_CONSUMABLE_CENTER_Y = 209

CONSUMABLE_LIST = [
    "health_draught",
    "mana_draught",
    "spirit_draught",
    "health_potion",
    "mana_potion",
    "spirit_potion",
    "BLANK",
    "BLANK",
    "BLANK",
    "BLANK",
    "BLANK",
    "BLANK",
    "BLANK",
    "BLANK",
    "BLANK"
]

CONSUMABLE_CENTER_X_LIST = []
CONSUMABLE_LEFT_CORNER_X_LIST = []

GEM_LEFT = 631
GEM_TOP = 154
GEM_WIDTH = 36
GEM_HEIGHT = 36


def crop_gem_image(fullscreen_image: Image) -> Image:  # TODO move the following function into internal
    box = [
        GEM_LEFT,
        GEM_TOP,
        GEM_LEFT + CONSUMABLE_HEIGHT,
        GEM_TOP + CONSUMABLE_HEIGHT
    ]
    gem_image = fullscreen_image.crop(box)
    return gem_image


def calc_gem_status(fullscreen_image: Image) -> str:
    gem_image = crop_gem_image(fullscreen_image)
    PATH = "res\\character\\"
    GEM_TYPE_LIST = ["channelling", "health", "mana", "spirit"]
    for gem_type in GEM_TYPE_LIST:
        os.chdir(hv_bot.util.path.ROOT_PATH)
        needle_image = Image.open(f"{PATH}gem_{gem_type}.png")
        if have_image(needle_image, gem_image):
            return gem_type
    return ""


def get_consumable_list(fullscreenImage) -> List[str]:
    consumable_list = []
    for i in range(len(CONSUMABLE_LIST)):
        left_corner_x = FIRST_CONSUMABLE_LEFT_CORNER_X + i * (CONSUMABLE_WIDTH + CONSUMABLE_INTERVAL)
        left_corner_y = FIRST_CONSUMABLE_LEFT_CORNER_Y

        rgb_image = fullscreenImage.convert("RGB")
        r, g, b = rgb_image.getpixel((left_corner_x, left_corner_y))
        total_bright = r + g + b
        # print('total_bright=' + str(total_bright))
        if total_bright <= 440:  # background=690，have_consumable=190
            consumable_list.append(CONSUMABLE_LIST[i])
    return consumable_list


def _calc_consumable_center_x_list() -> None:
    if len(CONSUMABLE_CENTER_X_LIST) > 0:
        return
    CONSUMABLE_CENTER_X_LIST.clear()
    x = FIRST_CONSUMABLE_CENTER_X
    for _ in CONSUMABLE_LIST:
        CONSUMABLE_CENTER_X_LIST.append(x)
        x += CONSUMABLE_WIDTH + CONSUMABLE_INTERVAL
    return
    # print(CONSUMABLE_X_LIST)


def _calc_consumable_left_top_corner_x_list() -> None:
    if len(CONSUMABLE_LEFT_CORNER_X_LIST) > 0:
        return
    CONSUMABLE_LEFT_CORNER_X_LIST.clear()
    x = FIRST_CONSUMABLE_LEFT_CORNER_X
    for _ in CONSUMABLE_LIST:
        CONSUMABLE_LEFT_CORNER_X_LIST.append(x)
        x += CONSUMABLE_WIDTH + CONSUMABLE_INTERVAL
    # print(CONSUMABLE_X_LIST)
    return


def _calc_consumable_location_from_name(consumable_name: str) -> [int, int]:
    if len(CONSUMABLE_CENTER_X_LIST) == 0:
        _calc_consumable_center_x_list()
    for i in range(len(CONSUMABLE_LIST)):
        if consumable_name == CONSUMABLE_LIST[i]:
            return [CONSUMABLE_CENTER_X_LIST[i], FIRST_CONSUMABLE_CENTER_Y]
    return [-1, -1]


def calc_consumable_left_top_corner_location_from_name(consumable_name: str) -> [int, int]:
    if len(CONSUMABLE_LEFT_CORNER_X_LIST) == 0:
        _calc_consumable_left_top_corner_x_list()
    for i in range(len(CONSUMABLE_LIST)):
        if consumable_name == CONSUMABLE_LIST[i]:
            return CONSUMABLE_LEFT_CORNER_X_LIST[i], FIRST_CONSUMABLE_LEFT_CORNER_Y
    return [-1, -1]
