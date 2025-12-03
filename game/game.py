import pygame
import random
from game.constants import *
from game.player import Player
from game.maze import Maze
from game.particles import ParticleSystem

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Re:Invent Maze - Find the Conference Room!")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize game objects
        self.maze = Maze(30)
        self.current_room_id = self.maze.start_room_id
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.particles = ParticleSystem()
        
        # Screen shake
        self.shake_amount = 0
        self.shake_duration = 0
        
        # Transition effect
        self.transitioning = False
        self.transition_alpha = 0
        self.transition_direction = 0
        
        # Invincibility frames
        self.invincibility_frames = 0
        
        # Game stats
        self.steps_taken = 0
        self.rooms_visited = set([self.current_room_id])
        self.time_elapsed = 0
        
        self.won = False
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r and self.won:
                    self.reset_game()
    
    def update(self):
        # Update particles
        self.particles.update()
        
        # Update screen shake
        if self.shake_duration > 0:
            self.shake_duration -= 1
            if self.shake_duration == 0:
                self.shake_amount = 0
        
        # Update transition
        if self.transitioning:
            self.transition_alpha += 15
            if self.transition_alpha >= 255:
                self.transitioning = False
                self.transition_alpha = 0
        
        # Update invincibility
        if self.invincibility_frames > 0:
            self.invincibility_frames -= 1
        
        if self.won:
            return
        
        # Update game stats
        self.time_elapsed += 1
        
        # Handle player movement
        keys = pygame.key.get_pressed()
        dx = keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]
        dy = keys[pygame.K_DOWN] - keys[pygame.K_UP]
        
        # Alternative WASD controls
        dx += keys[pygame.K_d] - keys[pygame.K_a]
        dy += keys[pygame.K_s] - keys[pygame.K_w]
        
        current_room = self.maze.get_room(self.current_room_id)
        
        # Initialize room contents if not done
        if not current_room.initialized:
            current_room.initialize_contents(self.maze)
        
        self.player.move(dx, dy, current_room)
        
        # Update room (obstacles, NPCs)
        current_room.update(self.player.get_rect())
        
        # Check for collisions with obstacles (only if not invincible)
        if self.invincibility_frames == 0 and current_room.check_collisions(self.player.get_rect()):
            self.on_collision()
            return
        
        # Check for NPC interaction (E key)
        if keys[pygame.K_e]:
            npc = current_room.check_npc_interaction(self.player.get_rect())
            if npc:
                npc.interact()
        
        # Check for room transitions
        exit_direction = current_room.check_exit(self.player.get_rect())
        if exit_direction:
            next_room_id = current_room.connections[exit_direction]
            self.transition_room(next_room_id, exit_direction)
    
    def transition_room(self, next_room_id, from_direction):
        """Move player to next room"""
        self.current_room_id = next_room_id
        self.rooms_visited.add(next_room_id)
        self.steps_taken += 1
        
        # Set entrance cooldown to prevent spawning at this entrance
        opposite_dir = {'north': 'south', 'south': 'north', 'east': 'west', 'west': 'east'}
        current_room = self.maze.get_room(next_room_id)
        current_room.last_entrance = opposite_dir[from_direction]
        current_room.entrance_cooldown = 180  # 3 seconds
        
        # Position player at opposite entrance
        if from_direction == 'north':
            self.player.y = SCREEN_HEIGHT - ROOM_PADDING - self.player.height - 10
        elif from_direction == 'south':
            self.player.y = ROOM_PADDING + 10
        elif from_direction == 'east':
            self.player.x = ROOM_PADDING + 10
        elif from_direction == 'west':
            self.player.x = SCREEN_WIDTH - ROOM_PADDING - self.player.width - 10
        
        # Give brief invincibility after entering
        self.invincibility_frames = 60  # 1 second
        
        # Check if reached goal
        if self.current_room_id == self.maze.goal_room_id:
            self.won = True
    
    def on_collision(self):
        """Handle collision with obstacle"""
        # Screen shake
        self.shake_amount = 10
        self.shake_duration = 20
        
        # Particle explosion (purple sparkles - teleport effect!)
        player_rect = self.player.get_rect()
        self.particles.emit(player_rect.centerx, player_rect.centery, PURPLE_500, 20)
        
        # Reset to start
        self.reset_to_start()
    
    def reset_to_start(self):
        """Reset player to starting room after collision"""
        self.current_room_id = self.maze.start_room_id
        self.player.x = SCREEN_WIDTH // 2
        self.player.y = SCREEN_HEIGHT // 2
        self.transitioning = True
        self.transition_alpha = 0
        self.invincibility_frames = 120  # 2 seconds of invincibility after respawn
    
    def draw(self):
        # Apply screen shake
        shake_x = random.randint(-self.shake_amount, self.shake_amount) if self.shake_amount > 0 else 0
        shake_y = random.randint(-self.shake_amount, self.shake_amount) if self.shake_amount > 0 else 0
        
        # Create a surface for the game content
        game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        current_room = self.maze.get_room(self.current_room_id)
        current_room.draw(game_surface)
        
        # Draw player with flashing effect if invincible
        if self.invincibility_frames > 0 and (self.invincibility_frames // 10) % 2 == 0:
            # Flash by skipping draw every other 10 frames
            pass
        else:
            self.player.draw(game_surface)
        
        # Draw particles
        self.particles.draw(game_surface)
        
        # Draw UI
        self.draw_ui(game_surface)
        
        # Blit game surface with shake
        self.screen.fill(BLACK_900)
        self.screen.blit(game_surface, (shake_x, shake_y))
        
        # Draw transition overlay
        if self.transitioning:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(self.transition_alpha)
            overlay.fill(PURPLE_500)
            self.screen.blit(overlay, (0, 0))
        
        if self.won:
            self.draw_win_screen()
        
        pygame.display.flip()
    
    def draw_ui(self, surface):
        """Draw game UI elements"""
        # Instructions (bottom left)
        font_small = pygame.font.Font(None, 20)
        text = font_small.render("Press E near NPCs to talk", True, PREY_300)
        bg_rect = pygame.Rect(5, SCREEN_HEIGHT - 30, text.get_width() + 10, text.get_height() + 8)
        pygame.draw.rect(surface, PREY_750, bg_rect, border_radius=5)
        surface.blit(text, (10, SCREEN_HEIGHT - 27))
        
        # Stats panel (bottom right)
        stats_width = 200
        stats_x = SCREEN_WIDTH - stats_width - 10
        stats_y = SCREEN_HEIGHT - 95
        
        # Time
        minutes = self.time_elapsed // (60 * 60)
        seconds = (self.time_elapsed // 60) % 60
        time_text = f"Time: {minutes}:{seconds:02d}"
        
        # Steps
        steps_text = f"Rooms: {self.steps_taken}"
        
        # Unique rooms
        unique_text = f"Explored: {len(self.rooms_visited)}"
        
        font = pygame.font.Font(None, 22)
        
        # Draw stats background
        stats_height = 85
        pygame.draw.rect(surface, PREY_750, (stats_x, stats_y, stats_width, stats_height), border_radius=5)
        pygame.draw.rect(surface, PURPLE_500, (stats_x, stats_y, stats_width, stats_height), 2, border_radius=5)
        
        # Draw stats text
        y_offset = stats_y + 12
        for text_str in [time_text, steps_text, unique_text]:
            text_surf = font.render(text_str, True, WHITE)
            surface.blit(text_surf, (stats_x + 10, y_offset))
            y_offset += 25
    
    def draw_win_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(BLACK_900)
        self.screen.blit(overlay, (0, 0))
        
        # Pulsing effect
        import math
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003)) * 20
        
        # Draw celebration particles
        if random.random() < 0.3:
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            self.particles.emit(x, y, PURPLE_500, 3)
        
        self.particles.draw(self.screen)
        
        # Main text with glow
        font = pygame.font.Font(None, 72)
        glow_color = tuple(min(c + int(pulse), 255) for c in PURPLE_500)
        text = font.render("YOU FOUND RE:INVENT!", True, glow_color)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60))
        
        # Draw glow
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_text = font.render("YOU FOUND RE:INVENT!", True, (*PURPLE_500, 100))
            self.screen.blit(glow_text, (text_rect.x + offset[0], text_rect.y + offset[1]))
        
        self.screen.blit(text, text_rect)
        
        # Stats
        minutes = self.time_elapsed // (60 * 60)
        seconds = (self.time_elapsed // 60) % 60
        font_stats = pygame.font.Font(None, 28)
        stats_text = font_stats.render(f"Time: {minutes}:{seconds:02d} | Rooms: {self.steps_taken} | Explored: {len(self.rooms_visited)}", True, WHITE)
        stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10))
        self.screen.blit(stats_text, stats_rect)
        
        # Subtitle
        font_small = pygame.font.Font(None, 32)
        text2 = font_small.render("Press R to restart or ESC to quit", True, WHITE)
        text2_rect = text2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60))
        
        bg_rect = text2_rect.inflate(20, 10)
        pygame.draw.rect(self.screen, PREY_750, bg_rect, border_radius=10)
        pygame.draw.rect(self.screen, PURPLE_500, bg_rect, 2, border_radius=10)
        
        self.screen.blit(text2, text2_rect)
    
    def reset_game(self):
        self.maze = Maze(30)
        self.current_room_id = self.maze.start_room_id
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.particles = ParticleSystem()
        self.shake_amount = 0
        self.shake_duration = 0
        self.transitioning = False
        self.transition_alpha = 0
        self.invincibility_frames = 120  # 2 seconds of invincibility on new game
        self.steps_taken = 0
        self.rooms_visited = set([self.current_room_id])
        self.time_elapsed = 0
        self.won = False
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
