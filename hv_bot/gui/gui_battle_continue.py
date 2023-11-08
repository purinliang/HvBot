import logging

import hv_bot.gui.gui_execute
import hv_bot.gui.gui_interface


def is_battling() -> bool:
    fullscreen_image = hv_bot.gui.gui_execute.get_fullscreen_image()
    character, monster_list = (hv_bot.gui.gui_interface
                               .get_info_from_fullscreen_image(fullscreen_image))
    logging.warning(character)
    logging.warning(monster_list)
    return character is not None and monster_list is not None
