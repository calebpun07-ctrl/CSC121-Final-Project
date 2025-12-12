import pygame
from typing import List, Tuple
import csv
import time
from pathlib import Path

# Precomputed rotation states for each piece type (local coordinates, 4 rotations each)
ROTATION_STATES = {
    "I": [
        [(0, 0), (1, 0), (2, 0), (3, 0)],  # horizontal
        [(0, 0), (0, 1), (0, 2), (0, 3)],  # vertical
        [(0, 0), (1, 0), (2, 0), (3, 0)],  # horizontal (repeat)
        [(0, 0), (0, 1), (0, 2), (0, 3)],  # vertical (repeat)
    ],
    "O": [
        [(0, 0), (1, 0), (0, 1), (1, 1)],  # square (same in all rotations)
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
    ],
    "T": [
        [(-1, 0), (0, 0), (1, 0), (0, 1)],  # T pointing down
        [(0, -1), (0, 0), (0, 1), (-1, 0)],  # T pointing right
        [(-1, 0), (0, 0), (1, 0), (0, -1)],  # T pointing up
        [(0, -1), (0, 0), (0, 1), (1, 0)],   # T pointing left
    ],
    "S": [
        [(0, 0), (1, 0), (-1, 1), (0, 1)],  # S horizontal
        [(0, -1), (0, 0), (1, 0), (1, 1)],  # S vertical (approx)
        [(0, 0), (1, 0), (-1, 1), (0, 1)],
        [(0, -1), (0, 0), (1, 0), (1, 1)],
    ],
    "Z": [
        [(-1, 0), (0, 0), (0, 1), (1, 1)],  # Z horizontal
        [(1, -1), (1, 0), (0, 0), (0, 1)],  # Z vertical (approx)
        [(-1, 0), (0, 0), (0, 1), (1, 1)],
        [(1, -1), (1, 0), (0, 0), (0, 1)],
    ],
    "L": [
        [(-1, 0), (0, 0), (1, 0), (1, 1)],
        [(0, -1), (0, 0), (0, 1), (1, -1)],
        [(-1, -1), (-1, 0), (0, 0), (1, 0)],
        [(-1, 1), (0, -1), (0, 0), (0, 1)],
    ],
    "J": [
        [(-1, 0), (0, 0), (1, 0), (-1, 1)],
        [(-1, -1), (0, -1), (0, 0), (0, 1)],
        [(-1, 0), (0, 0), (1, 0), (1, -1)],
        [(0, -1), (0, 0), (0, 1), (1, 1)],
    ],
}
HS_PATH = Path("high_scores.csv")
def generate_random_piece():
        """Generate a random Tetris piece positioned at spawn location.

        Returns a dict with keys:
            - 'type': piece type (I, O, T, S, Z, L, J)
            - 'blocks': list of (col, row) tuples (world grid coordinates)
            - 'color': (r,g,b)
            - 'rotation_state': 0-3 (current rotation state)
            - 'origin_col', 'origin_row': position to add local coords to
        """
        import random

        cols = 10
        rows = 20
        center = cols // 2

        pieces = []

        # Helper to compute world blocks from local rotation state
        def world_blocks(piece_type, origin_col, origin_row, rot):
            return [(origin_col + c, origin_row + r) for (c, r) in ROTATION_STATES[piece_type][rot]]

        # I-piece
        pieces.append({
            "type": "I",
            "rotation_state": 0,
            "origin_col": center - 2,
            "origin_row": 0,
            "color": (0, 240, 240),
        })

        # O-piece
        pieces.append({
            "type": "O",
            "rotation_state": 0,
            "origin_col": center - 1,
            "origin_row": 0,
            "color": (240, 240, 0),
        })

        # T-piece
        pieces.append({
            "type": "T",
            "rotation_state": 0,
            "origin_col": center,
            "origin_row": 0,
            "color": (200, 0, 200),
        })

        # S, Z, L, J
        pieces.append({"type": "S", "rotation_state": 0, "origin_col": center, "origin_row": 0, "color": (0, 240, 0)})
        pieces.append({"type": "Z", "rotation_state": 0, "origin_col": center, "origin_row": 0, "color": (0, 0, 240)})
        pieces.append({"type": "L", "rotation_state": 0, "origin_col": center, "origin_row": 0, "color": (240, 0, 0)})
        pieces.append({"type": "J", "rotation_state": 0, "origin_col": center, "origin_row": 0, "color": (240, 0, 240)})

        p = random.choice(pieces)
        # compute actual world blocks
        p["blocks"] = world_blocks(p["type"], p["origin_col"], p["origin_row"], p["rotation_state"])
        return p

def attempt_rotation(piece: dict, cols: int, rows: int, occupied: set, direction) -> bool:
    """Attempt to rotate a piece clockwise with wall-kick.
    
    Tries the rotated position, then attempts wall-kicks (shifts left/right)
    if the original position collides.
    
    Mutates `piece` in-place if successful.
    
    Returns:
        True if rotation succeeded, False if blocked.
    """
    if piece["type"] not in ROTATION_STATES: return False  # no rotation defined for this piece
    
    # Get next rotation state
    next_state = (piece["rotation_state"] + direction) % 4
    local_blocks = ROTATION_STATES[piece["type"]][next_state]
    
    # Wall-kick offsets to try (in order): no shift, left 1, right 1, left 2, right 2
    offsets = [(0, 0), (-1, 0), (1, 0), (-2, 0), (2, 0)]
    
    for dx, dy in offsets:
        tentative = [
            (piece["origin_col"] + c + dx, piece["origin_row"] + r + dy)
            for (c, r) in local_blocks
        ]
        
        if can_move(tentative, cols, rows, occupied):
            # Rotation successful!
            piece["blocks"] = tentative
            piece["rotation_state"] = next_state
            piece["origin_col"] += dx  # update origin for next rotation
            return True
    
    return False  # all wall-kick attempts failed

def check_lineclears(occupied: set, cols: int, rows: int) -> int:
    """
    Clear fully-filled rows in `occupied` and shift blocks above down.
    Mutates `occupied` in-place.

    Args:
      occupied: set of (col, row) tuples
      cols, rows: board dimensions

    Returns:
      Number of rows cleared
    """
    # Find complete rows
    cleared_rows = [r for r in range(rows) if all((c, r) in occupied for c in range(cols))]
    if not cleared_rows:
        return 0

    cleared_set = set(cleared_rows)
    cleared_sorted = sorted(cleared_rows)  # ascending

    new_occupied = set()
    for (c, r) in occupied:
        # Skip blocks on cleared rows (they are removed)
        if r in cleared_set:
            continue
        # Count how many cleared rows are below this block
        shift = 0
        # cleared_sorted is ascending; rows below have value > r
        for cr in cleared_sorted:
            if cr > r:
                shift += 1
        new_occupied.add((c, r + shift))

    # Replace occupied contents
    occupied.clear()
    occupied.update(new_occupied)

    return len(cleared_rows)

def calculate_points(lines_cleared: int, level: int) -> int:
    lines = [40, 100, 300, 1200]
    return lines[lines_cleared-1] *(level +1)

def create_grid(screen_width: int, screen_height: int, cols: int = 10, rows: int = 20, margin: int = 0) -> Tuple[int, int, int, List[pygame.Rect]]:
    """Create a grid of square cells that fits inside the given screen dimensions.

    Returns a tuple (cell_size, offset_x, offset_y, rects) where `rects` is a
    list of `pygame.Rect` for each cell (row-major order).

    - `cols` and `rows` specify the grid dimensions (default 10x20).
    - `margin` reserves pixels on each side of the screen (optional).
    """
    available_w = max(0, screen_width - 2 * margin)
    available_h = max(0, screen_height - 2 * margin)

    # Determine the largest square cell size that fits both directions
    cell_size = int(min(available_w // cols, available_h // rows))
    if cell_size <= 0:
        raise ValueError("Screen too small for requested grid and margin")

    grid_w = cell_size * cols
    grid_h = cell_size * rows

    # Center the grid on screen (respecting margin)
    offset_x = (screen_width - grid_w) // 2
    offset_y = (screen_height - grid_h) // 2

    rects: List[pygame.Rect] = []
    for r in range(rows):
        for c in range(cols):
            rects.append(pygame.Rect(offset_x + c * cell_size, offset_y + r * cell_size, cell_size, cell_size))

    return cell_size, offset_x, offset_y, rects

def draw_grid(surface: pygame.Surface, rects: List[pygame.Rect], line_color: Tuple[int, int, int] = (0, 0, 0), fill_color: Tuple[int, int, int] = None):
    """Draw the provided grid rects to `surface`.

    If `fill_color` is provided, each cell will be filled before drawing
    the grid lines.
    """
    if fill_color is not None:
        for rect in rects:
            surface.fill(fill_color, rect)

    for rect in rects:
        pygame.draw.rect(surface, line_color, rect, 1)

def piece_blocks_to_rects(blocks: List[Tuple[int, int]], cell_size: int, offset_x: int, offset_y: int) -> List[pygame.Rect]:
    """Convert a list of grid blocks (col,row) into pygame.Rects using the
    provided `cell_size` and grid offsets (offset_x, offset_y).
    """
    rects: List[pygame.Rect] = []
    for (c, r) in blocks:
        rects.append(pygame.Rect(offset_x + c * cell_size, offset_y + r * cell_size, cell_size, cell_size))
    return rects

def set_piece_blocks_from_origin(piece: dict):
    """Update `piece['blocks']` from its origin and rotation_state."""
    piece_type = piece["type"]
    rot = piece.get("rotation_state", 0)
    ocol = piece.get("origin_col", 0)
    orow = piece.get("origin_row", 0)
    piece["blocks"] = [(ocol + c, orow + r) for (c, r) in ROTATION_STATES[piece_type][rot]]

def can_move(blocks, cols, rows, occupied):
    """Check if a list of blocks can legally occupy those positions.
    
    Args:
        blocks: list of (col, row) tuples (the tentative new position)
        cols, rows: board dimensions (10, 20)
        occupied: set of (col, row) tuples already locked/placed
    
    Returns:
        True if all blocks are in-bounds and not colliding; False otherwise
    """
    for c, r in blocks:
        # Out of horizontal bounds
        if not (0 <= c < cols):
            return False
        # Out of vertical bounds (hit bottom or top)
        if not (0 <= r < rows):
            return False
        # Occupied by a locked block
        if (c, r) in occupied:
            return False
    return True

def load_scores(path: Path = HS_PATH):
    """Load high scores from CSV.

    Returns a list of dicts with keys: 'name', 'score', 'lines', 'level'.
    """
    scores = []
    if not path.exists():
        return scores
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row:
                continue
            # Normalize keys (strip whitespace) so headers like "name, score" work
            row_norm = {k.strip(): v for k, v in row.items()}
            try:
                s = int(row_norm.get("score", 0))
            except Exception:
                s = 0
            try:
                lines = int(row_norm.get("lines", 0))
            except Exception:
                lines = 0
            try:
                lvl = int(row_norm.get("level", 0))
            except Exception:
                lvl = 0
            scores.append({
                "name": row_norm.get("name", ""),
                "score": s,
                "lines": lines,
                "level": lvl,
            })
    return scores


def save_scores(scores, path: Path = HS_PATH):
    """Save list of score dicts to CSV. Each item should have keys
    'name','score','lines','level'."""
    fieldnames = ["name", "score", "lines", "level"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for s in scores:
            writer.writerow({
                "name": s.get("name", ""),
                "score": s.get("score", 0),
                "lines": s.get("lines", 0),
                "level": s.get("level", 0),
            })

def add_score(name, score, lines=0, level=1, top_n: int = 10, path: Path = HS_PATH):
    """Add a score to the CSV and keep top_n highest entries.

    Returns updated list of score dicts.
    """
    scores = load_scores(path)
    try:
        s = int(score)
    except Exception:
        s = 0
    try:
        ln = int(lines)
    except Exception:
        ln = 0
    try:
        lv = int(level)
    except Exception:
        lv = 0

    scores.append({"name": str(name), "score": s, "lines": ln, "level": lv})
    scores.sort(key=lambda x: x["score"], reverse=True)
    scores = scores[:top_n]
    save_scores(scores, path)
    return scores

def get_user_input(screen, font, prompt="Enter name:", max_len: int = 10):
    """Simple wrapper that collects text input from the player and returns it.

    Uses `get_player_name` which provides a blocking pygame text-input UI.
    """
    return get_player_name(screen, font, prompt=prompt, max_len=max_len)


def get_player_name(screen, font, prompt="Enter name:", max_len=10):
    """Block until player presses Enter. Returns entered name (str)."""
    clock = pygame.time.Clock()
    name = ""
    cursor_visible = True
    last_blink = time.time()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return ""   # or handle quit specially
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    return name.strip() or "PLAYER"
                elif ev.key == pygame.K_ESCAPE:
                    return "PLAYER"
                elif ev.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    ch = ev.unicode
                    if ch and len(name) < max_len and (ch.isprintable()):
                        name += ch

        # simple cursor blink
        if time.time() - last_blink >= 0.5:
            cursor_visible = not cursor_visible
            last_blink = time.time()

        # render prompt
        screen.fill((30, 30, 30))
        prompt_surf = font.render(prompt, True, (255, 255, 255))
        name_display = name + ("|" if cursor_visible else "")
        name_surf = font.render(name_display, True, (255, 255, 0))
        screen.blit(prompt_surf, (50, 200))
        screen.blit(name_surf, (50, 250))
        pygame.display.flip()
        clock.tick(30)