# Maybe add text in levels? Level Text in The Levl

from typing import Literal
from enum import Enum, auto
import pygame as pg
import yaml
from systems import input_sys


class BlockType(Enum):
    STONE = auto()

    @staticmethod
    def from_str(x: str) -> BlockType:
        match x:
            case "stone":
                return BlockType.STONE
            case _:
                raise ValueError(f"BlockType '{x}' is undefined")


class Level:
    @staticmethod
    def load_from_file(path: str):
        with open(path) as f:
            level_data = yaml.safe_load(f)
            level_name = level_data["name"]
            tile_size = level_data["tile_size"]
            level_grid = {}
            for old_key in level_data["grid"]:
                x = int(old_key.split(",")[0])
                y = int(old_key.split(",")[1])
                level_grid[(x, y)] = BlockType.from_str(level_data["grid"][old_key])

        return Level(level_name, level_grid, tile_size, {
            BlockType.STONE: pg.image.load("levels/stone.png").convert(),
        })

    def __init__(self,
            name: str | None,
            grid: dict[tuple[int, int], BlockType],
            tile_size: int,
            assets: dict[BlockType, pg.Surface]) -> None:
        self.name = name # Use file path if None
        self.grid = grid
        self.assets = assets
        self._tile_size = tile_size

    def draw(self, display: pg.Surface) -> None:
        for tile_pos in self.grid:
            self.__draw_tile(display, tile_pos)

    def __draw_tile(self, display: pg.Surface, tile_pos: tuple[int, int]) -> None:
        display.blit(self.assets[self.grid[tile_pos]], 
                    (tile_pos[0] * self._tile_size, tile_pos[1] * self._tile_size))


class Player:
    def __init__(self, start_x: float, start_y: float) -> None:
        self._start_x = start_x
        self._start_y = start_y
        self.speed = 1.2
        self.jump_strength = 3.4
        self.gravity = 0.16
        self.dest = pg.FRect(start_x, start_y, 14.0, 13.0)
        self.velx = 0.0
        self.vely = 0.0
        self.img = pg.image.load("player/amazslime.png").convert_alpha()
        self.img_offset = (-1.0, -3.0)
        self.on_ground = False

    def update_independent_movement(self, input_state: input_sys.InputState) -> None:
        if not self.on_ground:
            self.vely += self.gravity

        direction_x = get_axis(input_state, "x")
        self.velx = direction_x * self.speed

        if input_state.events["z"].just_pressed and self.on_ground:
            self.vely = -self.jump_strength

        self.on_ground = False

    def collide_block(self, rect: pg.FRect | pg.Rect) -> None:
        if self.__is_colliding_x(rect):
            if self.velx > 0.0:
                self.dest.right = rect.left
            else:
                self.dest.left = rect.right
            self.velx = 0.0

        if self.__is_colliding_y(rect):
            if self.vely > 0.0:
                self.dest.bottom = rect.top
            else:
                self.dest.top = rect.bottom
            self.vely = 0.0

        if pg.FRect(self.dest.x, self.dest.y + 1.0, self.dest.w, self.dest.h).colliderect(rect):
            self.on_ground = True

    def collide_walls_x(self, screen_width: int) -> None:
        next_x = self.dest.x + self.velx
        if next_x < 0.0:
            self.dest.left = 0.0
            self.velx = 0.0
        elif next_x > screen_width:
            self.dest.right = screen_width
            self.velx = 0.0

    def apply_vel(self) -> None:
        self.dest.x += self.velx
        self.dest.y += self.vely

    def reset(self) -> None:
        self.dest.x = self._start_x
        self.dest.y = self._start_y
        self.velx = 0.0
        self.vely = 0.0

    def __is_colliding_x(self, rect: pg.FRect | pg.Rect) -> bool:
        return pg.Rect(
                self.dest.x + self.velx, self.dest.y, # x, y
                self.dest.w, self.dest.h # w, h
                ).colliderect(rect)

    def __is_colliding_y(self, rect: pg.FRect | pg.Rect) -> bool:
        return pg.FRect(
                self.dest.x, self.dest.y + self.vely, # x, y
                self.dest.w, self.dest.h # w, h
                ).colliderect(rect)



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

    player = Player(20.0, 20.0)
    level = Level.load_from_file("levels/test_level.yaml")

    while True:
        input_state.update()

        if input_state.events["r"].just_pressed:
            player.reset()

        player.update_independent_movement(input_state)
        player.collide_walls_x(screen.get_width())
        for old_key in level.grid:
            player.collide_block(pg.Rect(old_key[0] * TILE_SIZE, old_key[1] * TILE_SIZE, 16, 16))
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
