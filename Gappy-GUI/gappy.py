import numpy as np
from tkinter import *
from tkinter import ttk, messagebox
from datetime import time, date, datetime
import time
from minizinc import Instance, Model, Solver

DEBUG = False

DIFFICULTY = ["Easy", "Medium", "Difficult"]
INSTANCES = [
    "Instance 1",
    "Instance 2",
    "Instance 3",
    "Instance 4",
    "Instance 5",
    "Instance 6",
    "Instance 7",
    "Instance 8",
    "Instance 9",
    "Instance 10",
    "Instance 11",
    "Instance 12",
    "Instance 13",
    "Instance 14",
    "Instance 15",
    "Instance 16",
    "Instance 17",
    "Instance 18",
    "Instance 19",
    "Instance 20"
]

class Game(Tk):
    def __init__(self):
        # Tk.__init__(self)
        super().__init__()  # For python3
        self.N = 10
        self.clues_H = [2, 1, 1, 2, 2, 1, 5, 4, 3, 3]
        self.clues_V = [1, 6, 6, 1, 7, 1, 1, 3, 4, 4]
        self.setClues(1)

        self.diffVar = StringVar(self)
        self.diffVar.set(DIFFICULTY[0])

        self.instVar = StringVar(self)
        self.instVar.set(INSTANCES[0])

        self.initUI()

    def initUI(self):
        self.gr = np.full((self.N, self.N), False)
        print(self.gr)
        self.cells = {}
        self.startTime = None

        self.title('Gappy Puzzle')
        self.content = ttk.Frame(self, padding=10)
        self.content.grid(row=0, column=0, sticky=(N, S, E, W))

        self.timeLabel = Label(self.content, text="00:00:00")
        self.timeLabel.grid(row=1, column=0, sticky=(N, S, E, W), ipady=10)

        self.canvas = Canvas(self.content, width=550, height=550,
                             borderwidth=1, highlightthickness=0, background='gray')
        self.canvas.grid(row=2, column=0, sticky=(N, S, E, W))
        self.canvas.bind('<Configure>', self.draw)

        self.OM = OptionMenu(self, self.diffVar, *DIFFICULTY)
        self.OM.grid(row=3, column=0, sticky=(N, W), padx=20)
        self.OM["menu"].configure(bg="gray", selectcolor="white")

        self.OM1 = OptionMenu(self, self.instVar, *INSTANCES)
        self.OM1.grid(row=4, column=0, sticky=(N, W), padx=20)
        self.OM1["menu"].configure(bg="white", selectcolor="white")

        self.submit_button = Button(text='Submit', command=self.submit_game, bg='black', fg='white', font=(
            'helvetica', 11, 'bold'), width=20, height=2)
        self.submit_button.grid(row=3, column=0, sticky=(N, E), padx=20)

        self.restart_button = Button(text='RESTART', command=self.restart_game, bg='white', fg='black', font=(
            'helvetica', 11, 'bold'), width=20, height=2)
        self.restart_button.grid(
            row=4, column=0, sticky=(N, E), padx=20, pady=10)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)
        self.content.rowconfigure(0, weight=4)
        self.content.rowconfigure(1, weight=1)

        self.startTime = datetime.now()
        self.updateTimer()

    def draw(self, event=None):
        # Drawing grid with cells
        self.canvas.delete('rect')
        width = int(self.canvas.winfo_width()/(self.N + 1))
        height = int(self.canvas.winfo_height()/(self.N + 1))
        for col in range(self.N):
            # Drawing Horizontal Clues
            CHx1 = col*width + width
            CHx2 = CHx1 + width
            CHy1 = 0
            CHy2 = height
            clueH = self.canvas.create_rectangle(
                CHx1, CHy1, CHx2, CHy2, fill='white')
            if (self.clues_H[col] != '<>'):
                self.canvas.create_text(CHx1 + 25, 25, text=self.clues_H[col])

            # Drawing Vertical Clues and Board
            for row in range(self.N):
                # Drawing the Vertical Clues
                CVx1 = 0
                CVx2 = width
                CVy1 = row*height + height
                CVy2 = CVy1 + height
                clueV = self.canvas.create_rectangle(
                    CVx1, CVy1, CVx2, CVy2, fill='white')
                if (self.clues_V[row] != '<>'):
                    self.canvas.create_text(25, CVy1 + 25, text=self.clues_V[row])

                # Drawing the Board
                x1 = col*width + width
                y1 = row*height + height
                x2 = x1 + width
                y2 = y1 + height
                if self.gr[row][col] == 0:
                    cell = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                        fill='white', tags='cell')
                else:
                    cell = self.canvas.create_rectangle(x1, y1, x2, y2,
                                                        fill='black', tags='cell')
                self.cells[row, col] = cell
                self.canvas.tag_bind(cell, '<Button-1>', lambda event,
                                     row=row, col=col: self.click(row, col))

    def click(self, row, col):
        cell = self.cells[row, col]
        color = 'white' if self.gr[row, col] == True else 'black'
        if self.gr[row, col] == False:
            self.gr[row, col] = True
        else:
            self.gr[row, col] = False
        self.canvas.itemconfigure(cell, fill=color)

    def submit_game(self):
        print(self.gr)
        diff = DIFFICULTY.index(self.diffVar.get())
        inst = INSTANCES.index(self.instVar.get())
        real_instance = (diff*10)+(inst+1)
        data_file_path = "../Gappy-Data/instances_from_website/instance_" + str(real_instance) + ".dzn"
        print(np.array(self.get_all_solutions(data_file_path)[0]))

        if((np.array(self.get_all_solutions(data_file_path)[0])==self.gr).all()):
            messagebox.showerror("Correct Answer", "Amazing !")
        else:
            messagebox.showerror("Wrong Answer", "Try to check the RULES !")

    def validate_input(self, grid) -> bool:
        for row in range(self.N):
            rowSum = int(sum(grid[row]))
            if rowSum != 2:
                return False

        for col in range(self.N):
            colSum = 0
            for row in range(self.N):
                colSum += int(grid[row][col])
            if colSum != 2:
                return False

        pivot = grid[0][0]

        for row in range(self.N):
            for col in range(self.N):
                pivot = int(grid[row][col])
                if pivot == 1:
                    for i in range(-1, 2):
                        if (0 <= row+i < self.N):
                            for j in range(-1, 2):
                                if(i != 0 and j != 0 and 0 <= col+j < self.N):
                                    if int(grid[row+i][col+j]) == 1:
                                        return False
        return True

    def get_all_solutions(self, data_file):
        gecode = Solver.lookup("gecode")
        model = Model('../gaps.mzn')
        model._add_file(data_file)
        instance = Instance(gecode, model)
        result = instance.solve(all_solutions=True)
        if DEBUG:
            print(result)

        solutions = []

        for i in range(len(result)):
            solutions.append(result[i, "assign"])

        return(solutions)

    def check_response(self, grid) -> bool:
        print("Valid Input ... Let's check the response")
        for row in range(self.N):
            start_counting = False
            gaps = 0
            clue = int(self.clues_V[row])
            for col in range(self.N):
                if(grid[row][col] == 1):
                    start_counting = not(start_counting)
                elif(start_counting):
                    gaps += 1
            if(gaps != clue):
                messagebox.showerror("Wrong Answer", "Check RULES !")
                return False

        for col in range(self.N):
            start_counting_V = False
            gaps = 0
            clue = int(self.clues_H[col])
            for row in range(self.N):
                if(grid[row][col] == 1):
                    start_counting_V = not(start_counting_V)
                elif(start_counting_V):
                    gaps += 1
            if(gaps != clue):
                messagebox.showerror("Wrong Answer", "Check RULES !")
                return False
        messagebox.showerror("Good Answer", "You Are Brilliant !")
        self.startTime = None
        return True

    def updateTimer(self):
        ts = "00:00:00"
        if self.startTime != None:
            diff = datetime.now() - self.startTime
            ts = str(diff).split('.')[0]
            if diff.total_seconds() < 36000:
                ts = "0" + ts
        self.timeLabel.config(text=ts)
        self.content.after(100, self.updateTimer)

    def restart_game(self):
        print(DIFFICULTY.index(self.diffVar.get()))
        diff = DIFFICULTY.index(self.diffVar.get())
        inst = INSTANCES.index(self.instVar.get())
        real_instance = (diff*10)+(inst+1)
        self.setClues(real_instance)
        self.initUI()

    def setClues(self, instance):
        file_path = "./instances/instance_" + str(instance) + ".dzn"
        file = open(file_path, "r")
        cluesV = file.readline()[1:-2].split(", ")
        cluesH = file.readline()[1:-1].split(", ")
        self.clues_H = cluesH
        self.clues_V = cluesV
        print(cluesH)
        print(cluesV)

if __name__ == '__main__':
    gappy = Game()
    gappy.mainloop()
