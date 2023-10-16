import logging
import os
import unittest

from PIL import Image

from hv_bot.gui.gui_interface import get_info_from_fullscreen_image
from hv_bot.util import logger


class MyTestCase(unittest.TestCase):
    def test_get_info_from_fullscreen_image_1(self):
        fullscreen_image = Image.open(r"res\dialog_1005_085250.png")
        character, monster_list = get_info_from_fullscreen_image(fullscreen_image)
        logging.debug(character)
        logging.debug(monster_list)

        self.assertIsNone(character)
        self.assertIsNone(monster_list)

    def test_get_info_from_fullscreen_image_2(self):
        fullscreen_image = Image.open(r"res\finish_1007_015340.png")
        character, monster_list = get_info_from_fullscreen_image(fullscreen_image)
        logging.debug(character)
        logging.debug(monster_list)

        self.assertIsNone(character)
        self.assertIsNone(monster_list)

    def test_get_info_from_fullscreen_image_3(self):
        fullscreen_image = Image.open(r"res\screenshot_1012_021701.png")
        character, monster_list = get_info_from_fullscreen_image(fullscreen_image)
        logging.debug(character)
        logging.debug(monster_list)

        hp = 1.0
        mp = 0.848
        sp = 0.995
        cp = 104
        self.assertAlmostEqual(hp, character.hp, places=3)
        self.assertAlmostEqual(mp, character.mp, places=3)
        self.assertAlmostEqual(sp, character.sp, places=3)
        self.assertAlmostEqual(cp, character.cp)
        spirit_stance = False
        self.assertEqual(spirit_stance, character.spirit_stance)
        status_list = ['auto_shadow_veil', 'shadow_veil', 'auto_haste', 'haste', 'heartseeker',
                       'mana_draught', 'health_draught', 'spirit_shield', 'regen', 'spark_of_life', 'protection']
        self.assertListEqual(status_list, character.status_list)
        spell_list = [['regen', 0], ['heartseeker', 2], ['protection', 4], ['spark_of_life', 5], ['haste', 3],
                      ['spirit_shield', 6], ['shadow_veil', 1], ['imperil', 7], ['weaken', 8], ['silence', 9],
                      ['cure', 10], ['orbital_friendship_cannon', -1], ['cooldown_orbital_friendship_cannon', 12],
                      ['shield_bash', 13], ['cooldown_shield_bash', -1], ['vital_strike', 14],
                      ['cooldown_vital_strike', -1]]
        self.assertListEqual(spell_list, character.spell_list)
        consumable_list = ['health_draught', 'mana_draught', 'spirit_draught', 'health_potion', 'mana_potion',
                           'spirit_potion', 'BLANK', 'BLANK', 'BLANK', 'BLANK', 'BLANK', 'BLANK']
        self.assertListEqual(consumable_list, character.consumable_list)
        gem = ""
        self.assertEqual(gem, character.gem)

        self.assertTrue(monster_list.get_alive_monster_count() == 4)
        self.assertFalse(monster_list.have_boss())
        self.assertTrue(len(monster_list.monsters[0].status_list) == 0)
        self.assertTrue(len(monster_list.monsters[1].status_list) == 1)
        self.assertTrue(monster_list.monsters[1].have_status("shocked") == 1)

    def test_get_info_from_fullscreen_image_4(self):
        fullscreen_image = Image.open(r"res\screenshot_1010_123441.png")
        character, monster_list = get_info_from_fullscreen_image(fullscreen_image)
        logging.debug(character)
        logging.debug(monster_list)

        hp = 1.0
        mp = 0.748
        sp = 0.75
        cp = 65
        self.assertAlmostEqual(hp, character.hp, places=3)
        self.assertAlmostEqual(mp, character.mp, places=3)
        self.assertAlmostEqual(sp, character.sp, places=3)
        self.assertAlmostEqual(cp, character.cp)
        spirit_stance = True
        self.assertEqual(spirit_stance, character.spirit_stance)
        status_list = ['auto_haste', 'haste', 'auto_protection', 'protection', 'mana_draught', 'regen',
                       'spirit_shield', 'heartseeker', 'shadow_veil', 'spark_of_life']
        self.assertListEqual(status_list, character.status_list)
        spell_list = [['regen', 0], ['heartseeker', 2], ['protection', 4], ['spark_of_life', 5], ['haste', 3],
                      ['spirit_shield', 6], ['shadow_veil', 1], ['imperil', 7], ['weaken', 8], ['silence', 9],
                      ['cure', 10], ['orbital_friendship_cannon', -1], ['cooldown_orbital_friendship_cannon', 12],
                      ['shield_bash', 13], ['cooldown_shield_bash', -1], ['vital_strike', 14],
                      ['cooldown_vital_strike', -1]]
        self.assertListEqual(spell_list, character.spell_list)
        consumable_list = ['health_draught', 'mana_draught', 'spirit_draught', 'health_potion', 'mana_potion',
                           'spirit_potion', 'BLANK', 'BLANK', 'BLANK', 'BLANK', 'BLANK', 'BLANK']
        self.assertListEqual(consumable_list, character.consumable_list)
        gem = ""
        self.assertEqual(gem, character.gem)

        self.assertTrue(monster_list.get_alive_monster_count() == 8)
        self.assertTrue(monster_list.have_boss())
        self.assertFalse(monster_list.have_ultimate())
        self.assertTrue(monster_list.have_school_girl())
        self.assertTrue(len(monster_list.monsters[0].status_list) == 0)
        self.assertTrue(monster_list.monsters[0].is_school_girl())
        self.assertTrue(len(monster_list.monsters[1].status_list) == 0)
        self.assertTrue(monster_list.monsters[1].is_school_girl())

    def test_get_info_from_fullscreen_image_5(self):
        fullscreen_image = Image.open(r"res\screenshot_1010_130859.png")
        character, monster_list = get_info_from_fullscreen_image(fullscreen_image)
        logging.debug(character)
        logging.debug(monster_list)

        hp = 1.0
        mp = 0.686
        sp = 0.826
        cp = 98
        self.assertAlmostEqual(hp, character.hp, places=3)
        self.assertAlmostEqual(mp, character.mp, places=3)
        self.assertAlmostEqual(sp, character.sp, places=3)
        self.assertAlmostEqual(cp, character.cp)
        spirit_stance = False
        self.assertEqual(spirit_stance, character.spirit_stance)
        status_list = ['mana_draught', 'shadow_veil', 'heartseeker', 'spark_of_life', 'spirit_shield',
                       'regen', 'protection', 'haste']
        self.assertListEqual(status_list, character.status_list)
        spell_list = [['regen', 0], ['heartseeker', 2], ['protection', 4], ['spark_of_life', 5], ['haste', 3],
                      ['spirit_shield', 6], ['shadow_veil', 1], ['imperil', 7], ['weaken', 8], ['silence', 9],
                      ['cure', 10], ['orbital_friendship_cannon', -1], ['cooldown_orbital_friendship_cannon', 12],
                      ['shield_bash', 13], ['cooldown_shield_bash', -1], ['vital_strike', 14],
                      ['cooldown_vital_strike', -1]]
        self.assertListEqual(spell_list, character.spell_list)
        consumable_list = ['health_draught', 'mana_draught', 'spirit_draught', 'health_potion', 'mana_potion',
                           'spirit_potion', 'BLANK', 'BLANK', 'BLANK', 'BLANK', 'BLANK', 'BLANK']
        self.assertListEqual(consumable_list, character.consumable_list)
        gem = ""
        self.assertEqual(gem, character.gem)

        self.assertTrue(monster_list.get_alive_monster_count() == 9)
        self.assertTrue(monster_list.have_boss())
        self.assertFalse(monster_list.have_ultimate())
        self.assertTrue(monster_list.have_school_girl())
        self.assertTrue(len(monster_list.monsters[0].status_list) == 0)
        self.assertTrue(monster_list.monsters[0].is_school_girl())
        self.assertTrue(len(monster_list.monsters[1].status_list) == 0)
        self.assertFalse(monster_list.monsters[1].is_school_girl())

    def test_get_info_from_fullscreen_image_6(self):
        fullscreen_image = Image.open(r"res\screenshot_1012_011343.png")
        character, monster_list = get_info_from_fullscreen_image(fullscreen_image)
        logging.debug(character)
        logging.debug(monster_list)

        hp = 0.983
        mp = 0.49
        sp = 0.958
        cp = 115
        self.assertAlmostEqual(hp, character.hp, places=3)
        self.assertAlmostEqual(mp, character.mp, places=3)
        self.assertAlmostEqual(sp, character.sp, places=3)
        self.assertAlmostEqual(cp, character.cp)
        spirit_stance = False
        self.assertEqual(spirit_stance, character.spirit_stance)
        status_list = ['auto_spark_of_life', 'spark_of_life', 'auto_shadow_veil', 'shadow_veil', 'auto_haste', 'haste',
                       'mana_draught', 'regen', 'protection', 'spirit_shield', 'heartseeker']
        self.assertListEqual(status_list, character.status_list)
        spell_list = [['regen', 0], ['heartseeker', 2], ['protection', 4], ['spark_of_life', 5], ['haste', 3],
                      ['spirit_shield', 6], ['shadow_veil', 1], ['imperil', 7], ['weaken', 8], ['silence', 9],
                      ['cure', 10], ['orbital_friendship_cannon', -1], ['cooldown_orbital_friendship_cannon', 12],
                      ['shield_bash', 13], ['cooldown_shield_bash', -1], ['vital_strike', 14],
                      ['cooldown_vital_strike', -1]]
        self.assertListEqual(spell_list, character.spell_list)
        consumable_list = ['health_draught', 'spirit_draught', 'health_potion', 'mana_potion', 'spirit_potion',
                           'BLANK', 'BLANK', 'BLANK', 'BLANK', 'BLANK', 'BLANK']
        self.assertListEqual(consumable_list, character.consumable_list)
        gem = "health"
        self.assertEqual(gem, character.gem)

        self.assertTrue(monster_list.get_alive_monster_count() == 6)
        self.assertTrue(monster_list.have_boss())
        self.assertFalse(monster_list.have_ultimate())
        self.assertTrue(monster_list.have_school_girl())
        self.assertTrue(len(monster_list.monsters[0].status_list) == 0)
        self.assertFalse(monster_list.monsters[0].is_school_girl())
        self.assertTrue(len(monster_list.monsters[1].status_list) == 0)
        self.assertTrue(monster_list.monsters[1].is_school_girl())
        self.assertTrue(len(monster_list.monsters[5].status_list) == 1)
        self.assertTrue(monster_list.monsters[5].have_status("shocked"))

    def setUp(self) -> None:
        logger.init_logger()
        logging.getLogger().setLevel(logging.DEBUG)
        logging.error("------")

    def tearDown(self) -> None:
        DIR_PATH = os.path.dirname(os.path.realpath(__file__))
        os.chdir(DIR_PATH)


if __name__ == "__main__":
    unittest.main()
