from car_game.car_game import CarGame
from car_game.road_enum import RoadEnum


def main():
    car_game = CarGame(screen_size=(1280, 720), car_speed=1, frame_rate=60,
                       road=RoadEnum.TWO, sensor_threshold=200, generate_train_data=True, nn_model=None,
                       probability_to_decide=0.95)

    car_game.start_neat()


if __name__ == '__main__':
    main()