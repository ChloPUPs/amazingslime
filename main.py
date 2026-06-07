# Maybe add text in levels? Level Text in The Levl

from typing import Literal, NamedTuple, TypedDict
from collections.abc import Callable
import pygame as pg
import yaml
import sys
import os
from systems import input_sys


class Config(TypedDict):
    default_level: str


class Block(NamedTuple):
    block_id: str
    img: pg.Surface
    solid: bool = True
    on_collide: Callable[[], None] | None = None


class BlockIDError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class BlockRegistry:
    def __init__(self) -> None:
        self._registered: dict[str, Block] = {}

    def register(self, new: Block) -> None:
        if new.block_id in self._registered:
            raise BlockIDError(f"ID '{new.block_id}' already taken.")

        self._registered[new.block_id] = new

    def of_id(self, id: str) -> Block:
        if id not in self._registered:
            raise BlockIDError(f"ID '{id}' is not registered.")

        return self._registered[id]


class Level:
    @staticmethod
    def load_from_file(path: str, block_registry: BlockRegistry):
        with open(path) as f:
            level_data = yaml.safe_load(f)
            level_name = level_data["name"]
            tile_size = level_data["tile_size"]
            level_grid = {}
            for old_key in level_data["grid"]:
                x = int(old_key.split(",")[0])
                y = int(old_key.split(",")[1])
                block_id = level_data["grid"][old_key]
                level_grid[(x, y)] = block_registry.of_id(block_id)

        return Level(level_name, level_grid, tile_size)

    def __init__(self,
            name: str | None,
            grid: dict[tuple[int, int], Block],
            tile_size: int) -> None:
        self.name = name # Use file path if None
        self.grid = grid
        self._tile_size = tile_size

    def draw(self, display: pg.Surface) -> None:
        for pos in self.grid:
            self.__draw_tile(display, pos)

    def __draw_tile(self, display: pg.Surface, grid_pos: tuple[int, int]) -> None:
        pixel_pos = (
            grid_pos[0] * self._tile_size, # x
            grid_pos[1] * self._tile_size) # y
        display.blit(self.grid[grid_pos].img, pixel_pos)


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
        self.terminalvely = 6.0
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

        if self.vely > self.terminalvely:
            self.vely = self.terminalvely

        self.on_ground = False

    def collide_level(self, level: Level, tile_size: int) -> None:
        surround = self.__get_surround(level, tile_size)
        for pos, block in surround.items():
            self.collide_block(block, pos, tile_size)
        # for pos, block in level.grid.items():
        #     self.collide_block(block, pos, tile_size)

    def collide_block(self, block_data: Block, grid_pos: tuple[int, int], tile_size: int) -> None:
        rect = pg.Rect(*grid_to_pixel(grid_pos, tile_size), tile_size, tile_size)
        if block_data.solid:
            self.__collide_solid_block(rect)
        if block_data.on_collide:
            block_data.on_collide()

    def collide_walls_x(self, display_width: int) -> None:
        next_x = self.dest.x + self.velx
        if next_x < 0.0:
            self.dest.left = 0.0
            self.velx = 0.0
        elif next_x + self.dest.w > display_width:
            self.dest.right = display_width
            self.velx = 0.0

    def collide_floor(self, display_height: int) -> None:
        if self.dest.top + self.vely > display_height:
            self.reset()

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

    def __collide_solid_block(self, rect: pg.Rect | pg.FRect) -> None:
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

    def __get_surround(self, level: Level, tile_size: int) -> dict[tuple[int, int], Block]:
        surround: dict[tuple[int, int], Block] = {}
        grid_dest = pixel_to_grid((int(self.dest.x), int(self.dest.y)), tile_size)

        for pos, _ in level.grid.items():
            if (pos[0] >= grid_dest[0] - 2.0
                    and pos[0] <= grid_dest[0] + 2.0
                    and pos[1] >= grid_dest[1] - 2.0
                    and pos[1] <= grid_dest[1] + 2.0):
                surround[pos] = level.grid[pos]

        return surround


def get_axis(input_state: input_sys.InputState, axis: Literal["x", "y"]) -> float:
    if axis.lower() == "x":
        return input_state.events["right"].held - input_state.events["left"].held
    elif axis.lower() == "y":
        return input_state.events["down"].held - input_state.events["up"].held
    else:
        raise ValueError("Why?")


def grid_to_pixel(pos: tuple[int, int], tile_size: int) -> tuple[int, int]:
    return (pos[0] * tile_size, pos[1] * tile_size)


def pixel_to_grid(pos: tuple[int, int], tile_size: int) -> tuple[int, int]:
    x = int(pos[0] // tile_size)
    y = int(pos[1] // tile_size)
    return (x, y)


def pixel_to_grid_float(x: float, tile_size: int) -> float:
    return int(x // tile_size)


def get_real_mouse_pos() -> tuple[int, int]:
    """Gets the mouse position from the perspective of the display instead of the screen."""
    mouse_pos = pg.mouse.get_pos()
    return (mouse_pos[0] // 2, mouse_pos[1] // 2)


def run() -> None:
    args = sys.argv[1:]
    if len(args) > 1:
        raise RuntimeError(f"Invalid argument count; expected: <1, got: {len(args)}")

    with open("config.yaml") as f:
        config: Config = yaml.safe_load(f)

    level_path = __get_args_level_path(args, config)

    if not os.path.isfile(level_path):
        raise RuntimeError(f"File at path '{level_path}' doesn't exist.")

    pg.init()

    FPS_TARGET = 60
    TILE_SIZE = 16

    screen = pg.display.set_mode((640, 480))
    display = pg.Surface((screen.width / 2, screen.height / 2))
    clock = pg.Clock()
    info_font = pg.font.SysFont("Consolas", 10)
    display_info = False
    input_state = input_sys.InputState()

    block_registry = BlockRegistry()

    block_registry.register(Block(
        block_id="stone",
        img=pg.image.load("levels/stone.png").convert(),
        solid=True))

    block_registry.register(Block(
        block_id="grass_blades",
        img=pg.image.load("levels/grass_blades.png").convert(),
        solid=False))

    block_registry.register(Block(
        block_id="rock",
        img=pg.image.load("levels/rock.png").convert(),
        solid=False))

    block_registry.register(Block(
        block_id="rock_flipped",
        img=pg.transform.flip(pg.image.load("levels/rock.png").convert(), True, False),
        solid=False))

    player = Player(20.0, 20.0)
    level = Level.load_from_file(level_path, block_registry)

    while True:
        input_state.update()

        if input_state.events["r"].just_pressed:
            player.reset()
        if input_state.events["i"].just_pressed:
            display_info = not display_info

        player.update_independent_movement(input_state)
        player.collide_walls_x(display.get_width())
        player.collide_floor(display.get_height())
        player.collide_level(level, TILE_SIZE)
        player.apply_vel()

        display.fill("black")
        level.draw(display)
        pos = (player.dest.x + player.img_offset[0], player.dest.y + player.img_offset[1])
        display.blit(player.img, pos)

        if display_info:
            mouse_grid_pos = pixel_to_grid(get_real_mouse_pos(), TILE_SIZE)
            text = info_font.render(
                f"lvlname: {level.name}\n" \
                f"mousegridpos: {mouse_grid_pos}\n" \
                f"playerx: {player.dest.x:.4f}, vel: {player.velx}\n" \
                f"playery: {player.dest.y:.4f}, vel: {player.vely}\n" \
                f"playergrid: {pixel_to_grid((int(player.dest.x), int(player.dest.y)), TILE_SIZE)}" \
                , True, "white")
            display.blit(text, (5, 5))

        screen.blit(pg.transform.scale(display, screen.get_size()))
        clock.tick(FPS_TARGET)
        pg.display.update()


def __get_args_level_path(args: list[str], config: Config):
    try:
        return args[0]
    except IndexError:
        return config["default_level"]


if __name__ == "__main__":
    run()
