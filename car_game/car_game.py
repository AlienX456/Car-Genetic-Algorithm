import pygame
from typing import Tuple
from car_game.road_generator import RoadGenerator
from car_game.road_enum import RoadEnum
from pygame import Rect
from pygame.sprite import Sprite
from pygame import Surface
import pandas
import math
from datetime import datetime
from tensorflow.keras.models import Sequential
import numpy as np

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
                 road: RoadEnum, sensor_threshold: int, generate_train_data, nn_model: Sequential):
        pygame.init()
        self.car_speed = car_speed
        self.screen = pygame.display.set_mode(screen_size)
        self.screen_size = screen_size
        self.road = road
        self.road_generator = RoadGenerator(screen_size)
        self.clock = pygame.time.Clock()
        self.frame_rate = frame_rate
        self.sensor_threshold = sensor_threshold
        self.distance_sensor_1 = -1
        self.distance_sensor_2 = -1
        self.distance_sensor_3 = -1
        self.generate_train_data = generate_train_data
        self.nn_model = nn_model
        self.game_over = False

    def start_game(self):

        exit_game = False

        car_current_position_x, car_current_position_y = self.road_generator.get_road_initial_position(self.road)
        current_angle = 0

        image = pygame.image.load(CAR_SPRITE_LOCATION)
        player_image_rotated = pygame.transform.scale(image, (self.screen_size[0] * 0.0625, self.screen_size[1] * 0.05))
        player_image_1 = pygame.transform.rotate(player_image_rotated, -180)

        map_surface = self.road_generator.get_road_image(self.road)

        train_data_df = pandas.DataFrame(columns=['i_sensor_1', 'i_sensor_2', 'i_sensor_3', 'o_left', 'o_right'])

        while not exit_game:

            was_left_key_pressed = False
            was_right_key_pressed = False

            # VALIDATE EVENTS

            rotate_result = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True
                if self.generate_train_data:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_LEFT:
                            was_left_key_pressed = True
                            rotate_result = 5
                        if event.key == pygame.K_RIGHT:
                            was_right_key_pressed = True
                            rotate_result = -5

            if not self.generate_train_data:
                input_model = np.array(
                    [[self.distance_sensor_1, self.distance_sensor_2, self.distance_sensor_3]])
                prediction = self.nn_model.predict(input_model)
                if prediction[0][0] >= 0.80:
                    print('left')
                    rotate_result = 5
                elif prediction[0][1] >= 0.80:
                    print('right')
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

            sensor_surface_vector_0, surface_rect_vector_0, self.distance_sensor_1 = \
                self.__get_sensor_collision_vector(
                (car_current_position_x, car_current_position_y), current_angle, map_sprite)

            sensor_surface_vector_middle, surface_rect_vector_middle, self.distance_sensor_2 = \
                self.__get_sensor_collision_vector(
                (car_current_position_x, car_current_position_y), current_angle+MIDDLE_SENSOR_ANGLE, map_sprite)

            sensor_surface_vector_minus_middle, surface_rect_vector_minus_middle, self.distance_sensor_3 = \
                self.__get_sensor_collision_vector(
                (car_current_position_x, car_current_position_y), current_angle-MIDDLE_SENSOR_ANGLE, map_sprite)

            # GENERATE TRAIN DATA

            if self.generate_train_data:
                train_data_dict = {'i_sensor_1': self.distance_sensor_1,
                                   'i_sensor_2': self.distance_sensor_2,
                                   'i_sensor_3': self.distance_sensor_3,
                                   'o_left': was_left_key_pressed,
                                   'o_right': was_right_key_pressed
                                   }
                train_data_df = pandas.concat([train_data_df, pandas.DataFrame([train_data_dict])], sort=False)


            # PAINT DISPLAY AND OBJECTS AND SET FRAMERATE

            self.screen.fill(GRAY)
            self.screen.blit(map_surface, map_sprite.rect)
            self.screen.blit(player_image_1_rot, player_rect)
            self.screen.blit(sensor_surface_vector_0, surface_rect_vector_0)
            self.screen.blit(sensor_surface_vector_middle, surface_rect_vector_middle)
            self.screen.blit(sensor_surface_vector_minus_middle, surface_rect_vector_minus_middle)
            pygame.display.flip()
            self.clock.tick(self.frame_rate)

        self.game_over = True
        if self.generate_train_data:
            train_data_df.to_csv(f'training_data_{datetime.now().strftime("%m-%d-%Y-%H-%M-%S")}.csv')
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
