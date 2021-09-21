import time
import asyncio
import curses


def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    coroutine_1 = blink(canvas, 5, 5)
    coroutine_2 = blink(canvas, 5, 10)
    coroutine_3 = blink(canvas, 5, 15)
    coroutine_4 = blink(canvas, 5, 20)
    coroutine_5 = blink(canvas, 5, 25)
    coroutines = [
        coroutine_1,
        coroutine_2,
        coroutine_3,
        coroutine_4,
        coroutine_5
    ]
    while True:
        for coroutine in coroutines.copy():
            coroutine.send(None)
            canvas.refresh()
        time.sleep(2)
        for coroutine in coroutines.copy():
            coroutine.send(None)
            canvas.refresh()
        time.sleep(0.3)
        for coroutine in coroutines.copy():
            coroutine.send(None)
            canvas.refresh()
        time.sleep(0.5)
        for coroutine in coroutines.copy():
            coroutine.send(None)
            canvas.refresh()
        time.sleep(0.3)
        canvas.refresh()



async def blink(canvas, row, column, symbol='*'):
    while True:

        canvas.addstr(row, column, symbol, curses.A_DIM)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        await asyncio.sleep(0)


if __name__ == '__main__':

    TIC_TIMEOUT = 0.1

    curses.update_lines_cols()
    curses.wrapper(draw)

