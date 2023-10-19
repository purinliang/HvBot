import logging
import random

from PIL import Image

import hv_bot.gui.gui_execute
from hv_bot.gui.gui_captcha import detected_captcha
from hv_bot.gui.gui_dialog import detected_dialog
from hv_bot.gui.gui_execute import move_and_click
from hv_bot.gui.gui_finish import detected_finish
from hv_bot.identify.character import Character, get_character
from hv_bot.identify.monster_list import MonsterList, get_monster_list
from hv_bot.util import logger


def execute_strategy(character: Character, monster_list: MonsterList, strategy: dict) -> None:
    action = strategy.get("action")
    match action:
        case "close_spirit_stance":
            close_spirit_stance(character)
            return
        case "use_spirit_stance":
            use_spirit_stance(character)
            return
        case "use_spell":
            spell_name = strategy.get("spell_name")
            index = strategy.get("index")
            use_spell(character, monster_list, spell_name=spell_name, index=index)
            return
        case "use_gem":
            use_gem(character)
            return
        case "use_consumable":
            consumable_name = strategy.get("consumable_name")
            use_consumable(character, consumable_name)
            return
        case "attack":
            index = strategy.get("index")
            attack(monster_list, index)
            return
        case "skip":
            pass
            return
        case _:
            logging.error(f"unknown strategy={strategy}")
            return


def close_spirit_stance(character: Character) -> None:
    if not character.spirit_stance:
        logging.warning(f"close_spirit_stance failed, current is closed")
        return

    x, y = character.get_spirit_stance_location()
    if x < 0 or y < 0:
        logging.warning(f"close_spirit_stance failed, not find")
        return
    logging.info(f"close_spirit_stance, cp={character.cp:.0f}")
    move_and_click(x, y, ending_wait_duration=0.75)  # spirit stance requires a longer delay
    return


def use_spirit_stance(character: Character) -> None:
    if character.spirit_stance:
        logging.warning(f"use_spirit_stance failed, current is using")
        return
    x, y = character.get_spirit_stance_location()
    if x < 0 or y < 0:
        logging.warning(f"use_spirit_stance failed, not find")
        return
    logging.info(f"use_spirit_stance, cp={character.cp:.0f}")
    move_and_click(x, y, ending_wait_duration=1.0)  # spirit stance requires a longer delay
    return


def use_spell(character: Character, monster_list: MonsterList, spell_name: str, index: int) -> None:
    logging.info(f"use_spell: spell_name={spell_name}")
    x1, y1 = character.get_spell_location(spell_name)
    if x1 < 0 or y1 < 0:
        logging.warning("use_spell, location1 not find")
        return
    if spell_name in ["silence", "imperil", "weaken", "orbital_friendship_cannon", "shield_bash", "vital_strike"]:
        # these spells have a target
        x2, y2 = monster_list.calc_location_by_index(index)
        if x2 < 0 or y2 < 0:
            logging.warning("use_spell, location2 not find")
            return
        move_and_click(x1, y1)
        ending_wait_duration = 0.7
        if spell_name in ["imperil", "weaken"]:
            # these two spells have no inner cooldown, so they require a longer delay
            ending_wait_duration = 0.8
        move_and_click(x2, y2, ending_wait_duration=ending_wait_duration)
        return
    else:
        # these spells have no target
        # these spells have no inner cooldown, so they require a longer delay
        move_and_click(x1, y1, ending_wait_duration=0.7)
        return


def use_gem(character: Character) -> None:
    x, y = character.get_gem_location()
    if x < 0 or y < 0:
        logging.error(f"use_gem, gem={character.gem} not find")
        return
    logging.warning(f"use_gem, gem={character.gem}")
    move_and_click(x, y, ending_wait_duration=0.25)
    return


def use_consumable(character: Character, consumable_name: str) -> None:
    x, y = character.get_consumable_location(consumable_name)  # 这是相对于fullScreen的位移
    if x < 0 or y < 0:
        logging.error(f"use_consumable, consumable={consumable_name} not find")
        return
    logging.warning(f"use_consumable, consumable={consumable_name}")
    move_and_click(x, y, ending_wait_duration=0.25)
    return


def attack(monster_list: MonsterList, index: int) -> None:
    x, y = monster_list.calc_location_by_index(index)
    x += random.randint(0, 30)  # 打普通的怪物可以稍微往右偏一点点
    if x < 0 or y < 0:
        logging.error("attack, index not find")
        return
    move_and_click(x, y)
    return


def get_info_from_fullscreen_image(fullscreen_image: Image, *, ocr_round_count=False, round_count: int, sum_round: int) \
        -> [Character | None, MonsterList | None]:
    if detected_captcha(fullscreen_image) or detected_finish(fullscreen_image) or detected_dialog(fullscreen_image):
        logging.warning(f"have_captcha_or_finish_or_dialog")
        return None, None

    character: Character = get_character(fullscreen_image)
    # logging.debug(character)
    monster_list: MonsterList = get_monster_list(fullscreen_image, ocr_round_count=ocr_round_count,
                                                 round_count=round_count, sum_round=sum_round)
    # logging.debug(monster_list)

    return character, monster_list


if __name__ == '__main__':
    logger.init_logger()
    _fullscreen_image = hv_bot.gui.gui_execute.get_fullscreen_image()
    get_info_from_fullscreen_image(_fullscreen_image)
