from enemy import *
from constants import *
import config

PLAYER_SCREEN_X = SCREEN_WIDTH // 2
PLAYER_SCREEN_Y = SCREEN_HEIGHT // 2


class Player:
    """Класс, описывающий игрока"""

    def __init__(self, dungeon_map: list[list[str]] = dungeon_map) -> None:
        """Инициализация игрока
            Args:
                dungeon_map (list[list[str]]): Карта подземелья Defaults to dungeon_map
        """
        self.x = 0.0
        self.y = 0.0
        self.health = 10
        self.energy = 100
        self.coins = 0
        self.shoot_direction = [1, 0]
        self.last_trap_damage_time = 0
        for y in range(len(dungeon_map)):
            for x in range(len(dungeon_map[0])):
                if dungeon_map[y][x] == "S":
                    self.x = x * TILE_SIZE
                    self.y = y * TILE_SIZE
                    return

    def update_position(self, dx_px: float, dy_px: float) -> bool:
        """Обновляет позицию игрока с учётом столкновений со стенами
            Args:
                dx_px (float): Смещение по оси х
                dy_px (float): Смещение по оси у
            Returns:
                bool: True, если движение произошло
            """
        next_x = self.x + dx_px
        next_y = self.y + dy_px
        moved = False
        if player.can_move_to_area(next_x, self.y):
            self.x = next_x
            moved = True
        if player.can_move_to_area(self.x, next_y):
            self.y = next_y
            moved = True
        if not player.can_move_to_area(self.x, self.y):
            self.push_out_from_wall()
            moved = True
        return moved

    def shoot(self, dx: float, dy: float) -> None:
        """Производит выстрел в направлении (dx, dy)
            Args:
                dx (float): Направление по х
                dy (float): Направление по у
            """
        if self.energy <= 0:
            return
        if dx == 0 and dy == 0:
            dx = 1
        d = (dx ** 2 + dy ** 2) ** 0.5
        dx /= d
        dy /= d
        bullets.append(Bullet(self.x + dx * 5, self.y + dy * 5, dx, dy, "player"))
        self.energy -= 1

    def take_damage(self, amount: int) -> None:
        """Наносит урон игроку и завершает игру при 0 здоровья
            Args:
                amount (int): Количество нанесенного урона
        """
        self.health -= amount
        if self.health <= 0:
            config.game_over = True
            config.victory = False

    def get_nearest_enemy_in_room(self, room: "Room") -> Optional["Enemy"]:
        """Находит ближайшего живого врага в комнате
            Args:
                room (Room): Комната, в которой нужно искать врага
            Returns:
                Optional[Enemy]: Ссылка на ближайшего врага, либо None
        """
        if room is None:
            return None
        min_dist = 200000000000
        closest = None
        for e in enemies:
            if not e.alive:
                continue
            if room.x * TILE_SIZE <= e.x < (room.x + room.w) * TILE_SIZE and \
                    room.y * TILE_SIZE <= e.y < (room.y + room.h) * TILE_SIZE:
                dist = (e.x - self.x) ** 2 + (e.y - self.y) ** 2
                if dist < min_dist:
                    min_dist = dist
                    closest = e
        return closest

    def can_move_to_area(self, next_x: float, next_y: float, tolerance: int = 2) -> bool:
        """Проверяет, можно ли перейти на указанную позицию
            Args:
                next_x (float): Новая позиция по х
                next_y (float): Новая позиция по у
                tolerance (int): Допуск для проверки углов. Defaults to 2
            Returns:
                bool: True, если движение возможно, false иначе
        """
        corners = [
            (next_x + tolerance, next_y + tolerance),
            (next_x + TILE_SIZE - tolerance, next_y + tolerance),
            (next_x + tolerance, next_y + TILE_SIZE - tolerance),
            (next_x + TILE_SIZE - tolerance, next_y + TILE_SIZE - tolerance),
        ]
        for px, py in corners:
            if px < 0 or py < 0 or px >= len(dungeon_map[0]) * TILE_SIZE or py >= len(dungeon_map) * TILE_SIZE:
                return False
            tile_x = int(px // TILE_SIZE)
            tile_y = int(py // TILE_SIZE)
            if dungeon_map[tile_y][tile_x] not in walkable_tiles:
                return False
        return True

    def push_out_from_wall(self) -> None:
        """Выталкивает игрока из стены, если он оказался внутри препятствия"""
        tile_x = int(self.x // TILE_SIZE)
        tile_y = int(self.y // TILE_SIZE)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dx, dy in directions:
            nx = tile_x + dx
            ny = tile_y + dy
            if 0 <= ny < len(dungeon_map) and 0 <= nx < len(dungeon_map[0]):
                px = nx * TILE_SIZE
                py = ny * TILE_SIZE
                if self.can_move_to_area(px, py):
                    self.x = px
                    self.y = py
                    return

    def check_trap_damage(self) -> None:
        """Проверяет, находится ли игрок на ловушке, и наносит урон, если прошло больше 1.5 секунд с прошлого урона"""
        current_time = time.time()
        if current_time - self.last_trap_damage_time < 1.5:
            return
        player_rect = pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)
        tile_left = int(self.x // TILE_SIZE)
        tile_top = int(self.y // TILE_SIZE)
        tile_right = int((self.x + TILE_SIZE - 1) // TILE_SIZE)
        tile_bottom = int((self.y + TILE_SIZE - 1) // TILE_SIZE)
        for ty in range(tile_top, tile_bottom + 1):
            for tx in range(tile_left, tile_right + 1):
                if 0 <= ty < len(dungeon_map) and 0 <= tx < len(dungeon_map[0]):
                    if dungeon_map[ty][tx] == "^":
                        trap_rect = pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                        intersection = player_rect.clip(trap_rect)
                        if intersection.width * intersection.height >= 10:
                            self.take_damage(1)
                            self.last_trap_damage_time = current_time
                            return

    @staticmethod
    def handle_player_enemy_collisions() -> None:
        """Обработка столкновений игрока с врагами"""
        player_rect = pygame.Rect(PLAYER_SCREEN_X, PLAYER_SCREEN_Y, TILE_SIZE, TILE_SIZE)
        for e in enemies:
            enemy_px = e.x - config.camera_x
            enemy_py = e.y - config.camera_y
            enemy_rect = pygame.Rect(enemy_px, enemy_py, TILE_SIZE, TILE_SIZE)
            if player_rect.colliderect(enemy_rect):
                if e.alive:
                    e.health -= 2
                    if e.health <= 0:
                        e.alive = False
                else:
                    player.coins += 1
                    config.earned_coins += 1
                    enemies.remove(e)


player = Player(dungeon_map)
config.camera_x = player.x - SCREEN_WIDTH // 2
config.camera_y = player.y - SCREEN_HEIGHT // 2
