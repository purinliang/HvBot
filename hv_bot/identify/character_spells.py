import os

from PIL import Image

import hv_bot.util.path
from hv_bot.gui.gui_execute import locate_image


def _get_spell_location(status_bar_image: Image, status_name: str):
    os.chdir(hv_bot.util.path.ROOT_PATH)
    needle_image = Image.open(f"res\\character\\spells\\{status_name}.png")
    return locate_image(needle_image, status_bar_image)


SPELL_WIDTH = 36
SPELL_INTERVAL = 1

FIRST_SPELL_CENTER_X = 56
FIRST_SPELL_CENTER_Y = 171


def calc_spell_location_from_index(index: int) -> [int, int]:
    if index == -1:
        return [-1, -1]
    x = FIRST_SPELL_CENTER_X + (SPELL_WIDTH + SPELL_INTERVAL) * index
    y = FIRST_SPELL_CENTER_Y
    return [x, y]


def _get_spell_index(status_bar_image: Image, status_name: str) -> int:
    location = _get_spell_location(status_bar_image, status_name)
    if location is None:
        return -1
    index = location.left // (SPELL_WIDTH + SPELL_INTERVAL)
    return index


def get_spell_list(spell_bar_image: Image):
    check_list = ["regen", "heartseeker",
                  "protection", "spark_of_life", "haste", "spirit_shield", "shadow_veil",
                  "imperil", "weaken", "silence", "cure",
                  "orbital_friendship_cannon", "cooldown_orbital_friendship_cannon",
                  "shield_bash", "cooldown_shield_bash", "vital_strike", "cooldown_vital_strike"]
    spell_list = []
    for spell_name in check_list:
        spell_index = _get_spell_index(spell_bar_image, spell_name)
        spell_list.append([spell_name, spell_index])
    return spell_list


SPELL_BAR_BOX_LEFT = 38
SPELL_BAR_BOX_TOP = 153
SPELL_BAR_BOX_WIDTH = 593
SPELL_BAR_BOX_HEIGHT = 38


def crop_spell_bar_image(fullscreen_image: Image) -> Image:
    box = [
        SPELL_BAR_BOX_LEFT,
        SPELL_BAR_BOX_TOP,
        SPELL_BAR_BOX_LEFT + SPELL_BAR_BOX_WIDTH,
        SPELL_BAR_BOX_TOP + SPELL_BAR_BOX_HEIGHT
    ]

    spell_bar_image = fullscreen_image.crop(box)
    return spell_bar_image
