import pygame
import random
from const import *

pygame.init()

class Food:
    def __init__(self):
        self.number = FOODS
        self.positions = []
        self.spawn_new()

    def spawn_new(self, snake=None):
        """Spawn new food, avoiding snake body if provided"""
        self.positions = []
        
        # Get snake occupied positions
        occupied = []
        if snake:
            occupied = [snake.pos] + snake.body
        
        max_attempts = 100  # Prevent infinite loop
        attempts = 0
        
        while len(self.positions) < self.number and attempts < max_attempts:
            x = random.randint(0, WIDTH // GRID_AND_OBJ_SIZE - 1)
            y = random.randint(0, HEIGHT // GRID_AND_OBJ_SIZE - 1)
            pos = (x, y)
            
            # Check if position is not in snake and not already in food positions
            if pos not in self.positions and pos not in occupied:
                self.positions.append(pos)
            
            attempts += 1

    def draw(self, surface):
        for pos in self.positions:
            center_x = pos[0] * GRID_AND_OBJ_SIZE + GRID_AND_OBJ_SIZE // 2
            center_y = pos[1] * GRID_AND_OBJ_SIZE + GRID_AND_OBJ_SIZE // 2
            radius = GRID_AND_OBJ_SIZE // 2
            pygame.draw.circle(surface, Peachy_Red, (center_x, center_y), radius)

    def can_spawn(self, snake=None):
        """Respawn food if needed, avoiding snake body"""
        occupied = []
        if snake:
            occupied = [snake.pos] + snake.body
        
        max_attempts = 100
        attempts = 0
        
        while len(self.positions) < self.number and attempts < max_attempts:
            x = random.randint(0, WIDTH // GRID_AND_OBJ_SIZE - 1)
            y = random.randint(0, HEIGHT // GRID_AND_OBJ_SIZE - 1)
            pos = (x, y)
            
            if pos not in self.positions and pos not in occupied:
                self.positions.append(pos)
            
            attempts += 1
