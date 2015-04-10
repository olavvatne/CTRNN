import numpy as np
import random

class Environment:
    TRACKER = 5

    OBJECT_MAX_DIM = 6
    OBJECT_MIN_DIM = 1

    MOVE_LEFT = 0
    MOVE_RIGHT = 1

    def __init__(self, width, height):
        #TODO: No need for matrix.
        #TODO: Need to keep track of object and tracker position oynl
        #Board dimensions. 30x15 for Beer's game
        self.board_width = width
        self.board_height = height

        #Position of agent

        self.recording = []

        #TODO: consider how scoring should be done
        self.score = 0



    def score_agent(self, agent, timesteps=600, rec=False):
        if rec:
            recording = []
        self.avoidance= 0
        self.capture = 0
        self.failure = 0
        x,y, dim= self._init_agent()
        object_x, object_y, object_dim = self._spawn_object()

        for t in range(timesteps):
            #Shadow sensor gathering
            shadow_sensors = self._get_sensor_data(x, dim, object_x, object_dim)

            #Motor output
            motor_output = agent.feedforward(shadow_sensors)

            #Move agent
            x, y = self._move_agent(x ,y, motor_output)

            #Move object closer to bottom
            object_y -= 1

            #Score if at bottom
            if self._object_at_bottom(object_y):
                self._score_target(x, dim, object_x, object_dim)
                object_x, object_y, object_dim = self._spawn_object()
            if rec:
                self.recording.append((t, (x,y, Environment.TRACKER), (object_x, object_y, object_dim)))

        return self.avoidance, self.capture, self.failure

    def _spawn_object(self):
        #Assume objects cant wrap around. Will make no-wrap scenario easier
        dim = random.randint(Environment.OBJECT_MIN_DIM, Environment.OBJECT_MAX_DIM)
        return (random.randint(0, self.board_width-1-dim), 0, dim)

    def _init_agent(self):
        agent_x = random.randint(0, self.board_width-1)
        agent_y = self.board_height-1
        return agent_x, agent_y, Environment.TRACKER

    def _object_at_bottom(self, oy):
        return oy == self.board_height-1

    def _score_target(self, x, dim, ox, odim):
        '''
        Full overlap  1,2,3,4 --> capture
        Full overlap 5 --> failure
        No overlap of 5,6 --> avoidance
        No overlap of 1,2,3,4 --> failure
        Partial overlap of 1,2,3,4,5,6 --> failure
        '''
        #TODO: decrement avoidance instead of failure?
        target = set([i%self.board_width for i in range(x, x+dim)])
        object = set([i for i in range(ox, ox, odim)])
        if object.issubset(target):
            if odim < 5:
                self.capture += 1
            else:
                self.failure += 1
        elif object not in target:
            if odim > 4:
                self.avoidance += 1
            else:
                self.failure += 1
        else:
            self.failure += 1



    def _move_agent(self, x, y, motor_output):
        #TODO: Move agent based on actual motor output
        #TODO:Magnitude and direction of agent
        #TODO: Assume random movement now until RNN up and running
        nx = (x + random.randint(-4, 4))%self.board_width #Wrap around
        ny = y
        return (nx, ny)

    def get_recording(self):
        return self.recording

    def _get_sensor_data(self, x, dim, ox, odim):
        '''
        Shadow sensor creation. If the x of tracker and object overlap
        the shadow sensor for the tracker agent is set to 1, indicating
        that an object is above the platform at that position
        '''
        sensor = np.zeros(dim)
        for i in range(dim):
            #TODO: handle wrap around. Think spawn assumption handles it
            if(x+i>=ox and x+i<ox+odim):
                sensor[i] = 1
        return sensor


    def __repr__(self):
        return "Environment of" + str(self.board_width) + "x" + str(self.board_height)

