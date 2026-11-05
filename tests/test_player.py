import pytest
import config
from player import Player
from constants import TILE_SIZE
from bullet import bullets
from map_generator import dungeon_map
from enemy import enemies

for y in range(len(dungeon_map)):
    for x in range(len(dungeon_map[0])):
        dungeon_map[y][x] = "."

dungeon_map[5][5] = "S"

enemies.clear()


class DummyRoom:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h


class DummyEnemy:
    def __init__(self, x, y, alive=True):
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.alive = alive
        self.health = 1


@pytest.fixture
def player():
    return Player(dungeon_map)


def test_initial_position(player):
    assert player.x >= 0 and player.y >= 0


def test_update_position(player):
    start_x, start_y = player.x, player.y
    player.update_position(32, 0)
    assert player.x > start_x


def test_shoot_decreases_energy(player):
    bullets.clear()
    player.shoot(1, 0)
    assert len(bullets) == 1
    assert player.energy < 100


def test_no_shoot_when_no_energy(player):
    player.energy = 0
    bullets.clear()
    player.shoot(1, 0)
    assert len(bullets) == 0


def test_take_damage_and_survive(player):
    player.take_damage(3)
    assert player.health == 7
    assert not config.game_over


def test_take_damage_and_die(player):
    player.health = 1
    player.take_damage(2)
    assert config.game_over
    assert not config.victory


def test_can_move_to_area_true(player):
    assert player.can_move_to_area(player.x, player.y)


def test_can_move_to_area_false(player):
    tile_x = int(player.x // TILE_SIZE)
    tile_y = int(player.y // TILE_SIZE)
    dungeon_map[tile_y][tile_x] = "#"
    assert not player.can_move_to_area(player.x, player.y)
    dungeon_map[tile_y][tile_x] = "."


def test_push_out_from_wall(player):
    dungeon_map[int(player.y // TILE_SIZE)][int(player.x // TILE_SIZE)] = "#"
    player.push_out_from_wall()
    assert dungeon_map[int(player.y // TILE_SIZE)][int(player.x // TILE_SIZE)] != "#"


def test_check_trap_damage_triggers(player):
    trap_x = int(player.x // TILE_SIZE)
    trap_y = int(player.y // TILE_SIZE)
    dungeon_map[trap_y][trap_x] = "^"
    old_health = player.health
    player.last_trap_damage_time = 0
    player.check_trap_damage()
    assert player.health == old_health - 1
    dungeon_map[trap_y][trap_x] = "."


def test_get_nearest_enemy_in_room(player):
    room = DummyRoom(1, 1, 10, 10)
    e1 = DummyEnemy(2, 2)
    e2 = DummyEnemy(3, 3)
    enemies.extend([e1, e2])
    closest = player.get_nearest_enemy_in_room(room)
    assert closest in [e1, e2]
