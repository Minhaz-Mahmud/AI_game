import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pygame
from main import update_scoreboard, increment_score, check_sos, check_winner, \
    check_game_end, handle_click_ai, player_turn, player1_score, player2_score, enable_all_buttons

pygame.mixer.init()

# Initialize global variables
board_window = None
buttons = []
board = []
blank_image = None
circle_image = None
square_image = None
player1 = "Player 1"
player2 = "Player 2"

import random
import heapq

# Memoization dictionary
memo = {}

def evaluate_board(board):
    score = 0
    for row in range(len(board)):
        for col in range(len(board[0])):
            if board[row][col] == 'S':
                if col + 2 < len(board[0]) and board[row][col + 1] == 'O' and board[row][col + 2] == 'S':
                    score += 1
                if row + 2 < len(board) and board[row + 1][col] == 'O' and board[row + 2][col] == 'S':
                    score += 1
                if row + 2 < len(board) and col + 2 < len(board[0]) and board[row + 1][col + 1] == 'O' and \
                        board[row + 2][col + 2] == 'S':
                    score += 1
                if row + 2 < len(board) and col - 2 >= 0 and board[row + 1][col - 1] == 'O' and board[row + 2][
                    col - 2] == 'S':
                    score += 1
            elif board[row][col] == 'O':
                if col - 1 >= 0 and col + 1 < len(board[0]) and board[row][col - 1] == 'S' and board[row][
                    col + 1] == 'S':
                    score += 1
                if row - 1 >= 0 and row + 1 < len(board) and board[row - 1][col] == 'S' and board[row + 1][col] == 'S':
                    score += 1
                if row - 1 >= 0 and row + 1 < len(board) and col - 1 >= 0 and col + 1 < len(board[0]) and \
                        board[row - 1][col - 1] == 'S' and board[row + 1][col + 1] == 'S':
                    score += 1
                if row - 1 >= 0 and row + 1 < len(board) and col + 1 < len(board[0]) and col - 1 >= 0 and \
                        board[row - 1][col + 1] == 'S' and board[row + 1][col - 1] == 'S':
                    score += 1
    return score


def heuristic(board):
    board_tuple = tuple(tuple(row) for row in board)
    if board_tuple in memo:
        return memo[board_tuple]
    score = evaluate_board(board)
    memo[board_tuple] = score
    return score


def get_possible_moves(board):
    moves = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == '':
                moves.append((i, j))
    return moves


def a_star(board, max_depth):
    pq = []
    initial_moves = get_possible_moves(board)
    
    # Optimize: limit initial exploration to reduce calculation time
    if len(initial_moves) > 30:
        initial_moves = random.sample(initial_moves, 30)
    
    for move in initial_moves:
        i, j = move
        board[i][j] = 'S'
        score = heuristic(board)
        heapq.heappush(pq, (-score, 0, move, 'S'))
        board[i][j] = ''
        board[i][j] = 'O'
        score = heuristic(board)
        heapq.heappush(pq, (-score, 0, move, 'O'))
        board[i][j] = ''

    best_move = (-1, -1)
    best_char = 'S'
    best_score = -1000
    
    explored = 0
    max_explore = 100  # Limit exploration for faster response

    while pq and explored < max_explore:
        neg_score, depth, (i, j), char = heapq.heappop(pq)
        score = -neg_score
        explored += 1
        
        if score > best_score:
            best_score = score
            best_move = (i, j)
            best_char = char

        if depth < max_depth:
            board[i][j] = char
            next_moves = get_possible_moves(board)
            
            # Limit next moves for performance
            if len(next_moves) > 15:
                next_moves = random.sample(next_moves, 15)
            
            for next_move in next_moves:
                ni, nj = next_move
                board[ni][nj] = 'S'
                next_score = heuristic(board)
                heapq.heappush(pq, (-next_score, depth + 1, next_move, 'S'))
                board[ni][nj] = ''
                board[ni][nj] = 'O'
                next_score = heuristic(board)
                heapq.heappush(pq, (-next_score, depth + 1, next_move, 'O'))
                board[ni][nj] = ''
            board[i][j] = ''

    return best_move, best_char


def ai_make_move(board, buttons, circle_image, square_image, player_turn, board_window, root,
                 update_scoreboard, check_winner, check_game_end, scoreboard_frame, player1, player2):
    if player_turn[0] == 2:  # AI's turn (player 2)
        max_depth = 1  # Reduced for faster calculation
        best_move, best_char = a_star(board, max_depth)
        if best_move != (-1, -1):
            row, col = best_move
            handle_click_ai(None, row, col, board, buttons, circle_image, square_image,
                player_turn, board_window, root, update_scoreboard,
                check_winner, check_game_end, scoreboard_frame, player1, player2,
                ai_make_move, best_char)

            # Check if the AI should make another move (recursively handled by handle_click_ai)
            # No while loop here - it will be called again by handle_click_ai if AI gets another turn

    # Check if board_window still exists before enabling buttons
    try:
        if board_window and board_window.winfo_exists():
            enable_all_buttons(buttons)
    except:
        pass  # Window was destroyed, skip enabling buttons


def enable_all_buttons(buttons):
    for row in buttons:
        for button in row:
            try:
                if button and button.winfo_exists():
                    if button["text"] == "":  # Only enable empty buttons
                        button.state(["!disabled"])
            except:
                pass  # Button was destroyed, skip it


def apply_a_star(root_window, p1, p2):
    global board_window, player1, player2, board_size, board, buttons, scoreboard_frame
    global blank_image, circle_image, square_image

    player1 = p1
    player2 = p2

    pygame.mixer.music.pause()

    board_window = tk.Toplevel(root_window)
    board_window.title("SOS-MEDIUM MODE")

    window_width = 900
    window_height = 650

    screen_width = root_window.winfo_screenwidth()
    screen_height = root_window.winfo_screenheight()

    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)

    board_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    board_window.resizable(False, False)

    # Create styles for matched SOS buttons
    style = ttk.Style()
    style.configure("SOS1.TButton", background="green")
    style.configure("SOS2.TButton", background="red")

    pygame.mixer.music.load("resources/music/forest.mp3")
    pygame.mixer.music.play(-1)

    main_frame = ttk.Frame(board_window, style="Custom.TFrame")
    main_frame.place(relx=0.5, rely=0.5, anchor="center")

    background_image = Image.open("resources/images/background_medium.png")
    frame_background_photo = ImageTk.PhotoImage(background_image.resize((window_width, window_height), Image.LANCZOS))
    frame_background_label = tk.Label(main_frame, image=frame_background_photo)
    frame_background_label.image = frame_background_photo
    frame_background_label.place(x=0, y=0, relwidth=1, relheight=1)

    board_frame = ttk.Frame(main_frame, style="Custom.TFrame")
    board_frame.grid(row=0, column=0, padx=(20, 10), pady=20)

    scoreboard_frame = tk.Canvas(main_frame, width=180, height=80)
    scoreboard_frame.grid(row=0, column=1, padx=(10, 20), pady=0)

    scoreboard_image = Image.open("resources/images/score_board.png")
    scoreboard_photo = ImageTk.PhotoImage(scoreboard_image.resize((200, 100), Image.LANCZOS))
    scoreboard_frame.create_image(0, 0, image=scoreboard_photo, anchor="nw")
    scoreboard_frame.image = scoreboard_photo

    update_scoreboard(scoreboard_frame, player1, player2)

    board_size = 7
    board = [['' for _ in range(board_size)] for _ in range(board_size)]

    # Load static images instead of GIF frames
    blank_image = ImageTk.PhotoImage(Image.open("resources/images/blank.jpg").resize((40, 40), Image.LANCZOS))
    circle_image = ImageTk.PhotoImage(Image.open("resources/images/circle.jpg").resize((40, 40), Image.LANCZOS))
    square_image = ImageTk.PhotoImage(Image.open("resources/images/sq.jpg").resize((40, 40), Image.LANCZOS))

    buttons = [[None for _ in range(board_size)] for _ in range(board_size)]
    for row in range(board_size):
        for col in range(board_size):
            button = ttk.Button(board_frame, text='', width=5,
                                command=lambda r=row, c=col: handle_click_ai(None, r, c, board, buttons, circle_image,
                                                                             square_image,
                                                                             player_turn, board_window, root_window,
                                                                             update_scoreboard, check_winner,
                                                                             check_game_end,
                                                                             scoreboard_frame, player1, player2,
                                                                             ai_make_move))

            button.grid(row=row, column=col, padx=5, pady=5)
            button.config(image=blank_image)
            button.bind('<Button-1>',
                        lambda event, r=row, c=col: handle_click_ai(event, r, c, board, buttons, circle_image,
                                                                    square_image,
                                                                    player_turn, board_window, root_window,
                                                                    update_scoreboard, check_winner, check_game_end,
                                                                    scoreboard_frame, player1, player2,
                                                                    ai_make_move))

            button.bind('<Button-3>',
                        lambda event, r=row, c=col: handle_click_ai(event, r, c, board, buttons, circle_image,
                                                                    square_image,
                                                                    player_turn, board_window, root_window,
                                                                    update_scoreboard, check_winner, check_game_end,
                                                                    scoreboard_frame, player1, player2,
                                                                    ai_make_move))
            buttons[row][col] = button

    board_window.protocol("WM_DELETE_WINDOW", root_window.destroy)


if __name__ == "__main__":
    root = tk.Tk()
    root.option_add("*Font", "Digital-7 12")
    apply_a_star(root, "Player 1", "Player 2")
    root.mainloop()