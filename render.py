from player import *
from bullet import *

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Пучков Иван Б05-424 проект Python")
clock = pygame.time.Clock()


def draw_map() -> None:
    """Отрисовывает видимую часть карты на экране"""
    first_tile_x = int(config.camera_x // TILE_SIZE)
    first_tile_y = int(config.camera_y // TILE_SIZE)
    offset_x = config.camera_x % TILE_SIZE
    offset_y = config.camera_y % TILE_SIZE
    for y in range(VISIBLE_ROWS + 2):
        for x in range(VISIBLE_COLS + 2):
            map_x = first_tile_x + x
            map_y = first_tile_y + y
            if 0 <= map_y < len(dungeon_map) and 0 <= map_x < len(dungeon_map[0]):
                tile = dungeon_map[map_y][map_x]
                if tile in TILES:
                    img = TILES[tile]
                    draw_x = x * TILE_SIZE - offset_x
                    draw_y = y * TILE_SIZE - offset_y
                    screen.blit(img, (draw_x, draw_y))


def draw_bullets() -> None:
    """Отрисовывает пули на экране"""
    for bullet in bullets:
        screen.blit(BULLET_SPRITE, (
            bullet.x - config.camera_x,
            bullet.y - config.camera_y
        ))


def draw_overlay_image() -> None:
    """Отображает мини-карту поверх основного экрана"""
    overlay_surface = draw_map_highlighted_room()
    quarter_x = SCREEN_WIDTH // 4 - overlay_surface.get_width() // 2
    quarter_y = SCREEN_HEIGHT // 4 - overlay_surface.get_height() // 2
    screen.blit(overlay_surface, (quarter_x, quarter_y))


def draw_map_highlighted_room():
    """Создаёт мини-карту подземелья с подсвеченной текущей комнатой игрока
        Returns:
            pygame.Surface: Поверхность с отрисованной мини-картой
    """
    cell_size = 2
    map_width = len(dungeon_map[0])
    map_height = len(dungeon_map)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, map_width * cell_size, map_height * cell_size)
    ctx = cairo.Context(surface)
    ctx.set_source_rgba(0, 0, 0, 0)
    ctx.paint()
    highlighted_room = None
    for room in exported_rooms:
        if room.x <= player.x // TILE_SIZE < room.x + room.w and room.y <= player.y // TILE_SIZE < room.y + room.h:
            highlighted_room = room
            break
    for y in range(map_height):
        for x in range(map_width):
            tile = dungeon_map[y][x]
            if tile == "#":
                ctx.set_source_rgb(90 / 255, 60 / 255, 30 / 255)
            elif tile in {".", "*", "+", "M", "S", "E", "C", "D", "^"}:
                if highlighted_room and (highlighted_room.x <= x < highlighted_room.x + highlighted_room.w) and (
                        highlighted_room.y <= y < highlighted_room.y + highlighted_room.h):
                    ctx.set_source_rgb(1, 1, 1)
                else:
                    ctx.set_source_rgb(180 / 255, 180 / 255, 180 / 255)
            else:
                continue
            ctx.rectangle(x * cell_size, y * cell_size, cell_size, cell_size)
            ctx.fill()
    return pygame.image.frombuffer(surface.get_data(), (map_width * cell_size, map_height * cell_size), "ARGB")


def draw_hud(surface: pygame.Surface) -> None:
    """Отрисовывает информационную панель
        Args:
            surface (pygame.Surface): Поверхность, на которую производится отрисовка
    """
    font = pygame.font.SysFont("Arial", 24)
    padding = 10
    spacing = 40
    icon_size = 32
    icon_coin = pygame.image.load("assets/coin.png")
    icon_heart = pygame.image.load("assets/heart.png")
    icon_bolt = pygame.image.load("assets/bolt.png")

    color_coin = (255, 215, 0)
    color_heart = (255, 0, 0)
    color_bolt = (0, 191, 255)

    text_coin = font.render(f"{player.coins}", True, color_coin)
    text_health = font.render(f"{player.health}", True, color_heart)
    text_energy = font.render(f"{player.energy}", True, color_bolt)

    x = SCREEN_WIDTH - padding
    y = padding

    surface.blit(icon_coin, (x - icon_size, y))
    surface.blit(text_coin, (x - icon_size - text_coin.get_width() - 5, y + (icon_size - text_coin.get_height()) // 2))

    y += spacing
    surface.blit(icon_heart, (x - icon_size, y))
    surface.blit(text_health,
                 (x - icon_size - text_health.get_width() - 5, y + (icon_size - text_health.get_height()) // 2))

    y += spacing
    surface.blit(icon_bolt, (x - icon_size, y))
    surface.blit(text_energy,
                 (x - icon_size - text_energy.get_width() - 5, y + (icon_size - text_energy.get_height()) // 2))
