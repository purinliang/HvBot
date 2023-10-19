import logging
import os
import time

from PIL import Image

import hv_bot.util.path
from hv_bot.external_communication_controller import send_text, send_image
from hv_bot.gui.gui_execute import have_image, locate_image_and_click, save_fullscreen_image, locate_image_and_hover


def detected_dialog(fullscreen_image: Image) -> bool:
    os.chdir(hv_bot.util.path.ROOT_PATH)
    needle_image = Image.open("res\\dialog_confirm_button.png")
    return have_image(needle_image, fullscreen_image)


def _hover_dialog_confirm_button(fullscreen_image: Image) -> None:
    os.chdir(hv_bot.util.path.ROOT_PATH)
    needle_image = Image.open("res\\dialog_confirm_button.png")
    locate_image_and_hover(needle_image, fullscreen_image)
    return


def _click_dialog_confirm_button(fullscreen_image: Image) -> None:
    os.chdir(hv_bot.util.path.ROOT_PATH)
    needle_image = Image.open("res\\dialog_confirm_button.png")
    locate_image_and_click(needle_image, fullscreen_image)
    return


def click_dialog(fullscreen_image: Image, *, report=True) -> None:
    if not detected_dialog(fullscreen_image):
        return

    detected_time_stamp = time.time()
    # sample time format: "%Y-%m-%d %H:%M:%S"
    style_time = time.strftime("%H:%M:%S", time.localtime(int(detected_time_stamp)))

    # send text that dialog detected
    logging.info("dialog detected")
    if report:
        send_text(f"检测到弹窗，于{style_time}")
        saved_fullscreen_image_path = save_fullscreen_image("dialog")
        send_image(saved_fullscreen_image_path)

    _click_dialog_confirm_button(fullscreen_image)
    return


def hover_dialog(fullscreen_image: Image) -> None:
    if not detected_dialog(fullscreen_image):
        return
    _hover_dialog_confirm_button(fullscreen_image)
    return
