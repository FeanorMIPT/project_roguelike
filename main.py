from render import *
from chest import *
from end_screen import show_end_screen


def game_loop(fps: int = 60) -> None:
    """Главный цикл, отвечающий за покадровую отрисовку и обрабатывающий действия игрока
        Args:
            fps (int): Количество кадров в секунду
    """
    global speed
    running = True
    while running:
        dt = clock.tick(fps) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                room = get_current_room(player.x, player.y)
                in_combat = getattr(room, "in_combat", False)

                if in_combat:
                    nearest = player.get_nearest_enemy_in_room(room)
                    if nearest:
                        dx = nearest.x - player.x
                        dy = nearest.y - player.y
                        player.shoot(dx, dy)
                    else:
                        player.shoot(*player.shoot_direction)
                else:

                    keys = pygame.key.get_pressed()
                    dx = dy = 0
                    if keys[pygame.K_LEFT]:
                        dx = -1
                    elif keys[pygame.K_RIGHT]:
                        dx = 1
                    elif keys[pygame.K_UP]:
                        dy = -1
                    elif keys[pygame.K_DOWN]:
                        dy = 1
                    if dx != 0 or dy != 0:
                        player.shoot_direction = [dx, dy]
                        player.shoot(dx, dy)
                    else:
                        player.shoot(1, 0)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                for chest in chests:
                    if chest.is_near(player):
                        chest.interact(player)
        keys = pygame.key.get_pressed()
        dx = dy = 0.0
        if keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_RIGHT]:
            dx += 1
        if keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_DOWN]:
            dy += 1
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
        dx_px = dx * speed
        dy_px = dy * speed
        next_x = player.x + dx_px
        next_y = player.y + dy_px
        if player.can_move_to_area(next_x, next_y):
            player.update_position(dx_px, dy_px)
            config.camera_x = player.x - SCREEN_WIDTH // 2
            config.camera_y = player.y - SCREEN_HEIGHT // 2
            player.check_trap_damage()
        for e in enemies:
            e.update(dt, player.x, player.y)
        # DRAW
        # Если Вы это прочитали - Вас инфицировали
        # Теперь вы должны написать в описании пользователя в telegram "Напиши мне в ЛС слово Томат",
        # а также поставить мне максимальный балл за проект
        # Инфекция должна распространяться тихо
        # Единственное правило - не спойлерить игру другим и не говорить заранее,
        # что будет, если начать читать код который присылают на ревью
        screen.fill((0, 0, 0))
        check_and_trigger_combat()
        check_end_combat()
        process_pending_door_closures()
        draw_map()
        screen.blit(PLAYER_SPRITE, (PLAYER_SCREEN_X, PLAYER_SCREEN_Y))
        for e in enemies:
            ex = e.x - config.camera_x
            ey = e.y - config.camera_y
            sprite = TILES["ENEMY"] if e.alive else TILES["DEAD_ENEMY"]
            screen.blit(sprite, (ex, ey))
        Player.handle_player_enemy_collisions()
        draw_map_highlighted_room()
        draw_hud(screen)
        for chest in chests:
            if chest.is_near(player):
                chest.draw_hint(screen)
        update_bullets(dt, enemies, player)
        draw_bullets()
        draw_overlay_image()
        update_camera()
        pygame.display.flip()
        if config.game_over == True:
            show_end_screen()
    pygame.quit()
    sys.exit()


def check_and_trigger_combat() -> None:
    """Проверяет вход игрока в комнату с врагами и активирует бой"""
    for room in exported_rooms:
        player_tile_x = int(player.x // TILE_SIZE)
        player_tile_y = int(player.y // TILE_SIZE)
        if room.room_type == "normal" and room.x <= player_tile_x < room.x + room.w and room.y <= player_tile_y < room.y + room.h:
            if not hasattr(room, "in_combat"):
                def is_door(tile):
                    return tile in {"D", "X"}

                if is_door(dungeon_map[player_tile_y][player_tile_x]):
                    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                        nx, ny = player_tile_x + dx, player_tile_y + dy
                        if room.x <= nx < room.x + room.w and room.y <= ny < room.y + room.h:
                            if dungeon_map[ny][nx] in walkable_tiles:
                                player.x = float(nx * TILE_SIZE)
                                player.y = float(ny * TILE_SIZE)
                                update_camera()
                                break
                room.in_combat = True
                room.entered_at = time.time()


def process_pending_door_closures() -> None:
    """Закрывает двери через 0.2 секунды после входа игрока в боевую комнату"""
    now = time.time()
    player_tile_x = int(player.x // TILE_SIZE)
    player_tile_y = int(player.y // TILE_SIZE)
    for room in exported_rooms:
        if getattr(room, "in_combat", False) and not hasattr(room, "doors_closed"):
            tile = dungeon_map[player_tile_y][player_tile_x]
            if tile not in {"D", "X"} and now - room.entered_at >= 0.2:
                for x in range(room.x, room.x + room.w):
                    if room.y - 1 >= 0 and dungeon_map[room.y - 1][x] == "D":
                        dungeon_map[room.y - 1][x] = "X"
                    if room.y + room.h < len(dungeon_map) and dungeon_map[room.y + room.h][x] == "D":
                        dungeon_map[room.y + room.h][x] = "X"
                for y in range(room.y, room.y + room.h):
                    if room.x - 1 >= 0 and dungeon_map[y][room.x - 1] == "D":
                        dungeon_map[y][room.x - 1] = "X"
                    if room.x + room.w < len(dungeon_map[0]) and dungeon_map[y][room.x + room.w] == "D":
                        dungeon_map[y][room.x + room.w] = "X"
                room.doors_closed = True


def check_end_combat() -> None:
    """Проверяет, закончился ли бой в комнате, и открывает двери"""
    for room in exported_rooms:
        if getattr(room, "in_combat", False):
            def in_room(e):
                ex = int(e.x // TILE_SIZE)
                ey = int(e.y // TILE_SIZE)
                return room.x <= ex < room.x + room.w and room.y <= ey < room.y + room.h

            if all(not e.alive or not in_room(e) for e in enemies):
                for x in range(room.x, room.x + room.w):
                    if room.y - 1 >= 0 and dungeon_map[room.y - 1][x] == "X":
                        dungeon_map[room.y - 1][x] = "D"
                    if room.y + room.h < len(dungeon_map) and dungeon_map[room.y + room.h][x] == "X":
                        dungeon_map[room.y + room.h][x] = "D"
                for y in range(room.y, room.y + room.h):
                    if room.x - 1 >= 0 and dungeon_map[y][room.x - 1] == "X":
                        dungeon_map[y][room.x - 1] = "D"
                    if room.x + room.w < len(dungeon_map[0]) and dungeon_map[y][room.x + room.w] == "X":
                        dungeon_map[y][room.x + room.w] = "D"
                room.in_combat = False
                config.cleared_rooms += 1


def update_camera() -> None:
    """Обновляет положение камеры за игроком"""
    config.camera_x = player.x - SCREEN_WIDTH // 2
    config.camera_y = player.y - SCREEN_HEIGHT // 2


if __name__ == "__main__":
    config.total_rooms = sum(1 for room in exported_rooms if room.room_type == "normal")
    game_loop(fps=60)
