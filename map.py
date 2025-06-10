# Import libraries
import pygame                       # For rendering graphics and handling input
import math                         # For mathematical functions (especially hexagon geometry)
import heapq                       
from itertools import permutations  #imports and constants remain unchanged

# ------------------------ Map Definitions ------------------------ #
START    = 'S'                      # Start tile symbol
TREASURE = 'T'                      # Treasure tile symbol
BLOCKED  = '#'                      # Blocked tile symbol (impassable)
TRAPS    = ['X1', 'X2', 'X3', 'X4'] # Trap tiles
REWARDS  = ['R1', 'R2']             # Reward tiles
EMPTY    = ''                       # Empty tile

# Hexagonal grid definition
grid = [
    ['', '', '', '', '', '', '', '', '', ''],
    ['S', 'X2', '', 'X4', 'R1', '', '', '', '', ''],
    ['', '', '', '', 'T', '', 'X3', 'R2', '#', ''],
    ['', 'R1', '#', '#', '#', 'X3', '', 'T', 'X1', 'T'],
    ['#', '', '', 'T', '', '', '#', '#', '', ''],
    ['', '', 'X2', '', '#', 'R2', '#', '', '', ''],
    ['', '', '', '', '', '', '', '', '', '']
]

ROWS, COLS = len(grid), len(grid[0])  # Grid dimensions

# ------------------------ Pygame Setup ------------------------ #
TILE_SIZE = 40                         # Width of hex tile
HEX_H = TILE_SIZE * math.sqrt(3) / 2  # Height of hex tile (from geometry)
WIDTH = int(COLS * TILE_SIZE * 0.75 + TILE_SIZE / 4) # Window width
HEIGHT = int(ROWS * HEX_H + HEX_H / 2 + 60 + 50)     # Window height

# Color definitions for each tile type
COLORS = {
    START: (0, 100, 255),
    TREASURE: (255, 255, 0),
    BLOCKED: (80, 80, 80),
    'X1': (200, 100, 100),
    'X2': (180, 80, 120),
    'X3': (160, 60, 140),
    'X4': (140, 40, 160),
    'R1': (100, 255, 100),
    'R2': (100, 200, 255),
    EMPTY: (255, 255, 255),
    'PATH': (255, 165, 0)
}

# Descriptions shown on hover/tooltips
TileInfo = {
    'X1': "Trap 1: Increases gravity — step costs double energy.",
    'X2': "Trap 2: Decreases speed — moves cost double steps.",
    'X3': "Trap 3: Pushes you two cells forward.",
    'X4': "Trap 4: Destroys all uncollected treasures.",
    'R1': "Reward 1: Decreases gravity — step costs half energy.",
    'R2': "Reward 2: Increases speed — moves cost half steps.",
    'T':  "Treasure! You found one!",
    '':   "Empty Tile",
    '#':  "Blocked Tile",
    'S':  "Start Position"
}

# ------------------------ Hex Coordinate Utilities ------------------------ #

# Converts grid coordinates to pixel position
def hex_to_pixel(r, c):
    x = TILE_SIZE * 0.75 * c + TILE_SIZE / 2
    y = HEX_H * r + (HEX_H / 2 if c % 2 == 1 else 0) + HEX_H / 2
    return x, y

# Converts pixel position to grid coordinates (for mouse click detection)
def pixel_to_hex(x, y):
    for r in range(ROWS):
        for c in range(COLS):
            hx, hy = hex_to_pixel(r, c)
            dist = math.hypot(hx - x, hy - y)
            if dist < TILE_SIZE / 2:
                return r, c
    return None, None

# Returns pixel coordinates of the 6 corners of a hexagon
def hex_corners(x, y):
    return [
        (x + TILE_SIZE / 2 * math.cos(math.radians(angle)),
         y + TILE_SIZE / 2 * math.sin(math.radians(angle)))
        for angle in range(0, 360, 60)
    ]

# Finds the starting tile's coordinates
def find_start():
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] == START:
                return r, c
    return 0, 0

# Gets all valid neighbors of a tile in hex grid
def get_neighbors(r, c):
    even = (c % 2 == 0)
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    dirs += [(-1 if even else 0, -1), (-1 if even else 0, 1)] if even else [(1, -1), (1, 1)]
    neighbors = []
    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] != BLOCKED:
            neighbors.append((nr, nc))
    return neighbors

# ------------------------ Pathfinding Algorithms ------------------------ #

# Finds the best path to collect all treasures
def find_best_treasure_path(start_pos, treasures, return_to_start=False):
    if not treasures:
        return []

    best_path = []
    min_total_cost = float('inf')

    # Generate all possible orders of visiting treasures
    for order in permutations(treasures):
        current_pos = start_pos
        total_path = []
        total_cost = 0
        valid = True

        # Visit each treasure in current order
        for target in order:
            path_segment, cost = ucs(current_pos, target)
            if not path_segment:
                valid = False
                break
            total_path += path_segment
            total_cost += cost
            current_pos = target

        # Optionally return to start after collecting all treasures
        if valid and return_to_start:
            return_path, return_cost = ucs(current_pos, start_pos)
            if return_path:
                total_path += return_path
                total_cost += return_cost
            else:
                valid = False

        # Update best path if current permutation is better
        if valid and total_cost < min_total_cost:
            min_total_cost = total_cost
            best_path = total_path

    return best_path

# Uniform-Cost Search Algorithm
def ucs(start, goal):
    open_set = [(0, start)]  # (cost, position)
    came_from = {}
    cost_so_far = {start: 0}

    while open_set:
        current_cost, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path, cost_so_far[goal]
        
        for neighbor in get_neighbors(*current):
            tile = grid[neighbor[0]][neighbor[1]]
            step_cost = 1.0  # Base cost

            # Apply trap/reward modifiers
            if tile in TRAPS:
                step_cost *= 2
            elif tile in REWARDS:
                step_cost *= 0.5

            new_cost = current_cost + step_cost
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                came_from[neighbor] = current
                heapq.heappush(open_set, (new_cost, neighbor))

    return [], float('inf')

# ------------------------ Drawing Functions ------------------------ #

pygame.init()                             # Initialize pygame
screen = pygame.display.set_mode((WIDTH, HEIGHT)) # Create display
pygame.display.set_caption("Hex Grid Treasure Hunt") # Window title
font = pygame.font.SysFont('Arial', 18)   # Font for text

health = 10                               # Initial health
collected_treasures = set()              # Tracks collected treasures
all_treasures = {(r, c) for r in range(ROWS) for c in range(COLS) if grid[r][c] == TREASURE} # All treasures in the grid

# Draws the entire grid and player
def draw_grid(player_pos, path=[]):
    screen.fill((100, 100, 100))  # Clear background
    for r in range(ROWS):
        for c in range(COLS):
            x, y = hex_to_pixel(r, c)
            corners = hex_corners(x, y)
            tile = grid[r][c]
            color = COLORS.get(tile, COLORS[EMPTY])
            if (r, c) in path:
                color = COLORS['PATH']
            pygame.draw.polygon(screen, color, corners)           # Fill hex
            pygame.draw.polygon(screen, (0, 0, 0), corners, 1)    # Hex border
            text = font.render(tile, True, (0, 0, 0))             # Tile label
            screen.blit(text, text.get_rect(center=(x, y)))       # Draw text
            if (r, c) == player_pos:                              # Draw player
                pygame.draw.circle(screen, (0, 0, 0), (int(x), int(y)), 10)
    draw_legend()
    draw_status()

# Draws legend box at bottom of screen
def draw_legend():
    y = HEIGHT - 45
    x = 30
    legend_items = [
        ('S = Start', COLORS[START]),
        ('T = Treasure', COLORS[TREASURE]),
        ('# = Blocked', COLORS[BLOCKED]),
        ('X1..X4 = Traps', (160, 60, 120)),
        ('R1..R2 = Rewards', (100, 200, 255)),
        ('. = Empty', COLORS[EMPTY]),
    ]
    for label, color in legend_items:
        pygame.draw.rect(screen, color, (x, y, 20, 20))
        pygame.draw.rect(screen, (0, 0, 0), (x, y, 20, 20), 1)
        text = font.render(label, True, (255, 255, 255))
        screen.blit(text, (x + 25, y))
        x += 150

# Shows player's health and treasure count
def draw_status():
    status = f"Health: {health} | Treasures: {len(collected_treasures)}/{len(all_treasures)}"
    text = font.render(status, True, (255, 255, 255))
    screen.blit(text, (10, HEIGHT - 90))

# Displays tile description as a tooltip
def display_description(desc):
    pygame.draw.rect(screen, (30, 30, 30), (0, HEIGHT - 120, WIDTH, 25))
    text = font.render(desc, True, (255, 255, 255))
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 110))
    screen.blit(text, rect)

# ------------------------ Game Logic ------------------------ #

'''
# Heuristic for A* (Euclidean distance)
def heuristic(a, b):
    ax, ay = hex_to_pixel(*a)
    bx, by = hex_to_pixel(*b)
    return math.hypot(ax - bx, ay - by)
'''
'''
# A* pathfinding implementation
def a_star(start, goal):
    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for neighbor in get_neighbors(*current):
            cost = 1
            tile = grid[neighbor[0]][neighbor[1]]
            if tile == 'X1': cost *= 2
            if tile == 'R1': cost *= 0.5
            tentative_g = g_score[current] + cost
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))

    return []
'''

# ------------------------ Main Game Loop ------------------------ #
def main():
    global health
    clock = pygame.time.Clock()
    player_r, player_c = find_start()  # Start position
    path = []
    running = True

    while running:
        clock.tick(10)  # Limit FPS
        draw_grid((player_r, player_c), path)
        tile = grid[player_r][player_c]
        display_description(TileInfo.get(tile, "Nothing interesting here"))
        pygame.display.flip()

        # Collect treasure if standing on it
        if (player_r, player_c) in all_treasures:
            collected_treasures.add((player_r, player_c))

        # Trap and reward effects
        if tile in TRAPS:
            health -= 1
        elif tile in REWARDS:
            health = min(health + 1, 10)

        # Trap X4: remove uncollected treasures
        if tile == 'X4':
            for r, c in list(all_treasures):
                if (r, c) not in collected_treasures:
                    grid[r][c] = ''
                    all_treasures.remove((r, c))

        # Game over conditions
        if health <= 0 or collected_treasures == all_treasures:
            print("Game Over" if health <= 0 else "All Treasures Found!")
            pygame.time.wait(2000)
            running = False
        '''
        # Handle mouse clicks and key presses
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                r, c = pixel_to_hex(mx, my)
                if r is not None and (r, c) != (player_r, player_c):
                    path = a_star((player_r, player_c), (r, c))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and path:
                    player_r, player_c = path.pop(0)
        '''
        # Handle mouse clicks and key presses
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                r, c = pixel_to_hex(mx, my)
                if r is not None:
                    #Compute best path covering all treasures
                    remaining_treasures = [t for t in all_treasures if t not in collected_treasures]
                    if remaining_treasures:
                        path = find_best_treasure_path((player_r, player_c), remaining_treasures)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and path:
                    player_r, player_c = path.pop(0)
                    
        # Arrow key movement
        keys = pygame.key.get_pressed()
        directions = {
            pygame.K_UP:    (-1, 0),
            pygame.K_DOWN:  (1, 0),
            pygame.K_LEFT:  (0, -1),
            pygame.K_RIGHT: (0, 1),
        }
        for key, (dr, dc) in directions.items():
            if keys[key]:
                nr, nc = player_r + dr, player_c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] != BLOCKED:
                    player_r, player_c = nr, nc
                break

    pygame.quit()  # Close the game

# Entry point
if __name__ == "__main__":
    main()
