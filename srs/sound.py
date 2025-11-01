import pygame
import os

pygame.mixer.init()

class Sounds:
    def __init__(self):
        self.mutted = False
        try:
            self.eat = pygame.mixer.Sound("assets/eat.wav")
            self.dead = pygame.mixer.Sound("assets/dead.wav")
            pygame.mixer.music.load("assets/BGM.wav")
        except pygame.error as e:
            print(f"Error loading music file: {e}")
        pygame.mixer.music.play(-1)

    def bgm(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_m:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                    self.mutted = True
                    print("🔇 Sounds muted")
                else:
                    pygame.mixer.music.play(-1)
                    self.mutted = False
                    print("🔊 Sounds unmuted")

    def sfx_eat(self):
        if not self.mutted:
            self.eat.play()

    def sfx_dies(self):
        if not self.mutted:
            # Play without waiting (non-blocking)
            self.dead.play()
