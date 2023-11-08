# HvBot

- **Latest Stable Version:** v0.3.1.1
- **Author:** purinliang
- **Author Email:** purinliang@gmail.com

## Description

HvBot is a program that helps you to automate some actions when playing a less-known web game. The game is one type of
out-of-date RPG (Role-Playing Game) games, without colorful and vivid graphics but just like text-based RPG, but this
feature makes it incredibly suitable for developing easy and simple automatically scripts, to learn and improve
programming skills.

## Game Description

### Character

The character you control, maybe have some job, for example warrior or magician. The latest version HvBot only works for
warrior job, more specifically a warrior using one-handed weapon and a shield.

- Basic status:
    - HP: Health Points.
    - MP: Magic Points. Used for casting spells, for more information, look Spells.
    - SP: Spirit Points. Used for casting Weapon Skills, for more information, look Weapon Skills.
    - CP: Used for casting Weapon Skills, for more information, look Weapon Skills.
- Spells: Spells include supportive spells, which can give you some positive buffs. Or deprecating spells, which can
  give monsters negative debuffs. Or the other spells that deal damage to monsters, but useless to warrior job.
- Weapon Skills: Warrior job can use weapon skills, to deal vital damage to monsters.
- Status: Mostly supportive buffs, which can enhance the power of character, including offensive and defensive.
- Consumables: Character can use consumables to recover basic status, for example HP Potion for recovering 100% HP
  immediately.

### Monster

The monsters you battle with, including normal monsters or bosses. Some bosses can deal huge damage, and they are really
dangerous to character.

- Basic status: Monsters have 3 types of basic status, including HP, MP and SP. MP and SP are used to cast spell,
  dealing much more
  damage than normal attack.
- Status: The status monsters have, normally some debuffs you give to them. For example, "silenced" for cannot cast any
  spells, "
  weakened" for dealing less damage.
- Boss: There are 4 types of bosses, including normal bosses, and special bosses.

## How to use

### Run independently

HvBot can be run independently, by just double-click the scripts (e.g. arena_controller.py and encounter_controller.py
for automatically battle, income_statistics.py and stamina_statistics.py for data analysis).

### Run with AriaBot

However, the most efficient approach to use is to use with AriaBot.

AriaBot is a TelegramBot, and it can help you to control your computer to run some commands or python scripts
automatically. It provides methods to start, monitor, control, interrupt, and close other commands or scripts running in
its sub-threads or sub-processes.

AriaBot can start HvBot by command, and inspect the running status including automatically start arena or random
encounter battle, or start battle with different strategy.

#### AriaBot Commands

The following is all the commands that can be used by AriaBot:

> /hv help

Command **/hv help** can output the help text, including all the commands that can be used by AriaBot and their
corresponding functions.

> /hv auto arena

Command **/hv auto arena** can automatically select the latest arena in the arena selecting panel.

- The bot will check whether random encounter battle is ready, if true, it will tackle random encounter battle first.
- The routine of selecting arena and its corresponding automatic battle will be run twice.
    - However, if the command be executed when the previous battle is not finished, the bot will tackle the previous
      battle in "arena battle mode", and seem that as a normal routine mentioned above.

> /hv auto encounter

Command **/hv auto encounter** can automatically select the random encounter battle, and wait for the next coming random
encounter battle.

- To avoid the power of the computer or the monitor automatically shutdown, when waiting for the next coming random
  encounter battle, the bot will randomly move the mouse periodically.

> /hv once encounter

Command **/hv auto encounter** can automatically select the random encounter battle, but will not wait for the next
coming random
encounter battle, the bot will exit immediately instead.

> /hv arena

Command **/hv arena** can automatically continue a battle in "arena mode".

> /hv encounter

Command **/hv encounter** can automatically continue a battle in "random encounter mode".

> /hv help

Command **/hv help** can output the help text, including all the commands that can be used by AriaBot and their
corresponding functions. (Already mentioned above)

> /hv screenshot

Command **/hv screenshot** can ask the bot to get a screenshot and send it through AriaBot. This command is useful when
need to monitor the running status or check and save the situation that cause bugs. The screenshots caused bugs can be
used as test-case to check whether the new version bot can tackle the problem right.

> /hv close

Command **/hv screenshot** can ask the bot to close itself. Sometimes the bot is running in a wrong situation, this
command can interrupt the wrong running mode. Additionally, this command can also be used to close the bot for saving
power of the computer.

### Attention

In addition, there are a lot of features to develop and some bugs to fix.

- HvBot will **fully control** your mouse, to stop it, move your mouse quickly to one of the 4 corners of your screen.

- Sometimes HvBot may crash, so run in **process mode** is preferable, rather than thread mode.

## Project Description

### Project Structure

- Controllers
    - Main Controller
    - Arena Controller
    - Encounter Controller
- GUI: The interface that between HvBot's main control program and PyAutoGUI library.
- Identify: To Identify the graph and get corresponding information.
    - Identify.Character
    - Identify.Monster
- Strategy
    - Deterrent
- Util

### Development History

#### v0.3.1.1 [Nov. 8th, 2023]

- All Test passed.
- The issues remained in v0.3.1.0 have been fixed.

#### v0.3.1.0 [Oct. 24th, 2023]

- Remained issues:
    - When start arena or encounter, sometimes the program will be idle.
    - When encounter dawn_event, the program will be idle.
    - When battle finish, sometimes the mouse will select the finish_button make its color turn into blue, leading the
      program can not identify to finish button, and the program will be idle.
    - When parse encounter_text fail, the program send too many error reporting texts.
- New features:
    - Battle_with_dragons: Now the program can identify special dragon bosses and use specific strategy to battle with
      them.
    - Battle_continue: Now auto_arena and auto_encounter command can identify the status that the previous battle is not
      finished, and automatically continue the battle.
    - Income_statistics: Now the program can analysis the finish panel screenshot to calc income by OCR. But it needs to
      be run manually.
    - Stamina_statistics: Now the program can calc the stamina cost penalty rate. But it needs to
      be run manually.
