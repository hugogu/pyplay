"""
Turtle Maze Generator
---------------------
Generates a random perfect maze (i.e. a maze with *exactly one* path between any
 two cells) using a depth-first search (recursive back-tracker) algorithm and
 draws it with the `turtle` module.

The generator is fully parameterised:
    rows, cols        ‑ size of the maze in cells.
    cell_size         ‑ pixel size of one cell.
    complexity (0-1)  ‑ how twisty the passages are. 0 produces long tunnels
                        (easy), 1 produces many short branches (hard).
    difficulty (0-1)  ‑ how far apart *start* and *end* points are. 0 puts them
                        near each other, 1 uses the two ends of the maze’s
                        diameter to maximise path length.

Each invocation creates a brand-new maze thanks to Python’s `random` module.
Because the underlying structure is a spanning-tree (no loops), the maze always
has exactly one solution.

Run this file directly to see a demo::

    python turtle_maze_generator.py

Press the turtle window’s *close* button or hit ⌘-Q/ALT-F4 to quit.
"""
from __future__ import annotations

import random
import turtle
from collections import deque
from typing import Dict, List, Tuple

# Wall identifiers used inside each cell dictionary
N, S, E, W = "N", "S", "E", "W"
OPPOSITE = {N: S, S: N, E: W, W: E}
DIR_VEC = {N: (-1, 0), S: (1, 0), E: (0, 1), W: (0, -1)}  # row, col diffs


class MazeGenerator:
    """Generate and draw perfect mazes with Turtle graphics."""

    def __init__(
        self,
        rows: int = 20,
        cols: int = 20,
        *,
        cell_size: int = 20,
        complexity: float = 0.75,
        difficulty: float = 0.75,
    ) -> None:
        if rows < 2 or cols < 2:
            raise ValueError("Maze must have at least 2×2 cells")
        if not 0 <= complexity <= 1:
            raise ValueError("complexity must be between 0 and 1")
        if not 0 <= difficulty <= 1:
            raise ValueError("difficulty must be between 0 and 1")

        self.rows, self.cols = rows, cols
        self.cell_size = cell_size
        self.complexity = complexity
        self.difficulty = difficulty

        # Grid initialisation. Every cell starts with all four walls intact.
        self.grid: List[List[Dict[str, bool]]] = [
            [{N: True, S: True, E: True, W: True} for _ in range(cols)]
            for _ in range(rows)
        ]

        # Public attributes describing entrance/exit once generated
        self.start: Tuple[int, int] | None = None
        self.end: Tuple[int, int] | None = None

    # ---------------------------------------------------------------------
    #  MAZE GENERATION (RECURSIVE BACK-TRACKER)
    # ---------------------------------------------------------------------
    def _unvisited_neighbours(self, r: int, c: int, visited: List[List[bool]]):
        """Return list of (nr, nc, dir_from_current, dir_from_neighbour)."""
        neighbours = []
        for direction, (dr, dc) in DIR_VEC.items():
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols and not visited[nr][nc]:
                neighbours.append((nr, nc, direction, OPPOSITE[direction]))
        # *complexity* controls how much we shuffle: more shuffle ⇒ twistier.
        shuffle_portion = int(len(neighbours) * self.complexity)
        random.shuffle(neighbours[:shuffle_portion])
        return neighbours

    def _carve_passage(self, start_r: int, start_c: int) -> None:
        """Iterative version of the maze carving algorithm using an explicit stack"""
        visited = [[False] * self.cols for _ in range(self.rows)]
        stack = [(start_r, start_c)]
        visited[start_r][start_c] = True
        
        while stack:
            r, c = stack[-1]  # Get current cell, but don't pop yet
            
            neighbours = self._unvisited_neighbours(r, c, visited)
            if neighbours:
                # Bias: with high *complexity* pick random neighbour, otherwise take first
                nr, nc, here_dir, there_dir = (
                    random.choice(neighbours) if random.random() < self.complexity else neighbours[0]
                )
                # Knock down the shared wall
                self.grid[r][c][here_dir] = False
                self.grid[nr][nc][there_dir] = False
                # Mark as visited and add to stack
                visited[nr][nc] = True
                stack.append((nr, nc))
            else:
                # No unvisited neighbors, backtrack
                stack.pop()

    def _longest_path_endpoints(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Return approximate diameter endpoints of the tree via double-BFS."""

        def bfs(start: Tuple[int, int]):
            sr, sc = start
            dist = [[-1] * self.cols for _ in range(self.rows)]
            dist[sr][sc] = 0
            q = deque([start])
            parent: Dict[Tuple[int, int], Tuple[int, int]] = {}
            farthest = start
            while q:
                r, c = q.popleft()
                farthest = max(farthest, (r, c), key=lambda rc: dist[rc[0]][rc[1]])
                for direction, (dr, dc) in DIR_VEC.items():
                    if self.grid[r][c][direction]:
                        continue  # wall in that direction
                    nr, nc = r + dr, c + dc
                    if dist[nr][nc] == -1:
                        dist[nr][nc] = dist[r][c] + 1
                        parent[(nr, nc)] = (r, c)
                        q.append((nr, nc))
            return farthest, dist, parent

        end_a, *_ = bfs((0, 0))
        end_b, *_ = bfs(end_a)
        return end_a, end_b

    def generate(self) -> None:
        """Create a new maze in `self.grid` and set start/end."""
        start_r, start_c = random.randrange(self.rows), random.randrange(self.cols)
        self._carve_passage(start_r, start_c)

        # Choose entrance/exit according to *difficulty*
        if self.difficulty < 0.1:
            self.start, self.end = (0, 0), (1, 1)
        elif self.difficulty < 0.5:
            self.start, self.end = (0, 0), (self.rows - 1, self.cols - 1)
        else:
            # Use diameter endpoints for maximum path length.
            self.start, self.end = self._longest_path_endpoints()

    # ---------------------------------------------------------------------
    #  DRAWING WITH TURTLE
    # ---------------------------------------------------------------------
    def _draw_line(self, t: turtle.Turtle, x1: float, y1: float, x2: float, y2: float):
        t.penup()
        t.goto(x1, y1)
        t.pendown()
        t.goto(x2, y2)

    def draw(self) -> None:
        """Generate (if necessary) and draw the maze in a Turtle window."""

        if self.start is None or self.end is None:
            self.generate()

        # Turtle setup ----------------------------------------------------
        t = turtle.Turtle()
        t.hideturtle()
        t.speed(0)
        t.pensize(2)
        screen = turtle.Screen()
        screen.tracer(False)  # fast drawing

        offset_x = -self.cols * self.cell_size / 2
        offset_y = self.rows * self.cell_size / 2

        # Draw outer border ----------------------------------------------
        self._draw_line(
            t,
            offset_x,
            offset_y,
            offset_x + self.cols * self.cell_size,
            offset_y,
        )  # top
        self._draw_line(
            t,
            offset_x,
            offset_y - self.rows * self.cell_size,
            offset_x + self.cols * self.cell_size,
            offset_y - self.rows * self.cell_size,
        )  # bottom
        self._draw_line(
            t,
            offset_x,
            offset_y,
            offset_x,
            offset_y - self.rows * self.cell_size,
        )  # left
        self._draw_line(
            t,
            offset_x + self.cols * self.cell_size,
            offset_y,
            offset_x + self.cols * self.cell_size,
            offset_y - self.rows * self.cell_size,
        )  # right

        # Draw internal walls --------------------------------------------
        for r in range(self.rows):
            for c in range(self.cols):
                x = offset_x + c * self.cell_size
                y = offset_y - r * self.cell_size
                cell = self.grid[r][c]

                if cell[N]:
                    self._draw_line(t, x, y, x + self.cell_size, y)
                if cell[W]:
                    self._draw_line(t, x, y, x, y - self.cell_size)
                # Draw southern & eastern walls for bottom/last column cells only
                if r == self.rows - 1 and cell[S]:
                    self._draw_line(
                        t, x, y - self.cell_size, x + self.cell_size, y - self.cell_size
                    )
                if c == self.cols - 1 and cell[E]:
                    self._draw_line(
                        t, x + self.cell_size, y, x + self.cell_size, y - self.cell_size
                    )

        # Mark entrance and exit -----------------------------------------
        def mark_cell(rc: Tuple[int, int], colour: str):
            rr, cc = rc
            cx = offset_x + cc * self.cell_size + self.cell_size / 2
            cy = offset_y - rr * self.cell_size - self.cell_size / 2
            t.penup()
            t.goto(cx, cy - self.cell_size / 4)
            t.pendown()
            t.color(colour)
            t.begin_fill()
            for _ in range(4):
                t.forward(self.cell_size / 2)
                t.left(90)
            t.end_fill()
            t.color("black")

        mark_cell(self.start, "green")
        mark_cell(self.end, "red")

        screen.tracer(True)
        screen.mainloop()


# -------------------------------------------------------------------------
#  DEMO
# -------------------------------------------------------------------------
if __name__ == "__main__":
    random.seed()  # ensure different maze each run

    # You can tweak these parameters or expose them via argparse.
    maze = MazeGenerator(
        rows=25,
        cols=25,
        cell_size=18,
        complexity=0.75,
        difficulty=0.9,
    )
    maze.draw()
