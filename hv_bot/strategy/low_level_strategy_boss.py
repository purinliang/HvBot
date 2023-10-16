import functools
import logging
from typing import List

from hv_bot.identify.monster import Monster
from hv_bot.identify.monster_list import MonsterList
from hv_bot.strategy import lowest_level_strategy_common


def should_use_spell_to_boss(monster_list: MonsterList, spell_name: str) -> bool:
    boss_target_index = get_boss_spell_target_index(monster_list, spell_name)
    if boss_target_index == -1:
        return False
    monster: Monster = monster_list.monsters[boss_target_index]
    if monster.dead:
        # debuff spell will choose boss's neighbour instead!
        logging.error("find monster is dead, please debug")
        return False
    return True


def should_use_spell_to_yggdrasil(monster_list: MonsterList, spell_name: str) -> bool:
    yggdrasil_target_index = get_boss_spell_target_index_for_yggdrasil(monster_list, spell_name)
    if yggdrasil_target_index == -1:
        return False
    monster: Monster = monster_list.monsters[yggdrasil_target_index]
    if monster.dead:
        # debuff spell will choose boss's neighbour instead!
        logging.error("find monster is dead, please debug")
        return False
    return True


def get_boss_spell_target_index_for_normal_boss(monster_list: MonsterList, spell_name) -> int:
    """
    get_boss_spell_target_index_for_normal_boss
    :param monster_list:
    :param spell_name:
    :return:
    """
    # attention: schoolgirls has been processed before, there is no school girls
    # boss list, who is boss and still alive
    boss_list: List[Monster] = [monster for monster in monster_list.monsters
                                if not monster.dead and monster.is_boss()]
    if len(boss_list) == 0:
        return -1

    if spell_name in ["silence", "imperil"]:
        # for a normal boss, it is not necessary to use spell "imperil" or "silence"
        return -1
    if spell_name in ["weaken"]:
        return get_boss_spell_target_index_for_debuff_spell(monster_list, boss_list, spell_name)
    if spell_name in ["vital_strike", "attack", "orbital_friendship_cannon", "shield_bash"]:
        return get_boss_spell_target_index_for_damage_spell(monster_list, boss_list, spell_name)

    logging.warning(f"not supportive spell_name={spell_name}")
    return -1


def get_boss_spell_target_index_for_school_girl(monster_list: MonsterList, spell_name) -> int:
    """
    get_boss_spell_target_index_for_school_girl
    :param monster_list:
    :param spell_name:
    :return:
    """
    school_girl_list: List[Monster] = [monster for monster in monster_list.monsters
                                       if not monster.dead and monster.is_school_girl()]
    if len(school_girl_list) == 0:
        return -1

    if spell_name in ["weaken", "silence", "imperil"]:
        return get_boss_spell_target_index_for_debuff_spell(monster_list, school_girl_list, spell_name)
    if spell_name in ["vital_strike", "attack", "orbital_friendship_cannon", "shield_bash"]:
        return get_boss_spell_target_index_for_damage_spell(monster_list, school_girl_list, spell_name)

    logging.warning(f"not supportive spell_name={spell_name}")
    return -1


def get_boss_spell_target_index_for_yggdrasil(monster_list: MonsterList, spell_name) -> int:
    """
    get_boss_spell_target_index_for_yggdrasil
    :param monster_list:
    :param spell_name:
    :return:
    """
    yggdrasil_list: List[Monster] = [monster for monster in monster_list.monsters
                                     if not monster.dead and monster.is_yggdrasil()]
    if len(yggdrasil_list) == 0:
        return -1
    if len(yggdrasil_list) != 1:
        logging.error("multiple yggdrasil")
        return -1

    if spell_name in ["weaken", "silence", "imperil"]:
        return get_boss_spell_target_index_for_debuff_spell(monster_list, yggdrasil_list, spell_name)
    if spell_name in ["vital_strike", "attack", "shield_bash"]:
        return get_boss_spell_target_index_for_damage_spell(monster_list, yggdrasil_list, spell_name)

    logging.warning(f"not supportive spell_name={spell_name}")
    return -1


def get_boss_spell_target_index_for_debuff_spell(monster_list: MonsterList, boss_list: List[Monster],
                                                 spell_name: str) -> int:
    """
    Damage spell (including "weaken", "silence", "imperil", "shield_bash") share the same logic
    But for processing school girls first, convey suitable parameter to this function

    :param monster_list:
    :param boss_list:
    :param spell_name:
    :return:
    """
    boss_no_spell_status_list = [boss for boss in boss_list
                                 if not boss.have_status(spell_name) and not boss.have_status("too_many")]
    # every boss is "weaken" or has too many status
    if len(boss_no_spell_status_list) == 0:
        return -1

    deterrent_of_position_spell_name = functools.partial(
        lowest_level_strategy_common.deterrent_of_position, monster_list=monster_list, spell_name=spell_name)

    # choose the one has most deterrent
    max_deterrent_boss = max(boss_no_spell_status_list, key=deterrent_of_position_spell_name)

    # try to choose a position that can affect multiple boss at the same time
    alive_monster_list: List[Monster] = [monster for monster in monster_list.monsters if not monster.dead]
    max_deterrent_position_monster = max(alive_monster_list, key=deterrent_of_position_spell_name)
    if abs(max_deterrent_boss.index - max_deterrent_position_monster.index) <= 1:
        # this position's monster is neighbor of max_deterrent_boss
        return max_deterrent_position_monster.index

    # no such position that can affect max_deterrent_boss, insist previous choice
    return max_deterrent_boss.index


def get_boss_spell_target_index_for_damage_spell(monster_list: MonsterList, boss_list: List[Monster],
                                                 spell_name: str) -> int:
    """
    Damage spell (including "vital_strike", "attack", "orbital_friendship_cannon", "shield_bash") share the same logic
    But for processing school girls first, convey suitable parameter to this function

    :param monster_list:
    :param boss_list:
    :param spell_name:
    :return:
    """

    deterrent_of_position_spell_name = functools.partial(
        lowest_level_strategy_common.deterrent_of_position, monster_list=monster_list, spell_name=spell_name)

    if spell_name in ["vital_strike"]:
        boss_shocked_list = [boss for boss in boss_list
                             if boss.have_status("shocked")]
        # no such "shocked" boss
        if len(boss_shocked_list) == 0:
            return -1

        # choose the one has the least hp
        min_hp_boss = min(boss_shocked_list, key=lambda boss: boss.hp)
        return min_hp_boss.index
    if spell_name in ["attack", "orbital_friendship_cannon"]:
        # normal attack or "orbital_friendship_cannon" should choose the one has the least hp
        min_hp_boss = min(boss_list, key=lambda boss: boss.hp)
        return min_hp_boss.index
    if spell_name in ["shield_bash"]:
        # "shield_bash" should choose the one is not "shocked"
        # if there are multiple choices, choose the most deterrent one
        boss_not_shocked_list = [boss for boss in boss_list
                                 if not boss.have_status("shocked")]
        # no such "shocked" boss
        if len(boss_not_shocked_list) == 0:
            return -1

        # choose the one has most deterrent
        max_deterrent_boss = max(boss_not_shocked_list, key=deterrent_of_position_spell_name)
        return max_deterrent_boss.index

    logging.warning(f"not supportive spell_name={spell_name}")
    return -1


def get_boss_spell_target_index(monster_list: MonsterList, spell_name) -> int:
    """
    Find a suitable target who is boss for spell
    :param monster_list:
    :param spell_name:
    :return: the target's index
    """
    index = get_boss_spell_target_index_for_yggdrasil(monster_list, spell_name)
    if index != -1:
        return index
    index = get_boss_spell_target_index_for_school_girl(monster_list, spell_name)
    if index != -1:
        return index
    index = get_boss_spell_target_index_for_normal_boss(monster_list, spell_name)
    if index != -1:
        return index

    # logging.debug(f"no target for spell_name={spell_name}")
    return -1
