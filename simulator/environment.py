import numpy as np


class Environment:
    EMPTY = 0
    FOOD = 1
    POISON = 2

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3

    MOVE_FORWARD = 0
    MOVE_LEFT = 1
    MOVE_RIGHT = 2

    def __init__(self, dim, f_prob=0.333, p_prob=0.333, agent_start_pos=(5,5)):
        #F_prob of a cell being filled with food, and p_prob that a remaining empty cell
        #is filled with poisoon
        probabilites = [1-f_prob-(f_prob*(1-p_prob)), f_prob, f_prob*(1-p_prob)]
        self.board = np.random.choice(3, replace=True, p=probabilites, size=(dim, dim))
        self.agent_x = agent_start_pos[1]
        self.agent_y = agent_start_pos[0]
        self.agent_dir = Environment.NORTH
        self.recording = []
        self.poison = 0
        self.food = 0
        self.dim = dim
        self.board[self.agent_y, self.agent_x] = Environment.EMPTY
        #Food and poision removed from agent's start position

    def init_scoring(self):
        b = np.empty_like (self.board)
        b[:] = self.board
        #TODO: Might consider using a structure to keep track of changes made
        #to board while sim
        self.food = 0
        self.poison = 0
        y = self.agent_y
        x = self.agent_x
        dir = self.agent_dir
        return b, y, x, dir

    def score_agent(self, agent, timesteps=60):
        b, y, x, dir = self.init_scoring()
        #print("SCORE ------------------------------------")
        #TODO: Create a record method? And not dilute score agent
        self.recording = []

        for i in range(timesteps):

            #Senor gathering
            food_sensors = self._get_sensor_data(y,x,dir, b, Environment.FOOD)
            poison_sensors = self._get_sensor_data(y,x,dir, b, Environment.POISON)
            #Motor output
            motor_output = agent.feedforward(np.array(food_sensors + poison_sensors, dtype=np.int32))
            #print("Motor", motor_output)
            winning_output = np.argmax(motor_output)
            #print("FOOD", food_sensors)
            #print("POISON", poison_sensors)
            #print(i ,motor_output)
            if motor_output[winning_output] > 0.5:
                m = 0
                if winning_output == Environment.MOVE_LEFT:
                    #print("MOVE LEFT")
                    m = -1
                elif winning_output == Environment.MOVE_RIGHT:
                    #print("MOVE RIGHT")
                    m = 1

                #Update scoring and environment
                self.recording.append((i, x,y,(dir+m)%4))
                y,x,dir = self._move_agent(y, x, (dir+m)%4, b)
        #print("Score: ", self.food, self.poison)
        return (self.food, self.poison)

    def get_recording(self):
        b = np.empty_like (self.board)
        b[:] = self.board
        rec = []
        for i,x,y, dir in self.recording:
            a = np.empty_like (b)
            a[:] = b
            rec.append((i,x,y, dir, a))
            self._move_agent(y,x, dir, b)
        return rec

    def _move_agent(self, y,x, dir, b):
        #print("dir", dir)
        if dir == Environment.NORTH:
            y = (y-1)%self.dim
        elif dir == Environment.EAST:
             x = (x+1)%self.dim
        elif dir == Environment.SOUTH:
            y = (y+1)%self.dim
        else:
            x = (x-1)%self.dim

        content = b[y][x]
        if content == Environment.FOOD:
            self.food += 1
        elif content == Environment.POISON:
            self.poison += 1
        b[y][x] = Environment.EMPTY
        return (y, x, dir)


    def _get_sensor_data(self, y,x, dir, b,type):
        dim = len(b)
        if dir == Environment.NORTH:
            data = [b[y][(x-1)%dim] == type,
                    b[(y-1)%dim][x] == type,
                    b[y][(x+1)%dim] == type]
        elif dir == Environment.EAST:
            data = [b[(y-1)%dim][x] == type,
                    b[y][(x+1)%dim] == type,
                    b[(y+1)%dim][x]== type]
        elif dir == Environment.SOUTH:
            data = [b[y][(x+1)%dim] == type,
                    b[(y+1)%dim][x] == type,
                    b[y][(x-1)%dim]== type]
        else:
            data = [b[(y+1)%dim][x] == type,
                    b[y][(x-1)%dim] == type,
                    b[(y-1)%dim][x]== type]
        return data


    def __repr__(self):
        return str(self.board)

