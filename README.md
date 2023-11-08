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
  inflicting negative debuffs on monsters. There are also spells that deal damage to monsters, but they are not useful
  for warrior characters.

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

Please be aware that HvBot has several features under development and may contain some bugs that need to be addressed.

- HvBot will have full control over your mouse during its operation. To stop HvBot, you can quickly move your mouse to
  one of the four corners of your screen.
- It is recommended to run HvBot in process mode rather than thread mode to minimize the risk of crashes.

## Project Description

The project is structured as follows:

### Controllers

- Main Controller: Responsible for the overall control and coordination of HvBot's operations.
- Arena Controller: Handles operations related to the arena battles.
- Encounter Controller: Manages operations related to random encounter battles.

### GUI

The GUI module serves as the interface between HvBot's main control program and the PyAutoGUI library. It facilitates
interaction and communication with the graphical elements of the game.

### Identify

The Identify module is responsible for identifying various elements within the game's graphics and extracting relevant
information.

- Identify.Character: Handles the identification and retrieval of information related to characters in the game.
- Identify.Monster: Deals with the identification and extraction of information regarding monsters in the game.

### Strategy

The Strategy module contains different strategies that HvBot can employ during battles.

### Util

The Util module includes utility functions and helpers that support various functionalities within HvBot.

### Development History

#### v0.3.1.1 (release) [Nov. 8th, 2023]

- All tests have passed successfully.
- Fixed issues:
    - Resolved an issue where the program would occasionally become idle when starting an arena or encounter battle.
    - Fixed an issue where the program would become idle during the "dawn_event" encounter.
    - Addressed a problem where, after a battle finishes, the program would sometimes fail to identify the finish
      button. This occurred when the mouse inadvertently selected the finish button, causing its color to turn blue and
      preventing the program from recognizing it. As a result, the program would become idle.
    - Reduced the number of error reporting texts sent when encountering a failure to parse encounter text.

#### v0.3.1.0 [Oct. 24th, 2023]

- New features:
    - Battle_with_dragons: The program can now identify special dragon bosses and utilize specific strategies to battle
      against them.
    - Battle_continue: The auto_arena and auto_encounter commands can now identify if the previous battle was not
      finished and automatically continue from where it left off.
    - Income_statistics: The program can now analyze the finish panel screenshot to calculate income using OCR (Optical
      Character Recognition). However, this feature needs to be run manually.
    - Stamina_statistics: The program can now calculate the stamina cost penalty rate. This feature also needs to be run
      manually.

#### v0.3.0.5  [Oct. 19th, 2023]

- Fixed issues:
    - Resolved an issue where the program would report excessive text to AriaBot when encountering a captcha.
    - Implemented a delay before clicking the start_encounter or start_arena button to allow for proper initialization.
    - Fixed the logic for sending arena_round_info.
    - Fixed the limitation on waiting for the captcha answer.

#### v0.3.0.4 (release) [Oct. 18th, 2023]

- Fixed issues:
    - Resolved an issue where the bot would misjudge the submission of a captcha if the checkbox of "Twilight Sparkle"
      was checked.
    - Addressed a problem where the main_controller thread and the battle thread would simultaneously execute os.chdir,
      leading to crashes. This resulted in the inability to send screenshots and text (main_controller crash) or the
      stoppage of the battle (battle crash).

#### v0.3.0.3 [Oct. 18th, 2023]

- Fixed issues:
    - Implemented a waiting time before confirming the dialog when selecting an arena.
    - Resolved the issue where debuffs were only applied to the monster placed in the first position.

#### v0.3.0.2 [Oct. 16th, 2023]

- Refactored HvBot from v0.2 to v0.3.
- Redesigned the project structure.
- Translated most comments to English.