import pygame as pg
import sys
from systems import input_sys


class Player:
    def __init__(self):
        self.dest = pg.FRect(20.0, 20.0, 16.0, 16.0)


def run():
    pg.init()

    screen = pg.display.set_mode((640, 480))
    display = pg.Surface((screen.width / 2, screen.height / 2))
    input_state = input_sys.InputState()

    player = Player()

    num = 1

    while True:
        input_state.update_just_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            input_state.update_input(event)

        if input_state.events["up"].held:
            num += 1
            print(f"Apple sauce! x{num}...")

        pg.draw.rect(display, "lime", player.dest)

        screen.blit(pg.transform.scale(display, screen.get_size()))
        pg.display.update()


if __name__ == "__main__":
    run()
