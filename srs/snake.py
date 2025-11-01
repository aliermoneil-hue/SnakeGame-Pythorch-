import pygame
import const
import numpy as np
from sound import Sounds

class Snake:
    def __init__(self, sound=None):
        self.sd = sound if sound else Sounds()  # Use passed sound or create new
        self.x = 10
        self.y = 10
        self.pos = (self.x, self.y)
        self.direction = 'RIGHT'
        self.SNAKE_SPEED = 1
        self.dead = False
        self.body = [(9, 10)]
        self.bodycount = 1
        self.frame_iteration = 0

    def draw(self, surface):
        # Draw head
        head_rect = pygame.Rect(self.x * const.GRID_AND_OBJ_SIZE, self.y * const.GRID_AND_OBJ_SIZE,
                                const.GRID_AND_OBJ_SIZE, const.GRID_AND_OBJ_SIZE)
        pygame.draw.rect(surface, const.Light_Blue, head_rect)
        
        # Draw body
        for segment in self.body:
            seg_rect = pygame.Rect(segment[0] * const.GRID_AND_OBJ_SIZE, segment[1] * const.GRID_AND_OBJ_SIZE,
                                   const.GRID_AND_OBJ_SIZE, const.GRID_AND_OBJ_SIZE)
            pygame.draw.rect(surface, (255, 255, 255), seg_rect)

    def move(self, action):
        # Action Guide: Straight[1, 0, 0] Right [0, 1, 0] Left [0, 0, 1]
        self.frame_iteration += 1
        
        clock_wise = ['RIGHT', 'DOWN', 'LEFT', 'UP']
        idx = clock_wise.index(self.direction)

        if self.bodycount > 0:
            self.body.insert(0, self.pos)
            if len(self.body) > self.bodycount:
                self.body.pop()

        # Determine new direction based on action
        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]
        elif np.array_equal(action, [0, 1, 0]):
            new_idx = (idx + 1) % 4
            new_dir = clock_wise[new_idx]
        elif np.array_equal(action, [0, 0, 1]):
            new_idx = (idx - 1) % 4
            new_dir = clock_wise[new_idx]
        else:
            new_dir = self.direction

        self.direction = new_dir

        # Move head according to direction
        if self.direction == 'RIGHT':
            self.x += self.SNAKE_SPEED
        elif self.direction == 'LEFT':
            self.x -= self.SNAKE_SPEED
        elif self.direction == 'UP':
            self.y -= self.SNAKE_SPEED
        elif self.direction == 'DOWN':
            self.y += self.SNAKE_SPEED

        self.pos = (self.x, self.y)

    def food_eated(self, food):
        if self.pos in food.positions:
            food.positions.remove(self.pos)
            const.score += 1
            self.bodycount += 1
            self.sd.sfx_eat()
            return True
        return False

    def is_dead(self, pt=None):
        if pt is None:
            pt = self.pos
        
        if pt in self.body:
            return True
        
        if pt[0] < 0 or pt[0] >= const.WIDTH // const.GRID_AND_OBJ_SIZE:
            return True
        if pt[1] < 0 or pt[1] >= const.HEIGHT // const.GRID_AND_OBJ_SIZE:
            return True
        
        return False

    def died(self, food):
        if self.dead:
            self.x = 10
            self.y = 10
            food.spawn_new()
            const.score = 0
            self.bodycount = 1
            self.body = [(9, 10)]
            self.dead = False
