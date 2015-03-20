from tkinter import *
from tkinter import ttk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import style
import csv
style.use('ggplot')


class Graph(Frame):
    '''
    Gui element for a graphing standard deviation, best fitness and average fitness over time or cycles.
    The element display to plots. The class has methods for animating and adding new data points.
    '''
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.f = Figure()
        self.a = self.f.add_subplot(211)
        self.b = self.f.add_subplot(212)
        self.x_list = []
        self.bf_list = []
        self.af_list = []
        self.std_list = []

        canvas = FigureCanvasTkAgg(self.f, self)
        canvas._tkcanvas.config(highlightthickness=0)
        canvas.show()
        canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)

    def add(self, x, bf, af, std):
        '''
        During the Ea run data points can be added to the figure.
        '''
        self.x_list.append(x)
        self.bf_list.append(bf)
        self.af_list.append(af)
        self.std_list.append(std)

    def animate(self, i):
        '''
        Matplotlib can be animated. This method clears the plots and redraw the figure.
        By using animation.FuncAnimation this function will be called at a fixed interval.
        '''
        self.a.clear()
        self.b.clear()
        self.a.plot(self.x_list, self.bf_list, label="Best")
        self.a.plot(self.x_list, self.af_list, label="Average")
        self.b.plot(self.x_list, self.std_list, label="Std")
        self.a.legend( loc='lower right' )
        self.b.legend( loc='upper right' )

    def clear(self):
        '''
        Removes all data points from the graph.
        '''
        self.x_list = []
        self.bf_list = []
        self.af_list = []
        self.std_list = []

    def dump(self):
        '''
        Writes figure data to a csv file. Useful for drawing figures with external programs.
        '''
        file = open("dump.csv", "w")
        writer = csv.writer(file, delimiter=',', lineterminator='\n')
        data = zip(self.x_list, self.bf_list, self.af_list, self.std_list)
        writer.writerows(data)
        file.close()


class ConfigurationDialog(object):
    '''
    The Ea is highly parameterized, and ConfigurationDialog gives the user the option of changing
    the parameters found in a file or dictionary. The dialog dynamically creates tabs for each module
    and a labelled entry box for each parameter.
    '''
    def __init__(self, parent, config):

        top = self.top = Toplevel(parent)
        top.title("EA solver - Configuration")
        panes = ttk.Notebook(top)
        panes.pack()
        param = "parameters"
        self.result = None
        self.config = config
        self.elements = config.copy()
        #Creates tabs and labelled entry boxes for all parameters.
        for module_name, module in config.items():
            sub = Frame(panes)
            panes.add(sub, text=module_name)
            for element_name, element in module.items():
                if param in element:
                    t = element[param]
                    header = Label(sub, text=element_name,font=("Helvatica", 10, "bold"))
                    header.pack(padx=5, anchor=W)
                    for i in t.keys():
                        self.elements[module_name][element_name][param][i] = LabelledEntry(sub, i, t[i])
                        self.elements[module_name][element_name][param][i].pack(padx=5, fill="both")


        b = Button(top, text="OK", command=self.ok)
        b.pack(pady=5)

    def ok(self):
        self.update()
        self.result = self.config
        self.top.destroy()

    def update(self):
        '''
        Update method takes the value of all entries and write them back into the config dict.
        '''
        param = "parameters"
        for module_name, module in self.config.items():
            for element_name, element in module.items():
                if param in element:
                    t = element[param]
                    for i in t.keys():
                        e = self.elements[module_name][element_name][param][i].get()
                        self.config[module_name][element_name][param][i] = e


class LabelledSelect(Frame):
    '''
    LabelledSelect is a gui component that create a label and drop down box with options and put them in
    a frame. This element can then be displayed in the GUI. The selected value can be retrieved using the
    get method.
    '''
    def __init__(self, parent, options, label_text, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.label = Label(self, text=label_text)
        self.selected = StringVar(self)
        self.selected.set(options[0])
        self.option_select = OptionMenu(self, self.selected, *options)
        self.option_select.pack(side="right", anchor=E)
        self.label.pack(side="left", anchor=W, expand=True)

    def get(self):
        return self.selected.get()


class LabelledEntry(Frame):
    '''
    LabelledEntry created a gui component consisting of a label and an entry box. Numbers and text
    can be entered. The element can be put in the Gui. Several methods are supplied for retrieving
    the value.
    '''
    def __init__(self, parent, label_text, default_value,  *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.label = Label(self, text=label_text)
        self.content = StringVar(self)
        self.content.set(str(default_value))
        self.entry = Entry(self, textvariable=self.content)
        self.label.pack(side="left", anchor=W, expand=True)
        self.entry.pack(side="right", anchor=E)

    def get(self):
        '''
        Depending on what has been entered a integer, float or boolean are returned.
        The content of the entry is a string and this method returns a number or a boolean.
        '''
        v = self.content.get()
        if self._is_int(v):
            return int(v)
        elif self._is_float(v):
            return float(v)
        elif v == 'True' or v == 'False':
            return eval(v)
        else:
            raise RuntimeError(v + ". Not a number or bool!")

    def get_special(self):
        v = self.content.get()
        if not len(v)>0:
            return float("inf")
        else:
            return self.get()

    def _is_float(self, n):
        '''
        Test to see if content of entry is a float
        '''
        try:
            float(n)
            return True
        except ValueError:
            return False

    def _is_int(self, n):
        '''
        Test to see if content of entry is a integer
        '''
        try:
            int(n)
            return True
        except ValueError:
            return False
