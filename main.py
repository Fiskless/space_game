import random
import time
import asyncio
import curses

from itertools import cycle


SPACE_KEY_CODE = 32
LEFT_KEY_CODE = 260
RIGHT_KEY_CODE = 261
UP_KEY_CODE = 259
DOWN_KEY_CODE = 258

TIC_TIMEOUT = 0.1
STARS_COUNT = 100


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)
    height, width = canvas.getmaxyx()
    star_symbols = ["+", "*", ".", ":"]
    board_half_height = height/2
    board_half_width = width/2
    cannon_shot = fire(canvas, board_half_height, board_half_width)
    spaceship = animate_spaceship(
        canvas,
        board_half_height,
        board_half_width
    )
    coroutines = [spaceship, cannon_shot]

    for _ in range(STARS_COUNT):
        symbol = random.choice(star_symbols)
        row = random.randint(1, height - 2)
        column = random.randint(1, width - 2)
        time_delay = random.randint(0, 5)
        coroutines.append(blink(canvas, row, column, time_delay, symbol))

    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
                canvas.refresh()
            except StopIteration:
                coroutines.remove(coroutine)


async def animate_spaceship(canvas, row, column):

    with open("animation_frames/rocket_frame_1.txt", "r") as file:
        rocket_frame_1 = file.read()

    with open("animation_frames/rocket_frame_2.txt", "r") as file:
        rocket_frame_2 = file.read()

    row_max, column_max = canvas.getmaxyx()
    spaceship_row, spaceship_column = get_frame_size(rocket_frame_1)
    rocket_frames = [rocket_frame_1, rocket_frame_1, rocket_frame_2, rocket_frame_2]
    current_coordinates = [row, column]
    for rocket_frame in cycle(rocket_frames):
        rows_direction, columns_direction, _ = read_controls(canvas)
        current_row = current_coordinates[0] + rows_direction
        current_column = current_coordinates[1] + columns_direction
        if current_row+spaceship_row >= row_max \
                or current_column+spaceship_column-1 >= column_max \
                or current_row+1 <= 0 \
                or current_column+1 <= 0:
            current_row, current_column = current_coordinates
        draw_frame(canvas, current_row, current_column, rocket_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, current_row, current_column, rocket_frame, negative=True)
        current_coordinates = [current_row, current_column]



def draw_frame(canvas, start_row, start_column, text, negative=False):
    """Draw multiline text fragment on canvas, erase text instead of drawing if negative=True is specified."""

    rows_number, columns_number = canvas.getmaxyx()

    for row, line in enumerate(text.splitlines(), round(start_row)):
        if row < 0:
            continue

        if row >= rows_number:
            break

        for column, symbol in enumerate(line, round(start_column)):
            if column < 0:
                continue

            if column >= columns_number:
                break

            if symbol == ' ':
                continue

            # Check that current position it is not in a lower right corner of the window
            # Curses will raise exception in that case. Don`t ask why…
            # https://docs.python.org/3/library/curses.html#curses.window.addch
            if row == rows_number - 1 and column == columns_number - 1:
                continue

            symbol = symbol if not negative else ' '
            canvas.addch(row, column, symbol)


def read_controls(canvas):
    """Read keys pressed and returns tuple witl controls state."""

    rows_direction = columns_direction = 0
    space_pressed = False

    while True:
        pressed_key_code = canvas.getch()

        if pressed_key_code == -1:
            # https://docs.python.org/3/library/curses.html#curses.window.getch
            break

        if pressed_key_code == UP_KEY_CODE:
            rows_direction = -10

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 10

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 10

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -10

        if pressed_key_code == SPACE_KEY_CODE:
            space_pressed = True

    return rows_direction, columns_direction, space_pressed


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, time_delay, symbol='*'):

    while True:
        time.sleep(time_delay / STARS_COUNT)
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)
        time.sleep(2/STARS_COUNT)
        await asyncio.sleep(0)

        time.sleep(time_delay / STARS_COUNT)
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)
        time.sleep(0.3/STARS_COUNT)
        await asyncio.sleep(0)

        time.sleep(time_delay / STARS_COUNT)
        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)
        time.sleep(0.5/STARS_COUNT)
        await asyncio.sleep(0)

        time.sleep(time_delay / STARS_COUNT)
        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)
        time.sleep(0.3/STARS_COUNT)
        await asyncio.sleep(0)


def get_frame_size(text):
    """Calculate size of multiline text fragment, return pair — number of rows and colums."""

    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()

