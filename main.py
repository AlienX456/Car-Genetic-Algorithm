from car_game.car_game import CarGame
from car_game.road_enum import RoadEnum


def main():
    car_game = CarGame(screen_size=(1600, 1200), car_speed=2,
                       number_of_cars=1, frame_rate=60,
                       road=RoadEnum.ONE, sensor_threshold=200)

    car_game.start_game()


if __name__ == '__main__':
    main()