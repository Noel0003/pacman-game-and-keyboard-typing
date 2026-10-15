import pygame
import cv2
import mediapipe as mp

# Initialize Pygame
pygame.init()

# Constants for player movement and screen dimensions
WIDTH = 900         # Width of the game window
HEIGHT = 700        # Height of the game window
player_radius = 20  # Radius of the player
player_speed = 5    # Speed of the player

# Global variables for player position
player_x = WIDTH // 2  # Start in the middle of the screen
player_y = HEIGHT // 2  # Start in the middle of the screen

# Function to move the player based on control input
def move_player(control):
    global player_x, player_y
    if control == 'right' and player_x < WIDTH - player_radius:
        player_x += player_speed
    elif control == 'left' and player_x > player_radius:
        player_x -= player_speed
    elif control == 'up' and player_y > player_radius:
        player_y -= player_speed
    elif control == 'down' and player_y < HEIGHT - player_radius:
        player_y += player_speed

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man Movement Example")

# Create a clock to control the frame rate
clock = pygame.time.Clock()
FPS = 60  # Frames per second

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

# Start video capture
cap = cv2.VideoCapture(0)

# Main game loop
run = True  # Initialize the run variable
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Read a frame from the webcam
    success, img = cap.read()
    if not success:
        continue

    # Convert the image to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    # Initialize control variable
    control = None

    # Check if any hands are detected
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Get the position of the wrist (landmark 0)
            wrist_y = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y
            index_finger_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
            middle_finger_y = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y

            # Determine control based on hand position
            if index_finger_y < wrist_y:  # Hand is up
                control = 'up'
            elif index_finger_y > wrist_y:  # Hand is down
                control = 'down'
            if hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x < hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x:  # Hand is left
                control = 'left'
            elif hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x > hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x:  # Hand is right
                control = 'right'

            # Draw hand landmarks
            mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # Move the player based on the detected control
    if control:
        move_player(control)

    # Clear the screen
    screen.fill((0, 0, 0))

    # Draw the player (example)
    pygame.draw.circle(screen, (255, 255, 0), (player_x, player_y), player_radius)

    # Update the display
    pygame.display.flip()

    # Limit the frame rate
    clock.tick(FPS)

# Release the video capture and quit Pygame
cap.release()
pygame.quit()