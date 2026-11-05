import pytest
from enemy import Enemy, can_enemy_move_to_area
from constants import TILE_SIZE
from bullet import bullets
import enemy
from map_generator import dungeon_map

for y in range(len(dungeon_map)):
    for x in range(len(dungeon_map[0])):
        dungeon_map[y][x] = "."


class DummyRoom:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


enemy.exported_rooms.clear()
enemy.exported_rooms.append(DummyRoom(0, 0, 50, 50))


def test_enemy_patrol_mode():
    e = Enemy(10, 10, None)
    e.patrol_mode(0.1)
    assert e.mode == "patrol"
    assert isinstance(e.patrol_target, tuple)


def test_enemy_move_towards_moves():
    e = Enemy(5, 5, None)
    moved = e.move_towards(32, 0, TILE_SIZE)
    assert moved
    assert e.x != 5 * TILE_SIZE


def test_enemy_push_out_from_wall():
    e = Enemy(5, 5, None)
    dungeon_map[int(e.y // TILE_SIZE)][int(e.x // TILE_SIZE)] = "#"
    e.push_out_from_wall()
    assert can_enemy_move_to_area(e.x, e.y)


def test_has_line_of_sight_true():
    e = Enemy(5, 5, None)
    e.x = 5 * TILE_SIZE + TILE_SIZE // 2
    e.y = 5 * TILE_SIZE + TILE_SIZE // 2
    target_x = e.x + 5 * TILE_SIZE
    target_y = e.y
    for tx in range(5, 11):
        dungeon_map[5][tx] = "."
    assert e.has_line_of_sight(target_x, target_y)


def test_has_line_of_sight_blocked():
    e = Enemy(5, 5, None)
    e.x = 5 * TILE_SIZE + TILE_SIZE // 2
    e.y = 5 * TILE_SIZE + TILE_SIZE // 2
    dungeon_map[5][6] = "#"
    target_x = e.x + 3 * TILE_SIZE
    target_y = e.y
    assert not e.has_line_of_sight(target_x, target_y)
    dungeon_map[5][6] = "."


def test_enemy_attack_mode_and_shooting():
    bullets.clear()
    e = Enemy(5, 5, None)
    px = e.x + 3 * TILE_SIZE
    py = e.y
    e.shoot_timer = 2.0
    e.attack_mode(0.1, px, py)
    assert len(bullets) == 1
    b = bullets[0]
    assert b.owner == "enemy"


def test_enemy_update_switches_mode():
    e = Enemy(5, 5, None)
    px = e.x + 3 * TILE_SIZE
    py = e.y
    e.update(0.1, px, py)
    assert e.mode in {"patrol", "attack"}
