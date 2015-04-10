from tkinter import Toplevel, Button
from simulator.environment import Environment
from tkinter import *
from tkinter import ttk
from enum import Enum
from math import fabs, floor
from gui.elements import LabelledSelect
from collections import deque

#Subclass of the tkinters Canvas object. Contains methods
#for setting a graph model and drawing a graph, and changing
#the vertices' colors.
class PixelDisplay(Canvas):
    cWi = 600
    cHi = 300

    def __init__(self, parent):
        self.queue = deque([])
        self.model = None
        self.width = self.cWi
        self.height = self.cHi
        self.padding = int(self.width/64)
        self.parent = parent
        self.offset = 1
        self.event_rate = 400
        self._callback_id = None
        super().__init__(parent, bg='white', width=self.width, height=self.height, highlightthickness=0)

    def set_rate(self, n):
        self.event_rate = n

    def set_model(self, model):
        self.model = model

    def get_model(self):
        return self.model


    def draw(self):
        '''
        Draw will call itself and redraw (colorize nodes) as long
        as the display is in running mode or there are timeslices left
        in the queue. The queue of timeslices allow the algorithm to run at
        full speed while the display is delaying the rendering, so it is easy to
        watch it's progress

        Draw will pop a timeslice from the draw queue, and
        use it's data to draw the partial solution on screen.
        Each cell will be assigned a color, and a arrow/point to indicate
        direction the cell gives its output.
        '''
        if len(self.queue)>0:
            timeslice = self.queue.popleft()
            if timeslice:
                self.draw_model(timeslice)


        if not self.stopped or len(self.queue) > 0:
            self._callback_id =self.after(self.event_rate, self.draw)

    def colorize_item(self, item, color):
        self.itemconfig(item, fill=color)


    def draw_label(self, x_pos, y_pos, w, h, text,t="label", c="black"):
        x = self.translate_x(x_pos)
        y = self.translate_y(y_pos)
        w = self.translate_y(x_pos + w)
        h = self.translate_y(y_pos + h)
        penalty = len(text)
        font_size = 35 -penalty*2
        font = ("Helvetica", font_size, "bold")
        self.create_text((x+w)/2, (y+h)/2, text=text, tags=t, fill=c, font=font)

    #Method for drawing a graph from a ProblemModel.
    #Draws the model and add tags so individual nodes can later
    #be changed.
    def draw_model(self, timeslice):
        pass

    def start(self):
        self.stopped = False
        self.draw()

    def stop(self):
        self.after_cancel(self._callback_id)
        self.stopped = True

    #The actual x position of the graph element on screen
    def translate_x(self, x):
        self.padding = 0
        x_norm = fabs(self.min_x) + x
        available_width = min(self.width, self.height)
        x_screen = (self.padding/2) + x_norm*(float((available_width-self.padding)/self.w))
        return x_screen

    #The actual y position of the graph element on screen
    def translate_y(self, y):
        self.padding = 0
        available_height= min(self.width, self.height)
        y_norm = fabs(self.min_y) + y
        y_screen = (self.padding/2) + y_norm*(float((available_height-self.padding)/self.h))
        return y_screen

    def reset(self):
        self.delete(ALL)

    def set_padding(self, padding):
        self.padding = padding

    #draws a cell.
    def draw_pixel(self, x,y, w, h, c, tag=""):
        self.create_rectangle(self.translate_x(x),
            self.translate_y(y),
            self.translate_x(x+w),
            self.translate_y(y+h),
            fill=c,
            tags=tag)

    def draw_rounded(self, x_pos, y_pos, width, height, color, rad=5, tags="", padding=0, line="black"):
        x = self.translate_x(x_pos)+padding
        y = self.translate_y(y_pos)+padding
        w = self.translate_x(x_pos+width)-padding
        h = self.translate_y(y_pos+height)-padding
        self.create_oval(x, y, x +rad, y + rad, fill=color, tag=tags, width=1, outline=line)
        self.create_oval(w -rad, y, w, y + rad, fill=color, tag=tags, width=1, outline=line)
        self.create_oval(x, h-rad, x +rad, h, fill=color, tag=tags, width=1, outline=line)
        self.create_oval(w-rad, h-rad, w , h, fill=color, tag=tags, width=1, outline=line)
        self.create_rectangle(x + (rad/2.0), y, w-(rad/2.0), h, fill=color, tag=tags, width=0)
        self.create_rectangle(x , y + (rad/2.0), w, h-(rad/2.0), fill=color, tag=tags, width=0)

    def set_dimension(self, max_x, max_y, min_x, min_y):
        self.w = fabs(min_x) + max_x
        self.h = fabs(min_y) + max_y
        self.max_x = max_x
        self.max_y = max_y
        self.min_y = min_y
        self.min_x = min_x

    def set_queue(self, data):
        self.queue.clear()
        self.queue.extend(data)

    def event(self, data):
        self.queue.append(data)

class TrackerAgentDisplay(PixelDisplay):

    def __init__(self, parent, width, height):
        super().__init__(parent)
        self.bw = width
        self.bh = height
        self.bg = "#bbada0"
        self.empty_cell = "#ccc0b3"
        self.set_dimension(self.bw, self.bh, 0, 0 )
        self.draw_board()

    def draw_board(self):
        self.reset()
        self.draw_pixel(0, 0, self.bw, self.bg, self.bg, tag="bg")
        for i in range(self.bw):
            for j in range(self.bh):
                self.draw_rounded(i,j, 1, 1,  self.empty_cell, padding=2, line=self.bg, tags="bg")


    def draw_model(self, timeslice):
        if timeslice:
            timestep, tracker, object = timeslice
            self.delete("Piece")

            #Draw tracker
            x, y, dim = tracker
            for i in range(dim):
                #TODO: remove magic number
                self.draw_piece("Piece", x+i, y, 1)

            #Draw object
            x,y,dim = object
            for i in range(dim):
                #TODO: remove magic number
                self.draw_piece("Piece", x+i, y, 2)

            self.create_text(20, 20, font=("Arial",20), text=str(timestep+1), fill="white", tags="Piece")


    def draw_piece(self, piece_id, x, y, piece_type):
        self.draw_rounded(x,y, 1, 1,  self._get_color(piece_type), padding=8, line=self.bg, tags=piece_id)
        #self.draw_label( x,y, 1,1, str(piece_id), t=piece_id)

    def _get_color(self, type):
        c = {1:"green", 2:"red", 3:"blue"}
        return c.get(type)

class ResultDialog(object):
    '''
    The tracker agent can be visualized by the resultDialog. The dialog consists of a pixel display, speed adjuster,
    restart button, scenario list box and a new scenario button.
    '''
    def __init__(self, parent, individual):
        self.individual = individual

        self.scenario = Environment(30,15)

        top = self.top = Toplevel(parent)
        top.title("Tracker game - results")
        top.grid()
        self.canvas = TrackerAgentDisplay(top, self.dim)
        self.canvas.set_model(self.current)
        self.canvas.grid(row=0, column=0, columnspan=5, sticky=N ,padx=4, pady=4)

        self.v = StringVar()
        speed_adjuster = Scale(top, from_=200, to=1000, command=self.set_speed,orient=HORIZONTAL, variable=self.v)
        speed_adjuster.set(400)
        speed_adjuster.grid(row=1, column=0,padx=4, pady=4)

        restart_button = Button(top, text="Restart", command=self.reset)
        restart_button.grid(row=1, column=4,padx=4, pady=4)


        finish_button = Button(top, text="OK", command=self.ok)
        finish_button.grid(row=2, column=4,padx=4, pady=10)

        self.record_agent()

    def reset(self):
        self.canvas.stop()
        self.canvas.set_queue(self.recording)
        self.canvas.start()


    def set_speed(self, *args):
        self.canvas.set_rate(int(self.v.get()))

    def record_agent(self):
        p = self.individual.phenotype_container.get_ANN()
        self.current.score_agent(p, recording=True)
        self.recording = self.current.get_recording()
        self.canvas.set_queue(self.recording)
        self.canvas.start()

    def ok(self):

        self.top.destroy()