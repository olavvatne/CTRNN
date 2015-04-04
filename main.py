from tkinter import *
from tkinter import ttk
import threading

import matplotlib.animation as animation

from config.configuration import Configuration
from gui.elements import Graph, LabelledEntry, LabelledSelect, ConfigurationDialog
from gui.visualization import ResultDialog
from ea.ea import EA
import cProfile

class AppUI(Frame):
    '''
    Main user interface of EA. Uses elements found in gui.elements. Layout of application.
    '''
    def __init__(self, master=None):
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        master.title("EA problem solver system")
        Frame.__init__(self, master, relief=SUNKEN, bd=2, highlightthickness=0)
        self.grid(sticky=N+S+E+W)

        self.menubar = Menu(self)
        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=menu)
        menu.add_command(label="Exit", command=on_exit)

        menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Simulator", menu=menu)
        menu.add_command(label="Settings", command=lambda: open_configuration(), accelerator="Ctrl+A")
        master.bind("<Control-a>", lambda event: open_configuration())
        menu.add_command(label="Run", command=lambda: run_pressed(), accelerator="Ctrl+R")
        master.bind("<Control-r>", lambda event: run_pressed())
        menu.add_command(label="Stop", command=lambda: stop_pressed(), accelerator="Ctrl+S")
        master.bind("<Control-s>", lambda event: stop_pressed())

        options = Configuration.get()
        def run_pressed():
            run_ea()

        def stop_pressed():
            stop_ea()

        def open_configuration():
            options = Configuration.get()
            d = ConfigurationDialog(master, options)
            master.wait_window(d.top)
            if d.result:
                Configuration.store(d.result)

        try:
            self.master.config(menu=self.menubar)
        except AttributeError:
            self.master.tk.call(master, "config", "-menu", self.menubar)

        gui_control_elements = [
            {"name": "population_size", "label": "Pop size", "value": 20},
            {"name": "generations","label": "Cycles", "value": 100},
            {"name": "genome_length", "label": "Genome length", "value": 20},
            {"name": "threshold", "label": "Threshold","value": 1},
            {"name": "genotype", "label": "Genotype","value": None},
            {"name": "translator", "label": "Translator","value": None},
            {"name": "fitness", "label": "Fitness","value": None},
            {"name": "parent_selection", "label": "Parent selection","value": None},
            {"name": "adult_selection", "label": "Adult selection","value": None},
            ]

        self.elements = {}
        for i in range(4):
            e = gui_control_elements[i]
            self.elements[e["name"]] = LabelledEntry(self, e["label"], e["value"])
            self.elements[e["name"]].grid(row=i+1, column=0, padx=4, pady=4, sticky="WE")
            self.rowconfigure(i+1,weight=1)

        for i in range(4,len(gui_control_elements)):
            e = gui_control_elements[i]
            self.elements[e["name"]] = LabelledSelect(self, self.option_list(options[e["name"]]), e["label"])
            self.elements[e["name"]].grid(row=i+1, column=0, padx=4, pady=4, sticky="WE")
            self.rowconfigure(i+1,weight=1)

        self.average_fitness = Label(self, text="Avg fitness: ")
        self.average_fitness.grid(row=0, column=1, sticky=W ,padx=2, pady=4)
        self.average_fitness_value = Label(self, text="0")
        self.average_fitness_value.grid(row=0, column=1, sticky=E ,padx=2, pady=4)

        self.best_fitness = Label(self, text="Best fitness: ")
        self.best_fitness.grid(row=0, column=2, sticky=W ,padx=2, pady=4)
        self.best_fitness_value = Label(self, text="0")
        self.best_fitness_value.grid(row=0, column=2, sticky=E ,padx=2, pady=4)

        self.cycles = Label(self, text="Cycles: ")
        self.cycles.grid(row=0, column=3, sticky=W ,padx=2, pady=4)
        self.cycles_value = Label(self, text="0")
        self.cycles_value.grid(row=0, column=3, sticky=E ,padx=2, pady=4)

        self.progress = ttk.Progressbar(self, orient='horizontal')
        self.progress.grid(row=10, column=0, columnspan=5, sticky="WES")

        self.graph = Graph(self)
        self.graph.grid(row=1, column=1, columnspan=4, rowspan=9, sticky="WNSE")

        self.columnconfigure(0, minsize="150")
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)

    def option_list(self, d):
        return sorted(d, key=lambda k: d[k]["order"])

    def update(self, c, p, cf, bf, std):
        self.progress.step(p)
        self.average_fitness_value.configure(text=str("%.3f" %cf))
        self.best_fitness_value.configure(text=str("%.3f" %bf))
        self.cycles_value.configure(text=str(c))
        self.graph.add(c, bf, cf, std)


def stop_ea(*args):
    ea_system.stop()


def run_ea(*args):
    '''
    Method configure and runs EA in it's own thread so the user interface is
    responsive while running.
    '''
    Configuration.reload()
    ea_system.setup(app.elements["translator"].get(),
                 app.elements["fitness"].get(),
                 app.elements["genotype"].get(),
                 app.elements["adult_selection"].get(),
                 app.elements["parent_selection"].get(),
                 app.elements["genome_length"].get())
    app.graph.clear()

    def callback():
        pop_size = int(app.elements["population_size"].get())
        gen = int(app.elements["generations"].get())
        threshold = app.elements["threshold"].get_special()
        best = ea_system.run(pop_size, gen, threshold)
        app.progress.stop()
        app.graph.dump()
        #TODO: Make general. EA, get method that ask each component for important shit
        #TODO: that subclasses are in charge of
        show_result(best, ea_system.fitness_evaluator.scenarios)


    t = threading.Thread(target=callback)
    t.daemon = True
    t.start()


def show_result(individual, scenarios):
    config = Configuration.get()
    result_dialog = ResultDialog(app, individual, scenarios, config)

def on_exit(*args):
    '''
    Exits application
    '''
    root.quit()


root = Tk()
app = AppUI(master=root)
root.bind('<Return>', run_ea)
ea_system = EA()
ani = animation.FuncAnimation(app.graph.f, app.graph.animate, interval=3000)
ea_system.add_listener(app)
root.mainloop()
