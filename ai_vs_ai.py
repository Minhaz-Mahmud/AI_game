import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import pygame
import random
import heapq
import numpy as np

pygame.mixer.init()

# Global variables
board_window = None
buttons = []
board = []
blank_image = None
circle_image = None
square_image = None
player1_score = 0
player2_score = 0
player_turn = [1]
game_paused = False
move_delay = 1000

# ==================== CORE ALGORITHMS ====================

def evaluate_board(board):
    """Count potential SOS patterns on board"""
    score = 0
    for row in range(len(board)):
        for col in range(len(board[0])):
            if board[row][col] == 'S':
                # Check all 4 directions for S-O-S
                if col + 2 < len(board[0]) and board[row][col + 1] == 'O' and board[row][col + 2] == 'S':
                    score += 1
                if row + 2 < len(board) and board[row + 1][col] == 'O' and board[row + 2][col] == 'S':
                    score += 1
                if row + 2 < len(board) and col + 2 < len(board[0]) and board[row + 1][col + 1] == 'O' and board[row + 2][col + 2] == 'S':
                    score += 1
                if row + 2 < len(board) and col - 2 >= 0 and board[row + 1][col - 1] == 'O' and board[row + 2][col - 2] == 'S':
                    score += 1
            elif board[row][col] == 'O':
                # Check if O is between two S's
                if col - 1 >= 0 and col + 1 < len(board[0]) and board[row][col - 1] == 'S' and board[row][col + 1] == 'S':
                    score += 1
                if row - 1 >= 0 and row + 1 < len(board) and board[row - 1][col] == 'S' and board[row + 1][col] == 'S':
                    score += 1
                if row - 1 >= 0 and row + 1 < len(board) and col - 1 >= 0 and col + 1 < len(board[0]) and board[row - 1][col - 1] == 'S' and board[row + 1][col + 1] == 'S':
                    score += 1
                if row - 1 >= 0 and row + 1 < len(board) and col + 1 < len(board[0]) and col - 1 >= 0 and board[row - 1][col + 1] == 'S' and board[row + 1][col - 1] == 'S':
                    score += 1
    return score

# Algorithm 1: Fuzzy Logic
def fuzzy_move(board):
    """Uses fuzzy logic to evaluate moves"""
    def fuzzify(score):
        if score <= 0: return 1
        elif score == 1: return 1.5
        elif score == 2: return 2
        elif score == 3: return 2.5
        else: return 3
    
    best_val, best_move, best_char = -1000, (-1, -1), 'S'
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == '':
                for char in ['S', 'O']:
                    board[i][j] = char
                    val = fuzzify(evaluate_board(board))
                    board[i][j] = ''
                    if val > best_val:
                        best_val, best_move, best_char = val, (i, j), char
    return best_move, best_char

# Algorithm 2: A* Search
def astar_move(board):
    """Uses A* search to find best move"""
    pq = []
    moves = [(i, j) for i in range(len(board)) for j in range(len(board[0])) if board[i][j] == '']
    if len(moves) > 25:
        moves = random.sample(moves, 25)
    
    for i, j in moves:
        for char in ['S', 'O']:
            board[i][j] = char
            score = evaluate_board(board)
            heapq.heappush(pq, (-score, (i, j), char))
            board[i][j] = ''
    
    if pq:
        _, best_move, best_char = heapq.heappop(pq)
        return best_move, best_char
    return (-1, -1), 'S'

# Algorithm 3: MiniMax
def minimax_move(board):
    """Uses minimax with alpha-beta pruning"""
    def minimax(board, depth, is_max, alpha, beta):
        if depth == 2 or not any('' in row for row in board):
            return evaluate_board(board)
        
        if is_max:
            best = -1000
            for i in range(len(board)):
                for j in range(len(board[0])):
                    if board[i][j] == '':
                        for char in ['S', 'O']:
                            board[i][j] = char
                            best = max(best, minimax(board, depth + 1, False, alpha, beta))
                            board[i][j] = ''
                            alpha = max(alpha, best)
                            if beta <= alpha:
                                return best
            return best
        else:
            best = 1000
            for i in range(len(board)):
                for j in range(len(board[0])):
                    if board[i][j] == '':
                        for char in ['S', 'O']:
                            board[i][j] = char
                            best = min(best, minimax(board, depth + 1, True, alpha, beta))
                            board[i][j] = ''
                            beta = min(beta, best)
                            if beta <= alpha:
                                return best
            return best
    
    best_val, best_move, best_char = -1000, (-1, -1), 'S'
    cells = [(i, j) for i in range(len(board)) for j in range(len(board[0])) if board[i][j] == '']
    if len(cells) > 15:
        cells = random.sample(cells, 15)
    
    for i, j in cells:
        for char in ['S', 'O']:
            board[i][j] = char
            val = minimax(board, 0, False, -1000, 1000)
            board[i][j] = ''
            if val > best_val:
                best_val, best_move, best_char = val, (i, j), char
    return best_move, best_char



# AGENT 1: Switches algorithm based on game phase
def agent_1_move(board):
    """Phase-based: Fuzzy → A* → MiniMax"""
    empty = sum(1 for row in board for cell in row if cell == '')
    total = len(board) * len(board[0])
    filled_percent = ((total - empty) / total) * 100
    
    if filled_percent < 30:
        print("Agent 1 using: Fuzzy Logic")
        return fuzzy_move(board)
    elif filled_percent < 70:
        print("Agent 1 using: A* Search")
        return astar_move(board)
    else:
        print("Agent 1 using: MiniMax")
        return minimax_move(board)
# AGENT 2: Rotates through algorithms
def agent_2_move(board):
    """Rotation-based: cycles through all 3"""
    empty = sum(1 for row in board for cell in row if cell == '')
    choice = empty % 3
    
    if choice == 0:
        print("Agent 2 using: Fuzzy Logic")
        return fuzzy_move(board)
    elif choice == 1:
        print("Agent 2 using: A* Search")
        return astar_move(board)
    else:
        print("Agent 2 using: MiniMax")
        return minimax_move(board)



# ==================== GAME LOGIC ====================

def check_sos(board, row, col):
    """Check if move creates SOS pattern"""
    triplets = []
    size = len(board)
    
    for i in range(-2, 1):
        # Vertical
        if 0 <= row + i < size - 2 and board[row + i][col] == 'S' and board[row + i + 1][col] == 'O' and board[row + i + 2][col] == 'S':
            triplets.append([(row + i, col), (row + i + 1, col), (row + i + 2, col)])
        # Horizontal
        if 0 <= col + i < size - 2 and board[row][col + i] == 'S' and board[row][col + i + 1] == 'O' and board[row][col + i + 2] == 'S':
            triplets.append([(row, col + i), (row, col + i + 1), (row, col + i + 2)])
        # Diagonal \
        if 0 <= row + i < size - 2 and 0 <= col + i < size - 2 and board[row + i][col + i] == 'S' and board[row + i + 1][col + i + 1] == 'O' and board[row + i + 2][col + i + 2] == 'S':
            triplets.append([(row + i, col + i), (row + i + 1, col + i + 1), (row + i + 2, col + i + 2)])
        # Diagonal /
        if 2 <= row - i < size and 0 <= col + i < size - 2 and board[row - i][col + i] == 'S' and board[row - i - 1][col + i + 1] == 'O' and board[row - i - 2][col + i + 2] == 'S':
            triplets.append([(row - i, col + i), (row - i - 1, col + i + 1), (row - i - 2, col + i + 2)])
    
    positions = [pos for t in triplets for pos in t]
    return len(triplets) > 0, positions, len(triplets)

def update_scoreboard(canvas, name1, name2):
    """Update score display"""
    global player1_score, player2_score, player_turn
    canvas.delete("all")
    canvas.create_image(0, 0, image=canvas.image, anchor="nw")
    color1 = "#FBF6EE" if player_turn[0] == 1 else "black"
    color2 = "#FBF6EE" if player_turn[0] == 2 else "black"
    canvas.create_text(100, 20, text=f"{name1}: {player1_score}", fill=color1, font=("Arial", 12, "bold"))
    canvas.create_text(100, 60, text=f"{name2}: {player2_score}", fill=color2, font=("Arial", 12, "bold"))

def check_game_end(board, canvas):
    """Check if game is over"""
    if all(cell != '' for row in board for cell in row):
        if player1_score > player2_score:
            winner = "Agent 1 "
        elif player2_score > player1_score:
            winner = "Agent 2 "
        else:
            winner = "It's a tie! "
        
        try:
            pygame.mixer.music.load("resources/music/winner.mp3")
            pygame.mixer.music.play()
        except:
            pass
        
        messagebox.showinfo("Game Over", f"{winner}\n\nAgent 1: {player1_score}\nAgent 2: {player2_score}")
        return True
    return False

def ai_move(board, buttons, circle_img, square_img, canvas):
    """Execute AI move"""
    global player_turn, game_paused, player1_score, player2_score
    
    if game_paused or not board_window or not board_window.winfo_exists():
        return
    
    # Get move from appropriate agent
    if player_turn[0] == 1:
        best_move, best_char = agent_1_move(board)
    else:
        best_move, best_char = agent_2_move(board)
    
    if best_move == (-1, -1):
        return
    
    # Make the move
    row, col = best_move
    board[row][col] = best_char
    img = circle_img if best_char == 'S' else square_img
    buttons[row][col].config(image=img)
    
    # Check for SOS
    found, positions, count = check_sos(board, row, col)
    if found:
        for r, c in set(positions):
            buttons[r][c].config(style=f"SOS{player_turn[0]}.TButton")
        if player_turn[0] == 1:
            player1_score += count
        else:
            player2_score += count
        update_scoreboard(canvas, "Agent 1", "Agent 2")
    
    # Check if game ended
    if check_game_end(board, canvas):
        return
    
    # Switch turn if no SOS made
    if not found:
        player_turn[0] = 2 if player_turn[0] == 1 else 1
        update_scoreboard(canvas, "Agent 1", "Agent 2")
    
    # Schedule next move
    board_window.after(move_delay, lambda: ai_move(board, buttons, circle_img, square_img, canvas))

# ==================== MAIN GAME WINDOW ====================

def prompt_ai_selection(root):
    """Start AI vs AI battle"""
    global board_window, board, buttons, player_turn, player1_score, player2_score
    global blank_image, circle_image, square_image, game_paused
    
    # Reset game state
    player1_score = 0
    player2_score = 0
    player_turn = [1]
    game_paused = False
    
    root.withdraw()
    board_window = tk.Toplevel(root)
    board_window.title("AI Battle: Agent 1 vs Agent 2")
    
    # Window setup
    window_width, window_height = 1300, 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    board_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y-33}')
    board_window.resizable(False, False)
    
    # Styles
    style = ttk.Style()
    style.configure("SOS1.TButton", background="green")
    style.configure("SOS2.TButton", background="red")
    
    # Background music
    try:
        pygame.mixer.music.load("resources/music/forest.mp3")
        pygame.mixer.music.play(-1)
    except:
        pass
    
    # Main frame
    main_frame = ttk.Frame(board_window)
    main_frame.place(relx=0.5, rely=0.5, anchor="center")
    
    # Background image
    try:
        bg = Image.open("resources/images/background_medium.png")
        bg_photo = ImageTk.PhotoImage(bg.resize((window_width, window_height), Image.LANCZOS))
        bg_label = tk.Label(main_frame, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except:
        pass
    
    # Board frame
    board_frame = ttk.Frame(main_frame)
    board_frame.grid(row=0, column=0, padx=(20, 10), pady=20)
    
    # Scoreboard
    scoreboard = tk.Canvas(main_frame, width=180, height=80)
    scoreboard.grid(row=0, column=1, padx=(10, 20), pady=0)
    try:
        sb_img = Image.open("resources/images/score_board.png")
        sb_photo = ImageTk.PhotoImage(sb_img.resize((200, 100), Image.LANCZOS))
        scoreboard.create_image(0, 0, image=sb_photo, anchor="nw")
        scoreboard.image = sb_photo
    except:
        pass
    
    # Control buttons
    ctrl_frame = ttk.Frame(main_frame)
    ctrl_frame.grid(row=1, column=1, padx=(10, 20), pady=5)
    
    def toggle_pause():
        global game_paused
        game_paused = not game_paused
        pause_btn.config(text="Resume" if game_paused else "Pause")
        if not game_paused:
            ai_move(board, buttons, circle_image, square_image, scoreboard)
    
    pause_btn = ttk.Button(ctrl_frame, text="Pause", command=toggle_pause, width=15)
    pause_btn.pack(pady=5)
    
    def speed_up():
        global move_delay
        move_delay = max(200, move_delay - 200)
        speed_lbl.config(text=f"Speed: {1000//move_delay}x")
    
    def speed_down():
        global move_delay
        move_delay = min(3000, move_delay + 200)
        speed_lbl.config(text=f"Speed: {1000//move_delay}x")
    
    ttk.Button(ctrl_frame, text="Speed +", command=speed_up, width=15).pack(pady=5)
    ttk.Button(ctrl_frame, text="Speed -", command=speed_down, width=15).pack(pady=5)
    speed_lbl = ttk.Label(ctrl_frame, text="Speed: 1x", font=("Arial", 10, "bold"), background='lightblue', relief="solid", padding=5)
    speed_lbl.pack(pady=10)
    
    update_scoreboard(scoreboard, "Agent 1", "Agent 2")
    
    # Initialize board
    board_size = 7
    board = [['' for _ in range(board_size)] for _ in range(board_size)]
    
    # Load images
    try:
        blank_image = ImageTk.PhotoImage(Image.open("resources/images/blank.jpg").resize((40, 40), Image.LANCZOS))
        circle_image = ImageTk.PhotoImage(Image.open("resources/images/circle.jpg").resize((40, 40), Image.LANCZOS))
        square_image = ImageTk.PhotoImage(Image.open("resources/images/sq.jpg").resize((40, 40), Image.LANCZOS))
    except:
        blank_image = circle_image = square_image = None
    
    # Create board buttons
    buttons = [[None for _ in range(board_size)] for _ in range(board_size)]
    for r in range(board_size):
        for c in range(board_size):
            btn = ttk.Button(board_frame, text='', width=5, state='disabled')
            btn.grid(row=r, column=c, padx=5, pady=5)
            if blank_image:
                btn.config(image=blank_image)
            buttons[r][c] = btn
    
    board_window.protocol("WM_DELETE_WINDOW", lambda: [board_window.destroy(), root.deiconify()])
    
    # Start the battle
    board_window.after(1000, lambda: ai_move(board, buttons, circle_image, square_image, scoreboard))