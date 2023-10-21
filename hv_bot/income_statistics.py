import json
import logging
import os

from PIL import Image

from hv_bot.gui import gui_finish
from hv_bot.util import logger
from hv_bot.util import ocr
from hv_bot.util import path


# def parse_material_prices():
#     fullscreen_image = hv_bot.gui.gui_execute.get_fullscreen_image()
#     # fullscreen_image.show()
#     # hv_bot.gui.gui_execute.save_fullscreen_image("material")
#     LEFT = 360
#     TOP = 106


def open_finish_images(style_time: str = ""):
    saves_dir_path = path.get_saves_dir_path(style_time)

    dict_drops_cache_name = ".dict_drops_cache.txt"
    dict_drops_cache_full_path = os.path.join(saves_dir_path, dict_drops_cache_name)

    create_cache_file(dict_drops_cache_full_path)

    dict_file_name_dict_drops = load_cache_file(dict_drops_cache_full_path)
    logging.debug(dict_file_name_dict_drops)

    parse_unloaded_data(saves_dir_path, dict_file_name_dict_drops)

    dump_cache_file(dict_drops_cache_full_path, dict_file_name_dict_drops)

    dict_drops_sum_up = {}
    for file_name, dict_drops in dict_file_name_dict_drops.items():
        for name, num_int in dict_drops.items():
            if name not in dict_drops_sum_up:
                dict_drops_sum_up[name] = 0
            dict_drops_sum_up[name] += num_int

    logging.info(f"style_time={style_time} dict_drops_sum_up={dict_drops_sum_up}")

    def _is_trophies(drop_item_name: str):
        return (drop_item_name in ["Lock of Blue Hair", "Bunny-Girl Costume", "Broken Glasses", "Hinamatsuri Doll",
                                   "Mithra’s Flower", "ManBearPig Tail", "Holy Hand Grenade of Antioch",
                                   "Dalek Voicebox", "Sapling"])

    def _is_consumables(drop_item_name: str):
        return (drop_item_name in ["Health Draught", "Health Potion", "Health Elixir",
                                   "Mana Draught", "Mana Potion", "Mana Elixir",
                                   "Spirit Draught", "Spirit Potion", "Spirit Elixir",
                                   "Monster Edibles", "Monster Chow", "Monster Cuisine",
                                   "Happy Pills"]
                or drop_item_name.count("Scroll")
                or drop_item_name.count("Infusion"))

    def _is_less_equipment(drop_item_name: str):
        return drop_item_name.count("Exquisite") or drop_item_name == "Lesser Equipment"

    def _is_better_equipment(drop_item_name: str):
        return (drop_item_name.count("Magnificent") or drop_item_name.count("Legendary")
                or drop_item_name.count("Peerless"))

    def _is_other_valuable_item(drop_item_name: str):
        return drop_item_name in ["Crystals", "Soul Fragments", "Token of Blood", "Credits", "Precursor Artifact",
                                  "Featherweight Shard", "Voidseeker Shard", "Amnesia Shard"]

    def _is_other_ignore_item(drop_item_name: str):
        return drop_item_name in ["EXP", "Chaos Token"]

    filtered_dict_drop_sum_up = {}
    unfiltered_dict_drop_sum_up = {}
    for name, num_int in dict_drops_sum_up.items():
        if _is_trophies(name) or _is_other_valuable_item(name):
            filtered_dict_drop_sum_up[name] = num_int
        elif _is_less_equipment(name) or _is_better_equipment(name):
            continue
        elif _is_consumables(name) or _is_other_ignore_item(name):
            unfiltered_dict_drop_sum_up[name] = num_int
            continue
        else:
            logging.warning(f"unknown item type={name}")
            unfiltered_dict_drop_sum_up[name] = num_int

    logging.debug(f"filtered_dict_drop_sum_up={filtered_dict_drop_sum_up}")
    logging.info(f"unfiltered_dict_drop_sum_up={unfiltered_dict_drop_sum_up}")

    price_dict = {
        "Crystals": 1.2,
        "Credits": 1,
        "Soul Fragments": 1000,
        "Token of Blood": 10000,

        "Mithra’s Flower": 1400,
        "ManBearPig Tail": 1400,
        "Holy Hand Grenade of Antioch": 1400,
        "Dalek Voicebox": 1400,
        "Lock of Blue Hair": 1400,
        "Bunny-Girl Costume": 1400,
        "Broken Glasses": 1400,
        "Hinamatsuri Doll": 1400,
        "Sapling": 4500,

        "Precursor Artifact": 6500,

        "Featherweight Shard": 100,
        "Voidseeker Shard": 100,
        "Amnesia Shard": 7500,
    }

    sum_price = 0
    for name, num_int in filtered_dict_drop_sum_up.items():
        if name not in price_dict:
            if name in ["Crystals", "EXP"]:
                continue
            logging.error(f"price not exist: {name}")
            continue
        sum_price += price_dict[name] * num_int

    logging.warning(f"style_time={style_time} filtered_dict_drop_sum_price={sum_price / 1000:.0f}k")


def dump_cache_file(dict_drops_cache_full_path, dict_file_name_dict_drops):
    with open(dict_drops_cache_full_path, "w") as dict_drops_cache_file:
        json.dump(dict_file_name_dict_drops, dict_drops_cache_file, indent=2)


def parse_unloaded_data(saves_dir_path, dict_file_name_dict_drops):
    listdir = os.listdir(saves_dir_path)
    logging.debug(listdir)

    for file_name in listdir:
        if not file_name.startswith("finish") or not file_name.endswith(".png"):
            continue
        if file_name in dict_file_name_dict_drops:
            # cached
            continue

        logging.error("------")
        full_path = os.path.join(saves_dir_path, file_name)
        finish_image = Image.open(full_path)
        dict_drops = parse_drops(finish_image)
        dict_file_name_dict_drops[file_name] = dict_drops


def load_cache_file(dict_drops_cache_full_path):
    dict_file_name_dict_drops = {}
    with open(dict_drops_cache_full_path, "r") as dict_drops_cache_file:
        try:
            dict_file_name_dict_drops = json.load(dict_drops_cache_file)
        except json.decoder.JSONDecodeError as error:
            logging.error(error)
    return dict_file_name_dict_drops


def create_cache_file(dict_drops_cache_full_path):
    with open(dict_drops_cache_full_path, "a+"):
        pass


def parse_drops(fullscreen_image: Image):
    # fullscreen_image: Image = hv_bot.gui.gui_execute.get_fullscreen_image()
    # fullscreen_image.show()
    # hv_bot.gui.gui_execute.save_fullscreen_image("material")
    finish_button_location = gui_finish.locate_finish_button(fullscreen_image)
    LEFT = 740
    TOP = 39 + finish_button_location.top
    WIDTH = 280
    HEIGHT = 12
    drop_dict = {}
    for i in range(30):
        BOX = [
            LEFT,
            TOP + i * HEIGHT,
            LEFT + WIDTH,
            TOP + (i + 1) * HEIGHT
        ]
        single_line: Image = fullscreen_image.crop(BOX)
        # single_line.show()
        text = ocr.ocr_single_line_text(single_line)

        while not text[:1].isalnum():
            text = text[1:]
        while not text[-1:].isalnum():
            text = text[:-1]

        if text.startswith("Ix"):
            text = text.replace("Ix", "1x", 1)
        if text.startswith("ix"):
            text = text.replace("ix", "1x", 1)
        if text.startswith("Tx"):
            text = text.replace("Tx", "1x", 1)
        if text.startswith("S"):
            text = text.replace("S", "5", 1)

        text = text.replace("§", "5", 1)
        text = text.replace("$", "5")

        text = text.replace("Spint", "Spirit")
        text = text.replace("Elbar", "Elixir")
        text = text.replace("Eldar", "Elixir")
        text = text.replace("Elicr", "Elixir")
        text = text.replace("Elibdr", "Elixir")
        text = text.replace("Eltdr", "Elixir")
        text = text.replace("Tokens of Blood", "Token of Blood")
        text = text.replace("Hinamatsun", "Hinamatsuri")

        if text.endswith("EXP"):
            text = text.removesuffix("EXP").replace(" ", "") + " EXP"

        if text.endswith("Credits"):
            text = text.removesuffix("Credits").replace(" ", "") + " Credits"

        logging.info(text)

        try:
            num_text, name = text.split(" ", maxsplit=1)
            num_text: str = num_text.removesuffix("x")
            num_text = num_text.replace(",", "")
            num_text = num_text.replace(".", "")
            num_int = int(num_text)
            drop_dict[name] = num_int
        except ValueError as error:
            logging.error(error)

        if text.endswith("EXP"):
            break

    logging.warning(drop_dict)
    return drop_dict


if __name__ == "__main__":
    logger.init_logger()
    for style_time in ["1018", "1019", "1020", "1021", "1022"]:
        open_finish_images(style_time)
