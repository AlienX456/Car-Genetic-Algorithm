import pygame
from typing import Tuple

from car_game.Car import Car
from car_game.CarFactory import CarFactory
from car_game.road_generator import RoadGenerator
from car_game.road_enum import RoadEnum
import pandas
import math
from datetime import datetime
from tensorflow.keras.models import Sequential
import numpy as np

# COLORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (139, 139, 139)
GREEN = (24, 107, 24, 255)
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

            self.screen.fill(GREEN)
            self.screen.blit(map_surface, map_surface.get_rect())

            # VALIDATE EVENTS

            rotate_result = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True

            was_left_key_pressed = False
            was_right_key_pressed = False
            if self.generate_train_data:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    rotate_result = 3
                    was_left_key_pressed = True
                if keys[pygame.K_RIGHT]:
                    rotate_result = -3
                    was_right_key_pressed = True

            car.rotate_car(rotate_result)

            # SET CAR NEW SPEED AND ANGLE

            speed_in_x, speed_in_y = self.__calculate_speed(car.angle)

            car.current_position = (car.current_position[0] + speed_in_x, car.current_position[1] + speed_in_y)

            car_rotated_surface, player_rect = self.get_car_rotated_surface(car)

            # DETECT COLLISION BETWEEN CAR AND GRASS

            sensor_collision_point_list = self.__get_sensor_collision_vectors(car)

            distance_from_collision_list = []
            for sensor_collision_point in sensor_collision_point_list:
                distance_from_collision_list.append(
                    self.get_euclidean_distance(car.current_position, sensor_collision_point)
                )

            if not self.generate_train_data:
                input_model = np.array(
                    [[distance_from_collision_list[0],
                      distance_from_collision_list[1],
                      distance_from_collision_list[2],
                      distance_from_collision_list[3],
                      distance_from_collision_list[4]]])
                prediction = self.nn_model.predict(input_model)
                print(prediction)
                if prediction[0][0] >= self.probability_to_decide:
                    rotate_result = 3
                elif prediction[0][1] >= self.probability_to_decide:
                    rotate_result = -3

            car.rotate_car(rotate_result)


            # GENERATE TRAIN DATA

            if self.generate_train_data:
                print(distance_from_collision_list)
                train_data_dict = {'i_sensor_1': distance_from_collision_list[0],
                                   'i_sensor_2': distance_from_collision_list[1],
                                   'i_sensor_3': distance_from_collision_list[2],
                                   'i_sensor_4': distance_from_collision_list[3],
                                   'i_sensor_5': distance_from_collision_list[4],
                                   'o_left': was_left_key_pressed,
                                   'o_right': was_right_key_pressed
                                   }
                train_data_df = pandas.concat([train_data_df, pandas.DataFrame([train_data_dict])], sort=False)


            # PAINT DISPLAY AND OBJECTS AND SET FRAMERATE
            self.screen.blit(car_rotated_surface, player_rect)
            for sensor_collision_point in sensor_collision_point_list:
                pygame.draw.line(self.screen, RED, car.current_position, sensor_collision_point, 10)
            pygame.display.flip()
            self.clock.tick(self.frame_rate)

        self.game_over = True
        if self.generate_train_data:
            train_data_df.to_csv(f'training_data_{datetime.now().strftime("%m-%d-%Y-%H-%M-%S")}.csv')
        pygame.quit()

    def __calculate_speed(self, angle) -> Tuple[float, float]:
        print(angle)
        speed_x = self.car_speed * math.sin(math.radians(angle))
        speed_y = self.car_speed * math.cos(math.radians(angle))
        return speed_x, speed_y

    def __rot_center(self, image, angle, x, y):
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=image.get_rect(center=(x, y)).center)
        return rotated_image, new_rect

    def __rot_from_side(self, image, angle, x, y):
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=image.get_rect(center=(x, y)).center)
        return rotated_image, new_rect

    def __get_sensor_collision_vectors(self, car: Car) -> [Tuple[int, int]]:
        sensor_collision_positions = {}
        for i in range(0, self.sensor_threshold):
            sensor_positions = car.calculate_sensors_positions_respect_world(i)
            for j in range(0, len(sensor_positions)):
                try:
                    color_at_pixel = pygame.surface.Surface.get_at(self.screen, sensor_positions[j])
                except Exception as e:
                    color_at_pixel = GREEN

                if (color_at_pixel == GREEN or i == self.sensor_threshold - 1) and not sensor_collision_positions.get(f'{j}'):
                    sensor_collision_positions[f'{j}'] = sensor_positions[j]

        return list(sensor_collision_positions.values())

    def get_car_rotated_surface(self, car: Car):
        return self.__rot_center(car.image_surface,
                                 car.angle,
                                 car.current_position[0],
                                 car.current_position[1]
                                 )

    @staticmethod
    def get_euclidean_distance(point_1: Tuple[float, float], point_2: Tuple[float, float]) -> float:
        square_x = math.pow((point_1[0] - point_2[0]), 2)
        square_y = math.pow((point_1[1] - point_2[1]), 2)
        return round(math.sqrt(square_x + square_y))
