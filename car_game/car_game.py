import pygame
from typing import Tuple
from car_game.road_generator import RoadGenerator
from car_game.road_enum import RoadEnum
from pygame import Rect
from car_game.pygame_shapes.arc import Arc
import math

# COLORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (139, 139, 139)
GREEN = (24, 107, 24)
CAR_SPRITE_LOCATION = 'car_game/images/car.png'


class CarGame:

    def __init__(self, screen_size: Tuple[int, int], car_speed: int,
                 number_of_cars: int, frame_rate: int,
                 road: RoadEnum, road_width):
        pygame.init()
        self.car_speed = car_speed
        self.screen = pygame.display.set_mode(screen_size)
        self.screen_size = screen_size
        self.number_of_cars = number_of_cars
        self.road = road
        self.road_generator = RoadGenerator(screen_size, road_width)
        self.clock = pygame.time.Clock()
        self.frame_rate = frame_rate
        image = pygame.image.load(CAR_SPRITE_LOCATION)
        player_image_rotated = pygame.transform.scale(image, (screen_size[0] * 0.0625, screen_size[1] * 0.05))
        self.player_image = pygame.transform.rotate(player_image_rotated, -180)

    def start_game(self):

        exit_game = False

        car_current_position_x = self.screen_size[0]/2
        car_current_position_y = self.screen_size[1]/2

        while not exit_game:

            # DRAW MAP
            self.screen.fill(GREEN)
            self.__draw_road()

            # DRAW CAR AND ANGLE
            rotate_result = 0
            speed_in_x, speed_in_y = self.__calculate_speed(rotate_result)
            print(f'{speed_in_x} {speed_in_y}')
            car_current_position_x += speed_in_x
            car_current_position_y += speed_in_y

            self.player_image = pygame.transform.rotate(self.player_image, rotate_result)
            self.screen.blit(self.player_image, (car_current_position_x, car_current_position_y))





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

    def __calculate_speed(self, angle) -> Tuple[int, int]:
        speed_x = 0 if math.cos(angle) == 0 else round(self.car_speed / math.cos(angle))
        speed_y = 0 if math.sin(angle) == 0 else round(self.car_speed / math.sin(angle))
        return speed_x, speed_y
