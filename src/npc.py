import pygame
import os
from config import *

class NPC:
    def __init__(self, x, y, npc_type, player):
        self.type = npc_type
        self.player = player  # Store reference to the player
        self.rect = pygame.Rect(x, y, 32, 32)
        sprite_path = {
            "shopkeeper": "npcs/shopkeeper.png",
            "quest_giver": "npcs/quest_giver.png"
        }[npc_type]
        self.sprite = pygame.image.load(os.path.join(ASSETS_PATH, sprite_path)).convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (self.rect.width, self.rect.height))  # Scale sprite to 32x32
        self.shop_items = {"ice_bolt": 50, "health_potion": 20} if npc_type == "shopkeeper" else {}
        self.sold_items = []
        self.quest = {"task": "kill_enemies", "target": 5, "reward": 100} if npc_type == "quest_giver" else None
        self.kills = 0

    def interact(self):
        if self.type == "shopkeeper":
            # Shopkeeper interaction is handled in main.py (Game.handle_input)
            pass
        elif self.type == "quest_giver" and self.quest:
            if self.kills >= self.quest["target"]:
                self.player.experience += self.quest["reward"]  # Award EXP
                self.player.gold += self.quest["reward"]  # Award gold
                print(f"Quest completed! Gained {self.quest['reward']} EXP and {self.quest['reward']} gold.")
                self.quest = None  # Clear the quest
            else:
                print(f"Quest: Kill {self.quest['target']} enemies. Progress: {self.kills}/{self.quest['target']}")

    def mark_item_sold(self, item):
        if item in self.shop_items:
            self.sold_items.append(item)
            del self.shop_items[item]

    def update(self):
        # Placeholder for future NPC behavior (e.g., movement, dialogue updates)
        pass

    def draw(self, screen):
        screen.blit(self.sprite, self.rect)