import os
from typing import List

from PIL import Image

import hv_bot.util.path
from hv_bot.gui.gui_execute import have_image, locate_image

STATUS_BAR_BOX_LEFT = 99
STATUS_BAR_BOX_TOP = 9
STATUS_BAR_BOX_WIDTH = 480
STATUS_BAR_BOX_HEIGHT = 38


def crop_status_bar_image(fullscreen_image: Image) -> Image:
    box = [
        STATUS_BAR_BOX_LEFT,
        STATUS_BAR_BOX_TOP,
        STATUS_BAR_BOX_LEFT + STATUS_BAR_BOX_WIDTH,
        STATUS_BAR_BOX_TOP + STATUS_BAR_BOX_HEIGHT
    ]

    status_bar_image = fullscreen_image.crop(box)
    return status_bar_image


def get_status(status_bar_image: Image, status_name: str) -> [bool, int]:
    os.chdir(hv_bot.util.path.ROOT_PATH)
    needle_image = Image.open(f"res\\character\\status\\{status_name}.png")
    if not have_image(needle_image, status_bar_image):
        return [False, -1]
    location = locate_image(needle_image, status_bar_image)
    return [True, location.left]


def get_status_list(status_bar_image: Image) -> List[str]:
    # don't change the following positions, status prefixing with "auto_" must be the first
    check_list = ["auto_spirit_shield", "auto_spark_of_life", "auto_haste", "auto_protection", "auto_shadow_veil",
                  "spirit_shield", "spark_of_life", "haste", "protection", "shadow_veil",
                  "regen", "heartseeker",
                  "channelling", 'mana_draught', "health_draught", "spirit_draught"]
    status_list = []
    for status_name in check_list:
        attend, x = get_status(status_bar_image, status_name)
        if attend:
            # status prefixing with "auto_" have specific position, assign them manually
            match status_name:
                case "auto_spirit_shield":
                    x = -5
                case "auto_spark_of_life":
                    x = -4
                case "auto_shadow_veil":
                    x = -3
                case "auto_haste":
                    x = -2
                case "auto_protection":
                    x = -1
            status_list.append([x, status_name])  # TODO identify countdown
            if status_name in ["auto_spirit_shield", "auto_spark_of_life",
                               "auto_haste", "auto_protection", "auto_shadow_veil"]:
                # if status prefixing with "auto_" attend, add the same status without "auto_" prefix
                status_list.append([x, status_name.removeprefix("auto_")])
    status_list.sort()
    result = []
    for x, status_name in status_list:
        if result.count(status_name) > 0:
            # skip the status that already attended, works for "auto_" status
            continue
        result.append(status_name)
    return result
