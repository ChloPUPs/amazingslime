import pygame as pg
import sys
from systems import input_sys


class Player:
    def __init__(self):
        self.speed = 1.2
        self.jump_strength = 3.0
        self.gravity = 0.1
        self.dest = pg.FRect(20.0, 20.0, 16.0, 14.0)
        self.vx = 0.0
        self.vy = 0.0
        self.img = pg.image.load("player/amazslime.png").convert_alpha()
        self.img_offset = (0.0, -2.0)

    def update_vel(self, input_state):
        self.vy += self.gravity

        dx = get_axis(input_state, "x")
        self.vx = dx * self.speed

        if input_state.events["z"].just_pressed:
            self.vy = -self.jump_strength

    def collide(self, rect):
        if pg.Rect(
                self.dest.x + self.vx, self.dest.y, # x, y
                self.dest.w, self.dest.h # w, h
                ).colliderect(rect):
            if self.vx > 0.0:
                self.dest.right = rect.left
            else:
                self.dest.left = rect.right
            self.vx = 0.0
        if pg.FRect(
                self.dest.x, self.dest.y + self.vy, # x, y
                self.dest.w, self.dest.h # w, h
                ).colliderect(rect):
            if self.vy > 0.0:
                self.dest.bottom = rect.top
            else:
                self.dest.top = rect.bottom
            self.vy = 0.0

    def apply_vel(self):
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
    block = pg.FRect(20.0, 80.0, 16.0, 16.0)
    block_img = pg.image.load("levels/stone.png").convert()

    while True:
        input_state.update_just_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            input_state.update_input(event)

        player.update_vel(input_state)
        player.collide(block)
        player.apply_vel()

        display.fill("black")
        display.blit(block_img, block)
        pos = (player.dest.x + player.img_offset[0], player.dest.y + player.img_offset[1])
        display.blit(player.img, pos)

        screen.blit(pg.transform.scale(display, screen.get_size()))
        clock.tick(FPS_TARGET)
        pg.display.update()


if __name__ == "__main__":
    run()
