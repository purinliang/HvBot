import logging
import os
import random
import threading
import time

import pyautogui
from PIL import Image

from hv_bot.external_communication_controller import send_text
from hv_bot.gui import gui_battle_continue
from hv_bot.gui.gui_captcha import detected_captcha, handle_captcha
from hv_bot.gui.gui_dialog import detected_dialog, click_dialog
from hv_bot.gui.gui_execute import move_and_hover, move_and_click, get_fullscreen_image, move_relatively_and_hover, \
    have_image
from hv_bot.gui.gui_finish import detected_finish, click_finish
from hv_bot.gui.gui_interface import get_info_from_fullscreen_image, execute_strategy
from hv_bot.identify.character import get_exp
from hv_bot.strategy.strategy_encounter import get_strategy_encounter
from hv_bot.util import logger
from hv_bot.util import path
from hv_bot.util.ocr import ocr_single_line_text

# TODO move them into local
ENCOUNTER_IMAGE_LEFT = 900
ENCOUNTER_IMAGE_TOP = 4
ENCOUNTER_IMAGE_WIDTH = 92
ENCOUNTER_IMAGE_HEIGHT = 18


def _crop_encounter_image(fullscreen_image: Image) -> Image:
    # TODO it seem that some duplicate codes like the following among the project
    box = [ENCOUNTER_IMAGE_LEFT,
           ENCOUNTER_IMAGE_TOP,
           ENCOUNTER_IMAGE_LEFT + ENCOUNTER_IMAGE_WIDTH,
           ENCOUNTER_IMAGE_TOP + ENCOUNTER_IMAGE_HEIGHT]
    encounter_image = fullscreen_image.crop(box)
    return encounter_image


# TODO move them into local
STAMINA_IMAGE_LEFT = 528
STAMINA_IMAGE_TOP = 4
STAMINA_IMAGE_WIDTH = 92
STAMINA_IMAGE_HEIGHT = 18


def _crop_stamina_image(fullscreen_image: Image) -> Image:
    box = [STAMINA_IMAGE_LEFT,
           STAMINA_IMAGE_TOP,
           STAMINA_IMAGE_LEFT + STAMINA_IMAGE_WIDTH,
           STAMINA_IMAGE_TOP + STAMINA_IMAGE_HEIGHT]
    stamina_image = fullscreen_image.crop(box)
    return stamina_image


def _click_encounter() -> None:
    # logging.info(f"click_encounter")
    x = ENCOUNTER_IMAGE_LEFT + ENCOUNTER_IMAGE_WIDTH // 2
    y = ENCOUNTER_IMAGE_TOP + ENCOUNTER_IMAGE_HEIGHT // 2
    move_and_click(x, y, move_duration=0.1, ending_wait_duration=0.75)
    return


def _hover_encounter() -> None:
    # logging.info(f"hover_encounter")
    x = ENCOUNTER_IMAGE_LEFT + ENCOUNTER_IMAGE_WIDTH // 2
    y = ENCOUNTER_IMAGE_TOP + ENCOUNTER_IMAGE_HEIGHT // 2
    move_and_hover(x, y, move_duration=0.5)
    return


ENCOUNTER_FAILED_DIALOG_IMAGE_LEFT = 476
ENCOUNTER_FAILED_DIALOG_IMAGE_TOP = 336
ENCOUNTER_FAILED_DIALOG_IMAGE_WIDTH = 288
ENCOUNTER_FAILED_DIALOG_IMAGE_HEIGHT = 36


def _crop_encounter_failed_dialog_image(fullscreen_image: Image) -> Image:
    box = [ENCOUNTER_FAILED_DIALOG_IMAGE_LEFT,
           ENCOUNTER_FAILED_DIALOG_IMAGE_TOP,
           ENCOUNTER_FAILED_DIALOG_IMAGE_LEFT + ENCOUNTER_FAILED_DIALOG_IMAGE_WIDTH,
           ENCOUNTER_FAILED_DIALOG_IMAGE_TOP + ENCOUNTER_FAILED_DIALOG_IMAGE_HEIGHT]
    encounter_failed_dialog_image = fullscreen_image.crop(box)
    return encounter_failed_dialog_image


def _click_encounter_failed_dialog() -> None:
    logging.info(f"click_encounter_failed_dialog")
    # send_text(f"点击了遭遇战错误弹窗")
    x = ENCOUNTER_FAILED_DIALOG_IMAGE_LEFT + ENCOUNTER_FAILED_DIALOG_IMAGE_WIDTH // 2
    y = ENCOUNTER_FAILED_DIALOG_IMAGE_TOP + ENCOUNTER_FAILED_DIALOG_IMAGE_HEIGHT // 2
    move_and_click(x, y, move_duration=0.5, ending_wait_duration=0.75)
    return


def _detect_dawn_event(fullscreen_image: Image) -> bool:
    os.chdir(path.ROOT_PATH)
    dawn_dialog_image = Image.open("res\\dawn_event.png")
    if have_image(dawn_dialog_image, fullscreen_image):
        logging.info(f"_encounter_dawn_event")
        # send_text(f"检测到黎明事件")
        return True
    return False


def _handle_dawn_event() -> None:
    _click_encounter_failed_dialog()
    logging.info(f"_handle_dawn_event")
    # send_text(f"处理黎明事件")
    time.sleep(3)
    return


def _update_encounter_status(fullscreen_image: Image) -> [str, str]:
    if _detect_dawn_event(fullscreen_image):
        _handle_dawn_event()
        time.sleep(2)

    stamina_image = _crop_stamina_image(fullscreen_image)
    # Sometimes ocr returns Stamina: 58°
    stamina_text = ocr_single_line_text(stamina_image).removesuffix("°")
    if stamina_text.endswith("."):
        stamina_text = stamina_text.removesuffix(".")
    encounter_image = _crop_encounter_image(fullscreen_image)
    # Sometimes ocr returns (29:27 [24]
    encounter_text = ocr_single_line_text(encounter_image).removeprefix("(")
    logging.info(f"update_encounter_status stamina_text={stamina_text}, encounter_text={encounter_text}")
    send_text(f"耐力状态：{stamina_text}，遭遇战状态：{encounter_text}")
    return stamina_text, encounter_text


def _handle_encounter_failed_dialog(retry_times: int, retry_waiting_duration: int) -> bool:
    """handle encounter failed dialog
    to retry up to retry_times, between each 2 retries wait for retry_waiting_duration seconds
    :param retry_times:
    :param retry_waiting_duration:
    :return: whether handling is ok or not
    """
    logging.info(f"handle_encounter_failed_dialog")
    sent_encounter_failed_dialog_text = ""
    for _ in range(retry_times):
        time.sleep(0.75)
        fullscreen_image = get_fullscreen_image()
        encounter_failed_dialog_image = _crop_encounter_failed_dialog_image(fullscreen_image)

        encounter_failed_dialog_image_rgb = encounter_failed_dialog_image.convert("RGB")
        r, g, b = encounter_failed_dialog_image_rgb.getpixel((0, 0))
        if r >= 245 and g >= 245 and b >= 245:
            encounter_failed_dialog_text = ocr_single_line_text(encounter_failed_dialog_image)
            if encounter_failed_dialog_text != sent_encounter_failed_dialog_text:
                # only send same failed_dialog_text once
                logging.info(f"encounter_failed_dialog_text={encounter_failed_dialog_text}")
                send_text(f"遇到了遭遇战错误弹窗：{encounter_failed_dialog_text}")
                sent_encounter_failed_dialog_text = encounter_failed_dialog_text
            if encounter_failed_dialog_text.startswith("Failed"):
                _click_encounter_failed_dialog()
                time.sleep(retry_waiting_duration)
                _click_encounter()
            continue
        else:
            return True
    return False


CHARACTER_MAIN_MENU_BUTTON_X = 94
CHARACTER_MAIN_MENU_BUTTON_Y = 14
CHARACTER_SUB_MENU_BUTTON_X = 58
CHARACTER_SUB_MENU_BUTTON_Y = 46


# def _back_to_main_page() -> None:
#     logging.info(f"back_to_main_page")
#     send_text(f"回到主页面")
#     move_and_hover(CHARACTER_MAIN_MENU_BUTTON_X, CHARACTER_MAIN_MENU_BUTTON_Y,
#                    move_duration=0.5, hover_duration=0.75)
#     move_and_click(CHARACTER_SUB_MENU_BUTTON_X, CHARACTER_SUB_MENU_BUTTON_Y,
#                    move_duration=0.5, ending_wait_duration=0.75)
#     return


def _sleep_for_long_time(sleeping_time: int, event: threading.Event) -> None:
    rest_sleeping_time = sleeping_time
    count_sleeping_time = 0
    while rest_sleeping_time > 0:
        if event.is_set():
            return
        sleeping_time = min(10, rest_sleeping_time)
        rest_sleeping_time -= sleeping_time
        count_sleeping_time += sleeping_time
        time.sleep(sleeping_time)
        logging.debug(f"count_sleeping_time={count_sleeping_time}")

        if count_sleeping_time >= 4 * 60:
            # move the mouse randomly to avoid auto_cut_down screen's power
            logging.debug(f"random move mouse")
            x = random.randint(-5, 5)
            y = random.randint(-5, 5)
            move_relatively_and_hover(x, y, move_duration=0.25, hover_duration=0.5)
            count_sleeping_time = 0
        continue

    return


def start_battle_encounter(event: threading.Event) -> None:
    try:
        _start_battle_encounter(event)
    except pyautogui.FailSafeException as error:
        logging.error(error)
    return


def _start_battle_encounter(event: threading.Event) -> None:
    """
    battle in encounter, until finishing
    :return:
    """
    logging.info(f"start_battle_encounter")
    send_text(f"开始遭遇战自动战斗")

    while True:
        if event.is_set():
            # main thread is requiring to stop
            logging.warning("auto battle encounter, exit by event")
            send_text("遭遇战自动战斗，被主线程命令退出")
            time.sleep(2)
            return
        fullscreen_image = get_fullscreen_image()
        character, monster_list = get_info_from_fullscreen_image(fullscreen_image)

        if character is None or monster_list is None:
            if detected_captcha(fullscreen_image):
                handle_captcha(fullscreen_image)
                logging.warning(f"auto battle encounter, detected_captcha")
                continue
            if detected_dialog(fullscreen_image):
                click_dialog(fullscreen_image)
                logging.warning(f"auto battle encounter, detected_dialog")
                continue
            if detected_finish(fullscreen_image):
                click_finish(fullscreen_image)
                exp = get_exp(fullscreen_image)
                logging.warning(f"auto battle encounter, finished, exit, exp={exp:.2f}%")
                send_text(f"遭遇战自动战斗，战斗已结束，退出，exp={exp:.2f}%")
                time.sleep(2)
                return
            # Maybe there is some network lag
            time.sleep(3)
            continue

        # logging.debug(character)
        # logging.debug(monster_list)

        strategy = get_strategy_encounter(character, monster_list)
        execute_strategy(character, monster_list, strategy)
        continue

    return


def start_once_select_encounter(event: threading.Event) -> None:
    try:
        _start_once_select_encounter(event)
    except pyautogui.FailSafeException as error:
        logging.error(error)
    return


def _is_new_day() -> bool:
    current_time_hour = int(time.strftime("%H", time.localtime(time.time())))
    logging.debug(f"current_time={current_time_hour}")
    if 8 <= current_time_hour <= 12:
        logging.info(f"is new day")
        send_text(f"新的一天")
        return True
    return False


def _start_once_select_encounter(event: threading.Event) -> None:
    """
    if encounter is not ready, do nothing.
    :return:
    """
    logging.info(f"start_once_select_encounter")
    send_text(f"开始单次选择遭遇战")
    while True:
        if event.is_set():
            # main thread is requiring to stop
            return
        time.sleep(0.75)
        fullscreen_image = get_fullscreen_image()
        _, encounter_text = _update_encounter_status(fullscreen_image)
        if encounter_text.endswith("[24]"):
            # daily limit has been reached
            if _is_new_day():
                _click_encounter()
                time.sleep(2)
                continue

            logging.info(f"daily limit 24 times has been reached, exit")
            send_text(f"已到达24次每日上限，退出")
            break
        if encounter_text.startswith("Expired"):
            _click_encounter()
            time.sleep(1)
            continue
        if not encounter_text.startswith("Ready"):
            logging.info(f"failed to select encounter, not ready, exit")
            send_text(f"选择遭遇战失败，没有Ready，退出")
            break

        _hover_wait_and_click_encounter()

        if not _handle_encounter_failed_dialog(retry_times=3, retry_waiting_duration=15):
            logging.info(f"failed to select encounter, failed to handle failed dialog, exit")
            send_text(f"选择遭遇战失败，处理错误弹窗失败，退出")
            break

        time.sleep(2)

        _start_battle_encounter(event)
        time.sleep(2)

        # _back_to_main_page()
        # time.sleep(2)
        break

    return


def start_auto_select_encounter(event: threading.Event) -> None:
    try:
        _start_auto_select_encounter(event)
    except pyautogui.FailSafeException as error:
        logging.error(error)
    return


ENCOUNTER_TEXT_VALUE_ERROR_RETRY_WAITING_TIME_DEFAULT = 15
ENCOUNTER_TEXT_VALUE_ERROR_RETRY_WAITING_TIME = ENCOUNTER_TEXT_VALUE_ERROR_RETRY_WAITING_TIME_DEFAULT


def _start_auto_select_encounter(event: threading.Event) -> None:
    """
    if encounter is not ready, wait for it.
    :return:
    """
    logging.info(f"start_auto_select_encounter")
    send_text(f"开始连续选择遭遇战")

    if gui_battle_continue.is_battling():
        time.sleep(1)
        logging.info(f"the previous battle hasn't ended, battle_continue")
        send_text(f"上次战斗尚未结束，继续战斗")
        _start_battle_encounter(event)

    while True:
        if event.is_set():
            # main thread is requiring to stop
            return
        time.sleep(0.75)
        fullscreen_image = get_fullscreen_image()
        _, encounter_text = _update_encounter_status(fullscreen_image)
        if encounter_text.endswith("[24]"):
            # daily limit has been reached
            if _is_new_day():
                _click_encounter()
                time.sleep(2)
                continue

            sleeping_time = 30 * 60
            logging.info(f"daily limit 24 times has been reached, wait {sleeping_time} seconds")
            send_text(f"已到达24次每日上限，等待 {sleeping_time} 秒")
            _sleep_for_long_time(sleeping_time, event)
            continue
        if encounter_text.startswith("Expired"):
            _click_encounter()
            time.sleep(2)
            continue
        if not encounter_text.startswith("Ready"):
            try:
                rest_time_text = encounter_text.split("[")[0]
                rest_minutes = int(rest_time_text.split(":")[0])
                rest_seconds = int(rest_time_text.split(":")[1])
            except ValueError as error:
                global ENCOUNTER_TEXT_VALUE_ERROR_RETRY_WAITING_TIME
                sleeping_time = ENCOUNTER_TEXT_VALUE_ERROR_RETRY_WAITING_TIME
                logging.error(error)
                logging.error(f"failed to parse encounter rest time, wait {sleeping_time} seconds")
                send_text(f"解析遭遇战剩余时间失败，等待 {sleeping_time} 秒")
                ENCOUNTER_TEXT_VALUE_ERROR_RETRY_WAITING_TIME *= 2
                _sleep_for_long_time(sleeping_time, event)
                continue

            # sleeping_time up to 15 minutes
            sleeping_time = min(rest_minutes * 60 + rest_seconds, 15 * 60)
            logging.info(f"failed to select encounter, not ready, wait {sleeping_time} seconds")
            next_check_time = int(time.time() + sleeping_time)
            style_next_check_time = time.strftime("%H:%M:%S", time.localtime(next_check_time))
            send_text(f"下一次检查时间：{style_next_check_time}")
            _sleep_for_long_time(sleeping_time, event)
            continue

        ENCOUNTER_TEXT_VALUE_ERROR_RETRY_WAITING_TIME = ENCOUNTER_TEXT_VALUE_ERROR_RETRY_WAITING_TIME_DEFAULT
        _hover_wait_and_click_encounter()

        if not _handle_encounter_failed_dialog(retry_times=8, retry_waiting_duration=15):
            sleeping_time = 15 * 60
            logging.info(f"failed to select encounter, failed to handle failed dialog, wait {sleeping_time} seconds")
            send_text(f"选择遭遇战失败，处理错误弹窗失败，等待 {sleeping_time} 秒")
            _sleep_for_long_time(sleeping_time, event)
            continue

        time.sleep(2)

        _start_battle_encounter(event)
        time.sleep(2)

        # _back_to_main_page()
        # time.sleep(2)
        continue

    return


def _hover_wait_and_click_encounter():
    _hover_encounter()
    # the following warning logic is only suitable for auto_select_encounter
    before_clicking_encounter_warning_time = 5
    logging.info(f"click encounter in {before_clicking_encounter_warning_time} seconds, please get ready")
    send_text(f"将在{before_clicking_encounter_warning_time}秒内点击遭遇战，请准备")
    time.sleep(before_clicking_encounter_warning_time)
    _click_encounter()


if __name__ == '__main__':
    logger.init_logger()
    _start_auto_select_encounter(threading.Event())
    # _start_battle_encounter(threading.Event())
