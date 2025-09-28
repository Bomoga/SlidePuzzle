from __future__ import annotations

from dataclasses import dataclass
from heapq import heappop, heappush
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
import random


@dataclass(frozen=True)
class SlidePuzzleState:
    """An immutable representation of an n x n sliding puzzle state."""

    size: int
    tiles: Tuple[int, ...]

    def __post_init__(self) -> None:
        if len(self.tiles) != self.size * self.size:
            raise ValueError("Tile collection length does not match puzzle dimensions")
        expected = set(range(self.size * self.size))
        missing = expected.difference(self.tiles)
        if missing:
            raise ValueError(f"State missing tiles: {sorted(missing)}")

    @property
    def blank_index(self) -> int:
        return self.tiles.index(0)

    def index_of(self, tile: int) -> int:
        return self.tiles.index(tile)

    def coordinates(self, index: int) -> Tuple[int, int]:
        return divmod(index, self.size)

    def manhattan_distance(self) -> int:
        goal_positions = {value: idx for idx, value in enumerate(range(1, self.size * self.size))}
        total = 0
        for idx, value in enumerate(self.tiles):
            if value == 0:
                continue
            goal_idx = goal_positions[value]
            gx, gy = divmod(goal_idx, self.size)
            cx, cy = self.coordinates(idx)
            total += abs(gx - cx) + abs(gy - cy)
        return total

    def is_solved(self) -> bool:
        return self.tiles == tuple(range(1, self.size * self.size)) + (0,)

    def swap(self, idx_a: int, idx_b: int) -> "SlidePuzzleState":
        tiles_list = list(self.tiles)
        tiles_list[idx_a], tiles_list[idx_b] = tiles_list[idx_b], tiles_list[idx_a]
        return SlidePuzzleState(self.size, tuple(tiles_list))

    def move_blank(self, dx: int, dy: int) -> Optional["SlidePuzzleState"]:
        row, col = self.coordinates(self.blank_index)
        nr, nc = row + dx, col + dy
        if 0 <= nr < self.size and 0 <= nc < self.size:
            target = nr * self.size + nc
            return self.swap(self.blank_index, target)
        return None

    def move_tile(self, tile: int) -> Optional["SlidePuzzleState"]:
        tile_index = self.index_of(tile)
        br, bc = self.coordinates(self.blank_index)
        tr, tc = self.coordinates(tile_index)
        if abs(br - tr) + abs(bc - tc) != 1:
            return None
        return self.swap(self.blank_index, tile_index)

    def legal_moves(self) -> Iterable[Tuple[int, "SlidePuzzleState"]]:
        row, col = self.coordinates(self.blank_index)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dx, col + dy
            if 0 <= nr < self.size and 0 <= nc < self.size:
                idx = nr * self.size + nc
                tile = self.tiles[idx]
                yield tile, self.swap(self.blank_index, idx)

    def iter_tiles(self) -> Iterable[int]:
        return iter(self.tiles)

    @staticmethod
    def solved(size: int) -> "SlidePuzzleState":
        values = tuple(range(1, size * size)) + (0,)
        return SlidePuzzleState(size, values)

    @staticmethod
    def from_sequence(size: int, sequence: Sequence[int]) -> "SlidePuzzleState":
        return SlidePuzzleState(size, tuple(sequence))

    def shuffle(self, moves: int = 100, rng: Optional[random.Random] = None) -> "SlidePuzzleState":
        rng = rng or random.Random()
        state = self
        last_tile = None
        for _ in range(moves):
            options = list(state.legal_moves())
            if last_tile is not None:
                options = [item for item in options if item[0] != last_tile]
                if not options:
                    options = list(state.legal_moves())
            tile, state = rng.choice(options)
            last_tile = tile
        return state


def reconstruct_path(came_from: Dict[SlidePuzzleState, Tuple[SlidePuzzleState, int]], goal: SlidePuzzleState) -> List[int]:
    moves: List[int] = []
    current = goal
    while current in came_from:
        prev_state, tile = came_from[current]
        moves.append(tile)
        current = prev_state
    moves.reverse()
    return moves


def solve_puzzle(start: SlidePuzzleState) -> List[int]:
    """Return a sequence of tile numbers that solve the puzzle via A* search."""

    if start.is_solved():
        return []

    goal = SlidePuzzleState.solved(start.size)
    frontier: List[Tuple[int, int, SlidePuzzleState]] = []
    counter = 0
    heappush(frontier, (start.manhattan_distance(), counter, start))
    came_from: Dict[SlidePuzzleState, Tuple[SlidePuzzleState, int]] = {}
    g_score: Dict[SlidePuzzleState, int] = {start: 0}

    while frontier:
        _, _, current = heappop(frontier)
        if current == goal:
            return reconstruct_path(came_from, current)

        current_cost = g_score[current]
        for tile, neighbor in current.legal_moves():
            tentative = current_cost + 1
            if tentative < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = (current, tile)
                g_score[neighbor] = tentative
                counter += 1
                priority = tentative + neighbor.manhattan_distance()
                heappush(frontier, (priority, counter, neighbor))

    raise ValueError("Puzzle is unsolvable from the provided state")
