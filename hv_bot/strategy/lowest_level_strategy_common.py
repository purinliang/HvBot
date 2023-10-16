import logging

from hv_bot.identify.monster import Monster
from hv_bot.identify.monster_list import MonsterList
from hv_bot.strategy.format_strategy import strategy_attack


def find_attack_target_index(monster_list: MonsterList, attack_max_hp: bool) -> int:
    """
    Find a suitable target for normal attack.

    Notice that this function will not distinct boss monster.
    :param monster_list:
    :param attack_max_hp: whether to find monster with min or max hp first
    :return: target monster index, or -1 represent not find
    """

    # find monsters who don't affect by "silence" or "weaken" and aren't bosses
    filtered_monsters = [monster for monster in monster_list.monsters
                         if not monster.dead and not monster.have_status("silence")
                         and not monster.have_status("weaken") and not monster.is_boss()]
    if attack_max_hp:
        # in this situation, maybe it is ready to cast "orbital_friendship_canon"
        filtered_monsters = [monster for monster in monster_list.monsters
                             if not monster.dead]

    if len(filtered_monsters) == 0:
        filtered_monsters = [monster for monster in monster_list.monsters
                             if not monster.dead]
    if len(filtered_monsters) == 0:
        # in regular routine, the program will never enter this branch
        # logging.debug("attack: no target")
        return -1

    if attack_max_hp:
        # find the monster who has the most hp in above lists
        max_hp_monster: Monster = max(filtered_monsters, key=lambda monster: monster.hp)
        # logging.debug(f"attack: max_hp_target={monster_list.number_index_to_letter_index(max_hp_monster.index)}")
        return max_hp_monster.index
    else:
        # find the monster who has the least hp in above lists
        min_hp_monster: Monster = min(filtered_monsters, key=lambda monster: monster.hp)
        # logging.debug(f"attack: min_hp_monster={monster_list.number_index_to_letter_index(min_hp_monster.index)}")
        return min_hp_monster.index


def find_attack_max_deterrent_target_index(monster_list: MonsterList) -> int:
    """
    Find a suitable target for normal attack.

    Notice that this function will not distinct boss monster.
    :param monster_list:
    :return: target monster index, or -1 represent not find
    """
    filtered_monsters = [monster for monster in monster_list.monsters
                         if not monster.dead]

    if len(filtered_monsters) == 0:
        # in regular routine, the program will never enter this branch
        # logging.debug("attack: no target")
        return -1

    filtered_monsters_deterrents = [(monster, monster.calc_deterrent("attack")) for monster in filtered_monsters]

    # find the monster who has the most deterrent in above lists
    max_deterrent_monster: Monster = (max(filtered_monsters_deterrents, key=lambda tup: tup[1]))[0]
    # logging.debug(
    #     f"attack: max_deterrent_monster={monster_list.number_index_to_letter_index(max_deterrent_monster.index)}")
    return max_deterrent_monster.index


def maintain_attack(monster_list: MonsterList, attack_strategy: str) -> dict:
    if monster_list.get_alive_monster_count() == 0:
        return {}
    attack_index = find_attack_target_index(monster_list, False)
    if attack_strategy == "min_hp":
        attack_index = find_attack_target_index(monster_list, False)
    elif attack_strategy == "max_hp":
        attack_index = find_attack_target_index(monster_list, True)
    elif attack_strategy == "max_deterrent":
        attack_index = find_attack_max_deterrent_target_index(monster_list)
    if attack_index < 0 or attack_index >= len(monster_list.monsters) or monster_list.monsters[attack_index].dead:
        logging.error(f"maintain_attack try to attack invalid index={attack_index}")
        return {}
    return strategy_attack(attack_index)


def deterrent_of_position(monster: Monster, *, monster_list: MonsterList, spell_name: str) -> float:
    """
    deterrent of a position: the sum of the nearby 3 monsters' deterrent
    :param monster:
    :param monster_list:
    :param spell_name: calc_deterrent require this parameter
    :return: sum of deterrent of these 3 monsters
    """
    if monster.dead:
        # a dead monster cannot be a target, regardless how large its neighbors deterrent
        return 0.0
    neighbor_monster_list = [neighbor_monster for neighbor_monster in monster_list.monsters
                             if abs(monster.index - neighbor_monster.index) <= 1]
    return sum([neighbor.calc_deterrent(spell_name) for neighbor in neighbor_monster_list])
