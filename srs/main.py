import pygame
import sys
import const
from const import *
from food import Food
from snake import Snake
from sound import Sounds

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.Font(None, 30)
pygame.display.set_caption('Snake Game @Kallisto')
clock = pygame.time.Clock()

class Game:
	def __init__(self, sound=None):
		self.sd = sound if sound else Sounds()
		self.sk = Snake(self.sd)
		self.fd = Food()
		self.frame_iteration = 0

	def reset_game(self):
		# Snake Reset
		self.sk.x = 10
		self.sk.y = 10
		self.sk.bodycount = 1
		self.sk.body = [(9, 10)]
		self.sk.direction = 'RIGHT'
		self.sk.dead = False
		self.sk.frame_iteration = 0
        
		# Food Reset - pass snake to avoid collision
		self.fd.spawn_new(self.sk)

		# UI Reset
		const.score = 0
		self.frame_iteration = 0

	def play_step(self, action):
		self.frame_iteration += 1
		reward = 0

		# Move snake
		old_pos = self.sk.pos
		self.sk.move(action)

		# Check if game over
		game_over = False
		if self.sk.is_dead() or self.frame_iteration > 100 * len(self.sk.body):
			game_over = True
			reward = -10
			return reward, game_over, const.score

		# Check if food eaten
		if self.sk.food_eated(self.fd):
			reward = 10
			self.fd.can_spawn(self.sk)
		else:
			# Small reward for moving closer to food
			food_x, food_y = self.fd.positions[0]
			old_dist = abs(old_pos[0] - food_x) + abs(old_pos[1] - food_y)
			new_dist = abs(self.sk.pos[0] - food_x) + abs(self.sk.pos[1] - food_y)
			
			if new_dist < old_dist:
				reward = 0.1  # Small reward for getting closer
			else:
				reward = -0.1  # Small penalty for moving away
		
		self.fd.can_spawn(self.sk)
		
		return reward, game_over, const.score