import logging

import hv_bot.gui.gui_execute
from hv_bot.external_communication_controller import send_text, send_image
from hv_bot.identify.character import Character
from hv_bot.identify.monster_list import MonsterList
from hv_bot.strategy import lowest_level_strategy_common, mid_level_strategy_common, low_level_strategy_boss
from hv_bot.strategy.format_strategy import strategy_use_spell, strategy_use_spirit_stance, \
    strategy_close_spirit_stance, \
    strategy_attack


def _maintain_boss_debuff(character: Character, monster_list: MonsterList) -> dict:
    DEBUFF_SPELL_LIST = [["weaken", 0.5], ["imperil", 0.525], ["silence", 0.675]]
    for debuff, mp_limit in DEBUFF_SPELL_LIST:
        if (character.have_spell(debuff) and low_level_strategy_boss.should_use_spell_to_boss(monster_list, debuff)
                and character.mp >= mp_limit):
            # use debuff to boss
            index = low_level_strategy_boss.get_boss_spell_target_index(monster_list, debuff)
            return strategy_use_spell(debuff, index)
        if (character.have_spell(debuff) and mid_level_strategy_common.should_use_spell(monster_list, debuff)
                and character.mp >= mp_limit):
            # use debuff to normal monsters
            index = mid_level_strategy_common.get_spell_target_index(monster_list, debuff)
            return strategy_use_spell(debuff, index)
    return {}


def _maintain_boss_spirit_stance(character: Character) -> dict:
    # close spirit stance to save cp for using "vital_strike"
    if character.have_spell("cooldown_vital_strike") and character.spirit_stance and character.cp <= 61:
        return strategy_close_spirit_stance()

    # cp too many, use some
    if not character.spirit_stance and character.cp >= 230:
        return strategy_use_spirit_stance()
    return {}


def _battle_with_few_dangerous_bosses(character: Character, monster_list: MonsterList, attack_strategy: str) -> dict:
    # the following logic is using "vital_strike" in spirit stance to boss
    if (character.have_spell("vital_strike") and low_level_strategy_boss.should_use_spell_to_boss(monster_list,
                                                                                                  "vital_strike")
            and character.spirit_stance and character.cp >= 63):
        index = low_level_strategy_boss.get_boss_spell_target_index(monster_list, "vital_strike")
        return strategy_use_spell("vital_strike", index)

    # the following logic is using "vital_strike" in spirit stance to boss
    if (character.have_spell("vital_strike") and low_level_strategy_boss.should_use_spell_to_boss(monster_list,
                                                                                                  "vital_strike")
            and not character.spirit_stance and character.cp >= 85 and character.sp >= 0.5):
        return strategy_use_spirit_stance()

    _strategy = _maintain_boss_debuff(character, monster_list)
    if _strategy != {}:
        return _strategy

    _strategy = _maintain_boss_spirit_stance(character)
    if _strategy != {}:
        return _strategy

    # cp too many and "vital_strike" is ready, use "shield_bash" to give "stunned" buff to boss
    if character.have_spell("shield_bash") and character.have_spell("vital_strike") and character.cp >= 150:
        index = low_level_strategy_boss.get_boss_spell_target_index(monster_list, "shield_bash")
        return strategy_use_spell("shield_bash", index)
    return lowest_level_strategy_common.maintain_attack(monster_list, attack_strategy)


def _battle_with_yggdrasil(character, monster_list) -> dict:
    # the following logic is using "vital_strike" in spirit stance to boss
    if (character.have_spell("vital_strike") and low_level_strategy_boss.should_use_spell_to_yggdrasil(monster_list,
                                                                                                       "vital_strike")
            and character.spirit_stance and character.cp >= 63):
        index = low_level_strategy_boss.get_boss_spell_target_index_for_yggdrasil(monster_list, "vital_strike")
        return strategy_use_spell("vital_strike", index)

    # the following logic is using "vital_strike" in spirit stance to boss
    if (character.have_spell("vital_strike") and low_level_strategy_boss.should_use_spell_to_yggdrasil(monster_list,
                                                                                                       "vital_strike")
            and not character.spirit_stance and character.cp >= 85 and character.sp >= 0.5):
        return strategy_use_spirit_stance()

    _strategy = _maintain_boss_debuff(character, monster_list)
    if _strategy != {}:
        return _strategy

    _strategy = _maintain_boss_spirit_stance(character)
    if _strategy != {}:
        return _strategy

    # cp too many and "vital_strike" is ready, use "shield_bash" to give "stunned" buff to boss
    if character.have_spell("shield_bash") and character.have_spell("shield_bash") and character.cp >= 150:
        index = low_level_strategy_boss.get_boss_spell_target_index_for_yggdrasil(monster_list, "shield_bash")
        return strategy_use_spell("shield_bash", index)

    attack_index = low_level_strategy_boss.get_boss_spell_target_index_for_yggdrasil(monster_list, "attack")
    return strategy_attack(attack_index)


def battle_with_school_girls(character: Character, monster_list: MonsterList) -> dict:
    if not monster_list.have_school_girl():
        return {}
    # even there are some school girls, but monsters are too many, using common strategy
    if monster_list.get_alive_monster_count() >= 6:
        return {}

    if character.have_spell("orbital_friendship_cannon"):
        if not character.spirit_stance and character.cp >= 213 and character.sp >= 0.5:
            # use spirit stance first, the next loop will use "orbital_friendship_cannon" automatically
            # do only one action per turn!
            return strategy_use_spirit_stance()
        elif character.spirit_stance and character.cp >= 213:
            index = mid_level_strategy_common.get_spell_target_index(monster_list, "orbital_friendship_cannon")
            return strategy_use_spell("orbital_friendship_cannon", index)

    return _battle_with_few_dangerous_bosses(character, monster_list, "min_hp")


def battle_with_ultimates(character: Character, monster_list: MonsterList) -> dict:
    if not monster_list.have_ultimate():
        return {}
    yyg_index = monster_list.get_ygg_index()
    if yyg_index >= 0 and not monster_list.monsters[yyg_index].dead:
        return _battle_with_yggdrasil(character, monster_list)
    # logging.warning(monster_list)
    # if yggdrasil is alive, kill it first
    logging.debug(f"battle_with_ultimates yyg_index={yyg_index}")
    return _battle_with_few_dangerous_bosses(character, monster_list, "min_hp")


def battle_with_dragons(character: Character, monster_list: MonsterList) -> dict:
    if not monster_list.have_dragon():
        return {}
    return _battle_with_few_dangerous_bosses(character, monster_list, "min_hp")
