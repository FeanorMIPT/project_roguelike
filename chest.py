from constants import *
import config
import pygame
import math


class Chest:
    """Класс, отвечающий за предметы для взаимодействия:
     сундуки и точки входа/выхода из игры
     """

    def __init__(self, x: int, y: int, chest_type: str = "C") -> None:
        """Инициализирует сундук.
            Args:
                x (int): Координата x (в клетках)
                y (int): Координата y (в клетках)
                chest_type (str, optional): Тип: 'C' — обычный, 'E' - финальный, 'S' - стартовый. Defaults to 'C'
        """
        self.x = x
        self.y = y
        self.type = chest_type
        self.opened = False

    def is_near(self, player: "Player") -> bool:
        """Проверяет, находится ли игрок рядом с сундуком
            Args:
                player (Player): Объект игрока
            Returns:
                bool: True, если игрок рядом и сундук ещё не открыт
        """
        player_cx = player.x + TILE_SIZE // 2
        player_cy = player.y + TILE_SIZE // 2
        chest_cx = self.x * TILE_SIZE + TILE_SIZE // 2
        chest_cy = self.y * TILE_SIZE + TILE_SIZE // 2
        dist = math.hypot(player_cx - chest_cx, player_cy - chest_cy)
        return dist <= 40 and not self.opened

    def interact(self, player: "Player") -> None:
        """Позволяет игроку взаимодействовать с сундуком.
            Args:
                player (Player): Объект игрока который взаимодействует с сундуком
        """
        if self.opened or self.type == "S":
            return
        if self.type == "C":
            if player.coins > 0:
                player.coins -= 1
                config.earned_coins -= 1
                player.health += 1
                player.energy = 100
                self.opened = True
        elif self.type == "E":
            config.victory = True
            config.game_over = True

    def draw_hint(self, surface: pygame.Surface) -> None:
        """Отображает подсказку рядом с сундуком, если игрок близко
            Args:
                surface (pygame.Surface): Объект, который отображает подсказку
        """
        chest_cx = self.x * TILE_SIZE + TILE_SIZE // 2 - config.camera_x
        chest_cy = self.y * TILE_SIZE - config.camera_y

        font = pygame.font.SysFont("Arial", 20)
        if self.type == "C":
            text = font.render("Нажмите (E) чтобы получить благословение", True, (255, 255, 255))
        elif self.type == "S":
            text = font.render(
                "Двигаться - стрелками. Стрелять - пробел. Россия - наше отечество. Смерть неизбежна. Удачи!", True,
                (255, 255, 255))
        else:
            text = font.render("Победа! Загляните в дыру, Вам там покажут мультик", True, (255, 255, 255))
        surface.blit(text, (chest_cx - text.get_width() // 2, chest_cy - 25))


chests = []
for y in range(len(dungeon_map)):
    for x in range(len(dungeon_map[0])):
        if dungeon_map[y][x] == "C":
            chests.append(Chest(x, y, "C"))
        elif dungeon_map[y][x] == "E":
            chests.append(Chest(x, y, "E"))
        elif dungeon_map[y][x] == "S":
            chests.append(Chest(x, y, "S"))
