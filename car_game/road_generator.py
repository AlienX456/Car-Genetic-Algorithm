from typing import Tuple
from car_game.road_enum import RoadEnum
import pygame
from pygame import Surface

ROAD_ONE_LOCATION = 'car_game/images/road_1.png'
ROAD_TWO_LOCATION = 'car_game/images/road_2.png'
ROAD_THREE_LOCATION = 'car_game/images/road_3.png'
ROAD_FOUR_LOCATION = 'car_game/images/road_4.png'


class RoadGenerator:

    def __init__(self, surface_size: Tuple[int, int]):
        self.surface_width = surface_size[0]
        self.surface_height = surface_size[1]

    def get_road_image(self, number_of_road: RoadEnum) -> Surface:
        if number_of_road == RoadEnum.ONE:
            return pygame.image.load(ROAD_ONE_LOCATION)
        elif number_of_road == RoadEnum.TWO:
            return pygame.image.load(ROAD_TWO_LOCATION)
        elif number_of_road == RoadEnum.THREE:
            return pygame.image.load(ROAD_THREE_LOCATION)
        elif number_of_road == RoadEnum.FOUR:
            return pygame.image.load(ROAD_FOUR_LOCATION)

    def get_road_initial_position(self, number_of_road: RoadEnum) -> [int, int]:
        if number_of_road == RoadEnum.ONE:
            return self.surface_width / 2 - 150, self.surface_height * 0.10
        if number_of_road == RoadEnum.TWO:
            return self.surface_width / 2 - 150, self.surface_height * 0.04
        if number_of_road == RoadEnum.THREE:
            return self.surface_width / 2 - 100, self.surface_height * 0.90
        if number_of_road == RoadEnum.FOUR:
            return self.surface_width / 2 - 650, self.surface_height * 0.12

