import pygame
import random
from game.constants import *
from game.obstacle import Obstacle
from game.npc import NPC

class Room:
    # Venetian/Re:Invent themed room names
    ROOM_NAMES = [
        "Venetian Ballroom A", "Venetian Ballroom B", "Venetian Ballroom C",
        "Sands Expo Hall 1", "Sands Expo Hall 2", "Sands Expo Hall 3",
        "Near the Gondolas?", "By the Fake Canal", "That Fancy Restaurant",
        "Slot Machine Area", "The Lobby (Maybe?)", "Conference Check-in",
        "Escalator Landing", "Hotel Corridor 5B", "The Food Court",
        "Somewhere in Sands", "Past the Shops", "Near Registration",
        "The Big Hallway", "Carpeted Maze Zone", "Convention Center?",
        "That Place with Lights", "By the Starbucks", "Lost & Found Area",
        "Expo Floor North", "Expo Floor South", "The Confusing Corner",
        "Near the Bathrooms", "Vendor Alley", "Swag Pickup Zone"
    ]
    
    ROOM_THEMES = ["casino", "expo", "corridor"]
    
    def __init__(self, room_id, is_goal=False):
        self.id = room_id
        self.is_goal = is_goal
        self.connections = {}  # direction: room_id
        self.obstacles = []
        self.npcs = []
        self.initialized = False
        
        # Room flavor
        self.name = random.choice(self.ROOM_NAMES) if not is_goal else "RE:INVENT KEYNOTE!"
        self.theme = random.choice(self.ROOM_THEMES)
        self.has_fake_exit = random.random() < 0.15  # 15% chance
        self.fake_exit_direction = random.choice(['north', 'south', 'east', 'west'])
        
        # Jackpot animation (for casino theme)
        self.jackpot_timer = 0
        self.show_jackpot = False
        
        # Static obstacles (slot machines, etc.)
        self.static_obstacles = []
        
        # Track last entrance used (to prevent spawning there)
        self.last_entrance = None
        self.entrance_cooldown = 0
        
    def add_connection(self, direction, room_id):
        """Add a connection to another room. Direction: 'north', 'south', 'east', 'west'"""
        self.connections[direction] = room_id
    
    def is_in_safe_zone(self, x, y):
        """Check if position is in a safe zone around exits"""
        safe_zone_radius = 95  # Increased from 80
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Check each exit
        if 'north' in self.connections:
            if abs(x - center_x) < safe_zone_radius and y < ROOM_PADDING + safe_zone_radius:
                return True
        if 'south' in self.connections:
            if abs(x - center_x) < safe_zone_radius and y > SCREEN_HEIGHT - ROOM_PADDING - safe_zone_radius:
                return True
        if 'east' in self.connections:
            if x > SCREEN_WIDTH - ROOM_PADDING - safe_zone_radius and abs(y - center_y) < safe_zone_radius:
                return True
        if 'west' in self.connections:
            if x < ROOM_PADDING + safe_zone_radius and abs(y - center_y) < safe_zone_radius:
                return True
        
        return False
    
    def initialize_contents(self, maze):
        """Initialize obstacles and NPCs for this room"""
        if self.initialized or self.is_goal:
            return
        
        self.initialized = True
        
        # Add static obstacles based on theme
        if self.theme == "casino":
            # Add 3-6 slot machines
            num_slots = random.randint(3, 6)
            for _ in range(num_slots):
                attempts = 0
                while attempts < 30:
                    x = random.randint(ROOM_PADDING + 60, SCREEN_WIDTH - ROOM_PADDING - 100)
                    y = random.randint(ROOM_PADDING + 60, SCREEN_HEIGHT - ROOM_PADDING - 100)
                    
                    # Check if too close to other slot machines or in safe zone
                    too_close = False
                    for slot in self.static_obstacles:
                        distance = ((x - slot['x'])**2 + (y - slot['y'])**2)**0.5
                        if distance < 80:
                            too_close = True
                            break
                    
                    if not self.is_in_safe_zone(x, y) and not too_close:
                        self.static_obstacles.append({
                            'type': 'slot_machine',
                            'x': x,
                            'y': y,
                            'width': 40,
                            'height': 50
                        })
                        break
                    attempts += 1
        
        # Add moving obstacles based on theme (reduced since we have through-traffic now)
        if self.theme == "casino":
            # Casino rooms have fewer people (slot machines take up space)
            num_obstacles = random.randint(1, 3)
        elif self.theme == "expo":
            # Expo halls have moderate conference crowds
            num_obstacles = random.randint(2, 4)
        else:  # corridor
            # Corridors have some wandering people
            num_obstacles = random.randint(2, 4)
        
        obstacle_types = ["conference_goer", "casino_goer", "janitor", "influencer", "phone_person"]
        
        for _ in range(num_obstacles):
            # Try to spawn obstacle outside safe zones
            attempts = 0
            while attempts < 20:
                x = random.randint(ROOM_PADDING + 50, SCREEN_WIDTH - ROOM_PADDING - 80)
                y = random.randint(ROOM_PADDING + 50, SCREEN_HEIGHT - ROOM_PADDING - 80)
                if not self.is_in_safe_zone(x, y):
                    break
                attempts += 1
            
            obstacle_type = random.choice(obstacle_types)
            obstacle = Obstacle(x, y, obstacle_type)
            obstacle.room = self  # Give obstacle reference to room for safe zone checking
            self.obstacles.append(obstacle)
        
        # Add NPCs based on theme
        if self.theme == "expo":
            # Re:Invent expo halls have more helpful staff (0-4 NPCs)
            max_npcs = 4
        else:
            # Other rooms have fewer NPCs (0-2)
            max_npcs = 2
        
        for _ in range(max_npcs):
            if random.random() < 0.6:  # Same 60% spawn rate
                attempts = 0
                while attempts < 20:
                    x = random.randint(ROOM_PADDING + 100, SCREEN_WIDTH - ROOM_PADDING - 100)
                    y = random.randint(ROOM_PADDING + 100, SCREEN_HEIGHT - ROOM_PADDING - 100)
                    
                    # Check safe zone and distance from other NPCs
                    too_close = False
                    for existing_npc in self.npcs:
                        distance = ((x - existing_npc.x)**2 + (y - existing_npc.y)**2)**0.5
                        if distance < 80:  # Minimum distance between NPCs
                            too_close = True
                            break
                    
                    if not self.is_in_safe_zone(x, y) and not too_close:
                        break
                    attempts += 1
                
                self.npcs.append(NPC(x, y, self.id, maze))
    
    def update(self, player_rect):
        """Update room contents"""
        for obstacle in self.obstacles:
            obstacle.update()
        
        # Remove obstacles that reached their exit
        self.obstacles = [obs for obs in self.obstacles if not getattr(obs, 'reached_exit', False)]
        
        # Update entrance cooldown
        if self.entrance_cooldown > 0:
            self.entrance_cooldown -= 1
        
        # Cap total obstacles at 10
        max_obstacles = 10
        
        # Spawn new through-traffic obstacles if room has multiple exits and not too crowded
        if len(self.connections) >= 2 and len(self.obstacles) < max_obstacles and random.random() < 0.015:  # 1.5% chance per frame
            self.spawn_through_traffic_obstacle()
        
        for npc in self.npcs:
            npc.update()
    
    def check_collisions(self, player_rect):
        """Check if player collides with any moving obstacles"""
        for obstacle in self.obstacles:
            if player_rect.colliderect(obstacle.get_rect()):
                return True
        return False
    
    def check_static_collision(self, player_rect):
        """Check if player collides with static obstacles (returns True to block movement)"""
        for static_obj in self.static_obstacles:
            static_rect = pygame.Rect(static_obj['x'], static_obj['y'], 
                                     static_obj['width'], static_obj['height'])
            if player_rect.colliderect(static_rect):
                return True
        return False
    
    def check_npc_interaction(self, player_rect):
        """Check if player can interact with any NPC"""
        for npc in self.npcs:
            if npc.check_interaction(player_rect):
                return npc
        return None
    
    def draw(self, screen):
        # Draw room background
        screen.fill(BLACK_900)
        
        # Draw casino-style carpet pattern
        tile_size = 40
        for y in range(ROOM_PADDING, SCREEN_HEIGHT - ROOM_PADDING, tile_size):
            for x in range(ROOM_PADDING, SCREEN_WIDTH - ROOM_PADDING, tile_size):
                # Checkerboard pattern
                if (x // tile_size + y // tile_size) % 2 == 0:
                    color = PREY_750
                else:
                    color = (35, 35, 40)
                pygame.draw.rect(screen, color, (x, y, tile_size, tile_size))
                # Add subtle border
                pygame.draw.rect(screen, PREY_700, (x, y, tile_size, tile_size), 1)
        
        # Draw decorative border
        border_width = 5
        pygame.draw.rect(screen, PREY_700,
                        (ROOM_PADDING, ROOM_PADDING,
                         SCREEN_WIDTH - 2*ROOM_PADDING,
                         SCREEN_HEIGHT - 2*ROOM_PADDING), border_width)
        
        # Draw exits as paths with glow
        exit_color = PREY_700
        if self.is_goal:
            exit_color = PURPLE_500
            # Draw goal room with pulsing effect
            import math
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 30
            glow_color = tuple(min(c + int(pulse), 255) for c in PURPLE_500)
            
            font = pygame.font.Font(None, 64)
            text = font.render("RE:INVENT ROOM!", True, glow_color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            
            # Draw glow background
            glow_surface = pygame.Surface((text_rect.width + 40, text_rect.height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*PURPLE_500, 100), glow_surface.get_rect(), border_radius=10)
            screen.blit(glow_surface, (text_rect.x - 20, text_rect.y - 10))
            
            screen.blit(text, text_rect)
        
        # Draw paths to exits with gradient
        if 'north' in self.connections:
            for i in range(ROOM_PADDING):
                alpha = int(255 * (1 - i / ROOM_PADDING))
                color = (*exit_color[:3], alpha) if len(exit_color) == 4 else exit_color
                pygame.draw.rect(screen, color,
                               (SCREEN_WIDTH//2 - EXIT_SIZE//2, i, EXIT_SIZE, 2))
        if 'south' in self.connections:
            for i in range(ROOM_PADDING):
                alpha = int(255 * (1 - i / ROOM_PADDING))
                color = (*exit_color[:3], alpha) if len(exit_color) == 4 else exit_color
                pygame.draw.rect(screen, color,
                               (SCREEN_WIDTH//2 - EXIT_SIZE//2, SCREEN_HEIGHT - ROOM_PADDING + i, EXIT_SIZE, 2))
        if 'east' in self.connections:
            for i in range(ROOM_PADDING):
                alpha = int(255 * (1 - i / ROOM_PADDING))
                color = (*exit_color[:3], alpha) if len(exit_color) == 4 else exit_color
                pygame.draw.rect(screen, color,
                               (SCREEN_WIDTH - ROOM_PADDING + i, SCREEN_HEIGHT//2 - EXIT_SIZE//2, 2, EXIT_SIZE))
        if 'west' in self.connections:
            for i in range(ROOM_PADDING):
                alpha = int(255 * (1 - i / ROOM_PADDING))
                color = (*exit_color[:3], alpha) if len(exit_color) == 4 else exit_color
                pygame.draw.rect(screen, color,
                               (i, SCREEN_HEIGHT//2 - EXIT_SIZE//2, 2, EXIT_SIZE))
        
        # Draw static obstacles first (behind moving ones)
        for static_obj in self.static_obstacles:
            self.draw_static_obstacle(screen, static_obj)
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(screen)
        
        # Draw NPCs
        for npc in self.npcs:
            npc.draw(screen)
        
        # Draw room name with styled background
        font = pygame.font.Font(None, 22)
        text = font.render(self.name, True, WHITE)
        bg_rect = pygame.Rect(5, 5, text.get_width() + 10, text.get_height() + 10)
        pygame.draw.rect(screen, PREY_750, bg_rect, border_radius=5)
        pygame.draw.rect(screen, PURPLE_500, bg_rect, 2, border_radius=5)
        screen.blit(text, (10, 10))
        
        # Draw fake exit if present
        if self.has_fake_exit and self.fake_exit_direction not in self.connections:
            self.draw_fake_exit(screen)
        
        # Draw theme-specific decorations
        self.draw_theme_decorations(screen)
    
    def draw_fake_exit(self, screen):
        """Draw a fake exit that looks real but isn't"""
        fake_color = (80, 80, 85)  # Slightly different color
        direction = self.fake_exit_direction
        
        if direction == 'north':
            for i in range(ROOM_PADDING):
                pygame.draw.rect(screen, fake_color,
                               (SCREEN_WIDTH//2 - EXIT_SIZE//2, i, EXIT_SIZE, 2))
        elif direction == 'south':
            for i in range(ROOM_PADDING):
                pygame.draw.rect(screen, fake_color,
                               (SCREEN_WIDTH//2 - EXIT_SIZE//2, SCREEN_HEIGHT - ROOM_PADDING + i, EXIT_SIZE, 2))
        elif direction == 'east':
            for i in range(ROOM_PADDING):
                pygame.draw.rect(screen, fake_color,
                               (SCREEN_WIDTH - ROOM_PADDING + i, SCREEN_HEIGHT//2 - EXIT_SIZE//2, 2, EXIT_SIZE))
        elif direction == 'west':
            for i in range(ROOM_PADDING):
                pygame.draw.rect(screen, fake_color,
                               (i, SCREEN_HEIGHT//2 - EXIT_SIZE//2, 2, EXIT_SIZE))
    
    def draw_static_obstacle(self, screen, obj):
        """Draw static obstacles like slot machines"""
        if obj['type'] == 'slot_machine':
            x, y, w, h = obj['x'], obj['y'], obj['width'], obj['height']
            
            # Shadow
            pygame.draw.rect(screen, (0, 0, 0), (x + 3, y + 3, w, h))
            
            # Main body (red/gold slot machine)
            pygame.draw.rect(screen, (180, 30, 30), (x, y, w, h))
            
            # Screen area
            screen_rect = pygame.Rect(x + 5, y + 8, w - 10, h // 3)
            pygame.draw.rect(screen, (20, 20, 40), screen_rect)
            pygame.draw.rect(screen, (100, 100, 150), screen_rect, 2)
            
            # Slot symbols (777)
            font = pygame.font.Font(None, 18)
            symbols = font.render("777", True, (255, 215, 0))
            screen.blit(symbols, (x + 8, y + 12))
            
            # Coin slot
            pygame.draw.rect(screen, (50, 50, 50), (x + w//2 - 8, y + h//2, 16, 4))
            
            # Handle/lever on side
            pygame.draw.rect(screen, (100, 100, 100), (x + w - 5, y + h//3, 4, h//3))
            pygame.draw.circle(screen, (150, 150, 150), (x + w - 3, y + h//3), 4)
            
            # Highlight
            pygame.draw.rect(screen, (220, 80, 80), (x, y, w, h // 4))
            
            # Border
            pygame.draw.rect(screen, (255, 215, 0), (x, y, w, h), 2)
    
    def draw_theme_decorations(self, screen):
        """Draw theme-specific visual elements"""
        if self.theme == "casino":
            # Slot machine text in corners
            font = pygame.font.Font(None, 48)
            text = font.render("SLOTS", True, (255, 200, 0))
            screen.blit(text, (ROOM_PADDING + 20, ROOM_PADDING + 20))
            
            # Controlled "JACKPOT" animation (accessibility-friendly)
            if not self.show_jackpot and random.random() < 0.002:  # Much less frequent
                self.show_jackpot = True
                self.jackpot_timer = 180  # Show for 3 seconds
            
            if self.show_jackpot:
                self.jackpot_timer -= 1
                if self.jackpot_timer <= 0:
                    self.show_jackpot = False
                
                # Gentle fade instead of harsh flash
                alpha = min(255, self.jackpot_timer * 3) if self.jackpot_timer < 60 else 255
                
                jackpot_font = pygame.font.Font(None, 64)
                # Use softer, more accessible color (orange instead of bright yellow)
                jackpot_text = jackpot_font.render("JACKPOT!", True, (255, 165, 0))
                jackpot_rect = jackpot_text.get_rect()
                jackpot_rect.topleft = (SCREEN_WIDTH - 250, ROOM_PADDING + 20)
                
                # Draw with background for better contrast
                bg_rect = jackpot_rect.inflate(20, 10)
                pygame.draw.rect(screen, (50, 50, 50), bg_rect, border_radius=8)
                screen.blit(jackpot_text, jackpot_rect)
        
        elif self.theme == "expo":
            # Conference banners
            pygame.draw.rect(screen, PURPLE_500, 
                           (SCREEN_WIDTH//2 - 120, ROOM_PADDING + 10, 240, 40))
            font = pygame.font.Font(None, 28)
            text = font.render("AWS RE:INVENT 2024", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH//2 - 110, ROOM_PADDING + 20))
        
        elif self.theme == "corridor":
            # Hotel corridor signs
            font = pygame.font.Font(None, 24)
            text = font.render("← Rooms 500-599", True, PREY_300)
            screen.blit(text, (ROOM_PADDING + 10, SCREEN_HEIGHT - ROOM_PADDING - 35))
    
    def spawn_through_traffic_obstacle(self):
        """Spawn an obstacle that walks from one exit to another"""
        if len(self.connections) < 2:
            return
        
        # Pick random entrance and exit, avoiding the last entrance used by player
        directions = list(self.connections.keys())
        
        # Filter out the last entrance if cooldown is active
        if self.entrance_cooldown > 0 and self.last_entrance in directions:
            available_starts = [d for d in directions if d != self.last_entrance]
            if not available_starts:
                return
            start_dir = random.choice(available_starts)
        else:
            start_dir = random.choice(directions)
        
        end_dir = random.choice([d for d in directions if d != start_dir])
        
        # Create obstacle
        obstacle_types = ["conference_goer", "casino_goer", "janitor", "phone_person"]
        obstacle_type = random.choice(obstacle_types)
        
        obstacle = Obstacle(0, 0, obstacle_type)
        obstacle.room = self
        obstacle.set_through_traffic(start_dir, end_dir)
        
        self.obstacles.append(obstacle)
    
    def check_exit(self, player_rect):
        """Check if player is at an exit and return the direction"""
        px, py = player_rect.centerx, player_rect.centery
        
        if 'north' in self.connections and py < ROOM_PADDING:
            return 'north'
        if 'south' in self.connections and py > SCREEN_HEIGHT - ROOM_PADDING:
            return 'south'
        if 'east' in self.connections and px > SCREEN_WIDTH - ROOM_PADDING:
            return 'east'
        if 'west' in self.connections and px < ROOM_PADDING:
            return 'west'
        
        return None
