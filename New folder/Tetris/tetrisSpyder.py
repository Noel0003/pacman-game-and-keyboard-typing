import pygame
import cv2
import mediapipe as mp
import random
import numpy as np

# Initialize Pygame
pygame.init()

# Initialize MediaPipe Hand
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)

# Initialize Webcam
cap = cv2.VideoCapture(0)

# Game Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
BLOCK_SIZE = 30
PLAY_WIDTH = 10  # 10 blocks wide
PLAY_HEIGHT = 20  # 20 blocks tall
TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH * BLOCK_SIZE) // 2
TOP_LEFT_Y = SCREEN_HEIGHT - (PLAY_HEIGHT * BLOCK_SIZE) - 50

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
COLORS = [
    (0, 255, 0),  # Green
    (255, 0, 0),  # Red
    (0, 0, 255),  # Blue
    (255, 255, 0),  # Yellow
    (128, 0, 128),  # Purple
    (255, 165, 0),  # Orange
    (0, 255, 255)   # Cyan
]

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]  # Z
]

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = random.choice(COLORS)
        self.rotation = 0

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(PLAY_WIDTH)] for _ in range(PLAY_HEIGHT)]
    for y, x in locked_positions:
        if y >= 0:
            grid[y][x] = locked_positions[(y, x)]
    return grid

def convert_shape_format(piece):
    positions = []
    shape = piece.shape[piece.rotation % len(piece.shape)]
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                positions.append((piece.x + j, piece.y + i))
    return positions

def valid_space(piece, grid):
    accepted_positions = [[(j, i) for j in range(PLAY_WIDTH) if grid[i][j] == BLACK] for i in range(PLAY_HEIGHT)]
    accepted_positions = [j for sub in accepted_positions for j in sub]
    formatted = convert_shape_format(piece)
    
    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False
    return True

def check_lost(positions):
    for pos in positions:
        if pos[1] < 1:
            return True
    return False

def clear_rows(grid, locked):
    inc = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if BLACK not in row:
            inc += 1
            # Remove the row from locked_positions
            for x in range(len(row)):
                try:
                    del locked[(i, x)]
                except:
                    continue
            # Shift everything above this row down
            for y in range(i, 0, -1):
                for x in range(len(grid[y])):
                    if grid[y-1][x] != BLACK:
                        locked[(y, x)] = locked.pop((y-1, x))
    return inc

def draw_grid(surface, grid):
    for y, row in enumerate(grid):
        for x, color in enumerate(row):
            pygame.draw.rect(surface, color, (TOP_LEFT_X + x * BLOCK_SIZE, TOP_LEFT_Y + y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

def draw_window(surface, grid):
    surface.fill(BLACK)
    pygame.draw.rect(surface, WHITE, (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH * BLOCK_SIZE, PLAY_HEIGHT * BLOCK_SIZE), 5)
    draw_grid(surface, grid)
    pygame.display.update()

def get_hand_gesture(frame):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        
        # Simple gesture detection: 
        # - Index up and middle down: Move right
        # - Index down and middle up: Move left
        # - Both down: Move down (faster)
        # - Both up: No movement
        if index_tip.y < middle_tip.y:
            return 'right'
        elif index_tip.y > middle_tip.y:
            return 'left'
        elif index_tip.y > 0.5 and middle_tip.y > 0.5:
            return 'down'
    return 'none'

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Tetris with Hand Gestures')
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27  # seconds per block
    locked_positions = {}
    current_piece = Piece(3, 0, random.choice(SHAPES))
    next_piece = Piece(3, 0, random.choice(SHAPES))
    score = 0
    run = True
    
    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        # Check for hand gestures
        ret, frame = cap.read()
        if not ret:
            continue

        gesture = get_hand_gesture(frame)
        
        if fall_time / 1000 > fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # Handle movement based on gesture
        if gesture == 'right':
            current_piece.x += 1
            if not valid_space(current_piece, grid):
                current_piece.x -= 1
        elif gesture == 'left':
            current_piece.x -= 1
            if not valid_space(current_piece, grid):
                current_piece.x += 1
        elif gesture == 'down':
            fall_speed = 0.1  # Speed up falling when hand is down
        else:  # 'none' or both fingers up
            fall_speed = 0.27

        shape_pos = convert_shape_format(current_piece)

        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = Piece(3, 0, random.choice(SHAPES))
            change_piece = False
            score += clear_rows(grid, locked_positions) * 10

        if check_lost(locked_positions):
            run = False

        draw_window(screen, grid)

        # Display the webcam feed
        cv2.imshow('Gesture Control', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    pygame.quit()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()