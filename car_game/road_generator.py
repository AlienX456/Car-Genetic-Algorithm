from typing import Tuple
from car_game.road_enum import RoadEnum
import pygame
from pygame import Surface

ROAD_ONE_LOCATION = 'car_game/images/road_1.png'


class RoadGenerator:

    def __init__(self, surface_size: Tuple[int, int]):
        self.surface_width = surface_size[0]
        self.surface_height = surface_size[1]

    def get_road_image(self, number_of_road: RoadEnum) -> Surface:
        if number_of_road == RoadEnum.ONE:
            return pygame.image.load(ROAD_ONE_LOCATION)

    def get_road_initial_position(self, number_of_road: RoadEnum) -> [int, int]:
        if number_of_road == RoadEnum.ONE:
            return self.surface_width / 2, self.surface_height * 0.1
