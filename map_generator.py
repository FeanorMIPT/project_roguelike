import random
import math
import cairo
from data_for_map_generator import *
from typing import List, Tuple, Dict

dungeon_map = [[" " for _ in range(map_width)] for _ in range(map_height)]


class Room:
    """Класс, отвечающий за комнаты в подземелье"""

    def __init__(self, x: int, y: int, w: int, h: int, room_type: str = "normal") -> None:
        """Инициализация комнаты
            Args:
                x (int): координата x левого верхнего угла
                y (int): координата y левого верхнего угла
                w (int): ширина комнаты
                h (int): высота комнаты
                room_type (str): тип комнаты. Defaults to "normal"
        """
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.center = (x + w // 2, y + h // 2)
        self.room_type = room_type

    def distance_to(self, other: "Room") -> float:
        """Возвращает евклидово расстояние до другой комнаты
            Args:
                other (Room): другая комната
            Returns:
                float: искомое расстояние
        """
        dx = self.center[0] - other.center[0]
        dy = self.center[1] - other.center[1]
        return math.sqrt(dx ** 2 + dy ** 2)

    def carve_on_map(self) -> None:
        """Прокапывает комнату на карте (отмечает клетки как проходимые1)"""
        for y in range(self.y, self.y + self.h):
            for x in range(self.x, self.x + self.w):
                dungeon_map[y][x] = "."

    def add_doors(self) -> None:
        """Добавляет двери в комнату, если рядом есть проход"""
        for x in range(self.x, self.x + self.w):
            if self.y - 1 >= 0 and dungeon_map[self.y - 1][x] == ".":
                dungeon_map[self.y - 1][x] = "D"
            if self.y + self.h < map_height and dungeon_map[self.y + self.h][x] == ".":
                dungeon_map[self.y + self.h][x] = "D"
        for y in range(self.y, self.y + self.h):
            if self.x - 1 >= 0 and dungeon_map[y][self.x - 1] == ".":
                dungeon_map[y][self.x - 1] = "D"
            if self.x + self.w < map_width and dungeon_map[y][self.x + self.w] == ".":
                dungeon_map[y][self.x + self.w] = "D"

    def populate_with_content(self) -> None:
        """Случайным образом заполняет комнату препятствиями, ловушками и врагами"""
        cx, cy = self.center
        key = (self.w, self.h)
        if key in obstacle_patterns:
            pattern = random.choice(obstacle_patterns[key])
            for dy, row in enumerate(pattern):
                for dx, ch in enumerate(row):
                    x = self.x + 1 + dx
                    y = self.y + 1 + dy
                    if ch == "*":
                        dungeon_map[y][x] = "*"
                    elif ch == "+":
                        dungeon_map[y][x] = "+"
        for y in range(self.y + 1, self.y + self.h - 1):
            for x in range(self.x + 1, self.x + self.w - 1):
                if (x, y) == (cx, cy):
                    continue
                if dungeon_map[y][x] != ".":
                    continue
                r = random.random()
                if r < 0.05:
                    dungeon_map[y][x] = "^"
                elif r < 0.08:
                    dungeon_map[y][x] = "+"
                elif r < 0.14:
                    dungeon_map[y][x] = "M"

    @staticmethod
    def rooms_overlap(a: "Room", b: "Room") -> bool:
        """Проверяет пересекаются ли две комнаты
            Args:
                a (Room): Первая комната
                b (Room): Вторая комната
            Returns:
                bool: True, если комнаты пересекаются, false иначе
        """
        return (a.x - 1 < b.x + b.w + 1 and a.x + a.w + 1 > b.x - 1 and
                a.y - 1 < b.y + b.h + 1 and a.y + a.h + 1 > b.y - 1)

    @staticmethod
    def create_rooms() -> List["Room"]:
        """Генерирует список комнат, которые не пересекаются
            Returns:
                List[Room]: Список комнат
        """
        rooms = []
        attempts = 0
        target_rooms = random.randint(min_rooms, max_rooms)
        while len(rooms) < target_rooms and attempts < 2000:
            w, h = random.choice(room_sizes)
            x = random.randint(20, map_width - w - 21)
            y = random.randint(20, map_height - h - 21)
            new_room = Room(x, y, w, h)
            if not any(Room.rooms_overlap(new_room, r) for r in rooms):
                new_room.carve_on_map()
                rooms.append(new_room)
                attempts = 0
            else:
                attempts += 1
        return rooms if len(rooms) >= min_rooms else None

    @staticmethod
    def minimum_spanning_tree(rooms: List["Room"]) -> List[Tuple["Room", "Room"]]:
        """Строит минимальное остовное дерево по комнатам
            Args:
                rooms (List[Room]): Список комнат
            Returns:
                List[Tuple[Room, Room]]: Список соединений между комнатами
        """
        edges = []
        for i in range(len(rooms)):
            for j in range(i + 1, len(rooms)):
                edges.append((i, j, rooms[i].distance_to(rooms[j])))
        edges.sort(key=lambda x: x[2])
        parent = list(range(len(rooms)))

        def find(u):
            while parent[u] != u:
                parent[u] = parent[parent[u]]
                u = parent[u]
            return u

        mst = []
        for u, v, _ in edges:
            if find(u) != find(v):
                mst.append((rooms[u], rooms[v]))
                parent[find(u)] = find(v)
        return mst

    @staticmethod
    def build_adjacency_list(connections: List[Tuple["Room", "Room"]],
                             rooms: List["Room"]) -> Dict["Room", List["Room"]]:
        """Создаёт список смежности по связям между комнатами
            Args:
                connections (List[Tuple[Room, Room]]): Связи между комнатами.
                rooms (List[Room]): Список всех комнат
            Returns:
                Dict[Room, List[Room]]: Список смежности
        """
        adj = {room: [] for room in rooms}
        for a, b in connections:
            adj[a].append(b)
            adj[b].append(a)
        return adj


def build_corridors(connections: List[Tuple[Room, Room]]) -> None:
    """Создаёт коридоры между комнатами
        Args:
            connections (List[Tuple[Room, Room]]): Список смежности комнат
    """
    built_pairs = set()
    for a, b in connections:
        pair = tuple(sorted((id(a), id(b))))
        if pair in built_pairs:
            continue
        built_pairs.add(pair)
        x1, y1 = a.center
        x2, y2 = b.center
        if random.choice([True, False]):
            create_h_tunnel(x1, x2, y1)
            create_v_tunnel(y1, y2, x2)
        else:
            create_v_tunnel(y1, y2, x1)
            create_h_tunnel(x1, x2, y2)


def create_h_tunnel(x1: int, x2: int, y: int) -> None:
    """Создаёт горизонтальный туннель между двумя x координатами
        Args:
            x1 (int): Начало
            x2 (int): Конец
            y (int): y координата туннеля
    """
    for x in range(min(x1, x2), max(x1, x2) + 1):
        for dy in [0, 1]:
            yy = y + dy
            if 0 <= yy < map_height:
                dungeon_map[yy][x] = "."


def create_v_tunnel(y1: int, y2: int, x: int) -> None:
    """Создаёт вертикальный туннель между двумя y координатами
        Args:
            y1 (int): Начало
            y2 (int): Конец
            x (int): х координата туннеля
    """
    for y in range(min(y1, y2), max(y1, y2) + 1):
        for dx in [0, 1]:
            xx = x + dx
            if 0 <= xx < map_width:
                dungeon_map[y][xx] = "."


def add_walls() -> None:
    """Добавляет стены по краям всех проходов."""
    for y in range(map_height):
        for x in range(map_width):
            if dungeon_map[y][x] == " ":
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < map_height and 0 <= nx < map_width:
                            if dungeon_map[ny][nx] == ".":
                                dungeon_map[y][x] = "#"
                                break


def assign_room_types(rooms: List[Room], adj: Dict[Room, List[Room]]) -> Tuple[Room, Room]:
    """Назначает типы комнат: стартовую, конечную и сундуки, остальные - обычные
        Args:
            rooms (List[Room]): Все комнаты
            adj (Dict[Room, List[Room]]): Список смежности
        Returns:
            Tuple[Room, Room]: Стартовая и конечная комнаты
    """
    leaf_rooms = [room for room in rooms if len(adj[room]) == 1]
    if len(leaf_rooms) >= 2:
        start, end = random.sample(leaf_rooms, 2)
    else:
        start = random.choice(rooms)
        while True:
            end = random.choice(rooms)
            if end != start:
                break
    start.room_type = "start"
    end.room_type = "end"
    chest_rooms = random.sample(
        [r for r in rooms if r.room_type == "normal"],
        max(1, len(rooms) // 5)
    )
    for room in chest_rooms:
        room.room_type = "chest"
        cx, cy = room.center
        dungeon_map[cy][cx] = "C"
    return start, end


def draw_dungeon(dungeon_map: List[List[str]]) -> None:
    """Отрисовывает карту подземелья и сохраняет как png
        Args:
            dungeon_map (List[List[str]]): Карта подземелья
    """
    surface = cairo.ImageSurface(cairo.FORMAT_RGB24, map_width * 2, map_height * 2)
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(0.0, 0.0, 0.0)
    ctx.paint()
    for y in range(map_height):
        for x in range(map_width):
            tile = dungeon_map[y][x]
            if tile == ".":
                ctx.set_source_rgb(180 / 255, 180 / 255, 180 / 255)
            elif tile == "#":
                ctx.set_source_rgb(90 / 255, 60 / 255, 30 / 255)
            elif tile == "S":
                ctx.set_source_rgb(0 / 255, 200 / 255, 0 / 255)
            elif tile == "E":
                ctx.set_source_rgb(200 / 255, 0 / 255, 0 / 255)
            elif tile == "C":
                ctx.set_source_rgb(255 / 255, 215 / 255, 0 / 255)
            elif tile == "^":
                ctx.set_source_rgb(255 / 255, 0 / 255, 255 / 255)
            elif tile == "*":
                ctx.set_source_rgb(0 / 255, 191 / 255, 255 / 255)
            elif tile == "+":
                ctx.set_source_rgb(255 / 255, 140 / 255, 0 / 255)
            elif tile == "M":
                ctx.set_source_rgb(0 / 255, 0 / 255, 255 / 255)
            elif tile == "D":
                ctx.set_source_rgb(255 / 255, 255 / 255, 255 / 255)
            else:
                continue
            ctx.rectangle(x * 2, y * 2, 2, 2)
            ctx.fill()
    surface.write_to_png("dungeon.png")


def generate_dungeon() -> List[Room]:
    """Генерирует полное подземелье
        Returns:
            List[Room]: Список сгенерированных комнат
    """
    global dungeon_map
    rooms = Room.create_rooms()
    mst = Room.minimum_spanning_tree(rooms)
    build_corridors(mst)
    add_walls()
    adj = Room.build_adjacency_list(mst, rooms)
    start, end = assign_room_types(rooms, adj)
    for room in rooms:
        if room.room_type not in {"start", "end", "chest"}:
            room.room_type = "normal"
    sx, sy = start.center
    ex, ey = end.center
    dungeon_map[sy][sx] = "S"
    dungeon_map[ey][ex] = "E"
    for room in rooms:
        if room.room_type == "normal":
            room.populate_with_content()
        room.add_doors()
    draw_dungeon(dungeon_map)
    return rooms


rooms = generate_dungeon()
exported_map = dungeon_map
exported_rooms = rooms
