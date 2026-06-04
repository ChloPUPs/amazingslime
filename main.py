# Maybe add text in levels? Level Text in The Levl

from typing import Literal
import pygame as pg
import sys
from enum import Enum, auto
import yaml
from systems import input_sys


type BlockID = Literal["stone"]


class Level:
    def __init__(self,
            name: str | None,
            grid: dict[tuple[int, int], BlockID],
            tile_size: int,
            assets: dict[BlockID, pg.Surface]) -> None:
        self.name = name # Use file path if None
        self.grid = grid
        self.assets = assets
        self._tile_size = tile_size

    def draw(self, display: pg.Surface) -> None:
        for key in self.grid:
            display.blit(self.assets[self.grid[key]], 
                    (key[0] * self._tile_size, key[1] * self._tile_size))


class Player:
    def __init__(self) -> None:
        self.speed = 1.2
        self.jump_strength = 3.4
        self.gravity = 0.16
        self.dest = pg.FRect(20.0, 20.0, 16.0, 14.0)
        self.vx = 0.0
        self.vy = 0.0
        self.img = pg.image.load("player/amazslime.png").convert_alpha()
        self.img_offset = (0.0, -2.0)
        self.on_ground = False

    def reset_on_ground(self):
        self.on_ground = False

    def update_vel(self, input_state: input_sys.InputState) -> None:
        if not self.on_ground:
            self.vy += self.gravity

        dx = get_axis(input_state, "x")
        self.vx = dx * self.speed

        if input_state.events["z"].just_pressed and self.on_ground:
            self.vy = -self.jump_strength

    def collide(self, rect: pg.FRect | pg.Rect) -> None:
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

        if pg.FRect(self.dest.x, self.dest.y + 1.0, self.dest.w, self.dest.h).colliderect(rect):
            self.on_ground = True

    def apply_vel(self) -> None:
        self.dest.x += self.vx
        self.dest.y += self.vy


def get_axis(input_state: input_sys.InputState, axis: Literal["x", "y"]) -> float:
    if axis.lower() == "x":
        return input_state.events["right"].held - input_state.events["left"].held
    elif axis.lower() == "y":
        return input_state.events["down"].held - input_state.events["up"].held
    else:
        raise ValueError("Why?")


def run() -> None:
    pg.init()

    FPS_TARGET = 60
    TILE_SIZE = 16

    screen = pg.display.set_mode((640, 480))
    display = pg.Surface((screen.width / 2, screen.height / 2))
    clock = pg.Clock()
    input_state = input_sys.InputState()

    player = Player()

    with open("levels/test_level.yaml") as f:
        level_data = yaml.safe_load(f)
        level_name = level_data["name"]
        level_grid = {(int(key.split(",")[0]), int(key.split(",")[1])): level_data["grid"][key] for key in level_data["grid"]}

    level = Level(level_name, level_grid, TILE_SIZE, {
        "stone": pg.image.load("levels/stone.png").convert(),
    })

    while True:
        input_state.update_just_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()
            input_state.update_input(event)

        player.update_vel(input_state)
        player.reset_on_ground()
        for key in level.grid:
            player.collide(pg.Rect(key[0] * TILE_SIZE, key[1] * TILE_SIZE, 16, 16))
        player.apply_vel()

        display.fill("black")
        level.draw(display)
        pos = (player.dest.x + player.img_offset[0], player.dest.y + player.img_offset[1])
        display.blit(player.img, pos)
        font = pg.font.SysFont("Arial", 16)
        text = font.render(f"{level.name}", True, "white")
        display.blit(text, (5, 5))

        screen.blit(pg.transform.scale(display, screen.get_size()))
        clock.tick(FPS_TARGET)
        pg.display.update()


if __name__ == "__main__":
    run()
