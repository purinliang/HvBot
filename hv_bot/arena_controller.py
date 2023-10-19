import logging
import threading
import time

import pyautogui
from PIL import Image

import hv_bot
from hv_bot.encounter_controller import _start_auto_select_encounter, _start_once_select_encounter
from hv_bot.external_communication_controller import send_text, send_image
from hv_bot.gui.gui_captcha import detected_captcha, handle_captcha
from hv_bot.gui.gui_dialog import detected_dialog, click_dialog, hover_dialog
from hv_bot.gui.gui_execute import save_fullscreen_image
from hv_bot.gui.gui_finish import detected_finish, click_finish
from hv_bot.gui.gui_interface import get_info_from_fullscreen_image, execute_strategy
from hv_bot.identify.character import Character, get_exp
from hv_bot.identify.monster_list import MonsterList
from hv_bot.strategy.strategy_arena import get_strategy_arena
from hv_bot.util import logger

LAST_START_ARENA_X = 1163
LAST_START_ARENA_Y = 566
START_ARENA_INTERVAL_Y = 36

ARENA_MENU_X = 398
ARENA_MENU_Y = 12


def click_arena_menu() -> None:
    hv_bot.gui.gui_execute.move_and_click(ARENA_MENU_X, ARENA_MENU_Y, move_duration=0.75, ending_wait_duration=1.0)
    time.sleep(2.5)
    return


def ordinal(n: int) -> str:
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix


LAST_ORBITAL_TIME = 0.0
LAST_NEW_ROUND_TIME = 0.0


def is_new_round(character: Character, monster_list: MonsterList) -> bool:
    global LAST_ORBITAL_TIME
    global LAST_NEW_ROUND_TIME

    current_time = time.time()
    if (current_time - LAST_ORBITAL_TIME >= 12.0 and
            (not character.have_spell("cooldown_orbital_friendship_cannon")
             and not character.have_spell("orbital_friendship_cannon"))):
        # after using "orbital_friendship_cannon", remove the counting duration check
        LAST_NEW_ROUND_TIME = 0
        LAST_ORBITAL_TIME = current_time

    for monster in monster_list.monsters:
        if monster.dead or monster.hp <= 0.975 or len(monster.status_list) > 0:
            # it is not new round yet, remove the counting duration check
            LAST_NEW_ROUND_TIME = 0
            return False

    if current_time - LAST_NEW_ROUND_TIME <= 5.0:
        # check duration to avoid counting new round multiple times
        return False

    LAST_NEW_ROUND_TIME = current_time
    return True


def start_once_select_arena(event: threading.Event) -> None:
    try:
        _start_once_select_arena(event)
    except pyautogui.FailSafeException as error:
        logging.error(error)
    return


def _start_once_select_arena(event: threading.Event) -> bool:
    fullscreen_image: Image = hv_bot.gui.gui_execute.get_fullscreen_image()
    current_time_stamp = time.time()
    # sample time format: "%Y-%m-%d %H:%M:%S"
    style_time = time.strftime("%H:%M:%S", time.localtime(int(current_time_stamp)))
    logging.info("start_once_select_arena")
    send_text(f"开始单次选择竞技场")

    # if current state is finished battle, exit it
    if detected_finish(fullscreen_image):
        click_finish(fullscreen_image)
        time.sleep(3)

    # after battle, the page may be in other panel, chose arena panel
    click_arena_menu()

    for i in range(10):
        if event.is_set():
            return False
        x = LAST_START_ARENA_X
        y = LAST_START_ARENA_Y - i * START_ARENA_INTERVAL_Y
        hv_bot.gui.gui_execute.move_and_click(x, y, ending_wait_duration=1)
        fullscreen_image: Image = hv_bot.gui.gui_execute.get_fullscreen_image()
        if detected_dialog(fullscreen_image):
            logging.info(f"select the {ordinal(i + 1)} arena has been selected")
            send_text(f"选择了倒数第{i + 1}个竞技场，于{style_time}")

            hover_wait_and_click_arena(fullscreen_image)
            return True

    # no suitable arena
    logging.warning(f"no suitable arena")
    send_text(f"没有合适的竞技场")
    arena_penal_image_path = save_fullscreen_image("screenshot")
    send_image(f"{arena_penal_image_path}")
    time.sleep(3)
    return False


def hover_wait_and_click_arena(fullscreen_image):
    hover_dialog(fullscreen_image)
    # the following warning logic is only suitable for start_auto_select_arena
    before_starting_arena_warning_time = 5
    logging.info(f"start arena in {before_starting_arena_warning_time} seconds, please get ready")
    send_text(f"将在{before_starting_arena_warning_time}秒内开始竞技场，请准备")
    time.sleep(before_starting_arena_warning_time)
    click_dialog(fullscreen_image, report=False)
    time.sleep(1.5)
    return


def start_auto_select_arena(event: threading.Event) -> None:
    battle_count_limit = 2
    try:
        _start_auto_select_arena(event, battle_count_limit)
    except pyautogui.FailSafeException as error:
        logging.error(error)
    return


def _start_auto_select_arena(event: threading.Event, battle_count_limit=2) -> None:
    logging.info(f"start_auto_select_arena, battle_count_limit={battle_count_limit}")
    send_text(f"开始连续选择竞技场，次数限制={battle_count_limit}")
    battle_count = 0
    while battle_count < battle_count_limit:
        # check whether encounter is stand by, if true, take encounter first
        _start_once_select_encounter(event)
        # start_once_select_arena
        if _start_once_select_arena(event):
            battle_count += 1
            time.sleep(1)
            # selected, get ready to battle
            _start_battle_arena(event)
        else:
            # no suitable arena
            break
        continue

    # start_auto_select_encounter after finishing start_auto_select_arena
    _start_auto_select_encounter(event)
    return


def start_battle_arena(event: threading.Event) -> None:
    try:
        _start_battle_arena(event)
    except pyautogui.FailSafeException as error:
        logging.error(error)
    return


def _start_battle_arena(event: threading.Event) -> None:
    """
    battle in arena, until finishing
    :param event: if set, stop this threading
    :return:
    """
    logging.info(f"start_battle_encounter")
    send_text(f"开始竞技场自动战斗")

    round_count, sum_round = 0, 0
    ocr_round_count = True
    while True:
        if event.is_set():
            # main thread is requiring to stop
            logging.warning("auto battle arena, exit by event")
            send_text("竞技场自动战斗，被主线程命令退出")
            time.sleep(2)
            return

        fullscreen_image = hv_bot.gui.gui_execute.get_fullscreen_image()
        character, monster_list = get_info_from_fullscreen_image(fullscreen_image, ocr_round_count=ocr_round_count)

        if character is None or monster_list is None:
            if detected_captcha(fullscreen_image):
                handle_captcha(fullscreen_image)
                logging.warning(f"auto battle arena, detected_captcha")
                continue
            if detected_dialog(fullscreen_image):
                click_dialog(fullscreen_image)
                logging.warning(f"auto battle arena, detected_dialog")
                continue
            if detected_finish(fullscreen_image):
                click_finish(fullscreen_image)
                exp = get_exp(fullscreen_image)
                logging.warning(f"auto battle arena, finished, exit，exp={exp:.2f}%")
                send_text(f"竞技场自动战斗，战斗已结束，退出，exp={exp:.2f}%")
                time.sleep(2)
                return

        ocr_round_count = False

        if is_new_round(character, monster_list):
            round_count += 1
            if round_count % 5 == 3 or round_count % 5 == 4:
                # each 5 round to ocr the round_count twice, correct it
                ocr_round_count = True
            send_round_info(round_count, sum_round, character.exp)

        # TODO move the following code to other place
        if monster_list.round_count > 0 and monster_list.sum_round > 0:
            round_count, sum_round = monster_list.round_count, monster_list.sum_round

        # logging.debug(character)
        # logging.debug(monster_list)

        strategy = get_strategy_arena(character, monster_list)
        execute_strategy(character, monster_list, strategy)
        continue

    return


def _should_send_round_info(round_count: int, sum_round: int) -> bool:
    if round_count == 1:
        return True
    if sum_round <= 75:  # 树场打的比较快
        if round_count % 20 == 0:
            return True
    elif sum_round <= 85:  # 单个女高中生的场，打的还算快
        if round_count % 15 == 0:
            return True
    else:
        if round_count % 10 == 0:
            return True
    return False


def send_round_info(round_count: int, sum_round: int, exp: float) -> None:
    logging.warning(f"the {ordinal(round_count)} round, exp={exp:.2f}%")
    if _should_send_round_info(round_count, sum_round):
        send_text(f"第{round_count}/{sum_round}轮，exp={exp:.2f}%")

    # if round_count % 30 == 0:
    #     screenshot_image_path = save_fullscreen_image("screenshot")
    #     send_image(screenshot_image_path)
    return


if __name__ == "__main__":
    logger.init_logger()
    # _start_auto_select_arena(threading.Event())
    _start_battle_arena(threading.Event())
