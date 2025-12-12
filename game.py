#IMPORT STATEMENTS
import pygame
from functions import calculate_points, create_grid, draw_grid, generate_random_piece, piece_blocks_to_rects, can_move, check_lineclears, attempt_rotation, set_piece_blocks_from_origin, get_user_input, add_score

"""INITAL STATEMENTS"""

def tetris(screen, screen_width, screen_height, clock, set_level=1):
    # Create font for displaying text
    font = pygame.font.Font(None, 36)  # None = default font, 36 = size

    """board initals"""
    running = True
    cols, rows = 10, 20# board dimensions (used for movement bounds)
    level = set_level
    cell_size, grid_x, grid_y, grid_rects = create_grid(screen_width, screen_height, cols=cols, rows=rows, margin=0) # create the grid that fits the screen: 10 cols x 20 rows
    grid_line_color = (200, 200, 200)
    fall_acc = 0.0
    soft_drop = 1 
    occupied = set()
    score = 0
    total_lines = 0
    keys_pressed = {"left": False, "right": False}
    delay = 0.17
    delay_total = 0.0
    start_das_value = 0.0
    # create an initial random piece and convert its grid blocks to pixel rects
    current_piece = generate_random_piece()
    piece_rects = piece_blocks_to_rects(current_piece["blocks"], cell_size, grid_x, grid_y)

    while running:
        level = (level -1) + (total_lines+10)//10
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #found this online in most everything? TODO cite this
                running = False
            elif event.type == pygame.KEYDOWN:
                # Move the current piece on the grid instead of the custom image
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    # attempt to move origin left
                    keys_pressed["left"] = True
                    ptype = current_piece["type"]
                    rot = current_piece.get("rotation_state", 0)
                    tentative = [(current_piece["origin_col"] - 1 + c, current_piece["origin_row"] + r) for (c, r) in __import__("functions").ROTATION_STATES[ptype][rot]]
                    if can_move(tentative, cols, rows, occupied):
                        current_piece["origin_col"] -= 1
                        set_piece_blocks_from_origin(current_piece)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    keys_pressed["right"] = True
                    ptype = current_piece["type"]
                    rot = current_piece.get("rotation_state", 0)
                    tentative = [(current_piece["origin_col"] + 1 + c, current_piece["origin_row"] + r) for (c, r) in __import__("functions").ROTATION_STATES[ptype][rot]]
                    if can_move(tentative, cols, rows, occupied):
                        current_piece["origin_col"] += 1
                        set_piece_blocks_from_origin(current_piece)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    soft_drop = 8
                elif event.key == pygame.K_j:
                    # Rotate clockwise
                    attempt_rotation(current_piece, cols, rows, occupied, 1)
                elif event.key == pygame.K_k:
                    # Rotate counter-clockwise
                    attempt_rotation(current_piece, cols, rows, occupied, -1)
                elif event.key == pygame.K_SPACE:
                    while True:
                        # hard drop by moving origin down until collision
                        ptype = current_piece["type"]
                        rot = current_piece.get("rotation_state", 0)
                        tentative = [(current_piece["origin_col"] + c, current_piece["origin_row"] + 1 + r) for (c, r) in __import__("functions").ROTATION_STATES[ptype][rot]]
                        if can_move(tentative, cols, rows, occupied):
                            current_piece["origin_row"] += 1
                            set_piece_blocks_from_origin(current_piece)
                        else:
                            for c, r in current_piece["blocks"]: occupied.add((c,r))
                            #check line clear and clear lines
                            lines_cleared = check_lineclears(occupied, cols, rows)
                            if lines_cleared > 0:
                                score += calculate_points(lines_cleared, level)
                                total_lines += lines_cleared
                            current_piece = generate_random_piece()
                            if not can_move(current_piece["blocks"], cols, rows, occupied):
                                running = False
                            fall_acc = 0.0
                            break
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN or event.key == pygame.K_s: soft_drop = 1
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a: 
                    keys_pressed["left"] = False
                    start_das_value = 0
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d: 
                    keys_pressed["right"] = False
                    start_das_value = 0
        #DAS
        if keys_pressed["left"] or keys_pressed["right"]:
            start_das_value += 1
        delay_total += delay
        if delay_total >= 1 and start_das_value > 10:
            if keys_pressed["left"]:
                ptype = current_piece["type"]
                rot = current_piece.get("rotation_state", 0)
                tentative = [(current_piece["origin_col"] - 1 + c, current_piece["origin_row"] + r) for (c, r) in __import__("functions").ROTATION_STATES[ptype][rot]]
                if can_move(tentative, cols, rows, occupied):
                    current_piece["origin_col"] -= 1
                    set_piece_blocks_from_origin(current_piece)

            if keys_pressed["right"]:
                ptype = current_piece["type"]
                rot = current_piece.get("rotation_state", 0)
                tentative = [(current_piece["origin_col"] + 1 + c, current_piece["origin_row"] + r) for (c, r) in __import__("functions").ROTATION_STATES[ptype][rot]]
                if can_move(tentative, cols, rows, occupied):
                    current_piece["origin_col"] += 1
                    set_piece_blocks_from_origin(current_piece)

            delay_total = 0.0
        # GRAVITY
        grav_number = (1.6 - (level/8)) / soft_drop  # my gravity number and its modifiers
        if fall_acc >= grav_number:
            # attempt to move origin down
            ptype = current_piece["type"]
            rot = current_piece.get("rotation_state", 0)
            tentative = [
                (current_piece["origin_col"] + c, current_piece["origin_row"] + 1 + r)
                for (c, r) in __import__("functions").ROTATION_STATES[ptype][rot]
            ]
            if can_move(tentative, cols, rows, occupied):
                current_piece["origin_row"] += 1
                set_piece_blocks_from_origin(current_piece)
            else:
                # lock piece
                for c, r in current_piece["blocks"]:
                    occupied.add((c, r))

                # check line clear and clear lines
                lines_cleared = check_lineclears(occupied, cols, rows)
                if lines_cleared > 0:
                    score += calculate_points(lines_cleared, level)
                    total_lines += lines_cleared

                current_piece = generate_random_piece()
                if not can_move(current_piece["blocks"], cols, rows, occupied): #game is over
                    # Prompt for player name and save score
                    try:
                        player_name = get_user_input(screen, font, prompt="Game Over! Enter your name:", max_len=12)
                    except Exception:
                        player_name = "PLAYER"
                    try:
                        add_score(player_name, score, total_lines, level)
                    except Exception as e:
                        print("Failed to save score:", e)
                    running = False

            fall_acc = 0.0

        # update pixel rects for the piece after possible movement
        piece_rects = piece_blocks_to_rects(current_piece["blocks"], cell_size, grid_x, grid_y)

        screen.fill((255, 255, 255))
        # draw the piece (filled cells) then grid lines on top
        for r in piece_rects:
            screen.fill(current_piece['color'], r)

        for c, r in occupied:
            rect = pygame.Rect(grid_x + c * cell_size, grid_y + r * cell_size, cell_size, cell_size)
            screen.fill((100, 100, 100), rect)  # gray for locked blocks

        draw_grid(screen, grid_rects, line_color=grid_line_color)

        # Render and display score, level, lines
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        level_text = font.render(f"Level: {level}", True, (0, 0, 0))
        lines_text = font.render(f"Lines: {total_lines}", True, (0, 0, 0))

        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 50))
        screen.blit(lines_text, (10, 90))

        pygame.display.flip()
        et = clock.tick(30) /1000.0
        fall_acc += et # adding up elasped time

    return score, level, lines_cleared
