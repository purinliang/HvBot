import logging

from hv_bot.gui import gui_interface, gui_execute, gui_captcha, gui_dialog, gui_finish


def is_battling() -> bool:
    fullscreen_image = gui_execute.get_fullscreen_image()
    if gui_captcha.detected_captcha(fullscreen_image) or gui_finish.detected_finish(
            fullscreen_image) or gui_dialog.detected_dialog(fullscreen_image):
        logging.warning(f"have_captcha_or_finish_or_dialog")
        return True

    character, monster_list = gui_interface.get_info_from_fullscreen_image(fullscreen_image)
    logging.debug(f"is_battling character={character}")
    logging.debug(f"is_battling monster_list={monster_list}")
    return character is not None and monster_list is not None
