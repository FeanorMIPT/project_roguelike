from constants import *
import config
from typing import List


class Bullet:
    """Класс, отвечающий за снаряды, которые выпускают враги и игрок"""

    def __init__(self, x: float, y: float, dx: float, dy: float, owner: str) -> None:
        """Инициализирует пулю
            Args:
               x (float): Координата x пули
               y (float): Координата y пули
               dx (float): Направление по x                   dy (float): Направление по y
               owner (str): Кто выстрелил ("player" или "enemy")
        """
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.owner = owner

    def update(self, dt: float) -> None:
        """Обновляет положение пули с учётом времени
            Args:
                dt (float): Время между кадрами
        """
        self.x += self.dx * bullet_speed * dt
        self.y += self.dy * bullet_speed * dt

    def is_outside_map(self) -> bool:
        """Проверяет, находится ли пуля за пределами карты
            Returns:
                bool: True, если пуля вышла за пределы карты, иначе False
        """
        tile_x = int(self.x // TILE_SIZE)
        tile_y = int(self.y // TILE_SIZE)
        return not (0 <= tile_x < len(dungeon_map[0]) and 0 <= tile_y < len(dungeon_map))


def update_bullets(dt: float, enemies: List, player: "Player") -> None:
    """Обновляет список пуль, проверяя столкновения с препятствиями, врагами и игроком
        Args:
            dt (float): Время между кадрами
            enemies (List): Список объектов врагов
            player (Player): Игрок, по которому могут стрелять враги
    """
    global bullets
    for bullet in bullets[:]:
        bullet.update(dt)
        tile_x = int(bullet.x // TILE_SIZE)
        tile_y = int(bullet.y // TILE_SIZE)
        if bullet.is_outside_map():
            bullets.remove(bullet)
            continue
        tile = dungeon_map[tile_y][tile_x]
        bullet_rect = pygame.Rect(bullet.x, bullet.y, 8, 8)
        if tile == "+":
            tile_rect = pygame.Rect(tile_x * TILE_SIZE, tile_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if bullet_rect.colliderect(tile_rect):
                dungeon_map[tile_y][tile_x] = "."
                bullets.remove(bullet)
                continue
        if tile in {"#", "*"}:
            tile_rect = pygame.Rect(tile_x * TILE_SIZE, tile_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if bullet_rect.colliderect(tile_rect):
                bullets.remove(bullet)
                continue
        if bullet.owner == "player":
            for enemy in enemies:
                if not enemy.alive:
                    continue
                enemy_rect = pygame.Rect(enemy.x, enemy.y, TILE_SIZE, TILE_SIZE)
                if bullet_rect.colliderect(enemy_rect):
                    enemy.health -= 1
                    if enemy.health <= 0:
                        enemy.alive = False
                        config.killed_enemies += 1
                    bullets.remove(bullet)
                    break
        elif bullet.owner == "enemy":
            player_rect = pygame.Rect(player.x, player.y, TILE_SIZE, TILE_SIZE)
            if bullet_rect.colliderect(player_rect):
                player.health -= 1
                bullets.remove(bullet)
                if player.health <= 0:
                    config.game_over = True
                    return


bullets = []
