from enum import Enum


class GameState(Enum):
    EXITING = 0
    LOADING = 1
    MAIN_MENU = 2
    # TODO: Add Tutorial screen
    SETTINGS = 3
    IN_GAME = 4
    DEAD = 5

    def is_in_game(self) -> bool:
        return self == self.IN_GAME

    def is_running(self) -> bool:
        return self != self.EXITING
