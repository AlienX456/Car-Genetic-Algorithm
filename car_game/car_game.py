import math
import sys
from typing import Tuple
import neat
import os
import pygame
from tensorflow.keras.models import Sequential

from car_game.Car import Car
from car_game.CarFactory import CarFactory
from car_game.road_enum import RoadEnum
from car_game.road_generator import RoadGenerator

pygame.init()
# COLORS
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (139, 139, 139)
GREEN = (24, 107, 24, 255)
RED = (240, 34, 34)
CAR_SPRITE_LOCATION = 'car_game/images/car.png'
FONT = pygame.font.Font('freesansbold.ttf', 20)


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

        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config.txt')
        config = neat.config.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path
        )

        self.pop = neat.Population(config)

    def start_neat(self):
        self.pop.run(self.__start_game, 50)

    def __start_game(self, genomes, config):

        exit_game = False

        image = pygame.image.load(CAR_SPRITE_LOCATION)
        car_image = pygame.transform.scale(image, (self.screen_size[0] * 0.03, self.screen_size[1] * 0.10))

        car_list = []
        ge = []
        nets = []

        for genome_id, genome in genomes:
            car_list.append(CarFactory.build_five_sensor_car(
                position=self.road_generator.get_road_initial_position(self.road),
                angle=90,
                image_surface=car_image
            ))
            ge.append(genome)
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            nets.append(net)
            genome.fitness = 0

        map_surface = self.road_generator.get_road_image(self.road)

        while not exit_game:

            self.screen.fill(GREEN)
            self.screen.blit(map_surface, map_surface.get_rect())

            # VALIDATE EVENTS

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            car_surface_list = []

            car_to_remove_list = []

            for i, car in enumerate(car_list):

                # SET CAR NEW SPEED AND ANGLE
                speed_in_x, speed_in_y = self.__calculate_speed(car.angle)

                car.current_position = (car.current_position[0] + speed_in_x, car.current_position[1] + speed_in_y)

                # DETECT COLLISION BETWEEN CAR AND GRASS

                sensor_collision_point_list = self.__get_sensor_collision_vectors(car)

                distance_from_collision_list = []
                for sensor_collision_point in sensor_collision_point_list:
                    distance_from_collision_list.append(
                        self.get_euclidean_distance(car.current_position, sensor_collision_point)
                    )
                car.sensor_collision_point_list = sensor_collision_point_list
                car.distance_from_collision_list = distance_from_collision_list
                if list(filter(lambda x: x <= 1, distance_from_collision_list)):
                    car_to_remove_list.append(car)
                else:
                    car_surface_list.append(self.get_car_rotated_surface(car))
                    ge[i].fitness += 1

            for car_to_remove in car_to_remove_list:
                index = car_list.index(car_to_remove)
                car_list.pop(index)
                ge.pop(index)
                nets.pop(index)

            for i, car in enumerate(car_list):
                output = nets[i].activate((car.distance_from_collision_list[0],
                                           car.distance_from_collision_list[1],
                                           car.distance_from_collision_list[2],
                                           car.distance_from_collision_list[3],
                                           car.distance_from_collision_list[4]))

                rotate_result = 0
                if output[0] > 0.5:
                    rotate_result = 0.5
                elif output[1] > 0.5:
                    rotate_result = -0.5

                car.rotate_car(rotate_result)

            # PAINT DISPLAY AND OBJECTS AND SET FRAMERATE

            if len(car_list) == 0:
                exit_game = True

            for car_surface in car_surface_list:
                self.screen.blit(car_surface[0], car_surface[1])
            for car in car_list:
                for sensor_collision_point in car.sensor_collision_point_list:
                    pygame.draw.line(self.screen, RED, car.current_position, sensor_collision_point, 2)

            text_1 = FONT.render(f'Cars Alive:  {str(len(car_list))}', True, (0, 0, 0))
            text_2 = FONT.render(f'Generation:  {self.pop.generation + 1}', True, (0, 0, 0))
            self.screen.blit(text_1, (50, 480))
            self.screen.blit(text_2, (50, 500))
            pygame.display.flip()
            self.clock.tick(self.frame_rate)

    def __calculate_speed(self, angle) -> Tuple[float, float]:
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

                if (color_at_pixel == GREEN or i == self.sensor_threshold - 1) and not sensor_collision_positions.get(
                        f'{j}'):
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
