import getpass

import pygame as g

import game.ui.screen as screen
from game.data.game_data import GameData
from game.data.game_state import GameState
from game.repository.database import Database

# PyGame Clock
frames_per_second = 60
clock = g.time.Clock()

# Game State
state: GameState = GameState.LOADING

# Current Game
game_data: GameData | None = None

# Database
database = Database("dbs.spskladno.cz", "vyuka41", "student41", "spsnet")
player_name = getpass.getuser()


def main():
    g.init()
    screen.init()

    set_state(GameState.MAIN_MENU)

    while state.is_running():
        # Update Screen
        screen.update(state)

        # Update Game
        update_game()

        # Handle PyGame events
        for event in g.event.get():
            handle_event(event)

        # Tick internal clock
        clock.tick(frames_per_second)

    print("Game closed.")


def set_state(new_state: GameState):
    global state

    old_state = state
    state = new_state

    print(f"Game State changed from {old_state.name} to {state.name}")

    global game_data

    if state == GameState.MAIN_MENU:
        game_data = None
    elif state == GameState.SETTINGS:
        ...
    elif state == GameState.IN_GAME:
        game_data = GameData()
    elif state == GameState.DEAD:
        database.add_score(player_name, int(game_data.score))
        database.refresh_leaderboard()
        game_data.player.open_ui = None


def handle_event(event):
    if event.type == g.QUIT:
        stop()

    if event.type == g.MOUSEBUTTONDOWN and event.button == 1:
        screen.handle_left_click()

    if event.type == g.MOUSEBUTTONUP and event.button == 1:
        screen.handle_left_click_release()

    if event.type == g.KEYDOWN:
        handle_key(event.key)

    if event.type == g.VIDEORESIZE:
        screen.resize_screen(event.w, event.h)


def stop():
    print("Stopping...")
    set_state(GameState.EXITING)


def handle_key(key: int):
    if state == GameState.IN_GAME:
        game_data.handle_game_key(key)
    elif state == GameState.DEAD and key == g.K_ESCAPE:
        set_state(GameState.MAIN_MENU)


def update_game():
    # Return if not in-game
    if not state.is_in_game():
        return

    # Update Game
    game_data.update_game()