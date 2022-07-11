from tkinter import *
from shogi_files.pieces import *
import textwrap
import requests


wiki = None
scraper_url = 'http://flip3.engr.oregonstate.edu:8898/wiki_scraper'
wiki_dict = {'url': 'https://en.wikipedia.org/wiki/Shogi'}



def get_wiki():
    """
    send request to wiki scraper to get text from wiki page
    :return: None, but results saved to global variable
    """
    req = requests.get(scraper_url, params=wiki_dict)
    global wiki
    wiki = req.content.decode('unicode-escape')
    wiki = wiki.split('\n')


def find_section(title):
    """
    find section with a given title
    :param title: title string
    :return: list of paragraphs under the given title
    """
    paras = {'Objective': (16, 17),
             'Movement': (17, 33),
             'Promotion': (33, 44),
             'Drops': (52, 58),
             'End of the Game': (58, 63)}
    start, end = paras[title]
    return wiki[start:end]


def game_rules():
    """
    pops up game rules
    :return: None
    """

    categories = ['Objective',
                  'Movement',
                  'Promotion',
                  'Drops',
                  'End of the Game']

    if wiki is None:
        get_wiki()
    popup = Toplevel()
    popup.title('How to play')
    popup.geometry("800x250")
    select = Label(popup, text='Rule Categories', font=('Helvetica', 16, 'bold'))
    rules = Label(popup, text='What you should know', font=('Helvetica', 16, 'bold'))
    select.place(x=0, y=0)
    rules.place(x=200, y=0)

    cat_frame = Frame(popup)
    list_cats = Listbox(cat_frame, height=5, selectmode=SINGLE)
    list_cats.pack(expand=True, fill=Y)
    for cat in categories:
        list_cats.insert(END, cat)

    cat_frame.place(x=25, y=40)

    info_frame = Frame(popup)
    info_scroll = Scrollbar(info_frame)
    info_scroll.pack(side=RIGHT, fill=Y)
    info_txt = Text(info_frame, height=10, width=70)
    info_txt.pack(expand=True, fill=Y)
    info_txt.configure(yscrollcommand=info_scroll.set)
    info_scroll.config(command=info_txt.yview)

    info_frame.place(x=200, y=40)

    def show_rules():
        info_txt.delete('1.0', END)
        sec_title = list_cats.get(list_cats.curselection()[0])
        section = find_section(sec_title)
        for line in section:
            if line.strip() == '':
                pass
            else:
                info_txt.insert(END, textwrap.fill(line, width=65))
                info_txt.insert(END, '\n\n')

    select_button = Button(popup, text='View selection', font=('Helvetica', 12, 'bold'), command=show_rules)
    select_button.place(x=25, y=150)


def app_info():
    """
    pops up instructions for using the app
    :return: None
    """
    instruct_text = ['Instructions:',
                     'Starting with Player 1 at the bottom of the board, take turns '
                     'moving pieces until one player wins by putting the other in '
                     'checkmate!',
                     'To move a piece, click one; if it has legal moves, red circles '
                     'will appear on the board; click a space with a red circle to '
                     'move the piece to that space',
                     'To learn more about how a piece moves, right click on it',
                     'Captured pieces can be redeployed, or \'dropped\' by the player '
                     'that captured it; just click on a captured piece to see where '
                     'it can be dropped',
                     'Pay attention to the banner at the top of the application for '
                     'important information such as whose turn it is and if a player '
                     'is in check',
                     'Promoted pieces are red to make them more easily distinguishable.',
                     '',
                     'Key bindings:',
                     'Left-click: Select a piece to move, select a space to move a '
                     'selected piece, or deselect a piece',
                     'Middle-click: Promote a piece, if possible, or see why that '
                     'piece is not eligible for promotion',
                     'Right-click: Display a pop up with information about the piece',
                     '',
                     'This app was made for CS361 and uses Sravya Kaniti\'s Wikipedia '
                     'scraper and Alexander Kim\'s image rotator.'
                     ]
    popup = Toplevel()
    popup.title('How to use this app')

    for instr in instruct_text:
        Label(popup, text=textwrap.fill(instr), anchor='w', justify='left').pack(padx=20, side=TOP, anchor='w', fill='both')


def piece_info(piece):
    """
    pops up information about a selected piece
    :param piece: piece for which to display information
    :return: None
    """
    if wiki is None:
        get_wiki()

    piece_name = piece.get_name().split(' ')[-1].replace('promoted_', '')
    popup = Toplevel()
    popup.title(piece_name)

    Label(popup, text=str.title(piece_name.replace('_', ' ')), font=('Helvetica', 16, 'bold')).pack()

    info_frame = Frame(popup)

    piece_txt = Text(info_frame, width=53, height=20)
    scroll = Scrollbar(info_frame)
    scroll.pack(side=RIGHT, fill=Y)
    piece_txt.pack(side=RIGHT)
    piece_txt.configure(yscrollcommand=scroll.set)

    scroll.config(command=piece_txt.yview)

    for line in find_section('Movement')+find_section('Promotion'):
        if ' ' + piece_name.split('_')[0] in line:
            piece_txt.insert(END, textwrap.fill(line, width=50))
            piece_txt.insert(END, '\n\n')

    info_frame.pack()

def promotion_alert(piece):
    """
    pops up when a piece becomes eligible for promotion or when attempting to promote a piece eligible for promotion
    :param piece: piece to be promoted
    :return: TopLevel object
    """

    def accept():
        piece.promote_piece()
        popup.destroy()

    def decline():
        piece.future_alerts(checkbox.get() == 0)
        popup.destroy()


    popup = Toplevel()
    popup.title('Promotion Alert')

    if piece.must_promote():
        alert_msg = Label(popup, text='Piece promotion required')
        okay_button = Button(popup, text='Okay', command=popup.destroy)

        alert_msg.pack()
        okay_button.pack()

        piece.promote_piece()
    else:
        alert_msg = Label(popup, text='Piece promotion available')
        accept_button = Button(popup, text='Accept', command=accept)
        decline_button = Button(popup, text='Decline', command=decline)
        checkbox = IntVar()
        do_not_ask_again = Checkbutton(popup, text='Do not ask again for this piece', variable=checkbox, onvalue=1, offvalue=0)
        check_text = Label(popup, text='Promotion option can be accessed\nagain by middle clicking on this piece')

        alert_msg.grid(columnspan=2, padx=20, pady=10)
        accept_button.grid(row=1, column=0)
        decline_button.grid(row=1, column=1)
        do_not_ask_again.grid(columnspan=2)
        check_text.grid(columnspan=2)

    popup.grab_set()
    return popup


def alert_popup(alert_txt, alert_title):
    """
    generic template for alert popup - must be acknowledged before proceeding
    :param alert_txt: alert text to be displayed
    :param alert_title: title of popup
    :return: TopLevel object
    """
    popup = Toplevel()
    popup.title(alert_title)
    alert_msg = Label(popup, text=alert_txt)
    okay_button = Button(popup, text='Okay', command=popup.destroy)

    alert_msg.pack(padx=20, pady=10)
    okay_button.pack(padx=20, pady=10)

    popup.grab_set()
    return popup


class SaveLoad:
    """
    used for when the GUI needs feedback from a pop up to determine the next action
    """

    def __init__(self):
        self._confirm = False
        self._filename = ''


    def confirm_option(self):
        return self._confirm


    def get_filename(self):
        return self._filename


    def confirm_popup(self, option):
        """
        pop up with yes or no question
        :param option: string of what to ask the user if they want
        :return: Toplevel object
        """
        title_txt = option.title() + '?'
        heading_txt = 'Do you want\nto ' + option + '?'

        popup = Toplevel()
        popup.title(title_txt)
        heading = Label(popup, text=heading_txt, font=('Helvetica', 16))

        def accept():
            self._confirm = True
            popup.destroy()

        def decline():
            self._confirm = False
            popup.destroy()

        yes = Button(popup, text='Yes', command=accept)
        no = Button(popup, text='No', command=decline)

        heading.grid(columnspan=2, padx=20, pady=10)
        yes.grid(column=0, row=1, padx=20, pady=10, sticky=N+S+E+W)
        no.grid(column=1, row=1, padx=20, pady=10, sticky=N+S+E+W)

        popup.grab_set()
        return popup


    def load_popup(self, save_files):
        """
        pop up that is created when asking user which save file to load
        :param save_files: list of save files
        :return: Toplevel object
        """
        popup = Toplevel()
        popup.title('Load Game')
        heading = Label(popup, text='Detected Save Files', font=('Helvetica', 16))

        files_frame = Frame(popup)
        files_scroll = Scrollbar(files_frame)
        files_scroll.pack(side=RIGHT, fill=Y)
        list_files = Listbox(files_frame, height=5, selectmode=SINGLE, yscrollcommand=files_scroll.set)
        list_files.pack(expand=True, side=RIGHT, fill=Y)
        for f in save_files:
            list_files.insert(END, f)

        files_scroll.config(command=list_files.yview)

        def load_selected():
            self._filename = list_files.get(list_files.curselection()[0])
            popup.destroy()


        load_button = Button(popup, text='Load selection', font=('Helvetica', 12, 'bold'),
                               command=load_selected)

        heading.grid(column=0, row=0, padx=20, pady=10)
        files_frame.grid(column=0, row=1, padx=20, pady=10)
        load_button.grid(column=0, row=2, padx=20, pady=10)

        popup.grab_set()
        return popup


