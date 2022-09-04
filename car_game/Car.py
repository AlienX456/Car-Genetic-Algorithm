from typing import Tuple
from car_game.Sensor import Sensor

CAR_SPRITE_LOCATION = 'car_game/images/car.png'


class Car:

    def __init__(self, car_position: Tuple[int, int], angle: int, sensors_angle_list: [Sensor], image_surface):
        self.sensor_list = sensors_angle_list
        self.current_position = car_position
        self.angle = angle
        self.image_surface = image_surface

    def rotate_car(self, rotation_angle: int):
        new_angle = self.angle + rotation_angle
        if new_angle >= 360:
            new_angle -= 360
        self.angle = new_angle

    def calculate_sensors_positions_respect_world(self, distance_traveled_by_sensor) -> [Tuple[int, int]]:
        sensor_positions = []
        for sensor in self.sensor_list:
            sensor_positions.append(sensor.calculate_sensor_position_respect_world(
                self.current_position,
                self.angle,
                distance_traveled_by_sensor
            ))
        return sensor_positions
