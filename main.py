from car_game.car_game import CarGame
from car_game.road_enum import RoadEnum


def main():
    car_game = CarGame(screen_size=(1600, 1200), car_speed=5, frame_rate=60,
                       road=RoadEnum.ONE, sensor_threshold=600, generate_train_data=True, nn_model=None)

    car_game.start_game()


if __name__ == '__main__':
    main()