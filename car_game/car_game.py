import pygame
from typing import Tuple
from car_game.road_generator import RoadGenerator
from car_game.road_enum import RoadEnum
from pygame import Rect
from pygame.sprite import Sprite
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
                 road: RoadEnum):
        pygame.init()
        self.car_speed = car_speed
        self.screen = pygame.display.set_mode(screen_size)
        self.screen_size = screen_size
        self.number_of_cars = number_of_cars
        self.road = road
        self.road_generator = RoadGenerator(screen_size)
        self.clock = pygame.time.Clock()
        self.frame_rate = frame_rate

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

            player_sprite = Sprite()
            player_sprite.rect = player_rect
            player_sprite.image = player_image_1_rot

            print(pygame.sprite.collide_mask(map_sprite, player_sprite))

            # PAINT DISPLAY AND OBJECTS AND SET FRAMERATE

            self.screen.fill(GRAY)
            self.screen.blit(map_surface, map_sprite.rect)
            self.screen.blit(player_image_1_rot, player_rect)
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
