from tkinter import *
from shogi_files.pieces import *
from shogi_files.game import *
from shogi_files.popup import *
from copy import *
import requests
import os


# flip  = 'http://192.168.0.21:7534'
flip = 'http://flip2.engr.oregonstate.edu:7534'


class Board(Frame):

    _edge_len = 50


    def __init__(self, parent, game):

        Frame.__init__(self, parent)

        # the game being played
        self._game = game

        # set up the GUI
        self._width, self._height = self._game.get_board_dims()
        self._header = None
        self._bg = None
        self.draw_gui()

        # save images in dictionary to prevent having to find/transform them more than once
        self._images = {}

        # tuple containing the piece selected to move and all of the valid moves it can do
        self._to_be_moved = None

        # tuple containing the piece that moved last and the space it moved from
        self._just_moved = None

        # list of Game objects as the game progresses to allow undoing moves
        self._undo_back_up = []
        self._redo_back_up = []

        # draw the game
        self.show_pieces()
        self.change_header()

        self._bg.bind('<Button-1>', self.left_click)
        self._bg.bind('<Button-2>', self.middle_click)
        self._bg.bind('<Button-3>', self.right_click)


    def draw_gui(self):
        """
        create and place all static elements of the GUI
        :return: None
        """

        # constants for dimensioning
        heading_height = 2 * self._edge_len
        subheading_height = 0.7 * self._edge_len
        bg_height = (self._height + 2) * self._edge_len
        heading_width = (self._width + 2) * self._edge_len
        rules_width = 6 * self._edge_len
        bg_width = heading_width + rules_width

        # creating and setting up header
        self._header = Canvas(self, width=heading_width, height=heading_height,
                              background='white', highlightbackground='black')
        self._header.place(x=0, y=0)

        # creating and setting up background
        self._bg = Canvas(self, width=bg_width, height=bg_height,
                          background='grey', highlightbackground='black')
        self._bg.place(x=0, y=(heading_height + subheading_height + 4))

        jail_x2 = bg_width - self._edge_len
        jail_y1 = self._edge_len
        jail_y2 = jail_y1 + 4 * self._edge_len
        jail_y3 = jail_y2 + self._edge_len
        jail_y4 = jail_y3 + 4 * self._edge_len
        self._bg.create_rectangle(heading_width, jail_y1, jail_x2, jail_y2, outline='black')
        self._bg.create_rectangle(heading_width, jail_y3, jail_x2, jail_y4, outline='black')

        # setting up and creating other banners and buttons
        rules_txt = 'Rules of Shogi\n' \
                    'Shogi is a complicated chess variant\n' \
                    'from Japan with different rules and pieces\n' \
                    'Click here to learn how to play!'
        rules_button = Button(self, text=rules_txt, command=game_rules)
        rules_button.place(x=heading_width + 4, y=2,
                           width=rules_width, height=heading_height)

        instr_txt = 'Left-click on a piece to select and move it!\n' \
                    'Click the buttons to the right or use the Help menu for more information'
        basic_instr = Canvas(self, width=heading_width, height=subheading_height,
                             background='white', highlightbackground='black')
        basic_instr.create_text(heading_width // 2 + 1, subheading_height // 2 + 2,
                                justify=CENTER, text=instr_txt)
        basic_instr.place(x=0, y=heading_height + 2)

        instr_button = Button(self, text='Advanced Help', command=app_info)
        instr_button.place(x=heading_width + 4, y=heading_height + 4,
                           width=rules_width, height=subheading_height)

        # creating and setting up undo and redo buttons
        undo_button = Button(self, text='Undo\na move', command=self.undo)
        undo_button.place(x=heading_width + self._edge_len + 1, y=7.7 * self._edge_len + 10,
                          width=self._edge_len, height=self._edge_len - 10)
        redo_button = Button(self, text='Redo\na move', command=self.redo)
        redo_button.place(x=heading_width + 3 * self._edge_len + 1, y=7.7 * self._edge_len + 10,
                          width=self._edge_len, height=self._edge_len - 10)

        # drawing actual board
        self.draw_spaces()



    def draw_spaces(self):
        """
        draws out the board
        :return: None
        """
        for row in range(self._height):
            for col in range(self._width):
                x1 = (col + 1) * self._edge_len
                y1 = (self._height - row) * self._edge_len
                x2 = x1 + self._edge_len
                y2 = y1 + self._edge_len
                self._bg.create_rectangle(x1, y1, x2, y2, outline='black', fill='tan')


    def get_space(self, event):
        """
        gets the board coordinate of a click
        :param event: mouse click
        :return: tuple containing board location in format: column, row
        """
        col = (self._width + 1) - event.x // self._edge_len
        row = event.y // self._edge_len
        return col, row


    def create_piece_image(self, piece):
        """
        links image to piece based on piece type
        :param piece: Piece object to display
        :return: id of piece image
        """

        # try to find the image of the piece from just the piece type
        piece_key = 'shogi_files/img/%s.gif' % piece.get_name().split(' ')[-1].lower()

        # the two kings have different images, so need to find the proper one
        if 'king' in piece.get_name():
            if '1' in piece.get_name():
                piece_key = 'shogi_files/img/king1.gif'
            else:
                piece_key = 'shogi_files/img/king2.gif'

        file_name = piece_key

        # modify the dictionary key for upside down pieces
        if not piece.get_player():
            piece_key = piece_key.split('.gif')[0] + '_180.gif'

        # if image is not in the dictionary, open image, rotate if needed, and save image in dictionary
        if piece_key not in self._images:
            img_file = {'image': open(file_name, 'rb')}

            if not piece.get_player():
                r = requests.post(flip + '/rotation?180', files=img_file)
                if r.status_code == 200:
                    with open(piece_key, 'wb') as f:
                        f.write(r.content)

            self._images[piece_key] = PhotoImage(file=piece_key).zoom(self._edge_len).subsample(100)

            # delete saved image after storing it in dictionary
            for f in os.listdir('shogi_files/img'):
                if '180' in f:
                    os.remove('shogi_files/img/' + f)

        return self._bg.create_image(0, 0, image=self._images[piece_key], tags='piece')


    def place_piece(self, piece_id, coords):
        """
        places piece image on correct board location
        :param piece_id: id of the piece image
        :param coords: coordinates to center image
        :return: None
        """
        col, row = coords
        x = (self._width - col + 1) * self._edge_len + self._edge_len // 2
        y = row * self._edge_len + self._edge_len // 2
        self._bg.coords(piece_id, x, y)


    def show_pieces(self):
        """
        displays all pieces on the board with their respective icons
        :return: None
        """
        self._bg.delete('piece')
        for piece in self._game.get_board_pieces():
            piece_id = self.create_piece_image(piece)
            self.place_piece(piece_id, piece.get_space())

        for i, piece in enumerate(self._game.get_p1_jail()):
            col = (i % 5 + 1) * -1
            row = 9 - i // 5
            piece_id = self.create_piece_image(piece)
            self.place_piece(piece_id, (col, row))

        for i, piece in enumerate(self._game.get_p2_jail()):
            col = (i % 5 + 1) * -1
            row = i // 5 + 1
            piece_id = self.create_piece_image(piece)
            self.place_piece(piece_id, (col, row))


    def change_header(self, msg=None, player=None):
        """
        updates the header to show different messages
        :param msg: message to be displayed - if not given, header will display whose turn it is
        :param player: True for player 1, False for player 2
        :return: None
        """
        self._header.delete('head')

        if not self._game.is_finished():
            self._header.delete('king')

            if self._game.get_turn():
                img = 'shogi_files/img/king1.gif'
            else:
                img = 'shogi_files/img/king2_180.gif'

            self._header.create_image(self._edge_len, self._edge_len, image=self._images[img], tags='king')
            self._header.create_image(10 * self._edge_len, self._edge_len, image=self._images[img], tags='king')

        if msg is None:
            if self._game.get_turn():
                msg = 'Player 1\'s Turn'
            else:
                msg = 'Player 2\'s Turn'
        elif player is not None:
            if player:
                msg = 'Player 1 ' + msg
            else:
                msg = 'Player 2 ' + msg
        text_x = (self._width + 2) * self._edge_len // 2
        text_y = self._edge_len
        self._header.create_text(text_x, text_y, text=msg, font='Arial 20 bold', tags='head')


    def show_possible_moves(self, piece, col, row):
        """
        displays circles on the board to indicate spaces a given piece can legally move to
        :param piece: Piece object to be moved
        :param col: initial column on the board
        :param row: initial row on the board
        :return: None
        """
        self._bg.delete('circle')

        moves = self._game.possible_moves(piece)
        self._to_be_moved = piece, moves

        x1 = (self._width - col + 1) * self._edge_len
        y1 = row * self._edge_len
        x2 = x1 + self._edge_len
        y2 = y1 + self._edge_len
        self._bg.create_oval(x1, y1, x2, y2, outline='blue',
                             width=(self._edge_len // 8), tags='circle')
        for col, row in moves:
            if self._game.get_piece_on((col, row)) is None:
                x1 = (self._width - col + 1) * self._edge_len + self._edge_len // 4
                y1 = row * self._edge_len + self._edge_len // 4
                x2 = x1 + self._edge_len // 2
                y2 = y1 + self._edge_len // 2
                self._bg.create_oval(x1, y1, x2, y2, outline='red',
                                     width=(self._edge_len // 8), tags='circle')
            else:
                x1 = (self._width - col + 1) * self._edge_len
                y1 = row * self._edge_len
                x2 = x1 + self._edge_len
                y2 = y1 + self._edge_len
                self._bg.create_oval(x1, y1, x2, y2, outline='red',
                                     width=(self._edge_len // 8), tags='circle')


    def left_click(self, event):
        """
        all of the processes that occur when the board is left-clicked
        :param event: mouse click
        :return: None
        """
        if self._game.is_finished():
            return

        self._bg.delete('circle')

        col, row = self.get_space(event)

        piece = self._game.get_piece_on((col, row))

        self.change_header()

        # if there is no piece already selected
        if self._to_be_moved is None:
            if piece is None:
                return
            elif piece.get_player() != self._game.get_turn():
                self.change_header('Not your turn!')
                return
            self.show_possible_moves(piece, col, row)

        # if a piece is already selected to move
        else:

            # move the piece to the clicked space if possible
            if (col, row) in self._to_be_moved[1]:
                self._undo_back_up.append(deepcopy(self._game))
                self._just_moved = self._to_be_moved[0], copy(self._to_be_moved[0].get_space())
                self._game.move_piece(self._to_be_moved[0], (col, row))
                self.show_pieces()
                self._game.switch_turn()
                self._to_be_moved = None
                self._redo_back_up = []


                # check promotion availability and produce pop up if desired
                if self._game.eligible_for_promotion(*self._just_moved):
                    if self._just_moved[0].give_alert() or self._just_moved[0].must_promote():
                        self.promotion_popup(self._just_moved[0])

                self.check_for_check()


            # deselect the piece
            elif piece == self._to_be_moved[0]:
                self._to_be_moved = None

            # don't allow selection of opponent pieces
            elif piece is not None:
                if piece.get_player() != self._game.get_turn():
                    self.change_header('Not your turn!')
                    self._to_be_moved = None
                    return
                self.show_possible_moves(piece, col, row)


    def check_for_check(self):
        """
        changes the header depending on the game state
        :return: None
        """
        if self._game.is_in_check(self._game.get_turn()):
            if self._game.is_in_checkmate(self._game.get_turn()):
                self.change_header('Wins!', not self._game.get_turn())
            else:
                self.change_header('is in check!', self._game.get_turn())
        else:
            self.change_header()


    def right_click(self, event):
        """
        information for the clicked piece
        :param event: mouse right click
        :return: None
        """
        col, row = self.get_space(event)

        piece = self._game.get_piece_on((col, row))
        if piece:
            piece_info(piece)


    def promotion_popup(self, piece):
        """
        promotion pop up
        :param piece: piece to be promoted
        :return: None
        """
        popup = promotion_alert(piece)
        self.wait_window(popup)
        self.show_pieces()


    def middle_click(self, event):
        """
        alternative method of getting to the promotion menu/pop up
        :param event: mouse click
        :return: None
        """
        if self._game.is_finished():
            return

        space = self.get_space(event)
        if not self._game.on_board(space):
            return

        piece = self._game.get_piece_on(space)
        if piece is None:
            return

        if self._just_moved is None:
            error_txt = 'You need to start playing before\nyou can promote!'
        elif piece.is_promoted():
            error_txt = 'Piece cannot be promoted further'
        elif self._just_moved[0] != piece:
            error_txt = 'Piece must have been the last piece to move'
        elif not self._game.eligible_for_promotion(*self._just_moved):
            error_txt = 'Piece must have touched a space in\nthe furthest three rows to promote'
        elif self._just_moved[1] == (0, 0):
            error_txt = 'Piece cannot be promoted on the\nsame turn it was dropped'
        else:
            self.promotion_popup(piece)
            return

        popup = alert_popup(error_txt, 'Promotion Error')
        self.wait_window(popup)


    def undo(self):
        """
        go backwards one step
        :return: None
        """
        self._bg.delete('circle')
        if not self._undo_back_up:
            self.change_header('Cannot go further backwards')
        else:
            self._redo_back_up.append(deepcopy(self._game))
            self._game.undo_checkmate()
            self._game = self._undo_back_up.pop()
            self.change_header()
            self.show_pieces()


    def redo(self):
        """
        go forwards one step if the undo functionality was used
        :return: None
        """
        self._bg.delete('circle')
        if self._game.is_finished():
            return

        if not self._redo_back_up:
            self.change_header('Cannot go further forwards')
        else:
            self._undo_back_up.append(deepcopy(self._game))
            self._game = self._redo_back_up.pop()
            self.check_for_check()
            self.show_pieces()


    def new_game(self):
        """
        ask user if they want to start a new game and start it if so
        :return: None
        """
        new = SaveLoad()
        popup = new.confirm_popup('start a new game')
        self.wait_window(popup)

        if new.confirm_option():
            self._game.set_up_board()
            self._to_be_moved = None
            self._just_moved = None
            self._undo_back_up = []
            self.show_pieces()
            self.change_header()


    def load_game(self):
        """
        find list of save files and load a selected file if possible
        :return: None
        """
        if not os.path.isdir('shogi_files/saves'):
            popup = alert_popup('Save directory not found', 'Load Error')
            self.wait_window(popup)
            return

        files = [f for f in os.listdir('shogi_files/saves') if f.startswith('shogi_save')]
        files = [f for f in files if f.endswith('.txt')]
        if not files:
            popup = alert_popup('No game saves found', 'Load Error')
            self.wait_window(popup)
            return

        load = SaveLoad()
        popup = load.load_popup(files)
        self.wait_window(popup)

        filename = load.get_filename()
        if filename == '':
            return

        if self._game.load_game('shogi_files/saves/' + filename):
            self.show_pieces()
            self.change_header()
        else:
            popup = alert_popup('Game could not be loaded', 'Load Error')
            self.wait_window(popup)


    def save_game(self):
        """
        ask user if they want to save and create save file for current game state if so
        :return: None
        """
        save = SaveLoad()
        popup = save.confirm_popup('save')
        self.wait_window(popup)

        if save.confirm_option():
            save_num = self._game.save_game()

            popup = alert_popup('Game saved as:\nshogi_save'+str(save_num)+'.txt', 'Game Saved')
            self.wait_window(popup)


    def quit_game(self):
        """
        ask user if they want to quit and give the option to save if so
        :return: None
        """
        qt = SaveLoad()
        popup = qt.confirm_popup('quit')
        self.wait_window(popup)

        if qt.confirm_option():
            self.save_game()
        self.quit()


def set_up_menu(root, board):
    """
    set up menu bar
    :param root: Tk object
    :param board: Board object
    :return: None
    """
    menu_bar = Menu(root)
    file_options = Menu(menu_bar, tearoff=0)
    file_options.add_command(label='New Game', command=board.new_game)
    file_options.add_command(label='Load Game', command=board.load_game)
    file_options.add_command(label='Save Game', command=board.save_game)
    file_options.add_separator()
    file_options.add_command(label='Quit', command=board.quit_game)
    menu_bar.add_cascade(label='File', menu=file_options)

    help_options = Menu(menu_bar, tearoff=0)
    help_options.add_command(label='Game Rules', command=game_rules)
    help_options.add_command(label='Using this app', command=app_info)
    menu_bar.add_cascade(label='Help', menu=help_options)

    root.config(menu=menu_bar)


def display_board(game):
    """
    set up and display game GUI
    :param game: game being played
    :return: None
    """
    root = Tk()
    root.title('Shogi - by Alexander Kim (kima4) for CS361')
    gui = Board(root, game)
    set_up_menu(root, gui)
    gui.pack(side='top', fill='both', expand='true', padx=4, pady=4)
    root.geometry("862x701")
    root.mainloop()



def main():
    pass


if __name__ == '__main__':
    main()


