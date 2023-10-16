from multiprocessing import Queue

_SUB_FROM_QUEUE: Queue = Queue()
_TO_QUEUE: Queue = Queue()


def set_sub_from_queue(from_queue: Queue) -> None:
    global _SUB_FROM_QUEUE
    _SUB_FROM_QUEUE = from_queue
    return


def set_to_queue(to_queue: Queue) -> None:
    global _TO_QUEUE
    _TO_QUEUE = to_queue
    return


def get_sub_from_queue() -> Queue:
    return _SUB_FROM_QUEUE


def get_to_queue() -> Queue:
    return _TO_QUEUE


def send_text(text: str) -> None:
    """
    send a text
    :return: None
    """
    _TO_QUEUE.put(dict(op="send_text", text=text))
    return


def send_image(image_path: str) -> None:
    """
    send an image, which is indicated by image_path
    :param image_path: the image's path
    :return: None
    """
    _TO_QUEUE.put(dict(op="send_image", image_path=f"{image_path}"))
    return


def send_command_menu() -> None:
    """
    send a command_menu
    :return: None
    """
    send_text(get_command_menu())
    return


def send_captcha_poll() -> None:
    """
    send a text captcha_poll
    :return: None
    """
    _TO_QUEUE.put(dict(op="send_poll", poll_params=get_captcha_poll_params()))
    return


def get_command_menu() -> str:
    # in telegram chat, characters are not the same width
    return (
        "hv_bot_v3 命令列表如下\n"
        "\n"
        "/hv auto arena --- 连续选择竞技场\n"
        "/hv auto encounter --- 连续选择遭遇战\n"
        "\n"
        "/hv once encounter --- 选择单次遭遇战\n"
        "\n"
        "/hv arena --- 竞技场自动战斗\n"
        "/hv encounter --- 遭遇战自动战斗\n"
        "\n"
        "/hv help --- 显示命令列表\n"
        "/hv screenshot --- 远程截图\n"
        "\n"
        "/hv close --- 关闭此进程/线程\n"
    )


def get_captcha_poll_params() -> dict:
    CAPTCHA_POLL_QUESTION = "验证码：勾选验证码并点击提交"
    CAPTCHA_POLL_OPTIONS = ["Twilight Sparkle", "Rarity", "Fluttershy", "Rainbow Dash", "Pinkie Pie", "Applejack"]
    CAPTCHA_POLL_ALLOWS_MULTIPLE_ANSWERS = True
    return dict(question=CAPTCHA_POLL_QUESTION,
                options=CAPTCHA_POLL_OPTIONS,
                allows_multiple_answers=CAPTCHA_POLL_ALLOWS_MULTIPLE_ANSWERS)

# TODO get command_poll_params
