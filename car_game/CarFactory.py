from typing import Tuple
import pygame
from car_game.Car import Car
from car_game.Sensor import Sensor

FIVE_SENSOR_CAR_ANGLES = [90, 50, 0, -50, -90]


class CarFactory:

    @staticmethod
    def build_five_sensor_car(position: Tuple[int, int], angle: int, image_surface, name) -> Car:
        sensor_list = [
            Sensor(FIVE_SENSOR_CAR_ANGLES[0]),
            Sensor(FIVE_SENSOR_CAR_ANGLES[1]),
            Sensor(FIVE_SENSOR_CAR_ANGLES[2]),
            Sensor(FIVE_SENSOR_CAR_ANGLES[3]),
            Sensor(FIVE_SENSOR_CAR_ANGLES[4]),
        ]

        return Car(car_position=position,
                   angle=angle,
                   sensors_angle_list=sensor_list,
                   image_surface=image_surface,
                   name=name
                   )
