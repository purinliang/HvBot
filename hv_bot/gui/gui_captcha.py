import logging
import os
import random
import time
from typing import List

import winsound
from PIL import Image

import hv_bot.util.path
from hv_bot import external_communication_controller
from hv_bot.external_communication_controller import send_text, send_image, send_captcha_poll
from hv_bot.gui import gui_execute
from hv_bot.gui.gui_execute import have_image, move_and_click


def detected_captcha(fullscreen_image: Image) -> bool:
    os.chdir(hv_bot.util.path.ROOT_PATH)
    needle_image = Image.open(f"res\\captcha_twilight_sparkle.png")
    if have_image(needle_image, fullscreen_image, confidence=0.99):
        return True
    needle_image = Image.open(f"res\\captcha_confirm_button.png")
    if have_image(needle_image, fullscreen_image, confidence=0.99):
        return True
    needle_image = Image.open(f"res\\captcha_confirm_button_disabled.png")
    if have_image(needle_image, fullscreen_image, confidence=0.99):
        return True
    return False


def _answer_list_from_str_to_index(answer_str_list: List[str]) -> List[int]:
    captcha_list_str_to_index = {"Twilight Sparkle": 0, "Rarity": 1, "Fluttershy": 2,
                                 "Rainbow Dash": 3, "Pinkie Pie": 4, "Applejack": 5}
    return [captcha_list_str_to_index.get(answer_str) for answer_str in answer_str_list]


def _submit_captcha(answer_index_list: List[int]) -> None:
    ANSWER_LOCATION = [
        [270, 584],  # Twilight Sparkle
        [430, 584],  # Rarity
        [520, 584],  # Fluttershy
        [640, 584],  # Rainbow Dash
        [784, 584],  # Pinkie Pie
        [902, 584],  # Applejack
    ]
    for answer_index in answer_index_list:
        move_and_click(ANSWER_LOCATION[answer_index][0], ANSWER_LOCATION[answer_index][1],
                       move_duration=0.05, ending_wait_duration=0.1)

    captcha_submitted_image_path = gui_execute.save_fullscreen_image("captcha_submitted")

    SUBMIT_BUTTON_LOCATION = [648, 630]
    move_and_click(SUBMIT_BUTTON_LOCATION[0], SUBMIT_BUTTON_LOCATION[1],
                   move_duration=0.05, ending_wait_duration=0.75)

    send_image(captcha_submitted_image_path)
    return


# the following two variable is global, because they should be mocked by test
CAPTCHA_TIME_LIMITATION = 30 + 1
CAPTCHA_TIME_SUBMIT_LIMITATION = -60  # negative number means that captcha timeout for 60 seconds


def handle_captcha(fullscreen_image: Image):
    if not detected_captcha(fullscreen_image):
        return

    _clear_sub_from_queue()

    detected_time_stamp = time.time()
    # sample time format: "%Y-%m-%d %H:%M:%S"
    style_time = time.strftime("%H:%M:%S", time.localtime(int(detected_time_stamp)))

    # send text that captcha detected
    logging.info("captcha detected")
    send_text(f"检测到验证码，于{style_time}")
    send_captcha_poll()

    _captcha_beep()

    # wait for loading the captcha image
    time.sleep(3)
    captcha_image_path = gui_execute.save_fullscreen_image("captcha")

    # send captcha image and poll
    send_image(captcha_image_path)

    rest_time_alert = 20 + 0.2
    while True:
        current_time_stamp = time.time()
        rest_time = detected_time_stamp + CAPTCHA_TIME_LIMITATION - current_time_stamp
        if 0 <= rest_time <= rest_time_alert:
            logging.warning(f"rest_time={rest_time:.0f}")
            send_text(f"剩余时间：{rest_time:.0f}")

            _captcha_beep()

            if rest_time_alert >= 15:
                rest_time_alert -= 5
            else:
                rest_time_alert -= 2
        if not detected_captcha(fullscreen_image):
            # captcha has been submitted
            _report_captcha_submitted(rest_time)
            break
        if rest_time <= CAPTCHA_TIME_SUBMIT_LIMITATION:
            # captcha is going to timeout, random choice and submit
            # TODO: do not random choice so quick, get very-low riddle_master accuracy
            _random_choice_captcha_to_submit()
            _report_captcha_timeout(rest_time)
            break

        fullscreen_image = gui_execute.get_fullscreen_image()
        _handle_answer_from_sub_from_queue(rest_time)

        time.sleep(0.125)
    # sleep for about 1 second, waiting for submitting
    time.sleep(0.8)
    return


def _random_choice_captcha_to_submit() -> None:
    captcha_list = ["Twilight Sparkle", "Rarity", "Fluttershy", "Rainbow Dash", "Pinkie Pie", "Applejack"]
    answer_param_str = [random.choice(captcha_list)]
    answer_param_int = _answer_list_from_str_to_index(answer_param_str)

    _submit_captcha(answer_param_int)

    logging.warning(f"random_chosen_captcha={answer_param_str}")
    send_text(f"随机选择的验证码：{answer_param_str}")
    return


def _report_captcha_timeout(rest_time: float) -> None:
    logging.warning(f"captcha timeout, rest_time={rest_time:.0f}")
    text = f"验证码已超时，剩余时间={rest_time:.0f}"
    if rest_time < 0:
        text = f"验证码已超时，超时时间={abs(rest_time):.0f}"
    send_text(text)
    # winsound.Beep(1200, 600)
    time.sleep(0.8)
    return


def _report_captcha_submitted(rest_time: float) -> None:
    logging.info(f"captcha not find, has it been submitted? rest_time={rest_time:.1f}")
    send_text(f"验证码已消失，是否已被提交？剩余时间={rest_time:.1f}")
    # winsound.Beep(600, 600)
    time.sleep(0.8)
    return


def _captcha_beep():
    # winsound.Beep(1000, 350)
    time.sleep(0.075)
    # winsound.Beep(1000, 200)
    time.sleep(0.075)
    # winsound.Beep(1000, 200)
    time.sleep(0.075)


def _handle_answer_from_sub_from_queue(rest_time: float) -> None:
    sub_from_queue = external_communication_controller.get_sub_from_queue()
    while not sub_from_queue.empty():
        data: dict = sub_from_queue.get()
        # sample_data = {
        #     "op": "receive_poll_result",
        #     "poll_question": "question_text",
        #     "poll_result": ["option_1", "option_2"]
        # }
        if data.get("op") == "receive_poll_result":
            answer_str_list = data.get("poll_result")
            answer_index_list = _answer_list_from_str_to_index(answer_str_list)

            _submit_captcha(answer_index_list)

            logging.warning(
                f"remote submit captcha successfully answer={answer_str_list}, rest_time={rest_time:.1f}")
            send_text(
                f"远程提交验证码成功，选项={answer_str_list}，剩余时间={rest_time:.1f}")
            break
        else:
            logging.error(f"not supportive operation")
            send_text("不支持这个操作")
    return


def _clear_sub_from_queue() -> None:
    # clear sub_from_queue before using, to avoid previous unused data
    sub_from_queue = external_communication_controller.get_sub_from_queue()
    while not sub_from_queue.empty():
        try:
            data = sub_from_queue.get_nowait()
            logging.debug(f"ignore sub_from_queue data={data}")
        except ValueError as error:
            logging.error(error)
    return
