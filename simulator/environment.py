import numpy as np
import random

class Environment:
    TRACKER = 5

    OBJECT_MAX_DIM = 6
    OBJECT_MIN_DIM = 1

    MOVE_LEFT = 0
    MOVE_RIGHT = 1

    def __init__(self, width, height):
        #Board dimensions. 30x15 for Beer's game
        self.board_width = width
        self.board_height = height

        #Position of agent

        self.recording = []



    def score_agent(self, agent, timesteps=600, rec=False):
        if rec:
            self.recording = []
        self.avoidance= 0
        self.capture = 0
        self.failure_avoidance = 0
        self.failure_capture = 0
        self.speed = 0

        x,y, dim= self._init_agent(agent)
        object_x, object_y, object_dim = self._spawn_object()

        for t in range(timesteps):
            #Shadow sensor gathering
            shadow_sensors = self._get_sensor_data(x, dim, object_x, object_y, object_dim)
            #Motor output
            agent.input(shadow_sensors)
            motor_output = agent.output()

            if rec:
                score = (self.capture, self.avoidance,self.failure_capture, self.failure_avoidance)
                self.recording.append((t,score, (x,y, Environment.TRACKER, shadow_sensors), (object_x, object_y, object_dim)))

            #Score if at bottom
            #Move agent
            x, y = self._move_agent(x ,y, motor_output)

            at_bottom = self._object_at_bottom(object_y)
            if at_bottom:
                self._score_target(x, dim, object_x, object_dim)
                object_x, object_y, object_dim = self._spawn_object()
            else:
                #Move object closer to bottom
                object_y += 1
        bi_directional = int(self.move_right and self.move_left)
        return self.avoidance, self.capture, self.failure_avoidance, self.failure_capture,bi_directional

    def _spawn_object(self):
        #Assume objects cant wrap around. Will make no-wrap scenario easier
        dim = random.randint(Environment.OBJECT_MIN_DIM, Environment.OBJECT_MAX_DIM)
        return (random.randint(0, self.board_width-1-dim), 0, dim)

    def _init_agent(self, agent):
        agent.reset()
        agent_x = random.randint(0, self.board_width-1)
        agent_y = self.board_height-1
        self.move_right = False
        self.move_left = False
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
        object = set([i for i in range(ox, ox+odim)])
        if object.issubset(target):
            if odim < 5:
                self.capture += 1
            else:
                self.failure_avoidance += 1
        elif not object & target:
            if odim > 4:
                self.avoidance += 1
            else:
                self.failure_capture += 1
        else:
            if odim> 4:
                self.failure_avoidance += 1
            else:
                self.failure_capture += 1



    def _move_agent(self, x, y, motor_output):
        #TODO: Is this effient and capitalize motor_output?
        diff = motor_output[0] - motor_output[1]
        dir = 1
        #TODO: moving faster should be rewarded maybe
        magnitude = 0
        value = abs(diff)
        magnitude = int(value>=0.1) + int(value>=0.25) + int(value>=0.5)+ int(value>=0.65)
        if diff< 0:
            dir = -1
            if(magnitude>0):
                self.move_left = True
        else:
            if(magnitude>0):
                self.move_right = True
        nx = (x + (magnitude*dir))%self.board_width #Wrap around
        ny = y
        return (nx, ny)

    def get_recording(self):
        return self.recording

    def _get_sensor_data(self, x, dim, ox,oy, odim):
        '''
        Shadow sensor creation. If the x of tracker and object overlap
        the shadow sensor for the tracker agent is set to 1, indicating
        that an object is above the platform at that position
        '''
        sensor = np.zeros(dim)
        for i in range(dim):
            #TODO: handle wrap around. Think spawn assumption handles it
            if(x+i>=ox and x+i<ox+odim):
                sensor[i] =1 #/max(self.board_height - oy-5, 1.0)
        return sensor


    def __repr__(self):
        return "Environment of" + str(self.board_width) + "x" + str(self.board_height)

