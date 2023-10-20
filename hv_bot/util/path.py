import logging
import os
import time
from pathlib import Path

import hv_bot.util.logger

ROOT_PATH = Path(__file__).parent.parent


def get_saves_dir_path(style_time: str = "") -> str:
    # TODO remove all os.chdir, this action should not be execute in multithreading
    os.chdir(ROOT_PATH)

    user_data_path = r"..\user_data"
    if not os.path.exists(user_data_path):
        os.makedirs(user_data_path)
    # os.chdir(user_data_path)

    if not style_time:
        current_time = int(time.time())
        # sample time format: "%Y-%m-%d %H:%M:%S"
        style_time = time.strftime("%m%d", time.localtime(current_time))

    saves_path = os.path.join(user_data_path, f"saves_{style_time}")
    if not os.path.exists(saves_path):
        os.makedirs(saves_path)
    # os.chdir(saves_path)

    # cwd = os.getcwd()
    # logging.info(f"cwd={cwd}")
    return saves_path


if __name__ == "__main__":
    hv_bot.util.logger.init_logger()
    logging.info(get_saves_dir_path())
