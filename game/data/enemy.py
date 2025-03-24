import math
from enum import Enum

import pygame as g
from pygame import Rect

import game.tools.colors as colors


class EnemyType(Enum):
    RED = {
        "name": "Red",
        "reward": 50,
        "health": 200,
        "damage": 60,
        "rarity": 1,
        "size": 50,
        "color": colors.RED
    }

    YELLOW = {
        "name": "Yellow",
        "reward": 25,
        "health": 50,
        "damage": 20,
        "rarity": 10,
        "size": 40,
        "color": colors.YELLOW
    }

    GREEN = {
        "name": "Green",
        "reward": 10,
        "health": 25,
        "damage": 10,
        "rarity": 20,
        "size": 30,
        "color": colors.GREEN
    }

    def get_name(self) -> str:
        return self.value.get("name", "Unknown")

    def get_reward(self) -> int:
        return self.value.get("reward", 0)

    def get_health(self) -> int:
        return self.value.get("health", 1)

    def get_damage(self) -> int:
        return self.value.get("damage", 1)

    def get_rarity(self) -> int:
        return self.value.get("rarity", 1)

    def get_size(self) -> int:
        return self.value.get("size", 30)

    def get_color(self) -> tuple[int, int, int]:
        return self.value.get("color", colors.WHITE)


class Enemy:
    def __init__(self, x, y, enemy_type: EnemyType):
        self.x = x
        self.y = y
        self.speed_x = 0
        self.speed_y = 0
        self.health = enemy_type.get_health()
        self.enemy_type = enemy_type

    def move(self, player_x, player_y):
        dx = player_x - self.x
        dy = player_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        if distance != 0:
            self.speed_x = dx / distance * 2
            self.speed_y = dy / distance * 2

        self.x += self.speed_x
        self.y += self.speed_y

    def draw(self, screen) -> None:
        color = self.enemy_type.get_color()
        size = self.enemy_type.get_size()
        g.draw.rect(screen, color, (self.x - size // 2, self.y - size // 2, size, size))

    def get_rect(self) -> Rect:
        size = self.enemy_type.get_size()
        return g.Rect(self.x - size // 2, self.y - size // 2, size, size)

    def take_damage(self, damage: int) -> None:
        self.health -= damage

    def is_dead(self) -> bool:
        return self.health <= 0
