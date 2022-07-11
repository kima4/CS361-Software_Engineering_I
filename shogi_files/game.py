from shogi_files.pieces import *
from copy import deepcopy
import os


class Game:
    _width = 9
    _height = 9
    _default = 'l.n.s.g.k.g.s.n.l..r......b..p.p.p.p.p.p.p.p.p' \
               '............................' \
               'P.P.P.P.P.P.P.P.P..B......R..L.N.S.G.K.G.S.N.L||'

    _save_location = 'shogi_files/saves'

    def __init__(self):

        # True is player 1, False is player 2
        self._turn = True

        self._finished = False

        # board of determined size, plus extra space to divert bad inputs
        self._board = [None] * (self._width * self._height + 1)

        # captured pieces
        self._p1_jail = []
        self._p2_jail = []

        # set up pieces in beginning positions
        self.set_up_board()


    def get_turn(self):
        return self._turn

    def switch_turn(self):
        self._turn = not self._turn

    def is_finished(self):
        return self._finished

    def undo_checkmate(self):
        self._finished = False

    def get_board_dims(self):
        return self._width, self._height

    def get_p1_jail(self):
        return self._p1_jail

    def get_p2_jail(self):
        return self._p2_jail

    def __str__(self):
        return self.board_to_strings()


    def is_legal_game(self, piece_string=None):
        """
        determines if a save file contains the correct number of each piece as well as a king for each player on the board
        :param piece_string: save file format string
        :return: True if the file string contains a valid piece distribution
        """
        if piece_string is None:
            piece_string = self.game_to_strings() + '|1'

        kings = [p for p in piece_string.split('|')[0] if p.lower() == 'k']
        if not len(kings) == 2 or 'k' not in kings or 'K' not in kings:
            return False

        if not ('|1' in piece_string or '|2' in piece_string):
            return False

        piece_string = piece_string[:-2]

        comparison = self._default.replace('.', '').replace('|', '').lower()
        piece_string = piece_string.replace('.', '').replace('|', '').replace('+', '').lower()

        for p in piece_string:
            if p not in comparison:
                return False
            comparison = comparison.replace(p, '', 1)

        if comparison:
            return False
        return True


    def board_to_strings(self):
        """
        returns string to display board state to console
        :return: string representation of board state
        """
        board_strings = ''
        for col in range(self._width):
            board_strings += '   ' + str(self._width - col) + '  '
        board_strings += '\n'
        board_strings += ' -----' * self._width
        board_strings += '\n'
        for i in range(len(self._board) - 1):
            board_strings += '|  '
            if i % self._width == 0 and i != 0:
                board_strings += str(i // self._width)
                board_strings += '\n'
                board_strings += ' -----' * self._width
                board_strings += '\n|  '
            if self._board[i] is None:
                board_strings += '   '
            else:
                board_strings += self._board[i].get_sym().ljust(3)
        board_strings += '|  ' + str(self._height) + '\n'
        board_strings += ' -----' * self._width
        return board_strings


    def set_up_board(self, set_up=None):
        """
        sets up the board with pieces in specified state, default is starting positions
        :param set_up: set up for game if given
        :return: True if game set up is successful
        """
        piece_dict = {'k': King,
                      'r': Rook,
                      'b': Bishop,
                      'g': Gold,
                      's': Silver,
                      'n': Knight,
                      'l': Lance,
                      'p': Pawn}

        if set_up is None:
            set_up = self._default + '|1'

        if not self.is_legal_game(set_up):
            return False

        set_up = set_up.split('|')
        board = set_up[0].split('.')

        if len(board) > 81:
            return False

        self._board = [None] * (self._width * self._height + 1)
        self._p1_jail = []
        self._p2_jail = []

        for i, piece in enumerate(board):
            if piece != '':
                self._board[i] = piece_dict[piece[0].lower()](piece[0].isupper(), self.itos(i))
                if '+' in piece:
                    self._board[i].promote_piece()

        p1_j = set_up[1].split('.')
        for j, piece in enumerate(p1_j):
            if piece != '':
                self._p1_jail.append(piece_dict[piece[0].lower()](True, (0, 0)))

        p2_j = set_up[2].split('.')
        for k, piece in enumerate(p2_j):
            if piece != '':
                self._p2_jail.append(piece_dict[piece[0].lower()](False, (0, 0)))

        self._turn = set_up[3] == '1'

        return True


    def game_to_strings(self):
        """
        converts game information into a string
        :return: string containing board pieces and jail pieces deliminated by a period, with board
                 information and the two jails information separated by |
        """
        board = self.board_to_strings()
        board = board.replace(' |', '.')
        board = board.replace(' ', '').replace('-', '').replace('\n', '').replace('|', '')
        board = ''.join([i for i in board if not i.isdigit()])

        p1_j = ''
        for piece in self._p1_jail:
            p1_j += piece.get_sym() + '.'
        p2_j = ''
        for piece in self._p2_jail:
            p2_j += piece.get_sym() + '.'

        return board[:-1] + '|' + p1_j + '|' + p2_j


    def save_game(self):
        """
        saves game information including player turn in a file that it creates
        :return: int for the save file number
        """
        if not os.path.isdir(self._save_location):
            os.mkdir(self._save_location)

        save_num = 1
        while os.path.isfile(self._save_location + '/shogi_save' + str(save_num) + '.txt'):
            save_num += 1

        if self._turn:
            turn = '1'
        else:
            turn = '2'

        save_str = self.game_to_strings() + '|' + turn

        f = open(self._save_location + '/shogi_save' + str(save_num) + '.txt', 'w')
        f.write(save_str)
        f.close()
        return save_num


    def load_game(self, save_file_path):
        """
        loads game information from a file
        :param save_file_path: file path containing game information string
        :return: True if game set up is successful
        """
        if not os.path.isdir(self._save_location):
            return False
        if not os.path.isfile(save_file_path):
            return False

        permitted_chars = '.krbgsnlp|+12'
        f = open(save_file_path, 'r')
        save_file = f.read()
        f.close()

        if [i for i in save_file.lower() if i not in permitted_chars]:
            return False

        return self.set_up_board(save_file)


    def stoi(self, space):
        """
        stoi = space to index
        converts a tuple representing a space on the board to the index representing that space
        :param space: tuple containing board location in format: column, row
        :return: int corresponding to the index number representing the space
        """
        if len(space) != 2:
            return -1
        col, row = space
        index = self._width - col + (row - 1) * self._height
        if len(self._board) < index:
            return -1
        return index


    def itos(self, index):
        """
        itos = index to space
        reverses stoi()
        :param index: int corresponding to the index number representing the space
        :return: tuple containing board location in format: column, row
        """
        row = index // self._width + 1
        col = self._width - (index % 9)
        return col, row


    def get_piece_on(self, space):
        """
        gets the piece on a given space
        :param space: tuple containing board location in format: column, row
        :return: Piece object on the space if possible
        """
        col, row = space
        if not self.on_board(space) and not self.in_jail(space):
            return None
        try:
            if col < 0:
                if row < self._height / 2:
                    return self._p2_jail[(row - 1) * 5 - (col + 1)]
                return self._p1_jail[(self._height - row) * 5 - (col + 1)]
            return self._board[self.stoi(space)]
        except IndexError:
            return None


    def get_board_pieces(self):
        """
        gets all pieces on the board
        :return: list of Piece objects on the board
        """
        return [piece for piece in self._board if piece is not None]


    def get_player_team(self, player):
        """
        gets all pieces on the board for the specified player
        :param player: True for player 1, False for player 2
        :return: list of Piece objects on the board belonging to the specified player
        """
        pieces = self.get_board_pieces()
        return [piece for piece in pieces if piece.get_player() == player]


    def get_player_king(self, player):
        """
        gets the king piece of the specified player
        :param player: True for player 1, False for player 2
        :return: King object belonging to the specified player
        """
        team = self.get_player_team(player)
        for piece in team:
            if 'king' in piece.get_name():
                return piece


    def on_board(self, space):
        """
        determines if a given space is actually on the playing board
        :param space: tuple containing board location in format: column, row
        :return: True if on board, False if not
        """
        col, row = space
        if not 1 <= col <= self._width:
            return False
        if not 1 <= row <= self._height:
            return False
        return True


    def in_jail(self, space):
        """
        determines if a given space is in the jail of one of the players
        :param space: tuple containing board location in format: column, row
        :return: True if in a jail, False if not
        """
        col, row = space
        if not -5 <= col <= -1:
            return False
        if not 6 <= row <= self._height and not 1 <= row <= 4:
            return False
        return True


    def pseudo_possible_moves(self, piece):
        """
        finds spaces a piece can move from its initial position
        does not consider putting self in check by moving a piece blocking an attack
        :param piece: Piece object to be moved
        :return: list of tuples representing spaces on the board
        """
        move_list = []

        piece_x, piece_y = piece.get_space()
        if piece_x == 0 or piece_y == 0:
            return self.possible_drops(piece)

        directions = piece.get_dirs()

        for dir_set in directions:
            for x, y in dir_set[0]:
                pos_x = piece_x + x
                pos_y = piece_y + y
                dist_limit = dir_set[1]

                while self.on_board((pos_x, pos_y)) and dist_limit != 0:
                    dist_limit -= 1
                    piece_on_space = self.get_piece_on((pos_x, pos_y))

                    if piece_on_space is None:
                        move_list.append(tuple([pos_x, pos_y]))
                    elif piece_on_space.get_player() == piece.get_player():
                        dist_limit = 0
                    else:
                        dist_limit = 0
                        move_list.append(tuple([pos_x, pos_y]))

                    pos_x += x
                    pos_y += y

        return move_list


    def is_in_check(self, player):
        """
        determines if a given player is in check
        :param player: True for player 1, False for player 2
        :return: True if the given player is in check, False otherwise
        """
        pieces = self.get_player_team(not player)
        space = self.get_player_king(player).get_space()

        for piece in pieces:
            if space in self.pseudo_possible_moves(piece):
                return True

        return False


    def possible_moves(self, piece):
        """
        finds spaces a piece can move from its initial position
        forbids putting self in check by moving a piece blocking an attack
        :param piece: Piece object to be moved
        :return: list of tuples representing spaces on the board
        """
        pseudo_move_list = self.pseudo_possible_moves(piece)
        move_list = []

        for move in pseudo_move_list:
            tmp = deepcopy(self)
            if piece.get_space() == (0, 0):
                if piece.get_player():
                    tmp.move_piece(tmp._p1_jail[self._p1_jail.index(piece)], move)
                else:
                    tmp.move_piece(tmp._p2_jail[self._p2_jail.index(piece)], move)
            else:
                tmp.move_from_space(piece.get_space(), move)
            if not tmp.is_in_check(piece.get_player()):
                move_list.append(move)

        return move_list


    def pieces_stuck(self, player):
        """
        determines if a player cannot escape check by moving pieces already on the board
        :param player: True for player 1, False for player 2
        :return: True if king of specified player is stuck
        """
        for piece in self.get_player_team(player):
            if self.possible_moves(piece):
                return False

        return True


    def is_in_checkmate(self, player):
        """
        determines if a player is in checkmate
        :param player: True for player 1, False for player 2
        :return: True if player is in checkmate
        """
        if not self.is_in_check(player):
            return False

        if (player and self._p1_jail) or (not player and self._p2_jail):
            player_king = self.get_player_king(player)
            king_col, king_row = player_king.get_space()
            open_adj = []
            for x in range(-1, 2):
                for y in range(-1, 2):
                    space = (king_col + x, king_row + y)
                    if self.get_piece_on(space) is None:
                        open_adj.append(space)

            for space in open_adj:
                tmp = deepcopy(self)
                tmp_piece = Pawn(player, (10, 10))
                tmp.move_piece(tmp_piece, space)
                if not tmp.is_in_check(player):
                    return False


        if self.pieces_stuck(player):
            self._finished = True
            return True
        return False


    def move_piece(self, piece, destination):
        """
        used to move a given piece to a destination space
        :param piece: Piece object
        :param destination: tuple containing piece destination location in format: column, row
        :return: None
        """
        origin = piece.get_space()
        self.make_move(piece, origin, destination)


    def move_from_space(self, origin, destination):
        """
        used to move a piece on a given space to a destination space
        :param origin: tuple containing piece origin location in format: column, row
        :param destination: tuple containing piece destination location in format: column, row
        :return: None
        """
        piece = self.get_piece_on(origin)
        self.make_move(piece, origin, destination)


    def make_move(self, piece, origin, destination):
        """
        moves a piece from an initial position to its destination
        :param piece: Piece object to be moved
        :param origin: tuple containing piece origin location in format: column, row
        :param destination: tuple containing piece destination location in format: column, row
        :return: None
        """
        taken_piece = self.get_piece_on(destination)
        if taken_piece:
            taken_piece.got_captured()
            if piece.get_player():
                self._p1_jail.append(taken_piece)
            else:
                self._p2_jail.append(taken_piece)

        if origin == (0, 0):
            if piece.get_player():
                self._p1_jail.remove(piece)
            else:
                self._p2_jail.remove(piece)
        else:
            self._board[self.stoi(origin)] = None
        piece.set_space(destination)
        self._board[self.stoi(destination)] = piece


    def in_promotion_zone(self, space, player):
        """
        determines if a space on the board in in the promotion zone for a given player
        :param space: tuple containing board location in format: column, row
        :param player: True for player 1, False for player 2
        :return: True if space in in player promotion zone
        """
        col, row = space
        if not (1 <= col <= self._width):
            return False
        if player:
            if not (1 <= row <= 3):
                return False
        else:
            if not ((self._height - 2) <= row <= self._height):
                return False
        return True


    def eligible_for_promotion(self, piece, origin):
        """
        determines if a piece is eligible for promotion
        :param piece: Piece object
        :param origin: tuple containing board location from where the piece moved in format: column, row
        :return: True if piece is eligible for promotion, False otherwise
        """
        if piece.is_promoted():
            return False
        if origin == (0, 0):
            return False

        if self.in_promotion_zone(piece.get_space(), piece.get_player()):
            return True
        if self.in_promotion_zone(origin, piece.get_player()):
            return True

        return False


    def pseudo_possible_drops(self, piece):
        """
        finds spaces a piece can be dispatched to
        does not consider extra pawn drop rules
        :param piece: Piece object to be dropped
        :return: list of spaces the piece can be dropped
        """
        drop_list = []

        rows = list(range(1, self._height + 1))

        rows = [r for r in rows if r not in piece.get_forced_rows()]

        for col in range(self._width):
            for row in rows:
                piece = self.get_piece_on((col + 1, row))
                if piece is None:
                    drop_list.append(tuple((col + 1, row)))

        return drop_list


    def possible_drops(self, piece):
        """
        finds spaces a piece can be dispatched to
        considers extra pawn rules
        :param piece: Piece object to be dropped
        :return: list of spaces the piece can be dropped
        """
        drop_list = self.pseudo_possible_drops(piece)

        if 'pawn' in piece.get_name():
            pawn_forbidden = []

            player = piece.get_player()
            player_pieces = self.get_player_team(player)
            for p in player_pieces:
                if 'pawn' in p.get_name() and not p.is_promoted():
                    col = p.get_space()[0]
                    for row in range(self._height):
                        pawn_forbidden.append(tuple((col, row + 1)))

            enemy_king = self.get_player_king(not player)
            king_col, king_row = enemy_king.get_space()
            if player:
                check_space = king_col, king_row + 1
            else:
                check_space = king_col, king_row - 1

            if self.get_piece_on(check_space) is None:
                tmp = deepcopy(self)
                if piece.get_player():
                    tmp.move_piece(tmp._p1_jail[self._p1_jail.index(piece)], check_space)
                else:
                    tmp.move_piece(tmp._p2_jail[self._p2_jail.index(piece)], check_space)
                is_checkmated = tmp.pieces_stuck(not player)
                if is_checkmated:
                    pawn_forbidden.append(tuple(check_space))

            drop_list = [drop for drop in drop_list if drop not in pawn_forbidden]

        return drop_list


def main():
    pass


if __name__ == '__main__':
    main()