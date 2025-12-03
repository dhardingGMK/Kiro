import pygame
import random
from game.constants import *

class NPC:
    def __init__(self, x, y, room_id, maze):
        self.x = x
        self.y = y
        self.width = 35
        self.height = 35
        self.color = PURPLE_500
        self.room_id = room_id
        
        # Generate dialogue based on maze structure
        self.dialogue = self.generate_dialogue(maze)
        self.is_lying = random.random() < 0.4  # 40% chance NPC lies
        
        self.showing_dialogue = False
        self.dialogue_timer = 0
    
    def generate_dialogue(self, maze):
        """Generate helpful (or misleading) directions"""
        current_room = maze.get_room(self.room_id)
        goal_pos = maze.room_positions[maze.goal_room_id]
        current_pos = maze.room_positions[self.room_id]
        
        # Calculate general direction to goal
        dx = goal_pos[0] - current_pos[0]
        dy = goal_pos[1] - current_pos[1]
        
        directions = []
        if abs(dx) > abs(dy):
            if dx > 0:
                directions.append("east")
            else:
                directions.append("west")
        else:
            if dy > 0:
                directions.append("south")
            else:
                directions.append("north")
        
        # Generate dialogue
        phrases = [
            f"The Re:Invent room is to the {directions[0]}!",
            f"Head {directions[0]} to find the conference.",
            f"Try going {directions[0]}, friend!",
            f"I think it's {directions[0]} from here.",
        ]
        
        return random.choice(phrases)
    
    def get_lying_dialogue(self):
        """Return opposite or random wrong direction"""
        opposite_dirs = {
            "north": "south",
            "south": "north", 
            "east": "west",
            "west": "east"
        }
        
        for direction in ["north", "south", "east", "west"]:
            if direction in self.dialogue:
                wrong_dir = opposite_dirs[direction]
                return self.dialogue.replace(direction, wrong_dir)
        
        return self.dialogue
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def check_interaction(self, player_rect):
        """Check if player is close enough to interact"""
        distance = math.sqrt((self.x - player_rect.x)**2 + (self.y - player_rect.y)**2)
        return distance < 60
    
    def interact(self):
        """Show dialogue"""
        self.showing_dialogue = True
        self.dialogue_timer = 180  # Show for 3 seconds at 60 FPS
    
    def update(self):
        if self.showing_dialogue:
            self.dialogue_timer -= 1
            if self.dialogue_timer <= 0:
                self.showing_dialogue = False
    
    def draw(self, screen):
        center_x = int(self.x + self.width//2)
        center_y = int(self.y + self.height//2)
        
        # Draw shadow
        pygame.draw.circle(screen, (0, 0, 0), (center_x + 2, center_y + 2), self.width//2)
        
        # Draw NPC as a helpful person
        # Body (purple shirt - Re:Invent staff)
        pygame.draw.circle(screen, self.color, (center_x, center_y), self.width//2)
        
        # Head
        head_color = (220, 180, 140)
        pygame.draw.circle(screen, head_color, (center_x, center_y - 8), self.width//3)
        
        # Staff badge
        badge_rect = pygame.Rect(center_x - 8, center_y + 2, 16, 10)
        pygame.draw.rect(screen, WHITE, badge_rect)
        pygame.draw.rect(screen, self.color, badge_rect, 1)
        
        # Draw "STAFF" text on badge
        font_tiny = pygame.font.Font(None, 12)
        staff_text = font_tiny.render("STAFF", True, self.color)
        screen.blit(staff_text, (center_x - 10, center_y + 4))
        
        # Eyes
        pygame.draw.circle(screen, (0, 0, 0), (center_x - 4, center_y - 9), 2)
        pygame.draw.circle(screen, (0, 0, 0), (center_x + 4, center_y - 9), 2)
        
        # Smile (everyone smiles - can't tell who's lying!)
        pygame.draw.arc(screen, (0, 0, 0), 
                      (center_x - 5, center_y - 3, 10, 6), 
                      0, 3.14, 2)
        
        # Draw border
        pygame.draw.circle(screen, WHITE, (center_x, center_y), self.width//2, 3)
        
        # Draw "?" indicator with glow effect when not talking
        if not self.showing_dialogue:
            # Pulsing glow
            import math
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 10
            glow_radius = self.width//2 + int(pulse)
            glow_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*self.color, 50), (glow_radius, glow_radius), glow_radius)
            screen.blit(glow_surface, (center_x - glow_radius, center_y - glow_radius))
            
            # Floating "?" above head
            font = pygame.font.Font(None, 28)
            text = font.render("?", True, WHITE)
            text_rect = text.get_rect(center=(center_x, center_y - self.width//2 - 15))
            
            # Draw background circle for "?"
            pygame.draw.circle(screen, self.color, text_rect.center, 12)
            pygame.draw.circle(screen, WHITE, text_rect.center, 12, 2)
            screen.blit(text, text_rect)
        
        # Draw dialogue if showing
        if self.showing_dialogue:
            dialogue_text = self.dialogue if not self.is_lying else self.get_lying_dialogue()
            self.draw_dialogue_box(screen, dialogue_text)
    
    def draw_dialogue_box(self, screen, text):
        """Draw dialogue box above NPC"""
        font = pygame.font.Font(None, 20)
        text_surface = font.render(text, True, WHITE)
        
        padding = 10
        box_width = text_surface.get_width() + padding * 2
        box_height = text_surface.get_height() + padding * 2
        box_x = self.x + self.width//2 - box_width//2
        box_y = self.y - box_height - 10
        
        # Keep box on screen
        box_x = max(10, min(box_x, SCREEN_WIDTH - box_width - 10))
        box_y = max(10, box_y)
        
        # Draw box
        pygame.draw.rect(screen, PREY_750, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(screen, PURPLE_500, (box_x, box_y, box_width, box_height), 2)
        
        # Draw text
        screen.blit(text_surface, (box_x + padding, box_y + padding))

import math
