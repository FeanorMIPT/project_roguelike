import pytest
from constants import TILE_SIZE
import pygame
from chest import Chest
import config


class DummyPlayer:
    def __init__(self):
        self.x = 5 * TILE_SIZE
        self.y = 5 * TILE_SIZE
        self.coins = 1
        self.health = 5
        self.energy = 100


def test_is_near():
    chest = Chest(5, 5)
    player = DummyPlayer()
    assert chest.is_near(player)


def test_interact_coin_chest():
    config.earned_coins = 1
    player = DummyPlayer()
    chest = Chest(5, 5, "C")
    chest.interact(player)
    assert chest.opened
    assert player.health == 6
    assert player.coins == 0
    assert player.energy == 100
