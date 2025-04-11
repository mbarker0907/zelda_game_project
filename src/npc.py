import pygame
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class NPC:
    def __init__(self, x, y, npc_type):
        self.type = npc_type
        self.rect = pygame.Rect(x, y, 32, 32)
        sprite_path = {
            "shopkeeper": "assets/npcs/shopkeeper.png",
            "quest_giver": "assets/npcs/quest_giver.png"
        }[npc_type]
        self.sprite = pygame.image.load(os.path.join(PROJECT_ROOT, sprite_path)).convert_alpha()
        self.shop_items = {"ice_bolt": 50, "health_potion": 20} if npc_type == "shopkeeper" else {}
        self.sold_items = []  # Track sold items
        self.quest = {"task": "kill_enemies", "target": 5, "reward": 100} if npc_type == "quest_giver" else None
        self.kills = 0

    def interact(self, player):
        if self.type == "quest_giver":
            if self.kills >= self.quest["target"]:
                player.gold += self.quest["reward"]
                print(f"Quest complete! Rewarded {self.quest['reward']} gold.")
                self.quest = None
            else:
                print(f"Quest: Kill {self.quest['target']} enemies. Progress: {self.kills}/{self.quest['target']}")

    def mark_item_sold(self, item):
        if item in self.shop_items:
            self.sold_items.append(item)
            del self.shop_items[item]  # Remove the item from the shop

    def draw(self, screen):
        screen.blit(self.sprite, self.rect)