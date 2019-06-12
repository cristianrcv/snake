#!/usr/bin/python

# -*- coding: utf-8 -*-

# For better print formatting
from __future__ import print_function

# Imports
import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
from random import randint
from datetime import datetime
import logging

# CONFIGURABLE CONSTANTS
BOUNDS_ENABLED = False
BASE_SPEED = 5
NUM_PLAYERS = 4  # MAXIMUM: 4

# Key bindings
KEY_ESC = 27
KEY_SPACE = 32

KEY_W = 119
KEY_S = 115
KEY_D = 100
KEY_A = 97

KEY_I = 105
KEY_K = 107
KEY_L = 108
KEY_J = 106

KEY_NUM_8 = 56
KEY_NUM_5 = 53
KEY_NUM_6 = 54
KEY_NUM_4 = 52

KEYS_UP = [KEY_W, KEY_UP, KEY_I, KEY_NUM_8]
KEYS_DOWN = [KEY_S, KEY_DOWN, KEY_K, KEY_NUM_5]
KEYS_RIGHT = [KEY_D, KEY_RIGHT, KEY_L, KEY_NUM_6]
KEYS_LEFT = [KEY_A, KEY_LEFT, KEY_J, KEY_NUM_4]

# CONSTANTS
LEAST_SPEED = 600
TOP_SPEED = 30
INITIAL_SPEED = int(LEAST_SPEED / BASE_SPEED)

Y_SIZE = 40
X_SIZE = 100

CHAR_FOOD = '*'
CHAR_EMPTY = ' '
CHAR_SNAKE = '#'

COLOR_EMPTY = 1
VALID_COLORS = [209, 47, 227, 22]

MAX_SCORE_PER_FOOD = 100
SCORE_PER_KILL = 50

#
# Logger definition
#

logger = logging.getLogger("console")


#
# SECOND LEVEL HELPER METHODS
#


def build_keys_per_player(num_players):
    """
    Builds a dictionary containing the valid keys for each active player.

    :param num_players: Number of active players.
        + type: int
    :return: A dictionary containing a list of the valid keys for each active player.
        + type: dict<str, List<int>>
    """
    keys_per_player = {}
    for i in range(num_players):
        keys_per_player[str(i)] = [KEYS_UP[i], KEYS_DOWN[i], KEYS_RIGHT[i], KEYS_LEFT[i]]
    return keys_per_player


def build_colors_per_player(num_players):
    """
    Builds a list containing the color of each active player.

    :param num_players: Number of active players.
        + type: int
    :return: List containing the color assigned to each active player
        + List<int>
    """
    colors_per_player = []
    for i in range(num_players):
        colors_per_player.append(VALID_COLORS[i])
    return colors_per_player


def initial_key_random(player_id):
    """
    Selects a random initial direction key for the given player id.

    :param player_id: Player id.
        + type: int
    :return: A random initial direction key.
        + type: int
    """
    rand = randint(0, 3)
    if rand == 0:
        return KEYS_UP[player_id]
    elif rand == 1:
        return KEYS_DOWN[player_id]
    elif rand == 2:
        return KEYS_RIGHT[player_id]
    return KEYS_LEFT[player_id]


def random_position():
    """
    Returns a random position within the board.

    :return: A random valid position within the board
        + type: List<int,int>
    """
    return [randint(1, Y_SIZE - 2), randint(1, X_SIZE - 2)]


def initial_snake_random():
    """
    Returns a random position of a snake of size 3 within the board.

    :return: A random position of a snake of size 3 within the board.
        + List<List<int,int>, List<int,int>, List<int,int>>
    """
    snake_head = random_position()

    snake_body = snake_head
    snake_body[1] = snake_body[1] - 1
    if snake_body[1] < 0:
        snake_body[1] = X_SIZE - 2

    snake_tail = snake_body
    snake_tail[1] = snake_tail[1] - 1
    if snake_tail[1] < 0:
        snake_tail[1] = X_SIZE - 2

    snake = [snake_head, snake_body, snake_tail]
    return snake


def print_game_iteration(win, colors_per_player, scores, snakes):
    """
    Generates the window for the next game iteration

    :param win: Window screen.
        + type: curses.Window
    :param colors_per_player: List of assigned colors to each player
        + type: List<int>
    :param scores: Current scores
        + type: List<int>
    :param snakes: Snakes positions
        + type: List<List<List<int, int>>>
    :return: None
    """
    win.border(0)

    # Print Snake name
    # win.addstr(0, int(X_SIZE / 2), ' SNAKE ')  # 'SNAKE' strings

    # Print scores
    for player_id, score in enumerate(scores):
        msg = ' Player ' + str(player_id + 1) + " Score : " + str(score) + ' '
        if player_id / 2 == 0:
            posy = 0
        else:
            posy = Y_SIZE - 1
        if player_id % 2 == 0:
            posx = 2
        else:
            posx = int((3 * X_SIZE) / 5)

        win.addstr(posy, posx, msg, curses.color_pair(colors_per_player[player_id]))

    # Increase snake speed with its length
    longest_snake_len = max(len(snake) for snake in snakes)
    increase_speed = int(5 * (longest_snake_len / 5 + longest_snake_len / 10))
    speed = INITIAL_SPEED - increase_speed % (INITIAL_SPEED - TOP_SPEED)
    win.timeout(speed)


def process_event(win, keys_per_player):
    """
    Process the next event on the window and assigns it to the corresponding player

    :param win: Window screen.
        + type: curses.Window
    :param keys_per_player: Registered valid keys for each player
        + type: dict<str, List<int>>
    :return: Dictionary containing when entry per player that has registered an event, or global.
        + type: dict<str, int>
    """
    # Get event
    event = win.getch()

    # Only allow valid events
    events = {}
    if event == KEY_SPACE or event == KEY_ESC:
        # Register global event
        events["global"] = event
    else:
        # Register event to the corresponding player
        for player_id, player_keys in keys_per_player.items():
            if event in player_keys:
                events[player_id] = event

    return events


def process_events(win, keys_per_player):
    """
    Process the next NUM_PLAYERS events on the window and assigns them to the corresponding player

    :param win: Window screen.
        + type: curses.Window
    :param keys_per_player: Registered valid keys for each player
        + type: dict<str, List<int>>
    :return: Dictionary containing when entry per player that has registered an event, or global.
        + type: dict<str, int>
    """
    # Process 1 event
    # TODO: Maybe process more in the future?
    events = {}
    for _ in range(1):
        partial_events = process_event(win, keys_per_player)
        events.update(partial_events)

    return events


def wait_for_resume_game(win):
    """
    Waits until the game is resumed or ended.

    :param win: Window screen.
        + type: curses.Window
    :return: True if the game must end, False if the game must resume.
        + type: boolean
    """
    key = None
    while key != KEY_SPACE and key != KEY_ESC:
        key = win.getch()

    return key != KEY_SPACE


def print_char(win, pos, char, color):
    """
    Prints the given char at the given position using the given color.

    :param win: Window screen.
        + type: curses.Window
    :param pos: Position to write.
        + type: List<int, int>
    :param char: Character to write.
        + type: string
    :param color: Color code to use.
        + type: int
    :return: None
    """
    win.addch(pos[0], pos[1], char, curses.color_pair(color))


def clear_from_win(win, positions):
    """
    Prints an empty char on the given position.

    :param win: Window screen.
        + type: curses.Window
    :param positions: Positions to write
        + type: List<List<int, int>>
    :return: None
    """
    for pos in positions:
        print_char(win, pos, CHAR_EMPTY, COLOR_EMPTY)


def move_snakes(win, colors_per_player, keys, players_alive, scores, snakes, foods, food_times):
    """
    Calculates the next move of all the snakes.

    :param win:   Window screen.
        + type: curses.Window
    :param colors_per_player: Color for each active player.
        + type: List<int>
    :param keys: Pressed key for each active player.
        + type: List<int>
    :param players_alive: List indicating whether the player is alive or not.
        + type: List<boolean>
    :param scores: List indicating the current score of each player.
        + type: List<int>
    :param snakes: Current snake position of each player.
        + type: List<List<List<int, int>>>
    :param foods: Current food position of each player.
        + type: List<List<int, int>>
    :param food_times: Time when food of each player was created
        + type: List<time>
    :return: A tuple with the updated values: whether the game must end or not, the alive players,
        the scores, the new snakes positions, the new foods positions, and the new foods times.
        + type: List<Tuple<Boolean,List,List,List,List,List>>
    """
    # Calculates new coordinates of the snakes
    for player_id, snake in enumerate(snakes):
        if players_alive[player_id]:
            snake.insert(0, [snake[0][0] + (keys[player_id] in KEYS_DOWN and 1) + (keys[player_id] in KEYS_UP and -1),
                             snake[0][1] + (keys[player_id] in KEYS_LEFT and -1) + (
                                     keys[player_id] in KEYS_RIGHT and 1)])

            # If snake crosses the boundaries, make it enter from the other side
            if snake[0][0] == 0:
                snake[0][0] = Y_SIZE - 2
            if snake[0][1] == 0:
                snake[0][1] = X_SIZE - 2
            if snake[0][0] == Y_SIZE - 1:
                snake[0][0] = 1
            if snake[0][1] == X_SIZE - 1:
                snake[0][1] = 1

    # Control if the game must end
    for player_id, snake in enumerate(snakes):
        if players_alive[player_id]:
            # Snake out of bounds
            if BOUNDS_ENABLED:
                if snake[0][0] == 0 or snake[0][0] == Y_SIZE - 1 or snake[0][1] == 0 or snake[0][1] == X_SIZE - 1:
                    clear_from_win(win, snakes[player_id])
                    clear_from_win(win, [foods[player_id]])
                    snakes[player_id] = []
                    players_alive[player_id] = False
            # Snake runs over itself
            if snake[0] in snake[1:]:
                clear_from_win(win, snakes[player_id])
                clear_from_win(win, [foods[player_id]])
                snakes[player_id] = []
                players_alive[player_id] = False
            # Snake head touches another snake
            for other_player_id, other_snake in enumerate(snakes):
                if other_player_id != player_id:
                    if snake[0] in other_snake:
                        # Increase the other player's score
                        scores[other_player_id] = scores[other_player_id] + SCORE_PER_KILL
                        # Kill current snake
                        clear_from_win(win, snakes[player_id])
                        clear_from_win(win, [foods[player_id]])
                        snakes[player_id] = []
                        players_alive[player_id] = False
    if True not in players_alive:
        return True, players_alive, scores, snakes, foods, food_times

    # Check if the snakes eat
    for player_id, snake in enumerate(snakes):
        if players_alive[player_id]:
            food = foods[player_id]
            food_time = food_times[player_id]
            if snake[0] == food:
                # Increase the score
                elapsed_time = datetime.now() - food_time
                et_seconds = elapsed_time.total_seconds() + 1
                scores[player_id] = scores[player_id] + int(MAX_SCORE_PER_FOOD / et_seconds)

                # Recalculate new food
                foods[player_id] = [randint(1, Y_SIZE - 2), randint(1, X_SIZE - 2)]
                food_times[player_id] = datetime.now()
                print_char(win, foods[player_id], CHAR_FOOD, colors_per_player[player_id])
            else:
                # Decrease snake size (has not eaten)
                last = snake.pop()
                if last in foods:
                    # If there was a food, re-print it
                    food_player = foods.index(last)
                    print_char(win, last, CHAR_FOOD, colors_per_player[food_player])
                else:
                    # Otherwise just clean the position
                    clear_from_win(win, [last])

            # Print the snake head (advance)
            print_char(win, snake[0], CHAR_SNAKE, colors_per_player[player_id])

    # Return new state
    return False, players_alive, scores, snakes, foods, food_times


#
# FIRST LEVEL HELPER METHODS
#

def init_game_screen():
    """
    Initializes the game window screen.

    :return: The window screen.
        + type: curses.Window
    """
    logger.debug("Initializing window properties")

    # Initialize window screen
    curses.initscr()
    curses.noecho()
    curses.curs_set(0)

    win = curses.newwin(Y_SIZE, X_SIZE, 0, 0)
    win.keypad(1)
    win.border(0)
    win.nodelay(1)

    # Add colors
    curses.start_color()
    curses.use_default_colors()
    for i in range(0, curses.COLORS):
        curses.init_pair(i + 1, i, -1)

    return win


def run_game(win):
    """
    Runs the game until the user requests to end or he gets killed.

    :param win: Window screen.
        + type: curses.Window
    :return: Game score.
        + type: int
    """
    logger.debug("Running main game method")

    # Initializing values
    keys_per_player = build_keys_per_player(NUM_PLAYERS)
    colors_per_player = build_colors_per_player(NUM_PLAYERS)
    scores = [0 for _ in range(NUM_PLAYERS)]
    players_alive = [True for _ in range(NUM_PLAYERS)]
    keys = [initial_key_random(i) for i in range(NUM_PLAYERS)]
    snakes = [initial_snake_random() for _ in range(NUM_PLAYERS)]
    foods = [random_position() for _ in range(NUM_PLAYERS)]
    food_times = [datetime.now() for _ in range(NUM_PLAYERS)]

    # Print initial foods
    for player_id, food in enumerate(foods):
        print_char(win, food, CHAR_FOOD, colors_per_player[player_id])

    # Main loop
    must_end = False
    while not must_end:
        # Print game
        print_game_iteration(win, colors_per_player, scores, snakes)

        # Process events
        events = process_events(win, keys_per_player)
        if "global" in events:
            event_global = events["global"]
            if event_global == KEY_SPACE:
                # SPACE BAR pressed, pause/resume game
                must_end = wait_for_resume_game(win)
                # Start the loop again
                continue
            elif event_global == KEY_ESC:
                # ESC pressed, end game
                must_end = True
                # Start loop again
                continue

        # Update player keys
        for player, event in events.items():
            if event is not None:
                keys[int(player)] = event

        # Move snakes
        must_end, players_alive, scores, snakes, foods, food_times = move_snakes(win, colors_per_player, keys,
                                                                                 players_alive, scores, snakes, foods,
                                                                                 food_times)

    return scores


def end_game(scores):
    """
    Ends the game window screen and show the result.

    :param scores: User scores.
        + type: List<int>
    :return: None
    """
    logger.debug("Ending game")
    # Close window screen
    curses.endwin()

    # Print score
    final_scores = []
    for player_id, score in enumerate(scores):
        final_scores.append([score, player_id])
    final_scores.sort(reverse=True)

    print()
    print("FINAL SCORES:")
    for rank, player_info in enumerate(final_scores):
        player_score, player_id = player_info
        print(str(rank + 1) + ": Player " + str(player_id) + " with Score = " + str(player_score))
    print()

    print("PLAYER " + str(final_scores[0][1]) + " YOU ARE THE WINNER!!")
    print()


#
# MAIN
#

def main():
    """
    Main function to play the Snake game.
    Use ARROW KEYS to play, SPACE BAR for pausing/resuming, and Esc Key for exiting.

    :return: None
    """
    logger.info("Snake game start")
    win = init_game_screen()
    scores = run_game(win)
    end_game(scores)
    logger.info("Snake game end")


#
# ENTRY POINT
#
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(name)s - %(message)s')
    main()
