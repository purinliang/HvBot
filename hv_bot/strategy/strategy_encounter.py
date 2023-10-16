from hv_bot.identify.character import Character
from hv_bot.identify.monster_list import MonsterList
from hv_bot.strategy import lowest_level_strategy_common, mid_level_strategy_common
from hv_bot.strategy.format_strategy import strategy_use_spell, strategy_use_spirit_stance, strategy_skip


def get_strategy_encounter(character: Character, monster_list: MonsterList):
    if character.hp <= 0.35:
        if not character.have_spell("cure"):
            return strategy_skip()
        return strategy_use_spell("cure")

    if character.hp <= 0.65:
        if character.have_spell("cure"):
            return strategy_use_spell('cure')

    if character.have_spell("regen") and not character.have_status("regen"):
        return strategy_use_spell("regen")

    if (character.mp >= 0.375 and character.have_spell("silence")
            and mid_level_strategy_common.should_use_spell(monster_list, "silence", force_use=True)):
        index = mid_level_strategy_common.get_spell_target_index(monster_list, "silence", force_use=True)
        return strategy_use_spell("silence", index)

    if (character.mp >= 0.35 and character.have_spell("weaken")
            and mid_level_strategy_common.should_use_spell(monster_list, "weaken", force_use=False)):
        index = mid_level_strategy_common.get_spell_target_index(monster_list, "weaken", force_use=True)
        return strategy_use_spell("weaken", index)

    if character.have_spell("orbital_friendship_cannon") and character.cp >= 212:
        if not character.spirit_stance:
            return strategy_use_spirit_stance()
        index = mid_level_strategy_common.get_spell_target_index(monster_list, "orbital_friendship_cannon",
                                                                 force_use=True)
        return strategy_use_spell("orbital_friendship_cannon", index)

    # in encounter, attack the monster with "max_hp",
    # because they will be killed by "orbital_friendship_cannon" together
    return lowest_level_strategy_common.maintain_attack(monster_list, "max_hp")
