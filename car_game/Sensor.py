from typing import Tuple
import math


class Sensor:

    def __init__(self, angle: [int]):
        self.angle = angle

    def calculate_sensor_position_respect_world(self, car_current_position: Tuple[int, int],
                                                car_current_angle: int,
                                                distance_traveled_by_sensor: int) -> Tuple[int, int]:
        """ Returns the position of the sensor according to the car position
        and the distance traveled by the sensor and its angle """

        if car_current_angle > 360:
            raise Exception('Angle not allowed')

        sensor_angle_respect_world = car_current_angle + self.angle

        # Respect world is calculated respect to the screen or map
        if sensor_angle_respect_world > 360:
            sensor_angle_respect_world -= 360

        # Respect car means that the position of sensor is calculated as the car were on position (0,0)
        y_respect_car = distance_traveled_by_sensor * math.sin(math.radians(sensor_angle_respect_world))
        x_respect_car = distance_traveled_by_sensor * math.sin(math.radians(sensor_angle_respect_world))

        if sensor_angle_respect_world >= 90:
            x_respect_world = car_current_position[0] - x_respect_car
        else:
            x_respect_world = car_current_position[0] + x_respect_car

        if 45 <= sensor_angle_respect_world <= 180:
            y_respect_world = car_current_position[1] - y_respect_car
        else:
            y_respect_world = car_current_position[1] + y_respect_car

        return int(x_respect_world), int(y_respect_world)

