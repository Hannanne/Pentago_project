import pygame
import requests
import numpy as np
import random
import sys
import math
from io import BytesIO
import time
import pickle
import matplotlib.pyplot as plt


import cProfile
import pstats
from io import StringIO

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WINDOW_SIZE = (400, 300)
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 50

pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()

def draw_start_screen():
    screen.fill(WHITE)
    
    font = pygame.font.Font(None, 36)
    text = font.render("Select mode:", True, BLACK)
    text_rect = text.get_rect(center=(WINDOW_SIZE[0] // 2, 100))
    screen.blit(text, text_rect)

    # 2 joueurs physiques
    pygame.draw.rect(screen, GREEN, (40, 150, BUTTON_WIDTH, BUTTON_HEIGHT))
    font = pygame.font.Font(None, 24)
    text = font.render("2 Players", True, WHITE)
    text_rect = text.get_rect(center=(40 + BUTTON_WIDTH // 2, 150 + BUTTON_HEIGHT // 2))
    screen.blit(text, text_rect)

    # Minimax
    pygame.draw.rect(screen, RED, (200, 150, BUTTON_WIDTH, BUTTON_HEIGHT))
    text = font.render("Minimax", True, WHITE)
    text_rect = text.get_rect(center=(200 + BUTTON_WIDTH // 2, 150 + BUTTON_HEIGHT // 2))
    screen.blit(text, text_rect)

    # Minimax Alpha-Beta
    pygame.draw.rect(screen, GRAY, (40, 220, BUTTON_WIDTH, BUTTON_HEIGHT))
    text = font.render("Alpha-Beta", True, WHITE)
    text_rect = text.get_rect(center=(40 + BUTTON_WIDTH // 2, 220 + BUTTON_HEIGHT // 2))
    screen.blit(text, text_rect)

    # Q-learning
    pygame.draw.rect(screen, BLACK, (200, 220, BUTTON_WIDTH, BUTTON_HEIGHT))
    text = font.render("Q-learning", True, WHITE)
    text_rect = text.get_rect(center=(200 + BUTTON_WIDTH // 2, 220 + BUTTON_HEIGHT // 2))
    screen.blit(text, text_rect)

    pygame.display.flip()

def main_menu():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if 40 <= mouse_pos[0] <= 40 + BUTTON_WIDTH and 150 <= mouse_pos[1] <= 150 + BUTTON_HEIGHT:
                    main()
                elif 200 <= mouse_pos[0] <= 200 + BUTTON_WIDTH and 150 <= mouse_pos[1] <= 150 + BUTTON_HEIGHT:
                    print("Starting game with Minimax AI")
                    main_minimax()
                elif 40 <= mouse_pos[0] <= 40 + BUTTON_WIDTH and 220 <= mouse_pos[1] <= 220 + BUTTON_HEIGHT:
                    print("Starting game with Minimax Alpha-Beta AI")
                    #main_minimax_alpha_beta()
                    main_minimax_ab_simu()
                    plot_minimax_ab_simulation_data()
                elif 200 <= mouse_pos[0] <= 200 + BUTTON_WIDTH and 220 <= mouse_pos[1] <= 220 + BUTTON_HEIGHT:
                    print("Starting game with Q-learning AI")
                    main_q_learning()
                    #main_q_learning_simu()
                    #plot_simulation_data()

        clock.tick(30)
        draw_start_screen()

# def play_game(num_players):
#     print(f"Starting game with {num_players} players")
#     if num_players == 2:
#         main()
#     elif num_players == 1:
#         main_minimax()


######################## Partie jeu #############################################################################################""


# WHITE = (255, 255, 255)
# BLACK = (0, 0, 0)
RED = (255, 0, 0)
# GRAY = (200, 200, 200)
GRAY2 = (180, 180, 180)

BOARD_SIZE = 6
CELL_SIZE = 60
PADDING = 5
WINDOW_SIZE = (BOARD_SIZE * CELL_SIZE + (BOARD_SIZE + 1) * PADDING, BOARD_SIZE * CELL_SIZE + (BOARD_SIZE + 1) * PADDING)
FPS = 30

# clicked = False
pos = []
winner = None

# #values = np.zeros(6,6)
# #values = [[0,0,0,0,0,0],
# #            [0,0,0,0,0,0],
# #            [0,0,0,0,0,0],
# #            [0,0,0,0,0,0],
# #            [0,0,0,0,0,0],
# #               [0,0,0,0,0,0]]

pygame.init()

# Définitions des fonctions utilisées ##########################################################################################

screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()

# Dessine le plateau de départ 
def draw_board(board):
    screen.fill(GRAY)

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            pygame.draw.circle(screen, WHITE, (col * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING, row * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING), CELL_SIZE // 2)

    pygame.draw.line(screen, GRAY2, [WINDOW_SIZE[0] // 2, 0], [WINDOW_SIZE[0] // 2, WINDOW_SIZE[1]], 3)
    pygame.draw.line(screen, GRAY2, [0, WINDOW_SIZE[1] // 2], [WINDOW_SIZE[0], WINDOW_SIZE[1] // 2], 3)

    pygame.display.flip()


#Rotation des quadrants : coupe en quatre morceaux la matrice et change les valeurs par rotation
def rotate_board(board, quadrant, direction):
    quadrants = {
        'top_left': (slice(None, BOARD_SIZE//2), slice(None, BOARD_SIZE//2)),
        'top_right': (slice(None, BOARD_SIZE//2), slice(BOARD_SIZE//2, None)),
        'bottom_left': (slice(BOARD_SIZE//2, None), slice(None, BOARD_SIZE//2)),
        'bottom_right': (slice(BOARD_SIZE//2, None), slice(BOARD_SIZE//2, None))
    }
    
    if direction == 'clockwise':
        rotated_quadrant = np.rot90(board[quadrants[quadrant]], -1)
    elif direction == 'counterclockwise':
        rotated_quadrant = np.rot90(board[quadrants[quadrant]], 1)
    else:
        return board

    # Met à jour le plateau
    board[quadrants[quadrant]] = rotated_quadrant

    return board




# Met à jour la visualisation de la board : Met un point rouge à 2 et noir à 1 de la matrice
def update_board_display(board):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row, col] == 1:
                pygame.draw.circle(screen, BLACK, (col * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING, row * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING), CELL_SIZE // 2)
            elif board[row, col] == 2:
                pygame.draw.circle(screen, RED, (col * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING, row * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING), CELL_SIZE // 2)
            elif board[row,col] == 0:
                pygame.draw.circle(screen, WHITE, (col * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING, row * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING), CELL_SIZE // 2)

# Vérifie le gagnant : vérifie une à une les lignes et les diagonales

# def check_winner(board, player):
#     # Lignes
#     for row in range(BOARD_SIZE):
#         for col in range(BOARD_SIZE - 4):
#             if all(board[row, col:col+5] == player):
#                 return True

#     for col in range(BOARD_SIZE):
#         for row in range(BOARD_SIZE - 4):
#             if all(board[row:row+5, col] == player):
#                 return True

#     # Diagonales
#     for row in range(BOARD_SIZE - 4):
#         for col in range(BOARD_SIZE - 4):
#             if all(board[row+i, col+i] == player for i in range(5)):
#                 return True

#     for row in range(4, BOARD_SIZE):
#         for col in range(BOARD_SIZE - 4):
#             if all(board[row-i, col+i] == player for i in range(5)):
#                 return True

#     return False


winning_configs = [

    # Lignes verticales
    [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],
    [(0, 1), (1, 1), (2, 1), (3, 1), (4, 1)],
    [(0, 2), (1, 2), (2, 2), (3, 2), (4, 2)],
    [(0, 3), (1, 3), (2, 3), (3, 3), (4, 3)],
    [(0, 4), (1, 4), (2, 4), (3, 4), (4, 4)],
    [(0, 5), (1, 5), (2, 5), (3, 5), (4, 5)],
    [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0)],
    [(1, 1), (2, 1), (3, 1), (4, 1), (5, 1)],
    [(1, 2), (2, 2), (3, 2), (4, 2), (5, 2)],
    [(1, 3), (2, 3), (3, 3), (4, 3), (5, 3)],
    [(1, 4), (2, 4), (3, 4), (4, 4), (5, 4)],
    [(1, 5), (2, 5), (3, 5), (4, 5), (5, 5)],


    # Lignes horizontales
    [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4)],
    [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)],
    [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4)],
    [(1, 1), (1, 2), (1, 3), (1, 4), (1, 5)],
    [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4)],
    [(2, 1), (2, 2), (2, 3), (2, 4), (2, 5)],
    [(3, 0), (3, 1), (3, 2), (3, 3), (3, 4)],
    [(3, 1), (3, 2), (3, 3), (3, 4), (3, 5)],
    [(4, 0), (4, 1), (4, 2), (4, 3), (4, 4)],
    [(4, 1), (4, 2), (4, 3), (4, 4), (4, 5)],
    [(5, 0), (5, 1), (5, 2), (5, 3), (5, 4)],
    [(5, 1), (5, 2), (5, 3), (5, 4), (5, 5)],

    # Diagonales
    [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)],
    [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5)],
    [(1, 0), (2, 1), (3, 2), (4, 3), (5, 4)],
    [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)],
    [(0, 4), (1, 3), (2, 2), (3, 1), (4, 0)],
    [(0, 5), (1, 4), (2, 3), (3, 2), (4, 1)],
    [(1, 4), (2, 3), (3, 2), (4, 1), (5, 0)],
    [(1, 5), (2, 4), (3, 3), (4, 2), (5, 1)]
]

# def check_winner(board, player):
#     for config in winning_configs:
#         config_sum = sum(board[pos[0],pos[1]] for pos in config)
#         if config_sum == 5:
#             if player == 1:
#                 return True 
         
#         elif config_sum == 10:
#             if player == 2:
#                 return True
#     return False

def check_winner(board, player):
    for config in winning_configs:
        if all(board[pos[0], pos[1]] == player for pos in config):
            return True
    return False


# Dessine les flèches pour tourner le quadrant :
    
def draw_arrows(board):
    update_board_display(board)
    response = requests.get('https://i.ibb.co/NTC3rpV/FLECHE-COURBE-2048x1352.png')
    fleche = pygame.image.load(BytesIO(response.content))
    fleche = pygame.transform.scale(fleche, (40, 40))
    fleche_copy = fleche.copy()
    fleche_copy = pygame.transform.scale(fleche_copy, (40, 40))
    arrows = {
        'top_right': pygame.transform.rotate(pygame.transform.flip(fleche_copy, True, False), 20),
        'top_left':  pygame.transform.rotate(fleche, -20),
        'left_bottom': pygame.transform.rotate(fleche, 45),
        'right_bottom': pygame.transform.rotate(pygame.transform.flip(fleche_copy, True, False), - 45),
        'bottom_left': pygame.transform.rotate(pygame.transform.flip(fleche_copy, True, False), 200),
        'bottom_right' : pygame.transform.rotate(fleche, 160),
        'right_top': pygame.transform.rotate(fleche, -135),
        'left_top' : pygame.transform.rotate(pygame.transform.flip(fleche_copy, True, False), 135)
    }
    arrow_positions = {
        'top_left': (19, -10 ),
        'top_right': (WINDOW_SIZE[0] - 19 - arrows['top_right'].get_width(), -10),
        'left_top': (-10 , 30),  
        'right_top': (WINDOW_SIZE[0] + 10 - arrows['right_top'].get_width(), arrows['top_right'].get_height()-23),  
        'bottom_left': (19, WINDOW_SIZE[1] + 10 - arrows['bottom_left'].get_height()),
        'bottom_right': (WINDOW_SIZE[0] -19 - arrows['bottom_right'].get_width(), WINDOW_SIZE[1] +10 - arrows['bottom_right'].get_height()),
        'left_bottom': (-10  , WINDOW_SIZE[1] + 27 - arrows['left_bottom'].get_height()*2),  
        'right_bottom': (WINDOW_SIZE[0] + 10 - arrows['right_bottom'].get_width(), WINDOW_SIZE[1] + 23 - (arrows['right_bottom'].get_height()*2))  
    }

    for quadrant, arrow in arrows.items():
        screen.blit(arrow, arrow_positions[quadrant])
    pygame.display.flip()
    return arrow_positions, arrows


def distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


# Vérifie quelle flèche est cliquée
def check_arrow_clicked(board,position,arrow_positions,arrows):
        rotation_quadrant = None
        rotation_direction = None

        if (arrow_positions['top_left'][0] <= position[0] <= arrow_positions['top_left'][0] + arrows['top_left'].get_width() and
            arrow_positions['top_left'][1] <= position[1] <= arrow_positions['top_left'][1] + arrows['top_left'].get_height()):
            rotation_quadrant = 'top_left'
            rotation_direction = 'clockwise'
            print("Clicked top_left arrow!")
        
        elif (arrow_positions['top_right'][0] <= position[0] <= arrow_positions['top_right'][0] + arrows['top_right'].get_width() and
              arrow_positions['top_right'][1] <= position[1] <= arrow_positions['top_right'][1] + arrows['top_right'].get_height()):
            rotation_quadrant = 'top_right'
            rotation_direction = 'clockwise'
            print("Clicked top_right arrow!")

        elif (arrow_positions['left_top'][0] <= position[0] <= arrow_positions['left_top'][0] + arrows['left_top'].get_width() and
              arrow_positions['left_top'][1] <= position[1] <= arrow_positions['left_top'][1] + arrows['left_top'].get_height()):
            rotation_quadrant = 'top_left'
            rotation_direction = 'clockwise'
            print("Clicked left_top arrow!")
        
        elif (arrow_positions['right_top'][0] <= position[0] <= arrow_positions['right_top'][0] + arrows['right_top'].get_width() and
              arrow_positions['right_top'][1] <= position[1] <= arrow_positions['right_top'][1] + arrows['right_top'].get_height()):
            rotation_quadrant = 'top_right'
            rotation_direction = 'clockwise'
            print("Clicked right_top arrow!")
        
        elif (arrow_positions['bottom_left'][0] <= position[0] <= arrow_positions['bottom_left'][0] + arrows['bottom_left'].get_width() and
              arrow_positions['bottom_left'][1] <= position[1] <= arrow_positions['bottom_left'][1] + arrows['bottom_left'].get_height()):
            rotation_quadrant = 'bottom_left'
            rotation_direction = 'clockwise'
            print("Clicked bottom_left arrow!")
        
        elif (arrow_positions['bottom_right'][0] <= position[0] <= arrow_positions['bottom_right'][0] + arrows['bottom_right'].get_width() and
              arrow_positions['bottom_right'][1] <= position[1] <= arrow_positions['bottom_right'][1] + arrows['bottom_right'].get_height()):
            rotation_quadrant = 'bottom_right'
            rotation_direction = 'clockwise'
            print("Clicked bottom_right arrow!")
        
        elif (arrow_positions['left_bottom'][0] <= position[0] <= arrow_positions['left_bottom'][0] + arrows['left_bottom'].get_width() and
              arrow_positions['left_bottom'][1] <= position[1] <= arrow_positions['left_bottom'][1] + arrows['left_bottom'].get_height()):
            rotation_quadrant = 'bottom_left'
            rotation_direction = 'clockwise'
            print("Clicked left_bottom arrow!")
        
        elif (arrow_positions['right_bottom'][0] <= position[0] <= arrow_positions['right_bottom'][0] + arrows['right_bottom'].get_width() and
              arrow_positions['right_bottom'][1] <= position[1] <= arrow_positions['right_bottom'][1] + arrows['right_bottom'].get_height()):
            rotation_quadrant = 'bottom_right'
            rotation_direction = 'clockwise'
            print("Clicked right_bottom arrow!")
        return rotation_quadrant,rotation_direction


    # arrow_centers = {
    #         'top_left': (arrow_positions['top_left'][0] + arrows['top_left'].get_width() // 2, 
    #                      arrow_positions['top_left'][1] + arrows['top_left'].get_height() // 2),
    #         'top_right': (arrow_positions['top_right'][0] + arrows['top_right'].get_width() // 2, 
    #                       arrow_positions['top_right'][1] + arrows['top_right'].get_height() // 2),
    #         'left_top': (arrow_positions['left_top'][0] + arrows['left_top'].get_width() // 2, 
    #                      arrow_positions['left_top'][1] + arrows['left_top'].get_height() // 2),
    #         'right_top': (arrow_positions['right_top'][0] + arrows['right_top'].get_width() // 2, 
    #                       arrow_positions['right_top'][1] + arrows['right_top'].get_height() // 2),
    #         'bottom_left': (arrow_positions['bottom_left'][0] + arrows['bottom_left'].get_width() // 2, 
    #                         arrow_positions['bottom_left'][1] + arrows['bottom_left'].get_height() // 2),
    #         'bottom_right': (arrow_positions['bottom_right'][0] + arrows['bottom_right'].get_width() // 2, 
    #                          arrow_positions['bottom_right'][1] + arrows['bottom_right'].get_height() // 2),
    #         'left_bottom': (arrow_positions['left_bottom'][0] + arrows['left_bottom'].get_width() // 2, 
    #                         arrow_positions['left_bottom'][1] + arrows['left_bottom'].get_height() // 2),
    #         'right_bottom': (arrow_positions['right_bottom'][0] + arrows['right_bottom'].get_width() // 2, 
    #                          arrow_positions['right_bottom'][1] + arrows['right_bottom'].get_height() // 2)
    #     }

    # threshold_distance = 20

    # for quadrant, center in arrow_centers.items():
    #     if distance(position, center) < threshold_distance:
    #         if quadrant == 'top_left':
    #             rotation_quadrant = quadrant
    #             rotation_direction = 'clockwise'
    #         if quadrant == 'top_right':
    #             rotation_quadrant = quadrant
    #             rotation_direction = 'counterclockwise'
    #         if quadrant == 'left_top':
    #             rotation_quadrant = 'top_left'
    #             rotation_direction = 'counterclockwise'  
    #         if quadrant == 'right_left':
    #             rotation_quadrant = 'top_right'
    #             rotation_direction = 'clockwise' 
    #         if quadrant == 'bottom_left':
    #             rotation_quadrant = quadrant
    #             rotation_direction = 'counterclockwise' 
    #         if quadrant == 'bottom_right':
    #             rotation_quadrant = quadrant
    #             rotation_direction = 'clockwise'
    #         if quadrant == 'left_bottom':
    #             rotation_quadrant = 'bottom_left'
    #             rotation_direction = 'clockwise'
    #         if quadrant == 'right_bottom':
    #             rotation_quadrant = 'bottom_right'
    #             rotation_direction = 'counterclockwise'









# Fonction principale (actions) pour un joueur ###########################################################################################################################""

def main():
    pentago_board = np.zeros((BOARD_SIZE, BOARD_SIZE))      # values

    draw_board(pentago_board)
    clicked = False
    # current_player = 1 
    current_player = random.choice([1,2])
    rotation_quadrant = None  
    rotation_direction = None  
    played = False

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and not clicked and not played:
                clicked = True
                position = pygame.mouse.get_pos()
                
                row = position[1] // (CELL_SIZE + PADDING)
                # print(row)
                col = position[0] // (CELL_SIZE + PADDING)

                if pentago_board[row, col] == 0:
                    pentago_board[row, col] = current_player

                    if current_player == 1:
                        pygame.draw.circle(screen, BLACK, (col * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING, row * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING), CELL_SIZE // 2)
                    else:
                        pygame.draw.circle(screen, RED, (col * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING, row * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING), CELL_SIZE // 2)
                    
                    pygame.display.flip()
                played = True
                arrows_displayed = True

            # elif event.type == pygame.MOUSEBUTTONUP and clicked:
            #     clicked = False

            elif played and arrows_displayed:
                arrow_positions = draw_arrows(pentago_board)[0]
                arrows = draw_arrows(pentago_board)[1]
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_position = pygame.mouse.get_pos()
                    check_arrow_clicked(pentago_board,mouse_position,arrow_positions,arrows)
                    rotation_quadrant = check_arrow_clicked(pentago_board,mouse_position,arrow_positions,arrows)[0]
                    rotation_direction = check_arrow_clicked(pentago_board,mouse_position,arrow_positions,arrows)[1]

                    

            elif event.type == pygame.KEYDOWN and played:
                if event.key == pygame.K_a:
                    rotation_quadrant = 'top_left'
                    print('a')
                elif event.key == pygame.K_z:
                    rotation_quadrant = 'top_right'
                elif event.key == pygame.K_q:
                    rotation_quadrant = 'bottom_left'
                elif event.key == pygame.K_s:
                    rotation_quadrant = 'bottom_right'
                elif event.key == pygame.K_LEFT:
                    rotation_direction = 'clockwise'
                elif event.key == pygame.K_RIGHT:
                    rotation_direction = 'counterclockwise'

            if rotation_quadrant and rotation_direction:
                print('hello')
                pentago_board = rotate_board(pentago_board, rotation_quadrant, rotation_direction)

                    # if rotation_quadrant == 'top-right' or rotation_quadrant == 'bottom-right':
                    #     pentago_board = np.fliplr(pentago_board)
                    # if rotation_quadrant == 'bottom-left' or rotation_quadrant == 'bottom-right':
                    #     pentago_board = np.flipud(pentago_board)

                draw_board(pentago_board)    
                update_board_display(pentago_board)
                pygame.display.flip()
                rotation_quadrant = None
                rotation_direction = None
                clicked = False

                if check_winner(pentago_board, current_player):
                    print(f"Player {current_player} wins!")
                    running = False

                current_player = 2 if current_player == 1 else 1
                played = False
                arrows_displayed = False

            
        clock.tick(FPS)
















# Fonction principale du jeu contre un joueur qui joue aléatoirement
def main_random():
    pentago_board = np.zeros((BOARD_SIZE, BOARD_SIZE))      

    draw_board(pentago_board)
    clicked = False
    
    current_player = random.choice([1,2])
    print('First player is player number ' + str(current_player))

    rotation_quadrant = None  
    rotation_direction = None  
    played = False
    arrows_displayed = False

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and not clicked and not played:
                clicked = True
                position = pygame.mouse.get_pos()
                
                row = position[1] // (CELL_SIZE + PADDING)
                col = position[0] // (CELL_SIZE + PADDING)

                if pentago_board[row, col] == 0:
                    pentago_board[row, col] = current_player

                    if current_player == 1:
                        pygame.draw.circle(screen, BLACK, (col * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING, row * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING), CELL_SIZE // 2)
                    else:
                        pygame.draw.circle(screen, RED, (col * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING, row * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING), CELL_SIZE // 2)
                    
                    pygame.display.flip()
                played = True
                arrows_displayed = True

            elif played and arrows_displayed:
                arrow_positions = draw_arrows(pentago_board)[0]
                arrows = draw_arrows(pentago_board)[1]
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_position = pygame.mouse.get_pos()
                    check_arrow_clicked(pentago_board,mouse_position,arrow_positions,arrows)
                    rotation_quadrant = check_arrow_clicked(pentago_board,mouse_position,arrow_positions,arrows)[0]
                    rotation_direction = check_arrow_clicked(pentago_board,mouse_position,arrow_positions,arrows)[1]


            if rotation_quadrant and rotation_direction:
                print('hello')
                pentago_board = rotate_board(pentago_board, rotation_quadrant, rotation_direction)

                draw_board(pentago_board)    
                update_board_display(pentago_board)
                pygame.display.flip()
                rotation_quadrant = None
                rotation_direction = None
                clicked = False

                if check_winner(pentago_board, current_player):
                    print(f"Player {current_player} wins!")
                    running = False
                    break

                current_player = 2 if current_player == 1 else 1
                played = False
                arrows_displayed = False

        clock.tick(FPS)

        
        if current_player == 2 and not check_winner(pentago_board, 1):
            
            col = np.random.randint(0, BOARD_SIZE)
            row = np.random.randint(0, BOARD_SIZE)

            if pentago_board[row, col] == 0:
                pentago_board[row, col] = current_player
                draw_board(pentago_board)
                update_board_display(pentago_board)
                pygame.display.flip()
                pygame.time.wait(1000)  

                rotation_direction = random.choice(['clockwise','couterclockwise'])
                rotation_quadrant = random.choice(['top_left','top_right','bottom_left','bottom_right'])

                if rotation_quadrant and rotation_direction:
                    print('hello')
                    pentago_board = rotate_board(pentago_board, rotation_quadrant, rotation_direction)

                    draw_board(pentago_board)    
                    update_board_display(pentago_board)
                    pygame.display.flip()
                    rotation_quadrant = None
                    rotation_direction = None
                    clicked = False

                if check_winner(pentago_board, current_player):
                    print(f"Player {current_player} wins!")
                    running = False
                    break

                current_player = 1



################ MiniMax ###############################################################################################################""



# def get_possible_moves(board):
#     possible_moves = []
#     for i in range(len(board)):
#         for j in range(len(board)):
#             if board[i][j] == 0:
#                 for rotation_quadrant in ['top_left', 'top_right', 'bottom_left', 'bottom_right']:
#                     for rotation_direction in ['clockwise', 'counterclockwise']:
#                         possible_moves.append((i, j, rotation_quadrant, rotation_direction))
#     return possible_moves

def get_possible_moves(board):
    possible_moves = []
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == 0:
                for rotation_quadrant in ['top_left', 'top_right', 'bottom_left', 'bottom_right']:
                    for rotation_direction in ['clockwise', 'counterclockwise']:
                        possible_moves.append((i, j, rotation_quadrant, rotation_direction))
    return possible_moves


#tentative d'amélioration pour acélérer le parcours 
def get_best_moves(board):
    quadrants = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
    directions = ['clockwise', 'counterclockwise']
    

    empty_adjacent_cells = []

    # parcourir le plateau
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] != 0:
                
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < len(board) and 0 <= nj < len(board) and board[ni][nj] == 0:
                        empty_adjacent_cells.append((ni, nj))

    # cellules adjacentes
    if empty_adjacent_cells:
        possible_moves = [
            (i, j, quadrant, direction)
            for i, j in empty_adjacent_cells
            for quadrant in quadrants
            for direction in directions
        ]
    else:
        # les cellules vides
        empty_cells = [(i, j) for i in range(len(board)) for j in range(len(board)) if board[i][j] == 0]
        possible_moves = [
            (i, j, quadrant, direction)
            for i, j in empty_cells
            for quadrant in quadrants
            for direction in directions
        ]
    
    # mouvements triés en fonction de la stratégie du Pentago
    possible_moves.sort(key=lambda move: evaluate_move(board, move))

    return possible_moves

def evaluate_move(board, move):
    i, j, quadrant, direction = move
    #évaluation basée sur la position
    position_value = 0
    if (i, j) in [(1, 1), (1, 4), (4, 1), (4, 4)]:
        position_value += 100  
    elif i in [0, BOARD_SIZE-1] or j in [0, BOARD_SIZE-1]:
        position_value += 50 
    elif i in [1, 3] and j in [1, 3]:
        position_value += 30  
    return position_value




def number_of_pieces(board):
    n = 0
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] != 0:
                n+=1
    return n

def is_terminal_node(board,depth):
    if check_winner(board,1)== True or check_winner(board,2)==True:
        return True
    elif is_board_full(board):
        return True
    elif number_of_pieces(board) == depth + 1:
        return True
    else:
        return False

def is_board_full(board):
    for i in range(6):
        for j in range(6):
            if board[i][j] == 0:
                return False
    return True

"""
def evaluate(board):
    if check_winner(board, 1):
        return 1000  
    elif check_winner(board, 2):
        return -1000  
    elif is_board_full(board):
        return 0  
    else:
        score = 0
        for i in range(len(board)):
            for j in range(len(board)):
                # Vérifie les lignes
                row_count = 0
                for k in range(len(board)):
                    if board[i][k] == 2:
                        row_count -= 1
                    elif board[i][k] == 1:
                        row_count = 0
                    score += row_count ** 2  

                    if board[i][k] == 1:
                        row_count += 1  

                # Vérifie les colonnes
                col_count = 0
                for k in range(len(board)):
                    if board[k][j] == 2:
                        col_count -= 1
                    elif board[k][j] == 1:
                        col_count = 0
                    score += col_count ** 2 

                    if board[k][j] == 1:
                        col_count += 1  

                # Vérifie les diagonales
                diag_count = 0
                for k in range(len(board)):
                    if i + k < len(board) and j + k < len(board):
                        if board[i + k][j + k] == 2:
                            diag_count -= 1
                        elif board[i + k][j + k] == 1:
                            diag_count = 0
                        score += diag_count ** 2

                        if board[i + k][j + k] == 1:
                            diag_count += 1 

                diag_count = 0
                for k in range(len(board)):
                    if i + k < len(board) and j - k >= 0:
                        if board[i + k][j - k] == 2:
                            diag_count -= 1
                        elif board[i + k][j - k] == 1:
                            diag_count = 0
                        score += diag_count ** 2

                        if board[i + k][j - k] == 1:
                            diag_count += 1  

        return score
"""

def evaluate(board, current_player):
    score = 0
    # ajouter un if current_player == 2 ?
    # Probabilité de former une ligne de cinq billes dans le futur
    score += evaluate_future_wins(board, current_player)

    # Défense contre les lignes potentielles de l'adversaire
    score -= evaluate_defense(board, current_player)

    # Position sur le plateau
    score += evaluate_position(board, current_player)

    return score

def evaluate_future_wins(board, current_player):
    # si le prochain coup est gagnant
    future_wins = 0
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == 0:
                
                board[i][j] = current_player
                if check_winner(board, current_player):
                    future_wins += 1
                board[i][j] = 0  # etat initial
    return future_wins

def evaluate_defense(board, current_player):
    # score en fonction de si l'adversaire est dangereux
    defense = 0
    opponent = 2 if current_player == 1 else 1
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == 0:
                
                board[i][j] = opponent
                if check_winner(board, opponent):
                    defense -= 1
                board[i][j] = 0  # etat initial
    return defense

def evaluate_position(board, current_player):
    # meilleures positions
    position_value = 0
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == 0:
                position_value += 1 
    return position_value
# fonction pas finie
    

def minimax(board, depth, maximizing_player,current_player):
    if depth == 0 or is_terminal_node(board,depth):
        return evaluate(board,current_player)

    if maximizing_player:
        max_eval = float('-inf')
        for move in get_best_moves(board):
            new_board = np.copy(board)
            new_board[move[0], move[1]] = 1
            new_board = rotate_board(new_board, move[2], move[3])
            eval = minimax(new_board, depth - 1, False,current_player)
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for move in get_best_moves(board):
            new_board = np.copy(board)
            new_board[move[0], move[1]] = 2
            new_board = rotate_board(new_board, move[2], move[3])
            eval = minimax(new_board, depth - 1, True,current_player)
            min_eval = min(min_eval, eval)
        return min_eval

    
# Fonction principale contre un joueur IA qui utilise minmax
def main_minimax():
    pentago_board = np.zeros((BOARD_SIZE, BOARD_SIZE))      

    draw_board(pentago_board)
    clicked = False
    
    current_player = random.choice([1,2])
    print('First player is player number ' + str(current_player))

    rotation_quadrant = None  
    rotation_direction = None  
    played = False
    arrows_displayed = False

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and not clicked and not played:
                clicked = True
                position = pygame.mouse.get_pos()
                
                row = position[1] // (CELL_SIZE + PADDING)
                col = position[0] // (CELL_SIZE + PADDING)

                if pentago_board[row, col] == 0:
                    pentago_board[row, col] = current_player

                    if current_player == 1:
                        pygame.draw.circle(screen, BLACK, (col * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING, row * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING), CELL_SIZE // 2)
                    else:
                        pygame.draw.circle(screen, RED, (col * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING, row * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING), CELL_SIZE // 2)
                    
                    pygame.display.flip()
                played = True
                arrows_displayed = True

            elif played and arrows_displayed:
                arrow_positions = draw_arrows(pentago_board)[0]
                arrows = draw_arrows(pentago_board)[1]
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_position = pygame.mouse.get_pos()
                    check_arrow_clicked(pentago_board,mouse_position,arrow_positions,arrows)
                    rotation_quadrant = check_arrow_clicked(pentago_board,mouse_position,arrow_positions,arrows)[0]
                    rotation_direction = check_arrow_clicked(pentago_board,mouse_position,arrow_positions,arrows)[1]


            if rotation_quadrant and rotation_direction:
                print('hello')
                pentago_board = rotate_board(pentago_board, rotation_quadrant, rotation_direction)

                draw_board(pentago_board)    
                update_board_display(pentago_board)
                pygame.display.flip()
                rotation_quadrant = None
                rotation_direction = None
                clicked = False

                if check_winner(pentago_board, current_player):
                    print(f"Player {current_player} wins!")
                    running = False
                    break

                current_player = 2 if current_player == 1 else 1
                played = False
                arrows_displayed = False

        clock.tick(FPS)

        
        if current_player == 2 and not check_winner(pentago_board, 1):
            print("let's see the problem")

            best_move = None
            best_score = float('-inf')
            DEPTH = 2
            print("depth"+str(DEPTH))
            #for move in get_possible_moves(pentago_board):
            for move in get_best_moves(pentago_board):
                print("entrée dans la boucle for")
                new_board = pentago_board.copy()
                new_board[move[0], move[1]] = current_player
                new_board = rotate_board(new_board, move[2], move[3])
                score = minimax(new_board, DEPTH, False,current_player)
                print(score)
                if score > best_score:
                    print("entrée dans la boucle if numéro un")
                    best_score = score
                    best_move = move
                    # move est un  4-uplet i,j,rotation_quadrant, horaire
                    # si plusieurs scores identiques comment choisir le mouvement ? Garder la dernière possibilitée ou pas
            
            if best_move is not None:
                print("entrée deuxieme if")
                print(f"Best move: {best_move}")
                pentago_board[best_move[0], best_move[1]] = current_player
                # draw_board(pentago_board)
                # update_board_display(pentago_board)
                
                # #pygame.time.wait(1000)
                
                pentago_board = rotate_board(pentago_board, best_move[2], best_move[3])
                
                draw_board(pentago_board)    
                update_board_display(pentago_board)
                pygame.display.flip()
                
                if check_winner(pentago_board, current_player):
                    print(f"Player {current_player} wins!")
                    running = False
                    break
            
            current_player = 1
    
    pygame.quit()
            

#################################### alpha-beta #####################################################################################

def minimax_alpha_beta(board, depth, alpha, beta, maximizing_player,current_player):
    if depth == 0 or is_terminal_node(board,depth):
        return evaluate(board,current_player)

    if maximizing_player:
        max_eval = float('-inf')
        for move in get_best_moves(board):
            new_board = board.copy()
            new_board[move[0], move[1]] = 1
            new_board = rotate_board(new_board, move[2], move[3])
            eval = minimax_alpha_beta(new_board, depth - 1, alpha, beta, False, current_player)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Coupe 
        return max_eval
    else:
        min_eval = float('inf')
        for move in get_best_moves(board):
            new_board = board.copy()
            new_board[move[0], move[1]] = 2
            new_board = rotate_board(new_board, move[2], move[3])
            eval = minimax_alpha_beta(new_board, depth - 1, alpha, beta, True, current_player)
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Couper l'arbre
        return min_eval

# Fonction principale utilisant Minimax avec alpha-beta pruning
def main_minimax_alpha_beta():
    pentago_board = np.zeros((BOARD_SIZE, BOARD_SIZE))      

    draw_board(pentago_board)
    clicked = False
    
    current_player = random.choice([1, 2])
    print('Le premier joueur est le joueur ' + str(current_player))

    rotation_quadrant = None  
    rotation_direction = None  
    played = False
    arrows_displayed = False

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and not clicked and not played:
                clicked = True
                position = pygame.mouse.get_pos()
                
                row = position[1] // (CELL_SIZE + PADDING)
                col = position[0] // (CELL_SIZE + PADDING)

                if pentago_board[row, col] == 0:
                    pentago_board[row, col] = current_player

                    if current_player == 1:
                        pygame.draw.circle(screen, BLACK, (col * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING, row * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING), CELL_SIZE // 2)
                    else:
                        pygame.draw.circle(screen, RED, (col * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING, row * (CELL_SIZE + PADDING) + CELL_SIZE // 2 + PADDING), CELL_SIZE // 2)
                    
                    pygame.display.flip()
                played = True
                arrows_displayed = True

            elif played and arrows_displayed:
                arrow_positions = draw_arrows(pentago_board)[0]
                arrows = draw_arrows(pentago_board)[1]
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_position = pygame.mouse.get_pos()
                    check_arrow_clicked(pentago_board, mouse_position, arrow_positions, arrows)
                    rotation_quadrant = check_arrow_clicked(pentago_board, mouse_position, arrow_positions, arrows)[0]
                    rotation_direction = check_arrow_clicked(pentago_board, mouse_position, arrow_positions, arrows)[1]


            if rotation_quadrant and rotation_direction:
                print('hello')
                pentago_board = rotate_board(pentago_board, rotation_quadrant, rotation_direction)

                draw_board(pentago_board)    
                update_board_display(pentago_board)
                pygame.display.flip()
                rotation_quadrant = None
                rotation_direction = None
                clicked = False

                if check_winner(pentago_board, current_player):
                    print(f"Player {current_player} wins!")
                    running = False
                    break

                current_player = 2 if current_player == 1 else 1
                played = False
                arrows_displayed = False

        clock.tick(FPS)

        
        if current_player == 2 and not check_winner(pentago_board, 1):

            best_move = None
            best_score = float('-inf')
            DEPTH = 2
            alpha = float('-inf')
            beta = float('inf')
            for move in get_best_moves(pentago_board):
                new_board = pentago_board.copy()
                new_board[move[0], move[1]] = current_player
                new_board = rotate_board(new_board, move[2], move[3])
                score = minimax_alpha_beta(new_board, DEPTH, alpha, beta, False, current_player)
                if score > best_score:
                    best_score = score
                    best_move = move
            
            if best_move is not None:
                pentago_board[best_move[0], best_move[1]] = current_player
                
                
                pentago_board = rotate_board(pentago_board, best_move[2], best_move[3])
                
                draw_board(pentago_board)    
                update_board_display(pentago_board)
                pygame.display.flip()
                
                if check_winner(pentago_board, current_player):
                    print(f"Player {current_player} wins!")
                    running = False
                    break
            
            current_player = 1
    pygame.quit()
   

######################################################## La même en simulation (alpha-beta) ######################################################"##########################################
#############################################################################################################################################################################################################################

def main_minimax_ab_simu():
    BOARD_SIZE = 6
    EPISODES = 50   #trop long
    DEPTH = 2

    rewards = []
    episode_durations = []
    move_durations = []
    game_data = []
    total_start_time = time.time()

    for episode in range(EPISODES):
        pentago_board = np.zeros((BOARD_SIZE, BOARD_SIZE))
        starting_player = random.choice([1, 2])
        current_player = starting_player
        total_reward = 0
        done = False
        episode_start_time = time.time()
        episode_move_durations = []

        while not done:
            move_start_time = time.time()
            best_move = None
            best_score = float('-inf') if current_player == 1 else float('inf')
            alpha = float('-inf')
            beta = float('inf')

            for move in get_best_moves(pentago_board):
                new_board = pentago_board.copy()
                new_board[move[0], move[1]] = current_player
                new_board = rotate_board(new_board, move[2], move[3])
                score = minimax_alpha_beta(new_board, DEPTH, alpha, beta, current_player == 1, current_player)
                if (current_player == 1 and score > best_score) or (current_player == 2 and score < best_score):
                    best_score = score
                    best_move = move
            
            if best_move is not None:
                pentago_board[best_move[0], best_move[1]] = current_player
                pentago_board = rotate_board(pentago_board, best_move[2], best_move[3])

            if check_winner(pentago_board, current_player):
                reward = 1 if current_player == 1 else -1
                done = True
                winning_player = current_player
            elif is_terminal_state(pentago_board):
                reward = 0
                done = True
                winning_player = None
            else:
                reward = 0

            total_reward += reward

            current_player = 2 if current_player == 1 else 1
            move_end_time = time.time()
            move_duration = move_end_time - move_start_time
            episode_move_durations.append(move_duration)

        episode_end_time = time.time()
        episode_duration = episode_end_time - episode_start_time
        episode_durations.append(episode_duration)
        rewards.append(total_reward)
        move_durations.append(episode_move_durations)

        game_data.append({
            'episode': episode + 1,
            'starting_player': starting_player,
            'winning_player': winning_player,
            'final_board': pentago_board.copy(),
            'episode_duration': episode_duration,
            'move_durations': episode_move_durations
        })

    total_end_time = time.time()
    total_duration = total_end_time - total_start_time

    with open('minimax_ab_simulation_data.pkl', 'wb') as f:
        pickle.dump((rewards, episode_durations, move_durations, game_data, total_duration), f)

# Fonction pour tracer les graphes pertinents
def plot_minimax_ab_simulation_data():
    with open('minimax_ab_simulation_data.pkl', 'rb') as f:
        rewards, episode_durations, move_durations, game_data, total_duration = pickle.load(f)

    plt.figure(figsize=(15, 8))

    
    plt.figure(figsize=(10, 6))
    plt.plot(np.cumsum(rewards), label='Cumulative Rewards', color='blue')
    plt.xlabel('Episode')
    plt.ylabel('Cumulative Reward')
    plt.title('Cumulative Rewards over Episodes')
    plt.legend()
    plt.grid(True)
    plt.show()

    
    window_size = 50
    reward_smoothed = np.convolve(rewards, np.ones(window_size)/window_size, mode='valid')
    plt.figure(figsize=(10, 6))
    plt.plot(reward_smoothed, label=f'Smoothed Rewards (window size {window_size})', color='green')
    plt.xlabel('Episode')
    plt.ylabel('Smoothed Reward')
    plt.title('Smoothed Rewards over Episodes')
    plt.legend()
    plt.grid(True)
    plt.show()

    
    plt.figure(figsize=(10, 6))
    plt.plot(episode_durations, label='Episode Duration', color='orange')
    plt.xlabel('Episode')
    plt.ylabel('Duration (seconds)')
    plt.title('Duration per Episode')
    plt.legend()
    plt.grid(True)
    plt.show()

    
    move_durations_flat = [item for sublist in move_durations for item in sublist]
    plt.figure(figsize=(10, 6))
    plt.plot(move_durations_flat, label='Move Duration', color='red', alpha=0.5)
    plt.xlabel('Move')
    plt.ylabel('Duration (seconds)')
    plt.title('Duration per Move')
    plt.legend()
    plt.grid(True)
    plt.show()

    
    player1_wins = [1 if data['winning_player'] == 1 else 0 for data in game_data]
    player2_wins = [1 if data['winning_player'] == 2 else 0 for data in game_data]
    plt.figure(figsize=(10, 6))
    plt.plot(np.cumsum(player1_wins) / (np.arange(len(player1_wins)) + 1), label='Win Rate of Player 1', color='green')
    plt.plot(np.cumsum(player2_wins) / (np.arange(len(player2_wins)) + 1), label='Win Rate of Player 2', color='red')
    plt.xlabel('Episode')
    plt.ylabel('Win Rate')
    plt.title('Win Rates Over Episodes')
    plt.legend()
    plt.grid(True)
    plt.show()

    
    starting_player_wins = {
        'player_1': sum(1 for data in game_data if data['starting_player'] == 1 and data['winning_player'] == 1),
        'player_2': sum(1 for data in game_data if data['starting_player'] == 2 and data['winning_player'] == 2)
    }
    starting_player_losses = {
        'player_1': sum(1 for data in game_data if data['starting_player'] == 1 and data['winning_player'] == 2),
        'player_2': sum(1 for data in game_data if data['starting_player'] == 2 and data['winning_player'] == 1)
    }

    plt.figure(figsize=(10, 6))
    plt.bar(['Player 1 Starts', 'Player 2 Starts'], [starting_player_wins['player_1'], starting_player_wins['player_2']], label='Wins', alpha=0.6)
    plt.bar(['Player 1 Starts', 'Player 2 Starts'], [starting_player_losses['player_1'], starting_player_losses['player_2']], label='Losses', alpha=0.6, bottom=[starting_player_wins['player_1'], starting_player_wins['player_2']])
    plt.xlabel('Starting Player')
    plt.ylabel('Number of Games')
    plt.title('Win/Loss Distribution by Starting Player')
    plt.legend()
    plt.grid(True)
    plt.show()

    
    print(f"Total duration of all games: {total_duration:.2f} seconds")






#####################################################################################################################################################################""
###################################################### Tentative apprentissage ###############################################################################################

import numpy as np
import random
import pygame
import collections
import itertools
import pickle

def get_state(board):
    return tuple(board.flatten())

# def get_possible_moves(board):
#     moves = []
#     for i in range(board.shape[0]):
#         for j in range(board.shape[1]):
#             if board[i, j] == 0:
#                 for quadrant in range(4):
#                     for direction in [1, -1]:
#                         moves.append((i, j, quadrant, direction))
#     return moves

def apply_move(board, move, player):
    
    board[move[0], move[1]] = player
    board = rotate_board(board, move[2], move[3])
    draw_board(board)
    return board


def is_terminal_state(board):
    return check_winner(board, 1) or check_winner(board, 2) or np.all(board != 0)



# Fonction dapprentisage Qlearning
''' class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.q_table = collections.defaultdict(float)

    def choose_action(self, state, possible_moves):
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(possible_moves)
        q_values = [self.q_table[(state, move)] for move in possible_moves]
        max_q = max(q_values)
        max_q_moves = [move for move, q in zip(possible_moves, q_values) if q == max_q]
        return random.choice(max_q_moves)

    def learn(self, state, action, reward, next_state, next_possible_moves):
        next_q_values = [self.q_table[(next_state, next_move)] for next_move in next_possible_moves]
        max_next_q = max(next_q_values, default=0)
        current_q = self.q_table[(state, action)]
        self.q_table[(state, action)] = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)

    def save_q_table(self, file_name):
        with open(file_name, 'wb') as f:
            pickle.dump(dict(self.q_table), f)

    def load_q_table(self, file_name):
        with open(file_name, 'rb') as f:
            self.q_table = collections.defaultdict(float, pickle.load(f))
 '''

class QLearningAgent:
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1, epsilon_min=0.01, epsilon_decay=0.995):
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.q_table = collections.defaultdict(float)

    def choose_action(self, state, possible_moves):
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(possible_moves)
        q_values = [self.q_table[(state, move)] for move in possible_moves]
        max_q = max(q_values)
        max_q_moves = [move for move, q in zip(possible_moves, q_values) if q == max_q]
        return random.choice(max_q_moves)

    def learn(self, state, action, reward, next_state, next_possible_moves):
        next_q_values = [self.q_table[(next_state, next_move)] for next_move in next_possible_moves]
        max_next_q = max(next_q_values, default=0)
        current_q = self.q_table[(state, action)]
        self.q_table[(state, action)] = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def save_q_table(self, file_name):
        with open(file_name, 'wb') as f:
            pickle.dump(dict(self.q_table), f)

    def load_q_table(self, file_name):
        with open(file_name, 'rb') as f:
            self.q_table = collections.defaultdict(float, pickle.load(f))

# fonction principale
def main_q_learning():
    
    

    pygame.init()
    screen = pygame.display.set_mode((BOARD_SIZE * (CELL_SIZE + PADDING), BOARD_SIZE * (CELL_SIZE + PADDING)))
    pygame.display.set_caption("Pentago")
    clock = pygame.time.Clock()

    agent = QLearningAgent()
    try:
        agent.load_q_table("q_table.pkl")
    except:
        pass

    pentago_board = np.zeros((BOARD_SIZE, BOARD_SIZE))
    current_player = random.choice([1, 2])
    print('Le premier joueur est le joueur numéro ' + str(current_player))

    running = True
    played = False
    arrows_displayed = False
    rotation_quadrant = None
    rotation_direction = None

    while running:
        if current_player == 1:  
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and not played:
                    position = pygame.mouse.get_pos()
                    row = position[1] // (CELL_SIZE + PADDING)
                    col = position[0] // (CELL_SIZE + PADDING)

                    if pentago_board[row, col] == 0:
                        pentago_board[row, col] = current_player
                        draw_board(pentago_board)
                        pygame.display.flip()
                        played = True
                        arrows_displayed = True

                elif played and arrows_displayed:
                    arrow_positions = draw_arrows(pentago_board)[0]
                    arrows = draw_arrows(pentago_board)[1]
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_position = pygame.mouse.get_pos()
                        rotation_quadrant, rotation_direction = check_arrow_clicked(pentago_board, mouse_position, arrow_positions, arrows)

            if rotation_quadrant is not None and rotation_direction is not None:
                pentago_board = rotate_board(pentago_board, rotation_quadrant, rotation_direction)
                draw_board(pentago_board)
                pygame.display.flip()
                rotation_quadrant = None
                rotation_direction = None
                played = False
                arrows_displayed = False

                if check_winner(pentago_board, current_player):
                    print(f"Player {current_player} wins!")
                    running = False
                    break

                current_player = 2

        else:  
            
        # Tour de l'ordinateur
            state = get_state(pentago_board)
            possible_moves = get_possible_moves(pentago_board)
            action = agent.choose_action(state, possible_moves)
            pentago_board = apply_move(pentago_board, action, current_player)
            draw_board(pentago_board)
            update_board_display(pentago_board)
            pygame.display.flip()

            if check_winner(pentago_board, current_player):
                print(f"Player {current_player} wins!")
                running = False
                break

            current_player = 1

        clock.tick(FPS)

    agent.save_q_table("q_table.pkl")
    pygame.quit()













# Simulation joueur 1 et joueur 2 ordinateurs"
# Fonction principale ############################################ Simulation !!
# def main_q_learning_simu():
#     BOARD_SIZE = 6
#     CELL_SIZE = 50
#     PADDING = 10
#     FPS = 30
#     EPISODES = 1000

#     pygame.init()
#     screen = pygame.display.set_mode((BOARD_SIZE * (CELL_SIZE + PADDING), BOARD_SIZE * (CELL_SIZE + PADDING)))
#     pygame.display.set_caption("Pentago")
#     clock = pygame.time.Clock()

#     agent = QLearningAgent()
#     rewards = []
#     times = []

#     for episode in range(EPISODES):
#         pentago_board = np.zeros((BOARD_SIZE, BOARD_SIZE))
#         current_player = random.choice([1, 2])
#         state = get_state(pentago_board)
#         total_reward = 0
#         done = False

#         while not done:
#             start_time = time.time()
#             possible_moves = get_possible_moves(pentago_board)
#             action = agent.choose_action(state, possible_moves)
#             new_board = apply_move(pentago_board, action, current_player)
#             next_state = get_state(new_board)
#             reward = 0

#             if check_winner(new_board, current_player):
#                 reward = 1
#                 done = True
#             elif is_terminal_state(new_board):
#                 reward = 0.5
#                 done = True

#             next_possible_moves = get_possible_moves(new_board)
#             agent.learn(state, action, reward, next_state, next_possible_moves)

#             state = next_state
#             pentago_board = new_board
#             total_reward += reward

#             if done:
#                 rewards.append(total_reward)
#                 print(f"Episode {episode + 1}: Total Reward = {total_reward}")

#             end_time = time.time()
#             time_taken = end_time - start_time #temps pris pour jouer le coup (s)

#             times.append(time_taken)
#             current_player = 2 if current_player == 1 else 1

#         if episode % 100 == 0:
#             agent.save_q_table(f"q_table_{episode}.pkl")

#     pygame.quit()





def main_q_learning_simu():
    BOARD_SIZE = 6
    EPISODES = 10000

    agent = QLearningAgent()
    rewards = []
    episode_durations = []
    move_durations = []
    game_data = []
    total_start_time = time.time()

    for episode in range(EPISODES):
        pentago_board = np.zeros((BOARD_SIZE, BOARD_SIZE))
        starting_player = random.choice([1, 2])
        current_player = starting_player
        state = get_state(pentago_board)
        total_reward = 0
        done = False
        episode_start_time = time.time()

        while not done:
            move_start_time = time.time()
            possible_moves = get_possible_moves(pentago_board)
            action = agent.choose_action(state, possible_moves)
            new_board = apply_move(pentago_board, action, current_player)
            next_state = get_state(new_board)
            reward = 0

            if check_winner(new_board, current_player):
                reward = 1
                done = True
                winning_player = current_player
            elif is_terminal_state(new_board):
                reward = 0.5
                done = True
                winning_player = None

            next_possible_moves = get_possible_moves(new_board)
            agent.learn(state, action, reward, next_state, next_possible_moves)

            state = next_state
            pentago_board = new_board
            total_reward += reward

            print(f"Player {current_player} made a move:")
            print(pentago_board)

            current_player = 2 if current_player == 1 else 1
            move_end_time = time.time()
            move_duration = move_end_time - move_start_time
            move_durations.append(move_duration)

        episode_end_time = time.time()
        episode_duration = episode_end_time - episode_start_time
        episode_durations.append(episode_duration)
        rewards.append(total_reward)
        

        game_data.append({
            'episode': episode + 1,
            'starting_player': starting_player,
            'winning_player': winning_player,
            'final_board': pentago_board.copy(),
            'episode_duration': episode_duration,
            'move_duration': move_duration
        })

        if episode % 100 == 0:
            agent.save_q_table(f"q_table_{episode}.pkl")

    total_end_time = time.time()
    total_duration = total_end_time - total_start_time

    with open('simulation_data.pkl', 'wb') as f:
        pickle.dump((rewards, episode_durations, game_data, total_duration), f)

# Total duration of all games: 7179.77 seconds          pour simuler 10000 episodes

# FOnction qui permet de récupérer les images des courbes obtenues à partir des données





    # plt.subplot(2, 2, 1)
    # plt.plot(rewards, label='Total Rewards')
    # plt.xlabel('Episode')
    # plt.ylabel('Total Reward')
    # plt.title('Total Rewards per Episode')
    # plt.legend()



def plot_simulation_data():
    with open('simulation_data.pkl', 'rb') as f:
        rewards, episode_durations, game_data, total_duration = pickle.load(f)

    
    plt.figure(figsize=(10, 6))
    plt.plot(np.cumsum(rewards), label='Cumulative Rewards', color='blue')
    plt.xlabel('Episode')
    plt.ylabel('Cumulative Reward')
    plt.title('Cumulative Rewards over Episodes')
    plt.legend()
    plt.grid(True)
    plt.show()

    
    window_size = 50
    reward_smoothed = np.convolve(rewards, np.ones(window_size)/window_size, mode='valid')

    plt.figure(figsize=(10, 6))
    plt.plot(reward_smoothed, label=f'Smoothed Rewards (window size {window_size})', color='green')
    plt.xlabel('Episode')
    plt.ylabel('Smoothed Reward')
    plt.title('Smoothed Rewards over Episodes')
    plt.legend()
    plt.grid(True)
    plt.show()

    
    plt.figure(figsize=(10, 6))
    plt.plot(episode_durations, label='Episode Duration', color='orange')
    plt.xlabel('Episode')
    plt.ylabel('Duration (seconds)')
    plt.title('Duration per Episode')
    plt.legend()
    plt.grid(True)
    plt.show()

    
    move_durations = [data['move_duration'] for data in game_data]

    plt.figure(figsize=(10, 6))
    plt.plot(move_durations, label='Move Duration', color='purple')
    plt.xlabel('Move')
    plt.ylabel('Duration (seconds)')
    plt.title('Duration per Move in Episodes')
    plt.grid(True)
    plt.show()

    
    win_rates_player_1 = np.cumsum([1 if data['winning_player'] == 1 else 0 for data in game_data]) / (np.arange(len(game_data)) + 1)
    win_rates_player_2 = np.cumsum([1 if data['winning_player'] == 2 else 0 for data in game_data]) / (np.arange(len(game_data)) + 1)

    plt.figure(figsize=(10, 6))
    plt.plot(win_rates_player_1, label='Player 1 Win Rate', color='green')
    plt.plot(win_rates_player_2, label='Player 2 Win Rate', color='blue')
    plt.xlabel('Episode')
    plt.ylabel('Win Rate')
    plt.title('Win Rates of Player 1 and Player 2 Over Episodes')
    plt.legend()
    plt.grid(True)
    plt.show()

    
    starting_player_wins = {
        'player_1': sum(1 for data in game_data if data['starting_player'] == 1 and data['winning_player'] == 1),
        'player_2': sum(1 for data in game_data if data['starting_player'] == 2 and data['winning_player'] == 2)
    }
    starting_player_losses = {
        'player_1': sum(1 for data in game_data if data['starting_player'] == 1 and data['winning_player'] == 2),
        'player_2': sum(1 for data in game_data if data['starting_player'] == 2 and data['winning_player'] == 1)
    }

    plt.figure(figsize=(10, 6))
    plt.bar(['Player 1 Starts', 'Player 2 Starts'], [starting_player_wins['player_1'], starting_player_wins['player_2']], label='Wins', alpha=0.6)
    plt.bar(['Player 1 Starts', 'Player 2 Starts'], [starting_player_losses['player_1'], starting_player_losses['player_2']], label='Losses', alpha=0.6, bottom=[starting_player_wins['player_1'], starting_player_wins['player_2']])
    plt.xlabel('Starting Player')
    plt.ylabel('Number of Games')
    plt.title('Win/Loss Distribution by Starting Player')
    plt.legend()
    plt.grid(True)
    plt.show()

   
    print(f"Total duration of all games: {total_duration:.2f} seconds")


# Fonction principale contre un joueur IA codé à la main 
# def main_handmade()




def profile_simulation():
    pr = cProfile.Profile()
    pr.enable()

    #main_minimax_ab_simu() 
    main_minimax_alpha_beta()

    pr.disable()
    s = StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    with open('profiling_results.txt', 'w') as f:
        f.write(s.getvalue())

# profile_simulation()






if __name__ == "__main__":
    main_menu()

