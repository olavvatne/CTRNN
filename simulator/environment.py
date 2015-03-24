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
        self.dim = dim
        self.board[self.agent_y, self.agent_x] = Environment.EMPTY
        #Food and poision removed from agent's start position

    def score_agent(self, agent, timesteps=60):
        b = np.empty_like (self.board)
        b[:] = self.board
        #TODO: Might consider using a structure to keep track of changes made
        #to board while sim
        self.food = 0
        self.poison = 0
        y = self.agent_y
        x = self.agent_x
        dir = self.agent_dir

        for i in range(timesteps):

            #Senor gathering
            food_sensors = self._get_sensor_data(y,x,dir, Environment.FOOD)
            poison_sensors = self._get_sensor_data(y,x,dir, Environment.POISON)

            #Motor output
            motor_output = agent.feedforward(np.array(food_sensors + poison_sensors, dtype=np.int32))
            i = np.argmax(motor_output)
            m = 0
            if i == Environment.MOVE_LEFT:
                m = -1
            elif i == Environment.MOVE_RIGHT:
                m = 1
            y,x,dir = self._move_agent(y, x, (i+m)%4)

        return (self.food, self.poison)

    def _move_agent(self, y,x, dir):
        if dir == Environment.NORTH:
            y = (y-1)%self.dim
        elif dir == Environment.EAST:
             x = (x+1)%self.dim
        elif dir == Environment.SOUTH:
            y = (y+1)%self.dim
        else:
            x = (x-1)%self.dim

        content = self.board[y][x]
        if content == Environment.FOOD:
            self.food += 1
        elif content == Environment.POISON:
            self.poison += 1
        self.board[y][x] = Environment.EMPTY
        return (y, x, dir)


    def _get_sensor_data(self, y,x, dir, type):
        dim = len(self.board)
        if dir == Environment.NORTH:
            data = [self.board[y][(x-1)%dim] == type,
                    self.board[(y-1)%dim][x] == type,
                    self.board[y][(x+1)%dim] == type]
        elif dir == Environment.EAST:
            data = [self.board[(y-1)%dim][x] == type,
                    self.board[y][(x+1)%dim] == type,
                    self.board[(y+1)%dim][x]== type]
        elif dir == Environment.SOUTH:
            data = [self.board[y][(x+1)%dim] == type,
                    self.board[(y+1)%dim][x] == type,
                    self.board[y][(x-1)%dim]== type]
        else:
            data = [self.board[(y+1)%dim][x] == type,
                    self.board[y][(x-1)%dim] == type,
                    self.board[(y-1)%dim][x]== type]
        return data


    def __repr__(self):
        return str(self.board)

