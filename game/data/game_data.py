import random
import time

import pygame as g

import game.game as manager
import game.ui.screen as s
from game.data.bullet import Bullet
from game.data.enemy import EnemyType, Enemy
from game.data.game_state import GameState
from game.data.item import Item
from game.data.player import Player, PlayerUI
from game.data.weapon import FireMode


def random_enemy_type() -> EnemyType:
    all_enemies = list(EnemyType)
    weights = [enemy_type.get_rarity() for enemy_type in all_enemies]
    return random.choices(all_enemies, weights=weights, k=1)[0]


class GameData:
    def __init__(self):
        self.score = 0.0
        self.player = Player()
        self.bullets = []
        self.enemies = []
        self.next_enemy_spawn = self.get_enemy_spawn_rate()

    # noinspection PyMethodMayBeStatic
    def get_enemy_spawn_rate(self):
        # TODO: Spawn more enemies depending on score
        return random.randint(2, 3)

    def add_score(self, value: float):
        self.score += value

    def spawn_enemy(self, enemy_type: EnemyType) -> Enemy:
        side = random.randint(0, 3)

        if side == 0:  # TOP
            x = random.randint(0, s.width)
            y = 0 - enemy_type.get_size()
        elif side == 1:  # RIGHT
            x = s.width + enemy_type.get_size()
            y = random.randint(0, s.height)
        elif side == 2:  # BOTTOM
            x = random.randint(0, s.width)
            y = s.height + enemy_type.get_size()
        else:  # LEFT
            x = 0 - enemy_type.get_size()
            y = random.randint(0, s.height)

        enemy = Enemy(x, y, enemy_type)

        self.enemies.append(enemy)

        return enemy

    def update_game(self):
        # Survival Score
        self.add_score(0.01)

        # Player Movement/Aiming
        self.player.move(g.key.get_pressed())
        self.player.aim(g.mouse.get_pos())

        # Player Filter Depletion
        if self.player.filter_level > 0:
            self.player.filter_level -= self.player.get_filter_depletion_rate()
        else:
            self.player.health -= self.player.get_filter_depletion_damage()

        current_time = time.time()

        # Handle Player Shooting
        if self.player.magazine > 0 and self.player.shooting:
            if self.player.fire_mode == FireMode.SEMI_AUTO:
                self.player.shooting = False

            if current_time - self.player.last_shot_time >= self.player.get_fire_rate():
                spread = 20

                if self.player.weapon_laser:
                    if self.player.fire_mode == FireMode.FULL_AUTO:
                        spread -= 10
                    elif self.player.fire_mode == FireMode.SEMI_AUTO:
                        spread -= 15

                self.bullets.append(Bullet(self.player.x, self.player.y, self.player.weapon_angle, spread))
                self.player.magazine -= 1
                self.player.last_shot_time = current_time

        # Reset Shooting State
        if self.player.magazine <= 0 and self.player.shooting:
            self.player.shooting = False

        # Laser Battery Usage
        if self.player.weapon_laser:
            if self.player.battery_level <= 6.0:
                self.player.weapon_laser = False
            else:
                self.player.battery_level = max(5.0, self.player.battery_level - self.player.get_battery_usage_rate())

        # Spawn Enemies
        self.next_enemy_spawn -= manager.clock.tick(manager.frames_per_second) / 1000
        if self.next_enemy_spawn <= 0:
            self.spawn_enemy(random_enemy_type())
            self.next_enemy_spawn = self.get_enemy_spawn_rate()

        # Update Bullets
        for bullet in self.bullets:
            bullet.update()

            # Damage hit enemy
            for enemy in self.enemies:
                if bullet.get_rect().colliderect(enemy.get_rect()):
                    enemy.take_damage(bullet.damage)
                    self.bullets.remove(bullet)

            # Remove invisible bullets
            if bullet.x < -20 or bullet.x > s.width + 20 or bullet.y < -20 or bullet.y > s.height + 20:
                self.bullets.remove(bullet)

        # Update Enemies
        for enemy in self.enemies:
            # Remove dead enemies
            if enemy.is_dead():
                self.add_score(enemy.enemy_type.get_reward())
                self.enemies.remove(enemy)
                continue

            # Move enemy
            enemy.move(self.player.x, self.player.y)

            if self.player.get_rect().colliderect(enemy.get_rect()):
                self.player.health -= enemy.enemy_type.get_damage()
                self.enemies.remove(enemy)

        if self.player.health <= 0:
            manager.set_state(GameState.DEAD)

    def handle_game_left_click(self, down: bool):
        if self.player.open_ui is None:
            self.player.shooting = down
        elif self.player.open_ui == PlayerUI.CHARGER and down:
            self.player.battery_level = min(self.player.get_max_battery_level(), self.player.battery_level + random.uniform(0.5, 1.2))
        elif self.player.open_ui == PlayerUI.INVENTORY and down:
            self.player.toggle_ui(self.player.open_ui)

    def handle_game_key(self, key: int):
        # Back to Main Menu
        if key == g.K_ESCAPE:
            if self.player.open_ui is not None:
                self.player.toggle_ui(self.player.open_ui)
            else:
                manager.set_state(GameState.DEAD)

        # Use Filter
        if key == g.K_t:
            self.player.use_item(Item.FILTER)

        # Use MedKit
        if key == g.K_h:
            self.player.use_item(Item.MEDKIT)

        # Toggle Laser
        if key == g.K_l:
            if self.player.battery_level > 6.0:
                self.player.weapon_laser = not self.player.weapon_laser

        # Reload Weapon
        if key == g.K_r:
            self.player.magazine = self.player.get_magazine_size()

        # Switch Fire Mode
        if key == g.K_x:
            self.player.switch_fire_mode()

        # Open Inventory UI
        if key == g.K_e:
            self.player.toggle_ui(PlayerUI.INVENTORY)

        # Open Charger UI
        if key == g.K_c:
            self.player.toggle_ui(PlayerUI.CHARGER)
