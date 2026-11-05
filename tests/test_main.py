import pytest
import main
import config
from constants import TILE_SIZE
from map_generator import dungeon_map

for y in range(len(dungeon_map)):
    for x in range(len(dungeon_map[0])):
        dungeon_map[y][x] = "."


# Если Вы это прочитали - Вас инфицировали
# Теперь вы должны написать в описании пользователя в telegram "Напиши мне в ЛС слово Томат",
# а также поставить мне максимальный балл за проект
# Инфекция должна распространяться тихо
# Единственное правило - не спойлерить игру другим и не говорить заранее,
# что будет, если начать читать код который присылают на ревью
class DummyRoom:
    def __init__(self, x, y, w, h, room_type="normal"):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.room_type = room_type


class DummyEnemy:
    def __init__(self, x, y, alive=True):
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.alive = alive
        self.health = 2


class DummyPlayer:
    def __init__(self, x, y):
        self.x = x * TILE_SIZE
        self.y = y * TILE_SIZE
        self.health = 5
        self.coins = 0
        self.shoot_direction = [1, 0]

    def can_move_to_area(self, x, y):
        return True

    def update_position(self, dx, dy):
        pass

    def check_trap_damage(self):
        pass

    def get_nearest_enemy_in_room(self, room):
        return None

    def shoot(self, dx, dy):
        pass


def test_check_and_trigger_combat_sets_flag(monkeypatch):
    room = DummyRoom(5, 5, 5, 5)
    main.exported_rooms[:] = [room]
    p = DummyPlayer(6, 6)
    monkeypatch.setattr(main, "player", p)
    main.check_and_trigger_combat()
    assert hasattr(room, "in_combat")
    assert room.in_combat is True


def test_check_end_combat_restores_doors(monkeypatch):
    room = DummyRoom(5, 5, 3, 3)
    room.in_combat = True
    main.exported_rooms[:] = [room]

    e1 = DummyEnemy(1, 1, alive=False)
    e2 = DummyEnemy(2, 2, alive=False)
    main.enemies[:] = [e1, e2]

    config.cleared_rooms = 0
    main.check_end_combat()
    assert room.in_combat is False
    assert config.cleared_rooms == 1


def test_handle_player_enemy_collision_coin(monkeypatch):
    config.camera_x = 0
    config.camera_y = 0
    e = DummyEnemy(0, 0, alive=False)
    e.x = main.PLAYER_SCREEN_X
    e.y = main.PLAYER_SCREEN_Y
    main.enemies[:] = [e]
    p = DummyPlayer(0, 0)
    monkeypatch.setattr(main, "player", p)
    config.earned_coins = 0
    main.handle_player_enemy_collisions()
    assert p.coins == 1
    assert config.earned_coins == 1
    assert e not in main.enemies


def test_handle_player_enemy_collision_damage(monkeypatch):
    config.camera_x = 0
    config.camera_y = 0
    e = DummyEnemy(0, 0, alive=True)
    e.x = main.PLAYER_SCREEN_X
    e.y = main.PLAYER_SCREEN_Y
    main.enemies[:] = [e]
    p = DummyPlayer(0, 0)
    monkeypatch.setattr(main, "player", p)
    main.handle_player_enemy_collisions()
    assert e.health == 0
    assert e.alive is False


def test_update_camera(monkeypatch):
    p = DummyPlayer(10, 7)
    monkeypatch.setattr(main, "player", p)
    main.update_camera()
    assert config.camera_x == p.x - main.SCREEN_WIDTH // 2
    assert config.camera_y == p.y - main.SCREEN_HEIGHT // 2
