# Re:Invent Kiro Game

## Overview
This game is a satirical play on the first day confusion of navigating Re:Invent for the the first time. With all of the chaos of people trying to make their sessions mixed in with hotel staff and patrons. You may find that some of the help staff themselves get a bit confused, and may give you the wrong instructions!

## Install instructions
You will need Python installed to be able to run this game. From any terminal, navigate to the directory the game is in. From there run the following commands:
```
pip install -r requirements.txt

python main.py
```

## Purpose
The development of this game was done during the AWS Re:Invent session DVT402-R, which utilized the agentic AI IDE Kiro to fully build a game from the ground up. While given the opportunity to try some pre-cooked ideas, I elected to try my own, limit testing Kiro.
This game was entirely made using their "Vibe mode" feature in which you provide natural language and the agent makes changes to the code accordingly. You will find the steering files are extremely helpful and allow Kiro to know what to do for certain contexts, helping it switch contexts when needed.
I found that Kiro made a couple very minor mistakes here and there but overall did a very good job providing what was asked for. You DO need to provide feedback and make some directive decisions, but Kiro also came up with a lot of ideas on its own when asked.
For example, the names of rooms, NPC types, graphics, dialogue, and UI/UX were all completely created by Kiro with barely any guidance. 

## Game Controls/Objective
Navigate the halls of the Venetian with WASD, or arrow keys, pressing E on help staff to get tips, try to make it to Re:Invent!
