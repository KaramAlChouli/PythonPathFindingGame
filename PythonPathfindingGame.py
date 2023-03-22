import pygame
import random
from queue import PriorityQueue

# Initialize Pygame
pygame.init()

# Set up display
width, height = 900, 700
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Squares and Path with Obstacles")

# Define colors
white = (255, 255, 255)
green = (0, 255, 0)
blue = (0, 0, 255)
red = (255, 0, 0)
custom = (137,176,255)


# Define squares, path, and obstacles
square_size = 50

obstacle_sprite = pygame.image.load('sprite_obstacle.png')
user_sprite = pygame.image.load('sprite_user.png')
moving_sprite = pygame.image.load('sprite_moving.png')


obstacle_sprite = pygame.transform.scale(obstacle_sprite, (square_size, square_size))
user_sprite = pygame.transform.scale(user_sprite, (square_size, square_size))
moving_sprite = pygame.transform.scale(moving_sprite, (square_size, square_size))

grid_width, grid_height = width // square_size, height // square_size
square_top_left = pygame.Rect(0, 0, square_size, square_size)
square_bottom_right = pygame.Rect(width - square_size, height - square_size, square_size, square_size)
num_obstacles = 90

obstacles = []
for _ in range(num_obstacles):
    x = random.randint(1, grid_width - 1) * square_size
    y = random.randint(1, grid_height - 1) * square_size
    obstacles.append(pygame.Rect(x, y, square_size, square_size))
def show_game_over(screen, font):
    text = font.render("Game Over, Press R to restart", True, white)
    screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2))
# A* pathfinding
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
def random_position_not_colliding(obstacles):
    while True:
        x = random.randint(1, grid_width - 1) * square_size
        y = random.randint(1, grid_height - 1) * square_size
        rect = pygame.Rect(x, y, square_size, square_size)
        if not is_colliding(rect, obstacles):
            return rect
def a_star_search(grid, start, end):
    frontier = PriorityQueue()
    frontier.put((0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}

    while not frontier.empty():
        _, current = frontier.get()

        if current == end:
            break

        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0 or (dx != 0 and dy != 0):  # Disallow diagonal movement
                    continue
                next = (current[0] + dx, current[1] + dy)
                if 0 <= next[0] < grid_width and 0 <= next[1] < grid_height:
                    new_cost = cost_so_far[current] + 1
                    if next not in cost_so_far or new_cost < cost_so_far[next]:
                        if grid[next[1]][next[0]] == 0:
                            cost_so_far[next] = new_cost
                            priority = new_cost + heuristic(end, next)
                            frontier.put((priority, next))
                            came_from[next] = current

    return came_from


grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]
for obstacle in obstacles:
    grid[obstacle.y // square_size][obstacle.x // square_size] = 1

def reconstruct_path(came_from, start, end):
    path = []
    current = end
    while current != start:
        if current not in came_from:
            return []
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path
def is_colliding(rect, obstacles):
    for obstacle in obstacles:
        if rect.colliderect(obstacle):
            return True
    return False
# Define the moving square
moving_square = pygame.Rect(square_top_left.x, square_top_left.y, square_size, square_size)
moving_color = (255, 255, 0)  # Yellow

# Define user-controlled square
user_square = pygame.Rect(width // 2, height // 2, square_size, square_size)
user_color = (0, 128, 255)  # Light blue
user_speed = 5

# Variables to control the moving square
move_speed = 5
current_path_index = 0

start = (square_top_left.x // square_size, square_top_left.y // square_size)
end = (user_square.x // square_size, user_square.y // square_size)
came_from = a_star_search(grid, start, end)
path = reconstruct_path(came_from, start, end)
path_length = len(path)
font = pygame.font.Font(None, 36)
game_over = False
# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Check for game over condition
    if moving_square.colliderect(user_square):
        game_over = True
    keys = pygame.key.get_pressed()
    if game_over:
        if keys[pygame.K_r]:
            # Reset game state
            game_over = False
            user_square.x, user_square.y = width // 2, height // 2
            moving_square.x, moving_square.y = square_top_left.x, square_top_left.y
        else:
            show_game_over(screen, font)
            pygame.display.flip()
            continue
    if keys[pygame.K_w] and user_square.y > 0:
        user_square.y -= user_speed
        if is_colliding(user_square, obstacles):
            user_square.y += user_speed
    if keys[pygame.K_a] and user_square.x > 0:
        user_square.x -= user_speed
        if is_colliding(user_square, obstacles):
            user_square.x += user_speed
    if keys[pygame.K_s] and user_square.y < height - square_size:
        user_square.y += user_speed
        if is_colliding(user_square, obstacles):
            user_square.y -= user_speed
    if keys[pygame.K_d] and user_square.x < width - square_size:
        user_square.x += user_speed
        if is_colliding(user_square, obstacles):
            user_square.x -= user_speed

    start = (moving_square.x // square_size, moving_square.y // square_size)
    end = (user_square.x // square_size, user_square.y // square_size)
    came_from = a_star_search(grid, start, end)
    path = reconstruct_path(came_from, start, end)
    current_path_index = 0
    path_length = len(path)

    screen.fill(custom)


    # Draw obstacles
    for obstacle in obstacles:
        screen.blit(obstacle_sprite, obstacle)


    # Draw user-controlled square
    screen.blit(user_sprite, user_square)


    # Move the square along the path
    if current_path_index < path_length:
        next_pos = (path[current_path_index][0] * square_size, path[current_path_index][1] * square_size)
        dx, dy = next_pos[0] - moving_square.x, next_pos[1] - moving_square.y
        distance = (dx**2 + dy**2)**0.5

        if distance < move_speed:
            moving_square.x = next_pos[0]
            moving_square.y = next_pos[1]
            current_path_index += 1
        else:
            moving_square.x += move_speed * dx / distance
            moving_square.y += move_speed * dy / distance
    # Draw the moving square
    screen.blit(moving_sprite, moving_square)


    pygame.display.flip()
    pygame.time.delay(50)  # Add delay to control the speed of the game loop

# Clean up
pygame.quit()

