import logging
import os
import random
import time

import pyautogui
from PIL import Image

import hv_bot.util.path

pyautogui.PAUSE = 0.1  # duration between two actions that pyautogui imposes
pyautogui.FAILSAFE = True  # if set, move mouse to the corner of main screen will raise pyautogui.FailSafeException


def get_fullscreen_image() -> Image:
    fullscreen_image: Image = None

    # the following two lines are used for test
    # os.chdir(hv_bot.util.path.ROOT_PATH)
    # fullscreen_image = Image.open(r"res/enemies/monster_list_sample_dragons.png")

    if fullscreen_image is None:
        # if no test image, use screenshot to instead
        screenshot_image: Image = pyautogui.screenshot()
        fullscreen_image = crop_fullscreen_image(screenshot_image)

    # fullscreen_image.show()
    return fullscreen_image


def save_fullscreen_image(image_name_prefix: str) -> str:
    fullscreen_image = get_fullscreen_image()

    current_time = int(time.time())
    # sample time format: "%Y-%m-%d %H:%M:%S"
    style_time = time.strftime("%m%d_%H%M%S", time.localtime(current_time))

    saves_dir_path = hv_bot.util.path.get_saves_dir_path()
    image_path = os.path.join(saves_dir_path, f"{image_name_prefix}_{style_time}.png")
    fullscreen_image.save(image_path)
    cwd = os.getcwd()
    full_path = os.path.join(cwd, image_path)
    logging.info(f"save_fullscreen_image full_path={full_path}")
    return full_path


FULLSCREEN_LEFT = 2
FULLSCREEN_TOP = 111
FULLSCREEN_WIDTH = 1238
FULLSCREEN_HEIGHT = 704


def crop_fullscreen_image(screenshot_image: Image):
    box = [
        FULLSCREEN_LEFT,
        FULLSCREEN_TOP,
        FULLSCREEN_LEFT + FULLSCREEN_WIDTH,
        FULLSCREEN_TOP + FULLSCREEN_HEIGHT
    ]
    fullscreen_image = screenshot_image.crop(box)
    return fullscreen_image


def _add_offset(x: int, y: int) -> [int, int]:
    return [x + FULLSCREEN_LEFT, y + FULLSCREEN_TOP]


def move_relatively_and_hover(x: int, y: int, *, move_duration: float = 0.0, hover_duration: float = 0.0) -> None:
    x, y = _add_offset(x, y)
    rx = random.randint(-3, 3)
    ry = random.randint(-3, 3)
    try:
        pyautogui.moveRel(x + rx, y + ry, duration=move_duration)
    except pyautogui.FailSafeException as error:
        # relatively moving will raise pyautogui.FailSafeException, ignore it
        logging.error(error)
    if hover_duration > 0.0:
        time.sleep(hover_duration)
    return


def move_and_hover(x: int, y: int, *, move_duration: float = 0.0, hover_duration: float = 0.0) -> None:
    x, y = _add_offset(x, y)
    rx = random.randint(-3, 3)
    ry = random.randint(-3, 3)
    pyautogui.moveTo(x + rx, y + ry, duration=move_duration)
    if hover_duration > 0.0:
        time.sleep(hover_duration)
    return


def move_and_click(x: int, y: int, *, move_duration: float = 0.0, ending_wait_duration: float = 0.0) -> None:
    x, y = _add_offset(x, y)
    rx = random.randint(-3, 3)
    ry = random.randint(-3, 3)
    pyautogui.click(x + rx, y + ry, duration=move_duration)
    if ending_wait_duration > 0.0:
        time.sleep(ending_wait_duration)
    return


def have_image(needle_image, haystack_image, *, confidence=None) -> bool:
    return locate_image(needle_image, haystack_image, confidence=confidence) is not None


def locate_image(needle_image, haystack_image, *, confidence=None):
    if confidence is None:
        return pyautogui.locate(needle_image, haystack_image)
    return pyautogui.locate(needle_image, haystack_image, confidence=confidence)


def locate_image_and_click(needle_image, haystack_image, *, confidence=None) -> None:
    if not have_image(needle_image, haystack_image, confidence=confidence):
        return
    location = locate_image(needle_image, haystack_image, confidence=confidence)
    x = location.left + location.width // 2
    y = location.top + location.height // 2
    move_and_click(x, y)
    return


def locate_image_and_hover(needle_image, haystack_image, *, confidence=None) -> None:
    if not have_image(needle_image, haystack_image, confidence=confidence):
        return
    location = locate_image(needle_image, haystack_image, confidence=confidence)
    x = location.left + location.width // 2
    y = location.top + location.height // 2
    move_and_hover(x, y)
    return
