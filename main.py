import tkinter as tk
from tkinter import messagebox as mb
from random import sample


class Node(tk.Label):
    """ Represents a part of the snake or an element of the game field.
    """
    def __init__(self, master, x, y, stay: int):
        super().__init__(master, bg='#15FA52', width=2, height=1)
        self.x = x
        self.y = y
        self.stay = stay

    def blink(self):
        """ Shows the part of the snake on a random place of the field.
        """
        self.config(bg='#FA3D3D')
        self.master.after(self.stay, self.clear)
        root.update_idletasks()
        root.update()

    def clear(self):
        """ Makes the part of the snake an element of the field again.
        """
        if (self.x, self.y) in snake.body or snake.game_finished or not snake.game_started:
            return
        self.config(bg='#15FA52')


class Snake:
    """ Represents the snake itself.
        Includes some features of the game (like control of start, finish, pause of the game).
    """
    def __init__(self, master, speed: int):
        self.master = master
        self.speed = speed
        self.length = tk.IntVar()
        self.length.set(3)
        self.head = nodes[ROOT_HEIGHT // 50][3]
        # list of the snake's body coords
        self.body = [(ROOT_HEIGHT // 50, 3), (ROOT_HEIGHT // 50, 2), (ROOT_HEIGHT // 50, 1)]
        self.tail = nodes[ROOT_HEIGHT // 50][1]
        self.direction = 'right'
        self.game_finished = False
        self.game_started = False
        self.eat = False
        self.pause = True

    def show(self):
        """ Responsible for the snake's view.
        """
        if not self.game_started:
            self.head['bg'] = '#FF5500'
            nodes[ROOT_HEIGHT // 50][2]['bg'] = '#FF8900'
            nodes[ROOT_HEIGHT // 50][1]['bg'] = '#FF8900'
            return

        self.head['bg'] = '#FF5500'
        neck = nodes[self.body[1][0]][self.body[1][1]]  # the part following the snake's head
        neck['bg'] = '#FF8900'
        if self.eat:
            self.eat = False
            self.body.append((self.tail.x, self.tail.y))
            self.length.set(int(self.length.get()) + 1)
            if int(self.length.get()) == (ROOT_HEIGHT // 20 - 5)*(ROOT_WIDTH // 20) - 1:
                self.survive()
                return
            snake_length_info.set(f'Snake\'s length: {snake.length.get()}')
            return
        self.tail['bg'] = '#15FA52'

    def move(self):
        """ Responsible for changing the snake's coordinates.
        """
        dx, dy = directions[self.direction][0], directions[self.direction][1]
        x_ahead, y_ahead = self.head.x + dx, self.head.y + dy
        if not (0 <= x_ahead < len(nodes)) or \
           not (0 <= y_ahead < len(nodes[0])) or \
           nodes[x_ahead][y_ahead]['bg'] == '#FF8900':
            self.crash()
            return
        self.head = nodes[x_ahead][y_ahead]
        if self.head['bg'] == '#FA3D3D':
            self.eat = True
        self.tail = nodes[self.body[-1][0]][self.body[-1][1]]
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i] = self.body[i - 1]
        self.body[0] = (self.head.x, self.head.y)
        self.show()

    def crash(self):
        """ Called when the player fails.
        """
        self.game_finished = True
        answer = mb.askyesno(title="You lost!", message="Play again?")
        if answer:
            reload()

    def survive(self):
        """ Called when the player succeeds.
        """
        self.game_finished = True
        level_value = int(level.get())
        difficulty_in_the_end = 'Normal'
        if level_value == 1:
            difficulty_in_the_end = 'Easy'
        elif level_value == 2:
            difficulty_in_the_end = 'Normal'
        elif level_value == 3:
            difficulty_in_the_end = 'Hard'
        answer = mb.askyesno(title="You win!",
                             message=f"Congratulations!\nYou survived in {difficulty_in_the_end} mode!\n\nPlay again?")
        if answer:
            reload()


def reload(values=None):
    """ Launch the game from the start with new or previous parameters.
    :param values: tuple of global values, that is needed to change. If None - no need of changing.
    """
    global pause_setter, ROOT_WIDTH, ROOT_HEIGHT, SNAKE_SPEED, NODES_QUANTITY, NODES_STAY, nodes
    pause_setter = 0
    if values:
        ROOT_WIDTH, ROOT_HEIGHT, SNAKE_SPEED, NODES_QUANTITY, NODES_STAY = values
    root.geometry(f'{ROOT_WIDTH}x{ROOT_HEIGHT}+600+150')
    [child.destroy() for child in root.winfo_children()]
    nodes = create_widgets()
    snake.__init__(root, SNAKE_SPEED)
    snake.show()
    root.focus_set()
    create_menu()
    snake_length_info.set('Press Space to start/pause')


def run():
    """ Constantly makes the snake move and nodes appear.
    """
    while not snake.game_finished and not snake.pause:
        nodes_appear()
        root.after(SNAKE_SPEED, snake.move())
        root.update_idletasks()
        root.update()


def choose_nodes():
    """ Compose a list of the nodes' coords except for the parts of the snake's body.
    :return: list of tuples
    """
    result = []
    for row in nodes:
        for node in row:
            element = (node.x, node.y)
            result.append(element)
    for coord in snake.body:
        if coord in result:
            result.remove(coord)
    return result


def nodes_appear():
    """ Randomly chooses nodes to appear.
    """
    possible_nodes = choose_nodes()
    max_nodes = NODES_QUANTITY
    if max_nodes > len(possible_nodes) - 1:
        max_nodes = len(possible_nodes) - 1
    nodes_to_appear = sample(possible_nodes, max_nodes)
    for node in nodes_to_appear:
        nodes[node[0]][node[1]].blink()


def turn(event, current_direction, opposite_direction):
    """ Changes the snake's direction.
        Do nothing if the player tries to change the direction to the opposite one.
    """
    if snake.direction == current_direction or snake.direction == opposite_direction:
        return
    snake.direction = current_direction


def set_pause(event):
    """ Makes the snake stop or move again.
    """
    global pause_setter
    if pause_setter % 2 == 0:
        if not snake.game_started:
            snake.game_started = True
        snake.pause = False
        pause_setter += 1
        snake_length_info.set(f'Snake\'s length: {snake.length.get()}')
        run()
    else:
        snake.pause = True
        pause_setter += 1


def bind_keys():
    root.bind('<Left>', lambda event, direction='left', op_direction='right': turn(event, direction, op_direction))
    root.bind('<Right>', lambda event, direction='right', op_direction='left': turn(event, direction, op_direction))
    root.bind('<Up>', lambda event, direction='up', op_direction='down': turn(event, direction, op_direction))
    root.bind('<Down>', lambda event, direction='down', op_direction='up': turn(event, direction, op_direction))
    root.bind('<space>', set_pause)


def create_menu():
    def restart():
        snake.game_finished = True
        reload()
    mainmenu = tk.Menu(root)
    root.config(menu=mainmenu)
    filemenu = tk.Menu(mainmenu, tearoff=0)
    filemenu.add_command(label='Restart', command=restart)
    filemenu.add_command(label='New Game', command=lambda: set_difficulty_and_values())
    filemenu.add_separator()
    filemenu.add_command(label='Exit', command=lambda: root.destroy())
    mainmenu.add_cascade(label='File', menu=filemenu)


def new_game():
    """ Called only one time for the session, when the game is launched.
    """
    root.geometry(f'{ROOT_WIDTH}x{ROOT_HEIGHT}+600+150')
    bind_keys()
    root.focus_set()
    create_menu()
    set_difficulty_and_values()


def create_widgets():
    """ Forms and returns a list of the field's elements and place them.
        Also place the inscription below the game field.
    :return: list
    """
    global snake_length_info
    snake_length_info = tk.StringVar()
    labels = []
    for i in range(ROOT_HEIGHT // 20 - 5):
        temp = []
        for j in range(ROOT_WIDTH // 20):
            node = Node(root, i, j, NODES_STAY)
            temp.append(node)
            node.grid(row=i, column=j)
        labels.append(temp)
    tk.Label(textvariable=snake_length_info, font='Bahnschrift 18', bg='#1DB34F', fg='#FDD81C').\
        grid(row=ROOT_HEIGHT // 20 - 5, column=0, rowspan=5, columnspan=ROOT_WIDTH // 20, sticky='nsew', ipady=8)
    return labels


def set_difficulty_and_values():
    """ Pops the window to set difficulty and reload the game.
    """
    global level
    window = tk.Toplevel()
    window.title('Difficulty settings')
    window.geometry('350x300+600+150')
    window.resizable(False, False)
    window.config(bg='#FFE577')
    window.grab_set()
    tk.Label(window, text='Choose the difficulty level.\nOn your choice depend the field\'s size,\n'
                          ' the snake\'s speed, how many parts appear\n and their durability.',
             font='Bahnschrift 12', bg='#FFE577', pady=10).pack()
    level = tk.IntVar()
    level.set(2)
    tk.Radiobutton(window, text='Easy', bg='#FFE577', variable=level, value=1,
                   font=('Bahnschrift', 14, 'bold'), activebackground='#F3D351').pack()
    tk.Radiobutton(window, text='Normal', bg='#FFE577', variable=level, value=2,
                   font=('Bahnschrift', 14, 'bold'), activebackground='#F3D351').pack()
    tk.Radiobutton(window, text='Hard', bg='#FFE577', variable=level, value=3,
                   font=('Bahnschrift', 14, 'bold'), activebackground='#F3D351').pack()

    def apply():
        level_value = int(level.get())
        main_values = (500, 500, 150, 5, 1500)
        if level_value == 1:
            main_values = (400, 400, 250, 8, 2000)
        elif level_value == 2:
            main_values = (500, 500, 150, 5, 1500)
        elif level_value == 3:
            main_values = (700, 700, 50, 3, 1000)
        reload(main_values)
        window.destroy()

    tk.Button(window, text='Apply', command=apply, font='Bahnschrift 13', bg='#76FF76',
              padx=5, pady=3, relief=tk.GROOVE, activebackground='#58E258').place(relx=0.3, rely=0.75)
    tk.Button(window, text='Cancel', command=lambda: window.destroy(), font='Bahnschrift 13', bg='#76FF76',
              padx=3, pady=3, relief=tk.GROOVE, activebackground='#58E258').place(relx=0.53, rely=0.75, anchor='nw')


root = tk.Tk()
root.title('Snake the game')
root.resizable(False, False)
root.config(bg='#15FA52')

ROOT_WIDTH = 500
ROOT_HEIGHT = 500
SNAKE_SPEED = 150
NODES_QUANTITY = 5  # how many nodes appear simultaneously
NODES_STAY = 1500  # how long nodes are visible

nodes = create_widgets()
snake = Snake(root, SNAKE_SPEED)
pause_setter = 0
directions = {'right': (0, 1), 'left': (0, -1), 'up': (-1, 0), 'down': (1, 0)}

new_game()
root.mainloop()
