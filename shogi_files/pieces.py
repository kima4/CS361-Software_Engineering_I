

class Piece:

    _diagonals = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    _cardinals = [(-1, 0), (0, -1), (0, 1), (1, 0)]

    def __init__(self, player, space):

        # True is player 1, False is player 2
        self._player = player

        # tuple containing piece location in format: column, row
        self._space = space

        # False is not promoted, True is promoted
        self._promoted = False

        # True to alert player whenever piece can promote, False to stop alerts
        self._alert_for_promotion = not self.is_promoted()

        # list of rows in which the piece is forced to promote
        self._forced_promotion = [None]
        self.set_forced_rows()


    def get_player(self):
        return self._player


    def get_space(self):
        return self._space


    def set_space(self, space):
        self._space = space


    def is_promoted(self):
        return self._promoted


    def promote_piece(self):
        self._promoted = True


    def give_alert(self):
        if self._promoted:
            return False
        return self._alert_for_promotion


    def future_alerts(self, wants_alert):
        self._alert_for_promotion = wants_alert


    def get_forced_rows(self):
        return self._forced_promotion


    def set_forced_rows(self):
        pass


    def get_name(self):
        return 'Error: undesignated piece on ' + ', '.join(self._space)


    def get_piece_name(self, name):
        """
        returns the name of the piece
        :param name: string of piece type
        :return: string with player, promotion status, and piece type
        """
        if self._promoted:
            if not ('king' in name or 'gold' in name):
                name = 'promoted_' + name

        if self._player:
            name = 'player 1\'s ' + name
        else:
            name = 'player 2\'s ' + name

        return name


    def get_sym(self):
        return self.get_name()


    def get_piece_sym(self, sym):
        """
        returns a symbolic representation of the piece for printing to console
        :param sym: character of piece type
        :return: string with piece type character, capitalized for player 1, with a + appended if promoted
        """
        if self._promoted:
            sym += '+'

        if self._player:
            return sym.upper()

        return sym


    def get_dirs(self):
        """
        gets the directions and distance a piece can legally travel
        :return: array of tuples, with each tuple representing a set of directions and a distance
                 each tuple contains another array of tuples and an integer
                    the tuples in the array contain the directions the piece can travel
                    the integer represents how many spaces in that direction the piece can move
                        1 means the piece can move one space, -1 mean the pieces can move infinitely
                 e.g. [([(x, y), (z, a)], 1), ([(b, c)], -1)]
                 the piece can move 1 space in the (x, y) or (z, a) directions and infinitely in the (b, c) direction
        """
        return None


    def got_captured(self):
        """
        reset parameters when piece is captured
        :return: None
        """
        self._player = not self._player
        self._space = (0, 0)
        self._promoted = False
        self._alert_for_promotion = self.is_promoted()
        self.set_forced_rows()


    def gold_dirs(self):
        """
        gets movement of gold general and some promoted pieces
        :return: see get_dirs()
        """
        if self._player:
            return [(self._cardinals + [(-1, -1), (1, -1)], 1)]
        return [(self._cardinals + [(-1, 1), (1, 1)], 1)]


    def must_promote(self):
        return False


    def __str__(self):
        return self.get_name()


    def __len__(self):
        return 1


class Pawn(Piece):

    def get_name(self):
        return self.get_piece_name('pawn')


    def get_sym(self):
        return self.get_piece_sym('p')


    def get_dirs(self):
        if self._promoted:
            return self.gold_dirs()
        if self._player:
            return [([(0, -1)], 1)]
        else:
            return [([(0, 1)], 1)]


    def set_forced_rows(self):
        if self._player:
            self._forced_promotion = [1]
        else:
            self._forced_promotion = [9]


    def must_promote(self):
        col, row = self._space
        if row in self._forced_promotion:
            return True
        return False



class Lance(Piece):

    def get_name(self):
        return self.get_piece_name('lance')


    def get_sym(self):
        return self.get_piece_sym('l')


    def get_dirs(self):
        if self._promoted:
            return self.gold_dirs()
        if self._player:
            return [([(0, -1)], -1)]
        else:
            return [([(0, 1)], -1)]


    def set_forced_rows(self):
        if self._player:
            self._forced_promotion = [1]
        else:
            self._forced_promotion = [9]


    def must_promote(self):
        col, row = self._space
        if row in self._forced_promotion:
            return True
        return False


class Knight(Piece):

    def get_name(self):
        return self.get_piece_name('knight')


    def get_sym(self):
        return self.get_piece_sym('n')


    def get_dirs(self):
        if self._promoted:
            return self.gold_dirs()
        if self._player:
            return [([(-1, -2), (1, -2)], 1)]
        return [([(-1, 2), (1, 2)], 1)]


    def set_forced_rows(self):
        if self._player:
            self._forced_promotion = [1, 2]
        else:
            self._forced_promotion = [8, 9]


    def must_promote(self):
        col, row = self._space
        print(row)
        print(self._forced_promotion)
        if row in self._forced_promotion:
            return True
        return False


class Silver(Piece):

    def get_name(self):
        return self.get_piece_name('silver_general')


    def get_sym(self):
        return self.get_piece_sym('s')


    def get_dirs(self):
        if self._promoted:
            return self.gold_dirs()
        if self._player:
            return [(self._diagonals + [(0, -1)], 1)]
        return [(self._diagonals + [(0, 1)], 1)]


class Gold(Piece):

    def is_promoted(self):
        return True


    def get_name(self):
        return self.get_piece_name('gold_general')


    def get_sym(self):
        return self.get_piece_sym('g')


    def get_dirs(self):
        return self.gold_dirs()


class Bishop(Piece):

    def get_name(self):
        return self.get_piece_name('bishop')


    def get_sym(self):
        return self.get_piece_sym('b')


    def get_dirs(self):
        if self._promoted:
            return [(self._diagonals, -1), (self._cardinals, 1)]
        return [(self._diagonals, -1)]


class Rook(Piece):

    def get_name(self):
        return self.get_piece_name('rook')


    def get_sym(self):
        return self.get_piece_sym('r')


    def get_dirs(self):
        if self._promoted:
            return [(self._cardinals, -1), (self._diagonals, 1)]
        return [(self._cardinals, -1)]


class King(Piece):

    def is_promoted(self):
        return True


    def get_name(self):
        return self.get_piece_name('king')


    def get_sym(self):
        return self.get_piece_sym('k')


    def get_dirs(self):
        return [(self._diagonals + self._cardinals, 1)]



