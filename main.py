import pygame as pg
import sys
from systems import input_sys


class Player:
    def __init__(self):
        self.speed = 1.2
        self.jump_strength = 3.0
        self.gravity = 0.1
        self.dest = pg.FRect(20.0, 20.0, 16.0, 16.0)
        self.vx = 0.0
        self.vy = 0.0
        self.img = pg.image.load("player/amazslime.png").convert()

    def update(self, input_state):
        self.vy += self.gravity

        dx = get_axis(input_state, "x")
        self.vx = dx * self.speed

        if input_state.events["z"].just_pressed:
            self.vy = -self.jump_strength

        self.dest.x += self.vx
        self.dest.y += self.vy


def get_axis(input_state, axis):
    if axis.lower() == "x":
        return input_state.events["right"].held - input_state.events["left"].held
    elif axis.lower() == "y":
        return input_state.events["down"].held - input_state.events["up"].held
    else:
        raise ValueError("Why?")


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

        player.update(input_state)

        display.fill("black")
        display.blit(player.img, player.dest)

        screen.blit(pg.transform.scale(display, screen.get_size()))
        clock.tick(FPS_TARGET)
        pg.display.update()


if __name__ == "__main__":
    run()
