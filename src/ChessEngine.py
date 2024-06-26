

class GameState():

    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.move_functions = {'p': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves, 
                               'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}

        self.whiteToMove = True
        self.movelog = []
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.en_passant_possible = () # square where en passant is possible
        self.en_passant_possible_log = [self.en_passant_possible]
        self.current_caslting_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_caslting_rights.wks, self.current_caslting_rights.bks, 
                                               self.current_caslting_rights.wqs, self.current_caslting_rights.bqs)]
        
        
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.movelog.append(move)
        self.whiteToMove = not self.whiteToMove

        # update kings location if moves
        if move.piece_moved == 'wK':
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_location = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        # en passant move
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = '--' # capturing the pawn

        # update en passant variable
        if move.piece_moved[1] == 'p' and abs(move.start_row - move.end_row) == 2: # only on 2 square pawn advances
            self.en_passant_possible = ((move.start_row + move.end_row)//2, move.start_col)
        else:
            self.en_passant_possible = ()

        # castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2: # kingside castle
                self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col+1] # moves the rook
                self.board[move.end_row][move.end_col+1] = '--' # erase the old rook
            else: # queenside castle
                self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-2] # moves the rook
                self.board[move.end_row][move.end_col-2] = '--'


        self.en_passant_possible_log.append(self.en_passant_possible)

        # update castling rights - whenever it is a rook or a king move
        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.current_caslting_rights.wks, self.current_caslting_rights.bks, 
                                               self.current_caslting_rights.wqs, self.current_caslting_rights.bqs))
    
    # undo the last move
    def undo_move(self):
        if len(self.movelog) != 0: # need a move to undo 
            move = self.movelog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whiteToMove = not self.whiteToMove # switch turns
            # update kings position
            if move.piece_moved == 'wK':
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_location = (move.start_row, move.start_col)

            # undo en passant
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = '--' # removes the pawn that was added in the wrong square
                self.board[move.start_row][move.end_col] = move.piece_captured # puts the pawn back on the correct square it was captured from
                
            self.en_passant_possible_log.pop()
            self.en_passant_possible = self.en_passant_possible_log[-1]

            # undo castling rights
            self.castle_rights_log.pop() # get rid of new castle rights from move we are undoing
            self.current_caslting_rights = self.castle_rights_log[-1] # set the current castle rights to the last one in the list

            # undo castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2: # kingside
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-1]
                    self.board[move.end_row][move.end_col-1] = '--'
                else: # queenside
                    self.board[move.end_row][move.end_col-2] = self.board[move.end_row][move.end_col+1]
                    self.board[move.end_row][move.end_col+1] = '--'

            self.checkmate = False;
            self.stalemate = False;


    # update castle rights given the move
    def update_castle_rights(self, move):
        if move.piece_moved == 'wK':
            self.current_caslting_rights.wks = False
            self.current_caslting_rights.wqs = False
        elif move.piece_moved == 'bK':
            self.current_caslting_rights.bks = False
            self.current_caslting_rights.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0: # left rook
                    self.current_caslting_rights.wqs = False
                elif move.start_col == 7: # right rook
                    self.current_caslting_rights.wks = False 
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0: # left rook
                    self.current_caslting_rights.bqs = False
                elif move.start_col == 7: # right rook
                    self.current_caslting_rights.bks = False

        # if a rook is captured
        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_col == 0:
                    self.current_caslting_rights.wqs = False
                elif move.end_col == 7:
                    self.current_caslting_rights.wks = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.current_caslting_rights.bqs = False
                elif move.end_col == 7:
                    self.current_caslting_rights.bks = False


    # all moves considering checks
    def get_valid_moves(self):
        temp_en_passant_possible = self.en_passant_possible
        temp_castle_rights = CastleRights(self.current_caslting_rights.wks, self.current_caslting_rights.bks,
                                          self.current_caslting_rights.wqs, self.current_caslting_rights.bqs) # copy the current ccastlign rights
        moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        
        if self.whiteToMove:
           king_row = self.white_king_location[0]
           king_col = self.white_king_location[1]
        else:
            king_row = self.black_king_location[0]
            king_col = self.black_king_location[1]
        if self.in_check:
            if len(self.checks) == 1: # only for one check, able to block or move king
                moves = self.get_all_possible_moves()
                # blocking a check must move a piece into one of hte squares between king ane enemy piece
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col] # enemy piece causing check
                valid_squares = [] # squares that pieces are able to move to
                # knight has to be taken or move king, since other pieces can be blocked but knight moves over pieces
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i) # check[2] and check[3] are the check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col: # once you get to piece end checks
                            break
                    # get rid of any moves that don't block check or move king
                for i in range(len(moves) -1, -1, -1): # go through bakcwards when you are removing form a list as iterating
                    if moves[i].piece_moved[1] != 'K': # move doesn't move king, so it must block or capture
                        if not (moves[i].end_row, moves[i].end_col) in valid_squares: # move does not block check or capture
                            moves.remove(moves[i])
            else: # double check, king has to move
                self.get_king_moves(king_col, king_col, moves)
        else: # not in check so all moves are fine
            moves = self.get_all_possible_moves()
            if self.whiteToMove:
                self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
            else:
                self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)

        if len(moves) == 0:
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False


        self.en_passant_possible = temp_en_passant_possible
        self.current_caslting_rights = temp_castle_rights
        return moves
    
    # determine if current player is under attack
    def in_check(self):
        if self.whiteToMove:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])
        

    # determine if enemy ca attack square r, c
    def square_under_attack(self, r, c):
        self.whiteToMove = not self.whiteToMove  # switch to opponent's turn
        opp_moves = self.get_all_possible_moves()
        self.whiteToMove = not self.whiteToMove # switch back turns
        for move in opp_moves:
            if move.end_row == r and move.end_col == c: # square is under attack
                return True    
        return False
    
    def check_for_pins_and_checks(self):
        pins = [] # squares where the allied piece is and the direction pinned from
        checks = [] # squares where enemy is applying check
        in_check = False
        if self.whiteToMove:
            enemy_color = 'b'
            ally_color = 'w'
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = 'w'
            ally_color = 'b'
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        # check outward from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = () # reset possible pins
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != 'K':
                        if possible_pin == (): # list allied piece could be
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else: # 2nd allied piece, so no pin or check possible in this direction
                            break
                    elif end_piece[0] == enemy_color:
                        enemy_type = end_piece[1]
                        # 5 possibilities here in this complex conditional:
                        # 1) orthogonally away from king and piece is a rook
                        # 2) diagonally away from king and piece is a bishop
                        # 3) 1 square away diagonally from king and piece is a pawn
                        # 4) any direction and piece is a queen
                        # 5) any direction 1 square away and piece is a king (necessary: prevents king move to a sqaure controlled by opposing king)
                        if (0 <= j <= 3 and enemy_type == 'R') or (4 <= j <= 7 and enemy_type == 'B') or (i == 1 and enemy_type == 'p' and ((enemy_color == 'w' and 6 <= j <= 7) or (enemy_color == 'b' and 4 <= j <= 5))) or (enemy_type == 'Q') or ( i == 1 and enemy_type == 'K'):
                            if possible_pin == (): # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else: # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else: # enemy piece not applying check
                            break
                else: # off board
                    break
        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == 'N': # enemy knight attacking king
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))
        return in_check, pins, checks

    # all moves without considering checks
    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):  # number of rows
            for c in range(len(self.board[r])):  # number of columns in given row
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves) # calls appropriate move function on piece type


        return moves


    # get all pawn moves for the pawn located at (row, col) and add to list
    def get_pawn_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove: # white pawn moves
            if self.board[r-1][c] == '--': # 1 square move
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == '--': # 2 square moves
                        moves.append(Move((r, c), (r-2, c), self.board))

            # captures
            if c-1 >= 0: # capture to the left
                if self.board[r-1][c-1][0] == 'b':
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, is_enpassant_move=True))

            if c+1 <= 7: # capture to the right
                if self.board[r-1][c+1][0] == 'b':
                    if not piece_pinned or piece_pinned == (-1, 1):
                        moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, is_enpassant_move=True))

        else: # black pawn moves
            if self.board[r+1][c] == '--': # 1 square move
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == '--': # 2 square moves
                        moves.append(Move((r, c), (r+2, c), self.board))

            # captures
            if c-1 >= 0: # capture to the left
                if self.board[r+1][c-1][0] == 'w':
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, is_enpassant_move=True))
            if c+1 <= 7: # capture to the right
                if self.board[r+1][c+1][0] == 'w':
                    if not piece_pinned or piece_pinned == (1, 1):
                        moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, is_enpassant_move=True))


    # get all rook moves for the pawn located at (row, col) and add to list
    def get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned =True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q': # can't remove queen from pin on the rook moves, only remove it on the bishop moves
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8: # on board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--": # empty space valid
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color: # rival piece valid
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else: # friendly piece invalid
                            break
                    else: # off board
                        break

    # get all knight moves for the pawn located at (row, col) and add to list
    def get_knight_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned =True
                self.pins.remove(self.pins[i])
                break
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        ally_color = "w" if self.whiteToMove else "b"
        for m in knight_moves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0<= end_col < 8:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_color: # not an ally 
                        moves.append(Move((r, c), (end_row, end_col), self.board))

    # get all bishop moves for the pawn located at (row, col) and add to list
    def get_bishop_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned =True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8: # on board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "--": # empty space valid
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color: # rival piece valid
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break
                        else: # friendly piece invalid
                            break
                    else: # off board
                        break

    # get all queen moves for the pawn located at (row, col) and add to list
    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    # get all king moves for the pawn located at (row, col) and add to list
    def get_king_moves(self, r, c, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_color = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_color: # not an ally piece (empty or enemy piece)
                    # place king on end square and check for checks
                    if ally_color == 'w':
                        self.white_king_location = (end_row, end_col)
                    else:
                        self.black_king_location = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    # place king back to original location
                    if ally_color == 'w':
                        self.white_king_location = (r, c)
                    else:
                        self.black_king_location = (r, c)

        


    # generate all valid castle moves for the king at (r, c) and add them to the list of moves
    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return # cannot castle while in check
        if (self.whiteToMove and self.current_caslting_rights.wks) or (not self.whiteToMove and self.current_caslting_rights.bks):
            self.get_kingside_castle_moves(r, c, moves)
        if (self.whiteToMove and self.current_caslting_rights.wqs) or (not self.whiteToMove and self.current_caslting_rights.bqs):
            self.get_queenside_castle_moves(r, c, moves)


    def get_kingside_castle_moves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, is_castle_move=True))


    def get_queenside_castle_moves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, is_castle_move=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


    
class Move():

    # maps keys to values
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}

    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    
    cols_to_files = {v: k for k, v in files_to_cols.items()}



    def __init__(self, start_sq, end_sq, board, is_enpassant_move = False, is_castle_move=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        # pawn promotion
        self.is_pawn_promotion = (self.piece_moved == 'wp' and self.end_row == 0) or (self.piece_moved == 'bp' and self.end_row == 7)

        # en passant
        self.is_enpassant_move = is_enpassant_move
        if self.is_enpassant_move:
            self.piece_captured = "wp" if self.piece_moved == "bp" else "bp"

        # castle move
        self.is_castle_move = is_castle_move
        

        self.move_ID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
        

    # overriding equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_ID == other.move_ID
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
    
