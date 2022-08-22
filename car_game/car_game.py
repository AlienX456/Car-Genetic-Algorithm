import pygame
from typing import Tuple
from car_game.road_generator import RoadGenerator
from car_game.road_enum import RoadEnum
from pygame import Rect
from pygame.sprite import Sprite
from pygame import Surface
import math

# COLORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (139, 139, 139)
GREEN = (24, 107, 24)
RED = (240, 34, 34)
SENSOR_LINE_WIDTH = 5
CAR_SPRITE_LOCATION = 'car_game/images/car.png'
MIDDLE_SENSOR_ANGLE = 60


class CarGame:

    def __init__(self, screen_size: Tuple[int, int], car_speed: int, frame_rate: int,
                 road: RoadEnum, sensor_threshold: int):
        pygame.init()
        self.car_speed = car_speed
        self.screen = pygame.display.set_mode(screen_size)
        self.screen_size = screen_size
        self.road = road
        self.road_generator = RoadGenerator(screen_size)
        self.clock = pygame.time.Clock()
        self.frame_rate = frame_rate
        self.sensor_threshold = sensor_threshold

    def start_game(self):

        exit_game = False

        car_current_position_x, car_current_position_y = self.road_generator.get_road_initial_position(self.road)
        current_angle = 0

        image = pygame.image.load(CAR_SPRITE_LOCATION)
        player_image_rotated = pygame.transform.scale(image, (self.screen_size[0] * 0.0625, self.screen_size[1] * 0.05))
        player_image_1 = pygame.transform.rotate(player_image_rotated, -180)

        map_surface = self.road_generator.get_road_image(self.road)

        while not exit_game:

            # VALIDATE EVENTS

            rotate_result = 0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        rotate_result = 5
                    if event.key == pygame.K_RIGHT:
                        rotate_result = -5
            current_angle += rotate_result

            # SET CAR NEW SPEED AND ANGLE

            speed_in_x, speed_in_y = self.__calculate_speed(current_angle)
            # print(f'{current_angle} {speed_in_x} {speed_in_y}')
            car_current_position_x += speed_in_x
            car_current_position_y -= speed_in_y

            player_image_1_rot, player_rect = self.__rot_center(player_image_1,
                                                                current_angle,
                                                                car_current_position_x,
                                                                car_current_position_y)

            # DETECT COLLISION BETWEEN CAR AND GRASS

            map_sprite = Sprite()
            map_sprite.rect = Rect(0, 0, self.screen_size[0], self.screen_size[1])
            map_sprite.image = map_surface

            # COLLISION VECTORS

            sensor_surface_vector_0, surface_rect_vector_0, collision_distance_vector_0 = \
                self.__get_sensor_collision_vector(
                (car_current_position_x, car_current_position_y), current_angle, map_sprite)

            print(f'sensor collision {collision_distance_vector_0}')

            sensor_surface_vector_middle, surface_rect_vector_middle, collision_distance_vector_middle = \
                self.__get_sensor_collision_vector(
                (car_current_position_x, car_current_position_y), current_angle+MIDDLE_SENSOR_ANGLE, map_sprite)

            sensor_surface_vector_minus_middle, surface_rect_vector_minus_middle, collision_distance_vector_minus_middle = \
                self.__get_sensor_collision_vector(
                (car_current_position_x, car_current_position_y), current_angle-MIDDLE_SENSOR_ANGLE, map_sprite)

            # PAINT DISPLAY AND OBJECTS AND SET FRAMERATE

            self.screen.fill(GRAY)
            self.screen.blit(map_surface, map_sprite.rect)
            self.screen.blit(player_image_1_rot, player_rect)
            self.screen.blit(sensor_surface_vector_0, surface_rect_vector_0)
            self.screen.blit(sensor_surface_vector_middle, surface_rect_vector_middle)
            self.screen.blit(sensor_surface_vector_minus_middle, surface_rect_vector_minus_middle)
            pygame.display.flip()
            self.clock.tick(self.frame_rate)

        pygame.quit()

    def __calculate_speed(self, angle) -> Tuple[int, int]:
        speed_x = 0 if math.cos(angle) == 0 else self.car_speed * math.cos(math.radians(angle))
        speed_y = 0 if math.sin(angle) == 0 else self.car_speed * math.sin(math.radians(angle))
        return speed_x, speed_y

    def __rot_center(self, image, angle, x, y):
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=image.get_rect(center=(x, y)).center)
        return rotated_image, new_rect

    def __rot_from_side(self, image, angle, x, y):
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=image.get_rect(center=(x, y)).center)
        return rotated_image, new_rect

    def __get_sensor_collision_vector(self, car_position: [int, int], car_sensor_angle: int, map_sprite: Sprite) \
            -> Tuple[Surface, Rect, int]:
        sensor_surface = Surface((self.sensor_threshold, self.sensor_threshold), pygame.SRCALPHA)
        # sensor_surface.fill(BLACK)
        pygame.draw.line(sensor_surface, RED,
                         (self.sensor_threshold/2, self.sensor_threshold/2),
                         (self.sensor_threshold, self.sensor_threshold/2),
                         SENSOR_LINE_WIDTH)


        rotated_image = pygame.transform.rotate(sensor_surface, car_sensor_angle)
        rotated_rect = rotated_image.get_rect(
            center=rotated_image.get_rect(center=(car_position[0], car_position[1])).center)

        sensor_sprite = Sprite()
        sensor_sprite.rect = rotated_rect
        sensor_sprite.image = rotated_image

        collision_point = pygame.sprite.collide_mask(map_sprite, sensor_sprite)

        distance_from_collision = -1

        if collision_point:
            distance_from_collision = CarGame.get_euclidean_distance(
               collision_point,
               (car_position[0], car_position[1])
            )
        return rotated_image, rotated_rect, distance_from_collision

    @staticmethod
    def get_euclidean_distance(point_1: Tuple[int, int], point_2: Tuple[int, int]) -> int:
        square_x = math.pow((point_1[0] - point_2[0]), 2)
        square_y = math.pow((point_1[1] - point_2[1]), 2)
        return round(math.sqrt(square_x+square_y))
