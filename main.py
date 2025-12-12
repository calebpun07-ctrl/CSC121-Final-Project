import pygame
import sys
from game import tetris
from functions import load_scores

# INITIAL STATEMENTS
pygame.init()
clock = pygame.time.Clock()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode([screen_width, screen_height])
pygame.display.set_caption("Cetris")
font = pygame.font.Font(None, 36)


def run_menu():
    selected = 0  # 0: Start, 1: Level, 2: Quit
    level = 5
    max_level = 19
    scores = load_scores()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % 3
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % 3
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    if selected == 1: level = max(1, level - 1)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    if selected == 1:
                        level = min(max_level, level + 1)
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if selected == 0:
                        # Start the game with chosen level; tetris() returns on game over
                        tetris(screen, screen_width, screen_height, clock, set_level=level)
                        # refresh scores after returning from the game
                        scores = load_scores()
                    elif selected == 2:
                        pygame.quit()
                        sys.exit()

        # render menu
        screen.fill((30, 30, 30))
        title = font.render("Caleb - Tetris", True, (255, 255, 255))
        screen.blit(title, (screen_width // 2 - title.get_width() // 2, 80))

        options = ["Start Game", f"Start Level: {level}", "Quit"]
        for i, text in enumerate(options):
            color = (255, 255, 0) if i == selected else (200, 200, 200)
            prefix = "> " if i == selected else "  "
            txt = font.render(prefix + text, True, color)
            screen.blit(txt, (screen_width // 2 - txt.get_width() // 2, 200 + i * 50))

        # build strings
        to_show = scores[:5]
        entries = []
        for i, entry in enumerate(to_show):
            name = (entry.get("name") or "").strip()[:12]
            pts = entry.get("score", 0)
            lines = entry.get("lines", 0)
            lvl = entry.get("level", 0)
            entries.append(f"{i+1}. {name:<12} {pts:>5} L{lines} Lv{lvl}")

        # measure block size
        header = "High Scores"
        hdr_w, hdr_h = font.size(header)
        line_h = font.get_linesize()
        entry_widths = [font.size(s)[0] for s in entries] if entries else [0]
        block_w = max(hdr_w, max(entry_widths)) + 20   # padding
        
        # centered position
        lb_x = (screen_width - block_w) // 2
        lb_y = 400
        # draw header + entries
        screen.blit(font.render(header, True, (255,215,0)), (lb_x + 10, lb_y))
        for i, text in enumerate(entries):
            y = lb_y + hdr_h + 8 + i * line_h
            screen.blit(font.render(text, True, (200,200,200)), (lb_x + 10, y))

        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    run_menu()
