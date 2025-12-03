import pygame
import random
import math
from game.constants import *

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 30
        self.max_life = 30
        self.color = color
        self.size = random.randint(3, 6)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Gravity
        self.life -= 1
    
    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        size = int(self.size * (self.life / self.max_life))
        if size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)
    
    def is_dead(self):
        return self.life <= 0

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def emit(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))
    
    def update(self):
        self.particles = [p for p in self.particles if not p.is_dead()]
        for particle in self.particles:
            particle.update()
    
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)
