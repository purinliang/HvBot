# HvBot

- **Latest Stable Version:** v0.3.1.1
- **Author:** purinliang
- **Author Email:** purinliang@gmail.com

## Description

HvBot is a program that helps you automate actions while playing a lesser-known out-of-date web game. The game is a type
of RPG (Role-Playing Game) with a text-based interface instead of fancy graphics. This simplicity makes it perfect for
developing easy and straightforward automation scripts, allowing you to learn and improve your programming skills.

## Game Description

### Character

In the game, you control a character who can have different jobs, such as a warrior or a magician. However, the latest
version of HvBot is specifically designed for the warrior job, particularly for warriors who use a one-handed weapon and
a shield.

- **Basic Status:**
    - **HP:** Health Points, which represent the character's health.
    - **MP:** Magic Points, used for casting spells (more details in the "Spells" section).
    - **SP:** Spirit Points, used for casting Weapon Skills (more details in the "Weapon Skills" section).
    - **DP:** Used for casting Weapon Skills (more details in the "Weapon Skills" section).

- **Spells:** Spells in the game can be supportive, providing positive buffs to the character, or deprecating,
  inflicting
  negative debuffs on monsters. There are also spells that deal damage to monsters, but they are not useful for warrior
  characters.

- **Weapon Skills:** Warrior characters can use special Weapon Skills that allow them to deal significant damage to
  monsters.

- **Status:** These are mostly supportive buffs that enhance the character's power, both in offense and defense.

- **Consumables:** Characters can use consumable items to recover their basic status. For example, an HP Potion can
  instantly restore 100% of the character's HP.

### Monsters

In the game, you will encounter various types of monsters, including normal monsters and bosses. Some bosses can inflict
significant damage and pose a real threat to your character.

- **Basic Status:** Monsters have three types of basic status:
    - **HP:** Health Points
    - **MP:** Magic Points
    - **SP:** Spirit Points
    - MP and SP are used by monsters to cast spells, which can cause much more damage than their normal attacks.

- **Status:** Monsters can also have status effects, which are typically debuffs inflicted by the player. For example, a
  monster may be "silenced," meaning it cannot cast any spells, or "weakened," resulting in reduced damage output.

- **Bosses:** There are four types of bosses in the game, including normal bosses and special bosses. These bosses are
  typically more challenging to defeat and may require specific strategies to overcome.

## How to use

### Run Independently

You can run HvBot independently by double-clicking on the scripts:

- arena_controller.py or encounter_controller.py to automatically engage in battles.

- income_statistics.py or stamina_statistics.py for data analysis purposes.

### Run with AriaBot

To maximize efficiency, it is recommended to use HvBot with AriaBot.

AriaBot is a TelegramBot that enables you to control your computer and automate the execution of commands or Python
scripts. It offers a range of methods for starting, monitoring, controlling, interrupting, and closing other commands or
scripts running within its sub-threads or sub-processes.

By using AriaBot, you can start HvBot through a command and inspect its running status. Additionally, AriaBot allows you
to automatically initiate battles in the arena or with random encounters. You can also customize the battle strategy
based on your preferences.

By leveraging the capabilities of AriaBot, you can enhance your control over HvBot and streamline your gaming
experience.

#### AriaBot Commands

To control HvBot using AriaBot, you need to start the AriaBot server on your computer and send commands through the
Telegram bot **@ArcticAriaBot**.

Here are all the commands that can be used with AriaBot:

1. `/hv help`

    - The command `/hv help` displays the help text, which includes a list of commands that can be used with
      AriaBot, along with their corresponding functions.

2. `/hv auto arena`

    - The command `/hv auto arena` automatically selects the latest arena from the arena selection panel.

    - The bot will check if a random encounter battle is ready. If true, it will prioritize tackling the random
      encounter battle first.

    - The routine of selecting the arena and initiating the automatic battle will be executed twice.
        - However, if the command is executed while a previous battle is still in progress, the bot will continue with
          the previous battle in "arena battle mode," as part of the normal routine mentioned above.

3. `/hv auto encounter`

    - The command `/hv auto encounter` automatically selects the random encounter battle and waits for the next one to
      occur.

    - To prevent the computer or monitor from automatically shutting down during the wait for the next random encounter
      battle, the bot will periodically move the mouse randomly.

4. `/hv once encounter`

    - The command `/hv once encounter` automatically selects the random encounter battle but does not wait for the next
      one. Instead, the bot will exit immediately.

5. `/hv arena`

    - The command `/hv arena` automatically continues a battle in "arena mode".

6. `/hv encounter`

    - The command `/hv encounter` automatically continues a battle in "random encounter mode".

7. `/hv help`

    - The command `/hv help` outputs the help text, which includes a list of commands that can be used with AriaBot and
      their corresponding functions. (Already mentioned above)

8. `/hv screenshot`

    - The command `/hv screenshot` instructs the bot to capture a screenshot and send it through AriaBot.

        - This command is useful for monitoring the running status, checking for bugs, and saving the current situation
          as a test case.

        - Screenshots of situation that cause bugs can be used to verify whether the new version of the bot can handle
          the issue correctly.

9. `/hv close`

    - The command `/hv close` instructs the bot to close itself. This command can be useful in situations where the bot
      is running incorrectly and needs to be interrupted. Additionally, it can be used to close the bot and save power
      on the computer.

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

#### v0.3.1.1(release) [Nov. 8th, 2023]

- All Test passed.

- Fixed issues:
    - When start arena or encounter, sometimes the program will be idle.
    - When encounter dawn_event, the program will be idle.
    - When battle finish, sometimes the mouse will select the finish_button make its color turn into blue, leading the
      program can not identify to finish button, and the program will be idle.
    - When parse encounter_text fail, the program send too many error reporting texts.

#### v0.3.1.0 [Oct. 24th, 2023]

- New features:
    - Battle_with_dragons: Now the program can identify special dragon bosses and use specific strategy to battle with
      them.
    - Battle_continue: Now auto_arena and auto_encounter command can identify the status that the previous battle is not
      finished, and automatically continue the battle.
    - Income_statistics: Now the program can analysis the finish panel screenshot to calc income by OCR. But it needs to
      be run manually.
    - Stamina_statistics: Now the program can calc the stamina cost penalty rate. But it needs to
      be run manually.

#### v0.3.0.5  [Oct. 19th, 2023]

- Fixed issues:
    - When meeting captcha, report too much text to AriaBot.
    - Before clicking start_encounter or start_arena, wait some seconds.
    - Fix the arena_round_info sending logic
    - Fix the limitation of waiting captcha answer

- New features:
    - Now can calc stamina cost penalty manually

#### v0.3.0.4 (released)  [Oct. 18th, 2023]

- Fixed issues:
    - When submitting captcha, if the checkbox of twilight sparkle is checked, the bot will misjudge that the captcha
      has been submitted.
    - When receiving command "/hv screenshot", thread main_controller will os.chdir, while battle thread also os.chdir
      at the same time, sometimes it will lead to one of them threads crash. it seems like cannot send screenshot and
      send text anymore (main_controller crash) or battle is stopped (battle crash).

#### v0.3.0.3 [Oct. 18th, 2023]

- Fixed issues:
    - Before confirming the dialog when selecting an arena, there is no waiting time.
    - Only use debuff to the first position.

#### v0.3.0.2 [Oct. 16th, 2023]

- Refactor HvBot v0.2, updating to v0.3

- Redesign the structure of the project

- Translate most comments to English