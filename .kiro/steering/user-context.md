---
inclusion: always
---

# User Game Preferences - Re:Invent Maze Game

## Technology Stack
- **Language**: Python
- **Framework**: Pygame
- **Style**: Retro top-down 2D maze game

## Game Concept
A maze navigation game themed around navigating the chaos of AWS Re:Invent to find the Re:Invent room.

## Core Features
- **Rooms**: 10-15 procedurally connected rooms
- **Room Layout**: Casino-style with paths only to available exits (top/left/right/bottom based on connections)
- **Player**: Kiro logo (kiro-logo.png) as the player sprite
- **Movement**: Basic 2D top-down movement (arrow keys/WASD)
- **No gravity**: Flat 2D plane movement

## Obstacles (Moving)
Three types of aimless wandering obstacles that send player back to start on collision:
1. Conference goers
2. Casino goers  
3. Janitors

## NPCs
- Max 1 helper NPC per room (some rooms have none)
- Give directional instructions for next rooms
- Some NPCs lie - player must discern truth from misinformation

## Win Condition
- Reach the Re:Invent room
- No time limit or scoring (keep it simple)

## Visual Style
- Retro pixel art aesthetic
- Kiro brand colors (Purple-500: #790ECB, dark backgrounds)
- Casino/conference floor layout aesthetic
- Clear visual paths to room exits
