import random
import time
import asyncio
import curses

from itertools import cycle

from curses_tools import get_frame_size, draw_frame, read_controls
from obstacles import Obstacle, show_obstacles
from physics import update_speed


TIC_TIMEOUT = 0.1
STARS_COUNT = 30

COROUTINES = []

SPACESHIP_FRAME = ''

OBSTACLES = []

OBSTACLES_IN_LAST_COLLISISONS = []


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)
    height, width = canvas.getmaxyx()
    star_symbols = ["+", "*", ".", ":"]
    board_half_height = height/2
    board_half_width = width/2
    frames = (
        get_frame('animation_frames/rocket_frame_1.txt'),
        get_frame('animation_frames/rocket_frame_2.txt'),
    )

    COROUTINES = [
        animate_spaceship(frames),
        run_spaceship(canvas, board_half_height, board_half_width),
        fire(canvas, board_half_height, board_half_width),
        show_obstacles(canvas, OBSTACLES)]

    for _ in range(STARS_COUNT):
        symbol = random.choice(star_symbols)
        row = random.randint(1, height - 2)
        column = random.randint(1, width - 2)
        COROUTINES.append(blink(canvas, row, column, symbol))

    for _ in range(2):
        COROUTINES.append(fill_orbit_with_garbage(canvas, width))

    while True:
        for coroutine in COROUTINES:
            try:
                coroutine.send(None)
            except StopIteration:
                COROUTINES.remove(coroutine)
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


async def fill_orbit_with_garbage(canvas, width):

    trash_large = get_frame("animation_frames/trash_large.txt")
    trash_small = get_frame("animation_frames/trash_small.txt")
    trash_xl = get_frame("animation_frames/trash_xl.txt")

    while True:
        frame = random.choice([trash_xl, trash_small, trash_large])
        rows, columns = get_frame_size(frame)
        columns_min = 0
        columns_max = int(width - columns)
        await sleep(random.randint(0, 30))
        await fly_garbage(canvas,
                          column=random.randint(columns_min, columns_max),
                          garbage_frame=frame)


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    frame_height, frame_width = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, frame_height, frame_width)
    OBSTACLES.append(obstacle)

    while row < rows_number:
        draw_frame(canvas, row, column, garbage_frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed
        obstacle.row += speed

        if obstacle in OBSTACLES_IN_LAST_COLLISISONS:
            OBSTACLES_IN_LAST_COLLISISONS.remove(obstacle)
            OBSTACLES.remove(obstacle)
            return

    OBSTACLES.remove(obstacle)


async def animate_spaceship(frames):
    """Define the current frame for a spaceship.

    Params:
        * frames: tuple with images of a spaceship
    """
    global SPACESHIP_FRAME
    while True:
        for frame in cycle(frames):
            SPACESHIP_FRAME = frame
            await sleep(2)


async def run_spaceship(canvas, row, column):

    row_speed, column_speed = (0, 0)
    row_max, column_max = canvas.getmaxyx()
    current_coordinates = [row, column]

    global SPACESHIP_FRAME

    while True:
        spaceship_row, spaceship_column = get_frame_size(SPACESHIP_FRAME)
        rows_direction, columns_direction, space_pressed = read_controls(canvas, row, column)
        row_speed, column_speed = update_speed(
            row_speed,
            column_speed,
            rows_direction,
            columns_direction,
        )

        current_row = current_coordinates[0] + row_speed
        current_column = current_coordinates[1] + column_speed

        if space_pressed:
            fire_coroutine = await fire(canvas, current_row, current_column, rows_speed=-2)
            COROUTINES.append(fire_coroutine)

        if current_row+spaceship_row+1 >= row_max \
                or current_column+spaceship_column+1 >= column_max \
                or current_row-1 <= 0 \
                or current_column-1 <= 0:
            current_row, current_column = current_coordinates
        draw_frame(canvas, current_row, current_column, SPACESHIP_FRAME)
        current_frame = SPACESHIP_FRAME
        await asyncio.sleep(0)
        draw_frame(canvas, current_row, current_column, current_frame, negative=True)
        current_coordinates = [current_row, current_column]


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column + 2

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

        for obstacle in OBSTACLES:
            if obstacle.has_collision(row, column):
                OBSTACLES_IN_LAST_COLLISISONS.append(obstacle)
                return

        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def blink(canvas, row, column, symbol='*'):

    while True:
        await sleep(random.randint(0, 10))

        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(20)

        canvas.addstr(row, column, symbol)
        await sleep(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(5)

        canvas.addstr(row, column, symbol)
        await sleep(3)


def get_frame(file):
    """Load animation frame from the file."""
    with open(file, 'r') as file:
        frame = file.read()
    return frame


async def sleep(tics=1):
    for _ in range(tics):
        await asyncio.sleep(0)


def main():
    curses.update_lines_cols()
    curses.wrapper(draw)


if __name__ == '__main__':
    main()

