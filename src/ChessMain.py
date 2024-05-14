import os
import pygame as p
from ChessEngine import *
from ChessAI import *
from multiprocessing import Process, Queue


os.chdir(os.path.dirname(os.path.abspath(__file__)))

BOARD_WIDTH = BOARD_HEIGHT = 512
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

# load in the images
def load_images():
    pieces = ['wp', 'wR', 'wB', 'wN', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

    
    

def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    move_log_font = p.font.SysFont("Arial", 12, False, False)
    gs = GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False # flag variable when move is made
    animate = False # flag variable for when to animate
    print(gs.board)
    load_images()
    running = True
    sq_selected = () # no square selected, keeps track of last click (row, col)
    player_clicks = [] # keep track of player clicks e.g. [(6,5), (4,4)]
    game_over = False
    player_one = True # if a human is playing white, then this will be true, if AI is playing then false
    player_two = False # same as above, just for black
    ai_thinking = False
    move_finder_process = None
    move_undone = False

    while running:
        human_turn = (gs.whiteToMove and player_one) or (not gs.whiteToMove and player_two)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handling
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # x and y location of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sq_selected == (row, col): # clicked the same square twice
                        sq_selected = ()
                        player_clicks = [] # clear the clicks
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected) # append first and second clicks
                    if len(player_clicks) == 2 and human_turn:  # after 2nd click
                        move = Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.get_chess_notation())
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                sq_selected = () # reset user clicks
                                player_clicks = []
                        if not move_made:
                            player_clicks = [sq_selected]
            # key handling
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # bind to "z" key
                    gs.undo_move()
                    move_made = True
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True
                    
                if e.key == p.K_r: # reset the board when 'r' is pressed
                    gs = GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_over = False
                    if ai_thinking:
                        move_finder_process.terminate()
                        ai_thinking = False
                    move_undone = True


        # AI move finder logic
        if not game_over and not human_turn and not move_undone:
            if not ai_thinking:
                ai_thinking = True
                return_queue = Queue() # used to pass data between threads
                move_finder_process = Process(target=find_best_move, args=(gs, valid_moves, return_queue))
                move_finder_process.start() # call find_best_move(gs, valid_moves, return_queue)
            
            if not move_finder_process.is_alive():
                AI_move = return_queue.get()
                if AI_move is None:
                    AI_move = find_random_move(valid_moves)
                gs.make_move(AI_move)
                move_made = True
                animate = True
                ai_thinking = False

        if move_made:
            if animate:
                animated_move(gs.movelog[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False
            animate = False
            move_undone = False

        draw_game_state(screen, gs, valid_moves, sq_selected)

        if gs.checkmate or gs.stalemate:
            game_over = True
            draw_endgame_text(screen, 'Stalemate' if gs.stalemate else 'Black wins by checkmate' if gs.whiteToMove else 'White wins by checkmate')

        clock.tick(MAX_FPS)
        p.display.flip()

# highlight square selected and moves for the piece selected
def  highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): # sq_selected is a piece that can be moved
            # highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # transparency value -> 0 = transparent, 255 -> opaque
            s.fill(p.Color('green'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col*SQ_SIZE, move.end_row*SQ_SIZE))


def draw_game_state(screen , gs, valid_moves, sq_selected):
    draw_board(screen) # draw squares on the board
    highlight_squares(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board) # layer pieces on top of the board
    

def draw_board(screen):
    global colors
    colors = [p.Color("white"), p.Color("navy")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            


def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


# animating a move
def animated_move(move, screen, board, clock):
    global colors
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    frames_per_square = 5 # frames to move one square
    frame_count = (abs(dR) + abs(dC)) * frames_per_square
    for frame in range(frame_count + 1):
        r, c = ((move.start_row + dR*frame/frame_count, move.start_col + dC*frame/frame_count))
        draw_board(screen)
        draw_pieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        # draw captured piece onto the rectangle
        if move.piece_captured != "--":
            if move.is_enpassant_move:
                en_passant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_col*SQ_SIZE, en_passant_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60) 


def draw_endgame_text(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    text_object = font.render(text, 0, p.Color('Red'))
    text_location = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - text_object.get_width()/2, BOARD_HEIGHT/2 - text_object.get_height()/2)
    screen.blit(text_object, text_location)
    

if __name__ == "__main__":
    main()


