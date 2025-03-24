import math
import random

import pygame as g
from pygame import Rect

from game.tools.colors import BULLET_COLOR

bullet_speed = 20


class Bullet:
    def __init__(self, x, y, angle, spread):
        self.x = x
        self.y = y
        self.angle = angle
        self.spread = spread
        self.damage = 20

    def update(self) -> None:
        spread_angle = self.angle + random.uniform(-self.spread, self.spread)
        self.x += math.cos(math.radians(spread_angle)) * bullet_speed
        self.y += math.sin(math.radians(spread_angle)) * bullet_speed

    def draw(self, screen) -> None:
        g.draw.circle(screen, BULLET_COLOR, (int(self.x), int(self.y)), 2)

    def get_rect(self) -> Rect:
        return g.Rect(self.x - 2, self.y - 2, 4, 4)
