import config
from constants import *


def show_end_screen() -> None:
    """Отображает финальный экран после завершения игры
        В зависимости от флага config.victory показывает либо экран победы, либо поражения
        Ожидает нажатия Enter и завершает работу окна Pygame
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    font = pygame.font.SysFont("Arial", 48)
    small_font = pygame.font.SysFont("Arial", 32)
    if config.victory:
        screen.fill((255, 255, 255))
        title = font.render("Вы победили!", True, (0, 0, 0))
        kills = small_font.render(f"Убито врагов: {config.killed_enemies}", True, (0, 0, 0))
        coins = small_font.render(f"Заработано монет: {config.earned_coins}", True, (0, 0, 0))
        screen.blit(title, center(title, screen, y_offset=-60))
        screen.blit(kills, center(kills, screen, y_offset=0))
        screen.blit(coins, center(coins, screen, y_offset=60))
    else:
        screen.fill((0, 0, 0))
        title = font.render("Вы проиграли!", True, (255, 0, 0))
        rooms = small_font.render(f"Зачищено комнат: {config.cleared_rooms} из {config.total_rooms}", True,
                                  (255, 255, 255))
        screen.blit(title, center(title, screen, y_offset=-30))
        screen.blit(rooms, center(rooms, screen, y_offset=30))
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                pygame.quit()
                return


def center(surface: pygame.Surface, screen: pygame.Surface, y_offset: int = 0) -> tuple[int, int]:
    """Вычисляет координаты, чтобы отцентрировать изображение по центру экрана.
        Args:
            surface (pygame.Surface): Отрисовываемый объект
            screen (pygame.Surface): Экран, на котором происходит отрисовка
            y_offset (int, optional): Смещение по вертикали от центра. Defaults to 0
        Returns:
            tuple[int, int]: Координаты (x, y), где нужно разместить surface
    """
    x = (screen.get_width() - surface.get_width()) // 2
    y = (screen.get_height() - surface.get_height()) // 2 + y_offset
    return (x, y)
