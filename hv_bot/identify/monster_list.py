import logging

from PIL import Image

from hv_bot.identify.monster import Monster
from hv_bot.util.ocr import ocr_single_line_text

FULLSCREEN_WIDTH = 1238
FULLSCREEN_HEIGHT = 704

MONSTER_A_BOX_LEFT = 697
MONSTER_A_BOX_TOP = 47
MONSTER_BOX_WIDTH = 366
MONSTER_BOX_HEIGHT = 56
MONSTER_HEIGHT_DIFFERENCE = 58


class MonsterList:

    def __init__(self):
        self.monsters = []
        self.round_count = 0
        self.sum_round = 0

    def __str__(self):
        result = 'MonsterInformation: \n'
        for monster in self.monsters:
            result += '    ' + monster.__str__() + '\n'
        return result

    def get_alive_monster_count(self) -> int:
        """
        Count how many monsters are still alive
        :return: count
        """
        res = 0
        for m in self.monsters:
            m: Monster = m
            if not m.dead:
                res += 1
        return res

    def have_boss(self) -> bool:
        """
        have any boss?
        :return: True or False
        """
        return any([(not monster.dead and monster.is_boss()) for monster in self.monsters])

    def have_school_girl(self) -> bool:
        """
        have any school girl?
        :return: True or False
        """
        return any([(not monster.dead and monster.is_school_girl()) for monster in self.monsters])

    def have_ultimate(self) -> bool:
        """
        have any ultimate?
        :return: True or False
        """
        return any([(not monster.dead and monster.is_ultimate()) for monster in self.monsters])

    @classmethod
    def number_index_to_letter_index(cls, index: int) -> str:
        """
        Convert number index to letter index

        For example, 0 to "A", 1 to "B"
        :param index:
        :return:
        """
        return chr(ord("A") + index)

    @classmethod
    def calc_location_by_index(cls, index: int) -> [int, int]:
        """
        Calculate location by monster's index
        :param index: monster's index, a 0-index int
        :return: [x, y] monster's location
        """
        if index < 0:
            logging.error(f"calc_location_by_index monster index={index}")
            return [-1, -1]
        x = MONSTER_A_BOX_LEFT
        y = MONSTER_A_BOX_TOP + index * MONSTER_HEIGHT_DIFFERENCE
        x += 23
        y += MONSTER_BOX_HEIGHT / 2
        return [x, y]

    def get_ygg_index(self) -> int:
        for monster in self.monsters:
            if monster.is_yggdrasil():
                return monster.index
        return -1


def crop_monster_image(fullscreen_image: Image, monster_index: int):
    monster_box = (
        MONSTER_A_BOX_LEFT,
        MONSTER_A_BOX_TOP + MONSTER_HEIGHT_DIFFERENCE * monster_index,
        MONSTER_A_BOX_LEFT + MONSTER_BOX_WIDTH,
        MONSTER_A_BOX_TOP + MONSTER_HEIGHT_DIFFERENCE * monster_index + MONSTER_BOX_HEIGHT
    )

    monster_image = fullscreen_image.crop(monster_box)
    # monster_image.show()
    rgb_image = monster_image.convert("RGB")
    r, g, b = rgb_image.getpixel((0, 0))
    total_bright = r + g + b
    # print("total_bright=" + str(total_bright))
    # alive=230, dead=550, none=690
    if total_bright >= 620:
        return None
    return monster_image


def crop_round_image(fullscreen_image: Image, monster_count: int):
    round_box = [
        MONSTER_A_BOX_LEFT,
        MONSTER_A_BOX_TOP + MONSTER_HEIGHT_DIFFERENCE * monster_count,
        MONSTER_A_BOX_LEFT + MONSTER_BOX_WIDTH,
        MONSTER_A_BOX_TOP + MONSTER_HEIGHT_DIFFERENCE * monster_count + MONSTER_BOX_HEIGHT
    ]

    round_image = fullscreen_image.crop(round_box)
    return round_image


def get_monster_list(fullscreen_image: Image, *, ocr_round_count=False) -> MonsterList:
    """
    Get monster list by fullscreen image
    :param ocr_round_count:
    :param fullscreen_image:
    :return:
    """
    MONSTER_COUNT_LIMITATION = 10

    monsters = []
    for monster_index in range(0, MONSTER_COUNT_LIMITATION):
        monster_image = crop_monster_image(fullscreen_image, monster_index)
        if monster_image is None:
            # no more monster
            break
        monster: Monster = Monster(monster_index, monster_image)
        monsters.append(monster)

    monster_list = MonsterList()
    monster_list.monsters = monsters

    if ocr_round_count:
        # round_count attend below the last monster
        round_image = crop_round_image(fullscreen_image, len(monsters))
        # round_image.show()
        text = ocr_single_line_text(round_image)
        logging.warning(f"ocr_round_count: text={text}")
        if text.startswith("Round "):
            text = text.removeprefix("Round ")
            round_count, sum_round = 0, 0
            try:
                round_count, sum_round = map(int, text.split("/"))
            except ValueError as error:
                logging.error(error)
            if round_count > 0 and sum_round > 0:
                monster_list.round_count = round_count
                monster_list.sum_round = sum_round
                logging.warning(f"ocr_round_count: round_count/sum_round={round_count}/{sum_round}")

    return monster_list
