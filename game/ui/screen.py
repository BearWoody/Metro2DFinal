import random

import pygame as g
from pygame._sdl2.video import Window

import game.game as manager
import game.tools.colors as colors
from game.data.game_state import GameState
from game.data.player import PlayerUI
from game.tools import images

min_width = 800
min_height = 600

width = min_width
height = min_height

s = g.display.set_mode((width, height), g.RESIZABLE)


def init():
    g.display.set_caption("Metro 2D")
    g.display.set_allow_screensaver(False)
    g.display.set_icon(images.ICON)

    # Start Maximized
    Window.from_display_module().maximize()

    refresh_particles()


def resize_screen(new_width: int, new_height: int):
    global width
    global height
    old_width = width
    old_height = height

    width = (new_width if new_width >= min_width else min_width)
    height = (new_height if new_height >= min_height else min_height)

    print(f"Resizing video from [{old_width}x{old_height}] to [{width}x{height}]")

    global s
    s = g.display.set_mode((width, height), g.RESIZABLE)

    refresh_particles()


def handle_left_click():
    if manager.state == GameState.IN_GAME:
        manager.game_data.handle_game_left_click(True)
    elif manager.state == GameState.MAIN_MENU:
        manager.set_state(GameState.IN_GAME)
    elif manager.state == GameState.DEAD:
        manager.set_state(GameState.MAIN_MENU)


def handle_left_click_release():
    if manager.state == GameState.IN_GAME:
        manager.game_data.handle_game_left_click(False)


def clear_screen():
    s.fill(colors.BLACK)


def update_screen():
    g.display.flip()


def update(state: GameState):
    clear_screen()

    if state == GameState.LOADING:
        ...
    elif state == GameState.MAIN_MENU:
        draw_title("Metro 2D", colors.WHITE, "Click to start!", colors.GRAY)
    elif state == GameState.SETTINGS:
        ...
    elif state == GameState.IN_GAME or state == GameState.DEAD:
        # Draw Background
        draw_particles()

        # Draw Player
        manager.game_data.player.draw(s)

        # Draw Bullets
        for bullet in manager.game_data.bullets:
            bullet.draw(s)

        # Draw Enemies
        for enemy in manager.game_data.enemies:
            enemy.draw(s)

        # Draw UI
        draw_ui()

    update_screen()


def get_font(size: int, plain: bool = False):
    return g.font.Font(None if plain else "resources/font/font.ttf", size)


def draw_title(title, title_color, subtitle, subtitle_color):
    display_subtitle = subtitle is not None

    font_title = get_font(74).render(title, True, title_color)

    title_y = 0

    if display_subtitle:
        font_subtitle = get_font(48, True).render(subtitle, True, subtitle_color)

        title_y += (font_subtitle.get_height() // 2) + (font_subtitle.get_height() // 3)

        s.blit(font_subtitle, font_subtitle.get_rect(center=(width // 2, (height // 2) + title_y)))

    s.blit(font_title, font_title.get_rect(center=(width // 2, (height // 2) - title_y)))


def draw_ui():
    # Draw Stats
    stat_color = colors.WHITE

    health = manager.game_data.player.health
    max_health = manager.game_data.player.get_max_health()
    health_color = colors.RED if health <= max_health // 4 else (
        colors.ORANGE if health <= max_health // 2 else colors.GREEN)

    filter_level = manager.game_data.player.filter_level
    filter_color = colors.RED if filter_level <= 25 else (colors.ORANGE if filter_level <= 50 else colors.GREEN)

    battery_level = manager.game_data.player.battery_level
    battery_color = colors.YELLOW

    ammo = manager.game_data.player.magazine
    max_ammo = manager.game_data.player.get_magazine_size()
    fire_mode = manager.game_data.player.fire_mode.value["short_name"]
    ammo_color = colors.GREEN if ammo > 0 else colors.RED

    h = 0
    h = draw_stat(h, f"Score   ", f"{round(manager.game_data.score, 2)}", stat_color, colors.SCORE)
    h += 10
    h = draw_stat(h, f"Health  ", f"{int(max(health, 0))}", stat_color, health_color)
    h = draw_stat(h, f"Filter  ", f"{int(filter_level)}%", stat_color, filter_color)
    h = draw_stat(h, f"Battery ", f"{round(battery_level, 1)}V", stat_color, battery_color)
    h += 10
    h = draw_stat(h, f"Gun ({fire_mode}) ", f"{ammo}/{max_ammo}", stat_color, ammo_color)

    # Draw Opened Player UI
    if manager.game_data.player.open_ui is not None:
        draw_overlay(128)

        # Draw Charger
        if manager.game_data.player.open_ui == PlayerUI.CHARGER:
            draw_charger()

        # Draw Inventory
        elif manager.game_data.player.open_ui == PlayerUI.INVENTORY:
            draw_inventory()

    # Dead State
    if manager.state == GameState.DEAD:
        # Dark Overlay
        draw_overlay(208)

        # Draw Death UI
        draw_dead()


def draw_overlay(alpha):
    overlay = g.Surface((s.get_width(), s.get_height()), g.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    s.blit(overlay, (0, 0))


def draw_stat(offset, key, value, key_color, value_color):
    position = (10, 10 + offset)
    font = get_font(20)

    prefix = font.render(key, True, key_color)
    text = font.render(value, True, value_color)

    s.blit(prefix, position)
    s.blit(text, (position[0] + prefix.get_width(), position[1]))

    return offset + prefix.get_height()


def draw_charger():
    battery_level = manager.game_data.player.battery_level

    if battery_level > 10:
        charger_image = images.CHARGER_FULL
    elif battery_level > 8.5:
        charger_image = images.CHARGER_3
    elif battery_level > 7:
        charger_image = images.CHARGER_2
    elif battery_level > 6:
        charger_image = images.CHARGER_1
    else:
        charger_image = images.CHARGER_0

    scaled_charger = g.transform.scale(charger_image, (s.get_width() // 2, s.get_width() // 2))
    charger_rect = scaled_charger.get_rect(center=(s.get_width() // 2, s.get_height() // 2))
    s.blit(scaled_charger, charger_rect)


def draw_inventory():
    title = get_font(64).render("Inventory", True, colors.BLUE)
    title_rect = title.get_rect(center=(s.get_width() // 2, (s.get_height() // 2) - (s.get_height() // 4)))
    s.blit(title, title_rect)

    spacing = 10
    inner_spacing = 10
    y_offset = 0

    for item, count in manager.game_data.player.inventory.items():
        x = title_rect.bottomleft[0]
        y = title_rect.bottomleft[1] + spacing + y_offset

        background = g.Surface((title_rect.width, 60), g.SRCALPHA)
        background.fill((0, 0, 0, 192))

        s.blit(background, (x, y))

        item_name = get_font(32).render(f"{item.get_name()}", True, colors.WHITE)
        s.blit(item_name, (x + inner_spacing, y + item_name.get_height() // 2))

        item_count = get_font(32).render(f"{max(count, 0)}", True, colors.GREEN if count > 0 else colors.RED)
        s.blit(item_count, (x + background.get_width() - inner_spacing - item_count.get_width(), y + item_count.get_height() // 2))

        y_offset += background.get_height() + spacing


def draw_dead():
    title = get_font(64).render("Game Over", True, colors.RED)
    title_rect = title.get_rect(center=(s.get_width() // 2, (s.get_height() // 2) - (s.get_height() // 3)))
    s.blit(title, title_rect)

    subtitle = get_font(36).render(f"Your Score: {int(manager.game_data.score)}", True, colors.WHITE)
    subtitle_rect = subtitle.get_rect(center=(s.get_width() // 2, (title_rect.center[1] + title_rect.height)))
    s.blit(subtitle, subtitle_rect)

    leaderboard = get_font(36).render("Leaderboard:", True, colors.ORANGE)
    leaderboard_rect = leaderboard.get_rect(center=(s.get_width() // 2, (subtitle_rect.center[1] + subtitle_rect.height + 40)))
    s.blit(leaderboard, leaderboard_rect)

    spacing = 0
    inner_spacing = 10
    y_offset = 10
    x_spacing = 100

    position = 0
    for score_data in manager.database.top_scores:
        position += 1
        name = score_data[0][:16]
        score = score_data[1]
        date = score_data[2].strftime("%Y-%m-%d")

        x = title_rect.bottomleft[0] - x_spacing
        y = leaderboard_rect.bottomleft[1] + spacing + y_offset

        display_data = get_font(16).render(f"#{"{:02d}".format(position)} | {date} | {name}", True, colors.WHITE)
        display_score = get_font(16).render(f"{max(score, 0)}", True, colors.ORANGE)

        background = g.Surface((title_rect.width + 2*x_spacing, display_data.get_height() + 10), g.SRCALPHA)
        background.fill((0, 0, 0, 192))

        s.blit(background, (x, y))

        s.blit(display_data, (x + inner_spacing, y + display_data.get_height() // 2))

        s.blit(display_score, (x + background.get_width() - inner_spacing - display_score.get_width(), y + display_score.get_height() // 2))

        y_offset += background.get_height() + spacing



particles = []


def refresh_particles():
    count = int(0.2 * s.get_width())

    global particles

    particles = []

    for _ in range(count):
        particles.append(create_particle({}))


def create_particle(original):
    original["x"] = random.randrange(0, s.get_width())
    original["y"] = -5 if "y" in original else random.randrange(0, s.get_height())
    original["speed"] = random.uniform(0.1, 0.3)
    original["size"] = random.randrange(3, 6)
    return original


def draw_particles():
    for particle in particles:
        particle["y"] += particle["speed"]

        if particle["y"] > s.get_height():
            create_particle(particle)

        g.draw.rect(
            s,
            colors.DARK_GREEN,
            (
                int(particle["x"]),
                int(particle["y"]),
                particle["size"],
                particle["size"]
            )
        )
