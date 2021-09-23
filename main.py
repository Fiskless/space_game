import random
import time
import asyncio
import curses

from itertools import cycle


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)
    height, width = canvas.getmaxyx()
    star_symbols = ["+", "*", ".", ":"]
    cannon_shot = fire(canvas, height/2, width/2)
    spaceship = animate_spaceship(
        canvas,
        height/2,
        width/2
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

    rocket_frames = [rocket_frame_1, rocket_frame_1]
    for rocket_frame in cycle(rocket_frames):
        draw_frame(canvas, row, column, rocket_frame, negative=True)
        await asyncio.sleep(0)


    # for rocket_number, rocket_frame in cycle(enumerate(rocket_frames, start=1)):
    #     if rocket_number % 2 == 0:
    #         draw_frame(canvas, row, column, rocket_frame)
    #     else:
    #         draw_frame(canvas, row, column, rocket_frame)
    #     await asyncio.sleep(0)


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
            rows_direction = -1

        if pressed_key_code == DOWN_KEY_CODE:
            rows_direction = 1

        if pressed_key_code == RIGHT_KEY_CODE:
            columns_direction = 1

        if pressed_key_code == LEFT_KEY_CODE:
            columns_direction = -1

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


if __name__ == '__main__':
    SPACE_KEY_CODE = 32
    LEFT_KEY_CODE = 260
    RIGHT_KEY_CODE = 261
    UP_KEY_CODE = 259
    DOWN_KEY_CODE = 258

    TIC_TIMEOUT = 0.1
    STARS_COUNT = 100

    with open("animation_frames/rocket_frame_1.txt", "r") as file:
        rocket_frame_1 = file.read()

    with open("animation_frames/rocket_frame_2.txt", "r") as file:
        rocket_frame_2 = file.read()

    curses.update_lines_cols()
    curses.wrapper(draw)

