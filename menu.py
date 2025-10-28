
import tkinter as tk
from tkinter import ttk,font
import pygame
from PIL import Image, ImageTk, ImageSequence
from two_player import open_multiplayer_board
import os
from fuzzy_logic import apply_fuzzy_logic
from a_star import apply_a_star
from mini_max import apply_mini_max_algorithm
from ai_vs_ai import prompt_ai_selection

# Initialize pygame for sound and animation
pygame.init()

# Load sound files
background_sound = pygame.mixer.Sound('resources/music/background_music.mp3')
click_sound = pygame.mixer.Sound('resources/music/button_click.mp3')

# Play background sound in a loop
background_sound.play(loops=-1)

# Function to play button click sound
def play_click_sound():
    click_sound.play()

# Function to stop background sound
def stop_background_sound():
    background_sound.stop()



def prompt_player_names():
    play_click_sound()
    player_name_window = tk.Toplevel(root)
    player_name_window.title("Enter Player Names")

    window_width = 600
    window_height = 400
    screen_width = player_name_window.winfo_screenwidth()
    screen_height = player_name_window.winfo_screenheight()
    center_x = int(screen_width / 2 - window_width / 2)
    center_y = int(screen_height / 2 - window_height / 2)
    player_name_window.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    player_name_window.resizable(False, False)

    tk.Label(player_name_window, text="Player 1 Name:",font=label_font).pack(pady=5)
    player1_entry = ttk.Entry(player_name_window,font=entry_font, width=30)
    player1_entry.pack(pady=5)

    tk.Label(player_name_window, text="Player 2 Name:",font=label_font).pack(pady=5)
    player2_entry = ttk.Entry(player_name_window,font=entry_font, width=30)
    player2_entry.pack(pady=5)

    def start_game():
        play_click_sound()
        player1 = player1_entry.get()
        player2 = player2_entry.get()
        player_name_window.destroy()
        # Stop background music and withdraw root window before opening multiplayer board
        stop_background_sound()
        root.withdraw()
        open_multiplayer_board(root, player1, player2)

    start_button = ttk.Button(player_name_window, text="Start Game", command=start_game)
    start_button.pack(pady=20)

def start_multiplayer():
    prompt_player_names()


def select_difficulty(difficulty):
    play_click_sound()
    stop_background_sound()  # Stop background sound before opening the next GUI
    print(f"Selected difficulty: {difficulty}")
    if difficulty == "Easy":
        root.withdraw()
        apply_fuzzy_logic(root, "HUMAN", "ROBOT")

    elif difficulty == "Medium":
        root.withdraw()
        apply_a_star(root, "HUMAN", "ROBOT")

    elif difficulty == "Hard":
        root.withdraw()
        apply_mini_max_algorithm(root, "HUMAN", "ROBOT")

# Function to animate the background
def animate_background(canvas, image_sequence, image_index):
    canvas.image = image_sequence[image_index]
    canvas.create_image(0, 0, image=canvas.image, anchor=tk.NW)
    root.after(100, animate_background, canvas, image_sequence, (image_index + 1) % len(image_sequence))

# Create main window
root = tk.Tk()
root.title("Game Menu")

label_font = font.Font(family="Arial", size=18, weight="bold")  # Adjust size & weight
entry_font = font.Font(family="Arial", size=16)

# Set the game icon
icon_path = os.path.abspath('resources/images/icon.ico')
if os.path.exists(icon_path):
    try:
        img = ImageTk.PhotoImage(Image.open(icon_path))
        root.tk.call('wm', 'iconphoto', root._w, img)
    except Exception as e:
        print(f"Failed to set icon: {e}")
else:
    print(f"Icon file not found at {icon_path}")

window_width = 900
window_height = 700
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
root.resizable(False, False)


try:
    digital_font = font.Font(family="Bitcount Prop Double Ink Light ", size=36)  # note the space
except Exception as e:
    print(f"Font loading error: {e}")
    digital_font = font.Font(size=32, weight="bold")  # fallback



# Create canvas for background animation
canvas = tk.Canvas(root, width=window_width, height=window_height)
canvas.pack(fill="both", expand=True)

# Load and prepare animated GIF for background
background_img = Image.open('resources/images/background.jpg')
frames = [ImageTk.PhotoImage(frame) for frame in ImageSequence.Iterator(background_img)]

# Start animation
animate_background(canvas, frames, 0)

# Add label and buttons to the canvas
label = ttk.Label(root, text="CIRCLE SQUARE GAME", font=digital_font, background='lightblue', anchor="center",justify="center")
label_window = canvas.create_window(window_width/2, 70, window=label,  width=600, height=80)

# Configure styles for ttk widgets
style = ttk.Style()
style.configure("TButton", font=digital_font, padding=1)  # Reduced padding
style.configure("TMenubutton", font=digital_font, padding=1)  # Reduced padding

# Create buttons for  MULTIPLAYER
button_width = 20  # Reduced button width


multiplayer_button = ttk.Button(root, text="TWO PLAYER", width=button_width, command=start_multiplayer)
multiplayer_button_window = canvas.create_window(window_width/2, 170, window=multiplayer_button)

# Create menu for Single button

single_button = ttk.Button(root, text="SINGLE PLAYER", width=button_width)
single_button_window = canvas.create_window(window_width/2, 270, window=single_button)


single_menu = tk.Menu(root, tearoff=0)
for difficulty in ["Easy", "Medium", "Hard"]:
    single_menu.add_command(label=difficulty, command=lambda d=difficulty: select_difficulty(d))

# In your menu section, add the AI vs AI button after the single player button:
ai_battle_button = ttk.Button(root, text="AI VS AI", width=button_width, command=lambda: prompt_ai_selection(root))
ai_battle_button_window = canvas.create_window(window_width/2, 370, window=ai_battle_button)

def show_single_menu(event):
    play_click_sound()
    single_menu.post(event.x_root, event.y_root)

single_button.bind("<Button-1>", show_single_menu)

# Hide menu when clicking outside
def hide_single_menu(event):
    if not single_menu.winfo_ismapped():
        return
    if event.widget is not single_button:
        single_menu.unpost()

root.bind("<Button-1>", hide_single_menu)


# Start the Tkinter main loop
root.mainloop()
