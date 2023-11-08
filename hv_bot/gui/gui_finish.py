import logging
import os
import time

import winsound
from PIL import Image

import hv_bot.util.path
from hv_bot.external_communication_controller import send_text, send_image
from hv_bot.gui.gui_execute import have_image, locate_image_and_click, save_fullscreen_image, locate_image


def detected_finish(fullscreen_image: Image) -> bool:
    os.chdir(hv_bot.util.path.ROOT_PATH)
    needle_image = Image.open("res\\finish_battle_button.png")
    if have_image(needle_image, fullscreen_image):
        return True
    needle_image = Image.open("res\\finish_battle_button_blue.png")
    if have_image(needle_image, fullscreen_image):
        return True
    return False


def locate_finish_button(fullscreen_image: Image):
    os.chdir(hv_bot.util.path.ROOT_PATH)
    needle_image = Image.open("res\\finish_battle_button.png")
    if have_image(needle_image, fullscreen_image):
        return locate_image(needle_image, fullscreen_image)
    needle_image = Image.open("res\\finish_battle_button_blue.png")
    if have_image(needle_image, fullscreen_image):
        return locate_image(needle_image, fullscreen_image)
    return None


def click_finish_button(fullscreen_image: Image) -> None:
    time.sleep(0.5)
    os.chdir(hv_bot.util.path.ROOT_PATH)
    needle_image = Image.open("res\\finish_battle_button.png")
    if have_image(needle_image, fullscreen_image):
        locate_image_and_click(needle_image, fullscreen_image)
    needle_image = Image.open("res\\finish_battle_button_blue.png")
    if have_image(needle_image, fullscreen_image):
        locate_image_and_click(needle_image, fullscreen_image)
    return


def click_finish(fullscreen_image: Image) -> None:
    if not detected_finish(fullscreen_image):
        return

    detected_time_stamp = time.time()
    # sample time format: "%Y-%m-%d %H:%M:%S"
    style_time = time.strftime("%H:%M:%S", time.localtime(int(detected_time_stamp)))

    # send text that finish detected
    logging.info("finish detected")

    send_text(f"检测到战斗结束，于{style_time}")
    saved_fullscreen_image_path = save_fullscreen_image("finish")
    send_image(saved_fullscreen_image_path)

    click_finish_button(fullscreen_image)

    # winsound.Beep(600, 600)
    return
