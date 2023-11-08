import os
from typing import List

from PIL import Image

import hv_bot.util.path
from hv_bot.gui.gui_execute import have_image


def num_index_to_letter_index(index: int):
    return chr(ord("A") + index)


class Monster:

    def __init__(self, index: int, monster_image: Image):
        self.index = index
        self.name = ""
        self.hp = 0.0
        self.mp = 0.0
        self.sp = 0.0
        self.dead = False
        self.status_list = []  # TODO countdown
        self.boss_tag = ""

        # monster_image.show()
        # self.name = get_name(monster_image)

        if judge_dead_monster_by_monster_image(monster_image):
            self.dead = True
        else:
            self.hp, self.mp, self.sp = get_xps_from_monster_image(monster_image)
            self.status_list = get_status_list(monster_image)
            self.boss_tag = judge_boss_by_monster_image(monster_image)
            # Notice that boss_tag = "DRAGON" will be assigned somewhere else

    def __str__(self):
        result = f" index={num_index_to_letter_index(self.index)} "
        if len(self.name) > 0:
            result += f"name={self.name} "
        if self.dead:
            result += "[DEAD] "
            return result
        result += f"hp={self.hp:.2} mp={self.mp:.2} sp={self.sp:.2} "
        if len(self.boss_tag) > 0:
            result += f"[{self.boss_tag}] "
        if len(self.status_list) > 0:
            result += "status_list=" + str(self.status_list) + " "
        return result

    def is_boss(self) -> bool:
        return len(self.boss_tag) > 0

    def is_school_girl(self) -> bool:
        return self.boss_tag == "SCHOOL_GIRL"

    def is_ultimate(self) -> bool:
        return self.boss_tag == "ULTIMATE" or self.boss_tag == "YGGDRASIL"

    def is_yggdrasil(self) -> bool:
        return self.boss_tag == "YGGDRASIL"

    def is_dragon(self) -> bool:
        return self.boss_tag == "DRAGON"

    def have_status(self, status_name: str) -> bool:
        return self.status_list.count(status_name) > 0 or self.status_list.count("auto_" + status_name) > 0

    def calc_deterrent(self, spell_name: str) -> float:
        """
        Calculate the deterrent factor of a monster.

        The deterrent illustrate the power that this monster can deal damage.
        :param spell_name: for using certain specific spell, the deterrent will change
        :return: the deterrent factor
        """
        # TODO identify imperil or armor break
        # a dead monster have no any deterrent
        if self.dead:
            return 0.0
        # to a monster with full mp and sp, the deterrent should be 3.0,
        # don't break this limitation, it relates to how other algorithm works
        deterrent = self.hp * (1.25 + 0.45 * self.mp + 1.30 * self.sp)  #
        # boss can deal much more damage
        if self.is_boss():
            deterrent *= 2.0
        # school_girl is a specific type of boss, dealing much, much more damage
        if self.is_school_girl():
            deterrent *= 3.0
        # yggdrasil have the highest priority to kill
        if self.is_yggdrasil():
            deterrent *= 120
        # if monster have this spell's buff, the spell should choose other monster first
        if self.have_status(spell_name):
            deterrent *= 0.05

        # to a monster with some debuff, it may deal less damage
        DEBUFF_CHECK_LIST = [["stunned", 0.875], ["silence", 0.225], ["weaken", 0.425]]
        for debuff, factor in DEBUFF_CHECK_LIST:
            if self.have_status(debuff):
                # for a spell named in check_list, it should be calc twice, it is not a bug
                deterrent *= factor
        return deterrent


# def get_name(monster_image: Image) -> str:
#     # don't use this function, it is too slow!
#     NAME_BAR_LEFT = 43
#     NAME_BAR_TOP = 4
#     NAME_BAR_WIDTH = 250
#     NAME_BAR_HEIGHT = 15
#     name_bar_box = (NAME_BAR_LEFT, NAME_BAR_TOP, NAME_BAR_LEFT + NAME_BAR_WIDTH, NAME_BAR_TOP + NAME_BAR_HEIGHT)
#     name_bar_box_image: Image = monster_image.crop(name_bar_box)
#
#     # print("time usage {} s".format(timeit(functools.partial(ocr, image=name_bar_box_image), number=1)))
#     name = ocr(name_bar_box_image)
#     return name


def get_xps_from_monster_image(monster_image: Image) -> [float, float, float]:
    XP_BAR_LEFT = 43
    XP_BAR_WIDTH = 118
    XP_BAR_HEIGHT = 10
    XP_BAR_HORIZONTAL_PADDING = 4
    XP_BAR_VERTICAL_PADDING = 4

    HP_BAR_TOP = 19
    MP_BAR_TOP = 31
    SP_BAR_TOP = 43

    XP_BAR_TOPS = [HP_BAR_TOP, MP_BAR_TOP, SP_BAR_TOP]
    xps = []
    for xp_bar_top in XP_BAR_TOPS:
        xp_bar_box = (XP_BAR_LEFT, xp_bar_top, XP_BAR_LEFT + XP_BAR_WIDTH, xp_bar_top + XP_BAR_HEIGHT)
        xp_bar_box_image = monster_image.crop(xp_bar_box)
        # xp_bar_box_image.show()
        rgb_image = xp_bar_box_image.convert("RGB")

        total_xp = XP_BAR_WIDTH - 2 * XP_BAR_HORIZONTAL_PADDING
        current_xp = 0
        for x in range(0 + XP_BAR_HORIZONTAL_PADDING, XP_BAR_WIDTH - XP_BAR_HORIZONTAL_PADDING):
            r, g, b = rgb_image.getpixel((x, XP_BAR_VERTICAL_PADDING))
            total_bright = r + g + b
            if total_bright <= 100:  # 因为怪物空的条是黑色
                break
            current_xp += 1
        xp = current_xp / total_xp
        xps.append(xp)
    hp, mp, sp = xps
    return hp, mp, sp


def is_yggdrasil(monster_image: Image) -> bool:
    os.chdir(hv_bot.util.path.ROOT_PATH)
    needle_image = Image.open("res\\enemies\\monster_name_yggdrasil.png")
    return have_image(needle_image, monster_image, confidence=0.97)


def get_status(monster_image: Image, status_name: str) -> bool:
    os.chdir(hv_bot.util.path.ROOT_PATH)
    needle_image = Image.open(f"res\\enemies\\{status_name}.png")
    return have_image(needle_image, monster_image)


def get_status_list(monster_image: Image) -> List[str]:
    # TODO silenceD, weakenED, imperilED, absorbED
    check_list = ["stunned", "silence", "imperil", "weaken", "absorb", "searing_skin", "penetrated_armor"]
    status_list = []
    for status_name in check_list:
        attend = get_status(monster_image, status_name)
        if attend:
            status_list.append(status_name)

    BACKGROUND_COLOR_DEFAULT = [237, 235, 223]
    BACKGROUND_COLOR_STUNNED = [143, 188, 143]
    rgb_image = monster_image.convert("RGB")
    box_color = rgb_image.getpixel((304, 40))
    total_diff1 = 0
    total_diff2 = 0
    for c in range(3):
        total_diff1 += abs(BACKGROUND_COLOR_DEFAULT[c] - box_color[c])
        total_diff2 += abs(BACKGROUND_COLOR_STUNNED[c] - box_color[c])
    if total_diff1 >= 10 and total_diff2 >= 10:
        status_list.append("too_many")

    return status_list


def judge_dead_monster_by_monster_image(monster_image: Image) -> bool:
    """
    Judge whether a monster is dead, by its image

    This function works by identifying monster's box borders' color
    :param monster_image:
    :return: True for dead, False for not dead
    """
    rgb_image = monster_image.convert("RGB")
    r, g, b = rgb_image.getpixel((0, 0))
    total_bright = r + g + b
    # print("total_bright=" + str(total_bright))
    # alive=230, dead=550, none=690
    if total_bright >= 390:
        return True
    return False


def judge_boss_by_monster_image(monster_image) -> str:
    """
    Judge whether a monster is dead, by its image

    This function works by identifying monster's background color
    :param monster_image:
    :return: boss_type, str, in ["BOSS", "SCHOOL_GIRL", "ULTIMATE"
    """
    # OFFSET 8 8
    # normal_monster 237 235 223
    # boss 230 204 163
    # schoolgirl 227 170 161 （存疑）
    # ultimate 169 137 165
    # stunned 143 188 143

    rgb_image = monster_image.convert("RGB")
    rgb_color = rgb_image.getpixel((8, 8))
    BOSS_TYPE_COLOR_LIST = [
        ["BOSS", [230, 204, 163]],
        ["SCHOOL_GIRL", [219, 168, 160]],
        ["ULTIMATE", [169, 137, 165]],
    ]
    for boss_type, boss_color in BOSS_TYPE_COLOR_LIST:
        total_diff = 0
        for c in range(3):
            total_diff += abs(rgb_color[c] - boss_color[c])
        if total_diff <= 15:
            if boss_type == "ULTIMATE":
                if is_yggdrasil(monster_image):
                    return "YGGDRASIL"
            return boss_type
    return ""
