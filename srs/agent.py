import pygame
import sys
import const
import torch
import numpy as np
import random
from collections import deque
from const import *
from main import Game
from food import Food
from snake import Snake
from sound import Sounds
from model import QTrainer, Linear_QNet
from potter import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 20)
large_font = pygame.font.Font(None, 60)
pygame.display.set_caption('Snake AI Training')
clock = pygame.time.Clock()

class Agent:
    def __init__(self):
        self.sound = Sounds()
        self.game = Game(self.sound)
        self.food = Food()
        self.num_of_game = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        self.speed = 20
        self.paused = False  # Pause state

    def get_state(self, game):
        head = game.sk
        food_x, food_y = game.fd.positions[0]

        # Check adjacent cells
        point_l = (head.x - 1, head.y)
        point_r = (head.x + 1, head.y)
        point_u = (head.x, head.y - 1)
        point_d = (head.x, head.y + 1)

        dir_l = head.direction == 'LEFT'
        dir_r = head.direction == 'RIGHT'
        dir_u = head.direction == 'UP'
        dir_d = head.direction == 'DOWN'

        state = [
            # Danger Straight
            (dir_r and game.sk.is_dead(point_r)) or
            (dir_l and game.sk.is_dead(point_l)) or
            (dir_u and game.sk.is_dead(point_u)) or
            (dir_d and game.sk.is_dead(point_d)),

            # Danger Right
            (dir_u and game.sk.is_dead(point_r)) or
            (dir_d and game.sk.is_dead(point_l)) or
            (dir_l and game.sk.is_dead(point_u)) or
            (dir_r and game.sk.is_dead(point_d)),

            # Danger Left
            (dir_d and game.sk.is_dead(point_r)) or
            (dir_u and game.sk.is_dead(point_l)) or
            (dir_r and game.sk.is_dead(point_u)) or
            (dir_l and game.sk.is_dead(point_d)),

            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,

            # Food Location
            food_x > head.x,
            food_x < head.x,
            food_y > head.y,
            food_y < head.y
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # Exploration vs exploitation
        self.epsilon = 80 - self.num_of_game
        final_move = [0, 0, 0]
        
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

def main_train():
    plot_score = []
    plot_mean_score = []
    total_score = 0
    record = 0
    agent = Agent()

    while True:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            agent.sound.bgm(event)
            
            if event.type == pygame.KEYDOWN:
                # Speed controls
                if event.key == pygame.K_z:
                    agent.speed = 20
                    print("⚡ Speed: SLOW (20 FPS)")
                elif event.key == pygame.K_x:
                    agent.speed = 60
                    print("⚡ Speed: MEDIUM (60 FPS)")
                elif event.key == pygame.K_c:
                    agent.speed = 0
                    print("⚡ Speed: MAX (Unlimited FPS)")
                
                # Pause toggle (SPACE or P key)
                elif event.key == pygame.K_SPACE or event.key == pygame.K_p:
                    agent.paused = not agent.paused
                    if agent.paused:
                        print("⏸️  PAUSED")
                    else:
                        print("▶️  RESUMED")

        # Skip game logic if paused
        if not agent.paused:
            # Get old state
            state_old = agent.get_state(agent.game)

            # Get action
            final_move = agent.get_action(state_old)

            # Perform move and get new state
            reward, done, score = agent.game.play_step(final_move)
            state_new = agent.get_state(agent.game)

            # Train short memory
            agent.train_short_memory(state_old, final_move, reward, state_new, done)

            # Remember
            agent.remember(state_old, final_move, reward, state_new, done)

            if done:
                # Train long memory
                agent.game.reset_game()
                agent.num_of_game += 1
                agent.train_long_memory()

                if score > record:
                    record = score
                    agent.model.save()

                print(f"Game: {agent.num_of_game}, Score: {score}, Record: {record}")

                plot_score.append(score)
                total_score += score
                mean_score = total_score / agent.num_of_game
                plot_mean_score.append(mean_score)
                plot(plot_score, plot_mean_score, agent.num_of_game, record)

        # Render game (always render even when paused)
        d_green = const.Dark_Green
        l_green = const.Light_Green
        for x in range(0, WIDTH, GRID_AND_OBJ_SIZE):
            for y in range(0, HEIGHT, GRID_AND_OBJ_SIZE):
                rect = pygame.Rect(x, y, GRID_AND_OBJ_SIZE, GRID_AND_OBJ_SIZE)
                pygame.draw.rect(screen, d_green, rect)
                pygame.draw.rect(screen, l_green, rect, 1)

        agent.game.sk.draw(screen)
        agent.game.fd.draw(screen)
        
        # Display info
        score_text = font.render(f'Score: {const.score}', True, (255, 255, 255))
        game_text = font.render(f'Game: {agent.num_of_game}', True, (255, 255, 255))
        record_text = font.render(f'Record: {record}', True, (255, 255, 255))
        
        if agent.speed == 0:
            speed_text = small_font.render('Speed: MAX', True, (50, 255, 50))
        else:
            speed_text = small_font.render(f'Speed: {agent.speed} FPS', True, (255, 255, 255))
        
        controls_text = small_font.render('Z: Slow | X: Medium | C: Max | SPACE: Pause', True, (200, 200, 200))
        
        screen.blit(score_text, (10, 10))
        screen.blit(game_text, (10, 40))
        screen.blit(record_text, (10, 70))
        screen.blit(speed_text, (10, 100))
        screen.blit(controls_text, (10, HEIGHT - 30))
        
        # Show PAUSED overlay
        if agent.paused:
            # Semi-transparent overlay
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # PAUSED text
            pause_text = large_font.render('PAUSED', True, (255, 255, 0))
            pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
            screen.blit(pause_text, pause_rect)
            
            # Resume instruction
            resume_text = small_font.render('Press SPACE or P to resume', True, (255, 255, 255))
            resume_rect = resume_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            screen.blit(resume_text, resume_rect)
        
        pygame.display.flip()
        
        # Apply speed limit (even when paused for smooth display)
        if agent.speed > 0:
            clock.tick(agent.speed)
        elif not agent.paused:
            # Only skip tick if not paused and max speed
            pass
        else:
            clock.tick(30)  # Smooth rendering when paused

if __name__ == '__main__':
    main_train()
    pygame.quit()
    sys.exit()