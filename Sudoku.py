#!/usr/bin/env python3

from tkinter import *
import tkinter.font as tf
import pickle
import os


class Panel:
    def __init__(self, master):
        master.resizable(width=False, height=False)
        master.protocol('WM_DELETE_WINDOW', root.quit)
        master.title('Sudoku')
        self.quit = master.quit
        self.mode = 1
        self.current_num = 1
        self.key_x = 4
        self.key_y = 4
        self.difficulty = 20
        self.elements = [0] * 81
        self.conflicts = []
        self.box = []
        self.cache = 'cache'
        self.color_dict = {0: 'black', 1: 'red', 2: 'green', 3: 'blue', 4: 'white', 5: 'purple', 6: 'orange'}
        self.operations = {'a': 1, 'd': 3, 'w': 4, 's': 5, 'x': 2, 'space': 1, 'Return': 1, 'BackSpace': 3, 'Delete': 3}
        self.buttons = {'P': lambda: self.setmode(1),
                        'E': lambda: self.setmode(2),
                        'S': self.solve,
                        'G': self.gen,
                        'C': self.clear,
                        'D': self.destroy_all,
                        'Q': self.quit}
        self.directions = ['Right', 'Left', 'Down', 'Up']
        self.num_font = tf.Font(family='Fixdsys', size=30, weight=tf.BOLD)
        self.button_font = tf.Font(family='Fixdsys', size=12)
        self.msg_font = tf.Font(family='Fixdsys', size=16)
        self.Str = StringVar()
        self.Str.set('Made by ZML\nFeb 28 2017\n')

        self.matrix = [0] * 81
        self.color = [0] * 81
        self.history = [(self.matrix, self.color)]
        self.future = []

        self.load()

        master.bind("<Key>", self.key)
        self.C = Canvas(master, width=496, height=496)
        self.C.grid(row=0, column=0, rowspan=8)
        self.C.bind("<Button-1>", self.play)
        self.C.bind("<Button-2>", self.play)
        self.C.bind("<Button-3>", self.play)
        self.C.bind("<Button-4>", self.play)
        self.C.bind("<Button-5>", self.play)
        self.C.bind("<Motion>", self.show_num)
        self.C.bind("<Enter>", self.show_num)
        self.C.bind("<Leave>", self.show_num)
        self.init_display()
        self.display()
        Button(master, text='Play', command=lambda: self.setmode(1), width=20, fg=self.color_dict[2],
               font=self.button_font).grid(row=0, column=1, sticky=N + E + S + W)
        Button(master, text='Edit', command=lambda: self.setmode(2), width=20, fg=self.color_dict[2],
               font=self.button_font).grid(row=1, column=1, sticky=N + E + S + W)
        Button(master, text='Solve', command=self.solve, width=20, fg=self.color_dict[3],
               font=self.button_font).grid(row=2, column=1, sticky=N + E + S + W)
        Button(master, text='Generate', command=self.gen, width=20, fg=self.color_dict[3],
               font=self.button_font).grid(row=3, column=1, sticky=N + E + S + W)
        Button(master, text='Clear', command=self.clear, width=20, fg=self.color_dict[5],
               font=self.button_font).grid(row=4, column=1, sticky=N + E + S + W)
        Button(master, text='Destroy', command=self.destroy_all, width=20, fg=self.color_dict[5],
               font=self.button_font).grid(row=5, column=1, sticky=N + E + S + W)
        Button(master, text='Quit', command=self.save, width=20, fg=self.color_dict[1],
               font=self.button_font).grid(row=6, column=1, sticky=N + E + S + W)
        self.M = Message(master, textvariable=self.Str, width=200, fg=self.color_dict[1], font=self.msg_font)
        self.M.grid(row=7, column=1, sticky=N + E + S + W)
        self.M.bind("<Button-1>", self.inc_difficulty)
        self.M.bind("<Button-2>", self.back_to_newest)
        self.M.bind("<Button-3>", self.dec_difficulty)
        self.M.bind("<Button-4>", self.redo)
        self.M.bind("<Button-5>", self.undo)

    def backup(self):
        if not self.history or self.history[-1] != (self.matrix, self.color):
            self.history.append((self.matrix.copy(), self.color.copy()))
            self.future.clear()
        if len(self.history) > 10000:
            del (self.history[0])

    def undo(self, event=None):
        if len(self.history) > 1:
            self.future.append(self.history.pop())
            self.matrix = self.history[-1][0].copy()
            self.color = self.history[-1][1].copy()
            self.display()
            self.Str.set("Rolling backward\n\n")
        else:
            self.Str.set('Already oldest!\n\n')

    def redo(self, event=None):
        if self.future:
            self.matrix = self.future[-1][0].copy()
            self.color = self.future[-1][1].copy()
            self.history.append(self.future.pop())
            self.display()
            self.Str.set("Rolling forward\n\n")
        else:
            self.Str.set('Already newest!\n\n')

    def back_to_newest(self, event=None):
        while self.future:
            self.matrix = self.future[-1][0].copy()
            self.color = self.future[-1][1].copy()
            self.history.append(self.future.pop())
            self.display()
        self.Str.set('Already newest!\n\n')

    def dec_difficulty(self, event=None):
        if self.difficulty > 0:
            self.difficulty -= 20
            self.Str.set('Set difficulty=%d\n\n' % (self.difficulty,))

    def inc_difficulty(self, event=None):
        if self.difficulty < 200:
            self.difficulty += 20
            self.Str.set('Set difficulty=%d\n\n' % (self.difficulty,))

    @staticmethod
    def one_to_nine(l):
        return list(sorted(l)) != list(range(1, 10))

    @staticmethod
    def have_same(l):
        l = [i for i in l if i]
        return len(set(l)) < len(l)

    def conflicted(self):
        l = [self.matrix[9 * i:9 * (i + 1)] for i in range(9)]
        for i in l:
            if self.have_same(i):
                return 1
        for i in zip(*l):
            if self.have_same(i):
                return 1
        for i in [[l[x][y] for x in range(i, i + 3) for y in range(j, j + 3)] for i in range(0, 9, 3) for j in
                  range(0, 9, 3)]:
            if self.have_same(i):
                return 1
        return 0

    def get_conflict(self):
        ans = []
        for i in range(9):
            for j in range(9):
                for k in range(9):
                    for l in range(9):
                        if self.matrix[i * 9 + j] and self.matrix[i * 9 + j] == self.matrix[k * 9 + l]:
                            if (i, j) != (k, l) and (i == k or j == l or (i // 3, j // 3) == (k // 3, l // 3)):
                                x1 = 8 + (i // 3) * 163 + (i % 3) * 53 + 25
                                y1 = 8 + (j // 3) * 163 + (j % 3) * 53 + 25
                                x2 = 8 + (k // 3) * 163 + (k % 3) * 53 + 25
                                y2 = 8 + (l // 3) * 163 + (l % 3) * 53 + 25
                                ans.append((x1, y1, x2, y2))
        return ans

    def finished(self):
        l = [self.matrix[9 * i:9 * (i + 1)] for i in range(9)]
        for i in l:
            if self.one_to_nine(i):
                return 0
        for i in zip(*l):
            if self.one_to_nine(i):
                return 0
        for i in [[l[x][y] for x in range(i, i + 3) for y in range(j, j + 3)] for i in range(0, 9, 3) for j in
                  range(0, 9, 3)]:
            if self.one_to_nine(i):
                return 0
        return 1

    def save(self):
        with open(self.cache, 'wb') as f:
            pickle.dump((self.history, self.future), f)
        self.quit()

    def load(self):
        if not os.path.isfile(self.cache):
            with open(self.cache, 'wb') as f:
                pickle.dump((self.history, self.future), f)
        with open(self.cache, 'rb') as f:
            try:
                (self.history, self.future) = pickle.load(f)
                self.matrix = self.history[-1][0].copy()
                self.color = self.history[-1][1].copy()
            except pickle.PickleError:
                print('Load error!')
                self.backup()
            finally:
                f.close()

    def key(self, event):

        if len(event.keysym) == 1 and 0 <= ord(event.keysym) - ord('0') <= 9:
            self.current_num = ord(event.keysym) - ord('0')
            event.num = 1
            self.play(event, self.key_x * 9 + self.key_y)

        if event.keysym in self.operations:
            event.num = self.operations[event.keysym]
            self.play(event, self.key_x * 9 + self.key_y)

        if event.keysym in self.buttons:
            self.buttons[event.keysym]()

        if event.keysym == self.directions[0] and self.key_x < 8:
            self.key_x += 1

        if event.keysym == self.directions[1] and self.key_x > 0:
            self.key_x -= 1

        if event.keysym == self.directions[2] and self.key_y < 8:
            self.key_y += 1

        if event.keysym == self.directions[3] and self.key_y > 0:
            self.key_y -= 1

        if event.keysym in self.directions:
            self.play(event, self.key_x * 9 + self.key_y)

        if event.keysym == 'Next':
            self.dec_difficulty()

        if event.keysym == 'Prior' and self.difficulty < 200:
            self.inc_difficulty()

        if event.keysym == 'q':
            self.undo()

        if event.keysym == 'e':
            self.redo()

    def destroy_all(self):
        self.history.clear()
        self.future.clear()
        self.matrix = [0] * 81
        self.color = [0] * 81
        self.backup()
        self.display()
        self.Str.set('Destroyed!\n\n')

    def clear(self):
        flag = 1
        for i in range(81):
            if self.color[i] and self.matrix[i]:
                self.matrix[i] = 0
                flag = 0
        if flag:
            self.matrix = [0] * 81
            self.color = [0] * 81
        self.backup()
        self.display()
        self.Str.set('Cleared!\n\n')

    @staticmethod
    def trans(x, y):
        ans_x = -1
        ans_y = -1
        for i in range(3):
            for j in range(3):
                a = 8 + i * 163 + j * 53
                b = a + 49
                if a <= x <= b:
                    ans_x = i * 3 + j
                if a <= y <= b:
                    ans_y = i * 3 + j
        if ans_x == -1 or ans_y == -1:
            return -1
        else:
            return ans_x * 9 + ans_y

    def show_num(self, event, t=-1):
        if t == -1:
            t = self.trans(event.x, event.y)
        if t != -1 and self.matrix[t] == 0:
            self.matrix[t] = self.current_num
            x = self.color[t]
            self.color[t] = 6
            self.display()
            self.color[t] = x
            self.matrix[t] = 0
        else:
            self.display()

    def play(self, event, t=-1):

        if t == -1:
            t = self.trans(event.x, event.y)

        if t == -1:
            return

        if event.num == 1:
            self.key_x = t // 9
            self.key_y = t % 9
            if self.matrix[t] == 0:
                self.matrix[t] = self.current_num
                self.color[t] = 3 if self.mode == 1 else 0
                self.backup()
            elif self.mode == 1:
                if self.color[t] in [2, 5]:
                    self.color[t] = 3
                    self.backup()
            elif self.mode == 2:
                self.color[t] = 0
                self.backup()

        if event.num == 2:
            if self.matrix[t] == 0:
                self.matrix[t] = self.current_num
                self.color[t] = 2 if self.mode == 1 else 0
                self.backup()

        if event.num == 3:
            if self.matrix[t]:
                self.current_num = self.matrix[t]
            if self.color[t] or self.mode == 2:
                self.matrix[t] = 0
                self.color[t] = 0
                self.backup()

        if event.num == 4:
            if self.current_num < 9:
                self.current_num += 1

        if event.num == 5:
            if self.current_num > 1:
                self.current_num -= 1

        if event.num in [0, 1, 2, 3]:

            self.Str.set("Play mode\n\n" if self.mode == 1 else "Edit mode\n\n")

            if self.mode == 1 and self.finished() and all(i in [0, 3] for i in self.color):
                self.Str.set("Congratulations!\n(^-^)\n")

            if self.conflicted():
                self.Str.set("Conflict found!\n\n")

        self.show_num(event, t)

    def init_display(self):
        for i in range(4, 496, 163):
            self.C.create_line(0, i, 496, i, width=7)
            self.C.create_line(0, i + 55, 496, i + 55, width=3)
            self.C.create_line(0, i + 108, 496, i + 108, width=3)
            self.C.create_line(i, 0, i, 496, width=7)
            self.C.create_line(i + 55, 0, i + 55, 496, width=3)
            self.C.create_line(i + 108, 0, i + 108, 496, width=3)

    def draw_conflict(self):
        for x in self.conflicts:
            self.C.delete(x)
        self.conflicts.clear()
        for x in self.get_conflict():
            self.conflicts.append(self.C.create_line(*x, width=2, fill=self.color_dict[1]))

    def draw_box(self):
        for x in self.box:
            self.C.delete(x)
        self.box.clear()
        x1 = 8 + (self.key_x // 3) * 163 + (self.key_x % 3) * 53 + 1
        y1 = 8 + (self.key_y // 3) * 163 + (self.key_y % 3) * 53 + 1
        x2 = x1 + 49 - 1
        y2 = y1 + 49 - 1
        self.box.append(self.C.create_line(x1, y1, x2, y1, width=5, fill=self.color_dict[4]))
        self.box.append(self.C.create_line(x1, y2, x2, y2, width=5, fill=self.color_dict[4]))
        self.box.append(self.C.create_line(x1, y1, x1, y2, width=5, fill=self.color_dict[4]))
        self.box.append(self.C.create_line(x2, y1, x2, y2, width=5, fill=self.color_dict[4]))

    def display(self):
        self.draw_conflict()
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    for l in range(3):
                        t = i * 27 + k * 9 + j * 3 + l
                        if self.elements[t]:
                            self.C.delete(self.elements[t])
                            self.elements[t] = 0
                        if self.matrix[t]:
                            x = 8 + i * 163 + k * 53 + 25
                            y = 8 + j * 163 + l * 53 + 25
                            self.elements[t] = self.C.create_text(x, y, text=str(self.matrix[t]),
                                                                  font=self.num_font,
                                                                  fill=self.color_dict[self.color[t]])
        self.draw_box()

    def setmode(self, x):
        self.mode = x
        if x == 1:
            self.Str.set('Play Mode\n\n')
        if x == 2:
            self.Str.set('Edit Mode\n\n')

    def solve(self):
        if all(i for i in self.matrix):
            self.Str.set('Already solved!\n\n')
            return
        s, m, c, t = DLX.solve(self.matrix)
        for i in range(81):
            if self.matrix[i] == 0:
                self.color[i] = 5
        self.matrix = s
        self.backup()
        self.display()
        msg = ''
        if m:
            msg += 'Solved in ' + '%.3f' % (t / 10 ** 6,) + 'ms\n'
            if m == 1:
                msg += 'Difficulty: %d\n' % (c - 82,)
            else:
                msg += 'Multiple Solutions!\n'
        else:
            msg = 'No solution!\n\n'
        self.Str.set(msg)
        self.mode = 1
        self.current_num = 1

    @staticmethod
    def make(difficulty):
        ans = [0] * 81
        d = 10 ** 9
        for i in range(100 + difficulty * 2):
            l = DLX.generate()
            m = DLX.solve(l)[2] - 82
            if abs(m - difficulty) <= d:
                d = abs(m - difficulty)
                ans = l
        return ans

    def gen(self):
        self.matrix = self.make(self.difficulty)
        self.color = [0] * 81
        self.backup()
        self.display()
        s, m, c, t = DLX.solve(self.matrix)
        self.Str.set('Generated!\nDifficulty: %d\n' % (c - 82,))
        self.mode = 1
        self.current_num = 1


try:
    import DLX
except ImportError:
    os.system("sh make.sh")
    import DLX

root = Tk()

app = Panel(root)

root.mainloop()
root.destroy()
