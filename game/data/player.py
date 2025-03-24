import math
from enum import Enum

import pygame as g

import game.ui.screen as s
from game.data.item import Item
from game.data.weapon import FireMode
from game.tools import images, colors

player_speed = 5
player_health = 100.0
player_filter_level = 100.0


class PlayerUI(Enum):
    INVENTORY = 1
    CHARGER = 2


class Player:
    def __init__(self):
        # Position
        self.x = s.width // 2
        self.y = s.height // 2
        self.weapon_angle = 0

        # Stats
        self.health = player_health
        self.battery_level = self.get_max_battery_level()
        self.filter_level = player_filter_level

        # Inventory
        self.inventory = {
            Item.FILTER: 3,
            Item.MEDKIT: 3
        }

        # Player UI
        self.open_ui = None

        # Weapons / Shooting
        self.weapon_laser = False
        self.shooting = False
        self.last_shot_time = 0
        self.magazine = self.get_magazine_size()
        self.fire_mode = FireMode.FULL_AUTO

    def get_item_count(self, item: Item) -> int:
        return self.inventory.get(item, 0)

    def has_item(self, item: Item) -> bool:
        return self.get_item_count(item) > 0

    def take_item(self, item: Item):
        self.inventory[item] = max(0, self.get_item_count(item) - 1)

    def use_item(self, item: Item):
        if not self.has_item(item):
            return

        self.take_item(item)

        if item == Item.FILTER:
            self.filter_level = player_filter_level
        elif item == Item.MEDKIT:
            self.health = self.get_max_health()


    def switch_fire_mode(self):
        self.fire_mode = FireMode.FULL_AUTO if self.fire_mode != FireMode.FULL_AUTO else FireMode.SEMI_AUTO

    def toggle_ui(self, ui_type: PlayerUI):
        # Stop shooting when toggling UI
        self.shooting = False

        # Set new UI or close if already open
        self.open_ui = None if self.open_ui == ui_type else ui_type

    # noinspection PyMethodMayBeStatic
    def get_fire_rate(self) -> float:
        return 0.095

    # noinspection PyMethodMayBeStatic
    def get_magazine_size(self) -> int:
        return 30

    # noinspection PyMethodMayBeStatic
    def get_max_battery_level(self) -> float:
        return 12.0

    # noinspection PyMethodMayBeStatic
    def get_speed(self) -> float:
        return player_speed

    # noinspection PyMethodMayBeStatic
    def get_battery_usage_rate(self) -> float:
        return 0.01

    # noinspection PyMethodMayBeStatic
    def get_filter_depletion_rate(self) -> float:
        return 0.02

    # noinspection PyMethodMayBeStatic
    def get_filter_depletion_damage(self) -> float:
        return 0.1

    # noinspection PyMethodMayBeStatic
    def get_max_health(self) -> float:
        return player_health

    def move(self, keys):
        if keys[g.K_w]:
            self.y -= self.get_speed()
        if keys[g.K_s]:
            self.y += self.get_speed()
        if keys[g.K_a]:
            self.x -= self.get_speed()
        if keys[g.K_d]:
            self.x += self.get_speed()

    def aim(self, mouse_pos):
        mx, my = mouse_pos

        dx = mx - self.x
        dy = my - self.y

        self.weapon_angle = math.degrees(math.atan2(dy, dx))

    def draw(self, screen):
        # Player Image
        player_image = images.PLAYER
        player_scale_factor = 1.5

        # Scale Player
        scaled_player = g.transform.scale(
            player_image, (
                int(player_image.get_width() * player_scale_factor),
                int(player_image.get_height() * player_scale_factor)
            )
        )

        flip = self.weapon_angle < -90 or self.weapon_angle > 90

        # Flip Player
        if flip:
            scaled_player = g.transform.flip(scaled_player, True, False)

        # Draw Player
        player_rect = scaled_player.get_rect(center=(self.x, self.y))
        screen.blit(scaled_player, player_rect)

        # Weapon Image
        weapon_image = images.WEAPON_AK_SHOOT if self.shooting else images.WEAPON_AK_IDLE
        weapon_scale_factor = 1.4

        # Scale Weapon
        scaled_weapon = g.transform.scale(
            weapon_image, (
                int(weapon_image.get_width() * weapon_scale_factor),
                int(weapon_image.get_height() * weapon_scale_factor)
            )
        )

        # Flip Weapon
        if flip:
            scaled_weapon = g.transform.flip(scaled_weapon, False, True)

        # Rotate Weapon
        scaled_weapon = g.transform.rotate(scaled_weapon, -self.weapon_angle)

        # Draw Weapon
        weapon_rect = scaled_weapon.get_rect(center=(self.x, self.y))
        screen.blit(scaled_weapon, weapon_rect)

        # Draw Laser
        if self.weapon_laser:
            g.draw.line(
                screen,
                colors.RED,
                (
                    self.x,
                    self.y
                ),
                (
                    self.x + math.cos(math.radians(self.weapon_angle)) * 200,
                    self.y + math.sin(math.radians(self.weapon_angle)) * 200
                ),
                2
            )

    def get_rect(self):
        return g.Rect(self.x - 20, self.y - 20, 40, 40)