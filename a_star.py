grid = [[0, 0, 0, 1, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 0],
        [1, 0, 1, 1, 0],
        [1, 0, 0, 1, 0],
        [1, 1, 1, 1, 0],
        [0, 0, 0, 0, 0]]

ROWS = len(grid)
COLS = len(grid[0])

def manhattan(a, b):
    (x1, y1), (x2, y2) = a, b
    return abs(x1 - x2) + abs(y1 - y2)

def neighbors(r, c):
    for nr, nc in [(r-1,c), (r+1,c), (r, c-1), (r,c+1)]:
        if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nc][nr] == 0:
            yield (nr, nc)

def findShortest(grid):
    start = (0, 0)
    goal = (6, 4)

    


    