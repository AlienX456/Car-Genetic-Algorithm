import pygame
from typing import Tuple

from car_game.Car import Car
from car_game.CarFactory import CarFactory
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
import os

# COLORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (139, 139, 139)
GREEN = (24, 107, 24)
RED = (240, 34, 34)
SENSOR_LINE_WIDTH = 5
MIDDLE_SENSOR_ANGLE = 60
RECT_SENSOR_ANGLE = 90
CAR_SPRITE_LOCATION = 'car_game/images/car.png'


class CarGame:

    def __init__(self, screen_size: Tuple[int, int], car_speed: int, frame_rate: int,
                 road: RoadEnum, sensor_threshold: int, generate_train_data, nn_model: Sequential,
                 probability_to_decide: float):
        pygame.init()
        self.car_speed = car_speed
        self.screen = pygame.display.set_mode(screen_size)
        self.screen_size = screen_size
        self.road = road
        self.road_generator = RoadGenerator(screen_size)
        self.clock = pygame.time.Clock()
        self.frame_rate = frame_rate
        self.sensor_threshold = sensor_threshold
        self.generate_train_data = generate_train_data
        self.nn_model = nn_model
        self.game_over = False
        self.probability_to_decide = probability_to_decide

    def start_game(self):

        exit_game = False

        image = pygame.image.load(CAR_SPRITE_LOCATION)
        car_image = pygame.transform.scale(image, (self.screen_size[0] * 0.03, self.screen_size[1] * 0.10))
        car = CarFactory.build_five_sensor_car(
            position=self.road_generator.get_road_initial_position(self.road),
            angle=90,
            image_surface=car_image
        )

        map_surface = self.road_generator.get_road_image(self.road)

        train_data_df = pandas.DataFrame(columns=['i_sensor_1', 'i_sensor_2', 'i_sensor_3', 'o_left', 'o_right'])

        while not exit_game:

            # VALIDATE EVENTS

            rotate_result = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True

            if self.generate_train_data:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    rotate_result = 5
                if keys[pygame.K_RIGHT]:
                    rotate_result = -5

            # if not self.generate_train_data:
            #     input_model = np.array(
            #         [[self.distance_sensor_1, self.distance_sensor_2, self.distance_sensor_3, self.distance_sensor_4,
            #           self.distance_sensor_5]])
            #     prediction = self.nn_model.predict(input_model)
            #     if prediction[0][0] >= self.probability_to_decide:
            #         rotate_result = 5
            #     elif prediction[0][1] >= self.probability_to_decide:
            #         rotate_result = -5

            car.rotate_car(rotate_result)

            # SET CAR NEW SPEED AND ANGLE

            speed_in_x, speed_in_y = self.__calculate_speed(car.angle)

            car.current_position = (car.current_position[0]+speed_in_x, car.current_position[1] + speed_in_y)

            car_rotated_surface, player_rect = self.get_car_rotated_surface(car)

            # DETECT COLLISION BETWEEN CAR AND GRASS

            # COLLISION VECTORS

            # sensor_surface_vector_0, surface_rect_vector_0, self.distance_sensor_1, collision_point_1 = \
            #     self.__get_sensor_collision_vector(
            #         (car_current_position_x, car_current_position_y), current_angle, map_sprite,
            #         self.sensor_threshold * 3)
            #
            # sensor_surface_vector_middle, surface_rect_vector_middle, self.distance_sensor_2, collision_point_2 = \
            #     self.__get_sensor_collision_vector(
            #         (car_current_position_x, car_current_position_y), current_angle + MIDDLE_SENSOR_ANGLE, map_sprite,
            #         self.sensor_threshold)
            #
            # sensor_surface_vector_minus_middle, surface_rect_vector_minus_middle, self.distance_sensor_3, collision_point_3 = \
            #     self.__get_sensor_collision_vector(
            #         (car_current_position_x, car_current_position_y), current_angle - MIDDLE_SENSOR_ANGLE, map_sprite,
            #         self.sensor_threshold)
            #
            # sensor_surface_vector_rect, surface_rect_vector_rect, self.distance_sensor_4, collision_point_4 = \
            #     self.__get_sensor_collision_vector(
            #         (car_current_position_x, car_current_position_y), current_angle + RECT_SENSOR_ANGLE, map_sprite,
            #         self.sensor_threshold)
            #
            # sensor_surface_vector_minus_rect, surface_rect_vector_minus_rect, self.distance_sensor_5, collision_point_5 = \
            #     self.__get_sensor_collision_vector(
            #         (car_current_position_x, car_current_position_y), current_angle - RECT_SENSOR_ANGLE, map_sprite,
            #         self.sensor_threshold)

            # GENERATE TRAIN DATA

            # if self.generate_train_data:
            #     train_data_dict = {'i_sensor_1': self.distance_sensor_1,
            #                        'i_sensor_2': self.distance_sensor_2,
            #                        'i_sensor_3': self.distance_sensor_3,
            #                        'i_sensor_4': self.distance_sensor_4,
            #                        'i_sensor_5': self.distance_sensor_5,
            #                        'o_left': was_left_key_pressed,
            #                        'o_right': was_right_key_pressed
            #                        }
            #     train_data_df = pandas.concat([train_data_df, pandas.DataFrame([train_data_dict])], sort=False)
            #
            # # PRINT SENSOR
            # os.system('clear')
            # print({'i_sensor_1': self.distance_sensor_1,
            #        'i_sensor_2': self.distance_sensor_2,
            #        'i_sensor_3': self.distance_sensor_3,
            #        'i_sensor_4': self.distance_sensor_4,
            #        'i_sensor_5': self.distance_sensor_5,
            #        })

            # PAINT DISPLAY AND OBJECTS AND SET FRAMERATE

            self.screen.fill(GRAY)
            self.screen.blit(map_surface, map_surface.get_rect())
            self.screen.blit(car_rotated_surface, player_rect)
            # self.screen.blit(sensor_surface_vector_0, surface_rect_vector_0)
            # self.screen.blit(sensor_surface_vector_middle, surface_rect_vector_middle)
            # self.screen.blit(sensor_surface_vector_minus_middle, surface_rect_vector_minus_middle)
            # self.screen.blit(sensor_surface_vector_minus_rect, surface_rect_vector_minus_rect)
            # self.screen.blit(sensor_surface_vector_rect, surface_rect_vector_rect)
            # pygame.draw.circle(self.screen, BLACK, collision_point_1, 10) if collision_point_1 else ''
            # pygame.draw.circle(self.screen, BLACK, collision_point_2, 10) if collision_point_2 else ''
            # pygame.draw.circle(self.screen, BLACK, collision_point_3, 10) if collision_point_3 else ''
            # pygame.draw.circle(self.screen, BLACK, collision_point_4, 10) if collision_point_4 else ''
            # pygame.draw.circle(self.screen, BLACK, collision_point_5, 10) if collision_point_5 else ''
            pygame.display.flip()
            self.clock.tick(self.frame_rate)

        self.game_over = True
        if self.generate_train_data:
            train_data_df.to_csv(f'training_data_{datetime.now().strftime("%m-%d-%Y-%H-%M-%S")}.csv')
        pygame.quit()

    def __calculate_speed(self, angle) -> Tuple[int, int]:
        speed_x = round(self.car_speed * math.sin(math.radians(angle)))
        speed_y = round(self.car_speed * math.cos(math.radians(angle)))
        return speed_x, speed_y

    def __rot_center(self, image, angle, x, y):
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=image.get_rect(center=(x, y)).center)
        return rotated_image, new_rect

    def __rot_from_side(self, image, angle, x, y):
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=image.get_rect(center=(x, y)).center)
        return rotated_image, new_rect

    def __get_sensor_collision_vectors(self, car_position: [int, int], car_sensor_angle: [int], map_sprite: Sprite,
                                       sensor_threshold: int) \
            -> Tuple[Surface, Rect, int, Tuple[int, int]]:
        pass

    def get_car_rotated_surface(self, car: Car):
        return self.__rot_center(car.image_surface,
                                 car.angle,
                                 car.current_position[0],
                                 car.current_position[1]
                                 )

    @staticmethod
    def get_euclidean_distance(point_1: Tuple[int, int], point_2: Tuple[int, int]) -> int:
        square_x = math.pow((point_1[0] - point_2[0]), 2)
        square_y = math.pow((point_1[1] - point_2[1]), 2)
        return round(math.sqrt(square_x + square_y))
