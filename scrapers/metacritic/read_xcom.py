import ast
import sys


def process_game_list(game_list, prefix=None):
    game_list = ast.literal_eval(game_list)
    game_list = [game for game in game_list]
    return game_list


if __name__ == "__main__":
    # Read the xcom_value argument
    xcom_value = sys.argv[1]

    # Call the read_xcom function with the provided value
    x = process_game_list(xcom_value)
    print(x[:20])
