import pytest
from bullet import Bullet, update_bullets, bullets
from constants import TILE_SIZE
import pygame

from map_generator import dungeon_map

for y in range(len(dungeon_map)):
    for x in range(len(dungeon_map[0])):
        dungeon_map[y][x] = "."


class DummyEnemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 1
        self.alive = True


class DummyPlayer:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 3


def test_bullet_update():
    bullet = Bullet(0, 0, 1, 0, "player")
    bullet.update(1.0)
    assert bullet.x > 0
    assert bullet.y == 0


def test_bullet_outside_map():
    bullet = Bullet(-100, -100, 0, 0, "player")
    assert bullet.is_outside_map()


def test_bullet_hits_enemy():
    bullets.clear()
    enemy = DummyEnemy(100, 100)
    player = DummyPlayer(0, 0)
    bullet = Bullet(enemy.x + TILE_SIZE // 2 - 4, enemy.y + TILE_SIZE // 2 - 4, 0, 0, "player")
    bullets.append(bullet)
    update_bullets(0.1, [enemy], player)
    assert not enemy.alive
    assert bullet not in bullets


def test_bullet_hits_player():
    bullets.clear()
    player = DummyPlayer(100, 100)
    enemy = DummyEnemy(0, 0)
    bullet = Bullet(100, 100, 0, 0, "enemy")
    bullets.append(bullet)
    update_bullets(0.1, [enemy], player)
    assert player.health == 2
    assert bullet not in bullets


def test_bullet_hits_wall():
    bullets.clear()
    x = 100
    y = 100
    dungeon_map[y][x] = "#"
    bullet = Bullet(x * TILE_SIZE + 1, y * TILE_SIZE + 1, 0, 0, "player")
    bullets.append(bullet)
    update_bullets(0.1, [], DummyPlayer(0, 0))
    assert bullet not in bullets
    dungeon_map[y][x] = "."


def test_bullet_hits_box():
    bullets.clear()
    x = 100
    y = 100
    dungeon_map[y][x] = "+"
    bullet = Bullet(x * TILE_SIZE + 1, y * TILE_SIZE + 1, 0, 0, "player")
    bullets.append(bullet)
    update_bullets(0.1, [], DummyPlayer(0, 0))
    assert dungeon_map[y][x] == "."
    assert bullet not in bullets
