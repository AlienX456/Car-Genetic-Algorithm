import pygame
from typing import Tuple
from car_game.road_generator import RoadGenerator
from car_game.road_enum import RoadEnum
from pygame import Rect
from car_game.pygame_shapes.arc import Arc

# COLORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (139, 139, 139)
GREEN = (24, 107, 24)


class CarGame:

    def __init__(self, screen_size: Tuple[int, int], car_speed: int,
                 number_of_cars: int, frame_rate: int,
                 road: RoadEnum, road_width):
        pygame.init()
        self.car_speed = car_speed
        self.screen = pygame.display.set_mode(screen_size)
        self.number_of_cars = number_of_cars
        self.road = road
        self.road_generator = RoadGenerator(screen_size, road_width)
        self.clock = pygame.time.Clock()
        self.frame_rate = frame_rate

    def start_game(self):

        exit_game = False

        while not exit_game:

            # DRAW MAP
            self.screen.fill(GREEN)
            self.__draw_road()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True

            pygame.display.flip()
            self.clock.tick(self.frame_rate)

        pygame.quit()

    def __draw_road(self):

        shapes = self.road_generator.get_road_shapes(self.road)

        for shape in shapes:

            if isinstance(shape, Rect):
                pass
            elif isinstance(shape, Arc):
                pygame.draw.arc(self.screen, GRAY, shape.rect, shape.start_angle, shape.stop_angle, shape.arc_width)

