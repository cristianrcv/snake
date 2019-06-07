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

KEYS_UP = [KEY_UP, KEY_W, KEY_I, KEY_NUM_8]
KEYS_DOWN = [KEY_DOWN, KEY_S, KEY_K, KEY_NUM_5]
KEYS_RIGHT = [KEY_RIGHT, KEY_D, KEY_L, KEY_NUM_6]
KEYS_LEFT = [KEY_LEFT, KEY_A, KEY_J, KEY_NUM_4]

# CONSTANTS
LEAST_SPEED = 600
TOP_SPEED = 30
INITIAL_SPEED = int(LEAST_SPEED / BASE_SPEED)

Y_SIZE = 40
X_SIZE = 100

INITIAL_KEY = KEY_RIGHT
INITIAL_FOOD = [10, 20]
INITIAL_SNAKE = [[4, 10], [4, 9], [4, 8]]

CHAR_FOOD = '*'
CHAR_EMPTY = ' '
CHAR_SNAKE = '#'

COLOR_FOOD = 209
COLOR_EMPTY = 1
COLOR_SNAKE = 47

MAX_SCORE_PER_FOOD = 100

#
# Logger definition
#

logger = logging.getLogger("console")


#
# SECOND LEVEL HELPER METHODS
#

def print_game_iteration(win, score, snake):
    """
    Generates the window for the next game iteration

    :param win: Window screen.
        + type: curses.Window
    :param score: Current score
        + type: int
    :param snake: Snake positions
        + type: List<List<int, int>>
    :return: None
    """
    win.border(0)

    # Print score
    win.addstr(0, 2, 'Score : ' + str(score) + ' ')

    # Print Snake name
    win.addstr(0, 27, ' SNAKE ')  # 'SNAKE' strings

    # Increase snake speed with its length
    increase_speed = int(5 * (len(snake) / 5 + len(snake) / 10))
    speed = INITIAL_SPEED - increase_speed % (INITIAL_SPEED - TOP_SPEED)
    win.timeout(speed)


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


def process_events(win):
    """
    Process the next event.

    :param win: Window screen.
        + type: curses.Window
    :return: One of the registered events or None.
        + type: int or None.
    """
    # Get event
    event = win.getch()

    # Only allow valid events
    if event not in KEYS_UP \
            and event not in KEYS_DOWN \
            and event not in KEYS_RIGHT \
            and event not in KEYS_LEFT \
            and event != KEY_SPACE \
            and event != KEY_ESC:
        return None
    return event


def wait_for_resume_game(win):
    """
    Waits until the game is resumed or ended.

    :param win: Window screen.
        + type: curses.Window
    :return: True if the game must end, False if the game must resume.
        + type: boolean
    """
    key = INITIAL_KEY
    while key != KEY_SPACE and key != KEY_ESC:
        key = win.getch()

    return key != KEY_SPACE


def move_snake(win, key, snake, food, food_time, score):
    """
    Calculates the next snake move.

    :param win: Window screen.
        + type: curses.Window
    :param key: Current pressed key.
        + type: int
    :param snake: Current snake position.
        + type: List<List<int, int>>
    :param food: Current food position.
        + type: List<int, int>
    :param food_time: Time when food was created.
        + type: time
    :param score: Current score.
        + type: int
    :return: A tuple representing if the game must be ended, the snake position, the next food position,
    the food creation time, and the current score
        + type: Tuple<Boolean, List, List, time, int>
    """
    # Calculates the new coordinates of the head of the snake
    snake.insert(0, [snake[0][0] + (key in KEYS_DOWN and 1) + (key in KEYS_UP and -1),
                     snake[0][1] + (key in KEYS_LEFT and -1) + (key in KEYS_RIGHT and 1)])

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
    # Exit if snake crosses the boundaries (Uncomment to enable)
    if BOUNDS_ENABLED:
        if snake[0][0] == 0 or snake[0][0] == Y_SIZE - 1 or snake[0][1] == 0 or snake[0][1] == X_SIZE - 1:
            return True, snake, food, food_time, score
    # If snake runs over itself
    if snake[0] in snake[1:]:
        return True, snake, food, food_time, score

    # Control if the snake its the food
    if snake[0] == food:
        # Increase the score
        elapsed_time = datetime.now() - food_time
        et_seconds = elapsed_time.total_seconds() + 1
        score = score + int(MAX_SCORE_PER_FOOD / et_seconds)

        # Recalculate new food
        food = None
        while food is None:
            # From 1 to size - 2 because of borders
            food = [randint(1, Y_SIZE - 2), randint(1, X_SIZE - 2)]
            if food in snake:
                food = None
        print_char(win, food, CHAR_FOOD, COLOR_FOOD)
        food_time = datetime.now()
    else:
        # Decrease the size of the snake if it does not eat (because we have increased it at the beginning)
        last = snake.pop()
        print_char(win, last, CHAR_EMPTY, COLOR_EMPTY)

    # Print the snake
    print_char(win, snake[0], CHAR_SNAKE, COLOR_SNAKE)

    return False, snake, food, food_time, score


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
    score = 0
    snake = INITIAL_SNAKE
    food = INITIAL_FOOD
    food_time = datetime.now()

    key = INITIAL_KEY
    print_char(win, food, CHAR_FOOD, COLOR_FOOD)

    # Main loop
    must_end = False
    while not must_end and key != KEY_ESC:
        # Print game
        print_game_iteration(win, score, snake)

        # Process events
        event = process_events(win)
        if event is not None:
            if event == KEY_SPACE:
                # SPACE BAR pressed, pause/resume game
                must_end = wait_for_resume_game(win)
                # Start the loop again
                continue
            else:
                key = event

        # Move snake
        must_end, snake, food, food_time, score = move_snake(win, key, snake, food, food_time, score)

    return score


def end_game(score):
    """
    Ends the game window screen and show the result.

    :param score: User score.
        + type: int
    :return: None
    """
    logger.debug("Ending game")
    # Close window screen
    curses.endwin()

    # Print score
    print()
    print("FINAL SCORE = " + str(score))
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
    score = run_game(win)
    end_game(score)
    logger.info("Snake game end")


#
# ENTRY POINT
#
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(name)s - %(message)s')
    main()
