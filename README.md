# HvBot

version: 0.3.1.0

author: purinliang

author email: purinliang@gmail.com

## Description

HvBot is a program that helps you to automate some actions when playing a well-known web game named __h*****v****__.

### Run with AriaBot

HvBot can be run independently. However, the most efficient approach to use is to use with AriaBot.

AriaBot can start HvBot by command, and inspect the running status including automatically start Arena or Random
Encounter battle, or start battle with different strategy.

### Attention

In addition, there are a lot of features to develop and some bugs to fix.

- HvBot will **fully control** your mouse, to stop it, move your mouse quickly to one of the 4 corners of your screen.

- Sometimes HvBot may crash, so run in **process mode** is preferable, rather than thread mode.

### Development History

#### v0.3.1.0 [Oct. 24th, 2023]

- Remained issues:

    - When start arena or encounter, sometimes the program will be idle.
    - When encounter dawn_event, the program will be idle.
    - When battle finish, sometimes the mouse will select the finish_button make its color turn into blue, leading the
      program can not identify to finish button, and the program will be idle.
    - When parse encounter_text fail, the program send too many error reporting texts.

- All tests passed

- Ready to test

- New features:

    - Battle_with_dragons: Now the program can identify special dragon bosses and use specific strategy to battle with
      them.
    - Battle_continue: Now auto_arena and auto_encounter command can identify the status that the previous battle is not
      finished, and automatically continue the battle.
    - Income_statistics: Now the program can analysis the finish panel screenshot to calc income by OCR. But it needs to
      be run manually.
    - Stamina_statistics: Now the program can calc the stamina cost penalty rate. But it needs to
      be run manually.