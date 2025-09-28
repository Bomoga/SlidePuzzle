"""Convenience helpers to run the slide puzzle solver from the command line."""

from __future__ import annotations

from typing import Iterable, Sequence

from src.slide_puzzle.puzzle import SlidePuzzleState, solve_puzzle


def state_from_rows(rows: Sequence[Sequence[int]]) -> SlidePuzzleState:
    size = len(rows)
    flat: list[int] = []
    for row in rows:
        if len(row) != size:
            raise ValueError("Rows must form a square grid")
        flat.extend(row)
    return SlidePuzzleState.from_sequence(size, flat)


def solve_from_rows(rows: Sequence[Sequence[int]]) -> Iterable[int]:
    state = state_from_rows(rows)
    return solve_puzzle(state)


if __name__ == "__main__":
    start = SlidePuzzleState.solved(3).shuffle(30)
    solution = solve_puzzle(start)
    print("Start:", start.tiles)
    print("Moves (tile numbers):", solution)
    print("Solution length:", len(solution))
