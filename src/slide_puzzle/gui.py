from __future__ import annotations

import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Dict, List, Optional

from PIL import ImageTk

from .image_slicer import slice_image
from .puzzle import SlidePuzzleState, solve_puzzle


class SlidePuzzleApp(tk.Tk):
    def __init__(self, grid_size: int = 3, tile_pixels: int = 150) -> None:
        super().__init__()
        self.title("Slide Puzzle")
        self.resizable(True, True)

        self.grid_size = grid_size
        self.tile_pixels = tile_pixels

        self.state: Optional[SlidePuzzleState] = None
        self.photo_cache: Dict[int, ImageTk.PhotoImage] = {}
        self.buttons: List[tk.Button] = []
        self._solving = False

        self.status_var = tk.StringVar(value="Upload an image!!")

        self._build_widgets()

    def _build_widgets(self) -> None:
        controls = tk.Frame(self)
        controls.pack(padx=10, pady=10)

        tk.Button(controls, text="Upload Image", command=self.load_image).grid(row=0, column=0, padx=5)
        self.shuffle_btn = tk.Button(controls, text="Shuffle", command=self.shuffle, state=tk.DISABLED)
        self.shuffle_btn.grid(row=0, column=1, padx=5)
        self.solve_btn = tk.Button(controls, text="Solve", command=self.solve, state=tk.DISABLED)
        self.solve_btn.grid(row=0, column=2, padx=5)

        status_label = tk.Label(self, textvariable=self.status_var)
        status_label.pack(pady=(0, 10))

        self.board = tk.Frame(self, bg="#222", bd=2, relief=tk.SUNKEN)
        self.board.pack(padx=10, pady=(0, 10))

        for idx in range(self.grid_size * self.grid_size):
            button = tk.Button(
                self.board,
                command=lambda index=idx: self.on_tile_click(index),
                relief=tk.RAISED,
                bd=1,
            )
            row, col = divmod(idx, self.grid_size)
            button.grid(row=row, column=col, padx=2, pady=2)
            self.buttons.append(button)

    def load_image(self) -> None:
        if self._solving:
            return
        path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            pil_tiles = slice_image(path, grid_size=self.grid_size, tile_pixels=self.tile_pixels)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("Image Error", f"Failed to load image: {exc}")
            return

        self.photo_cache = {tile: ImageTk.PhotoImage(image) for tile, image in pil_tiles.items()}
        self.state = SlidePuzzleState.solved(self.grid_size)
        self.state = self.state.shuffle(moves=80)
        self.status_var.set("Puzzle shuffled. Click tiles adjacent to the blank space.")
        self.shuffle_btn.config(state=tk.NORMAL)
        self.solve_btn.config(state=tk.NORMAL)
        self.render_board()

    def render_board(self) -> None:
        if self.state is None:
            return
        for idx, tile in enumerate(self.state.tiles):
            button = self.buttons[idx]
            if tile == 0:
                blank_image = self.photo_cache.get(0)
                button.config(
                    image=blank_image,
                    text="" if blank_image else " ",
                    state=tk.DISABLED,
                    bg="#111",
                )
            else:
                tile_image = self.photo_cache.get(tile)
                button.config(
                    image=tile_image,
                    text="" if tile_image else str(tile),
                    state=tk.NORMAL,
                    bg="white",
                )

    def on_tile_click(self, index: int) -> None:
        if self.state is None or self._solving:
            return
        tile = self.state.tiles[index]
        if tile == 0:
            return
        next_state = self.state.move_tile(tile)
        if next_state is None:
            return
        self.state = next_state
        self.render_board()
        if self.state.is_solved():
            self.status_var.set("YOU WIN! You get no prize, sorry.")

    def shuffle(self) -> None:
        if self.state is None or self._solving:
            return
        self.state = SlidePuzzleState.solved(self.grid_size).shuffle(moves=120)
        self.status_var.set("I like my puzzles the way I like my eggs... scrambled.")
        self.render_board()

    def solve(self) -> None:
        if self.state is None or self._solving:
            return
        if self.state.is_solved():
            self.status_var.set("Already solved, dude. Scramble it or something.")
            return
        self._solving = True
        self.shuffle_btn.config(state=tk.DISABLED)
        self.solve_btn.config(state=tk.DISABLED)
        self.status_var.set("Fine, i'll solve it if you're that lazy.")

        thread = threading.Thread(target=self._solve_thread, daemon=True)
        thread.start()

    def _solve_thread(self) -> None:
        assert self.state is not None
        try:
            moves = solve_puzzle(self.state)
        except Exception as exc:  # noqa: BLE001
            self.after(0, lambda: self._on_solve_failed(exc))
            return
        self.after(0, lambda: self._animate_solution(moves))

    def _on_solve_failed(self, exc: Exception) -> None:
        self.status_var.set(f"Sorry dude, solver failed: {exc}")
        self.shuffle_btn.config(state=tk.NORMAL)
        self.solve_btn.config(state=tk.NORMAL)
        self._solving = False

    def _animate_solution(self, moves: List[int], delay_ms: int = 200) -> None:
        if self.state is None:
            return
        if not moves:
            self.status_var.set("Solved!")
            self.shuffle_btn.config(state=tk.NORMAL)
            self.solve_btn.config(state=tk.NORMAL)
            self._solving = False
            return
        tile = moves.pop(0)
        next_state = self.state.move_tile(tile)
        if next_state is None:
            self.status_var.set("Solver encountered an invalid move.")
            self.shuffle_btn.config(state=tk.NORMAL)
            self.solve_btn.config(state=tk.NORMAL)
            self._solving = False
            return
        self.state = next_state
        self.render_board()
        self.after(delay_ms, lambda: self._animate_solution(moves, delay_ms))


__all__ = ["SlidePuzzleApp"]

