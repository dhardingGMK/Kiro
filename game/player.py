import pygame
from game.constants import *

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_SIZE
        self.height = PLAYER_SIZE
        
        # Load Kiro logo
        try:
            self.image = pygame.image.load('kiro-logo.png')
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except:
            # Fallback to purple square if image not found
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill(PURPLE_500)
    
    def move(self, dx, dy, room):
        # Try to move and check boundaries
        new_x = self.x + dx * PLAYER_SPEED
        new_y = self.y + dy * PLAYER_SPEED
        
        # Check if moving through an exit
        exit_zone_size = EXIT_SIZE
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Allow movement through exits
        can_move_x = True
        can_move_y = True
        
        # Check horizontal boundaries (but allow exits)
        if new_x < ROOM_PADDING:
            # Check if there's a west exit
            if 'west' not in room.connections or not (center_y - exit_zone_size//2 <= new_y + self.height//2 <= center_y + exit_zone_size//2):
                can_move_x = False
        elif new_x > SCREEN_WIDTH - ROOM_PADDING - self.width:
            # Check if there's an east exit
            if 'east' not in room.connections or not (center_y - exit_zone_size//2 <= new_y + self.height//2 <= center_y + exit_zone_size//2):
                can_move_x = False
        
        # Check vertical boundaries (but allow exits)
        if new_y < ROOM_PADDING:
            # Check if there's a north exit
            if 'north' not in room.connections or not (center_x - exit_zone_size//2 <= new_x + self.width//2 <= center_x + exit_zone_size//2):
                can_move_y = False
        elif new_y > SCREEN_HEIGHT - ROOM_PADDING - self.height:
            # Check if there's a south exit
            if 'south' not in room.connections or not (center_x - exit_zone_size//2 <= new_x + self.width//2 <= center_x + exit_zone_size//2):
                can_move_y = False
        
        # Check static obstacle collisions
        if can_move_x:
            test_rect = pygame.Rect(new_x, self.y, self.width, self.height)
            if room.check_static_collision(test_rect):
                can_move_x = False
        
        if can_move_y:
            test_rect = pygame.Rect(self.x, new_y, self.width, self.height)
            if room.check_static_collision(test_rect):
                can_move_y = False
        
        if can_move_x:
            self.x = new_x
        if can_move_y:
            self.y = new_y
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
