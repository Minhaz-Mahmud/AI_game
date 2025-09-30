import tkinter as tk
from tkinter import messagebox
import pygame

# Initialize global variables
tooltip_window = None
board_window = None
buttons = []
player_turn = [1]
board = []
player1 = "Player 1"
player2 = "Player 2"

global player1_score, player2_score
player1_score = 0
player2_score = 0


def update_scoreboard(scoreboard_frame, player1, player2):
    global player1_score, player2_score, player_turn

    if isinstance(scoreboard_frame, tk.Canvas):
        scoreboard_frame.delete("all")  # Clear the canvas
        scoreboard_frame.create_image(0, 0, image=scoreboard_frame.image, anchor="nw")  # Redraw background image

        # Change player names' color based on the turn
        player1_color = "#FBF6EE" if player_turn[0] == 1 else "black"
        player2_color = "#FBF6EE" if player_turn[0] == 2 else "black"

        scoreboard_frame.create_text(100, 20, text=f"{player1}: {player1_score}", fill=player1_color, font=("PlaywriteNO", 12, "bold"))
        scoreboard_frame.create_text(100, 60, text=f"{player2}: {player2_score}", fill=player2_color, font=("PlaywriteNO", 12, "bold"))

def increment_score(player, scoreboard_frame, player1, player2):
    global player1_score, player2_score
    if player == 1:
        player1_score += 1
    elif player == 2:
        player2_score += 1
    update_scoreboard(scoreboard_frame, player1, player2)

def check_sos(board, row, col):
    sos_positions = []
    board_size = 8

    for i in range(-2, 1):
        if (0 <= row + i < board_size - 2 and
            board[row + i][col] == 'S' and
            board[row + i + 1][col] == 'O' and
            board[row + i + 2][col] == 'S'):
            sos_positions.extend([(row + i, col), (row + i + 1, col), (row + i + 2, col)])
        if (0 <= col + i < board_size - 2 and
            board[row][col + i] == 'S' and
            board[row][col + i + 1] == 'O' and
            board[row][col + i + 2] == 'S'):
            sos_positions.extend([(row, col + i), (row, col + i + 1), (row, col + i + 2)])

    for i in range(-2, 1):
        if (0 <= row + i < board_size - 2 and 0 <= col + i < board_size - 2 and
            board[row + i][col + i] == 'S' and
            board[row + i + 1][col + i + 1] == 'O' and
            board[row + i + 2][col + i + 2] == 'S'):
            sos_positions.extend([(row + i, col + i), (row + i + 1, col + i + 1), (row + i + 2, col + i + 2)])
        if (2 <= row - i < board_size and 0 <= col + i < board_size - 2 and
            board[row - i][col + i] == 'S' and
            board[row - i - 1][col + i + 1] == 'O' and
            board[row - i - 2][col + i + 2] == 'S'):
            sos_positions.extend([(row - i, col + i), (row - i - 1, col + i + 1), (row - i - 2, col + i + 2)])

    return len(sos_positions) > 0, sos_positions

def handle_click(event, row, col, board, buttons, circle_image, square_image, player_turn, board_window, root, update_scoreboard, check_winner, check_game_end, scoreboard_frame, player1, player2):
    if event is None or event.num == 1:
        char = 'S'
        image = circle_image
    elif event.num == 3:
        char = 'O'
        image = square_image
    else:
        return

    if board[row][col] == '':
        board[row][col] = char
        print(f"Player {player_turn[0]} placed {char} at ({row}, {col})")
        buttons[row][col].config(image=image)

        # Print the board state after each move
        print_board(board)

        if not check_winner(row, col, char, board, buttons, player_turn, board_window, update_scoreboard, root):
            player_turn[0] = 2 if player_turn[0] == 1 else 1
            update_scoreboard(scoreboard_frame, player1, player2)
        check_game_end(board, scoreboard_frame, player1_score, player2_score, board_window, root, player1, player2)


def check_winner(row, col, char, board, buttons, player_turn, board_window, update_scoreboard, root):
    global player1_score, player2_score

    found_sos, sos_positions = check_sos(board, row, col)
    if found_sos:
        current_player = player_turn[0]
        
        # Change background color of matched SOS buttons
        for pos in sos_positions:
            r, c = pos
            buttons[r][c].config(style=f"SOS{current_player}.TButton")
        
        if current_player == 1:
            player1_score += len(sos_positions) // 3
        else:
            player2_score += len(sos_positions) // 3
        print(f"Player {current_player} completed 'SOS' at positions: {sos_positions}")
        update_scoreboard(root, player1, player2)
        return True
    return False

def check_game_end(board, scoreboard_frame, player1_score, player2_score, board_window, root, player1, player2):
    update_scoreboard(scoreboard_frame, player1, player2)
    if all(cell != '' for row in board for cell in row):
        print(player1_score)
        print(player2_score)
        if player1_score > player2_score:
            winner = player1
            emoji = "🎉🎊"
        elif player2_score > player1_score:
            winner = player2
            emoji = "🏆🥳"
        else:
            winner = "No one, it's a tie!"
            emoji = "😮😅"

        pygame.mixer.music.stop()
        pygame.mixer.music.load("resources/music/winner.mp3")
        pygame.mixer.music.play()

        show_winner_message(winner, emoji)
        
        board_window.destroy()
        root.destroy()

def show_winner_message(winner, emoji):
    messagebox.showinfo("Game Over", f"{winner} wins the game! {emoji}")
    

def disable_all_buttons(buttons):
    for row in buttons:
        for button in row:
            button.config(state=tk.DISABLED)

def enable_all_buttons(buttons):
    for row in buttons:
        for button in row:
            if button["text"] == "":  # Only enable empty buttons
                button.config(state=tk.NORMAL)


def print_board(board):
    for row in range(len(board)):
        for col in range(len(board[row])):
            cell_content = board[row][col]
            if cell_content == '':
                print(f"({row},{col}): Empty", end=' | ')
            else:
                print(f"({row},{col}): {cell_content}", end=' | ')
        print()  # Newline after each row
    print()  # Extra newline for better readability between prints




