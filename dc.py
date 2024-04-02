from __future__ import annotations
import os
import sys
from dataclasses import dataclass

import pygame as pg
import random

# Constants
FILE_PATH_TILES: list[str] = [
    "grass-1.png",
    "grass-2.png",
    "rock.png",  # the last element is a wall and cannot be passed through
]

FILE_PATH_PLAYER = "player.png"

TILE_COUNT = len(FILE_PATH_TILES)

SC_WIDTH = 1100
SC_HEIGHT = 1000

SC_CANVAS_HEIGHT = 300

RATIO = 10

DISP_WIDTH = SC_WIDTH // RATIO
DISP_HEIGHT = (SC_HEIGHT - SC_CANVAS_HEIGHT) // RATIO

TILE_SIZE = 10

LEVEL_COLS = DISP_WIDTH // TILE_SIZE
LEVEL_ROWS = DISP_HEIGHT // TILE_SIZE

@dataclass
class CharaProp(object):
    HP: int
    MAX_HP: int
    ATK: int
    DFS: int

    def copy(self) -> CharaProp:
        return CharaProp(self.HP, self.MAX_HP, self.ATK, self.DFS)

class Player(object):
    def __init__(self, row: int, col: int, img: pg.Surface, prop: CharaProp) -> None:
        self.img = img
        self.row = row
        self.col = col
        self.prop = prop.copy()

class Tile(object):
    def __init__(self, row: int, col: int, img: pg.Surface, is_movable: bool = True) -> None:
        self.img = img
        self.row = row
        self.col = col
        self.is_movable = is_movable

class Level(object):
    def __init__(self, rows: int, cols: int, tile_size: int) -> None:
        self.inner: list[list[Tile | None]] = [[None] * cols for _ in range(rows)]
        self.rows = rows
        self.cols = cols
        self.tile_size = tile_size

    def draw(self, surf: pg.Surface) -> None:
        for tiles in self.inner:
            for tile in tiles:
                if surf:
                    surf.blit(tile.img, (tile.col * self.tile_size, tile.row * self.tile_size))

    def set_at(self, row: int, col: int, tile: Tile) -> None:
        self.inner[row][col] = tile

    def get_at(self, row: int, col: int) -> Tile:
        return self.inner[row][col]

    @classmethod
    def generate(cls, rows: int, cols: int, tiles: list[pg.Surface], tile_size: int) -> Level:
        temp_level = [[0] * cols for _ in range(rows)]

        for col in range(cols):
            temp_level[0][col] = 1
            temp_level[rows - 1][col] = 1

        for row in range(rows):
            temp_level[row][0] = 1
            temp_level[row][cols - 1] = 1

        for row in range(2, rows - 2, 2):
            for col in range(2, cols - 2, 2):
                temp_level[row][col] = 1

        for row in range(2, rows - 2, 2):
            for col in range(2, cols - 2, 2):
                d = [[0, 1], [0, -1], [1, 0], [-1, 0]]
                if row == 2:
                    d = [[0, 1], [0, -1], [1, 0]]
                r_num = random.randrange(0, len(d))

                d_col = d[r_num][0]
                d_row = d[r_num][1]

                temp_level[row + d_row][col + d_col] = 1

        # Create Actual Level
        level = cls(rows, cols, tile_size)
        for row in range(rows):
            for col in range(cols):
                if temp_level[row][col] == 1:
                    index = len(FILE_PATH_TILES) - 1
                    tile = Tile(row, col, tiles[index].copy(), is_movable=False)
                else:
                    index = random.randrange(0, len(FILE_PATH_TILES) - 1)
                    tile = Tile(row, col, tiles[index].copy())
                level.set_at(row, col, tile)

        return level

# Functions
def load_graphic(path: str) -> pg.Surface:
    return pg.image.load(os.path.join("graphics", path)).convert_alpha()

def load_graphics(src: list[str]) -> list[pg.Surface]:
    c = []
    for i in range(len(src)):
        path = src[i]
        c.append(load_graphic(path))

    return c


def main() -> None:
    pg.init()
    random.seed(69)
    sc = pg.display.set_mode((SC_WIDTH, SC_HEIGHT))
    disp = pg.Surface((SC_WIDTH / RATIO, SC_HEIGHT / RATIO))
    is_killed = False
    clock = pg.Clock()

    # Initialize Game
    graphics = load_graphics(FILE_PATH_TILES)
    level = Level.generate(LEVEL_ROWS, LEVEL_COLS, graphics, TILE_SIZE)
    p = Player(
        1, 1,
        load_graphic(FILE_PATH_PLAYER),
        CharaProp(100, 100, 15, 7),
    )

    while not is_killed:
        for event in pg.event.get():
            # Quit pygame
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_q:
                is_killed = True

            # Press Key
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    # Can player move?
                    if p.row - 1 >= 0 and level.get_at(p.row - 1, p.col).is_movable:
                        p.row -= 1
                elif event.key == pg.K_DOWN:
                    # Can player move?
                    if p.row + 1 < level.rows and level.get_at(p.row + 1, p.col).is_movable:
                        p.row += 1

                elif event.key == pg.K_LEFT:
                    # Can player move?
                    if p.col - 1 >= 0 and level.get_at(p.row, p.col - 1).is_movable:
                        p.col -= 1
                elif event.key == pg.K_RIGHT:
                    # Can player move?
                    if p.col + 1 < level.cols and level.get_at(p.row, p.col + 1).is_movable:
                        p.col += 1

        clock.tick(30)

        level.draw(disp)

        disp.blit(p.img, (p.col * TILE_SIZE, p.row * TILE_SIZE))

        scaled_disp = pg.transform.scale(disp, (SC_WIDTH, SC_HEIGHT))
        sc.blit(scaled_disp, (0, 0))
        pg.display.update()

    pg.quit()
    sys.exit()


if __name__ == '__main__':
    main()
