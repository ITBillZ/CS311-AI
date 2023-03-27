import numpy as np
from numpy import uint64 as u64


BOARD_SIZE = 8

DIRS = set([(-1, 0), (-1, 1), (0, 1), (1, 1),
            (1, 0), (1, -1), (0, -1), (-1, -1)])

# move format
# (row, col, state)
MOVE_PASS = -1
MOVE_NONE = -2  # 针对开局情况

INIT_BOARD = np.array([[0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  1, -1,  0,  0,  0],
                      [0,  0,  0, -1,  1,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0],
                      [0,  0,  0,  0,  0,  0,  0,  0]])

class Game:
    BLACK = -1
    WHITE = 1
    EMPTY = 0

    mask = (
        u64(0xffff_ffff_ffff_ffff), # up
        u64(0xffff_ffff_ffff_ffff), # down
        u64(0xfefe_fefe_fefe_fefe), # left
        u64(0x7f7f_7f7f_7f7f_7f7f), # right
        u64(0xfefe_fefe_fefe_fe00), # left-up
        u64(0x007f_7f7f_7f7f_7f7f), # right-down
        u64(0x00fe_fefe_fefe_fefe), # left-down
        u64(0x7f7f_7f7f_7f7f_7f00), # right-up
    )

    steps = [
        u64(8),
        u64(1),
        u64(9),
        u64(7)
    ]

    mask_zero = u64(0)
    mask_one = u64(1)


    def __init__(self, board):
        self.bin_board = Game.get_bin_board(board)  # (black_bin_board, white_bin_board)
    
    @staticmethod
    def get_bin_board(board):
        s = list('0' * 64)
        for p in np.argwhere(board == -1):
            s[p[0] * 8 + p[1]] = '1'
        black_bin_board = u64(int(''.join(s), 2))

        s = list('0' * 64)
        for p in np.argwhere(board == 1):
            s[p[0] * 8 + p[1]] = '1'
        white_bin_board = u64(int(''.join(s), 2))
        return (black_bin_board, white_bin_board)
    

    def get_legal_moves(self, next_player):
        if next_player == Game.BLACK:
            my_board, opposite_board = self.bin_board
        else:
            my_board, opposite_board = self.bin_board[1], self.bin_board[0]
        
        empty = ~(my_board | opposite_board)
        legal_moves = Game.mask_zero

        for i in range(4):
            mask1, mask2 = Game.mask[2 * i], Game.mask[2 * i + 1]
            mask_op1, mask_op2 = mask1 & opposite_board, mask2 & opposite_board
            step = Game.steps[i]

            tmp = (my_board << step) & mask_op1
            
            tmp |= (tmp << step) & mask_op1
            tmp |= (tmp << step) & mask_op1
            tmp |= (tmp << step) & mask_op1
            tmp |= (tmp << step) & mask_op1
            tmp |= (tmp << step) & mask_op1

            legal_moves |= (tmp << step) & mask1 & empty
            ############################
            tmp = (my_board >> step) & mask_op2
            
            tmp |= (tmp >> step) & mask_op2
            tmp |= (tmp >> step) & mask_op2
            tmp |= (tmp >> step) & mask_op2
            tmp |= (tmp >> step) & mask_op2
            tmp |= (tmp >> step) & mask_op2

            legal_moves |= (tmp >> step) & mask2 & empty

        return legal_moves
    
    
    def apply_move(self, next_player, board_idx):
        if next_player == Game.BLACK:
            my_board, opposite_board = self.bin_board
        else:
            my_board, opposite_board = self.bin_board[1], self.bin_board[0]

        captured_board = Game.mask_zero
        new_board = Game.mask_one << u64(board_idx)
        my_board ^= new_board

        for i in range(4):
            mask1, mask2 = Game.mask[2 * i], Game.mask[2 * i + 1]
            mask_op1, mask_op2 = mask1 & opposite_board, mask2 & opposite_board
            step = Game.steps[i]

            tmp = (new_board << step) & mask_op1
            
            tmp |= (tmp << step) & mask_op1
            tmp |= (tmp << step) & mask_op1
            tmp |= (tmp << step) & mask_op1
            tmp |= (tmp << step) & mask_op1
            tmp |= (tmp << step) & mask_op1 

            captured_board |= tmp if ((tmp << step) & mask1 & my_board) else Game.mask_zero
            ############################
            tmp = (new_board >> step) & mask_op2
            
            tmp |= (tmp >> step) & mask_op2
            tmp |= (tmp >> step) & mask_op2
            tmp |= (tmp >> step) & mask_op2
            tmp |= (tmp >> step) & mask_op2
            tmp |= (tmp >> step) & mask_op2

            captured_board |= tmp if ((tmp >> step) & mask2 & my_board) else Game.mask_zero
        
        # change my_board and opposite_board
        my_board ^= captured_board
        opposite_board ^= captured_board

        return my_board, opposite_board
    
    
    @staticmethod
    def print_2d_board(bin_board):
        board = np.array([int(s) for s in list('{:064b}'.format(bin_board))]).reshape(8, 8)
        print(board)

    @staticmethod
    def popcount(x):
        n = 0
        mask_one = Game.mask_one
        while x:
            x &= x - mask_one
            n += 1
        return n


class GameState:
    def __init__(self, board, next_player, prev_state=None, last_move=(-2, -2)):
        self.board = board  # nparray
        self.next_player = next_player

        self.prev_state = prev_state
        self.last_move = last_move

        self.winner = None
        self.over = None

    def apply_move(self, move):
        """执行落子动作，返回新的GameState对象"""
        if move[0] != MOVE_PASS:
            next_board = np.copy(self.board)
            reverse = np.array(self.get_reverse(move))
            next_board[reverse[:, 0], reverse[:, 1]] = self.next_player
        else:
            next_board = self.board

        return Game(next_board, -self.next_player, self, move)

    @classmethod
    def new_game(cls):
        return Game(INIT_BOARD, BLACK, None)

    def is_valid_move(self, move):
        if self.over:
            return False

        # if len(move) == 3 and move[2] == MOVE_PASS:
        #     return True

        i, j = move

        if self.is_on_grid(i, j) and self.board[i, j] == EMPTY:
            for dx, dy in DIRS:
                op_cnt = 0
                x, y = i + dx, j + dy

                while self.is_on_grid(x, y):
                    if self.board[x, y] == -self.next_player:
                        op_cnt += 1
                        x += dx
                        y += dy
                    elif self.board[x, y] == self.next_player and op_cnt > 0:
                        return True

                    else:
                        break
        return False

    def get_reverse(self, move):
        if self.over or move[0] == MOVE_PASS:
            return []
        

        reverse = []
        i, j = move

        if self.is_on_grid(i, j) and self.board[i, j] == EMPTY:
            for dx, dy in DIRS:
                op_cnt = 0
                x, y = i + dx, j + dy

                while self.is_on_grid(x, y):
                    if self.board[x, y] == -self.next_player:
                        op_cnt += 1
                        x += dx
                        y += dy
                    elif self.board[x, y] == self.next_player and op_cnt > 0:
                        while op_cnt > 0:
                            x -= dx
                            y -= dy
                            reverse.append((x, y))
                            op_cnt -= 1
                        break

                    else:
                        break

        if len(reverse) > 0:
            reverse.append((i, j))  # 自己将要下的位置
        return reverse

    def is_over(self):
        if self.over is not None:
            return self.over

        if self.last_move[0] != MOVE_PASS:
            return False
        second_last_move = self.prev_state.last_move
        if second_last_move[0] != MOVE_PASS:
            return False
        
        self.winner = self.get_winner()
        return True

    def is_on_grid(self, i, j):
        return 0 <= i < BOARD_SIZE and 0 <= j < BOARD_SIZE

    def legal_moves(self):
        moves = []
        empty_points = np.argwhere(self.board == 0)
        # empty_points = self.board.argwhere(self.board == 0)
        for p in empty_points:
            if self.is_valid_move(p):
                moves.append(p)

        # ! 当没有位置可以下的时候，加入跳过
        if (len(moves) == 0):
            moves = [(-1, -1)]

        return moves

    def get_winner(self):
        # if not self.is_over():
        #     return None
        
        num_black = (self.board == BLACK).sum()
        num_white = (self.board == WHITE).sum()

        if num_black < num_white:
            return BLACK
        elif num_white < num_black:
            return WHITE
        else:
            # draw
            return 0



