import logging
import os

from PIL import Image

import hv_bot.util.path
from hv_bot.gui.gui_execute import have_image
from hv_bot.identify.character_comsuable import (_calc_consumable_location_from_name, calc_gem_status,
                                                 GEM_HEIGHT, GEM_TOP, GEM_WIDTH, GEM_LEFT, get_consumable_list)
from hv_bot.identify.character_spells import calc_spell_location_from_index, crop_spell_bar_image, get_spell_list
from hv_bot.identify.character_status import crop_status_bar_image, get_status_list
from hv_bot.identify.character_xps import get_xps_from_xp_bar_image, crop_xp_bar_image


class Character:
    def __init__(self):
        self.hp = 0.0
        self.mp = 0.0
        self.sp = 0.0
        self.cp = 0
        self.spirit_stance = False
        self.status_list = []  # TODO countdown
        self.spell_list = []  # TODO countdown
        self.consumable_list = []  # TODO now is using location to identify distinct consumables, which is not reliable
        self.gem = ""
        self.exp = 0.0
        return

    def __str__(self):
        return (
            "CharacterInformation: \n"
            f"    hp={self.hp:.3f} mp={self.mp:.3f} sp={self.sp:.3f} cp={self.cp} \n"
            f"    spirit_stance={self.spirit_stance}\n"
            f"    status_list: {self.status_list}\n"
            f"    spell_list: {self.spell_list}\n"
            f"    consumable_list: {self.consumable_list}\n"
            f"    gem={self.gem}\n"
            f"    exp={self.exp:.2f}%"
        )

    def have_status(self, status_name) -> bool:
        return self.status_list.count(status_name) > 0

    def have_spell(self, spell_name) -> bool:
        spell_status = [spell for spell in self.spell_list if spell[0] == spell_name]
        return len(spell_status) > 0 and spell_status[0][1] != -1  # -1 indicates that not find

    def have_consumable(self, consumable_name) -> bool:
        return self.consumable_list.count(consumable_name) > 0

    def get_spell_location(self, spell_name: str) -> [int, int]:
        spellIndex = -1
        for spell in self.spell_list:
            if spell[0] == spell_name:
                spellIndex = spell[1]
                break
        x, y = calc_spell_location_from_index(spellIndex)
        return [x, y]

    @staticmethod
    def get_consumable_location(consumable_name) -> [int, int]:
        x, y = _calc_consumable_location_from_name(consumable_name)  # TODO read from config, rather than write in code
        return [x, y]

    @staticmethod
    def get_spirit_stance_location() -> [int, int]:
        SPIRIT_STANCE_CENTER_X = 387
        SPIRIT_STANCE_CENTER_Y = 58
        return [SPIRIT_STANCE_CENTER_X, SPIRIT_STANCE_CENTER_Y]

    @staticmethod
    def get_gem_location() -> [int, int]:
        return [GEM_LEFT + GEM_WIDTH // 2, GEM_TOP + GEM_HEIGHT // 2]


def get_spirit_stance(fullscreen_image: Image) -> bool:
    os.chdir(hv_bot.util.path.ROOT_PATH)
    spirit_image = Image.open("res\\character\\spirit.png")
    have_spirit_image = have_image(spirit_image, fullscreen_image)
    spirit_red_image = Image.open("res\\character\\spirit_red.png")
    have_spirit_red_image = have_image(spirit_red_image, fullscreen_image)
    # red indicates "spirit stance opened"
    if have_spirit_image and not have_spirit_red_image:
        return False
    elif have_spirit_red_image and not have_spirit_image:
        return True
    logging.error(f"get_spirit_stance error, have_spirit_image={have_spirit_image},"
                  f" have_spirit_red_image={have_spirit_red_image}")
    return False


def _have_attack(fullscreen_image: Image) -> bool:
    os.chdir(hv_bot.util.path.ROOT_PATH)
    attack_image = Image.open("res\\character\\attack.png")
    return have_image(attack_image, fullscreen_image)


def get_exp(fullscreen_image: Image) -> float:
    EXP_BAR_BOX_LEFT = 0
    EXP_BAR_BOX_TOP = 692
    EXP_BAR_BOX_WIDTH = 1238
    EXP_BAR_BOX_HEIGHT = 12

    box = [
        EXP_BAR_BOX_LEFT,
        EXP_BAR_BOX_TOP,
        EXP_BAR_BOX_LEFT + EXP_BAR_BOX_WIDTH,
        EXP_BAR_BOX_TOP + EXP_BAR_BOX_HEIGHT
    ]

    exp_bar_image = fullscreen_image.crop(box)

    rgb_image = exp_bar_image.convert("RGB")

    total_exp = EXP_BAR_BOX_WIDTH
    current_exp = 0
    # threshold: EXP: 560/690
    for x in range(0, EXP_BAR_BOX_WIDTH):
        r, g, b = rgb_image.getpixel((x, EXP_BAR_BOX_HEIGHT // 2))
        # print(r, g, b)
        total_bright = r + g + b
        if total_bright >= 625:
            break
        current_exp += 1
    exp = current_exp / total_exp * 100
    return exp


def get_character(fullscreen_image: Image) -> Character | None:
    character = Character()

    if not _have_attack(fullscreen_image):
        return None

    hp, mp, sp, cp = get_xps_from_xp_bar_image(crop_xp_bar_image(fullscreen_image))
    character.hp, character.mp, character.sp, character.cp = hp, mp, sp, int(cp * 250)
    character.spirit_stance = get_spirit_stance(fullscreen_image)

    character.status_list = get_status_list(crop_status_bar_image(fullscreen_image))
    character.spell_list = get_spell_list(crop_spell_bar_image(fullscreen_image))

    character.consumable_list = get_consumable_list(fullscreen_image)
    character.gem = calc_gem_status(fullscreen_image)

    character.exp = get_exp(fullscreen_image)

    if hp <= 0.001 or (not character.status_list and not character.consumable_list):
        return None
    return character
