import pygame
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class NPC:
    # **Initialization**
    def __init__(self, x, y, npc_type):
        self.type = npc_type
        self.rect = pygame.Rect(x, y, 32, 32)
        # **ASSET REQUIRED**: Add sprites for each NPC type
        sprite_path = {
            "shopkeeper": "assets/npcs/shopkeeper.png",
            "quest_giver": "assets/npcs/quest_giver.png"
        }[npc_type]
        self.sprite = pygame.image.load(os.path.join(PROJECT_ROOT, sprite_path)).convert_alpha()
        self.shop_items = {"ice_bolt": 50, "health_potion": 20} if npc_type == "shopkeeper" else {}
        self.quest = {"task": "kill_enemies", "target": 5, "reward": 100} if npc_type == "quest_giver" else None
        self.kills = 0

    # **Interact with NPC**
    def interact(self, player):
        if self.type == "shopkeeper":
            print("Shopkeeper: Welcome! Buy something?")
            for item, price in self.shop_items.items():
                if player.gold >= price:
                    print(f" - {item}: {price} gold (Press {list(self.shop_items.keys()).index(item) + 1} to buy)")
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_1 + list(self.shop_items.keys()).index(item)]:
                        player.gold -= price
                        if item == "health_potion":
                            player.health = player.max_health
                        else:
                            player.inventory.append(item)
                        print(f"Bought {item}!")
        elif self.type == "quest_giver":
            if self.kills >= self.quest["target"]:
                player.gold += self.quest["reward"]
                print(f"Quest complete! Rewarded {self.quest['reward']} gold.")
                self.quest = None
            else:
                print(f"Quest: Kill {self.quest['target']} enemies. Progress: {self.kills}/{self.quest['target']}")

    # **Draw NPC**
    def draw(self, screen):
        screen.blit(self.sprite, self.rect)