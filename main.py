"""
AUTHOR: EUAN
DATE: 18/09/2023

TODO:
- Add in timer (MAYBE)
- Fix flag bug (something to do with positions and counting of mines left)
- Add in win condition
- Board generation is slightly wrong

DONE:
- Add in auto unveil through empty squares, up to the first instance of a non zero in all directions
- Mine counter
- Add in mine marking
- Ensure the first click is NEVER a mine, generate buttons beforehand in this case.

Extra:
AI to solve minesweeper.
"""

import numpy as np
import tkinter as tk


class Board:
    def __init__(self, num_mines, width, height):
        self.frame = None
        self.num_mines = num_mines
        self.width = width
        self.height = height
        self.board = np.zeros((width, height), dtype=int)
        self.mine_pos = []
        self.flag_pos = []
        self.buttons = []
        self.visited = []
        self.unvisited = []
        self.color = ("#4373cc", "#43cc78", "#c93052", "#111b9e", "#9e3e11", "#1daeb3", "black", "#706f70")
        self.root = tk.Tk()
        self.game_frame = tk.Frame(self.root)
        self.num_mines_label = tk.Label(text=f"Mines Left: {self.num_mines}")
        self.num_mines_label.grid(row=0, column=0)
        self.game_frame.grid(row=1, column=0)
        self.generate_buttons()
        self.first_play = True

    def check_pos(self, y, x):
        if self.board[y][x] != -1:
            self.board[y][x] += 1
    def generate_buttons(self):
        # Generate grid
        for x in range(0, self.width):
            for y in range(0, self.height):
                # Add to buttons to list to keep track when unveiling
                self.frame = tk.Frame(self.game_frame, highlightbackground="black", highlightthickness=1)
                button = tk.Frame(self.frame, bg="grey", width=122, height=122)
                label = tk.Label(self.frame)

                # Add bindings
                button.bind("<Button-1>", lambda pos=(x, y), f=button: self.unveil(f))
                button.bind("<Button-2>", lambda pos=(x, y), f=button: self.flag_place(f))
                button.bind("<Button-3>", lambda pos=(x, y), f=button: self.flag_place(f))

                # Place on to board
                self.frame.grid(row=y, column=x)
                button.grid(row=y, column=x)
                self.buttons.append([button, (x, y), label])

    def generate_board(self, click):
        # Generate mines
        mines_left = self.num_mines

        while mines_left != 0:
            # Chose a random location on the board
            x = np.random.randint(self.width) - 1
            y = np.random.randint(self.height) - 1

            # If the location selected isn't marked as a mine already, and x and y is not the start position
            if self.board[y][x] != -1 and (x, y) != click:
                # Mark it as a mine
                self.board[y][x] = -1
                self.mine_pos.append((x, y))
                mines_left -= 1
                self.check(self.check_pos, x, y)

            # Else, chose another location.

        # Generate GUI
        for i in self.buttons:
            x, y = i[1]
            val = self.board[y][x]
            if val == 0:
                i[2].config(text="", width=10, height=5, font=('Arial', 15), fg=self.color[val])
            elif val == -1:
                i[2].config(text="X", width=10, height=5, font=('Arial', 15), fg=self.color[val])
            elif val > 0:
                i[2].config(text=str(val), width=10, height=5, font=('Arial', 15), fg=self.color[val])

    def check_pos_unveil(self, y, x):
        if not (x > self.width - 1 or y > self.height - 1):
            if self.board[y][x] == 0 and (x, y) not in self.visited and (x, y) not in self.unvisited:
                self.unvisited.append((x, y))

            # Neighbour is non-zero and not a mine, unveil and add to visited.
            elif self.board[y][x] > 0 and self.board[y][x] != -1 and (x, y) not in self.visited:
                self.visited.append((x, y))
                # Unveil

    def unveil(self, button):
        pos = ()
        if self.first_play:
            self.first_play = False
            for i in self.buttons:
                if i[0] == button:
                    pos = i[1]
            self.generate_board(pos)

        pos = ()
        for i in self.buttons:
            if i[0] == button:
                pos = i[1]
        # Find neighbours of the current selection that are equal to 0 and add to unvisited. Any which are non-zero
        # and not -1, add to visited.
        self.unvisited = [pos]
        self.visited = []

        # Only unveil if the selected position is equal to 0
        if self.board[pos[1]][pos[0]] == 0:
            while self.unvisited:
                # Get next position in unvisited
                pos = self.unvisited.pop()
                self.visited.append(pos)

                # Find neighbours from current position
                self.find_neighbours(pos)

            # Unveil all items that have been visited
            for items in self.visited:
                for i, sublist in enumerate(self.buttons):
                    if sublist[1] == items:
                        sublist[0].grid_forget()
                        sublist[2].grid(row=sublist[1][1], column=sublist[1][0])

        else:
            for i, sublist in enumerate(self.buttons):
                if sublist[1] == pos:
                    if sublist[2]['text'] == "X":
                        self.end("You lose!")
                    sublist[0].grid_forget()
                    sublist[2].grid(row=sublist[1][1], column=sublist[1][0])

    def check(self, function, x, y):
        if x == 0:  # Left
            if y == 0:  # Top left
                function(y + 1, x + 1)
                function(y + 1, x)

            elif y == self.height - 1:  # Bottom Left
                function(y - 1, x + 1)
                function(y - 1, x)

            else:  # Left of board
                function(y - 1, x)
                self.check_pos(y - 1, x + 1)
                self.check_pos(y + 1, x + 1)
                function(y + 1, x)

            self.check_pos(y, x + 1)

        elif x == self.width - 1:  # Right
            if y == 0:  # Top right
                function(y + 1, x - 1)
                function(y + 1, x)

            elif y == self.height - 1:  # Bottom right
                function(y - 1, x - 1)
                function(y - 1, x)

            else:  # Right of board
                function(y - 1, x)
                function(y - 1, x - 1)
                function(y + 1, x - 1)
                function(y + 1, x)

            function(y, x - 1)

        else:
            if y == 0:  # Top
                function(y + 1, x - 1)
                function(y + 1, x + 1)
                function(y + 1, x)

            elif y == self.height - 1:  # Bottom
                function(y - 1, x - 1)
                function(y - 1, x)
                function(y - 1, x + 1)

            else:  # Anywhere else
                function(y - 1, x - 1)
                function(y - 1, x)
                function(y - 1, x + 1)
                function(y + 1, x - 1)
                function(y + 1, x)
                function(y + 1, x + 1)

            function(y, x - 1)
            function(y, x + 1)

    def flag_place(self, frame):
        pos = ()
        for i in self.buttons:
            if i[0] == frame:
                pos = i[1]
        print(f"Flag placed: {pos}")
        # When a frame is right-clicked, add a flag.
        # Only allow marking if there are enough mines
        if self.num_mines - len(self.flag_pos) > 0:
            flag = tk.Label(frame, text=u"\u2691", fg="black", width=10, height=5, font=('Arial', 15))
            flag.pack()
            self.flag_pos.append((frame, flag, pos))
            self.num_mines_label['text'] = f"Mines Left: {self.num_mines - len(self.flag_pos)}"

            flag.bind("<Button-2>", lambda f=frame: self.flag_remove(flag, pos, f))
            flag.bind("<Button-3>", lambda f=frame: self.flag_remove(flag, pos, f))

            # Update behaviour of flagged piece:
        correct = 0
        for item in self.flag_pos:
            if item[2] in self.mine_pos:
                correct += 1
                print("correct")
        print(f"Correct flags = {correct}")
        if correct == self.num_mines:
            self.end("You won!")

    def flag_remove(self, flag, pos, frame):
        # Remove flag
        for i in self.flag_pos:
            if i[2] == pos:
                self.flag_pos.remove(i)

        # Update flag counter
        self.num_mines_label['text'] = f"Mines Left: {self.num_mines - len(self.flag_pos)}"
        flag.pack_forget()

    def find_neighbours(self, pos):
        x = pos[0]
        y = pos[1]
        if x > self.width - 1:
            x = self.width - 1
        if y > self.height - 1:
            y = self.height - 1

        self.check(self.check_pos_unveil, x, y)

    def end(self, text):
        # Unbind all buttons
        for i in self.buttons:
            for j in range(1, 4):
                i[0].unbind(f"<Button-{j}")

        window = tk.Toplevel(self.root)
        window.geometry("200x50")
        tk.Label(window, text=text).pack()
        tk.Button(window, text="New Game", command=self.quit).pack()

    def quit(self):
        self.root.destroy()
        self.__init__(5, 5, 5)


msBoard = Board(5, 5, 5)
msBoard.root.mainloop()
