import logging
import threading
import time
from multiprocessing import Queue

from hv_bot import arena_controller
from hv_bot import encounter_controller
from hv_bot import external_communication_controller
from hv_bot.external_communication_controller import send_text, send_image, send_command_menu, send_captcha_poll
from hv_bot.gui.gui_execute import save_fullscreen_image
from hv_bot.util import logger


def exec_cmd_screenshot() -> None:
    logging.info("exec_cmd_screenshot")
    send_text("远程截图")
    screenshot_image_path = save_fullscreen_image("screenshot")
    send_image(screenshot_image_path)
    return


RUNNING_SUB_THREAD: threading.Thread = threading.Thread()
RUNNING_SUB_THREAD_EVENT: threading.Event = threading.Event()


def close_running_sub_thread() -> None:
    global RUNNING_SUB_THREAD_EVENT
    RUNNING_SUB_THREAD_EVENT.set()
    return


def exec_cmd_start_sub_thread(command: str) -> None:
    TARGET_DICT = {
        # the following is the full version of commands
        "start arena": [arena_controller.start_battle_arena, "arena_controller"],
        "start encounter": [encounter_controller.start_battle_encounter, "encounter_controller"],
        "start auto select arena": [arena_controller.start_auto_select_arena, "arena_controller"],
        "start auto select encounter": [encounter_controller.start_auto_select_encounter, "encounter_controller"],
        "start once select encounter": [encounter_controller.start_once_select_encounter, "encounter_controller"],
        # the following is the short version of commands
        "arena": [arena_controller.start_battle_arena, "arena_controller"],
        "encounter": [encounter_controller.start_battle_encounter, "encounter_controller"],
        "auto arena": [arena_controller.start_auto_select_arena, "arena_controller"],
        "auto encounter": [encounter_controller.start_auto_select_encounter, "encounter_controller"],
        "once encounter": [encounter_controller.start_once_select_encounter, "encounter_controller"]
    }
    target, name = TARGET_DICT[command]

    close_running_sub_thread()

    global RUNNING_SUB_THREAD
    global RUNNING_SUB_THREAD_EVENT
    RUNNING_SUB_THREAD_EVENT = threading.Event()
    RUNNING_SUB_THREAD = threading.Thread(target=target, name=name, args=(RUNNING_SUB_THREAD_EVENT,))
    RUNNING_SUB_THREAD.start()
    return


def main(event: threading.Event, from_queue: Queue, to_queue: Queue) -> None:
    # from_queue only should be used by main thread, main thread forwards data to sub thread
    external_communication_controller.set_to_queue(to_queue)

    logger.init_logger()
    logging.info(f"main_controller main start, v0.3.0.5")
    send_text(f"主控制器启动，v0.3.0.5")  # TODO translate to English

    while True:
        time.sleep(0.5)
        if event.is_set():
            break
        if from_queue.empty():
            continue
        data: dict = from_queue.get_nowait()
        if data == {}:
            continue
        command: str = data.get("cmd")
        if command is not None and command != "":
            # "cmd" means that the data is from user input
            logging.info(f"main_controller command={command}")
            match command:
                # the following is the short version of commands
                case "arena" | "encounter" | "auto arena" | "auto encounter" | "once encounter":
                    exec_cmd_start_sub_thread(command)
                    continue
                # the following is the full version of commands
                case "start arena" | "start encounter" | "start auto select arena" \
                     | "start auto select encounter" | "start once select encounter":
                    exec_cmd_start_sub_thread(command)
                    continue
                case "help":
                    send_command_menu()
                    continue
                case "screenshot":
                    exec_cmd_screenshot()
                    continue
                case "close":
                    event.set()
                    continue
                # the following command is to test captcha poll, so it will not be shown in command menu
                case "test captcha poll":
                    send_captcha_poll()
                    continue
                case _:
                    logging.error(f"hv:main_controller unknown data={command}")
                    send_text(f"主控制器收到了未知包：{data}")
                    continue
        op: str = data.get("op")
        if op is not None and op != "":
            # "op" means that the data is from queue, rather than user input
            # for example, {"op": "receive_poll_result", "poll_question": poll_question, "poll_result": poll_result}
            logging.info(f"main_controller op={op}")
            if op == "receive_poll_result":
                if data.get(
                        "poll_question") == external_communication_controller.get_captcha_poll_params().get("question"):
                    # is captcha poll
                    poll_result = data.get("poll_result")
                    logging.info(f"poll_result={poll_result}")
                    # forward to sub thread
                    external_communication_controller.get_sub_from_queue().put(data)
                    continue
            logging.error(f"hv:main_controller unknown data={command}")
            send_text(f"主控制器收到了未知包：{data}")
            continue
        logging.error(f"hv:main_controller unknown data={command}")
        send_text(f"主控制器收到了未知包：{data}")
        continue

    logging.info(f"main_controller main end")
    send_text(f"主控制器结束")  # TODO translate to English
    time.sleep(2)  # make some delay, ensure caller have time to handle the data in queue

    close_running_sub_thread()
    time.sleep(0.5)
    return


if __name__ == "__main__":
    main(threading.Event(), Queue(), Queue())
