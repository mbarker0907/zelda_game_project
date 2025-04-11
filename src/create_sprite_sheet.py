import pygame
import os

# Initialize Pygame
pygame.init()

# Set up a minimal display (required on some systems to load images)
pygame.display.set_mode((1, 1), pygame.NOFRAME)  # 1x1 pixel window, no frame (hidden)

# Define paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ice_bolt_path = os.path.join(PROJECT_ROOT, "assets", "projectiles", "ice bolt")
ice_bolt_files = ["ice1.png", "ice2.png", "ice3.png", "ice4.png", "ice5.png"]

# Print the path for debugging
print(f"Looking for ice bolt images in: {ice_bolt_path}")

# Load each image
ice_bolt_images = []
for file in ice_bolt_files:
    image_path = os.path.join(ice_bolt_path, file)
    if not os.path.exists(image_path):
        print(f"Error: File not found - {image_path}")
        exit(1)
    image = pygame.image.load(image_path).convert_alpha()
    if image.get_width() != 32 or image.get_height() != 32:
        print(f"Error: Image {file} is not 32x32 pixels! Dimensions: {image.get_width()}x{image.get_height()}")
        exit(1)
    ice_bolt_images.append(image)

# Create a sprite sheet (160x32)
sprite_sheet = pygame.Surface((160, 32), pygame.SRCALPHA)
for i, image in enumerate(ice_bolt_images):
    sprite_sheet.blit(image, (i * 32, 0))

# Save the sprite sheet
output_path = os.path.join(ice_bolt_path, "ice_bolt_sheet.png")
pygame.image.save(sprite_sheet, output_path)
print(f"Sprite sheet saved to {output_path}")

# Clean up
pygame.quit()