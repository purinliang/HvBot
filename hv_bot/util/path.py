import logging
import os
import time
from pathlib import Path

import hv_bot.util.logger

ROOT_PATH = Path(__file__).parent.parent


def chdir_saves_today():
    os.chdir(ROOT_PATH.parent)

    user_data_path = "user_data"
    if not os.path.exists(user_data_path):
        os.makedirs(user_data_path)
    os.chdir(user_data_path)

    current_time = int(time.time())
    # sample time format: "%Y-%m-%d %H:%M:%S"
    style_time = time.strftime("%m%d", time.localtime(current_time))

    saves_path = f"saves_{style_time}"
    if not os.path.exists(saves_path):
        os.makedirs(saves_path)
    os.chdir(saves_path)

    cwd = os.getcwd()
    logging.warning(f"cwd={cwd}")


if __name__ == "__main__":
    hv_bot.util.logger.init_logger()
    chdir_saves_today()
