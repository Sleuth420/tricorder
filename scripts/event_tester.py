import pygame
import sys

pygame.init()
screen = pygame.display.set_mode((300, 200))
pygame.display.set_caption("Event Tester")

while True:
    for event in pygame.event.get():
        print(event) # Print the raw event object
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            print(f"KEYDOWN: Key={pygame.key.name(event.key)}, Code={event.key}, Mod={pygame.key.get_mods()}")
        if event.type == pygame.KEYUP:
             print(f"KEYUP: Key={pygame.key.name(event.key)}, Code={event.key}, Mod={pygame.key.get_mods()}")

    pygame.time.Clock().tick(30) 