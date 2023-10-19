import logging

from hv_bot.external_communication_controller import send_text
from hv_bot.identify.character import Character
from hv_bot.identify.monster_list import MonsterList
from hv_bot.strategy import strategy_arena_battle_with_boss, lowest_level_strategy_common, mid_level_strategy_common, \
    low_level_strategy_boss
from hv_bot.strategy.format_strategy import strategy_use_spell, strategy_use_consumable, strategy_use_gem, \
    strategy_use_spirit_stance, strategy_close_spirit_stance, strategy_skip


def _maintain_xps(character: Character) -> dict:
    # use mana_draught
    if (character.mp <= 0.900
            and not character.have_status("mana_draught") and character.have_consumable("mana_draught")):
        return strategy_use_consumable("mana_draught")

    # use spirit_draught
    if (character.sp <= 0.675
            and not character.have_status("spirit_draught") and character.have_consumable("spirit_draught")):
        return strategy_use_consumable("spirit_draught")

    # use mana_potion
    if character.mp <= 0.425 and character.have_consumable("mana_potion"):
        logging.warning("low mp")
        return strategy_use_consumable("mana_potion")

    # need to use mana_potion but fail
    if character.mp <= 0.15:
        logging.error("low mp and have no potion")
        send_text("MP过低并且无法回复")
        return strategy_skip()

    # use spirit_potion
    if character.sp <= 0.375 and character.have_consumable("spirit_potion"):
        logging.warning("low sp")
        return strategy_use_consumable("spirit_potion")

    # use health_draught
    if (character.hp <= 0.825
            and not character.have_status("health_draught") and character.have_consumable("health_draught")):
        return strategy_use_consumable("health_draught")

    # use spell "cure"
    if character.hp <= 0.55 and character.have_spell("cure"):
        # TODO："full_cure" and "cure" now share the same logic, to distinct them
        return strategy_use_spell("cure")

    # use health_potion
    if character.hp <= 0.375 and character.have_consumable("health_potion"):
        logging.warning("low hp")
        return strategy_use_consumable("health_potion")

    # need to use health_potion but fail
    if character.hp <= 0.25:
        logging.error("low hp and have no potion")
        send_text("HP过低并且无法回复")
        return strategy_skip()

    return {}


def _maintain_gem(character: Character) -> dict:
    if character.gem != "":
        # logging.debug(f"gem={character.gem}")
        match character.gem:
            case "channelling":
                return strategy_use_gem()
            case "health":
                if character.hp <= 0.7:
                    return strategy_use_gem()
            case "mana":
                if character.mp <= 0.7:
                    return strategy_use_gem()
            case "spirit":
                if character.sp <= 0.75:
                    return strategy_use_gem()
            case _:
                logging.error(f"unknown type of gem={character.gem}")
                return {}
    return {}


def _maintain_buffs(character: Character) -> dict:
    # use spell "regen"
    if not character.have_status("regen"):
        return strategy_use_spell("regen")

    # use spell "heartseeker"
    if character.have_status("channelling") and (not character.have_status("heartseeker")):
        return strategy_use_spell("heartseeker")

    # channelling status means that the next spell will not cost any mana, to find a suitable spell and use
    if character.have_status("channelling"):
        # the buff status are sorted by duration, find the first one
        check_list = ["regen", "spark_of_life", "protection", "heartseeker", "haste", "spirit_shield", "shadow_veil"]
        fastest_expire_status = 'heartseeker'
        for status_name in character.status_list:
            # notice that "auto_" prefix status has different position with what actually showing
            if status_name in check_list:
                fastest_expire_status = status_name
                break
        return strategy_use_spell(fastest_expire_status)

    # too many mana, and recovering more mana by mana_draught, to find a suitable spell and use
    if character.mp >= 0.99 and character.have_status("mana_draught"):
        check_list = ["regen", "spark_of_life", "protection"]
        fastest_expire_status = "regen"
        for status_name in character.status_list:
            # notice that "auto_" prefix status has different position with what actually showing
            if status_name in check_list:
                fastest_expire_status = status_name
                break
        return strategy_use_spell(fastest_expire_status)

    return {}


def _maintain_debuff(character: Character, monster_list: MonsterList) -> dict:
    # DEBUFF_SPELL_LIST = [["weaken", 0.575], ["silence", 0.7], ["imperil", 0.6]]
    # there is no need to use "silence" when battle with normal monsters
    DEBUFF_SPELL_LIST = [["weaken", 0.55], ["imperil", 0.575]]
    for debuff, mp_limit in DEBUFF_SPELL_LIST:
        if (character.have_spell(debuff)
                and mid_level_strategy_common.should_use_spell(monster_list, debuff)
                and character.mp >= mp_limit):
            index = mid_level_strategy_common.get_spell_target_index(monster_list, debuff)
            return strategy_use_spell(debuff, index)
    return {}


def _maintain_spirit_stance(character: Character, monster_list: MonsterList) -> dict:
    # close spirit stance when sp too low, because some defensive buff need enough sp to work
    if character.sp <= 0.38:
        # if spirit stance is open, close it, otherwise do nothing
        if character.spirit_stance:
            return strategy_close_spirit_stance()
        return {}

    # use spirit stance when battle with only 1 boss
    if monster_list.have_boss() and monster_list.get_alive_monster_count() <= 1:
        if character.cp >= 100:
            if not character.spirit_stance:
                return strategy_use_spirit_stance()
        return {}

    # close spirit stance when need to save sp to cast "orbital_friendship_cannon"
    if character.have_spell("cooldown_orbital_friendship_cannon") or character.have_spell("orbital_friendship_cannon"):
        if not monster_list.have_school_girl() and _should_use_orbital_friendship_cannon(monster_list):
            # when battle with school girls, don't do that
            if character.cp <= 208 and character.spirit_stance:
                return strategy_close_spirit_stance()
            return {}

    # close spirit stance when battle with only 1 normal monster
    if monster_list.get_alive_monster_count() <= 1 and 31 <= character.cp <= 90:
        if character.spirit_stance:
            return strategy_close_spirit_stance()

    # use spirit stance when battle with more than 3 normal monsters
    if monster_list.get_alive_monster_count() >= 3 and character.cp >= 160 and not (
            # when need to use orbital_friendship_cannon, don't do that
            character.have_spell("cooldown_orbital_friendship_cannon")):
        if not character.spirit_stance:
            return strategy_use_spirit_stance()

    return {}


def _should_use_orbital_friendship_cannon(monster_list: MonsterList) -> bool:
    monster_count = len(monster_list.monsters)
    alive_monster_count = monster_list.get_alive_monster_count()
    dead_monster_count = monster_count - alive_monster_count
    if monster_count <= 4:
        return False
    if monster_count == 5:
        return dead_monster_count <= 1
    if 6 <= monster_count <= 7:
        return dead_monster_count <= 2
    if 8 <= monster_count <= 9:
        return dead_monster_count <= 3
    # monster_count >= 10
    return dead_monster_count <= 4


def _maintain_orbital_friendship_cannon(character: Character, monster_list: MonsterList) -> dict:
    if character.have_spell("orbital_friendship_cannon"):
        if _should_use_orbital_friendship_cannon(monster_list):
            if not character.spirit_stance and character.cp >= 213:
                return strategy_use_spirit_stance()
            elif character.spirit_stance and character.cp >= 213:
                index = mid_level_strategy_common.get_spell_target_index(monster_list,
                                                                         "orbital_friendship_cannon")
                return strategy_use_spell("orbital_friendship_cannon", index)

    return {}


def maintain_vital_strike(character: Character, monster_list: MonsterList) -> dict:
    if (mid_level_strategy_common.should_use_spell(monster_list, "vital_strike")
            and character.have_spell("vital_strike") and character.cp >= 63):
        if low_level_strategy_boss.should_use_spell_to_boss(monster_list, "vital_strike"):
            # have boss, use "vital_strike"
            if character.spirit_stance:
                index = low_level_strategy_boss.get_boss_spell_target_index(monster_list, "vital_strike")
                return strategy_use_spell("vital_strike", index)
            elif character.cp >= 75:
                return strategy_use_spirit_stance()
        if (character.have_spell("cooldown_orbital_friendship_cannon")
                or character.have_spell("orbital_friendship_cannon")):
            # if "orbital_friendship_cannon" is cooldown, use "vital_strike" only when cp is almost full
            if character.cp >= 245:
                index = mid_level_strategy_common.get_spell_target_index(monster_list, "vital_strike")
                return strategy_use_spell("vital_strike", index)
        else:
            # if "orbital_friendship_cannon" isn't cooldown, use "vital_strike"
            if 63 <= character.cp <= 180 and character.spirit_stance:
                index = mid_level_strategy_common.get_spell_target_index(monster_list, "vital_strike")
                return strategy_use_spell("vital_strike", index)
            # use "vital_strike" when cp is almost full, without anything extra condition
            if character.cp >= 245:
                if character.spirit_stance:
                    index = mid_level_strategy_common.get_spell_target_index(monster_list, "vital_strike")
                    return strategy_use_spell("vital_strike", index)
                else:
                    return strategy_use_spirit_stance()

    return {}


def maintain_shield_bash(character: Character, monster_list: MonsterList) -> dict:
    if character.have_spell("shield_bash") and character.cp >= 37:
        if character.cp >= 245:  # use "shield_bash" only when cp is almost full
            index = mid_level_strategy_common.get_spell_target_index(monster_list, "shield_bash")
            return strategy_use_spell("shield_bash", index)

    return {}


def battle_with_normal_monsters(character: Character, monster_list: MonsterList):
    strategy: dict = _maintain_spirit_stance(character, monster_list)
    if strategy != {}:
        return strategy

    strategy: dict = _maintain_orbital_friendship_cannon(character, monster_list)
    if strategy != {}:
        return strategy

    strategy: dict = _maintain_debuff(character, monster_list)
    if strategy != {}:
        return strategy

    strategy: dict = maintain_vital_strike(character, monster_list)
    if strategy != {}:
        return strategy

    strategy: dict = maintain_shield_bash(character, monster_list)
    if strategy != {}:
        return strategy

    # default, attack the min_hp monster
    strategy: dict = lowest_level_strategy_common.maintain_attack(monster_list, "min_hp")
    if strategy != {}:
        return strategy

    logging.warning("no strategy")
    return strategy_skip()


def get_strategy_arena(character: Character, monster_list: MonsterList):
    if monster_list.get_alive_monster_count() == 0:
        return {}

    # the following is to maintain character's live, should be processed at first priority
    strategy: dict = _maintain_gem(character)
    if strategy != {}:
        return strategy

    strategy: dict = _maintain_xps(character)
    if strategy != {}:
        return strategy

    strategy: dict = _maintain_buffs(character)
    if strategy != {}:
        return strategy

    strategy: dict = strategy_arena_battle_with_boss.battle_with_dragons(character, monster_list)
    if strategy != {}:
        return strategy

    strategy: dict = strategy_arena_battle_with_boss.battle_with_ultimates(character, monster_list)
    if strategy != {}:
        return strategy

    strategy: dict = strategy_arena_battle_with_boss.battle_with_school_girls(character, monster_list)
    if strategy != {}:
        return strategy

    strategy: dict = battle_with_normal_monsters(character, monster_list)
    if strategy != {}:
        return strategy

    logging.warning("no suitable strategy")
    return {}
