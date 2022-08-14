from typing import Tuple, Union
from pygame import Rect
from car_game.pygame_shapes.arc import Arc
from car_game.road_enum import RoadEnum
from math import pi


class RoadGenerator:

    def __init__(self, surface_size: Tuple[int, int], road_width: int):
        self.surface_width = surface_size[0]
        self.surface_height = surface_size[1]
        self.road_width = road_width

    def get_road_shapes(self, number_of_road: RoadEnum) -> [Union[Rect, Arc]]:
        shapes_list = []
        if number_of_road == RoadEnum.ELLIPSE:
            shapes_list.append(Arc(0, 0, self.surface_width, self.surface_height, pi/2, pi, self.road_width))
            shapes_list.append(Arc(0, 0, self.surface_width, self.surface_height, 0, pi, self.road_width))
            shapes_list.append(Arc(0, 0, self.surface_width, self.surface_height, 3*pi/2, 2*pi, self.road_width))
            shapes_list.append(Arc(0, 0, self.surface_width, self.surface_height, pi, 2*pi, self.road_width))

        return shapes_list


