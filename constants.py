import pygame
import time
import math
import random
import cairo
import sys
from map_generator import *
FPS = 60
TILE_SIZE = 32
VISIBLE_ROWS = 16
VISIBLE_COLS = 26
SCREEN_WIDTH = VISIBLE_COLS * TILE_SIZE
SCREEN_HEIGHT = VISIBLE_ROWS * TILE_SIZE
speed = 5.0
obstacle_tiles_for_vision = {"#", "*", "+", "D", "X"}
BULLET_SPRITE = pygame.image.load("assets/bullet.png")
PLAYER_SPRITE = pygame.image.load("assets/player.png")
TILES = {
    ".": pygame.image.load("assets/floor.png"),
    "#": pygame.image.load("assets/wall.png"),
    "S": pygame.image.load("assets/start.png"),
    "E": pygame.image.load("assets/end.png"),
    "C": pygame.image.load("assets/chest.png"),
    "^": pygame.image.load("assets/trap.png"),
    "*": pygame.image.load("assets/obstacle1.png"),
    "+": pygame.image.load("assets/obstacle2.png"),
    "M": pygame.image.load("assets/enemy_spawn.png"),
    "D": pygame.image.load("assets/door.png"),
    "ENEMY": pygame.image.load("assets/enemy.png"),
    "DEAD_ENEMY": pygame.image.load("assets/dead_enemy.png"),
    "X": pygame.image.load("assets/door_closed.png"),
    "BULLET_SPRITE": pygame.image.load("assets/bullet.png")
}
walkable_tiles = {".", "S", "E", "^", "M", "D"}
obstacle_tiles_for_movement = {"#", "*", "+", "D", "X"}
bullet_speed = 250.0
PATROL_DIRECTIONS = [
    (-32, 0), (32, 0), (0, -32), (0, 32),
    (-32, -32), (-32, 32), (32, -32), (32, 32)
]