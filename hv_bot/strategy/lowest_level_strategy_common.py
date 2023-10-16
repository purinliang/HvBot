import logging

from hv_bot.identify.monster import Monster
from hv_bot.identify.monster_list import MonsterList
from hv_bot.strategy.format_strategy import strategy_attack, strategy_skip


def find_attack_max_hp_target_index(monster_list: MonsterList) -> int:
    """
    Find a target with max_hp under some conditions for normal attack.

    Notice that this function will not distinct boss monster.
    :param monster_list:
    :return: target monster index, or -1 represent not find
    """
    # in this situation, maybe it is ready to cast "orbital_friendship_canon",
    # which can deal huge damage to every monster, so candidate targets should
    # be all monsters, find the one with the largest hp among them.
    filtered_monsters = [monster for monster in monster_list.monsters if not monster.dead]

    if not filtered_monsters:
        # in regular routine, the program will never enter this branch, maybe there is some bugs?
        return -1

    # find the monster who has the largest hp in above list
    max_hp_monster: Monster = max(filtered_monsters, key=lambda monster: monster.hp)
    # logging.debug(f"attack: max_hp_target={monster_list.number_index_to_letter_index(max_hp_monster.index)}")
    return max_hp_monster.index


def find_attack_min_hp_target_index(monster_list: MonsterList) -> int:
    """
    Find a target with min_hp under some conditions for normal attack.

    Notice that this function will not distinct boss monster.
    :param monster_list:
    :return: target monster index, or -1 represent not find
    """

    # in this situation, find a monster who are can deal large damage but are
    # easiest to be killed. obviously boss monsters are not easy to be killed.
    # and monster have debuff such as "silence" and "weaken" will deal less
    # damage.
    def is_normal_monster_without_silence_and_weaken(monster: Monster):
        return not (monster.dead or monster.is_boss()
                    or monster.have_status("silence") or monster.have_status("weaken"))

    # find normal monsters who aren't affected by "silence" or "weaken"
    filtered_monsters = [monster for monster in monster_list.monsters
                         if is_normal_monster_without_silence_and_weaken(monster)]

    if not filtered_monsters:
        # if no suitable candidate targets, widen the selecting conditions.
        filtered_monsters = [monster for monster in monster_list.monsters if not monster.dead]

    if not filtered_monsters:
        # in regular routine, the program will never enter this branch, maybe there is some bugs?
        return -1

    # find the monster who has the least hp in above list
    min_hp_monster: Monster = min(filtered_monsters, key=lambda monster: monster.hp)
    # logging.debug(f"attack: min_hp_monster={monster_list.number_index_to_letter_index(min_hp_monster.index)}")
    return min_hp_monster.index


def find_attack_max_deterrent_target_index(monster_list: MonsterList) -> int:
    """
    Find a target with max_deterrent under some conditions for normal attack.

    Notice that this function will not distinct boss monster.
    :param monster_list:
    :return: target monster index, or -1 represent not find
    """
    filtered_monsters = [monster for monster in monster_list.monsters if not monster.dead]

    if not filtered_monsters:
        # in regular routine, the program will never enter this branch, maybe there is some bugs?
        return -1

    # find the monster who has the most deterrent in above lists
    max_deterrent_monster: Monster = max(filtered_monsters, key=lambda monster: monster.calc_deterrent("attack"))
    # logging.debug(
    #     f"attack: max_deterrent_monster={monster_list.number_index_to_letter_index(max_deterrent_monster.index)}")
    return max_deterrent_monster.index


def maintain_attack(monster_list: MonsterList, attack_strategy: str) -> dict:
    if not (attack_strategy in ["min_hp", "max_hp", "max_deterrent"]):
        raise ValueError(f"invalid attack_strategy={attack_strategy}")
    if monster_list.get_alive_monster_count() == 0:
        return strategy_skip()

    attack_index = -1
    match attack_strategy:
        case "min_hp":
            attack_index = find_attack_min_hp_target_index(monster_list)
        case "max_hp":
            attack_index = find_attack_max_hp_target_index(monster_list)
        case "max_deterrent":
            attack_index = find_attack_max_deterrent_target_index(monster_list)

    if attack_index < 0 or attack_index >= len(monster_list.monsters) or monster_list.monsters[attack_index].dead:
        logging.error(f"maintain_attack selected invalid attack target index={attack_index}")
        return strategy_skip()
    return strategy_attack(attack_index)


def deterrent_of_position(monster: Monster, *, monster_list: MonsterList, spell_name: str) -> float:
    """
    Deterrent of a position is the sum of the monster's deterrent and its 2 adjacent monsters' deterrents
    :param monster:
    :param monster_list:
    :param spell_name: different spell correspond to different deterrent,
                       so method "calc_deterrent" require this parameter
    :return: sum of deterrents of the 3 monsters
    """
    if monster.dead:
        # a dead monster cannot be a target, regardless how large deterrent its neighbors have
        return 0.0
    adjacent_monster_list = [monster for monster in monster_list.monsters
                             if abs(monster.index - monster.index) <= 1]
    return sum([monster.calc_deterrent(spell_name) for monster in adjacent_monster_list])
