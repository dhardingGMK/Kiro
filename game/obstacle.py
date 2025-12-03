import pygame
import random
import math
from game.constants import *

class Obstacle:
    """Base class for moving obstacles"""
    
    # Funny quotes for each obstacle type
    CONFERENCE_QUOTES = [
        "Did you see the keynote?",
        "Where's the swag?",
        "Is this the right room?",
        "I need more coffee...",
        "Have you tried serverless?",
        "My badge isn't working!",
        "Which session is this?",
        "Free t-shirts?!",
        "I'm so lost...",
        "Is lunch included?"
    ]
    
    CASINO_QUOTES = [
        "Feeling lucky!",
        "One more spin...",
        "Where's the buffet?",
        "I can quit anytime!",
        "Double or nothing!",
        "The house always wins?",
        "Just one more hand...",
        "I'm up $5!",
        "Viva Las Vegas!",
        "Jackpot incoming!"
    ]
    
    JANITOR_QUOTES = [
        "Watch the wet floor...",
        "Just cleaned that!",
        "Not again...",
        "Where's my mop?",
        "This place is huge!",
        "Coffee spill on 3...",
        "Almost done here...",
        "Excuse me, coming through",
        "Long shift today...",
        "Clean up on aisle 5!"
    ]
    
    INFLUENCER_QUOTES = [
        "Wait, let me get this angle",
        "This lighting is perfect!",
        "Hold on, one more selfie",
        "Is this Insta-worthy?",
        "My followers will love this",
        "Can you take my photo?",
        "Strike a pose!",
        "Content creation time!",
        "This is going viral!",
        "Tag me in this!"
    ]
    
    PHONE_PERSON_QUOTES = [
        "Yeah, I'm at the thing...",
        "Can you hear me now?",
        "Sorry, bad signal here",
        "I'll call you back",
        "Wait, what did you say?",
        "I'm so lost right now",
        "Hold on, checking my map",
        "Where are you?",
        "This place is massive!",
        "I can't find the room..."
    ]
    
    def __init__(self, x, y, obstacle_type):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.type = obstacle_type
        self.speed = 2
        
        # Movement behavior
        self.direction = random.uniform(0, 2 * math.pi)
        self.change_direction_timer = 0
        self.change_direction_interval = random.randint(60, 180)
        
        # Speech bubble
        self.speech_text = ""
        self.speech_timer = 0
        self.speech_cooldown = random.randint(10, 60)  # Start talking soon (0.2-1 second)
        
        # Through traffic flag
        self.reached_exit = False
        
        # Movement mode
        self.movement_mode = "wander"  # "wander" or "through_traffic"
        self.target_x = None
        self.target_y = None
        
        # Type-specific properties
        if obstacle_type == "conference_goer":
            self.color = (100, 150, 200)  # Blue-ish
            self.speed = 1.5
            self.label = "C"
            self.quotes = self.CONFERENCE_QUOTES
        elif obstacle_type == "casino_goer":
            self.color = (200, 50, 50)  # Red-ish
            self.speed = 2.5
            self.label = "G"
            self.quotes = self.CASINO_QUOTES
        elif obstacle_type == "janitor":
            self.color = (150, 150, 50)  # Yellow-ish
            self.speed = 1.0
            self.label = "J"
            self.quotes = self.JANITOR_QUOTES
        elif obstacle_type == "influencer":
            self.color = (255, 105, 180)  # Pink
            self.speed = 0.5  # Very slow, always stopping for photos
            self.label = "I"
            self.quotes = self.INFLUENCER_QUOTES
        elif obstacle_type == "phone_person":
            self.color = (100, 200, 100)  # Green
            self.speed = 1.2
            self.label = "P"
            self.quotes = self.PHONE_PERSON_QUOTES
    
    def set_through_traffic(self, start_direction, end_direction):
        """Set this obstacle to walk from one exit to another"""
        self.movement_mode = "through_traffic"
        
        # Position at entrance
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        if start_direction == 'north':
            self.x = center_x - self.width // 2
            self.y = ROOM_PADDING + 10
        elif start_direction == 'south':
            self.x = center_x - self.width // 2
            self.y = SCREEN_HEIGHT - ROOM_PADDING - self.height - 10
        elif start_direction == 'east':
            self.x = SCREEN_WIDTH - ROOM_PADDING - self.width - 10
            self.y = center_y - self.height // 2
        elif start_direction == 'west':
            self.x = ROOM_PADDING + 10
            self.y = center_y - self.height // 2
        
        # Set target at exit
        if end_direction == 'north':
            self.target_x = center_x - self.width // 2
            self.target_y = ROOM_PADDING - 20
        elif end_direction == 'south':
            self.target_x = center_x - self.width // 2
            self.target_y = SCREEN_HEIGHT - ROOM_PADDING + 20
        elif end_direction == 'east':
            self.target_x = SCREEN_WIDTH - ROOM_PADDING + 20
            self.target_y = center_y - self.height // 2
        elif end_direction == 'west':
            self.target_x = ROOM_PADDING - 20
            self.target_y = center_y - self.height // 2
    
    def update(self):
        """Update obstacle position"""
        if self.movement_mode == "through_traffic":
            self.update_through_traffic()
        else:
            self.update_wander()
        
        # Update speech
        if self.speech_timer > 0:
            self.speech_timer -= 1
            if self.speech_timer == 0:
                self.speech_text = ""
        else:
            self.speech_cooldown -= 1
            if self.speech_cooldown <= 0:
                # Say something!
                self.speech_text = random.choice(self.quotes)
                self.speech_timer = 180  # Show for 3 seconds
                self.speech_cooldown = random.randint(120, 240)  # 2-4 seconds between quotes
    
    def update_through_traffic(self):
        """Move toward target exit"""
        if self.target_x is None or self.target_y is None:
            return
        
        # Calculate direction to target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 5:
            # Reached exit, mark for removal
            self.reached_exit = True
            return
        
        # Move toward target
        self.x += (dx / distance) * self.speed
        self.y += (dy / distance) * self.speed
    
    def update_wander(self):
        """Update obstacle position with aimless wandering"""
        self.change_direction_timer += 1
        
        # Randomly change direction
        if self.change_direction_timer >= self.change_direction_interval:
            self.direction = random.uniform(0, 2 * math.pi)
            self.change_direction_timer = 0
            self.change_direction_interval = random.randint(60, 180)
        
        # Move in current direction
        dx = math.cos(self.direction) * self.speed
        dy = math.sin(self.direction) * self.speed
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Check if new position is in safe zone
        if hasattr(self, 'room') and self.room.is_in_safe_zone(new_x + self.width//2, new_y + self.height//2):
            # Bounce away from safe zone
            self.direction = random.uniform(0, 2 * math.pi)
            return
        
        # Bounce off walls
        if new_x < ROOM_PADDING + 10 or new_x > SCREEN_WIDTH - ROOM_PADDING - self.width - 10:
            self.direction = math.pi - self.direction
        elif new_y < ROOM_PADDING + 10 or new_y > SCREEN_HEIGHT - ROOM_PADDING - self.height - 10:
            self.direction = -self.direction
        else:
            self.x = new_x
            self.y = new_y
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def draw_conference_goer(self, screen):
        """Draw a conference attendee with badge"""
        cx, cy = int(self.x + self.width//2), int(self.y + self.height//2)
        
        # Shadow
        pygame.draw.circle(screen, (0, 0, 0), (cx + 2, cy + 2), self.width//2)
        
        # Body (suit)
        pygame.draw.circle(screen, self.color, (cx, cy), self.width//2)
        
        # Head
        head_color = (220, 180, 140)
        pygame.draw.circle(screen, head_color, (cx, cy - 5), self.width//3)
        
        # Badge
        badge_rect = pygame.Rect(cx - 6, cy + 2, 12, 8)
        pygame.draw.rect(screen, WHITE, badge_rect)
        pygame.draw.rect(screen, self.color, badge_rect, 1)
        
        # Eyes
        pygame.draw.circle(screen, (0, 0, 0), (cx - 3, cy - 6), 2)
        pygame.draw.circle(screen, (0, 0, 0), (cx + 3, cy - 6), 2)
        
        # Border
        pygame.draw.circle(screen, WHITE, (cx, cy), self.width//2, 2)
    
    def draw_casino_goer(self, screen):
        """Draw a casino patron with drink"""
        cx, cy = int(self.x + self.width//2), int(self.y + self.height//2)
        
        # Shadow
        pygame.draw.circle(screen, (0, 0, 0), (cx + 2, cy + 2), self.width//2)
        
        # Body (casual clothes)
        pygame.draw.circle(screen, self.color, (cx, cy), self.width//2)
        
        # Head
        head_color = (220, 180, 140)
        pygame.draw.circle(screen, head_color, (cx, cy - 5), self.width//3)
        
        # Drink in hand
        drink_x = cx + self.width//3
        pygame.draw.rect(screen, (255, 200, 0), (drink_x - 3, cy - 2, 6, 10))
        pygame.draw.circle(screen, (255, 200, 0), (drink_x, cy - 2), 3)
        
        # Eyes (looking at drink)
        pygame.draw.circle(screen, (0, 0, 0), (cx - 2, cy - 5), 2)
        pygame.draw.circle(screen, (0, 0, 0), (cx + 2, cy - 5), 2)
        
        # Border
        pygame.draw.circle(screen, WHITE, (cx, cy), self.width//2, 2)
    
    def draw_janitor(self, screen):
        """Draw a janitor with mop"""
        cx, cy = int(self.x + self.width//2), int(self.y + self.height//2)
        
        # Shadow
        pygame.draw.circle(screen, (0, 0, 0), (cx + 2, cy + 2), self.width//2)
        
        # Body (uniform)
        pygame.draw.circle(screen, self.color, (cx, cy), self.width//2)
        
        # Head
        head_color = (220, 180, 140)
        pygame.draw.circle(screen, head_color, (cx, cy - 5), self.width//3)
        
        # Mop
        mop_x = cx - self.width//3
        pygame.draw.line(screen, (139, 69, 19), (mop_x, cy - 8), (mop_x, cy + 8), 2)
        pygame.draw.rect(screen, (180, 180, 180), (mop_x - 4, cy + 6, 8, 4))
        
        # Eyes
        pygame.draw.circle(screen, (0, 0, 0), (cx - 3, cy - 6), 2)
        pygame.draw.circle(screen, (0, 0, 0), (cx + 3, cy - 6), 2)
        
        # Border
        pygame.draw.circle(screen, WHITE, (cx, cy), self.width//2, 2)
    
    def draw_influencer(self, screen):
        """Draw an influencer taking selfies"""
        cx, cy = int(self.x + self.width//2), int(self.y + self.height//2)
        
        # Shadow
        pygame.draw.circle(screen, (0, 0, 0), (cx + 2, cy + 2), self.width//2)
        
        # Body
        pygame.draw.circle(screen, self.color, (cx, cy), self.width//2)
        
        # Head
        head_color = (220, 180, 140)
        pygame.draw.circle(screen, head_color, (cx, cy - 5), self.width//3)
        
        # Phone (selfie stick)
        phone_x = cx + self.width//2 + 5
        pygame.draw.rect(screen, (50, 50, 50), (phone_x - 2, cy - 8, 4, 8))
        pygame.draw.rect(screen, (200, 200, 255), (phone_x - 3, cy - 8, 6, 8))
        
        # Eyes
        pygame.draw.circle(screen, (0, 0, 0), (cx - 3, cy - 6), 2)
        pygame.draw.circle(screen, (0, 0, 0), (cx + 3, cy - 6), 2)
        
        # Border
        pygame.draw.circle(screen, WHITE, (cx, cy), self.width//2, 2)
    
    def draw_phone_person(self, screen):
        """Draw someone on their phone not paying attention"""
        cx, cy = int(self.x + self.width//2), int(self.y + self.height//2)
        
        # Shadow
        pygame.draw.circle(screen, (0, 0, 0), (cx + 2, cy + 2), self.width//2)
        
        # Body
        pygame.draw.circle(screen, self.color, (cx, cy), self.width//2)
        
        # Head (looking down at phone)
        head_color = (220, 180, 140)
        pygame.draw.circle(screen, head_color, (cx, cy - 3), self.width//3)
        
        # Phone in hand
        pygame.draw.rect(screen, (50, 50, 50), (cx - 4, cy + 3, 8, 12))
        pygame.draw.rect(screen, (150, 200, 255), (cx - 3, cy + 4, 6, 10))
        
        # Eyes (looking down)
        pygame.draw.circle(screen, (0, 0, 0), (cx - 3, cy - 2), 1)
        pygame.draw.circle(screen, (0, 0, 0), (cx + 3, cy - 2), 1)
        
        # Border
        pygame.draw.circle(screen, WHITE, (cx, cy), self.width//2, 2)
    
    def draw(self, screen):
        if self.type == "conference_goer":
            self.draw_conference_goer(screen)
        elif self.type == "casino_goer":
            self.draw_casino_goer(screen)
        elif self.type == "janitor":
            self.draw_janitor(screen)
        elif self.type == "influencer":
            self.draw_influencer(screen)
        elif self.type == "phone_person":
            self.draw_phone_person(screen)
        
        # Draw speech bubble if talking
        if self.speech_text:
            self.draw_speech_bubble(screen)
    
    def draw_speech_bubble(self, screen):
        """Draw a speech bubble above the obstacle"""
        font = pygame.font.Font(None, 16)
        text_surface = font.render(self.speech_text, True, (0, 0, 0))
        
        padding = 6
        box_width = text_surface.get_width() + padding * 2
        box_height = text_surface.get_height() + padding * 2
        box_x = int(self.x + self.width//2 - box_width//2)
        box_y = int(self.y - box_height - 10)
        
        # Keep box on screen
        box_x = max(ROOM_PADDING + 5, min(box_x, SCREEN_WIDTH - ROOM_PADDING - box_width - 5))
        box_y = max(ROOM_PADDING + 5, box_y)
        
        # Draw bubble
        bubble_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, WHITE, bubble_rect, border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), bubble_rect, 2, border_radius=8)
        
        # Draw pointer
        pointer_points = [
            (int(self.x + self.width//2), int(self.y)),
            (box_x + box_width//2 - 5, box_y + box_height),
            (box_x + box_width//2 + 5, box_y + box_height)
        ]
        pygame.draw.polygon(screen, WHITE, pointer_points)
        pygame.draw.lines(screen, (0, 0, 0), False, pointer_points, 2)
        
        # Draw text
        screen.blit(text_surface, (box_x + padding, box_y + padding))
