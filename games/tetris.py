# --- games/tetris.py ---
# Classic Tetris game logic for the tricorder

import pygame
import random
import logging

logger = logging.getLogger(__name__)

# --- Game Constants ---
COLS = 10
VISIBLE_ROWS = 20
CELL_SIZE = 24  # Will be scaled to fit; minimum cell size
INITIAL_FALL_DELAY = 45  # Frames per row (lower = faster)
LEVEL_ACCEL = 4  # Frames faster per level
MIN_FALL_DELAY = 4

# Standard tetromino shapes (row-major; 1 = filled). Each is a list of 4 (row,col) offsets from origin.
# I, O, T, S, Z, J, L
SHAPES = [
    [(0, 0), (0, 1), (0, 2), (0, 3)],   # I
    [(0, 0), (0, 1), (1, 0), (1, 1)],   # O
    [(0, 1), (1, 0), (1, 1), (1, 2)],   # T
    [(0, 1), (0, 2), (1, 0), (1, 1)],   # S
    [(0, 0), (0, 1), (1, 1), (1, 2)],   # Z
    [(0, 0), (1, 0), (1, 1), (1, 2)],   # J
    [(0, 2), (1, 0), (1, 1), (1, 2)],   # L
]
# Tricorder-friendly colors per shape index (I,O,T,S,Z,J,L)
SHAPE_COLORS = [
    (0, 255, 200),   # I - cyan
    (255, 255, 0),   # O - yellow
    (180, 100, 255), # T - purple
    (0, 255, 100),   # S - green
    (255, 80, 80),   # Z - red
    (80, 120, 255),  # J - blue
    (255, 160, 0),   # L - orange
]


def _rotate_cw(cells):
    """Rotate list of (r,c) 90° clockwise: (r,c) -> (c, -r). Normalize to min row/col 0."""
    rotated = [(c, -r) for (r, c) in cells]
    min_r = min(r for r, _ in rotated)
    min_c = min(c for _, c in rotated)
    return [(r - min_r, c - min_c) for (r, c) in rotated]


def _rotate_ccw(cells):
    """Rotate list of (r,c) 90° counter-clockwise: (r,c) -> (-c, r)."""
    rotated = [(-c, r) for (r, c) in cells]
    min_r = min(r for r, _ in rotated)
    min_c = min(c for _, c in rotated)
    return [(r - min_r, c - min_c) for (r, c) in rotated]


class TetrisGame:
    """Manages the state and logic for Tetris."""

    def __init__(self, width, height, config):
        self.width = width
        self.height = height
        self.config = config
        self.font = None

        # Grid: extra rows above visible for spawn; (row, col) = 0..COLS-1, row 0 = top
        self.total_rows = VISIBLE_ROWS + 4
        self.grid = []  # list of (color or None) per cell: grid[row][col]
        self._init_grid()

        # Cell size to fit play area (leave margin for score/hints)
        self.margin_x = 16
        self.margin_y = 40
        play_w = width - 2 * self.margin_x
        play_h = height - self.margin_y - 20
        self.cell_w = max(8, min(play_w // COLS, play_h // self.total_rows))
        self.cell_h = self.cell_w
        self.board_pixel_w = COLS * self.cell_w
        self.board_pixel_h = self.total_rows * self.cell_h
        self.board_left = self.margin_x + (play_w - self.board_pixel_w) // 2
        self.board_top = self.margin_y

        # Current piece: list of (row, col) in grid coords, color index
        self.piece_cells = []
        self.piece_color_idx = 0
        self.piece_row = 0
        self.piece_col = 0

        # Next piece (for preview)
        self.next_piece_idx = random.randint(0, len(SHAPES) - 1)

        # Timing
        self.fall_counter = 0
        self.fall_delay = INITIAL_FALL_DELAY

        # State
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
        self.winner_message = ""
        self.paused = False
        self.pause_menu_options = ["Resume", "Quit to Menu"]
        self.pause_menu_selected_index = 0

        self._spawn_piece()
        logger.info(f"Tetris game initialized {width}x{height}, grid {COLS}x{self.total_rows}, cell {self.cell_w}x{self.cell_h}")

    def _init_grid(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(self.total_rows)]

    def _spawn_piece(self):
        """Spawn next piece at top-center. Returns False if overlap (game over)."""
        self.piece_cells = [list(c) for c in SHAPES[self.next_piece_idx]]
        self.piece_color_idx = self.next_piece_idx
        self.next_piece_idx = random.randint(0, len(SHAPES) - 1)
        self.piece_row = 0
        self.piece_col = (COLS - self._piece_width()) // 2
        if self._piece_collides():
            self.game_over = True
            self.winner_message = "GAME OVER"
            logger.info("Tetris game over - blocked at spawn")
            return False
        return True

    def _piece_width(self):
        if not self.piece_cells:
            return 0
        return max(c for _, c in self.piece_cells) + 1

    def _piece_collides(self):
        for (dr, dc) in self.piece_cells:
            r, c = self.piece_row + dr, self.piece_col + dc
            if c < 0 or c >= COLS or r >= self.total_rows:
                return True
            if r >= 0 and self.grid[r][c] is not None:
                return True
        return False

    def _lock_piece(self):
        """Lock current piece into grid and spawn next."""
        color = SHAPE_COLORS[self.piece_color_idx]
        for (dr, dc) in self.piece_cells:
            r, c = self.piece_row + dr, self.piece_col + dc
            if 0 <= r < self.total_rows and 0 <= c < COLS:
                self.grid[r][c] = color
        self._clear_lines()
        self._spawn_piece()

    def _clear_lines(self):
        """Clear full lines and add score."""
        cleared = 0
        row = self.total_rows - 1
        while row >= 0:
            if all(self.grid[row][c] is not None for c in range(COLS)):
                cleared += 1
                del self.grid[row]
                self.grid.insert(0, [None] * COLS)
                # don't advance row; check same index again
            else:
                row -= 1
        if cleared > 0:
            self.lines_cleared += cleared
            # 100, 300, 500, 800 per 1,2,3,4 lines * level
            points = [0, 100, 300, 500, 800][cleared] * self.level
            self.score += points
            self.level = 1 + self.lines_cleared // 10
            self.fall_delay = max(MIN_FALL_DELAY, INITIAL_FALL_DELAY - (self.level - 1) * LEVEL_ACCEL)
            logger.debug(f"Tetris cleared {cleared} lines, score += {points}, level {self.level}")

    def move_left(self):
        if self.game_over or self.paused:
            return
        self.piece_col -= 1
        if self._piece_collides():
            self.piece_col += 1

    def move_right(self):
        if self.game_over or self.paused:
            return
        self.piece_col += 1
        if self._piece_collides():
            self.piece_col -= 1

    def rotate_cw(self):
        if self.game_over or self.paused:
            return
        old = [list(c) for c in self.piece_cells]
        self.piece_cells = _rotate_cw(self.piece_cells)
        if self._piece_collides():
            self.piece_cells = old

    def rotate_ccw(self):
        if self.game_over or self.paused:
            return
        old = [list(c) for c in self.piece_cells]
        self.piece_cells = _rotate_ccw(self.piece_cells)
        if self._piece_collides():
            self.piece_cells = old

    def soft_drop(self):
        """Move piece down one row; if lock, lock and spawn. Returns True if locked."""
        if self.game_over or self.paused:
            return False
        self.piece_row += 1
        if self._piece_collides():
            self.piece_row -= 1
            self._lock_piece()
            return True
        self.score += 1  # 1 point per soft drop
        return False

    def hard_drop(self):
        """Drop piece to bottom and lock."""
        if self.game_over or self.paused:
            return
        while not self._piece_collides():
            self.piece_row += 1
        self.piece_row -= 1
        self.score += 2 * (self.piece_row + sum(dr for dr, _ in self.piece_cells))  # bonus for height
        self._lock_piece()

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.pause_menu_selected_index = 0
        logger.info(f"Tetris game {'paused' if self.paused else 'resumed'}.")

    def navigate_pause_menu_up(self):
        if self.paused and self.pause_menu_options:
            self.pause_menu_selected_index = (self.pause_menu_selected_index - 1 + len(self.pause_menu_options)) % len(self.pause_menu_options)

    def navigate_pause_menu_down(self):
        if self.paused and self.pause_menu_options:
            self.pause_menu_selected_index = (self.pause_menu_selected_index + 1) % len(self.pause_menu_options)

    def select_pause_menu_option(self):
        if not self.paused or not self.pause_menu_options or self.pause_menu_selected_index >= len(self.pause_menu_options):
            return None
        opt = self.pause_menu_options[self.pause_menu_selected_index]
        if opt == "Resume":
            self.toggle_pause()
            return "RESUME_GAME"
        if opt == "Quit to Menu":
            return "QUIT_TO_MENU"
        return None

    def update(self, keys_held):
        if self.game_over or self.paused:
            return
        self.fall_counter += 1
        if self.fall_counter >= self.fall_delay:
            self.fall_counter = 0
            self.piece_row += 1
            if self._piece_collides():
                self.piece_row -= 1
                self._lock_piece()

    def draw(self, screen, fonts, config_module):
        if not self.font:
            self.font = fonts.get('medium', fonts.get('default'))

        # Board background
        board_rect = pygame.Rect(self.board_left, self.board_top, self.board_pixel_w, self.board_pixel_h)
        pygame.draw.rect(screen, config_module.COLOR_BACKGROUND, board_rect)
        pygame.draw.rect(screen, config_module.COLOR_GRAPH_BORDER, board_rect, 2)

        # Grid cells (only visible rows)
        for row in range(self.total_rows):
            for col in range(COLS):
                color = self.grid[row][col]
                if color is not None:
                    x = self.board_left + col * self.cell_w
                    y = self.board_top + row * self.cell_h
                    rect = pygame.Rect(x + 1, y + 1, self.cell_w - 2, self.cell_h - 2)
                    pygame.draw.rect(screen, color, rect)
                    # Highlight
                    highlight = tuple(min(255, c + 50) for c in color)
                    pygame.draw.line(screen, highlight, (rect.left, rect.top), (rect.right, rect.top), 1)
                    pygame.draw.line(screen, highlight, (rect.left, rect.top), (rect.left, rect.bottom), 1)

        # Current piece
        piece_color = SHAPE_COLORS[self.piece_color_idx]
        for (dr, dc) in self.piece_cells:
            r, c = self.piece_row + dr, self.piece_col + dc
            if r >= 0:
                x = self.board_left + c * self.cell_w
                y = self.board_top + r * self.cell_h
                rect = pygame.Rect(x + 1, y + 1, self.cell_w - 2, self.cell_h - 2)
                pygame.draw.rect(screen, piece_color, rect)
                pygame.draw.rect(screen, config_module.COLOR_FOREGROUND, rect, 1)

        # Score, level, lines
        score_text = f"Score: {self.score}  Lvl: {self.level}  Lines: {self.lines_cleared}"
        score_surf = self.font.render(score_text, True, config_module.COLOR_ACCENT)
        screen.blit(score_surf, (self.margin_x, 8))

        # Next piece preview (small)
        next_x = self.board_left + self.board_pixel_w + 12
        next_y = self.board_top + 30
        if next_x + 5 * self.cell_w <= self.width:
            tiny = max(6, self.cell_w // 2)
            idx = self.next_piece_idx
            for (dr, dc) in SHAPES[idx]:
                rx = next_x + dc * tiny
                ry = next_y + dr * tiny
                pygame.draw.rect(screen, SHAPE_COLORS[idx], (rx, ry, tiny - 1, tiny - 1))

        # Controls hint
        try:
            labels = config_module.get_control_labels()
        except Exception:
            labels = {'prev': 'A', 'next': 'D', 'select': 'Enter'}
        hint = f"{labels['prev']}=Left {labels['next']}=Right {labels['select']}=Rotate"
        hint_surf = self.font.render(hint, True, config_module.COLOR_FOREGROUND)
        screen.blit(hint_surf, (self.board_left, self.board_top + self.board_pixel_h + 4))

        # Game over overlay
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(160)
            overlay.fill(config_module.COLOR_BACKGROUND)
            screen.blit(overlay, (0, 0))
            go_text = self.font.render(self.winner_message, True, config_module.COLOR_ACCENT)
            go_x = self.width // 2 - go_text.get_width() // 2
            go_y = self.height // 2 - go_text.get_height() // 2 - 20
            screen.blit(go_text, (go_x, go_y))
            try:
                labels = config_module.get_control_labels()
                quit_hint = f"Press {labels['prev']} to quit"
            except Exception:
                quit_hint = "Press A to quit"
            hint_surf = self.font.render(quit_hint, True, config_module.COLOR_FOREGROUND)
            hint_x = self.width // 2 - hint_surf.get_width() // 2
            screen.blit(hint_surf, (hint_x, self.height // 2 + 15))

        # Pause menu
        if self.paused:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(160)
            overlay.fill(config_module.COLOR_BACKGROUND)
            screen.blit(overlay, (0, 0))
            menu_y = self.height // 2 - (len(self.pause_menu_options) * 28) // 2
            for i, option in enumerate(self.pause_menu_options):
                color = config_module.COLOR_ACCENT if i == self.pause_menu_selected_index else config_module.COLOR_FOREGROUND
                text = self.font.render(option, True, color)
                text_pos = (self.width // 2 - text.get_width() // 2, menu_y + i * 28)
                screen.blit(text, text_pos)
