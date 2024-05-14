import random



piece_score = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 3



knight_scores = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                 [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                 [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                 [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                 [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                 [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                 [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                 [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishop_scores = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                 [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                 [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                 [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rook_scores = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
               [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
               [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queen_scores = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

white_pawn_scores = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
                    [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
                    [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
                    [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
                    [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
                    [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
                    [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
                    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]

black_pawn_scores = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                     [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
                     [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
                     [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
                     [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
                     [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
                     [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
                     [0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8]]

piece_position_scores = {"N": knight_scores, "R": rook_scores, "Q": queen_scores,
                         "B": bishop_scores, "wp": white_pawn_scores, "bp": black_pawn_scores}


def find_random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves)-1)]


def find_best_move_minmax_norecursion(gs, valid_moves):
    turn_multiplier = 1 if gs.whiteToMove else -1
    opponent_minmax_score = CHECKMATE
    best_player_move = None
    random.shuffle(valid_moves)
    for player_move in valid_moves:
        gs.make_move(player_move)
        opponents_moves = gs.get_valid_moves()
        if gs.stalemate:
            opponent_max_score = STALEMATE
        elif gs.checkmate:
            opponent_max_score = -CHECKMATE
        else:
            opponent_max_score = -CHECKMATE
            for opponents_move in opponents_moves:
                gs.make_move(opponents_move)
                gs.get_valid_moves()
                if gs.checkmate:
                    score = CHECKMATE
                elif gs.stalemate:
                    score = STALEMATE
                else:
                    score = -turn_multiplier * score_material(gs.board)
                if score > opponent_max_score:
                    opponent_max_score = score
                gs.undo_move()
        if opponent_max_score < opponent_minmax_score:
            opponent_minmax_score = opponent_max_score
            best_player_move = player_move
        gs.undo_move()
    return best_player_move

# helper method for first recursive call
def find_best_move(gs, valid_moves, return_queue):
    global next_move, counter
    next_move = None
    random.shuffle(valid_moves)
    counter = 0
    # find_move_minmax(gs, valid_moves, DEPTH, gs.whiteToMove)
    # find_move_negamax(gs, valid_moves, DEPTH, 1 if gs.whiteToMove else -1)
    find_move_negamax_alphabeta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteToMove else -1)
    print(counter)
    return_queue.put(next_move)


def find_move_minmax(gs, valid_moves, depth, whiteToMove):
    global next_move
    if depth == 0:
        return score_material(gs.board)
    
    if whiteToMove:
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_minmax(gs, next_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return max_score

    else:
        min_score = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = find_move_minmax(gs, next_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    next_move = move
            gs.undo_move()
        return min_score
            
def find_move_negamax(gs, valid_moves, depth, turn_multiplier):
    global next_move, counter
    counter += 1
    if depth == 0:
        return turn_multiplier * score_board(gs)
    
    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_negamax(gs, next_moves, depth - 1, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo_move()
    return max_score

def find_move_negamax_alphabeta(gs, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move, counter
    counter += 1
    if depth == 0:
        return turn_multiplier * score_board(gs)
    
    # move ordering: implement this later for efficiency
    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        score = -find_move_negamax_alphabeta(gs, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
                # print(move, score) helps show how the AI is thinking
        gs.undo_move()
        if max_score > alpha: # pruning happens
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


def score_board(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -CHECKMATE # black wins
        else:
            return CHECKMATE # white wins
        
    elif gs.stalemate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                #  score postionally
                piece_position_score = 0
                if square[1] != "K": # no position table needed for king
                    if square[1] == "p": # for pawns
                        piece_position_score = piece_position_scores[square][row][col]
                    else: # for other pieces
                        piece_position_score = piece_position_scores[square[1]][row][col]

                if square[0] == 'w':
                    score += piece_score[square[1]] + piece_position_score
                elif square[0] == 'b':
                    score -= piece_score[square[1]] + piece_position_score

    return score



# score the board based on material
# black tries to make the board as negative as possible, while white tries to make it as positive as possible
def score_material(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += piece_score[square[1]]
            elif square[0] == 'b':
                score -= piece_score[square[1]]

    return score
