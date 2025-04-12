import pygame
from config import *

# Define colors if not already in config.py
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
DEEP_SKY_BLUE = (0, 191, 255)
GOLD = (255, 215, 0)
YELLOW = (255, 255, 0)

class HUD:
    def __init__(self, player, font):
        self.player = player
        self.font = font
        self.height = HUD_HEIGHT
        self.background = pygame.Surface((WINDOW_WIDTH, self.height))
        self.background.fill(BROWN)
        # Load UI sprites
        self.heart_sprite = pygame.image.load(os.path.join(ASSETS_PATH, "ui/heart.png")).convert_alpha()
        self.key_sprite = pygame.image.load(os.path.join(ASSETS_PATH, "ui/key.png")).convert_alpha()
        self.gold_sprite = pygame.image.load(os.path.join(ASSETS_PATH, "ui/gold.png")).convert_alpha()
        self.weapon_sprites = {
            "ice_bolt": pygame.image.load(os.path.join(ASSETS_PATH, "ui/ice_bolt_icon.png")).convert_alpha(),
            "bomb": pygame.image.load(os.path.join(ASSETS_PATH, "ui/bomb_icon.png")).convert_alpha()
        }
        # Scale sprites to a consistent size (e.g., 32x32)
        self.heart_sprite = pygame.transform.scale(self.heart_sprite, (24, 24))
        self.key_sprite = pygame.transform.scale(self.key_sprite, (24, 24))
        self.gold_sprite = pygame.transform.scale(self.gold_sprite, (24, 24))
        for item in self.weapon_sprites:
            self.weapon_sprites[item] = pygame.transform.scale(self.weapon_sprites[item], (24, 24))

    def draw(self, screen, world):
        screen.blit(self.background, (0, 0))

        # Draw health
        for i in range(self.player.max_health):
            heart_x = 10 + i * (self.heart_sprite.get_width() + 5)  # Reduced spacing for better fit
            heart_y = 10
            if i < self.player.health:
                screen.blit(self.heart_sprite, (heart_x, heart_y))
            else:
                empty_heart = self.heart_sprite.copy()
                empty_heart.fill((128, 128, 128, 128), special_flags=pygame.BLEND_RGBA_MULT)  # Gray out empty hearts
                screen.blit(empty_heart, (heart_x, heart_y))

        # Draw inventory (items)
        for idx, item in enumerate(self.player.inventory):
            if item in self.weapon_sprites:
                icon = self.weapon_sprites[item]
                icon_x = 150 + idx * 30  # Reduced spacing
                icon_y = 10
                screen.blit(icon, (icon_x, icon_y))

        # Draw current weapon
        weapon_text = self.font.render(f"Weapon: {self.player.current_weapon}", True, WHITE)
        screen.blit(weapon_text, (150, 40))

        # Draw level and EXP
        level_text = self.font.render(f"Level: {self.player.level}", True, WHITE)
        exp_text = self.font.render(f"EXP: {self.player.experience}/{self.player.experience_to_next_level}", True, WHITE)
        screen.blit(level_text, (300, 10))
        screen.blit(exp_text, (300, 40))

        # Draw EXP bar
        exp_bar_width = 100
        exp_ratio = self.player.experience / self.player.experience_to_next_level if self.player.experience_to_next_level > 0 else 0
        exp_bar = pygame.Rect(450, 10, exp_bar_width * exp_ratio, 10)
        pygame.draw.rect(screen, YELLOW, exp_bar)
        pygame.draw.rect(screen, WHITE, (450, 10, exp_bar_width, 10), 2)  # Border

        # Draw keys (directly use self.player.keys, since "key" is not in inventory in newer code)
        key_count = self.player.keys
        if key_count > 0:
            screen.blit(self.key_sprite, (450, 40))
            key_text = self.font.render(f"x{key_count}", True, WHITE)
            screen.blit(key_text, (480, 40))

        # Draw gold
        gold_text = self.font.render(f"Gold: {self.player.gold}", True, GOLD)
        gold_text_width = gold_text.get_width()
        gold_sprite_x = WINDOW_WIDTH - gold_text_width - 40
        gold_y = 10
        screen.blit(self.gold_sprite, (gold_sprite_x, gold_y))
        screen.blit(gold_text, (gold_sprite_x + 30, gold_y))

        # Draw day/night indicator
        time_text = self.font.render("Night" if world.is_night else "Day", True, WHITE)
        screen.blit(time_text, (WINDOW_WIDTH - 100, 40))

    def get_height(self):
        return self.height