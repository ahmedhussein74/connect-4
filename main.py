import sys
import math
import random
import pygame
import numpy as np
from threading import Timer
import time

# Assign some needed variables
ROWS = 6
COLS = 7
AI_TURN = 1
AI_PIECE = 2
COMPUTER_TURN = 0
COMPUTER_PIECE = 1
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Create 2d list, size = ROWS * COLS
def createBoard():
    return np.zeros((ROWS, COLS))

# Assign piece to cell in board
def dropPiece(board, row, col, piece):
    board[row][col] = piece

# Check if the selected col not complete
def isValidLocation(board, col):
    return board[0][col] == 0

# Get the first empty row
def getNextRow(board, col):
    for r in range(ROWS - 1, -1, -1):
        if board[r][col] == 0:
            return r

# check if any player win
def checkWinning(board, piece):
    # horizontal
    for c in range(COLS - 3):
        for r in range(ROWS):
            if (
                board[r][c] == piece  # (0,0)
                and board[r][c + 1] == piece  # (0,1)
                and board[r][c + 2] == piece  # (0,2)
                and board[r][c + 3] == piece  # (0,3)
            ):
                return True
    # vertical
    for c in range(COLS):
        for r in range(ROWS - 3):
            if (
                board[r][c] == piece  # (0,0)
                and board[r + 1][c] == piece  # (1,0)
                and board[r + 2][c] == piece  # (2,0)
                and board[r + 3][c] == piece  # (3,0)
            ):
                return True
    # positive slope
    for c in range(COLS - 3):
        for r in range(3, ROWS):
            if (
                board[r][c] == piece  # (3,3)
                and board[r - 1][c + 1] == piece  # (2,4)
                and board[r - 2][c + 2] == piece  # (1,5)
                and board[r - 3][c + 3] == piece  # (0,6)
            ):
                return True
    # negative slope
    for c in range(3, COLS):
        for r in range(3, ROWS):
            if (
                board[r][c] == piece  # (3,3)
                and board[r - 1][c - 1] == piece  # (2,2)
                and board[r - 2][c - 2] == piece  # (1,1)
                and board[r - 3][c - 3] == piece  # (0,0)
            ):
                return True

# create GUI of the board
def drawBoard(board):
    for c in range(COLS):
        for r in range(ROWS):
            pygame.draw.rect(
                screen,
                BLUE,
                (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE),)
            if board[r][c] == 0:
                pygame.draw.circle(
                    screen,
                    BLACK,
                    (
                        int(c * SQUARESIZE + SQUARESIZE / 2),
                        int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2),
                    ),
                    circleRadius,
                )
            elif board[r][c] == 1:
                pygame.draw.circle(
                    screen,
                    RED,
                    (
                        int(c * SQUARESIZE + SQUARESIZE / 2),
                        int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2),
                    ),
                    circleRadius,
                )
            else:
                pygame.draw.circle(
                    screen,
                    YELLOW,
                    (
                        int(c * SQUARESIZE + SQUARESIZE / 2),
                        int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2),
                    ),
                    circleRadius,
                )
    pygame.display.update()


def evaluateWindow(window, piece):
    opponent_piece = COMPUTER_PIECE
    if piece == COMPUTER_PIECE:
        opponent_piece = AI_PIECE
    score = 0
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2
    if window.count(opponent_piece) == 3 and window.count(0) == 1:
        score -= 4
    return score


def scorePosition(board, piece):
    score = 0
    center_array = [int(i) for i in list(board[:, COLS // 2])]
    center_count = center_array.count(piece)
    score += center_count * 6
    # horizontal
    for r in range(ROWS):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLS - 3):
            window = row_array[c: c + 4]
            score += evaluateWindow(window, piece)
    # vertical
    for c in range(COLS):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROWS - 3):
            window = col_array[r: r + 4]
            score += evaluateWindow(window, piece)
    # positive slope
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            window = [board[r - i][c + i] for i in range(4)]
            score += evaluateWindow(window, piece)
    # negative slope
    for r in range(3, ROWS):
        for c in range(3, COLS):
            window = [board[r - i][c - i] for i in range(4)]
            score += evaluateWindow(window, piece)
    return score


def isTerminalNode(board):
    return (
        checkWinning(board, COMPUTER_PIECE)
        or checkWinning(board, AI_PIECE)
        or len(getValidLocations(board)) == 0
    )


def minimax(board, depth, alpha, beta, maximizing_player):
    validLocations = getValidLocations(board)
    isTerminal = isTerminalNode(board)
    if depth == 0 or isTerminal:
        if isTerminal:
            if checkWinning(board, AI_PIECE):
                return None, 10000000
            elif checkWinning(board, COMPUTER_PIECE):
                return None, -10000000
            else:
                return None, 0
        else:
            return None, scorePosition(board, AI_PIECE)
    if maximizing_player:
        value = -math.inf
        column = random.choice(validLocations)

        for col in validLocations:
            row = getNextRow(board, col)
            b_copy = board.copy()
            dropPiece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(value, alpha)
            if alpha >= beta:
                break
        return column, value

    else:
        value = math.inf
        column = random.choice(validLocations)
        for col in validLocations:
            row = getNextRow(board, col)
            b_copy = board.copy()
            dropPiece(b_copy, row, col, COMPUTER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(value, beta)
            if alpha >= beta:
                break
        return column, value


def computerTurn():
    while True:
        time.sleep(1)
        return random.randint(0, 6)

# get empty locations
def getValidLocations(board):
    validLocations = []
    for column in range(COLS):
        if isValidLocation(board, column):
            validLocations.append(column)
    return validLocations


def endGame():
    global gameOver
    gameOver = True


move = 0
notOver = True
gameOver = False

# Create the board
board = createBoard()

# initial turn is random
turn = random.randint(COMPUTER_TURN, AI_TURN)

# initializing pygame
pygame.init()

# size of one game location
SQUARESIZE = 100

# dimensions for pygame GUI
width = COLS * SQUARESIZE
height = (ROWS + 1) * SQUARESIZE
circleRadius = int(SQUARESIZE/2 - 5)
size = (width, height)
screen = pygame.display.set_mode(size)

# font for win message
myFont = pygame.font.SysFont("monospace", 75)

# draw GUI
drawBoard(board)
pygame.display.update()

while not gameOver:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        pygame.display.update()


    if move == ROWS * COLS:
        print("Draw")
        label = myFont.render("Draw", True, RED)
        screen.blit(label, (40, 10))
        notOver = False
        t = Timer(3.0, endGame)
        t.start()

    elif turn == COMPUTER_TURN:
        col = computerTurn()
        if isValidLocation(board, col):
            row = getNextRow(board, col)
            dropPiece(board, row, col, COMPUTER_PIECE)
            if checkWinning(board, COMPUTER_PIECE):
                print("COMPUTER WINS!")
                label = myFont.render("COMPUTER WINS!", True, RED)
                screen.blit(label, (40, 10))
                notOver = False
                t = Timer(3.0, endGame)
                t.start()
        drawBoard(board)
        move += 1
        turn += 1
        turn = turn % 2

    elif turn == AI_TURN and not gameOver and notOver:
        col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)
        if isValidLocation(board, col):
            pygame.time.wait(500)
            row = getNextRow(board, col)
            dropPiece(board, row, col, AI_PIECE)
            if checkWinning(board, AI_PIECE):
                print("AI WINS!")
                label = myFont.render("AI WINS!", True, YELLOW)
                screen.blit(label, (40, 10))
                notOver = False
                t = Timer(3.0, endGame)
                t.start()
        drawBoard(board)
        move += 1
        turn += 1
        turn = turn % 2
