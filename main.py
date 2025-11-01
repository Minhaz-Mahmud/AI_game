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
    sos_triplets = []
    board_size = 7

    # Check vertical
    for i in range(-2, 1):
        if (0 <= row + i < board_size - 2 and
            board[row + i][col] == 'S' and
            board[row + i + 1][col] == 'O' and
            board[row + i + 2][col] == 'S'):
            sos_triplets.append([(row + i, col), (row + i + 1, col), (row + i + 2, col)])

    # Check horizontal
    for i in range(-2, 1):
        if (0 <= col + i < board_size - 2 and
            board[row][col + i] == 'S' and
            board[row][col + i + 1] == 'O' and
            board[row][col + i + 2] == 'S'):
            sos_triplets.append([(row, col + i), (row, col + i + 1), (row, col + i + 2)])

    # Check diagonal (top-left to bottom-right)
    for i in range(-2, 1):
        if (0 <= row + i < board_size - 2 and 0 <= col + i < board_size - 2 and
            board[row + i][col + i] == 'S' and
            board[row + i + 1][col + i + 1] == 'O' and
            board[row + i + 2][col + i + 2] == 'S'):
            sos_triplets.append([(row + i, col + i), (row + i + 1, col + i + 1), (row + i + 2, col + i + 2)])

    # Check diagonal (top-right to bottom-left)
    for i in range(-2, 1):
        if (2 <= row - i < board_size and 0 <= col + i < board_size - 2 and
            board[row - i][col + i] == 'S' and
            board[row - i - 1][col + i + 1] == 'O' and
            board[row - i - 2][col + i + 2] == 'S'):
            sos_triplets.append([(row - i, col + i), (row - i - 1, col + i + 1), (row - i - 2, col + i + 2)])

    # Collect all positions from triplets for highlighting
    all_positions = []
    for triplet in sos_triplets:
        all_positions.extend(triplet)

    return len(sos_triplets) > 0, all_positions, len(sos_triplets)

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
    #it checks the who have done a score menas wins a point
    global player1_score, player2_score

    found_sos, sos_positions, sos_count = check_sos(board, row, col)
    if found_sos:
        current_player = player_turn[0]
        
        # Remove duplicates and highlight unique positions
        unique_positions = list(set(sos_positions))
        for pos in unique_positions:
            r, c = pos
            buttons[r][c].config(style=f"SOS{current_player}.TButton")
        
        # Increment score by the number of SOS patterns found
        if current_player == 1:
            player1_score += sos_count
        else:
            player2_score += sos_count
        
        print(f"Player {current_player} completed {sos_count} 'SOS' pattern(s) at positions: {sos_positions}")
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
            emoji = ""
        elif player2_score > player1_score:
            winner = player2
            emoji = ""
        else:
            winner = "No one, it's a tie!"
            emoji = ""

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
            try:
                if button and button.winfo_exists():
                    button.state(["disabled"])
            except:
                pass



def enable_all_buttons(buttons):
    for row in buttons:
        for button in row:
            try:
                if button and button.winfo_exists():
                    if button["text"] == "":  # Only enable empty buttons
                        button.state(["!disabled"])
            except:
                pass


def handle_click_ai(event, row, col, board, buttons, circle_image, square_image, player_turn, board_window, root, update_scoreboard, check_winner, check_game_end, scoreboard_frame, player1, player2, ai_make_move=None, best_char=None):
    current_player = player_turn[0]
    
    # Determine character based on event or AI move
    if best_char is not None:  # AI move
        char = best_char
    elif event is not None and hasattr(event, 'num'):  # Player click
        if event.num == 1:
            char = 'S'
        elif event.num == 3:
            char = 'O'
        else:
            return
    else:
        return

    if board[row][col] == '':
        board[row][col] = char
        print(f"Player {current_player} placed {char} at ({row}, {col})")
        
        # Always determine image from what's on the board
        image = circle_image if board[row][col] == 'S' else square_image
        buttons[row][col].config(image=image)

        # Print the board state after each move
        print_board(board)

        # Check for "SOS" and update the score
        if not check_winner(row, col, char, board, buttons, player_turn, board_window, update_scoreboard, root):
            # Switch turn
            player_turn[0] = 2 if player_turn[0] == 1 else 1
            update_scoreboard(scoreboard_frame, player1, player2)
            
            # AI move if it's now AI's turn
            if ai_make_move and player_turn[0] == 2:
                disable_all_buttons(buttons)
                board_window.after(1000, lambda: ai_make_move(board, buttons, circle_image, square_image, player_turn, board_window, root, update_scoreboard, check_winner, check_game_end, scoreboard_frame, player1, player2))
        else:
            # Player/AI made SOS, gets another turn
            update_scoreboard(scoreboard_frame, player1, player2)
            # If it's still AI's turn and they get another move
            if player_turn[0] == 2 and ai_make_move:
                disable_all_buttons(buttons)
                board_window.after(1000, lambda: ai_make_move(board, buttons, circle_image, square_image, player_turn, board_window, root, update_scoreboard, check_winner, check_game_end, scoreboard_frame, player1, player2))
            else:
                # Enable buttons for player's next turn
                enable_all_buttons(buttons)

        check_game_end(board, scoreboard_frame, player1_score, player2_score, board_window, root, player1, player2)




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





# import tkinter as tk
# from tkinter import messagebox
# import pygame

# # Initialize global variables
# tooltip_window = None
# board_window = None
# buttons = []
# player_turn = [1]
# board = []
# player1 = "Player 1"
# player2 = "Player 2"

# global player1_score, player2_score
# player1_score = 0
# player2_score = 0


# def update_scoreboard(scoreboard_frame, player1, player2):
#     global player1_score, player2_score, player_turn

#     if isinstance(scoreboard_frame, tk.Canvas):
#         scoreboard_frame.delete("all")  # Clear the canvas
#         scoreboard_frame.create_image(0, 0, image=scoreboard_frame.image, anchor="nw")  # Redraw background image

#         # Change player names' color based on the turn
#         player1_color = "#FBF6EE" if player_turn[0] == 1 else "black"
#         player2_color = "#FBF6EE" if player_turn[0] == 2 else "black"

#         scoreboard_frame.create_text(100, 20, text=f"{player1}: {player1_score}", fill=player1_color, font=("PlaywriteNO", 12, "bold"))
#         scoreboard_frame.create_text(100, 60, text=f"{player2}: {player2_score}", fill=player2_color, font=("PlaywriteNO", 12, "bold"))

# def increment_score(player, scoreboard_frame, player1, player2):
#     global player1_score, player2_score
#     if player == 1:
#         player1_score += 1
#     elif player == 2:
#         player2_score += 1
#     update_scoreboard(scoreboard_frame, player1, player2)

# def check_sos(board, row, col):
#     sos_positions = []
#     board_size = 7

#     for i in range(-2, 1):
#         if (0 <= row + i < board_size - 2 and
#             board[row + i][col] == 'S' and
#             board[row + i + 1][col] == 'O' and
#             board[row + i + 2][col] == 'S'):
#             sos_positions.extend([(row + i, col), (row + i + 1, col), (row + i + 2, col)])
#         if (0 <= col + i < board_size - 2 and
#             board[row][col + i] == 'S' and
#             board[row][col + i + 1] == 'O' and
#             board[row][col + i + 2] == 'S'):
#             sos_positions.extend([(row, col + i), (row, col + i + 1), (row, col + i + 2)])

#     for i in range(-2, 1):
#         if (0 <= row + i < board_size - 2 and 0 <= col + i < board_size - 2 and
#             board[row + i][col + i] == 'S' and
#             board[row + i + 1][col + i + 1] == 'O' and
#             board[row + i + 2][col + i + 2] == 'S'):
#             sos_positions.extend([(row + i, col + i), (row + i + 1, col + i + 1), (row + i + 2, col + i + 2)])
#         if (2 <= row - i < board_size and 0 <= col + i < board_size - 2 and
#             board[row - i][col + i] == 'S' and
#             board[row - i - 1][col + i + 1] == 'O' and
#             board[row - i - 2][col + i + 2] == 'S'):
#             sos_positions.extend([(row - i, col + i), (row - i - 1, col + i + 1), (row - i - 2, col + i + 2)])

#     return len(sos_positions) > 0, sos_positions

# def handle_click(event, row, col, board, buttons, circle_image, square_image, player_turn, board_window, root, update_scoreboard, check_winner, check_game_end, scoreboard_frame, player1, player2):
#     if event is None or event.num == 1:
#         char = 'S'
#         image = circle_image
#     elif event.num == 3:
#         char = 'O'
#         image = square_image
#     else:
#         return

#     if board[row][col] == '':
#         board[row][col] = char
#         print(f"Player {player_turn[0]} placed {char} at ({row}, {col})")
#         buttons[row][col].config(image=image)

#         # Print the board state after each move
#         print_board(board)

#         if not check_winner(row, col, char, board, buttons, player_turn, board_window, update_scoreboard, root):
#             player_turn[0] = 2 if player_turn[0] == 1 else 1
#             update_scoreboard(scoreboard_frame, player1, player2)
#         check_game_end(board, scoreboard_frame, player1_score, player2_score, board_window, root, player1, player2)


# def check_winner(row, col, char, board, buttons, player_turn, board_window, update_scoreboard, root):
#     global player1_score, player2_score

#     found_sos, sos_positions = check_sos(board, row, col)
#     if found_sos:
#         current_player = player_turn[0]
        
#         # Change background color of matched SOS buttons
#         for pos in sos_positions:
#             r, c = pos
#             buttons[r][c].config(style=f"SOS{current_player}.TButton")
        
#         if current_player == 1:
#             player1_score += len(sos_positions) // 3
#         else:
#             player2_score += len(sos_positions) // 3
#         print(f"Player {current_player} completed 'SOS' at positions: {sos_positions}")
#         update_scoreboard(root, player1, player2)
#         return True
#     return False

# def check_game_end(board, scoreboard_frame, player1_score, player2_score, board_window, root, player1, player2):
#     update_scoreboard(scoreboard_frame, player1, player2)
#     if all(cell != '' for row in board for cell in row):
#         print(player1_score)
#         print(player2_score)
#         if player1_score > player2_score:
#             winner = player1
#             emoji = ""
#         elif player2_score > player1_score:
#             winner = player2
#             emoji = ""
#         else:
#             winner = "No one, it's a tie!"
#             emoji = ""

#         pygame.mixer.music.stop()
#         pygame.mixer.music.load("resources/music/winner.mp3")
#         pygame.mixer.music.play()

#         show_winner_message(winner, emoji)
        
#         board_window.destroy()
#         root.destroy()

# def show_winner_message(winner, emoji):
#     messagebox.showinfo("Game Over", f"{winner} wins the game! {emoji}")
    

# def disable_all_buttons(buttons):
#     for row in buttons:
#         for button in row:
#             button.config(state=tk.DISABLED)



# def enable_all_buttons(buttons):
#     for row in buttons:
#         for button in row:
#             if button["text"] == "":  # Only enable empty buttons
#                 button.config(state=tk.NORMAL)


# def handle_click_ai(event, row, col, board, buttons, circle_image, square_image, player_turn, board_window, root, update_scoreboard, check_winner, check_game_end,  scoreboard_frame, player1, player2, ai_make_move=None, best_char=None):
#     current_player = player_turn[0]
#     if event is None:
#         char = best_char
#         image = circle_image if char == 'S' else square_image
#     elif event.num == 1:
#         char = 'S'
#         image = circle_image
#     elif event.num == 3:
#         char = 'O'
#         image = square_image
#     else:
#         return

#     if board[row][col] == '':
#         board[row][col] = char
#         print(f"{current_player} {char} at ({row}, {col})")
#         buttons[row][col].config(image=image)

        
       

#         # Print the board state after each move
#         print_board(board)

#         # Check for "SOS" and update the score
#         if not check_winner(row, col, char, board, buttons, player_turn, board_window, update_scoreboard, root):
#             player_turn[0] = 2 if player_turn[0] == 1 else 1
#             update_scoreboard(scoreboard_frame, player1, player2)
            
#             # AI move
#             if ai_make_move and player_turn[0] == 2:
#                 disable_all_buttons(buttons)  # Disable buttons during AI's turn
#                 board_window.after(500, lambda: ai_make_move(board, buttons, circle_image, square_image, player_turn, board_window, root, update_scoreboard, check_winner, check_game_end, scoreboard_frame, player1, player2))
#         else:
#             # Allow AI to make another move if it created "SOS"
#             if player_turn[0] == 2 and ai_make_move:
#                 disable_all_buttons(buttons)  # Disable buttons during AI's turn
#                 board_window.after(500, lambda: ai_make_move(board, buttons, circle_image, square_image, player_turn, board_window, root, update_scoreboard, check_winner, check_game_end, scoreboard_frame, player1, player2))

#         check_game_end(board, scoreboard_frame, player1_score, player2_score, board_window, root, player1, player2)




# def print_board(board):
#     for row in range(len(board)):
#         for col in range(len(board[row])):
#             cell_content = board[row][col]
#             if cell_content == '':
#                 print(f"({row},{col}): Empty", end=' | ')
#             else:
#                 print(f"({row},{col}): {cell_content}", end=' | ')
#         print()  # Newline after each row
#     print()  # Extra newline for better readability between prints

# def print_board(board):
#     for row in range(len(board)):
#         for col in range(len(board[row])):
#             cell_content = board[row][col]
#             if cell_content == '':
#                 print(f"({row},{col}): Empty", end=' | ')
#             else:
#                 print(f"({row},{col}): {cell_content}", end=' | ')
#         print()  # Newline after each row
#     print()  # Extra newline for better readability between prints







##################################################################################################################################






# import tkinter as tk
# from tkinter import messagebox
# import pygame

# # Initialize global variables
# tooltip_window = None
# board_window = None
# buttons = []
# player_turn = [1]
# board = []
# player1 = "Player 1"
# player2 = "Player 2"

# global player1_score, player2_score
# player1_score = 0
# player2_score = 0


# def update_scoreboard(scoreboard_frame, player1, player2):
#     global player1_score, player2_score, player_turn

#     if isinstance(scoreboard_frame, tk.Canvas):
#         scoreboard_frame.delete("all")  # Clear the canvas
#         scoreboard_frame.create_image(0, 0, image=scoreboard_frame.image, anchor="nw")  # Redraw background image

#         # Change player names' color based on the turn
#         player1_color = "#FBF6EE" if player_turn[0] == 1 else "black"
#         player2_color = "#FBF6EE" if player_turn[0] == 2 else "black"

#         scoreboard_frame.create_text(100, 20, text=f"{player1}: {player1_score}", fill=player1_color, font=("PlaywriteNO", 12, "bold"))
#         scoreboard_frame.create_text(100, 60, text=f"{player2}: {player2_score}", fill=player2_color, font=("PlaywriteNO", 12, "bold"))

# def increment_score(player, scoreboard_frame, player1, player2):
#     global player1_score, player2_score
#     if player == 1:
#         player1_score += 1
#     elif player == 2:
#         player2_score += 1
#     update_scoreboard(scoreboard_frame, player1, player2)

# def check_sos(board, row, col):
#     sos_positions = []
#     board_size = 7

#     for i in range(-2, 1):
#         if (0 <= row + i < board_size - 2 and
#             board[row + i][col] == 'S' and
#             board[row + i + 1][col] == 'O' and
#             board[row + i + 2][col] == 'S'):
#             sos_positions.extend([(row + i, col), (row + i + 1, col), (row + i + 2, col)])
#         if (0 <= col + i < board_size - 2 and
#             board[row][col + i] == 'S' and
#             board[row][col + i + 1] == 'O' and
#             board[row][col + i + 2] == 'S'):
#             sos_positions.extend([(row, col + i), (row, col + i + 1), (row, col + i + 2)])

#     for i in range(-2, 1):
#         if (0 <= row + i < board_size - 2 and 0 <= col + i < board_size - 2 and
#             board[row + i][col + i] == 'S' and
#             board[row + i + 1][col + i + 1] == 'O' and
#             board[row + i + 2][col + i + 2] == 'S'):
#             sos_positions.extend([(row + i, col + i), (row + i + 1, col + i + 1), (row + i + 2, col + i + 2)])
#         if (2 <= row - i < board_size and 0 <= col + i < board_size - 2 and
#             board[row - i][col + i] == 'S' and
#             board[row - i - 1][col + i + 1] == 'O' and
#             board[row - i - 2][col + i + 2] == 'S'):
#             sos_positions.extend([(row - i, col + i), (row - i - 1, col + i + 1), (row - i - 2, col + i + 2)])

#     return len(sos_positions) > 0, sos_positions

# def handle_click(event, row, col, board, buttons, circle_image, square_image, player_turn, board_window, root, update_scoreboard, check_winner, check_game_end, scoreboard_frame, player1, player2):
#     if event is None or event.num == 1:
#         char = 'S'
#         image = circle_image
#     elif event.num == 3:
#         char = 'O'
#         image = square_image
#     else:
#         return

#     if board[row][col] == '':
#         board[row][col] = char
#         print(f"Player {player_turn[0]} placed {char} at ({row}, {col})")
#         buttons[row][col].config(image=image)

#         # Print the board state after each move
#         print_board(board)

#         if not check_winner(row, col, char, board, buttons, player_turn, board_window, update_scoreboard, root):
#             player_turn[0] = 2 if player_turn[0] == 1 else 1
#             update_scoreboard(scoreboard_frame, player1, player2)
#         check_game_end(board, scoreboard_frame, player1_score, player2_score, board_window, root, player1, player2)


# def check_winner(row, col, char, board, buttons, player_turn, board_window, update_scoreboard, root):
#     global player1_score, player2_score

#     found_sos, sos_positions = check_sos(board, row, col)
#     if found_sos:
#         current_player = player_turn[0]
        
#         # Change background color of matched SOS buttons
#         for pos in sos_positions:
#             r, c = pos
#             buttons[r][c].config(style=f"SOS{current_player}.TButton")
        
#         if current_player == 1:
#             player1_score += len(sos_positions) // 3
#         else:
#             player2_score += len(sos_positions) // 3
#         print(f"Player {current_player} completed 'SOS' at positions: {sos_positions}")
#         update_scoreboard(root, player1, player2)
#         return True
#     return False

# def check_game_end(board, scoreboard_frame, player1_score, player2_score, board_window, root, player1, player2):
#     update_scoreboard(scoreboard_frame, player1, player2)
#     if all(cell != '' for row in board for cell in row):
#         print(player1_score)
#         print(player2_score)
#         if player1_score > player2_score:
#             winner = player1
#             emoji = ""
#         elif player2_score > player1_score:
#             winner = player2
#             emoji = ""
#         else:
#             winner = "No one, it's a tie!"
#             emoji = ""

#         pygame.mixer.music.stop()
#         pygame.mixer.music.load("resources/music/winner.mp3")
#         pygame.mixer.music.play()

#         show_winner_message(winner, emoji)
        
#         board_window.destroy()
#         root.destroy()

# def show_winner_message(winner, emoji):
#     messagebox.showinfo("Game Over", f"{winner} wins the game! {emoji}")
    

# def disable_all_buttons(buttons):
#     for row in buttons:
#         for button in row:
#             try:
#                 if button and button.winfo_exists():
#                     button.state(["disabled"])
#             except:
#                 pass



# def enable_all_buttons(buttons):
#     for row in buttons:
#         for button in row:
#             try:
#                 if button and button.winfo_exists():
#                     if button["text"] == "":  # Only enable empty buttons
#                         button.state(["!disabled"])
#             except:
#                 pass


# def handle_click_ai(event, row, col, board, buttons, circle_image, square_image, player_turn, board_window, root, update_scoreboard, check_winner, check_game_end,  scoreboard_frame, player1, player2, ai_make_move=None, best_char=None):
#     current_player = player_turn[0]
#     if event is None:
#         char = best_char
#         image = circle_image if char == 'S' else square_image
#     elif event.num == 1:
#         char = 'S'
#         image = circle_image
#     elif event.num == 3:
#         char = 'O'
#         image = square_image
#     else:
#         return

#     if board[row][col] == '':
#         board[row][col] = char
#         print(f"{current_player} {char} at ({row}, {col})")
#         buttons[row][col].config(image=image)

#         # Print the board state after each move
#         print_board(board)

#         # Check for "SOS" and update the score
#         if not check_winner(row, col, char, board, buttons, player_turn, board_window, update_scoreboard, root):
#             # Switch turn
#             player_turn[0] = 2 if player_turn[0] == 1 else 1
#             update_scoreboard(scoreboard_frame, player1, player2)
            
#             # AI move
#             if ai_make_move and player_turn[0] == 2:
#                 disable_all_buttons(buttons)  # Disable buttons during AI's turn
#                 board_window.after(1000, lambda: ai_make_move(board, buttons, circle_image, square_image, player_turn, board_window, root, update_scoreboard, check_winner, check_game_end, scoreboard_frame, player1, player2))
#         else:
#             # Player made SOS, gets another turn
#             update_scoreboard(scoreboard_frame, player1, player2)
#             # Allow AI to make another move if it created "SOS"
#             if player_turn[0] == 2 and ai_make_move:
#                 disable_all_buttons(buttons)  # Disable buttons during AI's turn
#                 board_window.after(1000, lambda: ai_make_move(board, buttons, circle_image, square_image, player_turn, board_window, root, update_scoreboard, check_winner, check_game_end, scoreboard_frame, player1, player2))

#         check_game_end(board, scoreboard_frame, player1_score, player2_score, board_window, root, player1, player2)




# def print_board(board):
#     for row in range(len(board)):
#         for col in range(len(board[row])):
#             cell_content = board[row][col]
#             if cell_content == '':
#                 print(f"({row},{col}): Empty", end=' | ')
#             else:
#                 print(f"({row},{col}): {cell_content}", end=' | ')
#         print()  # Newline after each row
#     print()  # Extra newline for better readability between prints

# def print_board(board):
#     for row in range(len(board)):
#         for col in range(len(board[row])):
#             cell_content = board[row][col]
#             if cell_content == '':
#                 print(f"({row},{col}): Empty", end=' | ')
#             else:
#                 print(f"({row},{col}): {cell_content}", end=' | ')
#         print()  # Newline after each row
#     print()  # Extra newline for better readability between prints


