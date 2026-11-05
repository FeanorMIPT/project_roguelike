from bullet import *
from typing import Optional, List


class Enemy:
    """Класс, обрабатывающий врагов"""

    def __init__(self, x: int, y: int, sprite: pygame.Surface, health: int = 2) -> None:
        """Инициализация врага
            Args:
                x (int): Координата x в тайлах
                y (int): Координата y в тайлах
                sprite (pygame.Surface): Спрайт врага
                health (int, optional): Количество жизней Defaults to 2
        """
        self.x = float(x * TILE_SIZE)
        self.y = float(y * TILE_SIZE)
        self.dir = 1
        self.sprite = sprite
        self.health = health
        self.alive = True
        self.mode = "patrol"
        self.patrol_target = None
        self.shoot_timer = 0.0

    def update(self, dt: float, player_x: float, player_y: float) -> None:
        """Обновление состояния врага
            Args:
                dt (float): Время между кадрами
                player_x (float): Координата х игрока
                player_y (float): Координата у игрока
        """
        if not self.alive:
            return
        in_same_room = get_current_room(player_x, player_y) is get_current_room(self.x, self.y)
        if in_same_room and self.has_line_of_sight(player_x, player_y):
            self.mode = "attack"
        else:
            self.mode = "patrol"
        if self.mode == "attack":
            self.attack_mode(dt, player_x, player_y)
        else:
            self.patrol_mode(dt)

    def attack_mode(self, dt: float, player_x: float, player_y: float) -> None:
        """Режим атаки: приближается к игроку и стреляет
            Args:
                dt (float): Время между кадрами
                player_x (float): Координата х игрока
                player_y (float): Координата у игрока
        """
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 4 * TILE_SIZE:
            self.move_towards(dx, dy, dt * 3.5 * TILE_SIZE)
        self.shoot_timer += dt
        if self.shoot_timer >= 2.0 and dist <= 5 * TILE_SIZE:
            self.shoot_timer = 0
            d = math.hypot(dx, dy)
            dx /= d
            dy /= d
            bullets.append(Bullet(self.x, self.y, dx, dy, "enemy"))

    def patrol_mode(self, dt: float) -> None:
        """Режим патрулирования в случайном направлении
            Args:
                dt (float): Время между кадрами
        """
        if self.patrol_target is None or (
                abs(self.x - self.patrol_target[0]) < 2.0 and abs(self.y - self.patrol_target[1]) < 2.0
        ):
            for _ in range(100):
                if random.random() < 0.01:
                    dx_px, dy_px = random.choice(PATROL_DIRECTIONS)
                    tx = self.x + dx_px
                    ty = self.y + dy_px
                    if can_enemy_move_to_area(tx, ty):
                        self.patrol_target = (tx, ty)
                        break
            else:
                self.patrol_target = (self.x, self.y)
        dx = self.patrol_target[0] - self.x
        dy = self.patrol_target[1] - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.move_towards(dx, dy, dt * 2 * TILE_SIZE)

    def move_towards(self, dx: float, dy: float, speed: float) -> bool:
        """Враг движется по направлению (dx, dy) со скоростью speed
            Args:
                dx (float): Направление по x
                dy (float): Направление по y
                speed (float): Скорость движения
            Returns:
                bool: True, если смог сдвинуться
        """
        d = math.hypot(dx, dy)
        if d == 0:
            return False
        dx /= d
        dy /= d
        next_x = self.x + dx * speed
        next_y = self.y + dy * speed
        moved = False
        if can_enemy_move_to_area(next_x, self.y):
            self.x = next_x
            moved = True
        if can_enemy_move_to_area(self.x, next_y):
            self.y = next_y
            moved = True
        if not can_enemy_move_to_area(self.x, self.y):
            self.push_out_from_wall()
            moved = True
        return moved

    def has_line_of_sight(self, x1: float, y1: float, step: float = 0.1) -> bool:
        """Проверяет наличие прямой видимости до игрока
            Args:
                x1 (float): Координата x цели
                y1 (float): Координата y цели
                step (float, optional): Шаг проверки. Defaults to 0.1
            Returns:
                bool: True, если препятствий нет
        """
        dx = x1 - self.x
        dy = y1 - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return True
        steps = int(dist / (TILE_SIZE * step))
        for i in range(1, steps):
            t = i / steps
            x = self.x + dx * t
            y = self.y + dy * t
            tile_x = int(x // TILE_SIZE)
            tile_y = int(y // TILE_SIZE)
            if 0 <= tile_y < len(dungeon_map) and 0 <= tile_x < len(dungeon_map[0]):
                if dungeon_map[tile_y][tile_x] in obstacle_tiles_for_vision:
                    return False
            else:
                return False
        return True

    def push_out_from_wall(self, sprite_size: int = TILE_SIZE, tolerance: int = 5) -> None:
        """Выталкивает врага из стены, если он застрял
            Args:
                sprite_size (int, optional): Размер спрайта. Defaults to TILE_SIZE
                tolerance (int, optional): Допуск по краям для скольжения. Defaults to 5
        """
        tile_x = int(self.x // TILE_SIZE)
        tile_y = int(self.y // TILE_SIZE)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx = tile_x + dx
            ny = tile_y + dy
            if 0 <= ny < len(dungeon_map) and 0 <= nx < len(dungeon_map[0]):
                px = nx * TILE_SIZE
                py = ny * TILE_SIZE
                if can_enemy_move_to_area(px, py, sprite_size, tolerance):
                    self.x = px
                    self.y = py
                    return


def get_current_room(px: float, py: float) -> Optional["Room"]:
    """Возвращает комнату, в которой находится точка (px, py)
        Args:
            px (float): Координата x
            py (float): Координата y
        Returns:
            Optional[object]: Комната или None
    """
    tile_x = int(px // TILE_SIZE)
    tile_y = int(py // TILE_SIZE)
    for room in exported_rooms:
        if room.x <= tile_x < room.x + room.w and room.y <= tile_y < room.y + room.h:
            return room
    return None


def can_enemy_move_to_area(px: float, py: float, sprite_size: int = TILE_SIZE, tolerance: int = 5) -> bool:
    """Проверяет, можно ли врагу двигаться в данную точку
    Args:
        px (float): Позиция x
        py (float): Позиция y
        sprite_size (int, optional): Размер спрайта. Defaults to TILE_SIZE
        tolerance (int, optional): Допуск по краям для скольжения. Defaults to 5
    Returns:
        bool: True, если можно двигаться, False иначе
    """
    corners = [
        (px + tolerance, py + tolerance),
        (px + sprite_size - tolerance, py + tolerance),
        (px + tolerance, py + sprite_size - tolerance),
        (px + sprite_size - tolerance, py + sprite_size - tolerance),
    ]
    for px, py in corners:
        if px < 0 or py < 0 or px >= len(dungeon_map[0]) * TILE_SIZE or py >= len(dungeon_map) * TILE_SIZE:
            return False
        tile_x = int(px // TILE_SIZE)
        tile_y = int(py // TILE_SIZE)
        if dungeon_map[tile_y][tile_x] in obstacle_tiles_for_movement:
            return False
    return True


enemies = []
for y, row in enumerate(dungeon_map):
    for x, tile in enumerate(row):
        if tile == "M":
            enemies.append(Enemy(x, y, TILES["ENEMY"]))
