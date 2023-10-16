from hv_bot.identify.monster_list import MonsterList
from hv_bot.strategy import lowest_level_strategy_common, low_level_strategy_normal_monster, low_level_strategy_boss


def should_use_spell(monster_list: MonsterList, spell_name, *, force_use=False) -> bool:
    """
    should or should not use certain spell
    :param monster_list:
    :param spell_name: the spell's name
    :param force_use: force use, break most usage limitation
    :return: True or False
    """
    if low_level_strategy_boss.should_use_spell_to_boss(monster_list, spell_name):
        return True
    index = get_spell_target_index(monster_list, spell_name, force_use=force_use)
    return index != -1


def get_spell_target_index(monster_list: MonsterList, spell_name: str, *, force_use=False) -> int:
    """
    find suitable target for spell
    :param monster_list:
    :param force_use: to avoid most limitation
    :param spell_name:
    :return: target index
    """
    if low_level_strategy_boss.should_use_spell_to_boss(monster_list, spell_name):
        return low_level_strategy_boss.get_boss_spell_target_index(monster_list, spell_name)

    match spell_name:
        case "vital_strike":
            return low_level_strategy_normal_monster.find_vital_strike_target_index(monster_list)
        case "imperil":
            return -1
        case "silence":
            return low_level_strategy_normal_monster.find_silence_target_index(monster_list, force_use=force_use)
        case "weaken":
            return low_level_strategy_normal_monster.find_weaken_target_index(monster_list, force_use=force_use)
        case "shield_bash" | "orbital_friendship_cannon":
            return lowest_level_strategy_common.find_attack_target_index(monster_list, attack_max_hp=True)
    return -1
