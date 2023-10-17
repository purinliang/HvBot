import functools
import logging

from hv_bot.identify.monster import Monster
from hv_bot.identify.monster_list import MonsterList
from hv_bot.strategy import lowest_level_strategy_common


def find_debuff_targe_index(monster_list: MonsterList, *, spell_name: str,
                            alive_count_limit: int, sum_deterrent_limit: float, max_deterrent_of_position_limit: float,
                            force_use=False) -> int:
    """
    Find a suitable target for the spell "spell_name".

    Notice that this function will not distinct boss monster.

    :param monster_list:
    :param spell_name:
    :param alive_count_limit:
    :param sum_deterrent_limit:
    :param max_deterrent_of_position_limit:
    :param force_use: force to use, regardless most limitations
    :return: target monster index, or -1 represent not find
    """
    # if the amount of alive monsters is little, ignore it
    if not force_use and monster_list.get_alive_monster_count() <= alive_count_limit:  # 20难的时候5个怪也要小心
        # logging.debug(f"{spell_name}: too less alive monsters")
        return -1
    # sum of monsters' deterrent factor
    sum_deterrent = sum([monster.calc_deterrent(spell_name) for monster in monster_list.monsters])

    if (sum_deterrent <= 4.0
            or (not force_use and sum_deterrent <= sum_deterrent_limit)):
        # logging.debug(f"{spell_name}: sum_deterrent={sum_deterrent:.2f} too low")
        return -1

    deterrent_of_position_spell_name = functools.partial(
        lowest_level_strategy_common.deterrent_of_position, monster_list=monster_list, spell_name=spell_name)

    # max deterrent of a position: the sum of the nearby 3 monsters' deterrent
    max_deterrent_monster: Monster = max(monster_list.monsters, key=deterrent_of_position_spell_name)
    max_deterrent_of_position = deterrent_of_position_spell_name(max_deterrent_monster)
    if max_deterrent_monster.dead:
        logging.error(f"{spell_name}: max_deterrent_monster dead, something get wrong?")
        return -1
    if (max_deterrent_monster.dead or max_deterrent_of_position <= 1.75
            or (not force_use and max_deterrent_of_position <= max_deterrent_of_position_limit)):
        # logging.debug(f"{spell_name}: max_deterrent_of_position={max_deterrent_of_position:.2f} too low")
        return -1
    # logging.debug(f"{spell_name}: target={monster_list.number_index_to_letter_index(max_deterrent_monster.index)}")
    return max_deterrent_monster.index


def find_weaken_target_index(monster_list: MonsterList, *, force_use=False) -> int:
    """
    Find a suitable target for the spell "weaken".

    Notice that this function will not distinct boss monster.
    :param monster_list:
    :param force_use: force to use, regardless most limitations
    :return: target monster index, or -1 represent not find
    """
    return find_debuff_targe_index(monster_list, spell_name="weaken", alive_count_limit=3,
                                   sum_deterrent_limit=7.25, max_deterrent_of_position_limit=3.0, force_use=force_use)


def find_silence_target_index(monster_list, *, force_use=False) -> int:
    """
    Find a suitable target for the spell "silence".

    Notice that this function will not distinct boss monster.
    :param monster_list:
    :param force_use: force to use, regardless most limitations
    :return: target monster index, or -1 represent not find
    """
    return find_debuff_targe_index(monster_list, spell_name="silence", alive_count_limit=3,
                                   sum_deterrent_limit=12.25, max_deterrent_of_position_limit=4.25, force_use=force_use)


def find_vital_strike_target_index(monster_list) -> int:
    """
    Find a suitable target for the spell "vital_strike".

    Notice that this function will not distinct boss monster.
    :return: target monster index, or -1 represent not find
    """
    # filter monsters who are "shocked" and taking more damage by "vital_strike". it will be more efficient.
    shocked_monsters = [monster for monster in monster_list.monsters
                        if not monster.dead
                        and monster.have_status("shocked")]

    # find target without "silence" and "weaken" first, they are more deterrent
    # filter monsters who aren't "silence" and "weaken" and their hp >= 0.3
    filtered_shocked_monsters = [monster for monster in shocked_monsters
                                 if not monster.have_status("silence") and not monster.have_status("weaken")
                                 and monster.hp >= 0.3]

    if len(filtered_shocked_monsters) == 0:
        # no suitable target, to find target within the whole list
        # filter monsters whose hp >= 0.3
        filtered_shocked_monsters = [monster for monster in shocked_monsters
                                     if monster.hp >= 0.3]
    if len(filtered_shocked_monsters) == 0:
        # logging.debug("vital_strike: no target")
        return -1

    # find the monster who has the most hp in above lists
    max_hp_monster: Monster = max(filtered_shocked_monsters, key=lambda monster: monster.hp)
    # logging.debug(f"vital_strike: target={monster_list.number_index_to_letter_index(max_hp_monster.index)}")
    return max_hp_monster.index
