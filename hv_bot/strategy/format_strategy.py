def strategy_use_spell(spell_name: str, index: int = -1) -> dict:
    return {"action": "use_spell", "spell_name": spell_name, "index": index}


def strategy_use_consumable(consumable_name: str) -> dict:
    return {"action": "use_consumable", "consumable_name": consumable_name}


def strategy_use_gem() -> dict:
    return {"action": "use_gem"}


def strategy_use_spirit_stance() -> dict:
    return {"action": "use_spirit_stance"}


def strategy_close_spirit_stance() -> dict:
    return {"action": "close_spirit_stance"}


def strategy_attack(index: int) -> dict:
    return {"action": "attack", "index": index}


def strategy_skip() -> dict:
    return {"action": "skip"}
