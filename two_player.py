import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pygame
from main import update_scoreboard, handle_click, check_winner, check_game_end
from main import player_turn

pygame.mixer.init()

# Initialize global variables
tooltip_window = None
board_window = None
buttons = []
board = []
blank_image = None
circle_image = None
square_image = None
player1 = "Player 1"
player2 = "Player 2"

def open_multiplayer_board(root_window, p1, p2):
    global board_window, player1, player2, board_size, board, buttons, scoreboard_frame
    global blank_image, circle_image, square_image

    player1 = p1
    player2 = p2

    pygame.mixer.music.pause()

    board_window = tk.Toplevel(root_window)
    board_window.title("Two Player Board")

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

    background_image = Image.open("resources/images/background.jpg")
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
            button = ttk.Button(board_frame, text='', width=5, command=lambda r=row, c=col: handle_click(None, r, c, board, buttons, circle_image, square_image, player_turn, board_window, root_window, update_scoreboard, check_winner, check_game_end, scoreboard_frame, player1, player2))
            
            button.grid(row=row, column=col, padx=5, pady=5)
            button.config(image=blank_image)
            button.bind('<Button-1>', lambda event, r=row, c=col: handle_click(event, r, c, board, buttons, circle_image, square_image, player_turn, board_window, root_window, update_scoreboard, check_winner, check_game_end, scoreboard_frame, player1, player2))

            button.bind('<Button-3>', lambda event, r=row, c=col: handle_click(event, r, c, board, buttons, circle_image, square_image, player_turn, board_window, root_window, update_scoreboard, check_winner, check_game_end, scoreboard_frame, player1, player2))
            buttons[row][col] = button

    board_window.protocol("WM_DELETE_WINDOW", root_window.destroy)

if __name__ == "__main__":
    root = tk.Tk()
    root.option_add("*Font", "Digital-7 12")
    open_multiplayer_board(root, "Player 1", "Player 2")
    root.mainloop()


