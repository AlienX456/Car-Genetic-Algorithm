from car_game.car_game import CarGame
from car_game.road_enum import RoadEnum
import keras


def main():
    generate_train_data = False

    if generate_train_data:
        car_game = CarGame(screen_size=(1600, 1200), car_speed=3, frame_rate=60,
                           road=RoadEnum.ONE, sensor_threshold=600, generate_train_data=generate_train_data, nn_model=None)
    else:
        model = keras.models.load_model('car_game_model.h5')
        car_game = CarGame(screen_size=(1600, 1200), car_speed=3, frame_rate=30,
                           road=RoadEnum.ONE, sensor_threshold=600, generate_train_data=False, nn_model=model)

    car_game.start_game()


if __name__ == '__main__':
    main()