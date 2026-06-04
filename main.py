import pygame as pg
import sys
from systems import input_sys


class Player:
    def __init__(self):
        self.dest = pg.FRect(20.0, 20.0, 16.0, 16.0)


def get_movement(input_state):
    return input_state.events["right"].held - input_state.events["left"].held


def run():
    pg.init()

    FPS_TARGET = 60

    screen = pg.display.set_mode((640, 480))
    display = pg.Surface((screen.width / 2, screen.height / 2))
    clock = pg.Clock()
    input_state = input_sys.InputState()

    player = Player()

    while True:
        input_state.update_just_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            input_state.update_input(event)

        player.dest.x += get_movement(input_state)

        display.fill("black")
        pg.draw.rect(display, "lime", player.dest)

        screen.blit(pg.transform.scale(display, screen.get_size()))
        clock.tick(FPS_TARGET)
        pg.display.update()


if __name__ == "__main__":
    run()
