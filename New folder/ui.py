import os
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from tkinter import messagebox
import pygame  # Import pygame for sound playback

# For Windows DPI Awareness
if os.name == 'nt':
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)

# Initialize Pygame Mixer
pygame.mixer.init()

# Load your MP3 file (make sure to provide the correct path to your MP3 file)
CLICK_SOUND_PATH = r"C:\OBB Files\poseTetris-main\New folder\click.ogg"
pygame.mixer.music.load(CLICK_SOUND_PATH)

# Define paths to your projects
PROJECT1_PATH = r"C:\OBB Files\poseTetris-main\New folder"
PROJECT1_MAIN = "pacman.py"
PROJECT2_PATH = r"C:\OBB Files\poseTetris-main\New folder"
PROJECT2_MAIN = "virtual_keyboard.py"  # Update this

def play_click_sound():
    pygame.mixer.music.play()

def run_project(project_path, main_script):
    try:
        os.chdir(project_path)
        result = subprocess.run(["python", main_script], capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"Script execution failed with error: {result.stderr}")
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

def run_project1():
    play_click_sound()  # Play sound on button click
    run_project(PROJECT1_PATH, PROJECT1_MAIN)

def run_project2():
    play_click_sound()  # Play sound on button click
    run_project(PROJECT2_PATH, PROJECT2_MAIN)

def exit_app():
    play_click_sound()  # Play sound on button click
    root.destroy()

# Main window setup
root = tk.Tk()
root.title("Selector")
root.geometry("500x600")
root.configure(bg="#010101")
root.tk.call('tk', 'scaling', 1.9)  # Adjust this scaling factor if needed

# Custom Font (Arial might be clearer on some systems)
default_font = tkfont.nametofont("TkDefaultFont")
default_font.configure(family='Arial', size=12, weight='normal')

# Create a frame for the buttons with the desired background color
options_frame = tk.Frame(root, bg="#1d1a23")
options_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=20)

# Title for the options
title_label = tk.Label(options_frame, text="Options", fg="#d5d5da", bg="#1d1a23", font=("Arial", 25, "bold"))
title_label.pack(pady=(0, 10))  # Add some space below the title

# Button Style Function
def style_button(button):
    style = ttk.Style()
    style.configure("TButton", 
                    background="#1d1a23", 
                    foreground="#000000", 
                    borderwidth=0, 
                    relief="flat", 
                    font=("Arial", 14),
                    padding=10)
    style.map("TButton", 
              background=[('active', '#2a2633')])  # Slightly darker when active for better visibility
    button.configure(style="TButton", width=20)

# Creating and styling buttons using ttk, placed inside options_frame with no vertical space between them
btn_project1 = ttk.Button(options_frame, text="Pacman", command=run_project1)
style_button(btn_project1)
btn_project1.pack(pady=0, fill=tk.X)

btn_project2 = ttk.Button(options_frame, text="Air Keyboard", command=run_project2)
style_button(btn_project2)
btn_project2.pack(pady=0, fill=tk.X)

btn_exit = ttk.Button(options_frame, text="Quit", command=exit_app)
style_button(btn_exit)
btn_exit.pack(pady=0, fill=tk.X)

# Start the GUI event loop
root.mainloop()