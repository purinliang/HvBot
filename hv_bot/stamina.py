import logging

import hv_bot.util.logger


def calc_stamina_cost_penalty(start_stamina: int, end_stamina: int, battle_round_count: int) -> float:
    STAMINA_COST_RATE_GREAT = 0.03
    STAMINA_COST_RATE_NORMAL = 0.02
    STAMINA_GREAT_THRESHOLD = 60
    stamina_cost_great = max(0, start_stamina - STAMINA_GREAT_THRESHOLD)
    stamina_cost_normal = start_stamina - end_stamina - stamina_cost_great

    original_battle_round_count_great = stamina_cost_great / STAMINA_COST_RATE_GREAT
    original_battle_round_count_normal = stamina_cost_normal / STAMINA_COST_RATE_NORMAL

    original_battle_round_count = original_battle_round_count_great + original_battle_round_count_normal
    stamina_cost_penalty = original_battle_round_count / battle_round_count

    battle_round_great = stamina_cost_great / (STAMINA_COST_RATE_GREAT * stamina_cost_penalty)
    battle_round_normal = stamina_cost_normal / (STAMINA_COST_RATE_NORMAL * stamina_cost_penalty)

    logging.warning(f"stamina_cost_penalty={stamina_cost_penalty:.3f}")
    logging.warning(f"battle_round_great={battle_round_great:.2f}")
    logging.warning(f"battle_round_normal={battle_round_normal:.2f}")
    return stamina_cost_penalty


if __name__ == "__main__":
    hv_bot.util.logger.init_logger()
    calc_stamina_cost_penalty(57, 41, 330)
